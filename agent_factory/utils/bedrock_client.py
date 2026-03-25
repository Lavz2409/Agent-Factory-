"""
AWS Bedrock LLM client.
Real mode: boto3 bedrock-runtime InvokeModel API (temperature 0.2).
Local mode: BedrockMockClient returns valid JSON varied by request keywords.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
from typing import Any

try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass

logger = logging.getLogger(__name__)


def _extract_nova_output_text(result: dict[str, Any]) -> str:
    """Parse Amazon Nova InvokeModel (non-stream) JSON response body."""
    out = result.get("output")
    if isinstance(out, dict):
        msg = out.get("message")
        if isinstance(msg, dict):
            parts: list[str] = []
            for block in msg.get("content") or []:
                if isinstance(block, dict) and "text" in block:
                    parts.append(str(block["text"]))
            if parts:
                return "".join(parts).strip()
    # Some responses expose completion at top level
    alt = result.get("message")
    if isinstance(alt, dict):
        parts: list[str] = []
        for block in alt.get("content") or []:
            if isinstance(block, dict) and "text" in block:
                parts.append(str(block["text"]))
        if parts:
            return "".join(parts).strip()
    return ""


# Text generation default — Amazon Nova Lite (Invoke messages-v1 schema; enable in Bedrock console)
# Model IDs are region-prefixed, e.g. us.amazon.nova-lite-v1:0, eu.amazon.nova-lite-v1:0 — see model-ids.html
# Alternatives: anthropic.claude-3-haiku-20240307-v1:0, anthropic.claude-3-5-sonnet-20240620-v1:0
DEFAULT_BEDROCK_TEXT_MODEL = "us.amazon.nova-lite-v1:0"


class BedrockMockClient:
    """
    Valid JSON only; content varies with user prompt keywords (FastAPI vs CLI vs default).
    """

    def invoke(self, model_id: str, prompt: str, system_prompt: str | None = None) -> str:
        sp = (system_prompt or "").lower()
        p = (prompt or "").lower()
        combined = f"{p} {sp}"
        try:
            if (
                "requirements analyst" in sp
                or "input layer" in sp
                or "[agent_input]" in sp
            ):
                return self._mock_input(p, prompt)

            if "[agent_planner]" in sp or (
                "planner" in sp and "orchestrat" in sp
            ):
                return self._mock_planner(p, prompt)

            if "[agent_architect]" in sp or (
                "senior software architect" in sp
                or ("architect" in sp and "python developer" not in sp)
            ):
                return self._mock_architect(p, prompt)

            if "[agent_coder]" in sp or "python developer" in sp or "expert python developer" in sp:
                return self._mock_coder(p, prompt)

            return json.dumps({"error": "unknown_mock_route", "hint": sp[:200]}, ensure_ascii=False)
        except Exception as e:
            logger.warning("BedrockMockClient.invoke failed: %s", e)
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    def _seed(self, text: str) -> int:
        return int(hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()[:8], 16)

    def _mock_input(self, p_lower: str, prompt: str) -> str:
        intent = "Address the user's software request"
        if "fastapi" in p_lower:
            intent = "Build a REST API using FastAPI"
        elif "cli" in p_lower or "command line" in p_lower:
            intent = "Build a command-line application"
        domain = "web development" if "api" in p_lower or "fastapi" in p_lower else (
            "cli tooling" if "cli" in p_lower else "software engineering"
        )
        return json.dumps(
            {
                "intent": intent,
                "constraints": ["valid JSON only", "runnable Python"],
                "domain": domain,
                "expected_output": "working Python project",
                "complexity": "medium",
                "success_criteria": ["runs without errors"],
                "suggested_agents": ["architect", "coder"],
            },
            ensure_ascii=False,
        )

    def _mock_planner(self, p_lower: str, prompt: str) -> str:
        if "fastapi" in p_lower or "rest" in p_lower:
            strategy = "Design a FastAPI service with routers and Pydantic models, then implement endpoints."
            tasks = [
                {
                    "agent": "architect",
                    "task": "Design FastAPI app structure: routers, models, dependency injection, in-memory store",
                    "context": "Use FastAPI and Pydantic; stateless HTTP API",
                },
                {
                    "agent": "coder",
                    "task": "Implement the FastAPI application with CRUD routes and example usage",
                    "context": "fastapi, uvicorn, pydantic",
                },
            ]
        elif "cli" in p_lower or "argparse" in p_lower:
            strategy = "Design a small CLI with argparse (or typer), then implement commands."
            tasks = [
                {
                    "agent": "architect",
                    "task": "Design CLI commands, argument parsing flow, and module layout",
                    "context": "stdin/stdout only; no web server",
                },
                {
                    "agent": "coder",
                    "task": "Implement runnable CLI with subcommands and help text",
                    "context": "argparse",
                },
            ]
        else:
            s = self._seed(prompt)
            strategy = f"Decompose the request into design then implementation (variant {s % 10000})."
            tasks = [
                {
                    "agent": "architect",
                    "task": f"Design components and data flow for: {prompt[:200]}",
                    "context": "Keep modules small and testable",
                },
                {
                    "agent": "coder",
                    "task": f"Implement Python code that satisfies: {prompt[:200]}",
                    "context": "stdlib first; add pip deps only if needed",
                },
            ]
        return json.dumps(
            {
                "project_name": "generated_project",
                "strategy": strategy,
                "rag_patterns_used": 0,
                "tasks": tasks,
            },
            ensure_ascii=False,
        )

    def _mock_architect(self, p_lower: str, prompt: str) -> str:
        if "fastapi" in p_lower:
            components = [
                {
                    "name": "FastAPIApp",
                    "responsibility": "Application factory and route registration",
                    "interfaces": ["create_app()"],
                },
                {
                    "name": "ApiRouter",
                    "responsibility": "HTTP endpoints and request validation",
                    "interfaces": ["get_items()", "post_item()"],
                },
                {
                    "name": "Models",
                    "responsibility": "Pydantic schemas for request/response bodies",
                    "interfaces": ["Item", "ItemCreate"],
                },
            ]
            data_flow = (
                "1. HTTP request → FastAPI routing → 2. Pydantic validation → "
                "3. handler logic → 4. JSON response"
            )
            deps = ["fastapi", "uvicorn", "pydantic"]
        elif "cli" in p_lower:
            components = [
                {
                    "name": "CLIEntry",
                    "responsibility": "Parse argv and dispatch subcommands",
                    "interfaces": ["main()"],
                },
                {
                    "name": "Commands",
                    "responsibility": "Implement each CLI command",
                    "interfaces": ["run_echo()", "run_greet()"],
                },
            ]
            data_flow = "1. argv → argparse → 2. command handler → 3. stdout result"
            deps = []
        else:
            components = [
                {
                    "name": "AppCore",
                    "responsibility": "Core business logic",
                    "interfaces": ["run()"],
                },
                {
                    "name": "IO",
                    "responsibility": "Input/output adapters",
                    "interfaces": ["read()", "write()"],
                },
            ]
            data_flow = "Input → AppCore → Output"
            deps = []
        return json.dumps(
            {
                "components": components,
                "data_flow": data_flow,
                "file_structure": ["main.py"],
                "dependencies": deps,
                "architecture_notes": "Mock architecture aligned to request keywords.",
                "entry_point": "main.py",
            },
            ensure_ascii=False,
        )

    def _mock_coder(self, p_lower: str, prompt: str) -> str:
        if "fastapi" in p_lower:
            code = '''from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Generated API")

class Item(BaseModel):
    name: str
    value: int = 0

store: dict[int, Item] = {}
_next = 1

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/items/{item_id}")
def get_item(item_id: int):
    return store.get(item_id, {"detail": "not found"})

@app.post("/items")
def create_item(item: Item):
    global _next
    iid = _next
    _next += 1
    store[iid] = item
    return {"id": iid, "item": item.model_dump()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
            deps = ["fastapi", "uvicorn", "pydantic"]
            how = "uvicorn main:app --reload"
        elif "cli" in p_lower:
            code = '''import argparse

def cmd_echo(args: argparse.Namespace) -> None:
    print(" ".join(args.words))

def cmd_greet(args: argparse.Namespace) -> None:
    print(f"Hello, {args.name}!")

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="cli_app")
    sub = p.add_subparsers(dest="command", required=True)
    pe = sub.add_parser("echo")
    pe.add_argument("words", nargs="*", help="words to print")
    pe.set_defaults(func=cmd_echo)
    pg = sub.add_parser("greet")
    pg.add_argument("--name", default="world")
    pg.set_defaults(func=cmd_greet)
    return p

def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
'''
            deps = []
            how = "python main.py greet --name Ada"
        else:
            sid = self._seed(prompt)
            code = f'''def run_{sid % 10000}() -> str:
    """Generated module logic (mock) — unique per request hash."""
    return "ok-{sid}"

def main() -> None:
    print(run_{sid % 10000}())

if __name__ == "__main__":
    main()
'''
            deps = []
            how = "python main.py"
        return json.dumps(
            {
                "filename": "main.py",
                "code": code,
                "explanation": "Executable mock code keyed to request keywords.",
                "how_to_run": how,
                "dependencies_to_install": deps,
            },
            ensure_ascii=False,
        )


class BedrockRealClient:
    """Production client using boto3 bedrock-runtime."""

    def __init__(self) -> None:
        import boto3

        from utils.aws_config import get_aws_region

        region = get_aws_region()
        print(f"[Bedrock] Using region={region!r} (bedrock-runtime)")
        self.client = boto3.client("bedrock-runtime", region_name=region)
        self.reasoning_model = os.environ.get(
            "BEDROCK_REASONING_MODEL",
            DEFAULT_BEDROCK_TEXT_MODEL,
        )
        self.cost_model = os.environ.get(
            "BEDROCK_COST_MODEL",
            "meta.llama2-13b-chat-v1",
        )

    def invoke(self, model_id: str, prompt: str, system_prompt: str | None = None) -> str:
        """Invoke Bedrock model; raise RuntimeError on failure."""
        from botocore.exceptions import ClientError

        from utils.aws_config import get_aws_region

        temp = float(os.environ.get("BEDROCK_TEMPERATURE", "0.2"))
        try:
            if model_id.startswith("anthropic.claude"):
                body: dict[str, Any] = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 4096,
                    "temperature": temp,
                    "messages": [
                        {
                            "role": "user",
                            "content": [{"type": "text", "text": prompt}],
                        }
                    ],
                }
                if system_prompt:
                    body["system"] = system_prompt
                response = self.client.invoke_model(
                    modelId=model_id,
                    body=json.dumps(body),
                    contentType="application/json",
                    accept="application/json",
                )
                raw = response["body"].read()
                result = json.loads(raw)
                return str(result["content"][0]["text"]).strip()

            if model_id.startswith("amazon.titan-embed"):
                raise RuntimeError(
                    f"Invalid model for text generation: {model_id!r} is an embedding model. "
                    f"Set BEDROCK_REASONING_MODEL to a text model "
                    f"(e.g. {DEFAULT_BEDROCK_TEXT_MODEL!r})."
                )

            if "amazon.nova-" in model_id:
                message_list: list[dict[str, Any]] = [
                    {"role": "user", "content": [{"text": prompt.strip()}]}
                ]
                request_body: dict[str, Any] = {
                    "schemaVersion": "messages-v1",
                    "messages": message_list,
                    "inferenceConfig": {
                        "maxTokens": 4096,
                        "temperature": temp,
                    },
                }
                if system_prompt:
                    request_body["system"] = [{"text": system_prompt.strip()}]
                response = self.client.invoke_model(
                    modelId=model_id,
                    body=json.dumps(request_body),
                    contentType="application/json",
                    accept="application/json",
                )
                result = json.loads(response["body"].read())
                text = _extract_nova_output_text(result)
                if not text:
                    raise RuntimeError(
                        f"Nova model returned empty text; keys={list(result.keys())!r}"
                    )
                return text

            if model_id.startswith("amazon.titan"):
                # Titan Text has no separate system channel — prepend instructions.
                if system_prompt:
                    input_text = f"{system_prompt.strip()}\n\n{prompt.strip()}"
                else:
                    input_text = prompt
                body = {
                    "inputText": input_text,
                    "textGenerationConfig": {
                        "maxTokenCount": 4096,
                        "temperature": temp,
                    },
                }
                response = self.client.invoke_model(
                    modelId=model_id,
                    body=json.dumps(body),
                    contentType="application/json",
                    accept="application/json",
                )
                result = json.loads(response["body"].read())
                return str(result["results"][0]["outputText"]).strip()

            if model_id.startswith("meta.llama"):
                body = {
                    "prompt": prompt,
                    "max_gen_len": 2048,
                    "temperature": temp,
                }
                response = self.client.invoke_model(
                    modelId=model_id,
                    body=json.dumps(body),
                    contentType="application/json",
                    accept="application/json",
                )
                result = json.loads(response["body"].read())
                return str(result.get("generation", "")).strip()

            raise RuntimeError(f"Unsupported model_id for BedrockRealClient: {model_id}")
        except ClientError as e:
            err = e.response.get("Error", {})
            code = err.get("Code", "")
            msg = err.get("Message", str(e))
            region = get_aws_region()
            if "end of its life" in msg.lower() or "deprecated" in msg.lower():
                raise RuntimeError(
                    f"Bedrock model is end-of-life or deprecated: modelId={model_id!r} "
                    f"region={region!r}. Set BEDROCK_REASONING_MODEL to a current model such as "
                    f"{DEFAULT_BEDROCK_TEXT_MODEL!r}, anthropic.claude-3-haiku-20240307-v1:0, "
                    f"or anthropic.claude-3-5-sonnet-20240620-v1:0 (see model-ids for your region). "
                    f"Original error: {msg}"
                ) from e
            if code == "ValidationException":
                raise RuntimeError(
                    f"Bedrock model ID not valid in this account/region: modelId={model_id!r} "
                    f"region={region!r}. "
                    f"Enable the model in Bedrock console (Model access) and use an ID from "
                    f"https://docs.aws.amazon.com/bedrock/latest/userguide/model-ids.html — "
                    f"try {DEFAULT_BEDROCK_TEXT_MODEL!r} (or your region’s Nova prefix, e.g. "
                    f"eu.amazon.nova-lite-v1:0), anthropic.claude-3-haiku-20240307-v1:0, "
                    f"anthropic.claude-3-5-sonnet-20240620-v1:0, or meta.llama3-8b-instruct-v1:0. "
                    f"Original error: {msg}"
                ) from e
            raise RuntimeError(f"Bedrock invoke failed: {msg}") from e
        except Exception as e:
            raise RuntimeError(f"Bedrock invoke failed: {e}") from e


def get_bedrock_client() -> BedrockMockClient | BedrockRealClient:
    """Return mock or real Bedrock client based on LOCAL_MODE."""
    local = os.environ.get("LOCAL_MODE", "true").lower() == "true"
    if local:
        print("[Bedrock] LocalMode — MockClient active")
        return BedrockMockClient()
    model = os.environ.get(
        "BEDROCK_REASONING_MODEL",
        DEFAULT_BEDROCK_TEXT_MODEL,
    )
    print(f"[Bedrock] AWS Bedrock active: {model}")
    return BedrockRealClient()


# JSON helpers live in llm_json; re-export for imports from utils.bedrock_client
from utils.llm_json import (  # noqa: E402
    invoke_json_with_retry,
    log_fallback,
    parse_json_from_llm,
    parse_json_safely,
)
