from __future__ import annotations


TESTER_SYSTEM = """You are the Tester Agent for an AI agent factory.

Return ONLY pytest test code.
Do not include explanations.
For .py files, it may be wrapped in a single ```python fence.
"""


def build_tester_prompt(
    project_type: str,
    file_structure: dict[str, str],
    api_contracts: list[dict],
    tech_stack: list[str],
    instructions: str,
) -> str:
    contracts_text = "\n".join(
        [
            f"- file={c.get('file')} function/route={c.get('function') or c.get('route') or ''} args={c.get('args') or ''} returns={c.get('returns') or ''}"
            for c in api_contracts
        ]
    )
    files_text = "\n".join([f"- {k}: {v}" for k, v in (file_structure or {}).items()])
    stack = ", ".join(tech_stack) if tech_stack else "(unspecified)"

    return f"""Project type: {project_type}
Tech stack: {stack}

Files planned:
{files_text if files_text else '(none)'}

API contracts:
{contracts_text if contracts_text else '(none)'}

Tester instructions:
{instructions}

Write pytest tests that validate the required behavior described by the API contracts.
Assumptions:
- Tests live in `tests/test_main.py`
- Import modules from the project root (you may need to adjust sys.path in tests)
- If this is a web API (FastAPI/Flask/etc), use the appropriate TestClient / httpx approach.

Return only the test file content.

- If main app file is main.py, import as: from main import app
- NEVER import from a package named after the project
- Always add this at the top of the test file before any imports:
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

Return only the test file content.
"""

