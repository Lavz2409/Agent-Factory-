from __future__ import annotations

import time
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Any, Deque


@dataclass
class BusMessage:
    queue: str
    message_type: str
    source: str
    destination: str
    timestamp: float
    run_id: str
    payload: Any


class MessageBus:
    """
    Simple in-memory message bus.
    Phase 1 is synchronous (agents called in-process), but keeping this module makes
    it easy to evolve toward async/multi-process later.
    """

    def __init__(self) -> None:
        self._queues: dict[str, Deque[BusMessage]] = defaultdict(deque)

    def send_message(self, queue_name: str, message: dict[str, Any]) -> str:
        run_id = str(message.get("run_id", ""))
        msg = BusMessage(
            queue=queue_name,
            message_type=str(message.get("message_type", "")),
            source=str(message.get("source", "")),
            destination=str(message.get("destination", "")),
            timestamp=time.time(),
            run_id=run_id,
            payload=message.get("payload"),
        )
        self._queues[queue_name].append(msg)
        return run_id

    def receive_message(self, queue_name: str, timeout: float = 1.0) -> dict[str, Any] | None:
        # In-memory queues are immediate; we keep timeout for API compatibility.
        if not self._queues[queue_name]:
            return None
        msg = self._queues[queue_name].popleft()
        return {
            "queue": msg.queue,
            "message_type": msg.message_type,
            "source": msg.source,
            "destination": msg.destination,
            "timestamp": msg.timestamp,
            "run_id": msg.run_id,
            "payload": msg.payload,
        }

    def purge(self, queue_name: str) -> None:
        self._queues[queue_name].clear()

