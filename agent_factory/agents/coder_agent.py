from __future__ import annotations

from agent_factory.core.base_agent import BaseAgent
from agent_factory.core.state import PipelineState
from agent_factory.prompts.coder import CODER_SYSTEM, build_coder_prompt
from agent_factory.utils.file_writer import write_project_files


class CoderAgent(BaseAgent):
    def __init__(self, llm_client):
        super().__init__("CoderAgent", llm_client)

    def run(self, state: PipelineState) -> PipelineState:
        state.set_agent(self.name)
        self.log(f"Generating code for {len(state.file_structure)} files...")

        generated: dict[str, str] = {}

        # Build interface summary (signatures only, not full code)
        interface_summary = ""

        for filename, purpose in (state.file_structure or {}).items():
            self.log(f"Coding {filename}...")

            # Find relevant API contracts for this file
            contracts = [c for c in (state.api_contracts or []) if c.get("file") == filename]

            prompt = build_coder_prompt(
                filename=filename,
                purpose=purpose,
                tech_stack=state.tech_stack,
                api_contracts=contracts,
                research_notes=state.research_notes,
                interface_summary=interface_summary,
                instructions=state.agent_plan.get("coder", ""),
                full_requirement=state.raw_requirement,
            )

            code = self.call_llm(
                prompt=prompt,
                system=CODER_SYSTEM,
                use_cache=False,  # Never cache code — always fresh
            )

            code = self._clean_code(code)
            generated[filename] = code

            # Update interface summary with just the signatures from this file
            interface_summary += f"\n# {filename}\n{self._extract_signatures(code)}\n"

        state.generated_files = generated

        # Write to disk
        output_path = write_project_files(
            project_name=state.project_name,
            files=generated,
            libraries=state.relevant_libraries,
        )
        state.output_path = output_path
        self.log(f"All files written to {output_path}")
        return state

    def _clean_code(self, raw: str) -> str:
        if "```python" in raw:
            raw = raw.split("```python", 1)[1].split("```")[0]
        elif "```" in raw:
            raw = raw.split("```", 1)[1].split("```")[0]
        return (raw or "").strip()

    def _extract_signatures(self, code: str) -> str:
        """Extract function/class signatures only for interface summary."""
        lines = (code or "").split("\n")
        sigs: list[str] = []
        for l in lines:
            s = l.strip()
            if s.startswith("def ") or s.startswith("class ") or s.startswith("async def "):
                sigs.append(s)
            if len(sigs) >= 20:
                break
        return "\n".join(sigs)

