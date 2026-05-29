from __future__ import annotations

from agent_factory.core.base_agent import BaseAgent
from agent_factory.core.state import PipelineState
from agent_factory.prompts.researcher import RESEARCHER_SYSTEM, build_researcher_prompt


class ResearcherAgent(BaseAgent):
    def __init__(self, llm_client):
        super().__init__("ResearcherAgent", llm_client)

    def run(self, state: PipelineState) -> PipelineState:
        state.set_agent(self.name)
        self.log("Researching libraries and patterns...")

        prompt = build_researcher_prompt(
            project_type=state.project_type,
            tech_stack=state.tech_stack,
            instructions=state.agent_plan.get("researcher", ""),
            tasks=state.task_breakdown,
        )

        raw_research = self.call_llm(prompt=prompt, system=RESEARCHER_SYSTEM)

        # Compress before storing — downstream agents get summary only.
        compressed = self.llm.compress_context(raw_research, max_tokens=500)
        state.research_notes = compressed
        state.relevant_libraries = self._extract_libraries(raw_research)

        state.log(f"Research complete. {len(state.relevant_libraries)} libraries identified.")
        return state

    def _extract_libraries(self, text: str) -> list[str]:
        # Simple extraction — look for pip install lines.
        lines = text.split("\n")
        libs: list[str] = []
        for line in lines:
            if "pip install" in line:
                parts = line.replace("pip install", "").strip().split()
                libs.extend(parts)
        return list({l for l in libs if l})

