"""
Layer 4 — Communication Bus.
All agent messages flow through SQS. Agents never call each other directly.
Real mode: boto3 SQS. Local mode: Python queue.Queue.
This gives full observability, replay capability, and fault isolation.
"""

from __future__ import annotations

import json
import os
import queue
import uuid
from datetime import datetime, timezone
from typing import Any

try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _wrap_standard_message(message: dict[str, Any]) -> dict[str, Any]:
    """Ensure standard schema fields exist."""
    out = dict(message)
    if "message_id" not in out:
        out["message_id"] = str(uuid.uuid4())
    if "timestamp" not in out:
        out["timestamp"] = _iso_now()
    if "payload" not in out:
        out["payload"] = {}
    return out


class LocalSQSBus:
    """In-process queues simulating SQS channels."""

    def __init__(self) -> None:
        self.queues: dict[str, queue.Queue[dict[str, Any]]] = {}

    def _get_queue(self, name: str) -> queue.Queue[dict[str, Any]]:
        if name not in self.queues:
            self.queues[name] = queue.Queue()
        return self.queues[name]

    def send_message(self, queue_name: str, message: dict[str, Any]) -> str:
        msg = _wrap_standard_message(message)
        q = self._get_queue(queue_name)
        q.put(msg)
        mid = str(msg.get("message_id", ""))
        print(
            f"  [SQS-LOCAL] → {queue_name}: {msg.get('message_type', 'msg')}",
        )
        return mid

    def receive_message(self, queue_name: str, timeout: float = 1.0) -> dict[str, Any] | None:
        q = self._get_queue(queue_name)
        try:
            return q.get(timeout=timeout)
        except queue.Empty:
            return None

    def purge(self, queue_name: str) -> None:
        q = self._get_queue(queue_name)
        try:
            while True:
                q.get_nowait()
        except queue.Empty:
            pass


class RealSQSBus:
    """Production SQS client using logical queue names mapped to env URLs."""

    def __init__(self) -> None:
        import boto3

        from utils.aws_config import get_aws_region

        region = get_aws_region()
        print(f"[SQS] Using region={region!r}")
        self.client = boto3.client("sqs", region_name=region)
        self._urls = {
            "planner-queue": os.environ.get("SQS_PLANNER_QUEUE_URL", ""),
            "worker-queue": os.environ.get("SQS_WORKER_QUEUE_URL", ""),
            "output-queue": os.environ.get("SQS_OUTPUT_QUEUE_URL", ""),
            "dlq": os.environ.get("SQS_DLQ_URL", ""),
        }

    def _url(self, queue_name: str) -> str:
        """Resolve logical name to queue URL (also accepts raw https URL)."""
        if queue_name.startswith("https://"):
            return queue_name
        return self._urls.get(queue_name, "")

    def send_message(self, queue_name: str, message: dict[str, Any]) -> str:
        url = self._url(queue_name)
        if not url:
            raise RuntimeError(f"No SQS queue URL for {queue_name}")
        msg = _wrap_standard_message(message)
        resp = self.client.send_message(
            QueueUrl=url,
            MessageBody=json.dumps(msg),
        )
        return str(resp.get("MessageId", msg.get("message_id", "")))

    def receive_message(self, queue_name: str, timeout: float = 1.0) -> dict[str, Any] | None:
        del timeout  # unused for real long poll in this thin wrapper
        url = self._url(queue_name)
        if not url:
            return None
        resp = self.client.receive_message(
            QueueUrl=url,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=1,
        )
        msgs = resp.get("Messages", [])
        if not msgs:
            return None
        m = msgs[0]
        body = json.loads(m["Body"])
        self.client.delete_message(
            QueueUrl=url,
            ReceiptHandle=m["ReceiptHandle"],
        )
        return body

    def purge(self, queue_name: str) -> None:
        url = self._url(queue_name)
        if url:
            self.client.purge_queue(QueueUrl=url)


def get_sqs_bus() -> LocalSQSBus | RealSQSBus:
    """Return local or real SQS bus based on LOCAL_MODE."""
    local = os.environ.get("LOCAL_MODE", "true").lower() == "true"
    if local:
        return LocalSQSBus()
    return RealSQSBus()
