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

from src.ui import check_auth, inject_css, render_header, render_sidebar_footer, render_pipeline, parse_sources
from src.export import export_markdown, export_single_answer

if not check_auth():
    st.stop()

inject_css()
render_header()

from src.ingest import ingest_file, ingest_url, get_vectorstore
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

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    with col2:
        if st.session_state.get("messages"):
            md_export = export_markdown(st.session_state.messages)
            st.download_button(
                "📥 Export",
                data=md_export,
                file_name="cognify_chat.md",
                mime="text/markdown",
                use_container_width=True,
            )

    render_sidebar_footer()

# --- Check if API key is configured ---
if not os.getenv("LLM_API_KEY"):
    st.warning("⚠️ **No API key configured!** Go to ⚙️ Settings page and add your LLM API key to start using Cognify.")
    st.markdown("""
    **Supported providers:**
    - 🟢 **Ollama Cloud** — [Get free key](https://ollama.com) (Free/Pro/Max plans)
    - 🟢 **OpenAI** — [Get key](https://platform.openai.com/api-keys)
    - 🟢 **Anthropic** — [Get key](https://console.anthropic.com/)
    - 🟢 **Any OpenAI-compatible API**
    """)

# --- Empty State ---
if chunk_count == 0 and not st.session_state.get("messages"):
    st.info("📄 Upload documents in the sidebar to start researching. Then ask questions below!")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown("🔄 **Context**\n\nFollow-up aware")
    with c2:
        st.markdown("🔍 **Researcher**\n\nHybrid search")
    with c3:
        st.markdown("📝 **Synthesizer**\n\nCited answers")
    with c4:
        st.markdown("✅ **Fact-Checker**\n\nVerification")

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

        answer_placeholder = st.empty()
        status_container = st.status("🧠 **Agent Pipeline Running...**", expanded=True)

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
                    status_container.write("✅ **Fact-Checker** — streaming verified answer...")
                    continue

                state = data
                final_state = state
                timings = state.get("timings", {})

                if step_name == "context_rewriter":
                    t = timings.get("context_rewriter", 0)
                    status_container.write(f"🔄 **Context Rewriter** — done ({t:.1f}s)")
                    status_container.write("🔍 **Researcher** — searching knowledge base...")
                elif step_name == "researcher":
                    t = timings.get("researcher", 0)
                    status_container.write(f"🔍 **Researcher** — done ({t:.1f}s)")
                    status_container.write("📝 **Synthesizer** — creating cited answer...")
                elif step_name == "synthesizer":
                    t = timings.get("synthesizer", 0)
                    status_container.write(f"📝 **Synthesizer** — done ({t:.1f}s)")
                    status_container.write("✅ **Fact-Checker** — verifying claims...")

            total_elapsed = time.time() - start_total
            
            # Finalize status
            if final_state:
                t = final_state.get("timings", {})
                status_container.write(f"✅ **Fact-Checker** — done ({t.get('fact_checker', 0):.1f}s)")
            status_container.update(label=f"✅ **Complete** — {total_elapsed:.1f}s total", state="complete", expanded=False)

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

            # Export button for this answer
            q_num = len([m for m in st.session_state.messages if m["role"] == "user"])
            single_md = export_single_answer(prompt, answer, sources, trace)
            st.download_button(
                "📥 Export Answer",
                data=single_md,
                file_name=f"cognify_answer_{q_num}.md",
                mime="text/markdown",
                key=f"export_{q_num}_{time.time()}",
            )

            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "trace": trace,
                "sources": sources,
                "total_time": total_time_str,
            })

        except Exception as e:
            status_container.update(label="❌ Error", state="error", expanded=True)
            error_msg = f"❌ Error: {str(e)}"
            st.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
