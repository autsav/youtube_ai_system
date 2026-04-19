from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from app.utils.io import ensure_dir, write_json


@dataclass(slots=True)
class LLMStageArtifacts:
    stage_name: str
    raw_text: str
    parsed_json: dict[str, Any]
    validated_model: BaseModel
    captured_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


def save_llm_stage_artifacts(output_dir: Path, artifacts: LLMStageArtifacts) -> dict[str, Path]:
    stage_dir = output_dir / "_artifacts" / artifacts.stage_name
    ensure_dir(stage_dir)

    timestamp = artifacts.captured_at.strftime("%Y%m%dT%H%M%SZ")
    snapshot_prefix = f"{timestamp}_{artifacts.stage_name}"
    latest_prefix = f"{artifacts.stage_name}.latest"

    raw_text = _prepend_timestamp(artifacts.raw_text, artifacts.captured_at)
    parsed_json = artifacts.parsed_json
    validated_json = artifacts.validated_model.model_dump(mode="json")

    snapshot_paths = {
        "raw_text": stage_dir / f"{snapshot_prefix}.raw.txt",
        "parsed_json": stage_dir / f"{snapshot_prefix}.parsed.json",
        "validated_model": stage_dir / f"{snapshot_prefix}.validated.json",
    }
    latest_paths = {
        "latest_raw_text": stage_dir / f"{latest_prefix}.raw.txt",
        "latest_parsed_json": stage_dir / f"{latest_prefix}.parsed.json",
        "latest_validated_model": stage_dir / f"{latest_prefix}.validated.json",
    }

    for path in (snapshot_paths["raw_text"], latest_paths["latest_raw_text"]):
        path.write_text(raw_text, encoding="utf-8")

    for path in (snapshot_paths["parsed_json"], latest_paths["latest_parsed_json"]):
        write_json(path, parsed_json)

    for path in (snapshot_paths["validated_model"], latest_paths["latest_validated_model"]):
        write_json(path, validated_json)

    return {**snapshot_paths, **latest_paths}


def _prepend_timestamp(raw_text: str, captured_at: datetime) -> str:
    timestamp = captured_at.astimezone(timezone.utc).isoformat()
    return f"# captured_at: {timestamp}\n\n{raw_text}"
