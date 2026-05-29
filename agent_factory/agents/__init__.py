"""
agent_factory.agents
~~~~~~~~~~~~~~~~~~~~
Public agent exports — re-exported under both full and short names.

TesterAgent is DISABLED. ScribeAgent is now the final pipeline step.
"""
from agent_factory.agents.planner_agent    import PlannerAgent
from agent_factory.agents.researcher_agent import ResearcherAgent
from agent_factory.agents.architect_agent  import ArchitectAgent
from agent_factory.agents.coder_agent      import CoderAgent
# from agent_factory.agents.tester_agent import TesterAgent  # DISABLED — ScribeAgent handles final step
from agent_factory.agents.scribe_agent     import ScribeAgent

Planner    = PlannerAgent
Researcher = ResearcherAgent
Architect  = ArchitectAgent
Coder      = CoderAgent
Scribe     = ScribeAgent

__all__ = [
    "PlannerAgent", "ResearcherAgent", "ArchitectAgent", "CoderAgent",
    "ScribeAgent",
    "Planner", "Researcher", "Architect", "Coder", "Scribe",
]
