from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Optional

from agent_factory.core.base_agent import BaseAgent
from agent_factory.core.state import PipelineState

# ── system prompt ──────────────────────────────────────────────────────────────

SCRIBE_SYSTEM = """\
You are a senior technical writer. Generate a complete developer walkthrough \
in clean Markdown. Populate EVERY section fully — never write N/A or leave \
any section empty. Use the project context provided.

# 📦 Project Overview
- What was built (plain English, 3-5 sentences)
- Key features (bulleted list, minimum 4 items)

# 🔄 Architecture & Execution Flow
- Numbered step-by-step execution flow
- How components/agents interact
- Data flow diagram in ASCII if helpful

# 📁 Generated Files
| File | Purpose |
|------|---------|
(one row per generated file — infer from the code provided)

# 📚 Libraries & Frameworks
| Library | Type | Purpose | Install Command |
|---------|------|---------|-----------------|
(separate stdlib from third-party; include pip install commands)

# ⚙️ Setup & Installation
Numbered steps:
1. Python version requirement
2. pip install commands in ```bash blocks
3. Any .env or config setup needed

# ▶️ Commands to Run
```bash
python generated_agent.py
```
(list every relevant command with flags and env vars)

# 🧪 Test Cases
| # | Input | Expected Output | Pass Criteria |
|---|-------|-----------------|---------------|
(minimum 5 concrete test cases with real values)

# 🔍 Manual Testing Steps
Numbered step-by-step instructions for a human to verify the project works.
Minimum 6 steps.

# 🚀 Future Improvements
- At least 4 concrete, actionable suggestions

Return ONLY the Markdown. No outer code fences. No preamble."""


class ScribeAgent(BaseAgent):
    """
    Final pipeline step — generates a comprehensive developer walkthrough
    (walkthrough.md + README.md) and saves all project files to disk.
    """

    def __init__(self, llm_client, output_dir: Optional[str] = None) -> None:
        super().__init__("ScribeAgent", llm_client)
        if output_dir and os.path.isabs(str(output_dir)):
            self.output_dir = str(output_dir)
        else:
            # Default: agent_factory/output/ — always resolvable relative to this file
            base = Path(__file__).resolve().parents[1]   # agent_factory/
            self.output_dir = str(base / "output")
        os.makedirs(self.output_dir, exist_ok=True)

    # ── public interface (BaseAgent contract) ─────────────────────────────────

    def run(self, state: PipelineState) -> PipelineState:
        state.set_agent(self.name)
        self.log("Generating project walkthrough documentation...")

        requirement: str = state.raw_requirement

        plan: str = json.dumps(
            {
                "project_name":       state.project_name,
                "project_type":       state.project_type,
                "tasks":              state.task_breakdown,
                "tech_stack":         state.tech_stack,
                "agent_instructions": state.agent_plan,
            },
            indent=2,
        )

        architecture: str = json.dumps(
            {
                "system_design":  state.system_design,
                "file_structure": state.file_structure,
                "data_flow":      state.data_flow,
                "api_contracts":  state.api_contracts,
            },
            indent=2,
        )

        # Build code section — cap at 12 000 chars to avoid token overflow
        code_parts: list[str] = []
        total_chars = 0
        max_chars = 12_000
        for fname, content in state.generated_files.items():
            snippet = f"### {fname}\n```\n{content}\n```\n"
            if total_chars + len(snippet) > max_chars:
                code_parts.append(
                    f"### {fname}\n(content omitted — {len(content)} chars)\n"
                )
                total_chars += len(snippet)   # still count omitted to stop early
                continue
            code_parts.append(snippet)
            total_chars += len(snippet)
        code: str = "\n".join(code_parts)

        self.log("Calling LLM for walkthrough document...")
        walkthrough = self._generate_walkthrough(
            requirement=requirement,
            plan=plan,
            architecture=architecture,
            code=code,
            file_manifest=state.file_structure,
        )

        # Use the CoderAgent's output folder so walkthrough.md lives alongside
        # the generated code files.  Fall back to self.output_dir if not set.
        output_dir = state.output_path if state.output_path else self.output_dir
        os.makedirs(output_dir, exist_ok=True)

        self.log(f"Saving walkthrough.md to {output_dir} ...")
        walkthrough_path = os.path.join(output_dir, "walkthrough.md")
        with open(walkthrough_path, "w", encoding="utf-8") as f:
            f.write(walkthrough)
        self.log(f"[ScribeAgent] walkthrough.md → {walkthrough_path}")

        run_commands = self._extract_run_commands(walkthrough)

        # ── Persist in shared pipeline state ─────────────────────────────────
        state.scribe_walkthrough      = walkthrough
        state.scribe_saved_files      = [walkthrough_path]
        state.scribe_output_dir       = output_dir
        state.scribe_run_commands     = run_commands
        state.scribe_readme_path      = ""
        state.scribe_walkthrough_path = walkthrough_path

        # ── CRITICAL: inject into generated_files so the WS monitor thread
        #    streams it to the FILES panel immediately, just like code files ──
        state.generated_files["walkthrough.md"] = walkthrough

        self.log("Walkthrough generated and saved successfully.")
        return state

    # ── internal helpers ──────────────────────────────────────────────────────

    def _generate_walkthrough(
        self,
        requirement: str,
        plan: str,
        architecture: str,
        code: str,
        file_manifest: dict,
    ) -> str:
        """Call the LLM to produce the full Markdown walkthrough."""
        if file_manifest:
            manifest_lines = "\n".join(
                f"- **{fname}**: {purpose}"
                for fname, purpose in file_manifest.items()
            )
        else:
            manifest_lines = "(derived from generated code above)"

        user_message = (
            f"Requirement: {requirement}\n\n"
            f"Plan:\n{plan}\n\n"
            f"Architecture:\n{architecture}\n\n"
            f"Generated Code:\n{code}\n\n"
            f"Files Created:\n{manifest_lines}"
        )

        return self.call_llm(
            prompt=user_message,
            system=SCRIBE_SYSTEM,
            use_cache=False,
        ).strip()

    def _save_files(self, code: str, walkthrough: str, output_dir: str) -> list[str]:
        """Write walkthrough.md, README.md, and parsed source files to output_dir.

        Returns a list of absolute paths for every file successfully written.
        """
        os.makedirs(output_dir, exist_ok=True)
        saved: list[str] = []

        # 1. Always write walkthrough.md
        walkthrough_path = os.path.join(output_dir, "walkthrough.md")
        with open(walkthrough_path, "w", encoding="utf-8") as f:
            f.write(walkthrough)
        saved.append(walkthrough_path)
        print(f"[ScribeAgent] walkthrough.md → {walkthrough_path}")

        # 2. Parse and write code files
        # Matches: "# filename: foo.py" | "# File: foo.py" | "### foo.py" | "## foo.py"
        pattern = (
            r"(?m)^(?:#{1,3}\s+|# filename:\s*|# File:\s*)"
            r"([^\n]+\.(?:py|js|ts|jsx|tsx|json|yaml|yml|txt|sh|env|toml|cfg|ini))\s*\n"
        )
        parts = re.split(pattern, code)

        if len(parts) >= 3:
            # Interleaved: [preamble, name1, content1, name2, content2, …]
            pairs = list(zip(parts[1::2], parts[2::2]))
            for fname, fcontent in pairs:
                fname = fname.strip().replace("/", os.sep).replace("\\", os.sep)
                fpath = os.path.join(output_dir, fname)
                if os.path.dirname(fname):
                    os.makedirs(os.path.dirname(fpath), exist_ok=True)
                # Strip markdown code-fences that wrap the snippet (``` or ```python etc.)
                clean = fcontent.strip()
                clean = re.sub(r"^```[^\n]*\n", "", clean)
                clean = re.sub(r"\n```\s*$", "", clean)
                with open(fpath, "w", encoding="utf-8") as f:
                    f.write(clean.strip())
                saved.append(fpath)
                print(f"[ScribeAgent] {fname} → {fpath}")
        else:
            # No delimiters found — save entire code string as generated_agent.py
            fpath = os.path.join(output_dir, "generated_agent.py")
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(code.strip())
            saved.append(fpath)
            print(f"[ScribeAgent] generated_agent.py → {fpath}")

        return saved

    def _extract_run_commands(self, walkthrough: str) -> list[str]:
        """Parse walkthrough Markdown for bash code blocks in the Commands to Run section."""
        section_match = re.search(
            r"#.*?Commands to Run.*?\n(.*?)(?=\n#|\Z)",
            walkthrough,
            re.DOTALL | re.IGNORECASE,
        )
        search_text = section_match.group(1) if section_match else walkthrough

        blocks = re.findall(
            r"```(?:bash|sh|shell)\n(.*?)```",
            search_text,
            re.DOTALL,
        )

        commands: list[str] = []
        for block in blocks:
            for line in block.strip().splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    commands.append(line)

        return commands if commands else ["python generated_agent.py"]
