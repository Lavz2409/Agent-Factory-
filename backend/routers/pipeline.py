from __future__ import annotations

import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.services import pipeline_service

router = APIRouter(tags=["pipeline"])


class RunRequest(BaseModel):
    requirement: str


@router.post("/run")
async def start_run(body: RunRequest) -> dict:
    if not body.requirement.strip():
        raise HTTPException(status_code=400, detail="requirement cannot be empty")
    job_id = str(uuid.uuid4())[:12]
    await pipeline_service.launch_job(job_id, body.requirement.strip())
    return {"job_id": job_id, "status": "running", "ws_url": f"/ws/{job_id}"}


@router.get("/status/{job_id}")
async def get_status(job_id: str) -> dict:
    status = pipeline_service.get_status(job_id)
    if status is None:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found.")
    return {"job_id": job_id, **status}
