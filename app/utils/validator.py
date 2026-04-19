from __future__ import annotations

from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError

from app.llm.base import LLMClient
from app.utils.json_tools import pretty_json

ModelT = TypeVar("ModelT", bound=BaseModel)

_REPAIR_SYSTEM_PROMPT = (
    "You repair invalid JSON so it matches the required schema exactly. "
    "Return only a corrected JSON object."
)


class StructuredValidationError(ValueError):
    def __init__(
        self,
        *,
        model_name: str,
        original_payload: Any,
        initial_error: ValidationError,
        repaired_payload: Any | None = None,
        repair_error: ValidationError | None = None,
    ) -> None:
        self.model_name = model_name
        self.original_payload = original_payload
        self.initial_error = initial_error
        self.repaired_payload = repaired_payload
        self.repair_error = repair_error
        message = f"Failed to validate structured output for {model_name}"
        if repair_error is not None:
            message += " after one repair attempt"
        super().__init__(message)


def validate_with_repair(
    *,
    payload: Any,
    model: type[ModelT],
    llm_client: LLMClient,
    repair_context: str,
    system_prompt: str | None = None,
    schema_name: str | None = None,
) -> ModelT:
    try:
        return model.model_validate(payload)
    except ValidationError as initial_error:
        repaired_payload = llm_client.generate_structured(
            build_repair_prompt(
                payload=payload,
                model=model,
                validation_error=initial_error,
                repair_context=repair_context,
            ),
            schema=model.model_json_schema(),
            schema_name=schema_name or f"{model.__name__.lower()}_repair",
            system_prompt=system_prompt or _REPAIR_SYSTEM_PROMPT,
        )
        try:
            return model.model_validate(repaired_payload)
        except ValidationError as repair_error:
            raise StructuredValidationError(
                model_name=model.__name__,
                original_payload=payload,
                initial_error=initial_error,
                repaired_payload=repaired_payload,
                repair_error=repair_error,
            ) from repair_error


def build_repair_prompt(
    *,
    payload: Any,
    model: type[BaseModel],
    validation_error: ValidationError,
    repair_context: str,
) -> str:
    return "\n\n".join(
        [
            f"Repair this invalid JSON object for the {model.__name__} schema.",
            repair_context,
            "Validation errors:",
            pretty_json(validation_error.errors(include_url=False)),
            "Required JSON Schema:",
            pretty_json(model.model_json_schema()),
            "Invalid JSON object:",
            pretty_json(payload),
        ]
    )
