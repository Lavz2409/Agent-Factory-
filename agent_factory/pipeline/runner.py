from __future__ import annotations

import asyncio
import json
import logging
import os
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any
from typing import Optional

from agent_factory.agents.planner_agent    import PlannerAgent
from agent_factory.agents.researcher_agent import ResearcherAgent
from agent_factory.agents.architect_agent  import ArchitectAgent
from agent_factory.agents.coder_agent      import CoderAgent
# from agent_factory.agents.tester_agent import TesterAgent  # DISABLED — ScribeAgent handles final step
from agent_factory.agents.scribe_agent     import ScribeAgent  # final pipeline step
from agent_factory.core.state              import PipelineState, PipelineStatus
from agent_factory.llm.client              import get_llm_client

logger = logging.getLogger(__name__)

_AGENT_PIPELINE = [
    ("PlannerAgent",    PlannerAgent),
    ("ResearcherAgent", ResearcherAgent),
    ("ArchitectAgent",  ArchitectAgent),
    ("CoderAgent",      CoderAgent),
    # ("TesterAgent", TesterAgent),   # DISABLED — ScribeAgent is now the final pipeline step
    ("ScribeAgent",     ScribeAgent),  # generates walkthrough + saves all files
]

ProgressCallback = Callable[[str, str, float], None]

_DISPLAY_NAMES: dict[str, str] = {
    "PlannerAgent":    "Planner",
    "ResearcherAgent": "Researcher",
    "ArchitectAgent":  "Architect",
    "CoderAgent":      "Coder",
    "ScribeAgent":     "Scribe",
}


def _agent_full_output(agent_name: str, state: Any) -> str:
    """Extract a human-readable full output string for the activity log."""
    if agent_name == "PlannerAgent":
        tasks = state.task_breakdown or []
        stack = state.tech_stack or []
        return (
            f"Project: {state.project_name}  |  Type: {state.project_type}\n"
            f"Tech stack: {', '.join(stack[:10])}\n\n"
            f"Tasks ({len(tasks)}):\n"
            + "\n".join(f"  {i+1}. {t.get('title', t) if isinstance(t, dict) else t}"
                        for i, t in enumerate(tasks))
        )
    if agent_name == "ResearcherAgent":
        libs = state.relevant_libraries or []
        notes = state.research_notes or ""
        return (
            f"Libraries ({len(libs)}): {', '.join(libs[:20])}\n\n"
            + (notes[:2000] if notes else "(no notes)")
        )
    if agent_name == "ArchitectAgent":
        files = list((state.file_structure or {}).keys())
        return (
            f"Files planned ({len(files)}):\n"
            + "\n".join(f"  • {f}" for f in files)
            + (f"\n\nSystem design:\n{state.system_design[:800]}" if state.system_design else "")
        )
    if agent_name == "CoderAgent":
        files = list((state.generated_files or {}).keys())
        return (
            f"Generated {len(files)} file(s):\n"
            + "\n".join(f"  • {f}" for f in files)
        )
    if agent_name == "ScribeAgent":
        return state.scribe_walkthrough[:3000] if state.scribe_walkthrough else "(no walkthrough)"
    return ""


class PipelineError(Exception):
    def __init__(self, agent_name: str, cause: Exception) -> None:
        self.agent_name = agent_name
        self.cause      = cause
        super().__init__(f"{agent_name} failed: {cause}")


class PipelineRunner:
    def run(
        self,
        requirement: str,
        on_progress: Optional[ProgressCallback] = None,
    ) -> PipelineState:
        llm   = get_llm_client()
        state = PipelineState(raw_requirement=requirement)
        state.status = PipelineStatus.RUNNING

        for step, (agent_name, AgentClass) in enumerate(_AGENT_PIPELINE, start=1):
            agent = AgentClass(llm)
            t0    = time.monotonic()
            logger.info("[%s] starting", agent_name)
            try:
                state    = agent.run(state)
                duration = round(time.monotonic() - t0, 2)
                logger.info("[%s] done in %.2fs", agent_name, duration)

                full_out = _agent_full_output(agent_name, state)
                state.activity_log.append({
                    "agent":       _DISPLAY_NAMES.get(agent_name, agent_name),
                    "status":      "success",
                    "summary":     full_out[:300] + ("…" if len(full_out) > 300 else ""),
                    "full_output": full_out,
                    "duration":    duration,
                    "step":        step,
                })

                if on_progress:
                    on_progress(agent_name, "done", duration)
            except Exception as exc:
                duration = round(time.monotonic() - t0, 2)
                state.activity_log.append({
                    "agent":       _DISPLAY_NAMES.get(agent_name, agent_name),
                    "status":      "error",
                    "summary":     str(exc)[:300],
                    "full_output": str(exc),
                    "duration":    duration,
                    "step":        step,
                })
                logger.error("[%s] failed: %s", agent_name, exc, exc_info=True)
                raise PipelineError(agent_name, exc) from exc

        # ── ScribeAgent post-run logging ───────────────────────────────────────
        if state.scribe_walkthrough:
            print(f"[ScribeAgent] Walkthrough written to {state.scribe_walkthrough_path}")
            print(f"[ScribeAgent] Files saved: {state.scribe_saved_files}")

        state.status      = PipelineStatus.COMPLETED
        state.token_usage = llm.get_usage_report()
        return state

    async def run_async(self, requirement: str, queue: asyncio.Queue) -> PipelineState:
        loop = asyncio.get_running_loop()

        def _cb(agent_name: str, status: str, duration: float) -> None:
            loop.call_soon_threadsafe(
                queue.put_nowait,
                {"type": "progress", "agent": agent_name, "status": status, "duration": duration},
            )

        return await loop.run_in_executor(None, lambda: self.run(requirement, _cb))
