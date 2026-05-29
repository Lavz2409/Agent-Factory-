"""
WebSocket terminal endpoint — /ws/terminal

Accepts shell commands from the frontend, executes them via asyncio subprocess,
and streams stdout / stderr / exit-code back over the WebSocket connection.
No sandboxing. All commands are executed as-is.
"""
from __future__ import annotations

import asyncio
import json
import os

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()


@router.websocket("/ws/terminal")
async def terminal_ws(websocket: WebSocket) -> None:
    await websocket.accept()

    # Per-session working directory — starts at project root
    cwd: str = os.getcwd()

    async def _send(stream: str, data: str) -> None:
        try:
            await websocket.send_text(json.dumps({"stream": stream, "data": data}))
        except Exception:
            pass

    try:
        while True:
            raw = await websocket.receive_text()
            command = raw.strip()
            if not command:
                continue

            # Handle `cd` locally — subprocess cd doesn't persist across calls
            if command.startswith("cd "):
                target = command[3:].strip().strip('"').strip("'")
                new_dir = os.path.join(cwd, target) if not os.path.isabs(target) else target
                new_dir = os.path.normpath(new_dir)
                if os.path.isdir(new_dir):
                    cwd = new_dir
                    await _send("stdout", f"Changed directory to: {cwd}\n")
                else:
                    await _send("stderr", f"cd: no such directory: {new_dir}\n")
                await _send("exit", "0")
                continue

            try:
                proc = await asyncio.create_subprocess_shell(
                    command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=cwd,
                )
                stdout_bytes, stderr_bytes = await proc.communicate()

                if stdout_bytes:
                    await _send("stdout", stdout_bytes.decode("utf-8", errors="replace"))
                if stderr_bytes:
                    await _send("stderr", stderr_bytes.decode("utf-8", errors="replace"))
                await _send("exit", str(proc.returncode))

            except Exception as exc:
                await _send("stderr", f"Error executing command: {exc}\n")
                await _send("exit", "1")

    except WebSocketDisconnect:
        pass
