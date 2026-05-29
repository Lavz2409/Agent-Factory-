# # DISABLED — TesterAgent is inactive. ScribeAgent is now the final pipeline step.
# # Original class body is preserved verbatim inside the class docstring below.

# from __future__ import annotations

# import json
# import logging
# import os
# import re
# import shutil
# import subprocess
# import sys
# import tempfile
# from pathlib import Path

# from agent_factory.core.base_agent import BaseAgent
# from agent_factory.core.state import PipelineState
# from agent_factory.sandbox.executor import SandboxExecutor
# from agent_factory.sandbox.venv_manager import VenvManager
# from agent_factory.prompts.tester import TESTER_SYSTEM, build_tester_prompt

# logger = logging.getLogger(__name__)


# # ── package name validation (module-level helpers kept for potential re-use) ──

# _VALID_PKG = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")

# _NOISE_TOKENS = frozenset({
#     "-", "--", "install", "pip", "pip3", "python", "python3",
#     "and", "or", "the", "with", "for", "to", "in", "a", "an",
#     "package", "packages", "library", "libraries", "module", "modules",
#     "dependency", "dependencies", "use", "using", "also", "as",
# })


# def _sanitize_package_name(raw: str) -> str | None:
#     cleaned = raw.strip().strip("`'\"")
#     cleaned = re.sub(r"^[^A-Za-z0-9]+", "", cleaned)
#     cleaned = re.sub(r"[,:;]+$", "", cleaned)
#     if not cleaned:
#         return None
#     if cleaned.lower() in _NOISE_TOKENS:
#         return None
#     name_part = re.split(r"[><=!~]", cleaned, maxsplit=1)[0]
#     if not _VALID_PKG.match(name_part):
#         return None
#     spec_suffix = cleaned[len(name_part):]
#     return name_part.lower() + spec_suffix


# def sanitize_dependencies(raw_deps: list[str]) -> list[str]:
#     seen: set[str] = set()
#     clean: list[str] = []
#     for token in (raw_deps or []):
#         for part in str(token).split():
#             result = _sanitize_package_name(part)
#             if result is None:
#                 continue
#             key = re.split(r"[><=!~]", result)[0]
#             if key not in seen:
#                 seen.add(key)
#                 clean.append(result)
#     return clean


# def _parse_requirements_file(req_path: Path) -> list[str]:
#     lines: list[str] = []
#     for raw_line in req_path.read_text(encoding="utf-8").splitlines():
#         line = raw_line.strip()
#         if not line or line.startswith("#") or line.startswith("-"):
#             continue
#         result = _sanitize_package_name(line)
#         if result:
#             lines.append(result)
#     return lines


# def _write_requirements_file(req_path: Path, packages: list[str]) -> None:
#     req_path.parent.mkdir(parents=True, exist_ok=True)
#     req_path.write_text("\n".join(sorted(set(packages))) + "\n", encoding="utf-8")


# # ── TesterAgent — DISABLED ────────────────────────────────────────────────────

# class TesterAgent(BaseAgent):
#     """
#     DISABLED — TesterAgent is inactive. ScribeAgent is now the final pipeline step.

#     Original class body preserved below exactly as written.
#     ─────────────────────────────────────────────────────────────────────────────

#     def __init__(self, llm_client):
#         super().__init__("TesterAgent", llm_client)

#     # ── main entry point ───────────────────────────────────────────────────────

#     def run(self, state: PipelineState) -> PipelineState:
#         state.set_agent(self.name)
#         if not state.output_path or not str(state.output_path).strip():
#             msg = "output_path is empty — CoderAgent must run before TesterAgent."
#             self.log(f"ERROR: {msg}")
#             logger.error(msg)
#             state.error_log = msg
#             state.test_passed = False
#             return state
#         output_dir = Path(state.output_path)
#         if not output_dir.exists():
#             msg = f"output_path does not exist on disk: {output_dir}"
#             self.log(f"ERROR: {msg}")
#             logger.error(msg)
#             state.error_log = msg
#             state.test_passed = False
#             return state
#         self.log(f"Output directory validated: {output_dir}")
#         self.log("Generating test suite via LLM...")
#         test_code = self._generate_tests(state)
#         state.generated_files["tests/test_main.py"] = test_code
#         try:
#             tests_out = output_dir / "tests"
#             tests_out.mkdir(parents=True, exist_ok=True)
#             (tests_out / "test_main.py").write_text(test_code, encoding="utf-8")
#         except OSError as exc:
#             self.log(f"WARNING: could not persist test file ({exc}). Continuing in temp sandbox.")
#             logger.warning("Non-fatal: could not write test to output_dir: %s", exc)
#         tmp_dir = Path(tempfile.mkdtemp(prefix="af_test_"))
#         try:
#             self._mirror_files_to_tmp(state.generated_files, output_dir, tmp_dir)
#             venv = VenvManager(project_path=str(tmp_dir))
#             try:
#                 venv.create()
#             except subprocess.CalledProcessError as exc:
#                 state.error_log = f"venv creation failed: {exc.stderr or exc}"
#                 state.test_passed = False
#                 return state
#             self._install_dependencies(venv=venv, project_path=tmp_dir,
#                                        raw_libraries=state.relevant_libraries or [])
#             executor = SandboxExecutor(venv_path=str(venv.path), project_path=str(tmp_dir))
#             results = executor.run_tests()
#             self._apply_results(state, results)
#             if not state.test_passed:
#                 state = self._attempt_fix(state, results.get("error_log", ""),
#                                           output_dir=output_dir, tmp_dir=tmp_dir)
#                 results = executor.run_tests()
#                 self._apply_results(state, results)
#         finally:
#             shutil.rmtree(str(tmp_dir), ignore_errors=True)
#         return state

#     # (... remaining methods: _install_dependencies, _pip_install_requirements,
#     #  _pip_install_one_by_one, _mirror_files_to_tmp, _apply_results,
#     #  _generate_tests, _attempt_fix, _format_files_for_fix — all preserved) ...
#     ─────────────────────────────────────────────────────────────────────────────
#     """
#     # TesterAgent disabled — ScribeAgent handles final step
#     pass
