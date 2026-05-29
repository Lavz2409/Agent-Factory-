from __future__ import annotations

import asyncio
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.services import pipeline_service

router = APIRouter(tags=["websocket"])
logger = logging.getLogger(__name__)


@router.websocket("/ws/{job_id}")
async def ws_pipeline(websocket: WebSocket, job_id: str) -> None:
    await websocket.accept()
    queue = pipeline_service.get_queue(job_id)
    if queue is None:
        await websocket.send_json({"type": "error", "message": f"Unknown job: '{job_id}'"})
        await websocket.close(code=1008)
        return

    ping_task = asyncio.create_task(_ping(websocket))
    try:
        while True:
            msg = await queue.get()
            await websocket.send_json(msg)
            if msg.get("type") in ("done", "error"):
                break
    except WebSocketDisconnect:
        logger.info("Client disconnected from job %s", job_id)
    except Exception as exc:
        logger.error("WebSocket error job %s: %s", job_id, exc)
    finally:
        ping_task.cancel()
        try:
            await websocket.close()
        except Exception:
            pass


async def _ping(ws: WebSocket) -> None:
    while True:
        await asyncio.sleep(15)
        try:
            await ws.send_json({"type": "ping"})
        except Exception:
            break
