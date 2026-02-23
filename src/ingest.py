"""Document ingestion — PDF/text → chunks → ChromaDB embeddings."""

import os
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
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
