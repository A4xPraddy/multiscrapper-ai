import os
import time
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_classic.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
import streamlit as st

try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    st.error("Missing 'langchain-huggingface'. Please run: pip install langchain-huggingface sentence-transformers")
    st.stop()

from dotenv import load_dotenv

load_dotenv()

def get_llm(provider="Gemini (Flash 2.0)"):
    """
    Returns the requested LLM instance with basic error handling.
    """
    if provider == "Groq (Llama 3)":
        groq_key = os.getenv("GROQ_API_KEY")
        if not groq_key:
            st.warning("GROQ_API_KEY not found in .env. Falling back to Gemini.")
            provider = "Gemini (Flash 2.0)"
        else:
            return ChatGroq(model_name="llama3-8b-8192", groq_api_key=groq_key)

    if provider == "Gemini (Flash 1.5)":
        return ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.3, max_retries=3)
    
    # Default: Gemini 2.0 Flash
    return ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.3, max_retries=3)

def get_rag_chain(text_content, provider="Gemini (Flash 2.0)"):
    """
    Creates a RAG chain with customizable LLM providers for resilience.
    """
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_text(text_content)

    # Local Embeddings (Free & Unlimited)
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vector_store = FAISS.from_texts(chunks, embeddings)

    # Select LLM based on user preference or quota
    llm = get_llm(provider)

    template = """You are an advanced data assistant. Use the following context to answer the question.
    If you don't know, say you don't know. 
    
    Context: {context}
    Question: {question}

    Helpful Answer:"""
    
    QA_CHAIN_PROMPT = PromptTemplate.from_template(template)

    return RetrievalQA.from_chain_type(
        llm,
        retriever=vector_store.as_retriever(search_kwargs={"k": 3}),
        chain_type_kwargs={"prompt": QA_CHAIN_PROMPT}
    )

def parse_with_vision(image_path, user_prompt):
    """Fallback logic for Vision if 2.0 fails."""
    import google.generativeai as genai
    from PIL import Image
    
    # Try 2.0 first, then 1.5
    for model_name in ['gemini-2.0-flash', 'gemini-1.5-flash']:
        try:
            model = genai.GenerativeModel(model_name)
            img = Image.open(image_path)
            response = model.generate_content([user_prompt, img])
            return response.text
        except Exception as e:
            if "429" in str(e):
                continue
            return f"Vision Error: {e}"
    return "Quota exhausted for all Vision models."

def extract_structured_data(text_content, schema_description, provider="Gemini (Flash 2.0)"):
    """Extracts tables with fallback provider support."""
    llm = get_llm(provider)
    prompt = f"Extract the following as a markdown table: {schema_description}\n\nText: {text_content[:8000]}"
    
    try:
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        return f"Extraction Error: {e}. Try switching the AI Provider in the sidebar."