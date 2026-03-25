"""
Pytest suite: LOCAL_MODE=true, Mock Bedrock, no AWS credentials required.
"""

from __future__ import annotations

import os
import sys

# Must be set before imports that read environment / load clients
os.environ["LOCAL_MODE"] = "true"

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from utils.bedrock_client import BedrockMockClient, parse_json_safely
from utils.guardrails import Guardrails
from utils.knowledge_graph import LocalKnowledgeGraph
from utils.sqs_bus import LocalSQSBus
from utils.state_store import LocalStateStore

from layers.input_layer import InputLayer
from layers.planner_agent import PlannerAgent
from layers.workers.architect_agent import ArchitectAgent
from layers.workers.coder_agent import CoderAgent


def test_bedrock_mock_all_agents() -> None:
    client = BedrockMockClient()

    raw_in = client.invoke(
        "us.amazon.nova-lite-v1:0",
        "test",
        "You are an expert requirements analyst for a software agent factory.",
    )
    j = parse_json_safely(raw_in, {})
    assert "intent" in j and "constraints" in j and "domain" in j

    raw_pl = client.invoke(
        "us.amazon.nova-lite-v1:0",
        "plan",
        "You are the planner orchestrator of an AI agent factory.",
    )
    jp = parse_json_safely(raw_pl, {})
    assert "tasks" in jp and isinstance(jp["tasks"], list)

    raw_ar = client.invoke(
        "us.amazon.nova-lite-v1:0",
        "arch",
        "You are a senior software architect working inside an AI agent factory.",
    )
    ja = parse_json_safely(raw_ar, {})
    assert "components" in ja and "data_flow" in ja

    raw_cd = client.invoke(
        "us.amazon.nova-lite-v1:0",
        "code",
        "You are an expert Python developer working inside an AI agent factory.",
    )
    jc = parse_json_safely(raw_cd, {})
    assert "filename" in jc and "code" in jc and "explanation" in jc


def test_sqs_bus_message_flow() -> None:
    bus = LocalSQSBus()
    msg = {
        "message_type": "task",
        "source": "planner",
        "destination": "architect",
        "payload": {"task": "test"},
    }
    bus.send_message("test-queue", msg)
    received = bus.receive_message("test-queue")
    assert received is not None
    assert received["source"] == "planner"


def test_state_store_put_get() -> None:
    store = LocalStateStore()
    store.put("test-run-001", "status", "testing")
    result = store.get("test-run-001", "status")
    assert result == "testing"


def test_knowledge_graph_store_and_retrieve() -> None:
    kg = LocalKnowledgeGraph()
    kg.store_pattern(
        "r1",
        "Build REST API",
        "web development",
        {"components": [{"name": "Router"}], "entry_point": "app.py"},
    )
    results = kg.retrieve_similar("Build REST API", "web development")
    assert len(results) >= 1


def test_guardrails_all_gates() -> None:
    g = Guardrails()
    good_arch = {
        "components": [
            {
                "name": "App",
                "responsibility": "main logic",
                "interfaces": ["run()"],
            },
        ],
        "data_flow": "input goes in and output comes out of the system",
        "entry_point": "main.py",
        "file_structure": [],
        "dependencies": [],
        "architecture_notes": "clean",
    }
    good_code = {
        "filename": "main.py",
        "code": "import os\n\ndef main():\n    print('hello world from generated code')\n\n\nmain()\n",
    }
    ok, errs = g.validate_design(good_arch)
    assert ok, f"Design validation failed: {errs}"
    ok, errs = g.validate_code(good_code)
    assert ok, f"Code validation failed: {errs}"


def test_full_pipeline_local_mode() -> None:
    os.environ["LOCAL_MODE"] = "true"
    bedrock = BedrockMockClient()
    bus = LocalSQSBus()
    state = LocalStateStore()
    run_id = "test-001"

    parsed = InputLayer(bedrock, state, bus).parse("Build FastAPI CRUD API", run_id)
    assert "intent" in parsed

    plan = PlannerAgent(bedrock, state, bus).plan(parsed, run_id)
    assert "tasks" in plan and len(plan["tasks"]) > 0

    arch_out: dict = {}
    code_out: dict = {}
    for task in plan["tasks"]:
        ctx = {**plan, "context": task.get("context", "")}
        if task["agent"] == "architect":
            arch_out = ArchitectAgent(bedrock, state, bus).execute(
                task["task"],
                ctx,
                run_id,
            )
        elif task["agent"] == "coder":
            ctx["architect_output"] = arch_out
            code_out = CoderAgent(bedrock, state, bus).execute(
                task["task"],
                ctx,
                run_id,
            )

    assert "components" in arch_out
    assert "code" in code_out
    assert len(code_out["code"]) > 20

    gates = Guardrails().run_all_gates(arch_out, code_out, 5.0)
    assert "overall_passed" in gates

    print(f"\n[PASS] Full pipeline completed. File: {code_out['filename']}")
