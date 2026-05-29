from __future__ import annotations

from typing import Any


def format_test_results(results: dict[str, Any]) -> str:
    passed = bool(results.get("passed"))
    error_log = results.get("error_log", "")
    return "PASSED\n" + (error_log or "") if passed else "FAILED\n" + (error_log or "")

