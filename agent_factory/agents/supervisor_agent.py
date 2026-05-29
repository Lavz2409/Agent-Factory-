"""
SupervisorAgent — the first step in every pipeline run.

It acts as an intelligent router that:
  1. Deeply analyses the user's requirement
  2. Selects the most appropriate pipeline(s) from a fixed catalogue
  3. Recommends tools / tech stack
  4. Estimates complexity and required modules
  5. Returns a structured JSON result that subsequent agents use to focus their work

The result is stored on PipelineState and emitted to the frontend over WebSocket
so users see exactly how their requirement was interpreted before the build starts.
"""
from __future__ import annotations

import json
import re

from agent_factory.core.base_agent import BaseAgent
from agent_factory.core.state import PipelineState


# ── Catalogue of pipelines the supervisor can select ─────────────────────────

PIPELINE_CATALOGUE = {
    "AI_VISION":     "image processing, face recognition, object detection, CCTV analysis, video analytics",
    "WEB_APP":       "full-stack applications, dashboards, admin panels, REST APIs, user interfaces",
    "CHATBOT":       "conversational AI, assistants, NLP-based systems, chat interfaces",
    "DATA_PIPELINE": "data processing, ETL, analytics, large-scale data workflows",
    "AUTOMATION":    "workflow automation, triggers, background jobs, integrations",
    "MOBILE_APP":    "Android/iOS apps, React Native, Expo-based apps",
    "MARKETING":     "marketing strategy, competitor analysis, go-to-market plans, campaign ideas, growth hacking, brand positioning, product launch",
}


# ── System prompt ─────────────────────────────────────────────────────────────

SUPERVISOR_SYSTEM = """\
You are a highly intelligent Supervisor AI Agent responsible for routing project \
requirements to the most appropriate execution pipeline(s).

Your role is to:
1. Analyze the given project requirement deeply
2. Identify the core problem domain
3. Select the most relevant pipeline(s)
4. Suggest the appropriate tools/technologies
5. Provide a clear reasoning
6. Return a structured JSON output ONLY

---

AVAILABLE PIPELINES:

1. AI_VISION
   → Use for: image processing, face recognition, object detection, CCTV analysis, video analytics

2. WEB_APP
   → Use for: full-stack applications, dashboards, admin panels, APIs, user interfaces

3. CHATBOT
   → Use for: conversational AI, assistants, NLP-based systems, chat interfaces

4. DATA_PIPELINE
   → Use for: data processing, ETL, analytics, large-scale data workflows

5. AUTOMATION
   → Use for: workflow automation, triggers, background jobs, integrations

6. MOBILE_APP
   → Use for: Android/iOS apps, React Native, Expo-based apps

7. MARKETING
   → Use for: marketing strategy, competitor analysis, go-to-market plans, campaign ideas, growth hacking, brand positioning, product launch

---

INSTRUCTIONS:
- Carefully understand the intent of the project
- Do NOT guess — infer logically from keywords and context
- Select ONE or MULTIPLE pipelines if required
- Prioritize accuracy over simplicity
- Map each pipeline to relevant tools/tech stack
- Keep reasoning concise but meaningful
- Be deterministic (low randomness mindset)

---

OUTPUT FORMAT (STRICT JSON ONLY — no extra text, no markdown fences):

{
  "pipelines": ["PIPELINE_NAME"],
  "confidence": 0.0-1.0,
  "reason": "short explanation",
  "tools": ["tool1", "tool2", "..."],
  "complexity": "LOW | MEDIUM | HIGH",
  "estimated_modules": ["module1", "module2", "..."]
}

---

EXAMPLES:

Input: "Build a chatbot for customer support"
Output:
{"pipelines":["CHATBOT"],"confidence":0.95,"reason":"The project requires conversational AI for handling user queries","tools":["LLM","LangChain","Node.js"],"complexity":"MEDIUM","estimated_modules":["intent recognition","response generation","conversation memory"]}

Input: "Create a missing child detection system using CCTV and alerts"
Output:
{"pipelines":["AI_VISION","WEB_APP"],"confidence":0.97,"reason":"Requires image recognition for detection and a web system for alerts and monitoring","tools":["OpenCV","FaceNet","AWS Rekognition","React","Node.js","MongoDB"],"complexity":"HIGH","estimated_modules":["face detection","matching engine","alert system","admin dashboard"]}
"""


# ── Agent implementation ───────────────────────────────────────────────────────

class SupervisorAgent(BaseAgent):
    """
    Routes the user's requirement to the correct pipeline(s) and recommends
    an appropriate tech stack before any code is planned or written.
    """

    def __init__(self, llm_client) -> None:
        super().__init__("SupervisorAgent", llm_client)

    def run(self, state: PipelineState) -> PipelineState:
        state.set_agent(self.name)
        self.log("Analysing requirement and routing to the appropriate pipeline(s)...")

        raw = state.raw_requirement.strip()

        response = self.call_llm(
            prompt=f"INPUT:\n{raw}",
            system=SUPERVISOR_SYSTEM,
            use_cache=True,   # same requirement → same routing
        )

        routing = self._parse_json(response)

        # ── Persist on shared pipeline state ──────────────────────────────────
        state.supervisor_pipelines  = routing.get("pipelines",         [])
        state.supervisor_confidence = float(routing.get("confidence",  0.0))
        state.supervisor_reason     = routing.get("reason",            "")
        state.supervisor_tools      = routing.get("tools",             [])
        state.supervisor_complexity = routing.get("complexity",        "MEDIUM")
        state.supervisor_modules    = routing.get("estimated_modules", [])

        self.log(
            f"Routing → {state.supervisor_pipelines} "
            f"(confidence {state.supervisor_confidence:.0%}, "
            f"complexity {state.supervisor_complexity})"
        )
        self.log(f"Reason: {state.supervisor_reason}")
        self.log(f"Recommended tools: {', '.join(state.supervisor_tools)}")
        return state

    # ── helpers ──────────────────────────────────────────────────────────────

    @staticmethod
    def _parse_json(text: str) -> dict:
        """
        Robustly extract JSON from the LLM response even if the model wraps
        it in markdown code fences or adds preamble text.
        """
        text = text.strip()

        # Strip common code fences
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$",           "", text)
        text = text.strip()

        # Try direct parse
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Fallback: find the first {...} block in the response
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass

        # Last resort: return a safe default so the pipeline never crashes
        return {
            "pipelines":         ["WEB_APP"],
            "confidence":        0.5,
            "reason":            "Could not parse supervisor response; defaulting to WEB_APP.",
            "tools":             ["Python", "FastAPI"],
            "complexity":        "MEDIUM",
            "estimated_modules": [],
        }
