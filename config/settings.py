"""
Centralised application settings loaded from the .env file at project root.

Usage
-----
    from config.settings import settings
    print(settings.openrouter_api_key)
"""
from __future__ import annotations
from pathlib import Path
from pydantic_settings import BaseSettings

_ENV_FILE = Path(__file__).parent.parent / ".env"

class Settings(BaseSettings):
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openai_api_key: str = ""
    model: str = "gpt-4o"
    output_dir: str = "output"
    sandbox_timeout_seconds: int = 60
    max_sandbox_retries: int = 3
    log_level: str = "INFO"

    class Config:
        env_file = str(_ENV_FILE)
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()
