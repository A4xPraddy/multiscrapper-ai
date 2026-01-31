import os
from dotenv import load_dotenv

load_dotenv() # Load env vars from .env file

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
import io
import re

# We can reuse our logic from the root folder by importing or copying
# For a clean fullstack app, I'll put the core logic here or in a utils file.

from .scraper import scrape_website, clean_body_content
from PIL import Image
import base64

from youtube_transcript_api import YouTubeTranscriptApi
from PyPDF2 import PdfReader
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_classic.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings

# Initialize embeddings once at startup to save time on each request
print("Initializing HuggingFace Embeddings (this may take a moment)...")
embeddings_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
print("Embeddings loaded.")

# Global cache for vector store to avoid rebuilding it on every question
# In production, use Redis or a session-based storage.
vector_store_cache = {
    "text_hash": None,
    "store": None
}

app = FastAPI(title="MultiScrapper AI Pro API")

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Models ---
class YouTubeRequest(BaseModel):
    url: str
    provider: str = "Gemini (Flash 2.0)"

class WebRequest(BaseModel):
    url: str
    provider: str = "Gemini (Flash 2.0)"
    mode: str = "Smart Q&A (RAG)"

# --- Utilities ---
# Global cache for valid model names to avoid repeated API calls
valid_model_cache = {}

def get_llm(provider: str, google_api_key: str = None, groq_api_key: str = None):
    # Groq handling remains the same
    if provider == "Groq (Llama 3)" and groq_api_key:
        return ChatGroq(model_name="llama-3.3-70b-versatile", groq_api_key=groq_api_key)
    
    if google_api_key:
        import google.generativeai as genai
        
        # Check cache first
        if google_api_key in valid_model_cache:
            verified_model = valid_model_cache[google_api_key]
            return ChatGoogleGenerativeAI(model=verified_model, google_api_key=google_api_key, temperature=0.3)

        genai.configure(api_key=google_api_key)
        
        # 1. Try variable preferred choices based on provider string
        preferred_candidates = []
        if "2.0" in provider:
            preferred_candidates = ["gemini-2.0-flash", "gemini-2.0-flash-exp"]
        else:
            # Standard 1.5 candidates
            preferred_candidates = ["gemini-1.5-flash", "gemini-1.5-flash-latest", "gemini-1.5-flash-001"]

        # 2. Add safe fallbacks
        fallback_candidates = ["gemini-pro", "gemini-1.5-pro", "gemini-1.0-pro"]
        
        # 3. Dynamic Validation: Check which one actually exists
        final_model = None
        
        try:
            # Get list of all available models for this key
            # We strip 'models/' prefix for comparison because inputs usually don't have it
            available_models = [m.name.replace("models/", "") for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            
            print(f"DEBUG: Available Google Models: {available_models}")
            
            # Check preferences first
            for cand in preferred_candidates:
                if cand in available_models:
                    final_model = cand
                    break
            
            # If no preference found, check fallbacks
            if not final_model:
                for cand in fallback_candidates:
                    if cand in available_models:
                        final_model = cand
                        break
            
            # If still nothing, just grab the first valid gemini model
            if not final_model:
                for model in available_models:
                    if "gemini" in model:
                        final_model = model
                        break
                        
        except Exception as e:
            print(f"Warning: Could not list models ({e}). Defaulting to 'gemini-1.5-flash'.")
            final_model = "gemini-1.5-flash"

        if not final_model:
            # Absolute last resort
            final_model = "gemini-1.5-flash"
            
        print(f"Selected validated model: {final_model}")
        valid_model_cache[google_api_key] = final_model
        
        return ChatGoogleGenerativeAI(
            model=final_model, 
            google_api_key=google_api_key, 
            temperature=0.3,
            convert_system_message_to_human=True
        )
    
    raise HTTPException(status_code=400, detail="No valid API key provided for selected model")

# --- Endpoints ---

@app.post("/api/youtube")
async def summarize_youtube(
    request: YouTubeRequest, 
    x_google_api_key: Optional[str] = Header(None),
    x_groq_api_key: Optional[str] = Header(None)
):
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", request.url)
    video_id = match.group(1) if match else None
    
    if not video_id:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")
    
    try:
        print(f"Fetching transcript for: {video_id}")
        text = ""
        try:
            # The installed version of youtube-transcript-api (1.2.4) requires an instance
            yt_api = YouTubeTranscriptApi()
            
            # Try to get English transcript first (manual or auto), then fall back to others
            try:
                # fetch() on the instance is the equivalent of get_transcript
                data = yt_api.fetch(video_id, languages=['en'])
            except Exception:
                # If English fails, try to list all available and pick the first one
                transcript_list = yt_api.list(video_id)
                # Try to find any English transcript (manual or generated)
                try:
                    transcript = transcript_list.find_transcript(['en'])
                except Exception:
                    # If no English, just take the first available one
                    transcript = next(iter(transcript_list))
                data = transcript.fetch()
            
            # Fix: data is a list of objects, not dicts. Access .text attribute directly.
            text = " ".join([item.text for item in data])
            print(f"Transcript fetched. Length: {len(text)} characters.")
            
        except Exception as transcript_err:
            print(f"Transcript Error: {transcript_err}")
            # Instead of crashing, we return a helpful message
            return {
                "summary": f"⚠️ **Transcript Unavailable**\n\nI couldn't retrieve the subtitles for this video. This happens if:\n1. The video has disabled captions.\n2. The video is too new or too short.\n3. It's a music video or auto-generated clip.\n\n**Error Details:** {str(transcript_err)}"
            }
        
        # Smart Fallback Logic
        try:
            llm = get_llm(request.provider, x_google_api_key, x_groq_api_key)
            prompt = f"Summarize this video transcript with key takeaways and timestamp-style headings: {text}"
            response = llm.invoke(prompt)
        except Exception as e:
            if "404" in str(e) or "NOT_FOUND" in str(e):
                print("Model not found. Trying fallback model...")
                # Fallback to gemini-pro if flash fails
                llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=x_google_api_key)
                response = llm.invoke(f"Summarize this: {text[:30000]}") # Truncate for safety
            elif "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                 print("Gemini limit reached. Checking for Groq fallback...")
                 
                 # Check if we have a Groq Key (header or env)
                 local_groq = x_groq_api_key or os.getenv("GROQ_API_KEY")
                 
                 if local_groq:
                     print("Falling back to Groq (Llama 3)...")
                     llm = get_llm("Groq (Llama 3)", x_google_api_key, local_groq)
                     # GroqContext window might be smaller, truncate harder just in case
                     response = llm.invoke(f"Summarize this video transcript with key takeaways: {text[:15000]}")
                 else:
                     raise HTTPException(
                         status_code=429, 
                         detail="Gemini Quota Exceeded. Please wait a minute OR enter a Groq API Key in settings for instant infinite fallback."
                     )
            else:
                raise e
        
        # Strip asterisks as requested by user
        clean_summary = response.content.replace("*", "")
        return {"summary": clean_summary}
    except Exception as e:
        error_msg = str(e)
        print(f"ERROR in summarize_youtube: {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)

@app.post("/api/pdf/vectorize")
async def vectorize_pdf(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        pdf_reader = PdfReader(io.BytesIO(contents))
        
        raw_text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                # Clean up extracted text: replace multiple newlines/spaces with a single space
                # but keep double newlines for paragraph separation
                cleaned_page = re.sub(r'(?<!\n)\n(?!\n)', ' ', page_text)
                raw_text += cleaned_page + "\n\n"
        
        # Final pass to remove excessive whitespace
        final_text = re.sub(r' +', ' ', raw_text).strip()
        
        return {"text": final_text, "page_count": len(pdf_reader.pages)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ask")
async def ask_question(
    text: str = Form(...),
    question: str = Form(...),
    provider: str = Form("Gemini (Flash 2.0)"),
    x_google_api_key: Optional[str] = Header(None),
    x_groq_api_key: Optional[str] = Header(None)
):
    try:
        print(f"Starting Q&A for question: {question[:50]}...")
        
        import hashlib
        text_hash = hashlib.md5(text.encode()).hexdigest()

        # Check if we can reuse the vector store
        global vector_store_cache
        if vector_store_cache["text_hash"] == text_hash:
            print("Reusing cached vector store.")
            vector_store = vector_store_cache["store"]
        else:
            print("Building new vector store...")
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            chunks = text_splitter.split_text(text)
            print(f"Split text into {len(chunks)} chunks.")
            
            # Use the global embeddings model
            vector_store = FAISS.from_texts(chunks, embeddings_model)
            vector_store_cache["text_hash"] = text_hash
            vector_store_cache["store"] = vector_store
            print("Vector store created and cached.")
        
        # LLM Chain with Fallback
        try:
            llm = get_llm(provider, x_google_api_key, x_groq_api_key)
            template = """Use the context to answer. Context: {context} Question: {question}"""
            QA_CHAIN_PROMPT = PromptTemplate.from_template(template)
            qa_chain = RetrievalQA.from_chain_type(
                llm,
                retriever=vector_store.as_retriever(search_kwargs={"k": 3}),
                chain_type_kwargs={"prompt": QA_CHAIN_PROMPT}
            )
            response = qa_chain.invoke(question)
        except Exception as e:
            if ("429" in str(e) or "RESOURCE_EXHAUSTED" in str(e)) and x_groq_api_key:
                print("Gemini limit reached. Falling back to Groq...")
                llm = get_llm("Groq (Llama 3)", x_google_api_key, x_groq_api_key)
                qa_chain = RetrievalQA.from_chain_type(llm, retriever=vector_store.as_retriever())
                response = qa_chain.invoke(question)
            else:
                raise e

        print("AI Response generated.")
        return {"answer": response['result'].replace("*", "")}
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg:
             error_msg = "API Quota Exhausted. Please wait 60 seconds or use a Groq API Key."
        print(f"ERROR in ask_question: {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)

@app.post("/api/web/scrape")
async def scrape_web(request: WebRequest):
    try:
        html, screenshot = scrape_website(request.url)
        text = clean_body_content(html)
        return {"text": text, "screenshot": screenshot}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/web/vision")
async def analyze_vision(
    image_path: str = Form(...),
    prompt: str = Form(...),
    x_google_api_key: Optional[str] = Header(None)
):
    if not x_google_api_key:
        raise HTTPException(status_code=400, detail="Google API Key missing")
        
    import google.generativeai as genai
    genai.configure(api_key=x_google_api_key)
    
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        img = Image.open(image_path)
        response = model.generate_content([prompt, img])
        return {"analysis": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/web/extract")
async def extract_table(
    text: str = Form(...),
    provider: str = Form("Gemini (Flash 2.0)"),
    x_google_api_key: Optional[str] = Header(None),
    x_groq_api_key: Optional[str] = Header(None)
):
    llm = get_llm(provider, x_google_api_key, x_groq_api_key)
    prompt = f"Extract product names, prices, and features into a markdown table from this text:\n\n{text[:8000]}"
    try:
        response = llm.invoke(prompt)
        return {"table": response.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/web/screenshot")
async def get_screenshot():
    if os.path.exists("page.png"):
        return FileResponse("page.png")
    raise HTTPException(status_code=404, detail="No screenshot available")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))  # Use PORT from environment, default to 8000 for local dev
    uvicorn.run(app, host="0.0.0.0", port=port)
