from __future__ import annotations

from app.modules.base import PipelineModule
from app.schemas.models import StoryboardArtifact, KlingArtifact, KlingJob


class KlingModule(PipelineModule):
    name = "kling"
    output_filename = "07_kling_jobs.json"

    def run(self, **kwargs) -> KlingArtifact:
        storyboard: StoryboardArtifact = kwargs["storyboard"]
        jobs: list[KlingJob] = []
        for seg in storyboard.segments:
            for shot in seg.shots:
                if shot.shot_type != "AI_BROLL":
                    continue
                jobs.append(
                    KlingJob(
                        shot_id=shot.shot_id,
                        prompt=(
                            "Cinematic 1080p 30fps sequence, clean documentary tech aesthetic, "
                            f"{shot.description}, dynamic push-in camera, realistic motion physics, "
                            "soft directional contrast lighting, no face morphing, no artifacts, no uncanny motion"
                        ),
                        duration_sec=shot.duration_sec,
                        start_frame_guide="Enter mid-motion with visual energy already present.",
                        end_frame_guide="Land on a clear readable detail that can cut into the next shot.",
                        audio_suggestion="soft whoosh, interface taps, low cinematic pulse",
                    )
                )
        return KlingArtifact(kling_jobs=jobs)
