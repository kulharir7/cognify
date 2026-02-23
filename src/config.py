"""Configuration loader — supports Ollama Cloud, OpenAI, Anthropic, or any OpenAI-compatible API."""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # LLM
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")
    LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://ollama.com/v1")
    LLM_API_KEY = os.getenv("LLM_API_KEY", "")
    LLM_MODEL = os.getenv("LLM_MODEL", "mistral-large-3:675b")

    # Fast model for researcher (cheaper/faster)
    LLM_FAST_MODEL = os.getenv("LLM_FAST_MODEL", "deepseek-v3.1:671b")

    # Embeddings (local, free)
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

    # ChromaDB
    CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./data/chroma_db")

    # Chunking
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))

    # Retrieval
    TOP_K = int(os.getenv("TOP_K", "5"))
