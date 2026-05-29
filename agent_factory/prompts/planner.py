from __future__ import annotations


PLANNER_SYSTEM = """You are the Planner Agent for an AI agent factory.

Return ONLY valid JSON (no markdown, no code fences, no extra commentary).
All fields must be present and JSON must be directly parseable by json.loads().
"""


def build_planner_prompt(requirement: str, project_type: str) -> str:
    return f"""You will plan an implementation for the requested software system.

Requirement:
{requirement}

Classified project type:
{project_type}

Return a single JSON object with this exact shape:
{{
  "project_name": "todo_api",
  "project_type": "{project_type}",
  "tech_stack": ["Python", "FastAPI", "SQLite"],
  "tasks": [
    {{"id": 1, "name": "Setup project structure", "agent": "architect"}},
    {{"id": 2, "name": "Implement core logic", "agent": "coder"}},
    {{"id": 3, "name": "Write tests", "agent": "tester"}}
  ],
  "agent_instructions": {{
    "researcher": "Focus on best practices and patterns for this project type",
    "architect": "Design modules and interfaces",
    "coder": "Generate code files that satisfy the architect blueprint",
    "tester": "Generate pytest suite that covers all API contracts"
  }}
}}
"""

