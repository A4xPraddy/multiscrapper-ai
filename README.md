#  MultiScrapper AI Studio

**Premium Content Intelligence • Prasad Edition**

MultiScrapper AI is a powerful, full-stack application that allows you to extract, summarize, and interact with content from various sources (Web, YouTube, PDFs) using state-of-the-art AI models (**Gemini 2.0** & **Groq Llama 3**).



## ✨ Key Features

- **Web Scraper**: Extract text from any website and chat with its content. Includes **Visual Grounding** (screenshots) for context.
- **YouTube Intelligence**: Summarize videos and get key takeaways instantly using subtitles. Handles disabled subtitles gracefully.
- **PDF Analyst**: Upload PDF documents, vectorise them, and perform RAG (Retrieval-Augmented Generation) Q&A.
- **Dual-Engine AI**: 
  - **Gemini 2.0 Flash/Pro**: For deep reasoning and multimodal tasks.
  - **Groq (Llama 3)**: For lightning-fast summaries and infinite fallback support.
- **Auto-Failover Strategy**: Automatically switches to Groq if Gemini hits a rate limit (429 Error).
- **Premium UI**: Built with Next.js 14, TailwindCSS, and framer-motion animations.

---

## Tech Stack

- **Frontend**: Next.js 14 (App Router), TypeScript, Tailwind CSS, Lucide Icons.
- **Backend**: Python (FastAPI), Uvicorn.
- **AI/LLM**: Google Gemini API, Groq Cloud API, LangChain (for RAG).
- **Tools**: Selenium (Web Scraping), YouTube Transcript API, PyPDF2, FAISS (Vector Store).

---

## Getting Started

### Prerequisites
- Not using `npm run dev`? Install [Node.js](https://nodejs.org/).
- Install [Python 3.10+](https://www.python.org/).
- Get API Keys:
  - **Gemini API Key**: [Google AI Studio](https://aistudio.google.com/)
  - **Groq API Key**: [Groq Cloud](https://console.groq.com/)

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/yourusername/multiscrapper-ai.git
cd multiscrapper-ai
```

### 2️⃣ Backend Setup (Python)
Navigate to the root folder (where `App.py` or `backend/` is located):
```bash
# Install dependencies
pip install -r requirements.txt
pip install -r backend/requirements.txt

# Run the Server
python backend/main.py
```
*The backend runs on `http://localhost:8000`*

### 3️⃣ Frontend Setup (Next.js)
Open a new terminal and navigate to the `frontend` folder:
```bash
cd frontend

# Install dependencies
npm install

# Run Development Server
npm run dev
# OR for Production Performance
npm run build && npm start
```
*The frontend runs on `http://localhost:3000`*

---

## ☁️ Deployment Guide

### Backend (Render / Railway)
1.  Push code to GitHub.
2.  Create a **Web Service** on [Render](https://render.com/).
3.  **Build Command**: `pip install -r backend/requirements.txt`
4.  **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port 10000`
5.  Copy the provided URL (e.g., `https://my-api.onrender.com`).

### Frontend (Vercel)
1.  Import repository to [Vercel](https://vercel.com/).
2.  Set **Root Directory** to `frontend`.
3.  Add Environment Variable:
    - `NEXT_PUBLIC_API_URL`: Your Backend URL (e.g., `https://my-api.onrender.com`).
4.  Deploy!

---

## 🔐 Environment Variables

You can configure keys in the UI (stored in LocalStorage) or use a `.env` file in the `backend/` directory:

```env
GROQ_API_KEY=gsk_...
GOOGLE_API_KEY=AIza...
```

---

*Verified Production Ready - Jan 2026*
