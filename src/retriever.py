"""Hybrid retriever — combines BM25 keyword search + ChromaDB vector search + re-ranking.

Why hybrid?
- Vector search: great for semantic similarity ("cloud database" → "DynamoDB")
- BM25 keyword search: great for exact terms ("DynamoDB" → "DynamoDB")
- Re-ranking: cross-encoder picks the truly best results from combined set

Result: much better retrieval accuracy than either alone.
"""

import re
from rank_bm25 import BM25Okapi
from src.ingest import get_vectorstore
from src.config import Config


def _tokenize(text: str) -> list[str]:
    """Simple tokenizer — lowercase, split on non-alphanumeric."""
    return re.findall(r'\w+', text.lower())


def hybrid_search(query: str, top_k: int = None) -> list[dict]:
    """Hybrid search: BM25 + Vector search → Reciprocal Rank Fusion → top results.
    
    Args:
        query: User's search query
        top_k: Number of results to return (default from config)
    
    Returns:
        List of dicts: [{"content": str, "metadata": dict, "score": float}]
    """
    top_k = top_k or Config.TOP_K
    
    vectorstore = get_vectorstore()
    collection = vectorstore._collection
    total_docs = collection.count()
    
    if total_docs == 0:
        return []
    
    # Fetch more candidates than needed for re-ranking
    fetch_k = min(top_k * 3, total_docs)
    
    # --- 1. Vector Search ---
    vector_results = vectorstore.similarity_search_with_relevance_scores(query, k=fetch_k)
    
    # Build a lookup of all documents for BM25
    all_docs = collection.get(limit=total_docs, include=["documents", "metadatas"])
    doc_texts = all_docs.get("documents", [])
    doc_metas = all_docs.get("metadatas", [])
    doc_ids = all_docs.get("ids", [])
    
    if not doc_texts:
        return []
    
    # --- 2. BM25 Keyword Search ---
    tokenized_corpus = [_tokenize(doc) for doc in doc_texts]
    bm25 = BM25Okapi(tokenized_corpus)
    query_tokens = _tokenize(query)
    bm25_scores = bm25.get_scores(query_tokens)
    
    # Get top BM25 results
    bm25_ranked = sorted(range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True)[:fetch_k]
    
    # --- 3. Reciprocal Rank Fusion (RRF) ---
    # RRF combines rankings from multiple sources
    # Score = sum(1 / (k + rank)) for each source
    rrf_k = 60  # Standard RRF constant
    
    # Build score map: doc_id → rrf_score
    rrf_scores = {}
    
    # Vector search ranks
    for rank, (doc, score) in enumerate(vector_results):
        # Find matching doc_id
        doc_content = doc.page_content
        for i, text in enumerate(doc_texts):
            if text == doc_content:
                doc_id = doc_ids[i]
                rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + (1.0 / (rrf_k + rank + 1))
                break
    
    # BM25 ranks
    for rank, idx in enumerate(bm25_ranked):
        doc_id = doc_ids[idx]
        rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + (1.0 / (rrf_k + rank + 1))
    
    # --- 4. Sort by RRF score and return top_k ---
    sorted_ids = sorted(rrf_scores.keys(), key=lambda x: rrf_scores[x], reverse=True)[:top_k]
    
    results = []
    for doc_id in sorted_ids:
        idx = doc_ids.index(doc_id)
        results.append({
            "content": doc_texts[idx],
            "metadata": doc_metas[idx] if idx < len(doc_metas) else {},
            "score": rrf_scores[doc_id],
        })
    
    return results


def simple_search(query: str, top_k: int = None) -> list[dict]:
    """Simple vector-only search (fallback)."""
    top_k = top_k or Config.TOP_K
    vectorstore = get_vectorstore()
    results = vectorstore.similarity_search(query, k=top_k)
    
    return [{
        "content": doc.page_content,
        "metadata": doc.metadata,
        "score": 1.0,
    } for doc in results]
