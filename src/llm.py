"""LLM factory — works with Ollama Cloud, OpenAI, Anthropic, or any OpenAI-compatible API."""

import os
from langchain_openai import ChatOpenAI


def get_llm(temperature: float = 0.1, streaming: bool = False, fast: bool = False):
    """Create LLM instance. Reads from env at runtime (so UI changes take effect).
    
    Args:
        temperature: LLM temperature (0.0-1.0)
        streaming: Enable streaming (for token-by-token output)
        fast: Use the fast/cheaper model
    """
    base_url = os.getenv("LLM_BASE_URL", "https://ollama.com/v1")
    api_key = os.getenv("LLM_API_KEY", "not-needed")
    model = os.getenv("LLM_MODEL", "mistral-large-3:675b")
    fast_model = os.getenv("LLM_FAST_MODEL", model)

    return ChatOpenAI(
        model=fast_model if fast else model,
        base_url=base_url,
        api_key=api_key or "not-needed",
        temperature=temperature,
        streaming=streaming,
        request_timeout=120,
    )


def get_streaming_llm(temperature: float = 0.1, fast: bool = False):
    """Create streaming LLM for token-by-token output."""
    return get_llm(temperature=temperature, streaming=True, fast=fast)
