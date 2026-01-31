import os
import streamlit as st
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
import langcodes
from PyPDF2 import PdfReader
from dotenv import load_dotenv

# Import our custom modules
from scrape import scrape_website, clean_body_content
from parse import get_rag_chain, parse_with_vision, extract_structured_data

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    st.error("Missing Google API Key! Please add it to your .env file.")
    st.stop()

genai.configure(api_key=GOOGLE_API_KEY)

# ================= PAGE CONFIG & STYLING =================
st.set_page_config(
    page_title="MultiScrapper AI Pro",
    page_icon="🤖",
    layout="wide"
)

# Premium UI CSS (Glassmorphism & Neumorphism mix)
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #1e1e2f 0%, #121212 100%);
        color: #e0e0e0;
    }
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3em;
        background: linear-gradient(45deg, #6a11cb 0%, #2575fc 100%);
        color: white;
        border: none;
        transition: all 0.3s ease;
        font-weight: bold;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(106, 17, 203, 0.4);
        border: none;
        color: white;
    }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: rgba(255, 255, 255, 0.05) !important;
        color: white !important;
        border-radius: 10px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    div[data-testid="stExpander"] {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .status-badge {
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8em;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# ================= SIDEBAR =================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2103/2103633.png", width=100)
    st.title("Pro Tools")
    tool_choice = st.radio(
        "Navigation",
        ["🏠 Dashboard", "🎥 YouTube Pro", "📄 PDF Intelligence", "🌐 Web AI Agent"]
    )
    st.divider()
    st.info("Powered by RAG & Gemini 2.0 Flash")

# ================= DASHBOARD =================
if tool_choice == "🏠 Dashboard":
    st.title("🚀 MultiScrapper AI Pro")
    st.markdown("### Welcome to the most advanced content intelligence platform.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Retrieval Type", value="RAG Enabled")
    with col2:
        st.metric(label="AI Model", value="Gemini 2.0")
    with col3:
        st.metric(label="Speed", value="Ultra-Fast (Flash)")
    
    st.write("---")
    st.markdown("""
    #### ✨ Core Advancements:
    1. **RAG (Search Engine Logic)**: We don't just read text; we find the *answers* using vector embeddings.
    2. **Vision Integration**: We can look at screenshots to understand complex layouts.
    3. **Structured Miner**: Convert messy websites into clean data tables instantly.
    """)

elif tool_choice == "🎥 YouTube Pro":
    st.header("🎥 YouTube Content Intelligence")
    # Model Selection for resilience
    yt_ai_provider = st.selectbox("Select AI Engine (YouTube)", ["Gemini (Flash 2.0)", "Gemini (Flash 1.5)", "Groq (Llama 3)"], key="yt_model")
    
    video_url = st.text_input("Paste YouTube URL", placeholder="https://youtube.com/watch?v=...")
    
    if video_url:
        import re
        match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", video_url)
        video_id = match.group(1) if match else None
        
        if video_id:
            st.image(f"http://img.youtube.com/vi/{video_id}/maxresdefault.jpg", use_container_width=True)
            
            if st.button("Summarize & Analyze"):
                with st.spinner("🧠 Extracting insights..."):
                    try:
                        ytt_api = YouTubeTranscriptApi()
                        transcript_list = ytt_api.list(video_id)
                        
                        try:
                            transcript = transcript_list.find_transcript(['en'])
                        except:
                            transcript = next(iter(transcript_list))
                            
                        data = transcript.fetch()
                        text = " ".join([i.text for i in data])
                        
                        # Use the new resilient library
                        from parse import get_llm
                        llm = get_llm(yt_ai_provider)
                        
                        prompt = "Summarize this video transcript with key takeaways and timestamp-style headings: " + text
                        response = llm.invoke(prompt)
                        
                        st.markdown("### 📝 Video Insights")
                        st.write(response.content)
                    except Exception as e:
                        st.error(f"YouTube Error: {str(e)}")
                        st.info("Tip: If you see 'TranscriptsDisabled', YouTube might be blocking automated access or quota reached.")
        else:
            st.error("Could not extract Video ID. Please check the URL.")

# ================= PDF INTELLIGENCE =================
elif tool_choice == "📄 PDF Intelligence":
    st.header("📄 PDF RAG Analysis")
    
    # Model Selection for resilience
    ai_provider = st.selectbox("Select AI Engine", ["Gemini (Flash 2.0)", "Gemini (Flash 1.5)", "Groq (Llama 3)"])
    
    uploaded_file = st.file_uploader("Upload PDF", type="pdf")
    
    if uploaded_file:
        with st.spinner("📂 Reading PDF..."):
            reader = PdfReader(uploaded_file)
            text = "".join([page.extract_text() for page in reader.pages])
            st.success(f"Loaded {len(reader.pages)} pages")
        
        # Reset RAG if model or file changes
        if st.button("Initialize/Reset AI Engine"):
            with st.spinner("🤖 Vectorizing document..."):
                st.session_state.qa_chain = get_rag_chain(text, provider=ai_provider)
                st.success(f"RAG Online via {ai_provider}!")
        
        if 'qa_chain' in st.session_state:
            user_query = st.text_input("Ask a question about this document:")
            if user_query:
                with st.spinner("Searching knowledge base..."):
                    try:
                        response = st.session_state.qa_chain.invoke(user_query)
                        st.markdown("#### 💡 AI Answer:")
                        st.write(response['result'])
                    except Exception as e:
                        st.error(f"Quota issue with {ai_provider}. Please try switching to Gemini (Flash 1.5) or Groq.")

# ================= WEB AI AGENT =================
elif tool_choice == "🌐 Web AI Agent":
    st.header("🌐 Web Scraping & Vision Agent")
    
    # Model Selection for resilience
    ai_provider = st.selectbox("Select AI Engine", ["Gemini (Flash 2.0)", "Gemini (Flash 1.5)", "Groq (Llama 3)"])
    
    url = st.text_input("Enter Website URL")
    
    col1, col2 = st.columns(2)
    with col1:
        mode = st.radio("Analysis Mode", ["Smart Q&A (RAG)", "Data Table Extraction", "Visual Analysis (Vision)"])
    
    if st.button("Start Processing"):
        with st.spinner("🕸️ Navigating & Scraping..."):
            html_raw = scrape_website(url)
            text_cleaned = clean_body_content(html_raw)
            
            if mode == "Smart Q&A (RAG)":
                st.session_state.web_rag = get_rag_chain(text_cleaned, provider=ai_provider)
                st.success(f"Website Indexed via {ai_provider}!")
            
            elif mode == "Data Table Extraction":
                st.info("Extracting structured fields...")
                table_data = extract_structured_data(text_cleaned, "product names, prices, and features", provider=ai_provider)
                st.markdown(table_data)
            
            elif mode == "Visual Analysis (Vision)":
                st.image("page_screenshot.png", caption="Captured Screenshot", use_container_width=True)
                with st.spinner("👁️ AI is 'looking' at the page..."):
                    vision_result = parse_with_vision("page_screenshot.png", "Explain the layout and key categories of this website.")
                    st.write(vision_result)

    if mode == "Smart Q&A (RAG)" and "web_rag" in st.session_state:
        query = st.text_input("Ask anything about this website:")
        if query:
            res = st.session_state.web_rag.invoke(query)
            st.write(res['result'])

# ================= FOOTER =================
st.divider()
st.caption("Admin Mode: 🟢 Active | Region: Global-Cloud | Version: 2.0-Advanced")
