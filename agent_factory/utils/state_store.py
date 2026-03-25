"""
Layer 8 — State management.
Real mode: DynamoDB. Local mode: local_state.json file.
Stores pipeline run state so Step Functions can manage execution.
"""

from __future__ import annotations

import datetime
import json
import os
from pathlib import Path
from typing import Any

try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass

from utils.aws_config import get_aws_region, get_dynamodb_table_name


class LocalStateStore:
    """DynamoDB simulation using a JSON file on disk."""

    def __init__(self) -> None:
        self.filepath = Path("local_state.json")

    def _load(self) -> dict[str, Any]:
        if not self.filepath.exists():
            return {}
        try:
            return json.loads(self.filepath.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _save(self, data: dict[str, Any]) -> None:
        self.filepath.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def put(self, run_id: str, key: str, value: Any) -> None:
        data = self._load()
        if run_id not in data:
            data[run_id] = {}
        data[run_id][key] = value
        data[run_id]["updated_at"] = datetime.datetime.now().isoformat()
        self._save(data)

    def get(self, run_id: str, key: str | None = None) -> Any:
        data = self._load()
        if run_id not in data:
            return {} if key is None else None
        if key is None:
            return data[run_id]
        return data[run_id].get(key)

    def list_runs(self) -> list[str]:
        data = self._load()
        return list(data.keys())


class DynamoDBStateStore:
    """Production DynamoDB table for run state."""

    def __init__(self) -> None:
        import boto3
        from botocore.exceptions import ClientError

        region = get_aws_region()
        table_name = get_dynamodb_table_name()

        print(f"[DynamoDB] Using region={region!r} table={table_name!r}")

        ddb_client = boto3.client("dynamodb", region_name=region)
        try:
            ddb_client.describe_table(TableName=table_name)
        except ClientError as e:
            code = e.response.get("Error", {}).get("Code", "")
            if code == "ResourceNotFoundException":
                raise RuntimeError(
                    f"DynamoDB table not found. Please create table '{table_name}' "
                    f"in region {region}"
                ) from None
            raise

        self.region = region
        self.table_name = table_name
        self._resource = boto3.resource("dynamodb", region_name=region)
        self.table = self._resource.Table(table_name)

    @staticmethod
    def _encode_value(value: Any) -> Any:
        """Store dict/list as JSON strings for DynamoDB attribute compatibility."""
        if isinstance(value, (dict, list)):
            return json.dumps(value)
        return value

    @staticmethod
    def _decode_value(value: Any) -> Any:
        if isinstance(value, str) and (value.startswith("{") or value.startswith("[")):
            try:
                return json.loads(value)
            except Exception:
                return value
        return value

    def put(self, run_id: str, key: str, value: Any) -> None:
        ts = datetime.datetime.now().isoformat()
        enc = self._encode_value(value)
        self.table.update_item(
            Key={"run_id": run_id},
            UpdateExpression="SET #k = :v, updated_at = :t",
            ExpressionAttributeNames={"#k": key},
            ExpressionAttributeValues={":v": enc, ":t": ts},
        )

    def get(self, run_id: str, key: str | None = None) -> Any:
        response = self.table.get_item(Key={"run_id": run_id})
        item = response.get("Item", {})
        if key is None:
            return {k: self._decode_value(v) for k, v in item.items()}
        return self._decode_value(item.get(key))

    def list_runs(self) -> list[str]:
        scan = self.table.scan(ProjectionExpression="run_id")
        items = scan.get("Items", [])
        return [str(i["run_id"]) for i in items if "run_id" in i]


def get_state_store() -> LocalStateStore | DynamoDBStateStore:
    """Return local or DynamoDB state store based on LOCAL_MODE."""
    local = os.environ.get("LOCAL_MODE", "true").lower() == "true"
    if local:
        return LocalStateStore()
    return DynamoDBStateStore()
