from __future__ import annotations

from app.modules.base import PipelineModule
from app.schemas.models import ScriptArtifact, SelectedConcept, MetadataArtifact, Chapter


class MetadataModule(PipelineModule):
    name = "metadata"
    output_filename = "09_metadata.json"

    def run(self, **kwargs) -> MetadataArtifact:
        script: ScriptArtifact = kwargs["script"]
        selected: SelectedConcept = kwargs["selected_concept"]
        chapters = [Chapter(time="00:00", label="Hook")]
        for seg in script.segments[1:]:
            minutes = seg.start_sec // 60
            seconds = seg.start_sec % 60
            chapters.append(Chapter(time=f"{minutes:02d}:{seconds:02d}", label=seg.purpose.title()))
        return MetadataArtifact(
            final_title=selected.winner.title_options[0],
            description=(
                f"In this video, I test a real {selected.winner.format} format around {selected.winner.premise} "
                "and break down what actually worked, what failed, and what I would do next."
            ),
            tags=[
                "youtube strategy",
                "content system",
                "ai workflow",
                "creator workflow",
            ],
            chapters=chapters,
        )
