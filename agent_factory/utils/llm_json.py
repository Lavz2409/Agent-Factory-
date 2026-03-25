"""
Strict JSON extraction from LLM output, validation hooks, and one-shot retry.
Used by planner / architect / coder — logs failures; fallback only with FALLBACK TRIGGERED.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Callable

logger = logging.getLogger(__name__)

RETRY_SUFFIX = """
Your previous response was invalid. Return ONLY valid JSON. No markdown. No explanation.
If you fail, the system will reject your response.
"""


def log_fallback(agent: str, reason: str) -> None:
    logger.error("FALLBACK TRIGGERED — agent=%s reason=%s", agent, reason)


def _strip_code_fences(text: str) -> str:
    """Remove ```json ... ``` or ``` ... ``` wrappers."""
    t = text.strip()
    if not t.startswith("```"):
        return t
    lines = t.split("\n")
    if not lines:
        return t
    if lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]
    return "\n".join(lines).strip()


def _extract_json_object(text: str) -> str | None:
    """Best-effort: first balanced {...} block or greedy match."""
    t = _strip_code_fences(text.strip())
    try:
        json.loads(t)
        return t
    except json.JSONDecodeError:
        pass
    m = re.search(r"\{[\s\S]*\}", t)
    if m:
        return m.group(0)
    return None


def parse_json_from_llm(
    text: str | None,
    *,
    agent: str,
    log_raw_on_fail: bool = True,
) -> dict[str, Any] | None:
    """
    Parse JSON from raw LLM text. Returns None on failure (no silent fallback).
    Logs truncated raw output when parsing fails.
    """
    if text is None or not str(text).strip():
        if log_raw_on_fail:
            logger.warning("parse_json_from_llm: empty response agent=%s", agent)
        return None
    raw = str(text)
    blob = _extract_json_object(raw)
    if not blob:
        if log_raw_on_fail:
            logger.error(
                "parse_json_from_llm: no JSON object found agent=%s raw=%r",
                agent,
                raw[:4000],
            )
        return None
    try:
        data = json.loads(blob)
        if isinstance(data, dict):
            logger.debug("parse_json_from_llm: ok agent=%s keys=%s", agent, list(data.keys()))
            return data
    except json.JSONDecodeError as e:
        if log_raw_on_fail:
            logger.error(
                "parse_json_from_llm: JSONDecodeError agent=%s err=%s blob=%r",
                agent,
                e,
                blob[:4000],
            )
    return None


def invoke_json_with_retry(
    bedrock: Any,
    model_id: str,
    user_prompt: str,
    system_prompt: str,
    *,
    agent: str,
    validate: Callable[[dict[str, Any]], bool],
    emergency_fallback: dict[str, Any],
) -> dict[str, Any]:
    """
    Invoke Bedrock (or mock), parse JSON, validate. On failure, retry once with stricter suffix.
    If still invalid, log FALLBACK TRIGGERED and return emergency_fallback.
    """
    def _once(up: str, attempt: int) -> dict[str, Any] | None:
        raw = bedrock.invoke(model_id, up, system_prompt)
        logger.info(
            "llm raw response agent=%s attempt=%s len=%s",
            agent,
            attempt,
            len(raw or ""),
        )
        logger.debug("llm raw (truncated) agent=%s: %s", agent, (raw or "")[:8000])
        parsed = parse_json_from_llm(raw, agent=agent)
        if parsed is not None and validate(parsed):
            logger.info("llm parsed+validated ok agent=%s attempt=%s", agent, attempt)
            return parsed
        if parsed is not None:
            logger.warning("llm parsed but validation failed agent=%s attempt=%s", agent, attempt)
        return None

    first = _once(user_prompt, 1)
    if first is not None:
        return first

    second = _once(user_prompt.strip() + "\n\n" + RETRY_SUFFIX, 2)
    if second is not None:
        return second

    log_fallback(agent, "parse or validation failed after retry")
    return dict(emergency_fallback)


# Backward-compatible wrapper for layers that still call parse_json_safely
def parse_json_safely(
    text: str | None,
    fallback: dict[str, Any],
    *,
    agent: str = "legacy",
) -> dict[str, Any]:
    """Prefer parse_json_from_llm; if None, log and return fallback (explicit legacy path)."""
    p = parse_json_from_llm(text, agent=agent)
    if p is not None:
        return p
    log_fallback(agent, "parse_json_safely legacy fallback")
    return dict(fallback)
