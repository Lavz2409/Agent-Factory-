from __future__ import annotations

import asyncio
import logging
from typing import Optional

from agent_factory.core.state import PipelineState
from agent_factory.pipeline.runner import PipelineError, PipelineRunner

logger = logging.getLogger(__name__)
_jobs: dict[str, dict] = {}


def create_job(job_id: str) -> asyncio.Queue:
    queue: asyncio.Queue = asyncio.Queue()
    _jobs[job_id] = {"queue": queue, "status": "pending", "result": None}
    return queue


async def launch_job(job_id: str, requirement: str) -> None:
    queue = create_job(job_id)
    _jobs[job_id]["status"] = "running"
    asyncio.create_task(
        _run_pipeline(job_id, requirement, queue),
        name=f"pipeline-{job_id}",
    )


def get_queue(job_id: str) -> Optional[asyncio.Queue]:
    return _jobs.get(job_id, {}).get("queue")


def get_status(job_id: str) -> Optional[dict]:
    job = _jobs.get(job_id)
    if not job:
        return None
    return {"status": job["status"], "result": job.get("result")}


async def _run_pipeline(job_id: str, requirement: str, queue: asyncio.Queue) -> None:
    loop   = asyncio.get_running_loop()
    runner = PipelineRunner()

    def _cb(agent_name: str, status: str, duration: float) -> None:
        loop.call_soon_threadsafe(
            queue.put_nowait,
            {"type": "progress", "agent": agent_name, "status": status, "duration": duration},
        )

    try:
        state: PipelineState = await loop.run_in_executor(
            None, lambda: runner.run(requirement, _cb)
        )
        result = {
            "project_name":    state.project_name,
            "output_path":     state.output_path,
            "test_passed":     state.test_passed,
            "token_usage":     state.token_usage,
            "error_log":       state.error_log,
            "generated_files":     list(state.generated_files.keys()),
            # ScribeAgent output (TesterAgent disabled — ScribeAgent handles final step)
            "scribe_output":           state.scribe_walkthrough or "",
            "scribe_saved_files":      state.scribe_saved_files or [],
            "scribe_output_dir":       state.scribe_output_dir or "",
            "scribe_readme_path":      "",   # removed — walkthrough.md is canonical
            "scribe_walkthrough_path": state.scribe_walkthrough_path or "",
            "scribe_run_commands":     state.scribe_run_commands or [],
            "activity_log":            state.activity_log or [],
        }
        _jobs[job_id]["status"] = "done"
        _jobs[job_id]["result"] = result
        await queue.put({"type": "done", "result": result})

    except PipelineError as exc:
        _jobs[job_id]["status"] = "error"
        await queue.put({"type": "error", "agent": exc.agent_name, "message": str(exc.cause)})

    except Exception as exc:
        logger.exception("Job %s: unexpected failure", job_id)
        _jobs[job_id]["status"] = "error"
        await queue.put({"type": "error", "message": str(exc)})
