from __future__ import annotations

import json

from agent_factory.core.base_agent import BaseAgent
from agent_factory.core.state import PipelineState
from agent_factory.prompts.architect import ARCHITECT_SYSTEM, build_architect_prompt


class ArchitectAgent(BaseAgent):
    def __init__(self, llm_client):
        super().__init__("ArchitectAgent", llm_client)

    def run(self, state: PipelineState) -> PipelineState:
        state.set_agent(self.name)
        self.log("Designing system architecture...")

        prompt = build_architect_prompt(
            requirement=state.raw_requirement,
            project_type=state.project_type,
            tech_stack=state.tech_stack,
            tasks=state.task_breakdown,
            research_notes=state.research_notes,
            instructions=state.agent_plan.get("architect", ""),
        )

        raw_design = self.call_llm(prompt=prompt, system=ARCHITECT_SYSTEM)
        design = self._extract_json(raw_design)

        state.system_design = design.get("design_summary", "")
        state.file_structure = design.get("file_structure", {})
        state.data_flow = design.get("data_flow", "")
        state.api_contracts = design.get("api_contracts", [])

        self.log(f"Architecture designed. {len(state.file_structure)} files planned.")
        return state

    def _extract_json(self, raw: str) -> dict:
        try:
            start = raw.find("{")
            end = raw.rfind("}") + 1
            return json.loads(raw[start:end])
        except Exception:
            return {}

