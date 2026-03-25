"""
LAYER 3 — ARCHITECT AGENT (Worker)
Composable specialist: designs topology and data flow.
Spawned and scoped by the Planner. Output feeds the Coder agent.
Tech: AWS Bedrock Claude 3 for reasoning.
"""

from __future__ import annotations

import os
from typing import Any

from utils.bedrock_client import DEFAULT_BEDROCK_TEXT_MODEL, invoke_json_with_retry


def _validate_architecture(d: dict[str, Any]) -> bool:
    comps = d.get("components")
    if not isinstance(comps, list) or len(comps) == 0:
        return False
    for c in comps:
        if not isinstance(c, dict):
            return False
        if not str(c.get("name", "")).strip():
            return False
        if not str(c.get("responsibility", "")).strip():
            return False
    df = d.get("data_flow")
    if not isinstance(df, str) or len(df.strip()) < 8:
        return False
    ep = d.get("entry_point")
    if not isinstance(ep, str) or not ep.strip():
        return False
    return True


class ArchitectAgent:
    """Layer 3 architect worker: produces structured architecture JSON."""

    SYSTEM_PROMPT = """[AGENT_ARCHITECT]
You are a senior software architect working inside an AI agent factory.
Return ONLY valid JSON. Do NOT use markdown. Do NOT wrap in code fences.
Do NOT include explanations outside the JSON object.
The output must be directly parseable with json.loads().
If you fail, the system will reject your response.

Required JSON shape:
{
  "components": [
    {"name": "ComponentName", "responsibility": "what it does"}
  ],
  "data_flow": "clear description of how data moves",
  "entry_point": "main.py"
}

Optional keys: file_structure, dependencies, architecture_notes, interfaces per component.
"""

    def __init__(self, bedrock_client: Any, state_store: Any, sqs_bus: Any) -> None:
        self.bedrock = bedrock_client
        self.state = state_store
        self.bus = sqs_bus

    def execute(self, task: str, context: dict[str, Any], run_id: str) -> dict[str, Any]:
        """Design architecture for task; persist; publish result on output queue."""
        user_prompt = f"""
Design the complete system architecture for this task.

Task: {task}
Project: {context.get('project_name', 'project')}
Strategy: {context.get('strategy', 'not specified')}
Planner constraints for this agent: {context.get('context', 'none')}

The coder will implement this design directly.

Respond with ONLY this JSON:
{{
  "components": [
    {{"name": "Name", "responsibility": "one sentence", "interfaces": ["optional"]}}
  ],
  "data_flow": "numbered or stepwise data movement",
  "file_structure": ["main.py"],
  "dependencies": [],
  "architecture_notes": "brief rationale",
  "entry_point": "main.py"
}}
"""
        model_id = os.environ.get("BEDROCK_REASONING_MODEL", DEFAULT_BEDROCK_TEXT_MODEL)

        emergency: dict[str, Any] = {
            "components": [
                {
                    "name": "Application",
                    "responsibility": "Fulfill the task with clear modules",
                    "interfaces": ["run()"],
                },
            ],
            "data_flow": "Input is processed and produces output for the user request.",
            "file_structure": ["main.py"],
            "dependencies": [],
            "architecture_notes": "Emergency fallback architecture.",
            "entry_point": "main.py",
        }

        result = invoke_json_with_retry(
            self.bedrock,
            model_id,
            user_prompt,
            self.SYSTEM_PROMPT,
            agent="architect",
            validate=_validate_architecture,
            emergency_fallback=emergency,
        )

        for k in (
            "components",
            "data_flow",
            "file_structure",
            "dependencies",
            "architecture_notes",
            "entry_point",
        ):
            if k not in result and k in emergency:
                result[k] = emergency[k]

        try:
            self.state.put(run_id, "architect_output", result)
            self.state.put(run_id, "status", "architecture_complete")
        except Exception:
            pass

        try:
            self.bus.send_message(
                "output-queue",
                {
                    "message_type": "result",
                    "source": "architect",
                    "destination": "coder",
                    "run_id": run_id,
                    "payload": result,
                },
            )
        except Exception:
            pass

        return result
