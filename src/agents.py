"""Multi-agent pipeline using LangGraph — Researcher, Synthesizer, Fact-Checker."""

import time
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage
from src.llm import get_llm
from src.ingest import get_vectorstore
from src.config import Config


# --- State ---

class AgentState(TypedDict):
    query: str
    retrieved_docs: list[str]
    research_output: str
    synthesis: str
    fact_check: str
    final_answer: str
    agent_trace: list[dict]
    timings: dict


# --- Agent Nodes ---

def researcher(state: AgentState) -> AgentState:
    """Retrieve relevant chunks and extract key information."""
    start = time.time()
    vectorstore = get_vectorstore()
    results = vectorstore.similarity_search(state["query"], k=Config.TOP_K)

    retrieved = []
    for i, doc in enumerate(results):
        source = doc.metadata.get("source", "unknown")
        page = doc.metadata.get("page", "?")
        retrieved.append(f"[Source {i+1}: {source}, p.{page}]\n{doc.page_content}")

    state["retrieved_docs"] = retrieved

    llm = get_llm(fast=True)
    prompt = f"""You are a Research Agent. Analyze these document excerpts and extract key findings relevant to the query.

Query: {state['query']}

Documents:
{"---".join(retrieved)}

Extract:
1. Key facts and data points
2. Relevant quotes with source references [Source N]
3. Any contradictions or gaps

Be thorough but concise. Use bullet points."""

    response = llm.invoke([
        SystemMessage(content="You are a meticulous research agent. Extract facts precisely with source citations."),
        HumanMessage(content=prompt)
    ])
    elapsed = time.time() - start
    state["research_output"] = response.content
    state["agent_trace"].append({
        "agent": "🔍 Researcher",
        "action": f"Retrieved {len(retrieved)} chunks, extracted key findings",
        "output_preview": response.content[:300] + "..." if len(response.content) > 300 else response.content,
        "time": f"{elapsed:.1f}s",
    })
    state["timings"]["researcher"] = elapsed
    return state


def synthesizer(state: AgentState) -> AgentState:
    """Synthesize research into a clear, cited answer."""
    start = time.time()
    llm = get_llm()
    prompt = f"""You are a Synthesis Agent. Create a clear, well-structured answer using the research findings.

Query: {state['query']}

Research Findings:
{state['research_output']}

Original Sources:
{"---".join(state['retrieved_docs'])}

Rules:
- Cite sources using [Source N] format
- Use clear headings and bullet points
- Be comprehensive but readable
- If information is missing, say so clearly"""

    response = llm.invoke([
        SystemMessage(content="You are a synthesis expert. Create clear, well-cited, structured answers."),
        HumanMessage(content=prompt)
    ])
    elapsed = time.time() - start
    state["synthesis"] = response.content
    state["agent_trace"].append({
        "agent": "📝 Synthesizer",
        "action": "Created structured answer with citations",
        "output_preview": response.content[:300] + "..." if len(response.content) > 300 else response.content,
        "time": f"{elapsed:.1f}s",
    })
    state["timings"]["synthesizer"] = elapsed
    return state


def fact_checker(state: AgentState) -> AgentState:
    """Verify claims against source documents."""
    start = time.time()
    llm = get_llm()
    prompt = f"""You are a Fact-Check Agent. Verify the synthesized answer against the original sources.

Synthesized Answer:
{state['synthesis']}

Original Sources:
{"---".join(state['retrieved_docs'])}

For each major claim:
- ✅ VERIFIED — directly supported by sources
- ⚠️ PARTIALLY SUPPORTED — partially supported
- ❌ NOT FOUND — no source supports it

Then provide the FINAL VERIFIED ANSWER — clean, professional, with only well-supported claims. 
Keep the [Source N] citations. Use markdown formatting."""

    response = llm.invoke([
        SystemMessage(content="You are a rigorous fact-checker. Output a clean, verified final answer."),
        HumanMessage(content=prompt)
    ])
    elapsed = time.time() - start
    state["fact_check"] = response.content
    state["final_answer"] = response.content
    state["agent_trace"].append({
        "agent": "✅ Fact-Checker",
        "action": "Verified all claims against sources",
        "output_preview": response.content[:300] + "..." if len(response.content) > 300 else response.content,
        "time": f"{elapsed:.1f}s",
    })
    state["timings"]["fact_checker"] = elapsed
    return state


# --- Build Graph ---

def build_graph():
    """Create the multi-agent LangGraph pipeline."""
    workflow = StateGraph(AgentState)

    workflow.add_node("researcher", researcher)
    workflow.add_node("synthesizer", synthesizer)
    workflow.add_node("fact_checker", fact_checker)

    workflow.set_entry_point("researcher")
    workflow.add_edge("researcher", "synthesizer")
    workflow.add_edge("synthesizer", "fact_checker")
    workflow.add_edge("fact_checker", END)

    return workflow.compile()


# --- Run step by step (for UI progress) ---

def run_query_steps(query: str):
    """Generator that yields after each agent step for real-time UI updates."""
    state: AgentState = {
        "query": query,
        "retrieved_docs": [],
        "research_output": "",
        "synthesis": "",
        "fact_check": "",
        "final_answer": "",
        "agent_trace": [],
        "timings": {},
    }

    # Step 1: Researcher
    state = researcher(state)
    yield "researcher", state

    # Step 2: Synthesizer
    state = synthesizer(state)
    yield "synthesizer", state

    # Step 3: Fact-Checker
    state = fact_checker(state)
    yield "fact_checker", state


def run_query(query: str) -> AgentState:
    """Run full pipeline (non-streaming)."""
    state = None
    for step_name, step_state in run_query_steps(query):
        state = step_state
    return state
