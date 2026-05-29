import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def _getenv(name: str, default: str) -> str:
    val = os.getenv(name)
    return val if val is not None and str(val).strip() != "" else default


# OpenAI API key (used by Phase 1 LLMClient when OpenRouter is not configured).
OPENAI_API_KEY: str = _getenv("OPENAI_API_KEY", "")

# OpenRouter API key — when set, the LLMClient routes through OpenRouter instead of
# OpenAI directly. OpenRouter is OpenAI-compatible and supports 100+ models.
OPENROUTER_API_KEY: str = _getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"

# Resolved key used by LLMClient — prefers OpenRouter if available.
ACTIVE_API_KEY: str = OPENROUTER_API_KEY if OPENROUTER_API_KEY else OPENAI_API_KEY
ACTIVE_BASE_URL: str = OPENROUTER_BASE_URL if OPENROUTER_API_KEY else ""

# Model routing per agent — controls cost vs quality tradeoff.
MODEL_ROUTING: dict[str, str] = {
    "SupervisorAgent":    "gpt-4o-mini",   # routing only — fast + cheap
    "MarketingAgent":     "gpt-4o",        # deep strategy report — needs best model
    "PlannerAgent":       "gpt-4o",
    "ResearcherAgent":    "gpt-4o-mini",
    "ArchitectAgent":     "gpt-4o",
    "CoderAgent":         "gpt-4o",
    "UIUXAgent":          "gpt-4o",        # component library + design tokens
    "IntegrationAgent":   "gpt-4o",        # wiring frontend ↔ backend
    "ScribeAgent":        "gpt-4o",
    "ValidationAgent":    "gpt-4o-mini",   # static checks + short narrative
    "TesterAgent":        "gpt-4o-mini",
    "context_compressor": "gpt-4o-mini",
}


# Output directory for all generated projects.
# Anchored to the project root (parent of this file's package) so the path is
# stable regardless of which directory the server is started from.
# Override via OUTPUT_DIR env var (absolute or relative to project root).
_PROJECT_ROOT: Path = Path(__file__).parent.parent
_OUTPUT_DIR_ENV: str = _getenv("OUTPUT_DIR", "")
OUTPUT_DIR: Path = (
    Path(_OUTPUT_DIR_ENV).resolve()
    if _OUTPUT_DIR_ENV
    else (_PROJECT_ROOT / "output").resolve()
)


# Sandbox settings (isolated venv + pytest).
SANDBOX_TIMEOUT_SECONDS: int = int(_getenv("SANDBOX_TIMEOUT_SECONDS", "60"))
MAX_SANDBOX_RETRIES: int = int(_getenv("MAX_SANDBOX_RETRIES", "3"))


# Optional hard cap per run (not enforced in Phase 1 by default, but retained for future use).
MAX_TOKENS_PER_RUN: int = int(_getenv("MAX_TOKENS_PER_RUN", "150000"))

