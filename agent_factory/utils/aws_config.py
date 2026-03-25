"""
Shared AWS region resolution for boto3 clients.
Prefer AWS_REGION (as in .env), then AWS_DEFAULT_REGION, then us-east-1.
"""

from __future__ import annotations

import os

try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass


def get_aws_region() -> str:
    """Region used by Bedrock, DynamoDB, SQS, and other AWS clients."""
    r = (os.environ.get("AWS_REGION") or "").strip()
    if r:
        return r
    r = (os.environ.get("AWS_DEFAULT_REGION") or "").strip()
    if r:
        return r
    return "us-east-1"


def get_dynamodb_table_name() -> str:
    """Table name: DYNAMODB_TABLE, or legacy DYNAMODB_STATE_TABLE, or default."""
    t = (os.environ.get("DYNAMODB_TABLE") or "").strip()
    if t:
        return t
    t = (os.environ.get("DYNAMODB_STATE_TABLE") or "").strip()
    if t:
        return t
    return "agent-factory-state"
