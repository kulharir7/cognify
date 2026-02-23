# 🧠 Cognify — Multi-Agent Document Intelligence

> Three AI agents collaborate to research, synthesize, and fact-check answers from your documents — with full citation trails and transparent reasoning.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-orange.svg)](https://langchain-ai.github.io/langgraph/)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_Store-green.svg)](https://www.trychroma.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-UI-red.svg)](https://streamlit.io)

---

## 🎯 What It Does

Upload research papers, reports, or any documents → Ask questions in natural language → **Three specialized AI agents** collaborate to give you verified, cited answers.

```
📄 Your Documents → 🔍 Researcher → 📝 Synthesizer → ✅ Fact-Checker → 💬 Cited Answer
```

Unlike basic RAG that just retrieves and dumps text, this system uses **agentic reasoning** — each agent has a specialized role, and the pipeline ensures answers are accurate and well-sourced.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│              User Query                      │
└─────────────┬───────────────────────────────┘
              ▼
┌─────────────────────────────────────────────┐
│  🔍 RESEARCHER AGENT                        │
│  • Searches ChromaDB for relevant chunks    │
│  • Extracts key facts & data points         │
│  • Identifies gaps & contradictions         │
└─────────────┬───────────────────────────────┘
              ▼
┌─────────────────────────────────────────────┐
│  📝 SYNTHESIZER AGENT                       │
│  • Combines research into clear answer      │
│  • Adds [Source N] citations                │
│  • Structures with sections if needed       │
└─────────────┬───────────────────────────────┘
              ▼
┌─────────────────────────────────────────────┐
│  ✅ FACT-CHECKER AGENT                      │
│  • Verifies each claim against sources      │
│  • Marks: ✅ Verified / ⚠️ Partial / ❌ No  │
│  • Outputs final verified answer            │
└─────────────┴───────────────────────────────┘
```

**Tech Stack:**
- **LangGraph** — Agent orchestration with state management
- **ChromaDB** — Local vector database (your data stays private)
- **Sentence Transformers** — Free local embeddings (no API cost)
- **Streamlit** — Interactive web UI with agent trace visualization

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/kulharir7/agentic-rag-assistant.git
cd agentic-rag-assistant
pip install -r requirements.txt
```

### 2. Configure LLM

Copy `.env.example` to `.env` and set your preferred provider:

```bash
cp .env.example .env
```

**Ollama Cloud (default):**
```env
LLM_PROVIDER=ollama
LLM_BASE_URL=https://ollama.com/v1
LLM_API_KEY=your-key
LLM_MODEL=mistral-large-3:675b
```

**OpenAI:**
```env
LLM_PROVIDER=openai
LLM_API_KEY=sk-...
LLM_MODEL=gpt-4o
```

**Anthropic / Any OpenAI-compatible API:**
```env
LLM_BASE_URL=https://your-api-url/v1
LLM_API_KEY=your-key
LLM_MODEL=your-model
```

### 3. Run

```bash
streamlit run app.py
```

Open http://localhost:8501 → Upload documents → Start asking questions!

---

## 📖 How It Works

### Document Ingestion
1. Upload PDF/TXT/MD files via the sidebar
2. Documents are split into overlapping chunks (1000 chars, 200 overlap)
3. Chunks are embedded using `all-MiniLM-L6-v2` (runs locally, free)
4. Vectors stored in ChromaDB (persists on disk)

### Query Pipeline (3 Agents)

| Agent | Role | What It Does |
|-------|------|-------------|
| 🔍 **Researcher** | Information Retrieval | Searches vector DB, extracts key facts, identifies gaps |
| 📝 **Synthesizer** | Answer Generation | Combines findings into structured, cited answer |
| ✅ **Fact-Checker** | Verification | Cross-checks every claim against original sources |

### Agent Trace
Every query shows a **reasoning trace** — you can see exactly what each agent did, providing full transparency into the AI's decision-making process.

---

## 🔑 Key Features

- **Multi-Agent Pipeline** — Not just retrieve-and-answer; three specialized agents collaborate
- **Source Citations** — Every claim linked to [Source N] with page numbers
- **Agent Transparency** — Full reasoning trace visible in UI
- **Provider Agnostic** — Works with Ollama Cloud, OpenAI, Anthropic, or any OpenAI-compatible API
- **Privacy First** — Embeddings run locally, documents never leave your machine
- **Dark Theme UI** — Professional Streamlit interface

---

## 📁 Project Structure

```
agentic-rag-assistant/
├── app.py                 # Streamlit UI
├── src/
│   ├── config.py          # Configuration loader
│   ├── ingest.py          # Document ingestion pipeline
│   ├── llm.py             # LLM factory (multi-provider)
│   └── agents.py          # LangGraph multi-agent pipeline
├── data/
│   └── chroma_db/         # Vector database (auto-created)
├── .env.example           # Configuration template
├── requirements.txt       # Python dependencies
└── README.md
```

---

## 🤝 Contributing

PRs welcome! Areas to contribute:
- Web search fallback agent
- More document formats (DOCX, HTML)
- Conversation memory across queries
- Agent performance metrics

---

## 📄 License

MIT License — use freely for personal and commercial projects.

---

<p align="center">Built by <a href="https://github.com/kulharir7">Ravindra Kulhari</a> | AI/ML Engineer</p>
