from __future__ import annotations

from app.modules.base import PipelineModule
from app.schemas.models import ThumbnailArtifact, ThumbnailVariant, SelectedConcept, ChannelBrief


class ThumbnailModule(PipelineModule):
    name = "thumbnail"
    output_filename = "08_thumbnails.json"

    def run(self, **kwargs) -> ThumbnailArtifact:
        brief: ChannelBrief = kwargs["brief"]
        selected: SelectedConcept = kwargs["selected_concept"]
        colors = ", ".join(brief.brand_colors)
        variants = [
            ThumbnailVariant(
                id="thumb_a",
                visual="shocked creator face, app logos, giant result metric",
                text="12 HOURS SAVED?",
                emotion="shock",
                predicted_ctr="9-12%",
                psychological_angle=f"Immediate measurable outcome with strong contrast in brand colors: {colors}.",
            ),
            ThumbnailVariant(
                id="thumb_b",
                visual="split-screen before versus after workflow chaos to control",
                text="AI DID THIS",
                emotion="disbelief",
                predicted_ctr="8-10%",
                psychological_angle="High-curiosity transformation frame with a simple headline.",
            ),
            ThumbnailVariant(
                id="thumb_c",
                visual="one tool isolated in the center with creator pointing at failure point",
                text="THIS BROKE IT",
                emotion="alarm",
                predicted_ctr="8-11%",
                psychological_angle="Conflict-driven framing pulls attention faster than neutral education thumbnails.",
            ),
        ]
        return ThumbnailArtifact(
            thumbnail_variants=variants,
            test_order=["thumb_a vs thumb_b", "winner vs thumb_c"],
        )
