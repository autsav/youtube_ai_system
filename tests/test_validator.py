from __future__ import annotations

import pytest

from app.schemas.models import ConceptBatch
from app.utils.validator import StructuredValidationError, validate_with_repair


class FakeRepairLLM:
    def __init__(self, repaired_payload):
        self.repaired_payload = repaired_payload
        self.calls = 0

    @property
    def last_generation(self):
        return None

    def generate_text(self, prompt: str, *, system_prompt: str | None = None) -> str:
        raise NotImplementedError

    def generate_structured(
        self,
        prompt: str,
        *,
        schema: dict,
        system_prompt: str | None = None,
        schema_name: str = "structured_response",
    ) -> dict:
        self.calls += 1
        return self.repaired_payload


def _concept(concept_id: str) -> dict:
    return {
        "concept_id": concept_id,
        "format": "experiment",
        "title_options": ["one", "two", "three"],
        "premise": "A premise with enough clarity for testing.",
        "hook_script": "I tested this under pressure and something broke.",
        "thumbnail_seed": "face, logos, metric",
        "predicted_ctr_range": "7-11%",
        "predicted_avd_range": "42-55%",
        "why_it_should_work": "Clear payoff and practical relevance make this compelling.",
    }


def test_validate_with_repair_repairs_once_and_returns_model():
    invalid_payload = {"concepts": [_concept("concept_01")]}
    repaired_payload = {"concepts": [_concept(f"concept_0{i}") for i in range(1, 6)]}
    llm = FakeRepairLLM(repaired_payload)

    result = validate_with_repair(
        payload=invalid_payload,
        model=ConceptBatch,
        llm_client=llm,
        repair_context="repair concept batch",
    )

    assert result.concepts[0].concept_id == "concept_01"
    assert len(result.concepts) == 5
    assert llm.calls == 1


def test_validate_with_repair_raises_structured_exception_if_repair_fails():
    invalid_payload = {"concepts": [_concept("concept_01")]}
    llm = FakeRepairLLM(invalid_payload)

    with pytest.raises(StructuredValidationError) as exc_info:
        validate_with_repair(
            payload=invalid_payload,
            model=ConceptBatch,
            llm_client=llm,
            repair_context="repair concept batch",
        )

    assert exc_info.value.model_name == "ConceptBatch"
    assert exc_info.value.repair_error is not None
    assert llm.calls == 1
