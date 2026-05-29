"""
REST API routes for Agent Factory IDE.
"""
from __future__ import annotations

import asyncio
import uuid

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.db import get_runs, get_run
from backend.api.ws import create_pipeline_run

router = APIRouter()


# ── request models ────────────────────────────────────────────────────────────

class RunRequest(BaseModel):
    requirement: str


class AgentRunRequest(BaseModel):
    input: str
    context: dict = {}


class AnalyzeRequest(BaseModel):
    files: dict[str, str]
    error: str = ""


# ── pipeline endpoints ────────────────────────────────────────────────────────

@router.post("/pipeline/start")
async def start_pipeline(body: RunRequest) -> dict:
    """Start a new pipeline run; returns run_id + WebSocket URL."""
    if not body.requirement.strip():
        raise HTTPException(status_code=400, detail="Requirement cannot be empty.")
    run_id = str(uuid.uuid4())[:12]
    loop = asyncio.get_event_loop()
    create_pipeline_run(run_id, body.requirement.strip(), loop)
    return {
        "run_id":  run_id,
        "status":  "started",
        "ws_url":  f"/ws/pipeline/{run_id}",
    }


@router.post("/pipeline/{run_id}/pause")
async def pause_pipeline(run_id: str) -> dict:
    return {"run_id": run_id, "status": "pause_requested"}


@router.post("/pipeline/{run_id}/resume")
async def resume_pipeline(run_id: str) -> dict:
    return {"run_id": run_id, "status": "resume_requested"}


@router.post("/pipeline/{run_id}/cancel")
async def cancel_pipeline(run_id: str) -> dict:
    return {"run_id": run_id, "status": "cancelled"}


# ── run history ───────────────────────────────────────────────────────────────

@router.get("/runs")
async def list_runs() -> list[dict]:
    return get_runs(30)


@router.get("/runs/{run_id}")
async def get_run_detail(run_id: str) -> dict:
    run = get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found.")
    return run


# ── code analysis (DebugAgent) ────────────────────────────────────────────────

@router.post("/analyze")
async def analyze_code(body: AnalyzeRequest) -> dict:
    """Analyze files + error log and return AI-powered fix suggestions."""
    from agent_factory.core.llm_client import LLMClient
    llm = LLMClient()
    files_text = "\n\n".join(
        f"--- {fname} ---\n{content[:800]}"
        for fname, content in (body.files or {}).items()
    )
    prompt = (
        "You are a senior engineer debugging a failing project. "
        "Analyze the error and files, then propose specific code fixes.\n\n"
        f"ERROR:\n{body.error[:1500]}\n\n"
        f"FILES:\n{files_text}"
    )
    try:
        analysis = llm.call(prompt=prompt, agent_name="DebugAgent")
        return {"analysis": analysis, "suggested_fixes": [analysis]}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ── standalone agent run ──────────────────────────────────────────────────────

@router.post("/agents/{agent_name}/run")
async def run_single_agent(agent_name: str, body: AgentRunRequest) -> dict:
    run_id = str(uuid.uuid4())[:8]
    return {"run_id": run_id, "status": "queued", "agent": agent_name}
