"""Cognify — ⚙️ Settings."""

import os
import streamlit as st

st.set_page_config(page_title="Cognify — Settings", page_icon="🧠", layout="wide")

from src.ui import check_auth, inject_css, render_header, render_sidebar_footer

if not check_auth():
    st.stop()

inject_css()
render_header()

# --- Page Header ---
st.markdown('<div class="page-title">⚙️ Settings</div>', unsafe_allow_html=True)
st.markdown('<div class="page-desc">Configure LLM provider, model, and application settings</div>', unsafe_allow_html=True)

# --- Model Configuration ---
st.markdown("### 🤖 LLM Configuration")

provider = st.selectbox(
    "Provider",
    ["Ollama Cloud", "OpenAI", "Anthropic", "Custom (OpenAI-compatible)"],
    index=0,
)

provider_defaults = {
    "Ollama Cloud": {
        "url": "https://ollama.com/v1",
        "models": ["mistral-large-3:675b", "deepseek-v3.1:671b", "qwen3-coder:480b", "gpt-oss:120b", "gpt-oss:20b", "minimax-m2"],
    },
    "OpenAI": {
        "url": "https://api.openai.com/v1",
        "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
    },
    "Anthropic": {
        "url": "https://api.anthropic.com/v1",
        "models": ["claude-sonnet-4-20250514", "claude-3-5-haiku-20241022", "claude-opus-4-20250514"],
    },
    "Custom (OpenAI-compatible)": {
        "url": "",
        "models": [],
    },
}

defaults = provider_defaults[provider]

col1, col2 = st.columns(2)
with col1:
    if provider == "Custom (OpenAI-compatible)":
        base_url = st.text_input("Base URL", value=os.getenv("LLM_BASE_URL", ""), placeholder="https://your-api.com/v1")
        model = st.text_input("Model", value=os.getenv("LLM_MODEL", ""), placeholder="model-name")
    else:
        base_url = st.text_input("Base URL", value=defaults["url"])
        model = st.selectbox("Main Model", defaults["models"], index=0)

with col2:
    api_key = st.text_input("API Key", type="password", value=os.getenv("LLM_API_KEY", ""), placeholder="Enter your API key")
    if provider != "Custom (OpenAI-compatible)":
        fast_model_options = defaults["models"]
        fast_idx = min(1, len(fast_model_options) - 1) if len(fast_model_options) > 1 else 0
        fast_model = st.selectbox("Fast Model (for Researcher)", fast_model_options, index=fast_idx)
    else:
        fast_model = st.text_input("Fast Model", value="", placeholder="fast-model-name")

if st.button("💾 Save Settings", type="primary", use_container_width=True):
    if api_key:
        os.environ["LLM_API_KEY"] = api_key
    if base_url:
        os.environ["LLM_BASE_URL"] = base_url
    if model:
        os.environ["LLM_MODEL"] = model
    if fast_model:
        os.environ["LLM_FAST_MODEL"] = fast_model
    st.success("✅ Settings saved! Changes take effect on next query.")

st.divider()

# --- RAG Configuration ---
st.markdown("### 🔧 RAG Configuration")

col1, col2, col3 = st.columns(3)
with col1:
    chunk_size = st.number_input("Chunk Size", value=int(os.getenv("CHUNK_SIZE", "1000")), min_value=200, max_value=4000, step=100)
with col2:
    chunk_overlap = st.number_input("Chunk Overlap", value=int(os.getenv("CHUNK_OVERLAP", "200")), min_value=0, max_value=1000, step=50)
with col3:
    top_k = st.number_input("Top K Results", value=int(os.getenv("TOP_K", "5")), min_value=1, max_value=20, step=1)

if st.button("💾 Save RAG Settings", use_container_width=True):
    os.environ["CHUNK_SIZE"] = str(chunk_size)
    os.environ["CHUNK_OVERLAP"] = str(chunk_overlap)
    os.environ["TOP_K"] = str(top_k)
    st.success("✅ RAG settings saved!")

st.divider()

# --- Current Configuration ---
st.markdown("### 📋 Current Configuration")

config_data = {
    "Provider": provider,
    "Base URL": os.getenv("LLM_BASE_URL", "https://ollama.com/v1"),
    "Model": os.getenv("LLM_MODEL", "mistral-large-3:675b"),
    "Fast Model": os.getenv("LLM_FAST_MODEL", "same as main"),
    "API Key": "●●●●●●●●" if os.getenv("LLM_API_KEY") else "⚠️ Not set",
    "Chunk Size": os.getenv("CHUNK_SIZE", "1000"),
    "Chunk Overlap": os.getenv("CHUNK_OVERLAP", "200"),
    "Top K": os.getenv("TOP_K", "5"),
    "Embedding Model": os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
}

for key, val in config_data.items():
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(f"**{key}**")
    with col2:
        st.code(val, language=None)

# --- Sidebar ---
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    st.info(f"Provider: **{provider}**\nModel: **{os.getenv('LLM_MODEL', 'mistral-large-3:675b')}**")
    render_sidebar_footer()
