from __future__ import annotations


RESEARCHER_SYSTEM = """You are the Researcher Agent for an AI agent factory.

Return a concise research notes document (plain text, no JSON, no markdown fences).
Include:
- library choices and why
- recommended patterns / architecture idioms
- key APIs to look up (function/class names) and any important gotchas
- minimal dependency list (pip install lines if applicable)

Be specific enough that an Architect and Coder can implement without additional web search.
"""


def build_researcher_prompt(
    project_type: str,
    tech_stack: list[str],
    instructions: str,
    tasks: list[dict],
) -> str:
    stack = ", ".join(tech_stack) if tech_stack else "(unspecified)"
    tasks_text = "\n".join([f"- {t.get('id')}: {t.get('name')} -> agent={t.get('agent')}" for t in tasks])
    return f"""Project type: {project_type}
Tech stack (preferred): {stack}

Instructions from planner/agent plan:
{instructions}

Task breakdown:
{tasks_text}

Write the research notes document now.
"""

