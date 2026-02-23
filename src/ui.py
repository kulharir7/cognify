"""Shared UI components — CSS, auth, header, sidebar base."""

import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


def check_auth():
    """Check if user is authenticated. Shows login page if not."""
    if st.session_state.get("authenticated", False):
        return True
    
    st.markdown(get_login_css(), unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align:center; padding-top: 60px;">
            <div style="font-size: 4em; margin-bottom: 8px;">🧠</div>
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
                -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                font-size: 2.2em; font-weight: 800; letter-spacing: -0.03em;">Cognify</div>
            <div style="color: #6e7681; font-size: 0.9em; margin-bottom: 30px;">Multi-Agent Document Intelligence</div>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter username")
            password = st.text_input("Password", type="password", placeholder="Enter password")
            submit = st.form_submit_button("🔓 Sign In", use_container_width=True, type="primary")
            
            if submit:
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
            Default: admin / cognify123
        </div>
        """, unsafe_allow_html=True)
    
    return False


def get_login_css():
    return """<style>
    .stApp { background: #0a0a1a; }
    #MainMenu, footer { visibility: hidden; }
    </style>"""


def inject_css():
    """Inject the premium dark theme CSS."""
    st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
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
    
    /* Pipeline */
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
    .pipeline-node.waiting { opacity: 0.35; }
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
    .pipeline-arrow { color: #30363d; font-size: 1.2em; padding: 0 4px; }
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
    .agent-header { display: flex; justify-content: space-between; align-items: center; }
    .agent-name { color: #c9d1d9; font-weight: 700; font-size: 1em; }
    .agent-time {
        color: #58a6ff; font-size: 0.8em;
        background: rgba(88,166,255,0.1); padding: 2px 8px; border-radius: 12px;
    }
    .agent-action { color: #8b949e; font-size: 0.88em; margin-top: 6px; }
    .agent-preview {
        color: #b1bac4; font-size: 0.82em; margin-top: 8px; padding: 10px 14px;
        background: rgba(13,17,23,0.6); border-radius: 8px;
        border-left: 3px solid rgba(102,126,234,0.4);
        line-height: 1.5; max-height: 150px; overflow-y: auto;
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
        font-size: 1.8em; font-weight: 800;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
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
        color: #b1bac4; margin-top: 6px; font-size: 0.84em; line-height: 1.5;
        border-left: 2px solid rgba(240,136,62,0.3); padding-left: 10px;
    }
    
    /* Chat */
    [data-testid="stChatMessage"] {
        background: rgba(22,27,34,0.4);
        border: 1px solid rgba(48,54,61,0.3);
        border-radius: 16px;
        padding: 16px 20px;
        margin: 8px 0;
    }
    [data-testid="stChatMessage"][data-testid*="user"] {
        background: linear-gradient(135deg, rgba(102,126,234,0.08), rgba(118,75,162,0.05));
        border-color: rgba(102,126,234,0.2);
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
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1117 0%, #161b22 100%);
        border-right: 1px solid rgba(48,54,61,0.4);
    }
    
    /* Hide branding but keep sidebar toggle */
    #MainMenu, footer { visibility: hidden; }
    header { visibility: visible !important; }
    [data-testid="stHeader"] { background: transparent !important; }
    
    /* Data table */
    .doc-table {
        width: 100%;
        border-collapse: collapse;
        margin: 12px 0;
    }
    .doc-table th {
        background: rgba(102,126,234,0.1);
        color: #c9d1d9;
        padding: 10px 14px;
        text-align: left;
        font-size: 0.85em;
        border-bottom: 1px solid rgba(48,54,61,0.5);
    }
    .doc-table td {
        color: #b1bac4;
        padding: 10px 14px;
        font-size: 0.85em;
        border-bottom: 1px solid rgba(48,54,61,0.2);
    }
    .doc-table tr:hover td {
        background: rgba(102,126,234,0.05);
    }
    
    /* Page title */
    .page-title {
        color: #c9d1d9;
        font-size: 1.5em;
        font-weight: 700;
        margin-bottom: 4px;
    }
    .page-desc {
        color: #6e7681;
        font-size: 0.9em;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)


def render_header():
    """Render the Cognify header."""
    st.markdown("""
    <div class="hero-container">
        <div>
            <span class="hero-title">🧠 Cognify</span>
            <span class="hero-badge">MULTI-AGENT</span>
        </div>
        <div class="hero-subtitle">Multi-Agent Document Intelligence</div>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar_footer():
    """Render common sidebar footer with logout."""
    st.divider()
    st.caption("🔒 Embeddings run locally — your data stays private")
    st.caption(f"👤 **{st.session_state.get('username', 'admin')}**")
    if st.button("🚪 Logout", use_container_width=True, key="logout_btn"):
        st.session_state.authenticated = False
        st.session_state.messages = []
        st.rerun()


def render_pipeline(step="none", timings=None):
    """Render pipeline visualization using native Streamlit columns."""
    timings = timings or {}
    steps = [
        ("🔄", "Context", "context_rewriter"),
        ("🔍", "Researcher", "researcher"),
        ("📝", "Synthesizer", "synthesizer"),
        ("✅", "Fact-Checker", "fact_checker"),
    ]
    order = ["context_rewriter", "researcher", "synthesizer", "fact_checker"]
    current_idx = order.index(step) if step in order else -1

    # Build columns: agent → arrow → agent → arrow → ...
    cols = st.columns([3, 1, 3, 1, 3, 1, 3])
    
    col_idx = 0
    for i, (emoji, label, key) in enumerate(steps):
        if i > 0:
            # Arrow column
            with cols[col_idx]:
                arrow = "✅→" if order.index(key) <= current_idx else "→"
                st.markdown(f"<div style='text-align:center; padding-top:18px; color:#30363d; font-size:1.3em;'>{arrow}</div>", unsafe_allow_html=True)
            col_idx += 1
        
        with cols[col_idx]:
            if key == step:
                color = "#667eea"
                bg = "rgba(102,126,234,0.12)"
                border = "1px solid rgba(102,126,234,0.4)"
            elif order.index(key) < current_idx:
                color = "#3fb950"
                bg = "rgba(35,134,54,0.1)"
                border = "1px solid rgba(35,134,54,0.3)"
            else:
                color = "#6e7681"
                bg = "rgba(22,27,34,0.4)"
                border = "1px solid rgba(48,54,61,0.3)"
            
            t = timings.get(key, "")
            time_str = f"<div style='font-size:0.7em; color:#58a6ff;'>{t}</div>" if t else ""
            
            st.markdown(f"""<div style="text-align:center; padding:12px 8px; background:{bg}; border:{border}; border-radius:12px;">
<div style="font-size:1.5em;">{emoji}</div>
<div style="font-size:0.8em; color:{color}; font-weight:600;">{label}</div>
{time_str}
</div>""", unsafe_allow_html=True)
        col_idx += 1


def parse_sources(retrieved_docs):
    """Parse source information from retrieved documents."""
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
