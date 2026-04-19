from __future__ import annotations

from app.modules.base import PipelineModule
from app.schemas.models import ScriptArtifact, StoryboardArtifact, StoryboardSegment, Shot


class StoryboardModule(PipelineModule):
    name = "storyboard"
    output_filename = "06_storyboard.json"

    def run(self, **kwargs) -> StoryboardArtifact:
        script: ScriptArtifact = kwargs["script"]
        segments: list[StoryboardSegment] = []
        shot_counter = 1
        for seg in script.segments:
            shots = [
                Shot(
                    shot_id=f"shot_{shot_counter:03d}",
                    duration_sec=4.0,
                    type="A-roll",
                    description=f"Creator on camera introducing {seg.purpose}",
                    on_screen_text=seg.purpose.title(),
                    transition="hard cut",
                    sound_design="room tone + subtle hit",
                ),
                Shot(
                    shot_id=f"shot_{shot_counter+1:03d}",
                    duration_sec=3.0,
                    type="AI_BROLL",
                    description=f"Cinematic b-roll visualizing {seg.purpose} in a clean tech documentary style",
                    on_screen_text="",
                    transition="zoom cut",
                    sound_design="whoosh",
                ),
                Shot(
                    shot_id=f"shot_{shot_counter+2:03d}",
                    duration_sec=3.0,
                    type="SCREEN_CAPTURE",
                    description="Screen capture of tools, metrics, or workflow details",
                    on_screen_text="Proof / Metrics",
                    transition="match cut",
                    sound_design="UI clicks",
                ),
            ]
            segments.append(StoryboardSegment(segment_id=seg.segment_id, shots=shots))
            shot_counter += 3

        total = sum(len(s.shots) for s in segments)
        return StoryboardArtifact(
            segments=segments,
            estimated_total_shots=total,
            editing_rhythm={
                "intro": "fast",
                "middle": "medium-fast",
                "payoff": "medium",
            },
        )
