from __future__ import annotations

from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()


class Settings(BaseModel):
    llm_mode: str = os.getenv("LLM_MODE", "mock")
    llm_model: str = os.getenv("LLM_MODEL", "gpt-5")
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    llm_timeout_seconds: float = float(os.getenv("LLM_TIMEOUT_SECONDS", "60"))
    llm_max_retries: int = int(os.getenv("LLM_MAX_RETRIES", "2"))
    llm_retry_backoff_seconds: float = float(os.getenv("LLM_RETRY_BACKOFF_SECONDS", "1"))
    output_root: Path = Path(os.getenv("OUTPUT_ROOT", "outputs"))


settings = Settings()
