"""
LAYER 1 — INPUT LAYER
Accepts requirement documents in any format.
Extracts: intent, constraints, domain, success criteria.
Stores structured input as JSON to S3 (local: storage/inputs/).
Knowledge graph stores patterns from all past generated architectures.
Tech: S3 document store, JSON schema validation, semantic parsing via Bedrock.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from utils.bedrock_client import DEFAULT_BEDROCK_TEXT_MODEL, invoke_json_with_retry


def _validate_parsed_input(d: dict[str, Any]) -> bool:
    if not isinstance(d.get("intent"), str) or len(d.get("intent", "").strip()) < 3:
        return False
    if not isinstance(d.get("domain"), str) or not d.get("domain", "").strip():
        return False
    if not isinstance(d.get("expected_output"), str):
        return False
    if not isinstance(d.get("constraints"), list):
        return False
    return True


class InputLayer:
    """Layer 1: semantic parsing via Bedrock, persist to local/S3, notify planner via SQS."""

    SYSTEM_PROMPT = """[AGENT_INPUT]
You are an expert requirements analyst for a software agent factory.
Return ONLY valid JSON. Do NOT use markdown. Do NOT wrap in code fences.
Do NOT include explanations outside the JSON object.
The output must be directly parseable with json.loads().
If you fail, the system will reject your response.
"""

    def __init__(self, bedrock_client: Any, state_store: Any, sqs_bus: Any) -> None:
        self.bedrock = bedrock_client
        self.state = state_store
        self.bus = sqs_bus
        self.storage_path = Path("storage/inputs")
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def parse(self, user_input: str, run_id: str) -> dict[str, Any]:
        """Parse user request; persist JSON; update state; enqueue planner task."""
        user_prompt = f"""
Analyze this user request and extract all structured information.

User Request: "{user_input}"

Respond with ONLY this JSON:
{{
  "intent": "one precise sentence describing the core goal",
  "constraints": ["every technical constraint or requirement mentioned"],
  "domain": "technical domain (web development / data engineering / CLI tooling / etc)",
  "expected_output": "exact deliverable the user wants",
  "complexity": "simple | medium | complex",
  "success_criteria": ["how we know the output is correct"],
  "suggested_agents": ["architect", "coder"]
}}
"""
        model_id = os.environ.get("BEDROCK_REASONING_MODEL", DEFAULT_BEDROCK_TEXT_MODEL)

        emergency: dict[str, Any] = {
            "intent": user_input[:500] if user_input else "unspecified",
            "constraints": [],
            "domain": "general",
            "expected_output": "working solution",
            "complexity": "medium",
            "success_criteria": ["runs without errors"],
            "suggested_agents": ["architect", "coder"],
        }

        result = invoke_json_with_retry(
            self.bedrock,
            model_id,
            user_prompt,
            self.SYSTEM_PROMPT,
            agent="input_layer",
            validate=_validate_parsed_input,
            emergency_fallback=emergency,
        )

        for k, v in emergency.items():
            result.setdefault(k, v)

        filename = f"{run_id}_input.json"
        filepath = self.storage_path / filename
        try:
            filepath.write_text(json.dumps(result, indent=2), encoding="utf-8")
        except Exception:
            pass

        try:
            self.state.put(run_id, "input_parsed", result)
            self.state.put(run_id, "status", "input_complete")
        except Exception:
            pass

        try:
            self.bus.send_message(
                "planner-queue",
                {
                    "message_type": "task",
                    "source": "input_layer",
                    "destination": "planner",
                    "run_id": run_id,
                    "payload": result,
                },
            )
        except Exception:
            pass

        return result
