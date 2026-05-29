"""
UIUXAgent — step 4 in the 8-agent pipeline.

Produces a complete, modern UI design system with BOTH dark and light mode support,
a component library (Button, Input, Card, Modal, etc.), and a style guide document.

All generated files are injected into `state.generated_files` so they flow through
the existing WebSocket streamer and land in the frontend FILES panel.

The agent also writes a standalone `UI_DESIGN_SYSTEM.md` report that is streamed
alongside code files.
"""
from __future__ import annotations

import os
import re

from agent_factory.core.base_agent import BaseAgent
from agent_factory.core.state import PipelineState


# ── System prompt ─────────────────────────────────────────────────────────────

UIUX_SYSTEM = """\
You are a world-class Product Designer and Frontend Engineer (Stripe / Linear / \
Vercel caliber).  Produce a complete, production-ready UI design system.

Your output MUST include:

## 1. DESIGN TOKENS
- Full dark-mode and light-mode CSS variable palettes
- Typography scale (font family, sizes, weights, line-heights)
- Spacing scale, border-radius, shadow tokens
- Motion tokens (duration, easing)

## 2. COMPONENT LIBRARY
Generate COMPLETE, WORKING code for EVERY component below.  No placeholders, no
ellipsis, no "TODO".  Use the exact `FILE: /path/to/file.ext` format shown.

Components required:
  • Button   (variants: primary, secondary, danger, ghost; sizes: sm, md, lg; loading state)
  • Input    (text, email, password, with label + error slot)
  • Card     (header, body, footer slots)
  • Modal    (accessible, keyboard dismiss, focus trap)
  • Navbar   (logo, nav items, theme toggle, user menu)
  • Sidebar  (collapsible, active route indicator)
  • Alert    (info, success, warning, error)
  • Toast    (portal-based, auto-dismiss)
  • ThemeProvider (context-based dark/light toggle, persists to localStorage)

## 3. PAGE LAYOUTS
Complete JSX for each page:
  • Landing page (hero + features + CTA)
  • Login / Register
  • Dashboard (sidebar + content area)
  • Settings (profile + preferences)

## 4. TAILWIND CONFIG
Extend `tailwind.config.js` with the design tokens.

## STRICT OUTPUT CONTRACT

For EVERY file, use this EXACT marker format so our parser can extract it:

FILE: /frontend/src/components/Button.jsx
```jsx
// …complete code…
```

FILE: /frontend/src/styles/theme.css
```css
/* …complete css… */
```

Rules:
- Use React + Tailwind CSS unless the tech stack says otherwise
- Every component must be fully accessible (aria, keyboard)
- Every component must support dark + light themes out of the box
- Responsive, mobile-first
- No external UI libraries (Radix/shadcn are fine as pure copy-paste patterns, but no npm adds)
- Include keyboard shortcuts where meaningful
- Write clean, idiomatic TypeScript or JavaScript (match the project's stack)

Return nothing except the FILE blocks.  No preamble.  No "here is your design system".
"""


# ── Agent implementation ───────────────────────────────────────────────────────

class UIUXAgent(BaseAgent):
    """
    Generates a complete UI design system (tokens, components, pages) with dark
    + light mode support.  Output files are injected into state.generated_files.
    """

    FILE_HEADER_RE = re.compile(r"FILE:\s*([^\n]+?)\n```([a-zA-Z0-9]*)\n", re.MULTILINE)

    def __init__(self, llm_client) -> None:
        super().__init__("UIUXAgent", llm_client)

    def run(self, state: PipelineState) -> PipelineState:
        state.set_agent(self.name)
        self.log("Designing dark + light mode UI system and component library...")

        # Build a context-rich prompt using upstream state
        stack = ", ".join(state.tech_stack[:10]) if state.tech_stack else "React + Tailwind CSS"
        features = "\n".join(
            f"- {t.get('title', t) if isinstance(t, dict) else t}"
            for t in (state.task_breakdown or [])[:10]
        ) or "- (no explicit features)"

        user_prompt = (
            f"PROJECT REQUIREMENT:\n{state.raw_requirement}\n\n"
            f"PROJECT NAME: {state.project_name or 'Unnamed Project'}\n"
            f"TECH STACK: {stack}\n\n"
            f"CORE FEATURES:\n{features}\n\n"
            "Produce the complete UI design system now following the strict output contract."
        )

        response = self.call_llm(
            prompt=user_prompt,
            system=UIUX_SYSTEM,
            use_cache=False,
        )

        files = self._extract_files(response)
        self.log(f"Extracted {len(files)} UI files from response.")

        # Stream each file into state.generated_files so the WS monitor picks it up
        for path, content in files.items():
            state.generated_files[path] = content
            state.ui_files.append(path)

        # Also write to disk alongside other code if we have an output folder
        output_dir = state.output_path
        if output_dir:
            for rel_path, content in files.items():
                safe = rel_path.lstrip("/\\")
                dest = os.path.join(output_dir, safe)
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                with open(dest, "w", encoding="utf-8") as fh:
                    fh.write(content)

        # Build + save a human-readable design system markdown
        design_md = self._build_design_doc(files)
        state.ui_design_system = design_md
        state.generated_files["UI_DESIGN_SYSTEM.md"] = design_md

        if output_dir:
            md_path = os.path.join(output_dir, "UI_DESIGN_SYSTEM.md")
            with open(md_path, "w", encoding="utf-8") as fh:
                fh.write(design_md)

        self.log(
            f"Design system ready — {len(files)} component/style files + "
            "UI_DESIGN_SYSTEM.md"
        )
        return state

    # ── helpers ───────────────────────────────────────────────────────────────

    def _extract_files(self, text: str) -> dict[str, str]:
        """
        Parse `FILE: path\\n```lang\\n...code...\\n````` blocks from the LLM output.
        """
        files: dict[str, str] = {}
        # Use regex to split on FILE markers
        pattern = re.compile(
            r"FILE:\s*([^\n]+?)\s*\n```[a-zA-Z0-9+-]*\s*\n(.*?)\n```",
            re.DOTALL,
        )
        for match in pattern.finditer(text):
            raw_path = match.group(1).strip().strip("`").strip()
            code     = match.group(2).rstrip()
            # Normalise path
            path = raw_path.replace("\\", "/").lstrip("/")
            if path:
                files[path] = code
        return files

    @staticmethod
    def _build_design_doc(files: dict[str, str]) -> str:
        lines = [
            "# UI/UX Design System",
            "",
            "Complete component library with **dark mode** and **light mode** support.",
            "",
            "## Generated files",
            "",
        ]
        for path in sorted(files.keys()):
            lines.append(f"- `{path}`")
        lines.append("")
        lines.append("## How to use")
        lines.append("")
        lines.append("1. Drop the files into your frontend project at the paths shown above.")
        lines.append("2. Wrap `<App />` with `<ThemeProvider>` to enable the theme toggle.")
        lines.append("3. Import components from `src/components/*` where needed.")
        lines.append("")
        return "\n".join(lines)
