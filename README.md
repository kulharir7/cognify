# 🧠 Cognify — Multi-Agent Document Intelligence

> Four AI agents collaborate to research, synthesize, and fact-check answers from your documents — with full citation trails, hybrid search, and transparent reasoning.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-orange.svg)](https://langchain-ai.github.io/langgraph/)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_Store-green.svg)](https://www.trychroma.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-UI-red.svg)](https://streamlit.io)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

---

## 🎯 What It Does

Upload research papers, reports, or any documents → Ask questions in natural language → **Four specialized AI agents** collaborate to give you verified, cited answers.

```
📄 Documents → 🔄 Context Rewriter → 🔍 Researcher → 📝 Synthesizer → ✅ Fact-Checker → 💬 Answer
```

Unlike basic RAG that just retrieves and dumps text, Cognify uses **agentic reasoning** — each agent has a specialized role, and the pipeline ensures answers are accurate and well-sourced.

---

## ✨ Key Features

### 🤖 Multi-Agent Pipeline (4 Agents)
| Agent | Role | What It Does |
|-------|------|-------------|
| 🔄 **Context Rewriter** | Conversation Memory | Rewrites follow-up questions with context |
| 🔍 **Researcher** | Information Retrieval | Multi-query expansion + hybrid search |
| 📝 **Synthesizer** | Answer Generation | Structures findings with [Source N] citations |
| ✅ **Fact-Checker** | Verification | Cross-checks every claim, streams verified answer |

### 🔍 Advanced Retrieval
- **Hybrid Search** — BM25 keyword + ChromaDB vector search combined
- **Reciprocal Rank Fusion** — merges rankings from both search methods
- **Multi-Query Expansion** — auto-generates 2-3 alternative queries for broader coverage
- **Conversation Memory** — follow-up questions work naturally

### 📱 Multi-Page Application
- **💬 Chat** — main research interface with streaming answers
- **📁 Documents** — file manager, URL ingestion, per-doc delete
- **📊 Analytics** — response times, agent performance, query history
- **⚙️ Settings** — model configuration, RAG parameters

### 🔌 Provider Agnostic
- **Ollama Cloud** — mistral-large, deepseek, qwen3-coder, gpt-oss
- **OpenAI** — GPT-4o, GPT-4-turbo
- **Anthropic** — Claude Sonnet, Opus
- **Any OpenAI-compatible API** — custom providers

### 📤 Export & Utility
- Download answers as **Markdown**
- Per-answer or full chat export
- **URL Ingestion** — paste a link, auto-scrape & ingest
- Supports: PDF, TXT, Markdown files

### 🔒 Privacy & Security
- Local embeddings (`all-MiniLM-L6-v2`) — no API cost for embeddings
- Documents never leave your machine
- Password-protected access
- Session isolation

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      User Query                              │
│            "What about its pricing?"                         │
└─────────────┬───────────────────────────────────────────────┘
              ▼
┌─────────────────────────────────────────────────────────────┐
│  🔄 CONTEXT REWRITER                                        │
│  • Analyzes conversation history                             │
│  • Rewrites: "What is DynamoDB pricing model?"               │
│  • Fast model (~1-2s)                                        │
└─────────────┬───────────────────────────────────────────────┘
              ▼
┌─────────────────────────────────────────────────────────────┐
│  🔍 RESEARCHER (Multi-Query + Hybrid Search)                 │
│                                                              │
│  1. Generate 2-3 alternative queries                         │
│  2. For each query:                                          │
│     ├── BM25 keyword search                                  │
│     ├── ChromaDB vector search                               │
│     └── Reciprocal Rank Fusion                               │
│  3. Deduplicate & merge top results                          │
│  4. Extract key findings with citations                      │
└─────────────┬───────────────────────────────────────────────┘
              ▼
┌─────────────────────────────────────────────────────────────┐
│  📝 SYNTHESIZER                                              │
│  • Combines research into structured answer                  │
│  • Adds [Source N] citations                                 │
│  • Avoids repeating previous answers                         │
└─────────────┬───────────────────────────────────────────────┘
              ▼
┌─────────────────────────────────────────────────────────────┐
│  ✅ FACT-CHECKER (Streaming)                                 │
│  • Verifies each claim: ✅ / ⚠️ / ❌                         │
│  • Streams verified answer token-by-token                    │
│  • Output appears word-by-word with cursor                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Option 1: Local Install

```bash
git clone https://github.com/kulharir7/cognify.git
cd cognify
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env      # Edit with your API key
streamlit run app.py
```

### Option 2: Docker

```bash
git clone https://github.com/kulharir7/cognify.git
cd cognify
cp .env.example .env      # Edit with your API key
docker-compose up -d
```

Open http://localhost:8501 → Login (default: `admin` / `cognify123`)

### Configure LLM

Edit `.env`:

```env
# Ollama Cloud (default)
LLM_BASE_URL=https://ollama.com/v1
LLM_API_KEY=your-key
LLM_MODEL=mistral-large-3:675b

# Or OpenAI
LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=sk-...
LLM_MODEL=gpt-4o
```

Or configure in-app via ⚙️ Settings page.

---

## 📁 Project Structure

```
cognify/
├── app.py                    # 💬 Main chat page
├── pages/
│   ├── 2_📁_Documents.py     # File manager + URL ingest
│   ├── 3_📊_Analytics.py     # Usage analytics dashboard
│   └── 4_⚙️_Settings.py     # Model & RAG configuration
├── src/
│   ├── agents.py             # LangGraph 4-agent pipeline
│   ├── config.py             # Configuration loader
│   ├── export.py             # Markdown export
│   ├── ingest.py             # Document + URL ingestion
│   ├── llm.py                # LLM factory (multi-provider)
│   ├── retriever.py          # Hybrid search (BM25 + Vector + RRF)
│   └── ui.py                 # Shared UI components + CSS
├── data/
│   └── chroma_db/            # Vector database (auto-created)
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── requirements.txt
└── README.md
```

---

## 🔬 How It Compares

| Feature | Basic RAG | Cognify |
|---------|-----------|---------|
| Search | Vector only | Hybrid (BM25 + Vector + RRF) |
| Query | Single query | Multi-query expansion |
| Answer | Single LLM call | 4-agent pipeline |
| Verification | None | Fact-checker agent |
| Memory | None | Conversation history |
| Follow-ups | ❌ | ✅ Context rewriter |
| Streaming | ❌ | ✅ Token-by-token |
| Citations | Basic | [Source N] with page numbers |
| Transparency | Black box | Full agent trace |
| Export | ❌ | Markdown download |
| Multi-page | ❌ | Chat + Docs + Analytics + Settings |

---

## 🛠️ Tech Stack

- **[LangGraph](https://langchain-ai.github.io/langgraph/)** — Agent orchestration with state management
- **[ChromaDB](https://www.trychroma.com/)** — Local vector database
- **[Sentence Transformers](https://sbert.net/)** — Free local embeddings
- **[BM25](https://en.wikipedia.org/wiki/Okapi_BM25)** — Keyword search via rank-bm25
- **[Streamlit](https://streamlit.io/)** — Multi-page web application
- **[LangChain](https://langchain.com/)** — LLM integration framework

---

## 🤝 Contributing

PRs welcome! Areas to contribute:
- More document formats (DOCX, Excel)
- Web search fallback agent
- Multi-collection workspaces
- Improved re-ranking with cross-encoders
- Performance benchmarks

---

## 📄 License

MIT License — use freely for personal and commercial projects.

---

<p align="center">
Built by <a href="https://github.com/kulharir7">Ravindra Kulhari</a> — AI/ML Engineer<br>
<sub>🧠 Cognify — Making document research intelligent</sub>
</p>
