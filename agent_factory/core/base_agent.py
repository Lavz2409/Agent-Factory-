from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Optional

from agent_factory.core.llm_client import LLMClient
from agent_factory.core.state import PipelineState
from agent_factory.utils.logger import get_logger


class BaseAgent(ABC):
    def __init__(self, name: str, llm_client: LLMClient):
        self.name = name
        self.llm = llm_client
        self.logger = get_logger(name)

    @abstractmethod
    def run(self, state: PipelineState) -> PipelineState:
        """
        Each agent reads from state, does its work,
        writes results back to state, returns updated state.
        """

    def log(self, message: str) -> None:
        self.logger.info(f"[{self.name}] {message}")

    def call_llm(
        self,
        prompt: str,
        system: str = "",
        use_cache: bool = True,
        force_model: Optional[str] = None,
    ) -> str:
        return self.llm.call(
            prompt=prompt,
            system=system,
            agent_name=self.name,
            use_cache=use_cache,
            force_model=force_model,
        )

