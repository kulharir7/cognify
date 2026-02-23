"""Cognify — Multi-Agent Document Intelligence."""

import os
import time
import tempfile
import streamlit as st

# --- Page Config ---
st.set_page_config(
    page_title="Cognify — Multi-Agent Document Intelligence",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Authentication ---
def login_page():
    """Beautiful login page."""
    st.markdown("""
    <style>
        .stApp { background: #0a0a1a; }
        .login-container {
            max-width: 420px;
            margin: 80px auto;
            padding: 40px;
            background: rgba(22,27,34,0.8);
            border: 1px solid rgba(102,126,234,0.2);
            border-radius: 20px;
            backdrop-filter: blur(20px);
        }
        .login-logo {
            text-align: center;
            margin-bottom: 8px;
        }
        .login-title {
            text-align: center;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2.2em;
            font-weight: 800;
            letter-spacing: -0.03em;
        }
        .login-subtitle {
            text-align: center;
            color: #6e7681;
            font-size: 0.9em;
            margin-bottom: 30px;
        }
        .login-footer {
            text-align: center;
            color: #30363d;
            font-size: 0.75em;
            margin-top: 24px;
        }
        #MainMenu, footer, header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align:center; padding-top: 60px;">
            <div style="font-size: 4em; margin-bottom: 8px;">🧠</div>
            <div class="login-title">Cognify</div>
            <div class="login-subtitle">Multi-Agent Document Intelligence</div>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter username")
            password = st.text_input("Password", type="password", placeholder="Enter password")
            submit = st.form_submit_button("🔓 Sign In", use_container_width=True, type="primary")
            
            if submit:
                # Check credentials from env or defaults
                valid_user = os.getenv("COGNIFY_USER", "admin")
                valid_pass = os.getenv("COGNIFY_PASS", "cognify123")
                
                if username == valid_user and password == valid_pass:
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials")
        
        st.markdown("""
        <div style="text-align:center; color:#6e7681; font-size:0.8em; margin-top:16px;">
            Default: admin / cognify123<br>
            <span style="color:#30363d;">Set COGNIFY_USER & COGNIFY_PASS in .env to customize</span>
        </div>
        """, unsafe_allow_html=True)

# Check auth
if not st.session_state.get("authenticated", False):
    login_page()
    st.stop()

# --- Imports (after auth to speed up login page) ---
from src.ingest import ingest_file, get_vectorstore
from src.agents import run_query_steps

# --- Premium CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Global */
    .stApp {
        background: #0a0a1a;
        font-family: 'Inter', sans-serif;
    }
    
    /* Hero */
    .hero-container {
        padding: 8px 0 16px 0;
        border-bottom: 1px solid rgba(102,126,234,0.15);
        margin-bottom: 20px;
    }
    .hero-logo {
        display: inline-flex;
        align-items: center;
        gap: 12px;
    }
    .hero-title {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2em;
        font-weight: 800;
        letter-spacing: -0.03em;
        margin: 0;
        display: inline;
    }
    .hero-badge {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        font-size: 0.65em;
        padding: 2px 8px;
        border-radius: 20px;
        font-weight: 600;
        vertical-align: super;
    }
    .hero-subtitle {
        color: #6e7681;
        font-size: 0.92em;
        margin-top: 2px;
    }
    
    /* Pipeline Visualization */
    .pipeline-container {
        display: flex;
        align-items: center;
        gap: 0;
        padding: 14px 20px;
        background: rgba(22,27,34,0.6);
        border: 1px solid rgba(48,54,61,0.5);
        border-radius: 14px;
        margin: 12px 0 20px 0;
    }
    .pipeline-node {
        flex: 1;
        text-align: center;
        padding: 10px 8px;
        border-radius: 10px;
        transition: all 0.3s ease;
    }
    .pipeline-node.waiting {
        opacity: 0.35;
    }
    .pipeline-node.active {
        background: rgba(102,126,234,0.12);
        border: 1px solid rgba(102,126,234,0.3);
        animation: node-pulse 1.5s infinite;
    }
    .pipeline-node.done {
        background: rgba(35,134,54,0.1);
        border: 1px solid rgba(35,134,54,0.3);
    }
    .pipeline-emoji { font-size: 1.4em; }
    .pipeline-label { font-size: 0.78em; color: #8b949e; margin-top: 2px; }
    .pipeline-time { font-size: 0.72em; color: #58a6ff; margin-top: 1px; }
    .pipeline-arrow {
        color: #30363d;
        font-size: 1.2em;
        padding: 0 4px;
    }
    .pipeline-arrow.done { color: #238636; }
    
    @keyframes node-pulse {
        0%, 100% { box-shadow: 0 0 0 0 rgba(102,126,234,0); }
        50% { box-shadow: 0 0 20px 4px rgba(102,126,234,0.15); }
    }
    
    /* Agent Cards */
    .agent-card {
        background: linear-gradient(135deg, rgba(102,126,234,0.06) 0%, rgba(118,75,162,0.06) 100%);
        border: 1px solid rgba(102,126,234,0.15);
        border-radius: 12px;
        padding: 14px 18px;
        margin: 8px 0;
    }
    .agent-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .agent-name { color: #c9d1d9; font-weight: 700; font-size: 1em; }
    .agent-time {
        color: #58a6ff;
        font-size: 0.8em;
        background: rgba(88,166,255,0.1);
        padding: 2px 8px;
        border-radius: 12px;
    }
    .agent-action { color: #8b949e; font-size: 0.88em; margin-top: 6px; }
    .agent-preview {
        color: #b1bac4;
        font-size: 0.82em;
        margin-top: 8px;
        padding: 10px 14px;
        background: rgba(13,17,23,0.6);
        border-radius: 8px;
        border-left: 3px solid rgba(102,126,234,0.4);
        line-height: 1.5;
        max-height: 150px;
        overflow-y: auto;
    }
    
    /* Stat Cards */
    .stat-card {
        background: linear-gradient(135deg, rgba(102,126,234,0.1) 0%, rgba(118,75,162,0.06) 100%);
        border: 1px solid rgba(102,126,234,0.12);
        border-radius: 12px;
        padding: 14px;
        text-align: center;
    }
    .stat-value {
        font-size: 1.8em;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .stat-label { color: #6e7681; font-size: 0.8em; margin-top: 2px; }
    
    /* Source cards */
    .source-card {
        background: rgba(22,27,34,0.8);
        border: 1px solid rgba(48,54,61,0.6);
        border-radius: 10px;
        padding: 12px 16px;
        margin: 6px 0;
    }
    .source-file { color: #f0883e; font-weight: 600; font-size: 0.9em; }
    .source-page { color: #6e7681; font-size: 0.85em; }
    .source-text {
        color: #b1bac4;
        margin-top: 6px;
        font-size: 0.84em;
        line-height: 1.5;
        border-left: 2px solid rgba(240,136,62,0.3);
        padding-left: 10px;
    }
    
    /* Empty state */
    .empty-state {
        text-align: center;
        padding: 80px 20px;
    }
    .empty-icon { font-size: 4em; margin-bottom: 12px; }
    .empty-title { color: #c9d1d9; font-size: 1.3em; font-weight: 600; }
    .empty-desc { color: #6e7681; font-size: 0.95em; margin-top: 6px; }
    .feature-grid {
        display: flex;
        justify-content: center;
        gap: 48px;
        margin-top: 40px;
    }
    .feature-item { text-align: center; }
    .feature-icon { font-size: 2em; margin-bottom: 6px; }
    .feature-name { color: #c9d1d9; font-size: 0.88em; font-weight: 500; }
    .feature-desc { color: #58a6ff; font-size: 0.75em; margin-top: 2px; }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1117 0%, #161b22 100%);
        border-right: 1px solid rgba(48,54,61,0.4);
    }
    [data-testid="stSidebar"] [data-testid="stMarkdown"] h3 {
        color: #c9d1d9;
        font-size: 0.95em;
        font-weight: 600;
    }
    
    /* Chat styling */
    [data-testid="stChatMessage"] {
        background: rgba(22,27,34,0.4);
        border: 1px solid rgba(48,54,61,0.3);
        border-radius: 16px;
        padding: 16px 20px;
        margin: 8px 0;
    }
    /* User message */
    [data-testid="stChatMessage"][data-testid*="user"] {
        background: linear-gradient(135deg, rgba(102,126,234,0.08), rgba(118,75,162,0.05));
        border-color: rgba(102,126,234,0.2);
    }
    /* Chat input */
    [data-testid="stChatInput"] {
        border-radius: 16px !important;
    }
    [data-testid="stChatInput"] textarea {
        background: rgba(22,27,34,0.8) !important;
        border: 1px solid rgba(102,126,234,0.25) !important;
        border-radius: 14px !important;
        color: #c9d1d9 !important;
        font-size: 0.95em !important;
        padding: 14px 18px !important;
    }
    [data-testid="stChatInput"] textarea:focus {
        border-color: rgba(102,126,234,0.6) !important;
        box-shadow: 0 0 0 3px rgba(102,126,234,0.1) !important;
    }
    [data-testid="stChatInput"] button {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        border-radius: 12px !important;
        border: none !important;
    }
    
    /* Hide branding but keep sidebar toggle */
    #MainMenu, footer { visibility: hidden; }
    header { visibility: visible !important; }
    [data-testid="stHeader"] {
        background: transparent !important;
    }
    /* Make sidebar toggle button visible */
    [data-testid="stSidebarCollapsedControl"] {
        color: #667eea !important;
    }
    
    /* Total time badge */
    .total-time {
        display: inline-block;
        background: linear-gradient(135deg, rgba(35,134,54,0.15), rgba(35,134,54,0.05));
        border: 1px solid rgba(35,134,54,0.3);
        color: #3fb950;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.85em;
        font-weight: 600;
        margin-top: 8px;
    }
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("""
<div class="hero-container">
    <div class="hero-logo">
        <span class="hero-title">🧠 Cognify</span>
        <span class="hero-badge">MULTI-AGENT</span>
    </div>
    <div class="hero-subtitle">Upload documents → Ask questions → AI agents research, synthesize & fact-check with citations</div>
</div>
""", unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.markdown("### 📄 Documents")
    uploaded_files = st.file_uploader(
        "Upload files",
        type=["pdf", "txt", "md"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    if uploaded_files:
        if st.button("📥 Ingest Documents", type="primary", use_container_width=True):
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

    st.divider()

    # Stats
    st.markdown("### 📊 Knowledge Base")
    try:
        vs = get_vectorstore()
        chunk_count = vs._collection.count()
    except Exception:
        chunk_count = 0

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f'<div class="stat-card"><div class="stat-value">{chunk_count}</div><div class="stat-label">Chunks</div></div>', unsafe_allow_html=True)
    with c2:
        q_count = len([m for m in st.session_state.get("messages", []) if m["role"] == "user"])
        st.markdown(f'<div class="stat-card"><div class="stat-value">{q_count}</div><div class="stat-label">Queries</div></div>', unsafe_allow_html=True)

    st.divider()

    # Model Configuration
    st.markdown("### 🤖 Model Configuration")
    
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
    
    if provider == "Custom (OpenAI-compatible)":
        base_url = st.text_input("Base URL", value="", placeholder="https://your-api.com/v1")
        model = st.text_input("Model", value="", placeholder="model-name")
    else:
        base_url = st.text_input("Base URL", value=defaults["url"])
        model = st.selectbox("Model", defaults["models"], index=0)
    
    api_key = st.text_input("API Key", type="password", value=os.getenv("LLM_API_KEY", ""))
    
    # Save to session for runtime use
    if api_key:
        os.environ["LLM_API_KEY"] = api_key
    if base_url:
        os.environ["LLM_BASE_URL"] = base_url
    if model:
        os.environ["LLM_MODEL"] = model

    st.divider()

    # Display Settings
    st.markdown("### ⚙️ Display")
    show_trace = st.toggle("Agent Reasoning Trace", value=True)
    show_sources = st.toggle("Source Documents", value=True)
    show_pipeline = st.toggle("Pipeline Visualization", value=True)

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    with col2:
        if st.button("🗑️ KB", use_container_width=True):
            import shutil
            shutil.rmtree("./data/chroma_db", ignore_errors=True)
            st.rerun()

    st.divider()
    st.caption("🔒 Embeddings run locally — your data stays private")
    st.caption(f"👤 Logged in as **{st.session_state.get('username', 'admin')}**")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.messages = []
        st.rerun()

# --- Helper: Pipeline HTML ---
def pipeline_html(step="none", timings=None):
    timings = timings or {}
    steps = [
        ("🔄", "Context", "context_rewriter"),
        ("🔍", "Researcher", "researcher"),
        ("📝", "Synthesizer", "synthesizer"),
        ("✅", "Fact-Checker", "fact_checker"),
    ]
    order = ["context_rewriter", "researcher", "synthesizer", "fact_checker"]
    current_idx = order.index(step) if step in order else -1

    html = '<div class="pipeline-container">'
    for i, (emoji, label, key) in enumerate(steps):
        if i > 0:
            arrow_cls = "done" if i <= current_idx else ""
            html += f'<div class="pipeline-arrow {arrow_cls}">→</div>'

        if key == step:
            cls = "active"
        elif order.index(key) < current_idx:
            cls = "done"
        else:
            cls = "waiting"

        t = timings.get(key, "")
        time_html = f'<div class="pipeline-time">{t}</div>' if t else ""
        html += f'''<div class="pipeline-node {cls}">
            <div class="pipeline-emoji">{emoji}</div>
            <div class="pipeline-label">{label}</div>
            {time_html}
        </div>'''
    html += '</div>'
    return html

# --- Helper: parse sources ---
def parse_sources(retrieved_docs):
    sources = []
    for doc_text in retrieved_docs:
        if doc_text.startswith("[Source"):
            try:
                header = doc_text.split("]\n")[0] + "]"
                text = doc_text.split("]\n", 1)[1] if "]\n" in doc_text else doc_text
                source_info = header.split(": ", 1)[1].rstrip("]") if ": " in header else "unknown"
                parts = source_info.split(", p.")
                sources.append({
                    "source": os.path.basename(parts[0]) if parts else "unknown",
                    "page": parts[1] if len(parts) > 1 else "?",
                    "text": text,
                })
            except Exception:
                sources.append({"source": "document", "page": "?", "text": doc_text[:300]})
    return sources

# --- Empty State ---
if chunk_count == 0 and not st.session_state.get("messages"):
    st.markdown("""
    <div class="empty-state">
        <div class="empty-icon">🔍</div>
        <div class="empty-title">Upload documents to start researching</div>
        <div class="empty-desc">PDF, TXT, Markdown — drag & drop in the sidebar</div>
        <div class="feature-grid">
            <div class="feature-item">
                <div class="feature-icon">🔄</div>
                <div class="feature-name">Context Rewriter</div>
                <div class="feature-desc">Understands follow-ups</div>
            </div>
            <div class="feature-item">
                <div class="feature-icon">🔍</div>
                <div class="feature-name">Researcher</div>
                <div class="feature-desc">Semantic search + extraction</div>
            </div>
            <div class="feature-item">
                <div class="feature-icon">📝</div>
                <div class="feature-name">Synthesizer</div>
                <div class="feature-desc">Structured cited answers</div>
            </div>
            <div class="feature-item">
                <div class="feature-icon">✅</div>
                <div class="feature-name">Fact-Checker</div>
                <div class="feature-desc">Verification against sources</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- Chat ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant":
            if show_trace and msg.get("trace"):
                with st.expander("🔍 Agent Reasoning Trace", expanded=False):
                    for step in msg["trace"]:
                        st.markdown(f"""<div class="agent-card">
    <div class="agent-header">
        <span class="agent-name">{step['agent']}</span>
        <span class="agent-time">⏱ {step.get('time', '?')}</span>
    </div>
    <div class="agent-action">{step['action']}</div>
    <div class="agent-preview">{step.get('output_preview', '')}</div>
</div>""", unsafe_allow_html=True)

            if show_sources and msg.get("sources"):
                with st.expander(f"📚 Sources ({len(msg['sources'])})", expanded=False):
                    for src in msg["sources"]:
                        st.markdown(f"""<div class="source-card">
    <span class="source-file">📄 {src['source']}</span>
    <span class="source-page"> • p.{src['page']}</span>
    <div class="source-text">{src['text'][:300]}{'...' if len(src['text']) > 300 else ''}</div>
</div>""", unsafe_allow_html=True)

            if msg.get("total_time"):
                st.markdown(f'<span class="total-time">⏱ Total: {msg["total_time"]}</span>', unsafe_allow_html=True)

# --- Chat Input ---
if prompt := st.chat_input("Ask anything about your documents..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        start_total = time.time()

        # Build chat history for conversation memory (exclude current message)
        chat_history = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages[:-1]  # exclude current user msg
        ]

        # Pipeline visualization placeholder
        if show_pipeline:
            pipeline_placeholder = st.empty()
            pipeline_placeholder.markdown(pipeline_html("context_rewriter"), unsafe_allow_html=True)

        # Status area
        status_text = st.empty()
        status_text.markdown("🔄 **Context Rewriter** analyzing conversation...")

        # Streaming answer placeholder
        answer_placeholder = st.empty()

        try:
            final_state = None
            streamed_answer = ""
            
            for result in run_query_steps(prompt, chat_history=chat_history, streaming=True):
                # Handle different yield formats
                if len(result) == 2:
                    step_name, data = result
                else:
                    continue
                
                # Stream tokens
                if step_name == "stream_token":
                    streamed_answer += data
                    answer_placeholder.markdown(streamed_answer + "▌")
                    continue
                
                if step_name == "fact_checker_done":
                    final_state = data
                    # Remove cursor
                    answer_placeholder.markdown(final_state["final_answer"])
                    continue
                
                if step_name == "fact_checker_start":
                    status_text.markdown("✅ **Fact-Checker** streaming verified answer...")
                    if show_pipeline:
                        timings = data.get("timings", {})
                        pipeline_placeholder.markdown(pipeline_html("fact_checker", {k: f"{v:.1f}s" for k, v in timings.items()}), unsafe_allow_html=True)
                    continue
                
                # Regular agent steps
                state = data
                final_state = state
                timings = state.get("timings", {})

                if show_pipeline:
                    pipeline_placeholder.markdown(pipeline_html(step_name, {k: f"{v:.1f}s" for k, v in timings.items()}), unsafe_allow_html=True)

                if step_name == "context_rewriter":
                    status_text.markdown(f"🔍 **Researcher** searching knowledge base...")
                    if show_pipeline:
                        pipeline_placeholder.markdown(pipeline_html("researcher", {k: f"{v:.1f}s" for k, v in timings.items()}), unsafe_allow_html=True)
                elif step_name == "researcher":
                    status_text.markdown(f"📝 **Synthesizer** creating cited answer... (Researcher: {timings.get('researcher', 0):.1f}s)")
                    if show_pipeline:
                        pipeline_placeholder.markdown(pipeline_html("synthesizer", {k: f"{v:.1f}s" for k, v in timings.items()}), unsafe_allow_html=True)
                elif step_name == "synthesizer":
                    status_text.markdown(f"✅ **Fact-Checker** verifying claims... (Synthesizer: {timings.get('synthesizer', 0):.1f}s)")
                    if show_pipeline:
                        pipeline_placeholder.markdown(pipeline_html("fact_checker", {k: f"{v:.1f}s" for k, v in timings.items()}), unsafe_allow_html=True)

            total_elapsed = time.time() - start_total

            # Clear progress
            status_text.empty()
            if show_pipeline:
                final_timings = {k: f"{v:.1f}s" for k, v in final_state.get("timings", {}).items()}
                pipeline_placeholder.markdown(pipeline_html("done", final_timings), unsafe_allow_html=True)

            # Answer already streamed above via answer_placeholder
            answer = final_state["final_answer"]
            trace = final_state["agent_trace"]
            sources = parse_sources(final_state.get("retrieved_docs", []))

            # Time badge
            total_time_str = f"{total_elapsed:.1f}s"
            st.markdown(f'<span class="total-time">⏱ Total: {total_time_str}</span>', unsafe_allow_html=True)

            # Trace
            if show_trace and trace:
                with st.expander("🔍 Agent Reasoning Trace", expanded=False):
                    for step in trace:
                        st.markdown(f"""<div class="agent-card">
    <div class="agent-header">
        <span class="agent-name">{step['agent']}</span>
        <span class="agent-time">⏱ {step.get('time', '?')}</span>
    </div>
    <div class="agent-action">{step['action']}</div>
    <div class="agent-preview">{step.get('output_preview', '')}</div>
</div>""", unsafe_allow_html=True)

            # Sources
            if show_sources and sources:
                with st.expander(f"📚 Sources ({len(sources)})", expanded=False):
                    for src in sources:
                        st.markdown(f"""<div class="source-card">
    <span class="source-file">📄 {src['source']}</span>
    <span class="source-page"> • p.{src['page']}</span>
    <div class="source-text">{src['text'][:300]}{'...' if len(src['text']) > 300 else ''}</div>
</div>""", unsafe_allow_html=True)

            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "trace": trace,
                "sources": sources,
                "total_time": total_time_str,
            })

        except Exception as e:
            status_text.empty()
            if show_pipeline:
                pipeline_placeholder.empty()
            error_msg = f"❌ Error: {str(e)}"
            st.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
