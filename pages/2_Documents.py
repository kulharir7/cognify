"""Cognify — 📁 Document Manager."""

import os
import shutil
import tempfile
import streamlit as st

st.set_page_config(page_title="Cognify — Documents", page_icon="🧠", layout="wide")

from src.ui import check_auth, inject_css, render_header, render_sidebar_footer

if not check_auth():
    st.stop()

inject_css()
render_header()

from src.ingest import ingest_file, ingest_url, get_vectorstore

# --- Page Header ---
st.markdown('<div class="page-title">📁 Document Manager</div>', unsafe_allow_html=True)
st.markdown('<div class="page-desc">Upload, view, and manage your knowledge base documents</div>', unsafe_allow_html=True)

# --- Upload Section ---
st.markdown("### 📤 Upload Documents")
col1, col2 = st.columns([3, 1])

with col1:
    uploaded_files = st.file_uploader(
        "Drop files here",
        type=["pdf", "txt", "md"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

with col2:
    if uploaded_files:
        if st.button("📥 Ingest All", type="primary", use_container_width=True):
            progress = st.progress(0)
            total_chunks = 0
            for i, uf in enumerate(uploaded_files):
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uf.name)[1]) as tmp:
                    tmp.write(uf.read())
                    tmp_path = tmp.name
                try:
                    chunks = ingest_file(tmp_path)
                    total_chunks += chunks
                    st.success(f"✅ {uf.name} — {chunks} chunks")
                except Exception as e:
                    st.error(f"❌ {uf.name}: {e}")
                finally:
                    os.unlink(tmp_path)
                progress.progress((i + 1) / len(uploaded_files))
            st.balloons()
            st.info(f"📊 **{total_chunks}** chunks indexed")
            st.rerun()

st.divider()

# --- URL Ingestion ---
st.markdown("### 🌐 Ingest from URL")
url_col1, url_col2 = st.columns([4, 1])
with url_col1:
    url_input = st.text_input("Paste URL", placeholder="https://example.com/article", label_visibility="collapsed")
with url_col2:
    if url_input and st.button("🌐 Ingest", type="primary", use_container_width=True):
        with st.spinner(f"Scraping {url_input}..."):
            try:
                chunks = ingest_url(url_input)
                st.success(f"✅ {url_input} — {chunks} chunks")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error: {e}")

st.divider()

# --- Knowledge Base Stats ---
st.markdown("### 📊 Knowledge Base Overview")

try:
    vs = get_vectorstore()
    collection = vs._collection
    total_chunks = collection.count()
except Exception:
    total_chunks = 0
    collection = None

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f'<div class="stat-card"><div class="stat-value">{total_chunks}</div><div class="stat-label">Total Chunks</div></div>', unsafe_allow_html=True)

# Get unique sources
source_names = set()
results = {"metadatas": [], "ids": []}
if collection and total_chunks > 0:
    try:
        results = collection.get(limit=total_chunks, include=["metadatas"])
        for meta in results.get("metadatas", []):
            if meta and "source" in meta:
                source_names.add(os.path.basename(meta["source"]))
    except Exception:
        pass

with c2:
    st.markdown(f'<div class="stat-card"><div class="stat-value">{len(source_names)}</div><div class="stat-label">Documents</div></div>', unsafe_allow_html=True)

with c3:
    avg = total_chunks // max(len(source_names), 1)
    st.markdown(f'<div class="stat-card"><div class="stat-value">{avg}</div><div class="stat-label">Avg Chunks/Doc</div></div>', unsafe_allow_html=True)

st.divider()

# --- Document List ---
st.markdown("### 📄 Indexed Documents")

if source_names:
    for doc_name in sorted(source_names):
        doc_chunks = sum(
            1 for meta in results.get("metadatas", [])
            if meta and os.path.basename(meta.get("source", "")) == doc_name
        )
        
        col1, col2, col3 = st.columns([4, 1, 1])
        with col1:
            st.markdown(f"📄 **{doc_name}**")
        with col2:
            st.caption(f"{doc_chunks} chunks")
        with col3:
            if st.button("🗑️", key=f"del_{doc_name}", help=f"Delete {doc_name}"):
                try:
                    ids_to_delete = [
                        results["ids"][i]
                        for i, meta in enumerate(results.get("metadatas", []))
                        if meta and os.path.basename(meta.get("source", "")) == doc_name
                    ]
                    if ids_to_delete:
                        collection.delete(ids=ids_to_delete)
                        st.success(f"Deleted {doc_name} ({len(ids_to_delete)} chunks)")
                        st.rerun()
                except Exception as e:
                    st.error(f"Error deleting: {e}")
else:
    st.info("No documents indexed yet. Upload files above to get started.")

st.divider()

# --- Danger Zone ---
st.markdown("### ⚠️ Danger Zone")
if st.button("🗑️ Clear Entire Knowledge Base", type="secondary", use_container_width=True):
    shutil.rmtree("./data/chroma_db", ignore_errors=True)
    st.success("Knowledge base cleared!")
    st.rerun()

# --- Sidebar ---
with st.sidebar:
    st.markdown("### 📁 Documents")
    st.info(f"**{len(source_names)}** documents • **{total_chunks}** chunks")
    render_sidebar_footer()
