from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class TokenRecord:
    agent: str
    model: str
    prompt_tokens: int
    completion_tokens: int


class TokenCounter:
    """
    Tracks token usage per agent/model for reporting at the end of a Phase 1 run.
    """

    def __init__(self) -> None:
        self._records: list[TokenRecord] = []

    def record(
        self,
        agent: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
    ) -> None:
        self._records.append(
            TokenRecord(
                agent=agent,
                model=model,
                prompt_tokens=int(prompt_tokens or 0),
                completion_tokens=int(completion_tokens or 0),
            )
        )

    def get_report(self) -> dict[str, Any]:
        by_agent: dict[str, dict[str, int]] = {}
        totals: dict[str, int] = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

        for r in self._records:
            by_agent.setdefault(r.agent, {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0})
            by_agent[r.agent]["prompt_tokens"] += r.prompt_tokens
            by_agent[r.agent]["completion_tokens"] += r.completion_tokens
            by_agent[r.agent]["total_tokens"] += r.prompt_tokens + r.completion_tokens

            totals["prompt_tokens"] += r.prompt_tokens
            totals["completion_tokens"] += r.completion_tokens
            totals["total_tokens"] += r.prompt_tokens + r.completion_tokens

        return {
            "by_agent": by_agent,
            "totals": totals,
            "calls": len(self._records),
        }

