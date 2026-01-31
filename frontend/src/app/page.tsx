
"use client";

import React, { useState, useEffect } from 'react';
import {
  Youtube,
  Globe,
  FileText,
  Search,
  Sparkles,
  Zap,
  Activity,
  ArrowRight,
  Settings,
  ShieldCheck,
  ClipboardList,
  MessageSquare,
  Bot
} from 'lucide-react';

import { initAI } from '../geminiService';

// Types
type Tool = 'web' | 'youtube' | 'pdf';
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function ScrapperApp() {
  const [activeTool, setActiveTool] = useState<Tool>('web');
  const [apiKey, setApiKey] = useState('');
  const [groqKey, setGroqKey] = useState('');
  const [isAiReady, setIsAiReady] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [loading, setLoading] = useState(false);
  const [inputUrl, setInputUrl] = useState('');
  const [query, setQuery] = useState('');
  const [result, setResult] = useState<any>(null);
  const [chatHistory, setChatHistory] = useState<{ role: string, content: string }[]>([]);

  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  // Sync Keys from localStorage
  useEffect(() => {
    const savedGemini = localStorage.getItem('gemini_api_key');
    const savedGroq = localStorage.getItem('groq_api_key');
    if (savedGemini || savedGroq) {
      if (savedGemini) {
        setApiKey(savedGemini);
        initAI(savedGemini);
      }
      if (savedGroq) setGroqKey(savedGroq);
      setIsAiReady(true);
    } else {
      setShowSettings(true);
    }
  }, []);

  const handleSaveKeys = () => {
    if (apiKey || groqKey) {
      if (apiKey) localStorage.setItem('gemini_api_key', apiKey);
      if (groqKey) localStorage.setItem('groq_api_key', groqKey);
      if (apiKey) initAI(apiKey);
      setIsAiReady(true);
      setShowSettings(false);
      alert("Intelligence Suite Activated");
    }
  };

  const handleProcess = async () => {
    if (!isAiReady) {
      alert("Please connect your API keys first!");
      return;
    }
    setLoading(true);
    setResult(null);
    setChatHistory([]);

    try {
      if (activeTool === 'pdf') {
        if (!selectedFile) throw new Error("Please select a PDF file first");

        const formData = new FormData();
        formData.append('file', selectedFile);

        const response = await fetch(`${API_BASE_URL}/api/pdf/vectorize`, {
          method: 'POST',
          body: formData
        });

        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || "PDF Processing failed");
        setResult(data);
        return;
      }

      // Logic for Web, YouTube
      const endpoint = activeTool === 'web' ? '/api/web/scrape' : '/api/youtube';
      const payload = { url: inputUrl };

      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-google-api-key': apiKey,
          'x-groq-api-key': groqKey
        },
        body: JSON.stringify(payload)
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Processing failed");

      setResult(data);
    } catch (e: any) {
      alert("Error: " + e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleAsk = async () => {
    if (!query || !result) return;
    const currentQuery = query;
    setQuery('');
    setLoading(true);

    try {
      const formData = new FormData();
      // Backend expects 'text', 'question', 'provider'
      formData.append('text', result.text || result.summary || "");
      formData.append('question', currentQuery);
      formData.append('provider', 'Gemini (Flash 2.0)');

      const response = await fetch(`${API_BASE_URL}/api/ask`, {
        method: 'POST',
        headers: {
          'x-google-api-key': apiKey,
          'x-groq-api-key': groqKey
        },
        body: formData
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "QA failed");

      setChatHistory(prev => [...prev, { role: 'user', content: currentQuery }, { role: 'bot', content: data.answer }]);
    } catch (e: any) {
      alert(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0a0b] text-white selection:bg-purple-500/30">

      {/* Dynamic Background */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-purple-900/20 blur-[120px] rounded-full animate-pulse" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-blue-900/20 blur-[120px] rounded-full" />
      </div>

      {/* Header */}
      <header className="relative z-10 border-b border-white/5 backdrop-blur-md bg-black/20 px-6 py-4 flex justify-between items-center">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-tr from-purple-600 to-blue-500 rounded-xl flex items-center justify-center shadow-lg shadow-purple-500/20">
            <Bot size={24} className="text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight">MultiScrapper <span className="text-purple-400">AI</span></h1>
            <p className="text-[10px] text-gray-500 font-medium uppercase tracking-widest">Premium Content Intelligence • Prasad Edition</p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className={`flex items-center gap-2 px-3 py-1 rounded-full text-[10px] font-bold uppercase transition-all ${isAiReady ? 'bg-green-500/10 text-green-400 border border-green-500/20' : 'bg-red-500/10 text-red-400 border border-red-500/20'}`}>
            <Activity size={12} />
            {isAiReady ? 'AI Connected' : 'AI Offline'}
          </div>
          <button
            onClick={() => setShowSettings(!showSettings)}
            className={`p-2 transition-colors ${showSettings ? 'text-purple-400' : 'text-gray-400 hover:text-white'}`}
          >
            <Settings size={20} />
          </button>
        </div>
      </header>

      <main className="relative z-10 max-w-5xl mx-auto px-6 py-12">

        {/* Intro Section */}
        <section className="text-center mb-16 animate-in fade-in slide-in-from-bottom-4 duration-1000">
          <h2 className="text-5xl font-extrabold tracking-tight mb-4 bg-gradient-to-r from-white via-white to-gray-500 bg-clip-text text-transparent">
            Smart Content Deconstruction
          </h2>
          <p className="text-gray-400 text-lg max-w-2xl mx-auto">
            Extract, summarize, and talk to any web content, YouTube video, or PDF document powered by <span className="text-white font-bold">Groq Llama 3</span> & <span className="text-purple-400 font-bold">Gemini 2.0</span>.
          </p>
        </section>

        {/* API Key Input (if settings shown or no keys) */}
        {(showSettings || !isAiReady) && (
          <div className="mb-12 glass-card p-8 border-purple-500/30 animate-in fade-in duration-500">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-4 text-purple-400">
                <ShieldCheck />
                <h3 className="font-bold">Intelligence Strategy Suite</h3>
              </div>
              {isAiReady && (
                <button onClick={() => setShowSettings(false)} className="text-[10px] text-gray-500 hover:text-white uppercase font-black">Close</button>
              )}
            </div>
            <p className="text-sm text-gray-400 mb-6 font-medium">Configure your personal LLM gateways. Keys are encrypted in local storage.</p>
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Groq API Key (Fastest & Infinite)</label>
                <input
                  type="password"
                  placeholder="gsk_..."
                  className="input-field w-full font-mono text-sm"
                  value={groqKey}
                  onChange={(e) => setGroqKey(e.target.value)}
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Gemini API Key (Multimodal)</label>
                <input
                  type="password"
                  placeholder="AIza..."
                  className="input-field w-full font-mono text-sm"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                />
              </div>
              <button onClick={handleSaveKeys} className="btn-primary w-full flex items-center justify-center gap-2">
                Activate Strategy Suite <Zap size={16} fill="currentColor" />
              </button>
            </div>
          </div>
        )}

        {/* Tool Selector */}
        <div className="flex justify-center mb-12">
          <div className="bg-white/5 p-1.5 rounded-2xl border border-white/10 flex gap-2">
            {[
              { id: 'web', label: 'Web Scraper', icon: Globe },
              { id: 'youtube', label: 'YouTube Video', icon: Youtube },
              { id: 'pdf', label: 'PDF Document', icon: FileText },
            ].map((tool) => (
              <button
                key={tool.id}
                onClick={() => { setActiveTool(tool.id as Tool); setResult(null); setInputUrl(''); setSelectedFile(null); }}
                className={`flex items-center gap-2 px-6 py-3 rounded-xl text-sm font-bold transition-all ${activeTool === tool.id ? 'bg-white/10 text-white shadow-inner' : 'text-gray-500 hover:text-gray-300'}`}
              >
                <tool.icon size={18} />
                {tool.label}
              </button>
            ))}
          </div>
        </div>

        {/* Input Area */}
        <div className="glass-card mb-12 p-8 border-white/5 hover:border-white/10 transition-all group">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <div className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500">
                {activeTool === 'web' ? <Search size={20} /> : (activeTool === 'youtube' ? <Youtube size={20} /> : <FileText size={20} />)}
              </div>
              {activeTool === 'pdf' ? (
                <div className="flex gap-4">
                  <input
                    type="file"
                    accept=".pdf"
                    className="hidden"
                    id="pdf-upload"
                    onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                  />
                  <label
                    htmlFor="pdf-upload"
                    className="input-field w-full pl-12 h-14 text-base flex items-center cursor-pointer text-gray-400 overflow-hidden"
                  >
                    {selectedFile ? selectedFile.name : "Choose a PDF file..."}
                  </label>
                </div>
              ) : (
                <input
                  className="input-field w-full pl-12 h-14 text-base"
                  placeholder={activeTool === 'web' ? "Paste website URL (e.g., https://openai.com)..." : "Paste YouTube link..."}
                  value={inputUrl}
                  onChange={(e) => setInputUrl(e.target.value)}
                />
              )}
            </div>
            <button
              disabled={loading || (activeTool !== 'pdf' ? !inputUrl : !selectedFile)}
              onClick={handleProcess}
              className="btn-primary h-14 md:px-10 flex items-center justify-center gap-3 disabled:opacity-50 disabled:grayscale transition-all"
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <>Analyze <ArrowRight size={18} /></>
              )}
            </button>
          </div>
        </div>

        {/* Results & Q/A Section */}
        {result && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 animate-in zoom-in-95 duration-500">
            {/* Summary/Content Card */}
            <div className="glass-card p-8 border-white/5 space-y-6">
              <div className="flex items-center justify-between border-b border-white/10 pb-4">
                <div className="flex items-center gap-2 text-purple-400">
                  <ClipboardList size={20} />
                  <span className="font-bold text-sm uppercase tracking-wider">Analysis Result</span>
                </div>
                {result.screenshot && (
                  <span className="text-[10px] bg-white/5 px-2 py-1 rounded text-gray-500 uppercase font-black">Screenshot Captured</span>
                )}
              </div>

              <div className="prose prose-invert max-w-none">
                <div className="text-gray-300 text-sm leading-relaxed whitespace-pre-wrap max-h-[500px] overflow-y-auto pr-4 scrollbar-thin">
                  {result.summary || result.text || "No content extracted."}
                </div>
              </div>

              {result.screenshot && (
                <div className="pt-4">
                  <p className="text-[10px] text-gray-500 uppercase font-black mb-2 flex items-center gap-2">
                    <Activity size={10} /> Visual Grounding
                  </p>
                  <img src={`${API_BASE_URL}/api/web/screenshot?t=${Date.now()}`} alt="Screenshot" className="rounded-lg border border-white/10 w-full hover:scale-[1.02] transition-transform cursor-zoom-in" />
                </div>
              )}
            </div>

            {/* Chat/QA Card */}
            <div className="glass-card p-8 border-white/5 flex flex-col h-[600px]">
              <div className="flex items-center gap-2 text-blue-400 border-b border-white/10 pb-4 mb-6">
                <MessageSquare size={20} />
                <span className="font-bold text-sm uppercase tracking-wider">Intelligence Q&A</span>
              </div>

              <div className="flex-1 overflow-y-auto space-y-4 mb-6 pr-4 scrollbar-thin">
                {chatHistory.length === 0 ? (
                  <div className="h-full flex flex-col items-center justify-center text-center opacity-20 filter grayscale">
                    <Bot size={48} className="mb-4" />
                    <p className="text-sm font-medium">Ask anything about the analyzed content.</p>
                  </div>
                ) : (
                  chatHistory.map((msg, i) => (
                    <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                      <div className={`max-w-[85%] p-4 rounded-2xl text-sm ${msg.role === 'user' ? 'bg-purple-600 rounded-tr-none' : 'bg-white/5 border border-white/10 rounded-tl-none text-gray-200'}`}>
                        {msg.content}
                      </div>
                    </div>
                  ))
                )}
                {loading && (
                  <div className="flex justify-start">
                    <div className="bg-white/5 border border-white/10 p-4 rounded-2xl rounded-tl-none">
                      <div className="flex gap-1">
                        <div className="w-1.5 h-1.5 bg-gray-500 rounded-full animate-bounce" />
                        <div className="w-1.5 h-1.5 bg-gray-500 rounded-full animate-bounce [animation-delay:0.2s]" />
                        <div className="w-1.5 h-1.5 bg-gray-500 rounded-full animate-bounce [animation-delay:0.4s]" />
                      </div>
                    </div>
                  </div>
                )}
              </div>

              <div className="relative">
                <input
                  className="input-field w-full pr-12 h-12"
                  placeholder="Ask a question..."
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleAsk()}
                />
                <button
                  onClick={handleAsk}
                  className="absolute right-2 top-1/2 -translate-y-1/2 p-2 text-purple-400 hover:text-white transition-colors"
                >
                  <ArrowRight size={20} />
                </button>
              </div>
            </div>
          </div>
        )}

      </main>

      {/* Footer */}
      <footer className="relative z-10 border-t border-white/5 mt-20 py-12 px-6 flex flex-col items-center gap-4">
        <div className="flex items-center gap-2 text-gray-500">
          <ShieldCheck size={14} />
          <span className="text-[10px] font-bold uppercase tracking-[0.2em]">Secure Intelligence Portal</span>
        </div>
        <p className="text-[11px] text-gray-400 font-medium uppercase tracking-[0.4em]">
          © 2024 MultiScrapper AI • Created by <span className="text-white font-black">Prasad</span>
        </p>
        <div className="w-8 h-px bg-gradient-to-r from-transparent via-purple-500/50 to-transparent" />
      </footer>

      <style jsx global>{`
        @keyframes pulse-slow {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.8; }
        }
        .animate-pulse-slow {
          animation: pulse-slow 4s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }
        .scrollbar-thin::-webkit-scrollbar {
          width: 4px;
        }
        .scrollbar-thin::-webkit-scrollbar-thumb {
          background: rgba(255,255,255,0.1);
          border-radius: 10px;
        }
        .scrollbar-thin::-webkit-scrollbar-track {
          background: transparent;
        }
      `}</style>
    </div>
  );
}

