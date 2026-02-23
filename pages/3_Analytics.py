"""Cognify — 📊 Analytics Dashboard."""

import streamlit as st

st.set_page_config(page_title="Cognify — Analytics", page_icon="🧠", layout="wide")

from src.ui import check_auth, inject_css, render_header, render_sidebar_footer

if not check_auth():
    st.stop()

inject_css()
render_header()

from src.ingest import get_vectorstore

# --- Page Header ---
st.markdown('<div class="page-title">📊 Analytics Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="page-desc">Usage statistics, agent performance, and knowledge base insights</div>', unsafe_allow_html=True)

# --- Gather Data ---
messages = st.session_state.get("messages", [])
user_msgs = [m for m in messages if m["role"] == "user"]
asst_msgs = [m for m in messages if m["role"] == "assistant"]

try:
    vs = get_vectorstore()
    chunk_count = vs._collection.count()
except Exception:
    chunk_count = 0

# --- Top Stats ---
times = []
for m in asst_msgs:
    if m.get("total_time"):
        try:
            times.append(float(m["total_time"].rstrip("s")))
        except (ValueError, AttributeError):
            pass
avg_time = f"{sum(times)/len(times):.1f}s" if times else "—"

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="stat-card"><div class="stat-value">{len(user_msgs)}</div><div class="stat-label">Questions Asked</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="stat-card"><div class="stat-value">{len(asst_msgs)}</div><div class="stat-label">Answers Generated</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="stat-card"><div class="stat-value">{chunk_count}</div><div class="stat-label">Indexed Chunks</div></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="stat-card"><div class="stat-value">{avg_time}</div><div class="stat-label">Avg Response Time</div></div>', unsafe_allow_html=True)

st.divider()

# --- Agent Performance ---
st.markdown("### ⏱️ Agent Performance")

if asst_msgs:
    agent_times = {"🔄 Context Rewriter": [], "🔍 Researcher": [], "📝 Synthesizer": [], "✅ Fact-Checker": []}
    
    for m in asst_msgs:
        for step in m.get("trace", []):
            agent_name = step.get("agent", "")
            time_str = step.get("time", "")
            if agent_name in agent_times and time_str:
                try:
                    agent_times[agent_name].append(float(time_str.rstrip("s")))
                except (ValueError, AttributeError):
                    pass
    
    cols = st.columns(4)
    for i, (agent, times_list) in enumerate(agent_times.items()):
        with cols[i]:
            if times_list:
                avg = sum(times_list) / len(times_list)
                st.metric(agent, f"{avg:.1f}s avg", f"{len(times_list)} calls")
            else:
                st.metric(agent, "—", "0 calls")

    st.divider()

    st.markdown("### 📈 Response Time History")
    if times:
        import pandas as pd
        df = pd.DataFrame({
            "Query #": list(range(1, len(times) + 1)),
            "Response Time (s)": times,
        })
        st.line_chart(df.set_index("Query #"), color="#667eea")
    else:
        st.info("No timing data yet.")

    st.divider()

    st.markdown("### 💬 Recent Questions")
    for i, m in enumerate(reversed(user_msgs[-10:])):
        st.markdown(f"**Q{len(user_msgs) - i}:** {m['content']}")
else:
    st.info("No analytics data yet. Start asking questions on the Chat page!")

# --- Sidebar ---
with st.sidebar:
    st.markdown("### 📊 Analytics")
    st.info(f"**{len(user_msgs)}** questions • **{avg_time}** avg time")
    render_sidebar_footer()
