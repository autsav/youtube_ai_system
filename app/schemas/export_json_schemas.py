from __future__ import annotations

from pathlib import Path
from app.schemas.models import (
    ChannelBrief,
    TrendReport,
    ConceptBatch,
    SelectedConcept,
    ConceptPackage,
    ScriptArtifact,
    VoiceoverArtifact,
    StoryboardArtifact,
    KlingArtifact,
    ThumbnailArtifact,
    MetadataArtifact,
    PublishPack,
    ScriptVoicePackage,
    FinalPackage,
)
from app.utils.io import write_json


SCHEMA_MODELS = {
    "channel_brief": ChannelBrief,
    "trend_report": TrendReport,
    "concept_batch": ConceptBatch,
    "selected_concept": SelectedConcept,
    "concept_package": ConceptPackage,
    "script_artifact": ScriptArtifact,
    "voiceover_artifact": VoiceoverArtifact,
    "storyboard_artifact": StoryboardArtifact,
    "kling_artifact": KlingArtifact,
    "thumbnail_artifact": ThumbnailArtifact,
    "metadata_artifact": MetadataArtifact,
    "publish_pack": PublishPack,
    "script_voice_package": ScriptVoicePackage,
    "final_package": FinalPackage,
}


def export_all(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, model in SCHEMA_MODELS.items():
        write_json(output_dir / f"{name}.schema.json", model.model_json_schema())


if __name__ == "__main__":
    export_all(Path("app/schemas/json"))
