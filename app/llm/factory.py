from __future__ import annotations

from app.config import Settings
from app.llm.base import LLMClient
from app.llm.openai_client import OpenAIClient


def create_llm_client(settings: Settings) -> LLMClient | None:
    if settings.llm_mode == "mock":
        return None

    if settings.llm_mode == "openai":
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when LLM_MODE=openai")
        return OpenAIClient(
            api_key=settings.openai_api_key,
            model=settings.llm_model,
            timeout_seconds=settings.llm_timeout_seconds,
            max_retries=settings.llm_max_retries,
            retry_backoff_seconds=settings.llm_retry_backoff_seconds,
        )

    raise ValueError(f"Unsupported LLM_MODE: {settings.llm_mode}")
