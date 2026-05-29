from __future__ import annotations
"""Public import path for the LLM client."""
from agent_factory.core.llm_client import LLMClient  # noqa: F401
__all__ = ["LLMClient", "get_llm_client"]

def get_llm_client() -> LLMClient:
    """Factory — creates an LLMClient configured from environment."""
    return LLMClient()
