from __future__ import annotations


CODER_SYSTEM = """You are the Coder Agent for an AI agent factory.

Goal: Implement ONE file of a generated project.
Return only the file content (preferably wrapped in a single ```python fence for .py files).
Do not include explanations.
"""


def build_coder_prompt(
    filename: str,
    purpose: str,
    tech_stack: list[str],
    api_contracts: list[dict],
    research_notes: str,
    interface_summary: str,
    instructions: str,
    full_requirement: str,
) -> str:
    contracts_text = "\n".join(
        [
            f"- {c.get('function') or c.get('route') or c.get('name')} in {c.get('file')}: args={c.get('args') or ''} returns={c.get('returns') or ''}"
            for c in api_contracts
        ]
    )

    stack = ", ".join(tech_stack) if tech_stack else "(unspecified)"

    return f"""Generate the file: {filename}

Purpose:
{purpose}

Full requirement:
{full_requirement}

Tech stack:
{stack}

Relevant API contracts / interfaces for this file:
{contracts_text if contracts_text else '(none explicitly listed)'}

Compressed research notes:
{research_notes}

Interface summary from already-generated files (signatures only):
{interface_summary if interface_summary else '(none yet)'}

Planner/Coder instructions:
{instructions}

Constraints:
- Return complete, runnable code for this file.
- Ensure the generated code is consistent with the contracts above.
- Prefer clear types and minimal dependencies.
"""

