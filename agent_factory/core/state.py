from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class PipelineStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class PipelineState:
    # Input
    raw_requirement: str = ""
    project_name: str = ""
    project_type: str = ""  # web, mobile, cli, desktop, multi-agent

    # SupervisorAgent output — set before Planner runs
    supervisor_pipelines:  list[str] = field(default_factory=list)
    supervisor_confidence: float     = 0.0
    supervisor_reason:     str       = ""
    supervisor_tools:      list[str] = field(default_factory=list)
    supervisor_complexity: str       = ""
    supervisor_modules:    list[str] = field(default_factory=list)

    # Planner output
    task_breakdown: list[dict[str, Any]] = field(default_factory=list)
    agent_plan: dict[str, Any] = field(default_factory=dict)
    tech_stack: list[str] = field(default_factory=list)

    # Researcher output
    research_notes: str = ""
    relevant_libraries: list[str] = field(default_factory=list)
    reference_patterns: list[str] = field(default_factory=list)

    # Architect output
    system_design: str = ""
    file_structure: dict[str, str] = field(default_factory=dict)  # filename → purpose
    data_flow: str = ""
    api_contracts: list[dict[str, Any]] = field(default_factory=list)

    # Coder output
    generated_files: dict[str, str] = field(default_factory=dict)  # filename → code
    output_path: str = ""

    # Tester output
    test_results: list[dict[str, Any]] = field(default_factory=list)
    test_passed: bool = False
    error_log: str = ""
    coverage_report: str = ""

    # MarketingAgent output
    marketing_report:      str = ""    # full Markdown marketing intelligence report
    marketing_report_path: str = ""    # absolute path to marketing_report.md

    # UIUXAgent output
    ui_design_system: str = ""                                   # UI_DESIGN_SYSTEM.md body
    ui_files:         list[str] = field(default_factory=list)    # generated component/style paths

    # IntegrationAgent output
    integration_guide: str = ""                                   # INTEGRATION_GUIDE.md body
    integration_notes: list[str] = field(default_factory=list)
    integration_files: list[str] = field(default_factory=list)    # generated integration layer paths

    # ValidationAgent output
    validation_report:      str = ""                             # full validation_report.md
    validation_report_path: str = ""                             # absolute path
    validation_checks:      dict[str, Any] = field(default_factory=dict)
    validation_issues:      list[str]      = field(default_factory=list)
    validation_score:       float = 0.0
    validation_ready:       bool  = False

    # ScribeAgent output
    scribe_walkthrough: str = ""                                    # full Markdown walkthrough document
    scribe_readme_path: str = ""                                    # absolute path to README.md
    scribe_walkthrough_path: str = ""                               # absolute path to walkthrough.md
    scribe_saved_files: list[str] = field(default_factory=list)    # absolute paths of all files written
    scribe_output_dir: str = ""                                     # directory where files were saved
    scribe_run_commands: list[str] = field(default_factory=list)   # ready-to-run terminal commands

    # Activity log — one entry per agent: {agent, status, summary, full_output, duration, step}
    activity_log: list[dict[str, Any]] = field(default_factory=list)

    # Pipeline meta
    status: PipelineStatus = PipelineStatus.PENDING
    current_agent: str = ""
    logs: list[str] = field(default_factory=list)
    token_usage: dict[str, Any] = field(default_factory=dict)

    def log(self, message: str) -> None:
        self.logs.append(message)

    def set_agent(self, agent_name: str) -> None:
        self.current_agent = agent_name
        self.status = PipelineStatus.RUNNING
        self.log(f"▶ {agent_name} started")

