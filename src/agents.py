"""Multi-agent pipeline using LangGraph — Researcher, Synthesizer, Fact-Checker.

Supports conversation memory: agents receive chat history so follow-up
questions like "tell me more about that" or "what about chapter 3?" work.
"""

import time
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage
from src.llm import get_llm, get_streaming_llm
from src.ingest import get_vectorstore
from src.retriever import hybrid_search
from src.config import Config


# --- State ---

class AgentState(TypedDict):
    query: str                    # Current user question
    chat_history: list[dict]      # Previous Q&A pairs: [{"role": "user"/"assistant", "content": "..."}]
    context_query: str            # Rewritten query with context (for retrieval)
    retrieved_docs: list[str]
    research_output: str
    synthesis: str
    fact_check: str
    final_answer: str
    agent_trace: list[dict]
    timings: dict


# --- Helpers ---

def _format_chat_history(chat_history: list[dict], max_turns: int = 5) -> str:
    """Format recent chat history into a readable string.
    
    Only keeps last `max_turns` Q&A pairs to avoid token overflow.
    """
    if not chat_history:
        return "No previous conversation."
    
    # Keep only the last N turns (each turn = user + assistant)
    recent = chat_history[-(max_turns * 2):]
    
    lines = []
    for msg in recent:
        role = "User" if msg["role"] == "user" else "Assistant"
        # Truncate long assistant answers to save tokens
        content = msg["content"]
        if role == "Assistant" and len(content) > 500:
            content = content[:500] + "... [truncated]"
        lines.append(f"{role}: {content}")
    
    return "\n".join(lines)


# --- Agent Nodes ---

def context_rewriter(state: AgentState) -> AgentState:
    """Rewrite the user query with conversation context for better retrieval.
    
    Example: 
      History: "What is DynamoDB?" → "It's a NoSQL database..."
      New query: "What about its pricing?"
      Rewritten: "What is DynamoDB pricing model?"
    
    If no history or query is self-contained, returns original query.
    """
    start = time.time()
    
    # Skip rewriting if no chat history or query looks self-contained
    if not state["chat_history"]:
        state["context_query"] = state["query"]
        elapsed = time.time() - start
        state["agent_trace"].append({
            "agent": "🔄 Context Rewriter",
            "action": "No history — using original query",
            "output_preview": state["query"],
            "time": f"{elapsed:.1f}s",
        })
        state["timings"]["context_rewriter"] = elapsed
        return state
    
    llm = get_llm(fast=True)
    history_str = _format_chat_history(state["chat_history"])
    
    prompt = f"""Given the conversation history and a new question, rewrite the question to be 
self-contained (include all necessary context from the conversation).

If the new question is already self-contained, return it as-is.
ONLY output the rewritten question, nothing else.

Conversation History:
{history_str}

New Question: {state['query']}

Rewritten Question:"""

    response = llm.invoke([
        SystemMessage(content="You rewrite questions to be self-contained using conversation context. Output ONLY the rewritten question."),
        HumanMessage(content=prompt)
    ])
    
    rewritten = response.content.strip()
    # Safety: if LLM returns empty or very long, use original
    if not rewritten or len(rewritten) > 500:
        rewritten = state["query"]
    
    state["context_query"] = rewritten
    elapsed = time.time() - start
    
    state["agent_trace"].append({
        "agent": "🔄 Context Rewriter",
        "action": f"Rewrote query with conversation context",
        "output_preview": f"Original: {state['query']}\nRewritten: {rewritten}",
        "time": f"{elapsed:.1f}s",
    })
    state["timings"]["context_rewriter"] = elapsed
    return state


def _generate_sub_queries(query: str, llm) -> list[str]:
    """Generate 2-3 alternative queries for multi-query expansion.
    
    "What is DynamoDB?" → ["DynamoDB features and capabilities", "DynamoDB use cases", "AWS DynamoDB overview"]
    """
    prompt = f"""Generate 2-3 alternative search queries for the following question.
Each query should approach the topic from a different angle to find more relevant information.
Output ONLY the queries, one per line. No numbering, no explanations.

Original question: {query}"""

    response = llm.invoke([
        SystemMessage(content="You generate alternative search queries. Output only queries, one per line."),
        HumanMessage(content=prompt)
    ])
    
    sub_queries = [q.strip() for q in response.content.strip().split("\n") if q.strip()]
    # Safety: limit to 3 sub-queries
    return sub_queries[:3]


def researcher(state: AgentState) -> AgentState:
    """Retrieve relevant chunks using multi-query expansion + hybrid search.
    
    1. Generates alternative queries for better coverage
    2. Runs hybrid search (BM25 + Vector + RRF) on each query
    3. Deduplicates and merges results
    """
    start = time.time()
    
    search_query = state.get("context_query", state["query"])
    
    # Multi-query expansion
    llm = get_llm(fast=True)
    sub_queries = _generate_sub_queries(search_query, llm)
    all_queries = [search_query] + sub_queries
    
    # Run hybrid search on all queries and merge
    seen_texts = set()
    all_results = []
    
    for q in all_queries:
        results = hybrid_search(q, top_k=Config.TOP_K)
        for r in results:
            # Deduplicate by content
            content_hash = r["content"][:200]
            if content_hash not in seen_texts:
                seen_texts.add(content_hash)
                all_results.append(r)
    
    # Keep top_k best results
    all_results = all_results[:Config.TOP_K]

    retrieved = []
    for i, doc in enumerate(all_results):
        source = doc["metadata"].get("source", "unknown")
        page = doc["metadata"].get("page", "?")
        retrieved.append(f"[Source {i+1}: {source}, p.{page}]\n{doc['content']}")

    state["retrieved_docs"] = retrieved

    # Include conversation context in the research prompt
    history_str = _format_chat_history(state["chat_history"], max_turns=3)
    
    llm = get_llm(fast=True)
    prompt = f"""You are a Research Agent. Analyze these document excerpts and extract key findings relevant to the query.

Conversation History (for context):
{history_str}

Current Query: {state['query']}
Search Query Used: {search_query}

Documents:
{"---".join(retrieved)}

Extract:
1. Key facts and data points relevant to the current query
2. Relevant quotes with source references [Source N]
3. Any contradictions or gaps
4. If this is a follow-up question, focus on new information not already discussed

Be thorough but concise. Use bullet points."""

    response = llm.invoke([
        SystemMessage(content="You are a meticulous research agent. Extract facts precisely with source citations. Pay attention to conversation context for follow-up questions."),
        HumanMessage(content=prompt)
    ])
    elapsed = time.time() - start
    state["research_output"] = response.content
    state["agent_trace"].append({
        "agent": "🔍 Researcher",
        "action": f"Multi-query: {len(all_queries)} queries → {len(retrieved)} unique chunks (hybrid BM25+vector)",
        "output_preview": response.content[:300] + "..." if len(response.content) > 300 else response.content,
        "time": f"{elapsed:.1f}s",
    })
    state["timings"]["researcher"] = elapsed
    return state


def synthesizer(state: AgentState) -> AgentState:
    """Synthesize research into a clear, cited answer.
    
    Considers conversation history to avoid repeating information.
    """
    start = time.time()
    llm = get_llm()
    
    history_str = _format_chat_history(state["chat_history"], max_turns=3)
    
    prompt = f"""You are a Synthesis Agent. Create a clear, well-structured answer using the research findings.

Conversation History (for context — don't repeat what was already said):
{history_str}

Current Query: {state['query']}

Research Findings:
{state['research_output']}

Original Sources:
{"---".join(state['retrieved_docs'])}

Rules:
- Cite sources using [Source N] format
- Use clear headings and bullet points
- Be comprehensive but readable
- If this is a follow-up, build on previous answers — don't repeat
- If information is missing, say so clearly"""

    response = llm.invoke([
        SystemMessage(content="You are a synthesis expert. Create clear, well-cited, structured answers. For follow-up questions, build on context — don't repeat previous answers."),
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


def fact_checker_streaming(state: AgentState):
    """Streaming version of fact-checker — yields tokens one by one.
    
    Returns: generator of (token_str, final_state_or_None)
    Last yield has the final state.
    """
    start = time.time()
    llm = get_streaming_llm()
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

    messages = [
        SystemMessage(content="You are a rigorous fact-checker. Output a clean, verified final answer."),
        HumanMessage(content=prompt)
    ]
    
    full_response = ""
    for chunk in llm.stream(messages):
        token = chunk.content
        if token:
            full_response += token
            yield token, None
    
    elapsed = time.time() - start
    state["fact_check"] = full_response
    state["final_answer"] = full_response
    state["agent_trace"].append({
        "agent": "✅ Fact-Checker",
        "action": "Verified all claims against sources",
        "output_preview": full_response[:300] + "..." if len(full_response) > 300 else full_response,
        "time": f"{elapsed:.1f}s",
    })
    state["timings"]["fact_checker"] = elapsed
    yield "", state  # Final yield with complete state


# --- Build Graph ---

def build_graph():
    """Create the multi-agent LangGraph pipeline with context rewriting."""
    workflow = StateGraph(AgentState)

    workflow.add_node("context_rewriter", context_rewriter)
    workflow.add_node("researcher", researcher)
    workflow.add_node("synthesizer", synthesizer)
    workflow.add_node("fact_checker", fact_checker)

    workflow.set_entry_point("context_rewriter")
    workflow.add_edge("context_rewriter", "researcher")
    workflow.add_edge("researcher", "synthesizer")
    workflow.add_edge("synthesizer", "fact_checker")
    workflow.add_edge("fact_checker", END)

    return workflow.compile()


# --- Run step by step (for UI progress) ---

def run_query_steps(query: str, chat_history: list[dict] = None, streaming: bool = False):
    """Generator that yields after each agent step for real-time UI updates.
    
    Args:
        query: Current user question
        chat_history: List of previous messages
        streaming: If True, fact-checker streams tokens via ("stream_token", token, None) yields
    
    Yields:
        Non-streaming: (step_name, state)
        Streaming: (step_name, state) for first 3 agents, then ("stream_token", token_str, state_or_None)
    """
    state: AgentState = {
        "query": query,
        "chat_history": chat_history or [],
        "context_query": query,
        "retrieved_docs": [],
        "research_output": "",
        "synthesis": "",
        "fact_check": "",
        "final_answer": "",
        "agent_trace": [],
        "timings": {},
    }

    # Step 1: Context Rewriter
    state = context_rewriter(state)
    yield "context_rewriter", state

    # Step 2: Researcher
    state = researcher(state)
    yield "researcher", state

    # Step 3: Synthesizer
    state = synthesizer(state)
    yield "synthesizer", state

    # Step 4: Fact-Checker (streaming or non-streaming)
    if streaming:
        yield "fact_checker_start", state  # Signal: streaming about to begin
        for token, final_state in fact_checker_streaming(state):
            if final_state is not None:
                yield "fact_checker_done", final_state
            else:
                yield "stream_token", token
    else:
        state = fact_checker(state)
        yield "fact_checker", state


def run_query(query: str, chat_history: list[dict] = None) -> AgentState:
    """Run full pipeline (non-streaming)."""
    state = None
    for step_name, step_state in run_query_steps(query, chat_history):
        state = step_state
    return state
