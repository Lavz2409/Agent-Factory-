"""
ValidationAgent — final step in the 8-agent pipeline.

Performs deterministic, static checks on everything produced by the preceding
agents (code completeness, env docs, README, integration, marketing), plus an
LLM "sanity" review of the full artefact set.  Produces a structured Validation
Report (JSON + Markdown) that is saved alongside the project and streamed to
the frontend FILES panel.

The checks are DETERMINISTIC first — we don't rely on the LLM to decide if a
file is truncated.  The LLM is only used for the final narrative summary.
"""
from __future__ import annotations

import json
import os
import re

from agent_factory.core.base_agent import BaseAgent
from agent_factory.core.state import PipelineState


# ── Sanity-review system prompt ───────────────────────────────────────────────

VALIDATION_SUMMARY_SYSTEM = """\
You are a Senior QA Engineer reviewing an AI-generated codebase.

You will receive a compact JSON summary of the project (file count, detected
issues, pipeline status, token usage, etc.).

Respond with a SHORT Markdown section (max 10 bullet points) titled
"## 🧐 Senior QA Review" that lists:
  - the three most important wins
  - the three most important risks
  - a single go/no-go recommendation

Be realistic, technical, and specific.  Never invent issues that are not
evidenced in the JSON summary.  No preamble, no closing remarks, just the
Markdown section.
"""


# ── Agent implementation ───────────────────────────────────────────────────────

class ValidationAgent(BaseAgent):
    """Runs the quality gate and emits validation_report.md."""

    TRUNCATION_MARKERS = (
        "...",
        "// ...",
        "# ...",
        "/* ... */",
        "TODO",
        "Add logic here",
        "implement here",
        "fill in",
        "Your code here",
    )

    def __init__(self, llm_client) -> None:
        super().__init__("ValidationAgent", llm_client)

    # ── main entry ────────────────────────────────────────────────────────────

    def run(self, state: PipelineState) -> PipelineState:
        state.set_agent(self.name)
        self.log("Running static validation on all generated artefacts...")

        checks = {
            "code_completeness":  self._check_code_completeness(state),
            "architecture":       self._check_architecture(state),
            "integration":        self._check_integration(state),
            "documentation":      self._check_documentation(state),
            "marketing":          self._check_marketing(state),
            "usability":          self._check_usability(state),
        }

        issues = [i for c in checks.values() for i in c["issues"]]
        passed_count = sum(1 for c in checks.values() if c["pass"])
        total_count  = len(checks)
        score        = round((passed_count / total_count) * 10, 1) if total_count else 0.0
        ready        = len(issues) == 0

        summary = {
            "score":         score,
            "passed":        passed_count,
            "total":         total_count,
            "ready":         ready,
            "issues":        issues[:30],
            "file_count":    len(state.generated_files or {}),
            "pipeline":      state.supervisor_pipelines,
            "project_name":  state.project_name,
            "token_calls":   (state.token_usage or {}).get("calls", 0),
        }

        # LLM narrative
        qa_narrative = ""
        try:
            qa_narrative = self.call_llm(
                prompt="Project summary JSON:\n" + json.dumps(summary, indent=2),
                system=VALIDATION_SUMMARY_SYSTEM,
                use_cache=False,
            ).strip()
        except Exception as exc:
            self.log(f"LLM review skipped ({exc}); static report still emitted.")

        # Build Markdown report
        report_md = self._build_markdown(checks, summary, qa_narrative)

        # Persist
        state.validation_checks   = checks
        state.validation_issues   = issues
        state.validation_score    = score
        state.validation_ready    = ready
        state.validation_report   = report_md

        state.generated_files["validation_report.md"] = report_md

        output_dir = state.output_path
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            report_path = os.path.join(output_dir, "validation_report.md")
            with open(report_path, "w", encoding="utf-8") as fh:
                fh.write(report_md)
            state.validation_report_path = report_path

        self.log(
            f"Validation complete — score {score}/10, "
            f"{len(issues)} issue(s), ready={ready}"
        )
        return state

    # ── static checks ────────────────────────────────────────────────────────

    def _check_code_completeness(self, state: PipelineState) -> dict:
        issues: list[str] = []
        code_files = {
            p: c for p, c in (state.generated_files or {}).items()
            if not p.endswith(".md")
        }
        if not code_files:
            issues.append("No code files were generated.")
        else:
            for path, content in code_files.items():
                if not content or not content.strip():
                    issues.append(f"{path} is empty.")
                    continue
                low = content.lower()
                for marker in ("todo: implement", "add logic here", "your code here"):
                    if marker in low:
                        issues.append(f"{path} contains placeholder '{marker}'.")
                        break
                # Very short files (<40 chars) are almost certainly truncated
                if len(content.strip()) < 40 and not path.endswith((".env.example", ".gitignore")):
                    issues.append(f"{path} looks truncated (<40 chars).")
        return {"pass": not issues, "issues": issues}

    def _check_architecture(self, state: PipelineState) -> dict:
        issues: list[str] = []
        if not state.file_structure:
            issues.append("ArchitectAgent produced no file structure.")
        if not state.tech_stack:
            issues.append("No tech stack defined.")
        if not state.system_design:
            issues.append("No system design document was produced.")
        return {"pass": not issues, "issues": issues}

    def _check_integration(self, state: PipelineState) -> dict:
        issues: list[str] = []
        # Only enforce integration checks when the code branch ran
        is_code_run = bool(state.file_structure)
        if is_code_run:
            expected_markers = ("api.js", "api.ts", "AuthContext", "useAuth")
            files = list(state.generated_files.keys())
            if not any(m in f for f in files for m in expected_markers):
                issues.append(
                    "IntegrationAgent output not found "
                    "(expected api.js / AuthContext / useAuth)."
                )
        return {"pass": not issues, "issues": issues}

    def _check_documentation(self, state: PipelineState) -> dict:
        issues: list[str] = []
        if state.file_structure and not state.scribe_walkthrough:
            issues.append("Scribe did not produce a walkthrough.")
        # README.md or walkthrough.md should exist for code runs
        if state.file_structure and not any(
            name.lower() in ("readme.md", "walkthrough.md")
            for name in state.generated_files
        ):
            issues.append("No README.md or walkthrough.md in generated files.")
        return {"pass": not issues, "issues": issues}

    def _check_marketing(self, state: PipelineState) -> dict:
        issues: list[str] = []
        is_marketing_run = any(
            p.upper() == "MARKETING" for p in (state.supervisor_pipelines or [])
        )
        if is_marketing_run and not state.marketing_report:
            issues.append("MARKETING route selected but no marketing_report produced.")
        if state.marketing_report and len(state.marketing_report) < 800:
            issues.append("marketing_report.md is suspiciously short (<800 chars).")
        return {"pass": not issues, "issues": issues}

    def _check_usability(self, state: PipelineState) -> dict:
        issues: list[str] = []
        # walkthrough.md is accepted as the project's self-serve setup doc
        has_docs = any(
            p.lower().endswith(("readme.md", "walkthrough.md"))
            for p in (state.generated_files or {})
        )
        has_env = any(
            ".env.example" in p for p in (state.generated_files or {})
        )
        if state.file_structure:
            if not has_docs:
                issues.append("No README.md or walkthrough.md — developers can't self-serve setup.")
            if not has_env:
                issues.append("No .env.example — required env vars are undocumented.")
        return {"pass": not issues, "issues": issues}

    # ── markdown builder ─────────────────────────────────────────────────────

    @staticmethod
    def _fmt_check(title: str, result: dict) -> str:
        emoji = "✅" if result["pass"] else "❌"
        lines = [f"### {emoji} {title}"]
        if result["pass"]:
            lines.append("All checks passed.")
        else:
            for issue in result["issues"]:
                lines.append(f"- ❌ {issue}")
        return "\n".join(lines) + "\n"

    @classmethod
    def _build_markdown(
        cls,
        checks: dict[str, dict],
        summary: dict,
        qa_narrative: str,
    ) -> str:
        header = [
            "# Validation Report",
            "",
            f"**Project**: {summary.get('project_name') or '(unnamed)'}  ",
            f"**Pipeline**: {', '.join(summary.get('pipeline') or []) or '—'}  ",
            f"**Quality Score**: **{summary['score']}/10**  ",
            f"**Checks Passed**: {summary['passed']}/{summary['total']}  ",
            f"**Generated Files**: {summary['file_count']}  ",
            f"**LLM Calls**: {summary['token_calls']}  ",
            f"**Ready for Production**: {'✅ YES' if summary['ready'] else '❌ NO'}",
            "",
            "---",
            "",
        ]

        titles = {
            "code_completeness": "Code Completeness",
            "architecture":      "Architecture Validation",
            "integration":       "Integration Check",
            "documentation":     "Documentation Check",
            "marketing":         "Marketing Reality Check",
            "usability":         "Usability Check",
        }
        body = [cls._fmt_check(titles[k], checks[k]) for k in titles]

        footer: list[str] = []
        if summary["issues"]:
            footer.append("## 🐛 Issues Found\n")
            for i, issue in enumerate(summary["issues"], 1):
                footer.append(f"{i}. {issue}")
            footer.append("")
        else:
            footer.append("## 🐛 Issues Found\n\nNone — all checks passed.\n")

        if qa_narrative:
            footer.append("")
            footer.append(qa_narrative.strip())
            footer.append("")

        return "\n".join(header + body + footer).rstrip() + "\n"
