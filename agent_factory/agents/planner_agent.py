from __future__ import annotations

import json

from agent_factory.core.base_agent import BaseAgent
from agent_factory.core.state import PipelineState
from agent_factory.prompts.planner import PLANNER_SYSTEM, build_planner_prompt


class PlannerAgent(BaseAgent):
    def __init__(self, llm_client):
        super().__init__("PlannerAgent", llm_client)

    def run(self, state: PipelineState) -> PipelineState:
        state.set_agent(self.name)
        self.log("Analyzing requirement...")

        # Step 1: Classify project type (cheap call)
        classification_prompt = (
            "Classify this requirement into one of: "
            "[web_app, mobile_ios, mobile_android, cli_tool, desktop_app, "
            "multi_agent_pipeline, data_pipeline, api_service]\n\n"
            f"Requirement: {state.raw_requirement}\n\n"
            "Reply with only the classification label."
        )
        project_type = (
            self.call_llm(prompt=classification_prompt, force_model="gpt-3.5-turbo").strip()
        )
        state.project_type = project_type
        self.log(f"Project type: {project_type}")

        # Step 2: Full planning (rich call)
        plan_prompt = build_planner_prompt(state.raw_requirement, project_type)
        raw_plan = self.call_llm(prompt=plan_prompt, system=PLANNER_SYSTEM)

        # Parse structured JSON from LLM response
        plan = self._extract_json(raw_plan)
        state.task_breakdown = plan.get("tasks", [])
        state.tech_stack = plan.get("tech_stack", [])
        state.project_name = plan.get("project_name", "generated_project")
        state.agent_plan = plan.get("agent_instructions", {})

        state.log(f"Plan created: {len(state.task_breakdown)} tasks identified")
        self.log("Planning complete")
        return state

    def _extract_json(self, raw: str) -> dict:
        try:
            start = raw.find("{")
            end = raw.rfind("}") + 1
            return json.loads(raw[start:end])
        except Exception:
            self.log("WARNING: Failed to parse JSON from planner. Using fallback.")
            return {"tasks": [], "tech_stack": [], "project_name": "project", "agent_instructions": {}}

