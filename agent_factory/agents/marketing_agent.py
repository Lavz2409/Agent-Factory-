"""
MarketingAgent — a world-class Product Marketing Strategist AI.

Activated when the SupervisorAgent routes a requirement to the MARKETING pipeline.

Given a product idea / description, it generates a 10-section marketing
intelligence report and saves it as `marketing_report.md` alongside any other
output files so it appears automatically in the frontend FILES panel.
"""
from __future__ import annotations

import os
import re

from agent_factory.core.base_agent import BaseAgent
from agent_factory.core.state import PipelineState


# ── System prompt ─────────────────────────────────────────────────────────────

MARKETING_SYSTEM = """\
You are a world-class Product Marketing Strategist AI.

Your role is to analyse a given product or idea and generate a complete, \
actionable marketing intelligence report.

You think simultaneously as:
- A competitor analyst
- A product marketer  
- A growth hacker
- A brand strategist

---

REPORT SECTIONS (complete ALL of them):

## 1. PRODUCT UNDERSTANDING
- What the product does (2-3 clear sentences)
- Core value proposition (one sharp sentence)
- Problem it solves

## 2. COMPETITOR ANALYSIS
- Top 3-5 existing competitors
- Feature / pricing / strength / weakness comparison (use a table or bullets)
- Competitor gaps this product can exploit

## 3. DIFFERENTIATION STRATEGY
- What makes this product unique
- Positioning statement (one sentence, "For X who Y, [Product] is Z")
- Suggested brand tone (premium / fun / technical / minimal / bold …)

## 4. USE CASES
- 5+ real-world use cases
- Primary vs secondary users
- Industries with highest adoption potential

## 5. MARKETING STRATEGY
Broken into:
- Organic (SEO keywords, content pillars, social channels)
- Paid (ad formats, targeting strategy, platforms)
- Community (Discord / Reddit / forums strategy)
- Influencer (type, tier, collaboration format)
- Partnerships (co-marketing, integrations, APIs)

## 6. CAMPAIGN IDEAS
- 3-5 creative campaign concepts
- Each must include: Hook, Tagline, Messaging angle, Channel

## 7. GO-TO-MARKET PLAN
- Launch strategy (beta / waitlist / viral loop)
- First 30-day execution plan (week-by-week)

## 8. CONTENT STRATEGY
- 5 blog post ideas (with title + brief)
- 5 social media post ideas (with platform + format)
- 3 short-form video concepts (hook + format)

## 9. GROWTH HACKS
- 5 unconventional growth strategies
- Viral loop ideas, referral mechanics, automation hacks

## 10. SWOT ANALYSIS
| Factor | Detail |
|---|---|
| Strengths | … |
| Weaknesses | … |
| Opportunities | … |
| Threats | … |

---

RULES:
- Output ONLY the report in clean Markdown (start directly with "# Marketing Intelligence Report")
- No preamble, no "here is your report", no fluff
- Every bullet must be ACTIONABLE and SPECIFIC
- Be realistic AND creative
- Minimum 1,200 words
"""


# ── Agent implementation ───────────────────────────────────────────────────────

class MarketingAgent(BaseAgent):
    """
    Generates a full 10-section marketing intelligence report for the given
    product requirement and saves it as marketing_report.md.
    """

    def __init__(self, llm_client) -> None:
        super().__init__("MarketingAgent", llm_client)

    def run(self, state: PipelineState) -> PipelineState:
        state.set_agent(self.name)

        raw = state.raw_requirement.strip()
        self.log(f"Generating marketing intelligence report for: {raw[:120]}...")

        # Build a context-rich user message that includes supervisor insight
        context_lines = [f"Product / Idea Description:\n{raw}"]
        if state.supervisor_pipelines:
            context_lines.append(f"Pipeline Category: {', '.join(state.supervisor_pipelines)}")
        if state.supervisor_complexity:
            context_lines.append(f"Complexity: {state.supervisor_complexity}")
        if state.supervisor_tools:
            context_lines.append(f"Suggested Stack: {', '.join(state.supervisor_tools[:8])}")

        user_msg = "\n\n".join(context_lines)

        report = self.call_llm(
            prompt=user_msg,
            system=MARKETING_SYSTEM,
            use_cache=False,   # marketing reports should be fresh every run
        )

        # Strip any accidental code fences
        report = re.sub(r"^```[^\n]*\n", "", report.strip(), flags=re.MULTILINE)
        report = re.sub(r"\n```\s*$", "", report.strip())
        report = report.strip()

        if not report.startswith("#"):
            report = f"# Marketing Intelligence Report\n\n{report}"

        # Persist on state
        state.marketing_report = report

        # Inject into generated_files so the WebSocket monitor streams it immediately
        state.generated_files["marketing_report.md"] = report

        # Also save to disk alongside other output files
        output_dir = state.output_path if state.output_path else self._default_output_dir()
        os.makedirs(output_dir, exist_ok=True)

        report_path = os.path.join(output_dir, "marketing_report.md")
        with open(report_path, "w", encoding="utf-8") as fh:
            fh.write(report)

        state.marketing_report_path = report_path
        self.log(f"marketing_report.md saved → {report_path}")
        self.log(f"Report length: {len(report):,} chars  ({len(report.splitlines())} lines)")
        return state

    # ── helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _default_output_dir() -> str:
        return os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "output", "marketing",
        )
