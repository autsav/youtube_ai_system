from __future__ import annotations

import time
from typing import Any

from openai import APIConnectionError, APITimeoutError, InternalServerError, OpenAI, RateLimitError

from app.llm.base import StructuredGenerationCapture
from app.llm.json_utils import parse_json_object


class OpenAIClient:
    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        timeout_seconds: float = 60.0,
        max_retries: int = 2,
        retry_backoff_seconds: float = 1.0,
    ) -> None:
        if not api_key:
            raise ValueError("OPENAI_API_KEY is missing or empty")

        self.model = model
        self.client = OpenAI(api_key=api_key, timeout=timeout_seconds)
        self.max_retries = max_retries
        self.retry_backoff_seconds = retry_backoff_seconds
        self._last_generation: StructuredGenerationCapture | None = None

    @property
    def last_generation(self) -> StructuredGenerationCapture | None:
        return self._last_generation

    def generate_text(self, prompt: str, *, system_prompt: str | None = None) -> str:
        response = self._with_retries(
            lambda: self.client.responses.create(
                model=self.model,
                instructions=system_prompt,
                input=prompt,
            )
        )
        return response.output_text

    def generate_structured(
        self,
        prompt: str,
        *,
        schema: dict[str, Any],
        system_prompt: str | None = None,
        schema_name: str = "structured_response",
    ) -> dict[str, Any]:
        try:
            response = self._with_retries(
                lambda: self.client.responses.create(
                    model=self.model,
                    instructions=system_prompt,
                    input=prompt,
                    text={
                        "format": {
                            "type": "json_schema",
                            "name": schema_name,
                            "schema": schema,
                            "strict": True,
                        }
                    },
                )
            )
            parsed = parse_json_object(response.output_text)
            self._last_generation = StructuredGenerationCapture(
                raw_text=response.output_text,
                parsed_json=parsed,
            )
            return parsed
        except ValueError:
            fallback_prompt = "\n\n".join(
                [
                    prompt,
                    "Return only one JSON object that matches this schema exactly.",
                    f"JSON Schema:\n{schema}",
                ]
            )
            raw_text = self.generate_text(fallback_prompt, system_prompt=system_prompt)
            parsed = parse_json_object(raw_text)
            self._last_generation = StructuredGenerationCapture(
                raw_text=raw_text,
                parsed_json=parsed,
            )
            return parsed

    def _with_retries(self, operation: Any) -> Any:
        last_error: Exception | None = None
        for attempt in range(self.max_retries + 1):
            try:
                return operation()
            except (APIConnectionError, APITimeoutError, InternalServerError, RateLimitError) as exc:
                last_error = exc
                if attempt >= self.max_retries:
                    break
                time.sleep(self.retry_backoff_seconds * (2**attempt))

        assert last_error is not None
        raise last_error
