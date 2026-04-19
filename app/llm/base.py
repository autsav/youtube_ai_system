from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(slots=True)
class StructuredGenerationCapture:
    raw_text: str
    parsed_json: dict[str, Any]


class LLMClient(Protocol):
    @property
    def last_generation(self) -> StructuredGenerationCapture | None: ...

    def generate_text(self, prompt: str, *, system_prompt: str | None = None) -> str: ...

    def generate_structured(
        self,
        prompt: str,
        *,
        schema: dict[str, Any],
        system_prompt: str | None = None,
        schema_name: str = "structured_response",
    ) -> dict[str, Any]: ...
