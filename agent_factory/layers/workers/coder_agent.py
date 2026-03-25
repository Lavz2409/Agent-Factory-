"""
LAYER 3 — CODER AGENT (Worker)
Composable specialist: generates working Python code.
Receives Planner task + Architect design. Produces executable files.
Output: versioned deliverable saved to S3/local outputs/.
Tech: AWS Bedrock Claude 3 for code generation.
"""

from __future__ import annotations

import json
import os
from typing import Any

from utils.bedrock_client import DEFAULT_BEDROCK_TEXT_MODEL, invoke_json_with_retry


def _validate_coder(d: dict[str, Any]) -> bool:
    code = d.get("code", "")
    if not isinstance(code, str) or len(code) <= 50:
        return False
    if "def" not in code and "class" not in code:
        return False
    if not str(d.get("filename", "")).strip():
        return False
    if not str(d.get("how_to_run", "")).strip():
        return False
    if "dependencies_to_install" not in d:
        return False
    if not isinstance(d.get("dependencies_to_install"), list):
        return False
    return True


class CoderAgent:
    """Layer 3 coder worker: emits executable Python and metadata."""

    SYSTEM_PROMPT = """[AGENT_CODER]
You are an expert Python developer working inside an AI agent factory.
Return ONLY valid JSON. Do NOT use markdown. Do NOT wrap in code fences.
Do NOT include explanations outside the JSON object.
The output must be directly parseable with json.loads().
If you fail, the system will reject your response.

Required JSON shape:
{
  "filename": "main.py",
  "code": "FULL EXECUTABLE PYTHON SOURCE as a single string",
  "how_to_run": "python main.py",
  "dependencies_to_install": ["pip-package-names"]
}

The "code" string must contain real newlines inside the JSON string (escape as \\n if needed).
Include imports, definitions, and if __name__ == '__main__' when appropriate.
"""

    def __init__(self, bedrock_client: Any, state_store: Any, sqs_bus: Any) -> None:
        self.bedrock = bedrock_client
        self.state = state_store
        self.bus = sqs_bus

    def execute(self, task: str, context: dict[str, Any], run_id: str) -> dict[str, Any]:
        """Generate code from architect output; persist metadata; notify output queue."""
        arch = context.get("architect_output", {})
        components_str = json.dumps(arch.get("components", []), indent=2)
        deps = arch.get("dependencies", []) or []
        deps_str = ", ".join(str(d) for d in deps) if deps else "none"
        files = arch.get("file_structure", ["main.py"]) or ["main.py"]
        files_str = ", ".join(str(f) for f in files)

        user_prompt = f"""
Write complete, executable Python code for this task.

Task: {task}
Project: {context.get('project_name', 'project')}

Architecture to implement:
Components:
{components_str}

Data Flow: {arch.get('data_flow', 'not specified')}
Files to create: {files_str}
Dependencies hint: {deps_str}
Design Notes: {arch.get('architecture_notes', 'none')}
Entry Point: {arch.get('entry_point', 'main.py')}

REQUIREMENTS:
1. Implement the architecture faithfully.
2. Include imports and runnable main / CLI or app entry as appropriate.
3. No TODOs or pass-only stubs.

Respond with ONLY this JSON:
{{
  "filename": "main.py",
  "code": "FULL SOURCE",
  "explanation": "short",
  "how_to_run": "python main.py",
  "dependencies_to_install": []
}}
"""
        model_id = os.environ.get("BEDROCK_REASONING_MODEL", DEFAULT_BEDROCK_TEXT_MODEL)

        emergency: dict[str, Any] = {
            "filename": "main.py",
            "code": (
                "def main() -> None:\n"
                '    print("Emergency fallback: extend this implementation.")\n\n\n'
                'if __name__ == "__main__":\n'
                "    main()\n"
            ),
            "explanation": "Emergency minimal entrypoint",
            "how_to_run": "python main.py",
            "dependencies_to_install": [],
        }

        result = invoke_json_with_retry(
            self.bedrock,
            model_id,
            user_prompt,
            self.SYSTEM_PROMPT,
            agent="coder",
            validate=_validate_coder,
            emergency_fallback=emergency,
        )

        for k in ("filename", "code", "explanation", "how_to_run", "dependencies_to_install"):
            if k not in result and k in emergency:
                result[k] = emergency[k]

        try:
            meta = {k: v for k, v in result.items() if k != "code"}
            self.state.put(run_id, "coder_output", meta)
            self.state.put(run_id, "status", "code_complete")
        except Exception:
            pass

        try:
            self.bus.send_message(
                "output-queue",
                {
                    "message_type": "result",
                    "source": "coder",
                    "destination": "output_layer",
                    "run_id": run_id,
                    "payload": {
                        "filename": result.get("filename"),
                        "status": "complete",
                    },
                },
            )
        except Exception:
            pass

        return result
