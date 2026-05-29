from __future__ import annotations


ARCHITECT_SYSTEM = """You are the Architect Agent for an AI agent factory.

Return ONLY valid JSON (no markdown, no code fences, no commentary).
The JSON must be directly parseable by json.loads().
"""


def build_architect_prompt(
    requirement: str,
    project_type: str,
    tech_stack: list[str],
    tasks: list[dict],
    research_notes: str,
    instructions: str,
) -> str:
    stack = ", ".join(tech_stack) if tech_stack else "(unspecified)"
    tasks_text = "\n".join([f"- {t.get('id')}: {t.get('name')} (agent={t.get('agent')})" for t in tasks])
    return f"""Architect the system for the following requirement.

Requirement:
{requirement}

Project type: {project_type}
Tech stack: {stack}

Tasks:
{tasks_text}

Research notes (may be compressed):
{research_notes}

Planner/architect instructions:
{instructions}

Return a single JSON object with this exact shape:
{{
  "design_summary": "string",
  "data_flow": "string",
  "file_structure": {{
    "filename.py_or_other": "purpose string"
  }},
  "api_contracts": [
    {{
      "file": "filename.py_or_other",
      "function": "function_name_or_route",
      "args": ["argName: Type", "..."],
      "returns": "return type"
    }}
  ]
}}
"""

