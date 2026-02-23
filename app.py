"""Cognify — 💬 Chat Page (Main)."""

import os
import time
import tempfile
import streamlit as st

st.set_page_config(
    page_title="Cognify — Chat",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

from src.ui import check_auth, inject_css, render_header, render_sidebar_footer, pipeline_html, parse_sources

if not check_auth():
    st.stop()

inject_css()
render_header()

from src.ingest import ingest_file, get_vectorstore
from src.agents import run_query_steps

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

    # Display Settings
    st.markdown("### ⚙️ Display")
    show_trace = st.toggle("Agent Reasoning Trace", value=True)
    show_sources = st.toggle("Source Documents", value=True)
    show_pipeline = st.toggle("Pipeline Visualization", value=True)

    st.divider()

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    render_sidebar_footer()

# --- Empty State ---
if chunk_count == 0 and not st.session_state.get("messages"):
    st.markdown("""
    <div style="text-align:center; padding: 80px 20px;">
        <div style="font-size: 4em; margin-bottom: 12px;">🔍</div>
        <div style="color: #c9d1d9; font-size: 1.3em; font-weight: 600;">Upload documents to start researching</div>
        <div style="color: #6e7681; font-size: 0.95em; margin-top: 6px;">PDF, TXT, Markdown — drag & drop in the sidebar</div>
        <div style="display:flex; justify-content:center; gap:48px; margin-top:40px;">
            <div style="text-align:center;">
                <div style="font-size:2em;">🔄</div>
                <div style="color:#c9d1d9; font-size:0.88em; font-weight:500;">Context</div>
                <div style="color:#58a6ff; font-size:0.75em;">Follow-up aware</div>
            </div>
            <div style="text-align:center;">
                <div style="font-size:2em;">🔍</div>
                <div style="color:#c9d1d9; font-size:0.88em; font-weight:500;">Researcher</div>
                <div style="color:#58a6ff; font-size:0.75em;">Semantic search</div>
            </div>
            <div style="text-align:center;">
                <div style="font-size:2em;">📝</div>
                <div style="color:#c9d1d9; font-size:0.88em; font-weight:500;">Synthesizer</div>
                <div style="color:#58a6ff; font-size:0.75em;">Cited answers</div>
            </div>
            <div style="text-align:center;">
                <div style="font-size:2em;">✅</div>
                <div style="color:#c9d1d9; font-size:0.88em; font-weight:500;">Fact-Checker</div>
                <div style="color:#58a6ff; font-size:0.75em;">Verification</div>
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

        chat_history = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages[:-1]
        ]

        if show_pipeline:
            pipeline_placeholder = st.empty()
            pipeline_placeholder.markdown(pipeline_html("context_rewriter"), unsafe_allow_html=True)

        status_text = st.empty()
        status_text.markdown("🔄 **Context Rewriter** analyzing conversation...")
        answer_placeholder = st.empty()

        try:
            final_state = None
            streamed_answer = ""

            for result in run_query_steps(prompt, chat_history=chat_history, streaming=True):
                if len(result) != 2:
                    continue
                step_name, data = result

                if step_name == "stream_token":
                    streamed_answer += data
                    answer_placeholder.markdown(streamed_answer + "▌")
                    continue

                if step_name == "fact_checker_done":
                    final_state = data
                    answer_placeholder.markdown(final_state["final_answer"])
                    continue

                if step_name == "fact_checker_start":
                    status_text.markdown("✅ **Fact-Checker** streaming verified answer...")
                    if show_pipeline:
                        timings = data.get("timings", {})
                        pipeline_placeholder.markdown(pipeline_html("fact_checker", {k: f"{v:.1f}s" for k, v in timings.items()}), unsafe_allow_html=True)
                    continue

                state = data
                final_state = state
                timings = state.get("timings", {})

                if show_pipeline:
                    pipeline_placeholder.markdown(pipeline_html(step_name, {k: f"{v:.1f}s" for k, v in timings.items()}), unsafe_allow_html=True)

                if step_name == "context_rewriter":
                    status_text.markdown("🔍 **Researcher** searching knowledge base...")
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
            status_text.empty()
            
            if show_pipeline and final_state:
                final_timings = {k: f"{v:.1f}s" for k, v in final_state.get("timings", {}).items()}
                pipeline_placeholder.markdown(pipeline_html("done", final_timings), unsafe_allow_html=True)

            answer = final_state["final_answer"]
            trace = final_state["agent_trace"]
            sources = parse_sources(final_state.get("retrieved_docs", []))

            total_time_str = f"{total_elapsed:.1f}s"
            st.markdown(f'<span class="total-time">⏱ Total: {total_time_str}</span>', unsafe_allow_html=True)

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
