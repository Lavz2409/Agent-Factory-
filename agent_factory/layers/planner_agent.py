"""
LAYER 2 — PLANNER AGENT (The Crown Jewel)
The most important component. Decides which agents to spawn,
their scope, communication protocols, and execution sequence.
Uses RAG to match requirements against proven past architectures.
All investment in prompts and pattern retrieval concentrates here.
A smarter planner multiplies quality downstream.
Tech: Task decomposition, Agent topology design, RAG pattern matching.
"""

from __future__ import annotations

import os
from typing import Any

from utils.bedrock_client import DEFAULT_BEDROCK_TEXT_MODEL, invoke_json_with_retry
from utils.knowledge_graph import get_knowledge_graph


def _validate_plan(d: dict[str, Any]) -> bool:
    strat = d.get("strategy")
    if not isinstance(strat, str) or not strat.strip():
        return False
    tasks = d.get("tasks")
    if not isinstance(tasks, list) or len(tasks) < 2:
        return False
    agents: set[str] = set()
    for t in tasks:
        if not isinstance(t, dict):
            continue
        a = str(t.get("agent", "")).lower().strip()
        if a:
            agents.add(a)
    return "architect" in agents and "coder" in agents


class PlannerAgent:
    """Layer 2 planner: RAG + Bedrock decomposition; publishes worker tasks on SQS."""

    SYSTEM_PROMPT = """[AGENT_PLANNER]
You are the master orchestrator of an AI agent factory.
Return ONLY valid JSON. Do NOT use markdown. Do NOT wrap in code fences.
Do NOT include explanations outside the JSON object.
The output must be directly parseable with json.loads().
If you fail, the system will reject your response.

Required JSON shape:
{
  "strategy": "one clear sentence describing the overall approach",
  "tasks": [
    {"agent": "architect", "task": "specific design task for the architect"},
    {"agent": "coder", "task": "specific implementation task for the coder"}
  ]
}

Rules:
- Exactly two tasks minimum, one for architect and one for coder (you may add more tasks only if needed).
- Each task must include "agent" and "task" (string).
- "agent" must be exactly "architect" or "coder".
"""

    def __init__(self, bedrock_client: Any, state_store: Any, sqs_bus: Any) -> None:
        self.bedrock = bedrock_client
        self.state = state_store
        self.bus = sqs_bus
        self.kg = get_knowledge_graph()

    def plan(self, parsed_input: dict[str, Any], run_id: str) -> dict[str, Any]:
        """Build execution plan from parsed input; persist; enqueue worker tasks."""
        similar_patterns = self.kg.retrieve_similar(
            intent=str(parsed_input.get("intent", "")),
            domain=str(parsed_input.get("domain", "")),
            top_k=3,
        )

        rag_context = ""
        if similar_patterns:
            rag_context = "\n\nPast successful patterns for similar requests:\n"
            for i, p in enumerate(similar_patterns, 1):
                arch = p.get("architecture_summary", {})
                rag_context += f"{i}. Domain: {p.get('domain')} | "
                rag_context += f"Components: {arch.get('components', [])} | "
                rag_context += f"Entry: {arch.get('entry_point', '')}\n"

        constraints = parsed_input.get("constraints", ["none"])
        constraints_str = ", ".join(str(x) for x in constraints) if constraints else "none"
        criteria = parsed_input.get("success_criteria", ["runs correctly"])
        criteria_str = ", ".join(str(x) for x in criteria) if criteria else "runs correctly"

        user_prompt = f"""
Create a precise execution plan for this project.

Intent: {parsed_input['intent']}
Domain: {parsed_input['domain']}
Constraints: {constraints_str}
Expected Output: {parsed_input['expected_output']}
Complexity: {parsed_input.get('complexity', 'medium')}
Success Criteria: {criteria_str}
{rag_context}

Decompose into tasks. The architect designs first; the coder implements from that design.

Respond with ONLY this JSON (no extra keys required beyond strategy and tasks; you may add optional fields):
{{
  "strategy": "one sentence: overall approach",
  "tasks": [
    {{"agent": "architect", "task": "detailed design task", "context": "optional"}},
    {{"agent": "coder", "task": "detailed implementation task", "context": "optional"}}
  ]
}}
"""

        model_id = os.environ.get("BEDROCK_REASONING_MODEL", DEFAULT_BEDROCK_TEXT_MODEL)

        emergency: dict[str, Any] = {
            "project_name": "emergency_project",
            "strategy": f"Design then implement: {parsed_input.get('intent', 'project')}",
            "rag_patterns_used": len(similar_patterns),
            "tasks": [
                {
                    "agent": "architect",
                    "task": str(parsed_input.get("intent", "Design the system")),
                    "context": "",
                },
                {
                    "agent": "coder",
                    "task": str(parsed_input.get("expected_output", "Implement in Python")),
                    "context": "",
                },
            ],
        }

        raw_result = invoke_json_with_retry(
            self.bedrock,
            model_id,
            user_prompt,
            self.SYSTEM_PROMPT,
            agent="planner",
            validate=_validate_plan,
            emergency_fallback=emergency,
        )

        # Merge with extended fields for downstream compatibility
        result: dict[str, Any] = {
            "project_name": raw_result.get("project_name", "project"),
            "strategy": raw_result.get("strategy", emergency["strategy"]),
            "rag_patterns_used": raw_result.get(
                "rag_patterns_used",
                len(similar_patterns),
            ),
            "tasks": raw_result.get("tasks", emergency["tasks"]),
        }

        tasks = result.get("tasks", [])
        if not isinstance(tasks, list):
            tasks = emergency["tasks"]

        normalized: list[dict[str, Any]] = []
        for t in tasks:
            if not isinstance(t, dict):
                continue
            agent = str(t.get("agent", "")).lower().strip()
            if agent not in ("architect", "coder"):
                continue
            normalized.append(
                {
                    "agent": agent,
                    "task": str(t.get("task", "")),
                    "context": str(t.get("context", "")),
                },
            )
        if len(normalized) < 2:
            normalized = list(emergency["tasks"])
        result["tasks"] = normalized
        result["rag_patterns_used"] = len(similar_patterns)

        try:
            self.state.put(run_id, "plan", result)
            self.state.put(run_id, "status", "planned")
        except Exception:
            pass

        for task in result.get("tasks", []):
            try:
                self.bus.send_message(
                    "worker-queue",
                    {
                        "message_type": "task",
                        "source": "planner",
                        "destination": task["agent"],
                        "run_id": run_id,
                        "payload": task,
                    },
                )
            except Exception:
                pass

        return result
