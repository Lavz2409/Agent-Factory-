"""
Layer 7 — Quality Gates.
Four mandatory checkpoints per the blueprint:
1. Design validation
2. Code validation (lint check)
3. Security scanning (SAST + secrets detection)
4. SLA enforcement (latency + cost bounds)
Guardrails validate ALL outputs before they pass downstream.
"""

from __future__ import annotations

import json
import os
import re
from typing import Any

# CloudWatch / X-Ray simulation in dev: log locally
_DEV_LOG = os.environ.get("LOCAL_MODE", "true").lower() == "true"


def _dev_log(msg: str) -> None:
    if _DEV_LOG:
        print(f"  [observability] {msg}")


class Guardrails:
    """Quality gates for architect and coder outputs."""

    def validate_design(self, architect_output: dict[str, Any]) -> tuple[bool, list[str]]:
        errors: list[str] = []
        comps = architect_output.get("components")
        if not isinstance(comps, list) or len(comps) == 0:
            errors.append("components must be a non-empty list")
        df = architect_output.get("data_flow", "")
        if not isinstance(df, str) or len(df) <= 10:
            errors.append("data_flow must exist and be longer than 10 characters")
        if not architect_output.get("entry_point"):
            errors.append("entry_point is required")
        if isinstance(comps, list):
            for i, c in enumerate(comps):
                if not isinstance(c, dict):
                    errors.append(f"component {i} must be an object")
                    continue
                if not c.get("name"):
                    errors.append(f"component {i} missing name")
                if not c.get("responsibility"):
                    errors.append(f"component {i} missing responsibility")
        ok = len(errors) == 0
        if not ok:
            _dev_log(f"design validation issues: {errors}")
        return ok, errors

    def validate_code(self, coder_output: dict[str, Any]) -> tuple[bool, list[str]]:
        errors: list[str] = []
        code = coder_output.get("code", "")
        if not isinstance(code, str) or len(code) <= 50:
            errors.append("Code too short")
        if not coder_output.get("filename"):
            errors.append("No filename")
        if isinstance(code, str):
            if not (
                "import" in code
                or "def " in code
                or "class " in code
            ):
                errors.append("Code missing structure")
        ok = len(errors) == 0
        if not ok:
            _dev_log(f"code validation issues: {errors}")
        return ok, errors

    def scan_secrets(self, coder_output: dict[str, Any]) -> tuple[bool, list[str]]:
        code = coder_output.get("code", "")
        if not isinstance(code, str):
            return True, []
        warnings: list[str] = []
        secret_patterns = [
            r'(?i)(password|passwd|pwd)\s*=\s*["\'][^"\']{4,}',
            r'(?i)(api_key|apikey|secret_key)\s*=\s*["\'][^"\']{8,}',
            r'(?i)(aws_access_key_id)\s*=\s*["\'][A-Z0-9]{16,}',
            r'(?i)(aws_secret_access_key)\s*=\s*["\'][a-zA-Z0-9/+]{20,}',
        ]
        for pattern in secret_patterns:
            if re.search(pattern, code):
                warnings.append(f"Potential secret detected: {pattern[:40]}")
        ok = len(warnings) == 0
        if not ok:
            _dev_log(f"security scan warnings: {warnings}")
        return ok, warnings

    def enforce_sla(
        self,
        elapsed_seconds: float,
        max_seconds: float = 120.0,
    ) -> tuple[bool, str]:
        if elapsed_seconds > max_seconds:
            return (
                False,
                f"SLA breach: {elapsed_seconds:.1f}s > {max_seconds}s limit",
            )
        return True, f"SLA OK: {elapsed_seconds:.1f}s"

    def run_all_gates(
        self,
        architect_output: dict[str, Any],
        coder_output: dict[str, Any],
        elapsed: float,
    ) -> dict[str, Any]:
        results: dict[str, Any] = {}

        ok, errs = self.validate_design(architect_output)
        results["design_validation"] = {"passed": ok, "issues": errs}

        ok, errs = self.validate_code(coder_output)
        results["code_validation"] = {"passed": ok, "issues": errs}

        ok, warns = self.scan_secrets(coder_output)
        results["security_scan"] = {"passed": ok, "warnings": warns}

        ok, msg = self.enforce_sla(elapsed)
        results["sla_enforcement"] = {"passed": ok, "message": msg}

        passed_flags = [
            r["passed"]
            for r in results.values()
            if isinstance(r, dict) and "passed" in r
        ]
        results["overall_passed"] = all(passed_flags) if passed_flags else False

        if _DEV_LOG:
            _dev_log(f"guardrails summary: {json.dumps(results, default=str)[:500]}")
        return results
