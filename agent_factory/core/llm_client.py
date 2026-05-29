from __future__ import annotations

import hashlib
from typing import Optional

from openai import OpenAI

from agent_factory.config import ACTIVE_API_KEY, ACTIVE_BASE_URL, MODEL_ROUTING, OPENROUTER_API_KEY
from agent_factory.utils.logger import get_logger
from agent_factory.utils.token_counter import TokenCounter


logger = get_logger("LLMClient")

# Default fallback model — uses OpenRouter path when active.
_DEFAULT_MODEL = "openai/gpt-4o" if OPENROUTER_API_KEY else "gpt-4o"


class LLMClient:
    def __init__(self) -> None:
        if not ACTIVE_API_KEY or str(ACTIVE_API_KEY).strip() == "":
            raise ValueError(
                "No API key found. Set OPENROUTER_API_KEY (preferred) or OPENAI_API_KEY in `.env`."
            )

        client_kwargs: dict = {"api_key": ACTIVE_API_KEY}
        if ACTIVE_BASE_URL:
            client_kwargs["base_url"] = ACTIVE_BASE_URL

        self.client = OpenAI(**client_kwargs)
        self.using_openrouter = bool(OPENROUTER_API_KEY)
        self.cache: dict[str, str] = {}
        self.token_counter = TokenCounter()

        logger.info(
            f"LLMClient initialised — backend: {'OpenRouter' if self.using_openrouter else 'OpenAI direct'}"
        )

    def call(
        self,
        prompt: str,
        system: str = "",
        agent_name: str = "",
        use_cache: bool = True,
        force_model: Optional[str] = None,
    ) -> str:
        model = force_model or MODEL_ROUTING.get(agent_name, _DEFAULT_MODEL)

        cache_key = hashlib.sha256(f"{system}||{prompt}||{model}".encode("utf-8")).hexdigest()
        if use_cache and cache_key in self.cache:
            logger.info(f"[{agent_name}] Cache hit — skipping LLM call")
            return self.cache[cache_key]

        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        # Token budget: gpt-3.5 caps at 4096, gpt-4o-mini at 16384, everything else 8192
        max_tokens = (
            4096  if "gpt-3.5"   in model else
            16384 if "gpt-4o-mini" in model else
            8192
        )

        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.3,  # Lower = more deterministic, fewer retries
            max_tokens=max_tokens,
        )

        result = response.choices[0].message.content or ""
        usage = getattr(response, "usage", None)
        prompt_tokens = int(getattr(usage, "prompt_tokens", 0) or 0)
        completion_tokens = int(getattr(usage, "completion_tokens", 0) or 0)

        self.token_counter.record(
            agent=agent_name,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
        )

        if use_cache:
            self.cache[cache_key] = result

        logger.info(
            f"[{agent_name}] LLM call | model={model} | in={prompt_tokens} out={completion_tokens} tokens"
        )
        return result

    def compress_context(self, long_text: str, max_tokens: int = 800) -> str:
        """
        Summarize long context before passing to the next agent.
        (We approximate token budget via the prompt constraint.)
        """
        prompt = (
            f"Summarize the following in under {max_tokens} tokens, "
            f"preserving all technical details, decisions, and file names:\n\n{long_text}"
        )
        compressor_model = "openai/gpt-3.5-turbo" if self.using_openrouter else "gpt-3.5-turbo"
        return self.call(
            prompt=prompt,
            agent_name="context_compressor",
            force_model=compressor_model,
            use_cache=True,
        )

    def get_usage_report(self) -> dict:
        return self.token_counter.get_report()

