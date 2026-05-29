from __future__ import annotations

import time

from agent_factory.core.llm_client import LLMClient
from agent_factory.core.state import PipelineState, PipelineStatus
from agent_factory.agents.supervisor_agent import SupervisorAgent
from agent_factory.agents.marketing_agent import MarketingAgent
from agent_factory.agents.planner_agent import PlannerAgent
from agent_factory.agents.researcher_agent import ResearcherAgent
from agent_factory.agents.architect_agent import ArchitectAgent
from agent_factory.agents.coder_agent import CoderAgent
from agent_factory.agents.ui_ux_agent import UIUXAgent
from agent_factory.agents.integration_agent import IntegrationAgent
from agent_factory.agents.validation_agent import ValidationAgent
# from agent_factory.agents.tester_agent import TesterAgent  # DISABLED — ScribeAgent handles final step
from agent_factory.agents.scribe_agent import ScribeAgent
from agent_factory.utils.logger import get_logger


logger = get_logger("Pipeline")

_DISPLAY_NAMES: dict[str, str] = {
    "SupervisorAgent":  "Supervisor",
    "MarketingAgent":   "Marketing",
    "PlannerAgent":     "Planner",
    "ResearcherAgent":  "Researcher",
    "ArchitectAgent":   "Architect",
    "CoderAgent":       "Coder",
    "UIUXAgent":        "UI/UX",
    "IntegrationAgent": "Integration",
    "ScribeAgent":      "Scribe",
    "ValidationAgent":  "Validation",
}


def _is_marketing_run(state: PipelineState) -> bool:
    """Return True when the Supervisor routed exclusively to MARKETING."""
    pipes = [p.upper() for p in (state.supervisor_pipelines or [])]
    return bool(pipes) and all(p == "MARKETING" for p in pipes)


def _agent_full_output(agent_name: str, state: PipelineState) -> str:
    if agent_name == "MarketingAgent":
        report = state.marketing_report or ""
        lines  = report.splitlines()
        preview = "\n".join(lines[:20]) + ("\n…" if len(lines) > 20 else "")
        return (
            f"marketing_report.md — {len(lines)} lines, {len(report):,} chars\n\n"
            + preview
        )
    if agent_name == "SupervisorAgent":
        pipes = ", ".join(state.supervisor_pipelines) if state.supervisor_pipelines else "—"
        tools = ", ".join(state.supervisor_tools[:10]) if state.supervisor_tools else "—"
        mods  = "\n".join(f"  • {m}" for m in state.supervisor_modules) if state.supervisor_modules else "  (none)"
        return (
            f"Pipeline(s): {pipes}\n"
            f"Confidence:  {state.supervisor_confidence:.0%}\n"
            f"Complexity:  {state.supervisor_complexity}\n"
            f"Reason:      {state.supervisor_reason}\n\n"
            f"Recommended tools: {tools}\n\n"
            f"Estimated modules:\n{mods}"
        )
    if agent_name == "PlannerAgent":
        tasks = state.task_breakdown or []
        stack = state.tech_stack or []
        return (
            f"Project: {state.project_name}  |  Type: {state.project_type}\n"
            f"Tech stack: {', '.join(stack[:10])}\n\n"
            f"Tasks ({len(tasks)}):\n"
            + "\n".join(
                f"  {i+1}. {t.get('title', t) if isinstance(t, dict) else t}"
                for i, t in enumerate(tasks)
            )
        )
    if agent_name == "ResearcherAgent":
        libs  = state.relevant_libraries or []
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
    if agent_name == "UIUXAgent":
        files = state.ui_files or []
        return (
            f"UI design system produced {len(files)} file(s):\n"
            + "\n".join(f"  • {f}" for f in files[:30])
            + (f"\n\nDesign doc preview:\n{state.ui_design_system[:800]}" if state.ui_design_system else "")
        )
    if agent_name == "IntegrationAgent":
        files = state.integration_files or []
        notes = state.integration_notes or []
        return (
            f"Integration layer produced {len(files)} file(s):\n"
            + "\n".join(f"  • {f}" for f in files)
            + (("\n\nNotes:\n" + "\n".join(f"  - {n}" for n in notes[:10])) if notes else "")
        )
    if agent_name == "ValidationAgent":
        return (
            f"Quality score: {state.validation_score}/10\n"
            f"Ready: {'YES' if state.validation_ready else 'NO'}\n"
            f"Issues: {len(state.validation_issues or [])}\n\n"
            + (state.validation_report[:2400] if state.validation_report else "")
        )
    if agent_name == "ScribeAgent":
        return state.scribe_walkthrough[:3000] if state.scribe_walkthrough else "(no walkthrough)"
    return ""


class AgentFactoryPipeline:
    def __init__(self) -> None:
        self.llm = LLMClient()
        # Supervisor always runs first; remaining agents are selected at runtime
        # based on what the Supervisor decides.
        self._supervisor     = SupervisorAgent(self.llm)
        self._marketing      = MarketingAgent(self.llm)
        # Full 8-agent professional code pipeline:
        #   Planner (Input Analyzer) → Researcher → Architect → Coder
        #   → UI/UX → Integration → Scribe → Marketing → Validation
        self._code_pipeline  = [
            PlannerAgent(self.llm),       # 1. Input analysis
            ResearcherAgent(self.llm),    #    (research gathering)
            ArchitectAgent(self.llm),     # 2. System architecture
            CoderAgent(self.llm),         # 3. Core code generation
            UIUXAgent(self.llm),          # 4. UI/UX design system
            IntegrationAgent(self.llm),   # 5. Frontend ⇄ backend wiring
            ScribeAgent(self.llm),        # 6. Documentation
            MarketingAgent(self.llm),     # 7. Market analysis
            ValidationAgent(self.llm),    # 8. Quality gate
        ]

    def run(self, requirement: str, state: PipelineState | None = None) -> PipelineState:
        state = state or PipelineState(raw_requirement=requirement)
        state.raw_requirement = requirement
        state.status = PipelineStatus.RUNNING

        # ── Phase 1: SupervisorAgent always runs first ────────────────────────
        state = self._run_agent(self._supervisor, state, step=1)
        if state.status == PipelineStatus.FAILED:
            return state

        # ── Phase 2: branch based on supervisor routing ───────────────────────
        if _is_marketing_run(state):
            logger.info("Pipeline → MARKETING branch")
            remaining = [self._marketing]
        else:
            logger.info("Pipeline → CODE branch (%s)", state.supervisor_pipelines)
            remaining = self._code_pipeline

        for offset, agent in enumerate(remaining):
            state = self._run_agent(agent, state, step=2 + offset)
            if state.status == PipelineStatus.FAILED:
                return state

        state.status = PipelineStatus.COMPLETED
        state.token_usage = self.llm.get_usage_report()
        return state

    # ── internal helpers ──────────────────────────────────────────────────────

    def _run_agent(
        self,
        agent,
        state: PipelineState,
        step: int,
    ) -> PipelineState:
        t0 = time.monotonic()
        try:
            state    = agent.run(state)
            duration = round(time.monotonic() - t0, 2)
            full_out = _agent_full_output(agent.name, state)
            state.activity_log.append({
                "agent":       _DISPLAY_NAMES.get(agent.name, agent.name),
                "status":      "success",
                "summary":     full_out[:300] + ("…" if len(full_out) > 300 else ""),
                "full_output": full_out,
                "duration":    duration,
                "step":        step,
            })
        except Exception as e:
            duration = round(time.monotonic() - t0, 2)
            state.activity_log.append({
                "agent":       _DISPLAY_NAMES.get(agent.name, agent.name),
                "status":      "error",
                "summary":     str(e)[:300],
                "full_output": str(e),
                "duration":    duration,
                "step":        step,
            })
            logger.error("Agent %s failed: %s", agent.name, e)
            state.status   = PipelineStatus.FAILED
            state.error_log = str(e)
        return state

