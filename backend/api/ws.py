"""
WebSocket endpoint — bridges the synchronous Python pipeline with the React frontend.

Strategy: run the pipeline in a daemon thread, poll PipelineState changes every
150 ms, convert changes into PipelineEvent objects, and push them onto an asyncio
Queue that the WebSocket coroutine drains.
"""
from __future__ import annotations

import asyncio
import json
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from agent_factory.core.pipeline import AgentFactoryPipeline
from agent_factory.core.state import PipelineState, PipelineStatus
from backend.db import save_run, update_run, save_log, save_files

ws_router = APIRouter()

# run_id → asyncio.Queue[PipelineEvent]
_active_queues: dict[str, asyncio.Queue] = {}


# ── event model ───────────────────────────────────────────────────────────────

@dataclass
class PipelineEvent:
    type: str      # agent_start | agent_done | log | file | status | complete | error | ping
    agent: str     # agent name or "pipeline"
    data: dict     # payload
    ts: float = field(default_factory=time.time)

    def to_json(self) -> str:
        return json.dumps({
            "type":      self.type,
            "agent":     self.agent,
            "data":      self.data,
            "timestamp": self.ts,
        })


# ── pipeline runner ───────────────────────────────────────────────────────────

class PipelineRunner:
    """Runs the pipeline in a background thread and pushes events onto a queue."""

    POLL_INTERVAL = 0.15  # seconds

    def __init__(
        self,
        run_id: str,
        requirement: str,
        queue: asyncio.Queue,
        loop: asyncio.AbstractEventLoop,
    ) -> None:
        self.run_id = run_id
        self.requirement = requirement
        self.queue = queue
        self.loop = loop
        self._state: PipelineState | None = None
        self._finished = threading.Event()

    def start(self) -> None:
        threading.Thread(target=self._run_pipeline, daemon=True, name=f"pipeline-{self.run_id}").start()
        threading.Thread(target=self._monitor, daemon=True, name=f"monitor-{self.run_id}").start()

    # ── pipeline thread ───────────────────────────────────────────────────────

    def _run_pipeline(self) -> None:
        try:
            pipeline = AgentFactoryPipeline()
            self._state = PipelineState(raw_requirement=self.requirement)
            result = pipeline.run(self.requirement, state=self._state)

            # Push all generated files at the end (in case monitor missed any)
            for filename, content in result.generated_files.items():
                self._emit(PipelineEvent(
                    type="file",
                    agent="CoderAgent",
                    data={"filename": filename, "content": content},
                ))

            # Emit walkthrough.md as a file so it appears in the FILES panel
            if result.scribe_walkthrough:
                self._emit(PipelineEvent(
                    type="file",
                    agent="ScribeAgent",
                    data={"filename": "walkthrough.md", "content": result.scribe_walkthrough},
                ))

            self._emit(PipelineEvent(
                type="complete",
                agent="pipeline",
                data={
                    "status":              str(result.status.value),
                    "project_name":        result.project_name,
                    "output_path":         result.output_path,
                    "test_passed":         result.test_passed,
                    "token_usage":         result.token_usage,
                    "error_log":           (result.error_log or "")[:2000],
                    "generated_files":     list(result.generated_files.keys()),
                    # SupervisorAgent routing result
                    "supervisor_pipelines":  result.supervisor_pipelines or [],
                    "supervisor_confidence": result.supervisor_confidence,
                    "supervisor_reason":     result.supervisor_reason or "",
                    "supervisor_tools":      result.supervisor_tools or [],
                    "supervisor_complexity": result.supervisor_complexity or "",
                    "supervisor_modules":    result.supervisor_modules or [],
                    # MarketingAgent output
                    "marketing_report":      result.marketing_report or "",
                    "marketing_report_path": result.marketing_report_path or "",
                    # UIUXAgent output
                    "ui_design_system":      result.ui_design_system or "",
                    "ui_files":              result.ui_files or [],
                    # IntegrationAgent output
                    "integration_guide":     result.integration_guide or "",
                    "integration_notes":     result.integration_notes or [],
                    "integration_files":     result.integration_files or [],
                    # ValidationAgent output
                    "validation_report":       result.validation_report or "",
                    "validation_report_path":  result.validation_report_path or "",
                    "validation_score":        result.validation_score,
                    "validation_ready":        result.validation_ready,
                    "validation_issues":       result.validation_issues or [],
                    # ScribeAgent output
                    "scribe_output":           result.scribe_walkthrough or "",
                    "scribe_saved_files":      result.scribe_saved_files or [],
                    "scribe_output_dir":       result.scribe_output_dir or "",
                    "scribe_readme_path":      "",   # removed — walkthrough.md is canonical
                    "scribe_walkthrough_path": result.scribe_walkthrough_path or "",
                    "scribe_run_commands":     result.scribe_run_commands or [],
                    # Activity log — one entry per agent
                    "activity_log":            result.activity_log or [],
                },
            ))

            update_run(
                self.run_id,
                status=str(result.status.value),
                project_name=result.project_name,
                output_path=result.output_path,
                test_passed=1 if result.test_passed else 0,
                token_usage=json.dumps(result.token_usage),
                error_log=(result.error_log or "")[:5000],
                completed_at=datetime.utcnow().isoformat(),
            )
            save_files(self.run_id, result.generated_files)

        except Exception as exc:
            self._emit(PipelineEvent(
                type="error",
                agent="pipeline",
                data={"message": str(exc)},
            ))
            update_run(self.run_id, status="failed", error_log=str(exc)[:5000])
        finally:
            self._finished.set()

    # ── monitor thread ────────────────────────────────────────────────────────

    def _monitor(self) -> None:
        seen_logs: int = 0
        seen_files: set[str] = set()
        last_agent: str = ""

        while not self._finished.is_set():
            state = self._state
            if state is None:
                time.sleep(self.POLL_INTERVAL)
                continue

            current_agent = state.current_agent or ""

            # Agent transitions
            if current_agent != last_agent:
                if last_agent:
                    self._emit(PipelineEvent(type="agent_done", agent=last_agent, data={}))
                if current_agent:
                    self._emit(PipelineEvent(
                        type="agent_start",
                        agent=current_agent,
                        data={"description": _agent_desc(current_agent)},
                    ))
                last_agent = current_agent

            # New log lines
            logs = state.logs or []
            if len(logs) > seen_logs:
                for msg in logs[seen_logs:]:
                    level = _classify_level(msg)
                    self._emit(PipelineEvent(
                        type="log",
                        agent=current_agent or "pipeline",
                        data={"message": msg, "level": level},
                    ))
                    try:
                        save_log(self.run_id, current_agent or "pipeline", level, msg)
                    except Exception:
                        pass
                seen_logs = len(logs)

            # New generated files (stream as they appear)
            new_files = set(state.generated_files.keys()) - seen_files
            for fname in sorted(new_files):
                self._emit(PipelineEvent(
                    type="file",
                    agent="CoderAgent",
                    data={"filename": fname, "content": state.generated_files[fname]},
                ))
                seen_files.add(fname)

            # Token usage snapshot
            if state.token_usage:
                self._emit(PipelineEvent(
                    type="status",
                    agent="pipeline",
                    data={
                        "current_agent": current_agent,
                        "token_usage":   state.token_usage,
                        "status":        str(state.status.value),
                    },
                ))

            time.sleep(self.POLL_INTERVAL)

        # Final agent_done for the last agent
        if last_agent:
            self._emit(PipelineEvent(type="agent_done", agent=last_agent, data={}))

    # ── helpers ───────────────────────────────────────────────────────────────

    def _emit(self, event: PipelineEvent) -> None:
        asyncio.run_coroutine_threadsafe(self.queue.put(event), self.loop)


def _classify_level(msg: str) -> str:
    lower = msg.lower()
    if any(k in lower for k in ("error", "fail", "✗", "exception")):
        return "error"
    if "warn" in lower:
        return "warn"
    if any(k in lower for k in ("✓", "complete", "passed", "success")):
        return "success"
    return "info"


def _agent_desc(name: str) -> str:
    return {
        "SupervisorAgent":  "Routing requirement to the best pipeline",
        "MarketingAgent":   "Generating marketing intelligence report",
        "PlannerAgent":     "Analysing input & decomposing into tasks",
        "ResearcherAgent":  "Gathering libraries & patterns",
        "ArchitectAgent":   "Designing system architecture",
        "CoderAgent":       "Writing production code file by file",
        "UIUXAgent":        "Designing dark + light mode UI system",
        "IntegrationAgent": "Wiring frontend ⇄ backend integration",
        "ScribeAgent":      "Generating project walkthrough & saving files",
        "ValidationAgent":  "Running quality gate & validation report",
        "DebugAgent":       "Diagnosing and fixing errors",
        "ReviewerAgent":    "Evaluating code quality",
    }.get(name, name)


# ── public API (called from routes.py) ────────────────────────────────────────

def create_pipeline_run(
    run_id: str,
    requirement: str,
    loop: asyncio.AbstractEventLoop,
) -> None:
    queue: asyncio.Queue = asyncio.Queue()
    _active_queues[run_id] = queue
    save_run(run_id, requirement)
    PipelineRunner(run_id, requirement, queue, loop).start()


# ── WebSocket endpoint ────────────────────────────────────────────────────────

@ws_router.websocket("/ws/pipeline/{run_id}")
async def pipeline_ws(websocket: WebSocket, run_id: str) -> None:
    await websocket.accept()

    queue = _active_queues.get(run_id)
    if queue is None:
        await websocket.send_text(json.dumps({
            "type": "error",
            "agent": "server",
            "data": {"message": f"No active run with id '{run_id}'."},
        }))
        await websocket.close()
        return

    try:
        while True:
            try:
                event: PipelineEvent = await asyncio.wait_for(queue.get(), timeout=25.0)
                await websocket.send_text(event.to_json())
                if event.type in ("complete", "error"):
                    break
            except asyncio.TimeoutError:
                # Keepalive ping
                await websocket.send_text(json.dumps({"type": "ping", "agent": "", "data": {}}))
    except WebSocketDisconnect:
        pass
    finally:
        _active_queues.pop(run_id, None)
