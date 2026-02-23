"""Document ingestion — PDF/text/URL → chunks → ChromaDB embeddings."""

import os
import re
import tempfile
import requests
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from src.config import Config


def get_embeddings():
    """Local embedding model (free, no API key needed)."""
    return HuggingFaceEmbeddings(model_name=Config.EMBEDDING_MODEL)


def get_vectorstore():
    """Get or create ChromaDB vectorstore."""
    return Chroma(
        persist_directory=Config.CHROMA_PERSIST_DIR,
        embedding_function=get_embeddings(),
        collection_name="research_docs",
    )


def load_document(file_path: str):
    """Load a single PDF or text file."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return PyPDFLoader(file_path).load()
    elif ext in (".txt", ".md"):
        return TextLoader(file_path, encoding="utf-8").load()
    else:
        raise ValueError(f"Unsupported file type: {ext}")


def chunk_documents(docs):
    """Split documents into chunks."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=Config.CHUNK_SIZE,
        chunk_overlap=Config.CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    return splitter.split_documents(docs)


def ingest_file(file_path: str) -> int:
    """Full pipeline: load → chunk → embed → store. Returns chunk count."""
    docs = load_document(file_path)
    chunks = chunk_documents(docs)

    vectorstore = get_vectorstore()
    vectorstore.add_documents(chunks)

    return len(chunks)


def ingest_files(file_paths: list[str]) -> int:
    """Ingest multiple files. Returns total chunk count."""
    total = 0
    for fp in file_paths:
        total += ingest_file(fp)
    return total


def _extract_text_from_html(html: str) -> str:
    """Extract readable text from HTML, stripping tags."""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    # Remove script and style elements
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    text = soup.get_text(separator="\n", strip=True)
    # Clean up excessive whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text


def ingest_url(url: str) -> int:
    """Scrape a URL → extract text → chunk → embed → store. Returns chunk count."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    
    text = _extract_text_from_html(response.text)
    
    if len(text.strip()) < 50:
        raise ValueError("Could not extract meaningful text from URL")
    
    # Create documents with URL as source
    docs = [Document(page_content=text, metadata={"source": url, "page": "web"})]
    chunks = chunk_documents(docs)
    
    vectorstore = get_vectorstore()
    vectorstore.add_documents(chunks)
    
    return len(chunks)
