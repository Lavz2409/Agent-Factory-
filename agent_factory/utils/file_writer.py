from __future__ import annotations

from pathlib import Path

from agent_factory.config import OUTPUT_DIR


def write_single_file(path: str, content: str) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content or "", encoding="utf-8")


def write_project_files(project_name: str, files: dict[str, str], libraries: list[str]) -> str:
    project_path = OUTPUT_DIR / (project_name or "generated_project")
    (project_path / "tests").mkdir(parents=True, exist_ok=True)

    for filename, code in (files or {}).items():
        if filename.strip() == "":
            continue
        # Always write to project root, preserving any subdirectory the
        # LLM specified (e.g. "routers/todo.py") but never prepending src/.
        target = project_path / filename
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(code or "", encoding="utf-8")

    # Generate requirements.txt if coder didn't produce one
    req_path = project_path / "requirements.txt"
    if not req_path.exists():
        deps = sorted({d.strip() for d in (libraries or []) if str(d).strip()})
        req_path.write_text("\n".join(deps) + ("\n" if deps else ""), encoding="utf-8")

    run_sh = project_path / "run.sh"
    if not run_sh.exists():
        run_sh.write_text(
            "#!/usr/bin/env bash\necho 'See generated files for entry point.'\n",
            encoding="utf-8",
        )

    return str(project_path.resolve())

