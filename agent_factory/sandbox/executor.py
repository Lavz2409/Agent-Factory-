from __future__ import annotations

import json
import os
import subprocess

from agent_factory.config import SANDBOX_TIMEOUT_SECONDS


class SandboxExecutor:
    def __init__(self, venv_path: str, project_path: str):
        self.venv_path = venv_path
        self.project_path = project_path
        scripts_dir = os.path.join(venv_path, "Scripts" if os.name == "nt" else "bin")

        self.python_bin = os.path.join(scripts_dir, "python.exe" if os.name == "nt" else "python")
        self.pytest_bin = os.path.join(scripts_dir, "pytest.exe" if os.name == "nt" else "pytest")

    def _pytest_cmd(self) -> list[str]:
        # Prefer pytest binary if it exists; otherwise use `python -m pytest`.
        if os.path.exists(self.pytest_bin) and os.path.basename(self.pytest_bin).lower().startswith("pytest"):
            return [
                self.pytest_bin,
                "tests/",
                "--tb=short",
                "--json-report",
                "--json-report-file=test_report.json",
                "-v",
            ]
        return [
            self.python_bin,
            "-m",
            "pytest",
            "tests/",
            "--tb=short",
            "--json-report",
            "--json-report-file=test_report.json",
            "-v",
        ]

    def run_tests(self) -> dict:
        """Run pytest in isolated venv, capture structured results."""
        try:
            result = subprocess.run(
                self._pytest_cmd(),
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=SANDBOX_TIMEOUT_SECONDS,
            )

            report_path = os.path.join(self.project_path, "test_report.json")
            try:
                with open(report_path, encoding="utf-8") as f:
                    report = json.load(f)
                tests = report.get("tests", [])
                summary = report.get("summary", {}) or {}
                # Plugin uses different keys across versions; handle common shape.
                failed = summary.get("failed")
                if failed is None:
                    # Fallback: infer from return code
                    passed = result.returncode == 0
                else:
                    passed = int(failed) == 0
            except Exception:
                tests = []
                passed = result.returncode == 0

            return {
                "passed": bool(passed),
                "tests": tests,
                "error_log": (result.stdout or "") + (result.stderr or ""),
                "returncode": result.returncode,
            }

        except subprocess.TimeoutExpired:
            return {
                "passed": False,
                "tests": [],
                "error_log": f"Timeout after {SANDBOX_TIMEOUT_SECONDS}s",
                "returncode": -1,
            }
        except Exception as e:
            return {
                "passed": False,
                "tests": [],
                "error_log": str(e),
                "returncode": -1,
            }
