from __future__ import annotations

import sys

from core.pipeline import AgentFactoryPipeline
from core.state import PipelineStatus


def _print_banner(text: str, width: int = 68) -> None:
    print("\n" + "═" * width)
    print(f"  {text}")
    print("═" * width)


def _print_section(title: str, width: int = 68) -> None:
    print(f"\n  {'─' * (width - 4)}")
    print(f"  {title}")
    print(f"  {'─' * (width - 4)}")


def _print_kv(label: str, value: object, indent: int = 4) -> None:
    pad = " " * indent
    print(f"{pad}{label:<22}{value}")


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    requirement = " ".join(args).strip()

    if not requirement:
        try:
            requirement = input("  Requirement: ").strip()
        except (EOFError, KeyboardInterrupt):
            requirement = ""

    if not requirement:
        print("  No requirement provided. Exiting.")
        sys.exit(1)

    _print_banner("⚙️   Agent Factory — Phase 1")
    print(f"\n  Requirement : {requirement[:90]}{'...' if len(requirement) > 90 else ''}")

    pipeline = AgentFactoryPipeline()

    print("\n  Starting pipeline ...\n")
    state = pipeline.run(requirement)

    _print_section("RESULT")

    status_icon = {
        PipelineStatus.COMPLETED: "✓  completed",
        PipelineStatus.FAILED:    "✗  failed",
        PipelineStatus.RUNNING:   "⟳  running",
        PipelineStatus.PENDING:   "…  pending",
    }.get(state.status, str(state.status))

    _print_kv("Status", status_icon)
    _print_kv("Project", state.project_name or "(unnamed)")
    _print_kv("Output path", state.output_path or "(none)")
    _print_kv("Tests passed", "✓  yes" if state.test_passed else "✗  no")

    _print_section("TOKEN USAGE")
    totals = (state.token_usage or {}).get("totals", {})
    calls  = (state.token_usage or {}).get("calls", 0)
    _print_kv("Prompt tokens",     totals.get("prompt_tokens", 0))
    _print_kv("Completion tokens", totals.get("completion_tokens", 0))
    _print_kv("Total tokens",      totals.get("total_tokens", 0))
    _print_kv("LLM calls",         calls)

    by_agent = (state.token_usage or {}).get("by_agent", {})
    if by_agent:
        print()
        for agent, data in by_agent.items():
            print(f"    {agent:<22}{data.get('total_tokens', 0):>7} tokens")

    if state.error_log:
        _print_section("ERROR LOG")
        print()
        for line in state.error_log[:1000].splitlines():
            print(f"    {line}")

    print("\n" + "═" * 68 + "\n")


if __name__ == "__main__":
    main()
