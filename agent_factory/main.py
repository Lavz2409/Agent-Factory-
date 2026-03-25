"""
Agent Factory — Main Pipeline Runner
Implements: Layer 1 (Input) → Layer 2 (Planner) → Layer 3 (Workers)
            → Layer 7 (Quality Gates) → Layer 8 (Observability)
Communication: SQS message bus (async-first architecture)
State: DynamoDB / local JSON
Learning: Knowledge Graph updated after every run
"""

from __future__ import annotations

import datetime
import json
import logging
import os
import sys
import time
import uuid
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from layers.input_layer import InputLayer
from layers.planner_agent import PlannerAgent
from layers.workers.architect_agent import ArchitectAgent
from layers.workers.coder_agent import CoderAgent
from utils.bedrock_client import get_bedrock_client
from utils.guardrails import Guardrails
from utils.knowledge_graph import get_knowledge_graph
from utils.sqs_bus import _wrap_standard_message, get_sqs_bus
from utils.state_store import get_state_store


def _setup_logging() -> None:
    root = logging.getLogger()
    if not root.handlers:
        logging.basicConfig(
            level=logging.INFO,
            format="%(levelname)s %(name)s: %(message)s",
        )


def _configure_stdio_utf8() -> None:
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def print_banner(title: str, width: int = 65) -> None:
    print("\n" + "═" * width)
    print(f"  {title}")
    print("═" * width)


def print_layer_header(layer_num: str, name: str, subtitle: str = "") -> None:
    print(f"\n{'─' * 65}")
    print(f"  {layer_num}  ▸  {name}")
    if subtitle:
        print(f"  {subtitle}")
    print(f"{'─' * 65}")


def print_json_output(label: str, data: dict) -> None:
    print(f"\n  [{label}]")
    lines = json.dumps(data, indent=2, ensure_ascii=False).split("\n")
    for line in lines:
        print(f"  {line}")


def print_code_block(code: str, filename: str) -> None:
    pad = max(0, 55 - len(filename))
    print(f"\n  ┌─── {filename} {'─' * pad}")
    for line in code.split("\n"):
        print(f"  │  {line}")
    print(f"  └{'─' * 60}")


def save_generated_code(coder_output: dict, *, quiet: bool = False) -> str:
    Path("outputs").mkdir(exist_ok=True)
    filename = coder_output.get("filename", "output.py")
    filepath = Path("outputs") / filename
    filepath.write_text(coder_output.get("code", ""), encoding="utf-8")
    if not quiet:
        print(f"\n  ✓ Code saved → outputs/{filename}")
    return str(filepath)


def append_run_history(run_data: dict) -> None:
    history_file = Path("run_history.json")
    history: list = []
    if history_file.exists():
        try:
            history = json.loads(history_file.read_text(encoding="utf-8"))
            if not isinstance(history, list):
                history = []
        except Exception:
            history = []
    history.append(run_data)
    history_file.write_text(json.dumps(history, indent=2), encoding="utf-8")


def print_sqs_bus_activity(bus: object) -> None:
    """Show messages that flowed through the SQS bus this run."""
    print(f"\n  [SQS Bus Activity — Layer 4]")
    queues_to_check = ["planner-queue", "worker-queue", "output-queue"]
    for q in queues_to_check:
        msg = bus.receive_message(q)
        if msg:
            src = msg.get("source", "?")
            dst = msg.get("destination", "?")
            mtype = msg.get("message_type", "?")
            print(f"    • {src} → {dst} [{mtype}]")


class CapturingSQSBus:
    """Records each SQS send for optional UI visualization (delegates to inner bus)."""

    def __init__(self, inner: Any) -> None:
        self._inner = inner
        self.messages: list[dict[str, Any]] = []

    def send_message(self, queue_name: str, message: dict[str, Any]) -> str:
        wrapped = _wrap_standard_message(message)
        payload = wrapped.get("payload")
        summary: Any = payload
        if isinstance(payload, dict) and len(str(payload)) > 200:
            summary = {k: payload.get(k) for k in list(payload.keys())[:5]}
        self.messages.append(
            {
                "queue": queue_name,
                "source": wrapped.get("source", ""),
                "destination": wrapped.get("destination", ""),
                "message_type": wrapped.get("message_type", ""),
                "timestamp": wrapped.get("timestamp", ""),
                "run_id": wrapped.get("run_id", ""),
                "payload_summary": summary,
            },
        )
        return self._inner.send_message(queue_name, message)

    def receive_message(self, queue_name: str, timeout: float = 1.0) -> dict[str, Any] | None:
        return self._inner.receive_message(queue_name, timeout)

    def purge(self, queue_name: str) -> None:
        if hasattr(self._inner, "purge"):
            self._inner.purge(queue_name)


def run_pipeline_core(
    user_input: str,
    run_id: str,
    start_time: float,
    bedrock: Any,
    bus: Any,
    state: Any,
    kg: Any,
    guardrails: Guardrails,
    *,
    verbose: bool = True,
) -> dict[str, Any]:
    """Execute pipeline; optional console output for CLI."""
    state.put(run_id, "status", "started")
    state.put(run_id, "user_request", user_input)

    input_layer = InputLayer(bedrock, state, bus)
    planner = PlannerAgent(bedrock, state, bus)
    architect = ArchitectAgent(bedrock, state, bus)
    coder = CoderAgent(bedrock, state, bus)

    architect_output: dict = {}
    coder_output: dict = {}
    plan: dict = {}
    parsed_input: dict = {}

    if verbose:
        print_layer_header(
            "LAYER 1",
            "INPUT LAYER",
            "S3 document store · JSON schema validation · Semantic parsing",
        )
        print("  Extracting intent, constraints, domain, success criteria...")

    parsed_input = input_layer.parse(user_input, run_id)
    if verbose:
        print_json_output("Structured Input", parsed_input)
        print(f"\n  ✓ Stored to storage/inputs/{run_id}_input.json")

    if verbose:
        print_layer_header(
            "LAYER 2",
            "PLANNER AGENT  [Crown Jewel / Orchestrator]",
            "Task decomposition · Agent topology · RAG pattern matching",
        )
        kg_stats = kg.get_stats()
        print(f"  Knowledge graph: {kg_stats['total_patterns']} patterns stored")
        print("  Running RAG retrieval for similar past architectures...")
        print("  Decomposing task into agent assignments...")

    plan = planner.plan(parsed_input, run_id)
    if verbose:
        print_json_output("Execution Plan", plan)
        print(f"\n  Strategy : {plan.get('strategy', '')}")
        print(f"  RAG hits : {plan.get('rag_patterns_used', 0)} past patterns used")
        print(f"  Tasks    : {len(plan.get('tasks', []))}")
        for i, t in enumerate(plan.get("tasks", []), 1):
            print(
                f"    {i}. [{t.get('agent', '?').upper()}] {str(t.get('task', ''))[:65]}",
            )

    for task_def in plan.get("tasks", []):
        agent_name = str(task_def.get("agent", "")).lower()
        task_text = str(task_def.get("task", ""))

        if agent_name == "architect":
            if verbose:
                print_layer_header(
                    "LAYER 3",
                    "ARCHITECT AGENT  [Worker]",
                    "Topology design · Data flow · Component interfaces",
                )
                print("  Designing system architecture...")

            arch_context = {**plan, "context": task_def.get("context", "")}
            architect_output = architect.execute(task_text, arch_context, run_id)
            if verbose:
                print_json_output("Architecture Design", architect_output)
                if architect_output.get("components"):
                    print(f"\n  Components ({len(architect_output['components'])}):")
                    for c in architect_output["components"]:
                        print(
                            f"    • {c.get('name', '?')}: {str(c.get('responsibility', ''))[:60]}",
                        )
                if architect_output.get("data_flow"):
                    print(
                        f"\n  Data flow: {str(architect_output['data_flow'])[:100]}",
                    )
                if architect_output.get("dependencies"):
                    print(
                        f"  Dependencies: {', '.join(str(d) for d in architect_output['dependencies'])}",
                    )

        elif agent_name == "coder":
            if verbose:
                print_layer_header(
                    "LAYER 3",
                    "CODER AGENT  [Worker]",
                    "Code generation · Executable Python · Versioned deliverable",
                )
                print("  Generating complete executable code...")

            coder_context = {
                **plan,
                "context": task_def.get("context", ""),
                "architect_output": architect_output,
            }
            coder_output = coder.execute(task_text, coder_context, run_id)

            if verbose:
                print(f"\n  Filename    : {coder_output.get('filename', '?')}")
                print(f"  Run command : {coder_output.get('how_to_run', '?')}")
                print(f"  Explanation : {coder_output.get('explanation', '?')}")
                if coder_output.get("dependencies_to_install"):
                    print(
                        f"  pip install : {' '.join(str(x) for x in coder_output['dependencies_to_install'])}",
                    )
                if coder_output.get("code"):
                    print_code_block(
                        coder_output["code"],
                        coder_output.get("filename", "output.py"),
                    )

    elapsed = time.time() - start_time

    if verbose:
        print_layer_header(
            "LAYER 7",
            "QUALITY GATES",
            "Design validation · Code validation · Security scan · SLA check",
        )

    gate_results = guardrails.run_all_gates(architect_output, coder_output, elapsed)
    overall = bool(gate_results.get("overall_passed", False))

    if verbose:
        gate_icons = {True: "✓", False: "✗"}
        print(
            f"\n  {gate_icons[gate_results['design_validation']['passed']]} "
            f"Design validation  : "
            f"{'PASS' if gate_results['design_validation']['passed'] else 'FAIL'}",
        )
        if gate_results["design_validation"].get("issues"):
            for issue in gate_results["design_validation"]["issues"]:
                print(f"      ↳ {issue}")

        print(
            f"  {gate_icons[gate_results['code_validation']['passed']]} "
            f"Code validation    : "
            f"{'PASS' if gate_results['code_validation']['passed'] else 'FAIL'}",
        )

        print(
            f"  {gate_icons[gate_results['security_scan']['passed']]} "
            f"Security scan      : "
            f"{'PASS' if gate_results['security_scan']['passed'] else 'WARN'}",
        )
        if gate_results["security_scan"].get("warnings"):
            for w in gate_results["security_scan"]["warnings"]:
                print(f"      ↳ {w}")

        print(
            f"  {gate_icons[gate_results['sla_enforcement']['passed']]} "
            f"SLA enforcement    : {gate_results['sla_enforcement']['message']}",
        )

        print(
            f"\n  Overall: {'✓ ALL GATES PASSED' if overall else '⚠ SOME GATES FAILED'}",
        )

        print_layer_header(
            "LAYER 4",
            "SQS COMMUNICATION BUS",
            "Async message passing · Full observability · Fault isolation",
        )
        print_sqs_bus_activity(bus)

        print_layer_header(
            "LAYER 8",
            "INFRASTRUCTURE + OBSERVABILITY",
            "S3 output · DynamoDB state · Knowledge graph update · Run log",
        )

    return {
        "run_id": run_id,
        "user_input": user_input,
        "parsed_input": parsed_input,
        "plan": plan,
        "architecture": architect_output,
        "code_output": coder_output,
        "guardrails": gate_results,
        "elapsed_seconds": round(elapsed, 2),
        "overall_passed": overall,
    }


def finalize_pipeline_run(
    core: dict[str, Any],
    kg: Any,
    state: Any,
    *,
    quiet: bool = False,
) -> None:
    run_id = str(core["run_id"])
    user_input = str(core["user_input"])
    parsed_input = core["parsed_input"]
    plan = core["plan"]
    architect_output = core["architecture"]
    coder_output = core["code_output"]
    gate_results = core["guardrails"]
    elapsed = float(core["elapsed_seconds"])
    overall = bool(core["overall_passed"])

    if coder_output.get("code"):
        save_generated_code(coder_output, quiet=quiet)

    if architect_output and parsed_input:
        kg.store_pattern(
            run_id=run_id,
            intent=str(parsed_input.get("intent", "")),
            domain=str(parsed_input.get("domain", "")),
            architecture=architect_output,
            outcome="success" if overall else "partial",
        )
        if not quiet:
            print(f"  ✓ Pattern stored to knowledge graph")
            new_stats = kg.get_stats()
            print(f"  ✓ Knowledge graph now has {new_stats['total_patterns']} patterns")

    state.put(run_id, "status", "complete")
    state.put(run_id, "quality_gates", gate_results)

    run_data = {
        "run_id": run_id,
        "timestamp": datetime.datetime.now().isoformat(),
        "elapsed_seconds": round(elapsed, 2),
        "user_request": user_input,
        "project_name": plan.get("project_name", "unknown"),
        "layers_completed": [
            "input",
            "planner",
            "architect",
            "coder",
            "quality_gates",
        ],
        "quality_gates_passed": overall,
        "output_file": coder_output.get("filename", "none"),
        "rag_patterns_used": plan.get("rag_patterns_used", 0),
    }
    append_run_history(run_data)

    if not quiet:
        print(f"  ✓ State saved to DynamoDB / local_state.json")
        print(f"  ✓ Run appended to run_history.json")


def run_pipeline_from_ui(user_input: str) -> dict[str, Any]:
    """
    Run the full pipeline without interactive CLI; return structured data for Streamlit/UI.
    """
    _setup_logging()
    load_dotenv()
    _configure_stdio_utf8()
    run_id = str(uuid.uuid4())[:8]
    start_time = time.time()

    bedrock = get_bedrock_client()
    capturing = CapturingSQSBus(get_sqs_bus())
    state = get_state_store()
    kg = get_knowledge_graph()
    guardrails = Guardrails()

    core = run_pipeline_core(
        user_input.strip() or "Build a FastAPI CRUD API",
        run_id,
        start_time,
        bedrock,
        capturing,
        state,
        kg,
        guardrails,
        verbose=False,
    )
    finalize_pipeline_run(core, kg, state, quiet=True)

    return {
        "parsed_input": core["parsed_input"],
        "plan": core["plan"],
        "architecture": core["architecture"],
        "code_output": core["code_output"],
        "guardrails": core["guardrails"],
        "run_id": core["run_id"],
        "elapsed_seconds": core["elapsed_seconds"],
        "overall_passed": core["overall_passed"],
        "user_input": core["user_input"],
    }


def run_pipeline() -> None:
    _setup_logging()
    _configure_stdio_utf8()
    load_dotenv()

    print_banner("🏭  AGENT FACTORY  —  AWS Bedrock Multi-Agent Pipeline")
    print(
        f"  Mode: {'LOCAL (MockBedrock)' if os.environ.get('LOCAL_MODE', 'true').lower() == 'true' else 'AWS PRODUCTION'}",
    )
    print(f"  Layers: Input → Planner → Architect → Coder → Quality Gates")
    print(f"  Bus: SQS (async message passing)")
    print(f"  State: DynamoDB (run tracking)")
    print(f"  Learning: Bedrock Knowledge Graph (RAG)")

    print("\n  Enter your request:")
    print(
        "  (Press Enter for default: 'Build a FastAPI REST API with CRUD endpoints')\n",
    )
    try:
        user_input = input("  > ").strip()
    except EOFError:
        user_input = ""
    if not user_input:
        user_input = (
            "Build a FastAPI REST API with endpoints to create, read, update, and delete users. "
            "Use Pydantic models for validation and in-memory storage."
        )

    run_id = str(uuid.uuid4())[:8]
    start_time = time.time()

    print(f"\n  Run ID  : {run_id}")
    print(
        f"  Request : {user_input[:80]}{'...' if len(user_input) > 80 else ''}",
    )

    bedrock = get_bedrock_client()
    bus = get_sqs_bus()
    state = get_state_store()
    kg = get_knowledge_graph()
    guardrails = Guardrails()

    core = run_pipeline_core(
        user_input,
        run_id,
        start_time,
        bedrock,
        bus,
        state,
        kg,
        guardrails,
        verbose=True,
    )
    finalize_pipeline_run(core, kg, state, quiet=False)

    plan = core["plan"]
    coder_output = core["code_output"]
    elapsed = float(core["elapsed_seconds"])
    overall = bool(core["overall_passed"])

    print_banner("PIPELINE COMPLETE")
    print(f"  Run ID      : {core['run_id']}")
    print(f"  Project     : {plan.get('project_name', '?')}")
    print(f"  Duration    : {elapsed:.1f}s")
    print(f"  Gates       : {'ALL PASSED ✓' if overall else 'CHECK ABOVE ⚠'}")
    print(f"  Output      : outputs/{coder_output.get('filename', '?')}")
    if coder_output.get("how_to_run"):
        print(f"\n  ▶  Run generated code:")
        print(f"     cd outputs && {coder_output['how_to_run']}")
    print(f"\n  ▶  Run again to build RAG — factory learns each time.")
    print("\n" + "═" * 65 + "\n")


if __name__ == "__main__":
    run_pipeline()
