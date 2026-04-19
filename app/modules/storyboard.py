from __future__ import annotations

import json

from app.llm.base import LLMClient
from app.modules.base import PipelineModule
from app.prompts.module_prompts import build_storyboard_user_prompt, load_storyboard_system_prompt
from app.schemas.models import (
    ChannelBrief,
    ScriptArtifact,
    SelectedConcept,
    StoryboardArtifact,
    StoryboardSegment,
    StoryboardShot,
    VoiceoverArtifact,
)
from app.utils.artifact_store import LLMStageArtifacts
from app.utils.validator import validate_with_repair


class StoryboardModule(PipelineModule):
    name = "storyboard"
    output_filename = "06_storyboard.json"

    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self.llm_client = llm_client
        self.last_llm_artifacts: LLMStageArtifacts | None = None

    def run(self, **kwargs) -> StoryboardArtifact:
        brief: ChannelBrief = kwargs["brief"]
        selected: SelectedConcept = kwargs["selected_concept"]
        script: ScriptArtifact = kwargs["script"]
        voiceover: VoiceoverArtifact = kwargs["voiceover"]

        if self.llm_client is not None:
            system_prompt = load_storyboard_system_prompt()
            payload = self.llm_client.generate_structured(
                build_storyboard_user_prompt(
                    brief=brief,
                    selected_concept=selected,
                    script=script,
                    voiceover=voiceover,
                ),
                system_prompt=system_prompt,
                schema=StoryboardArtifact.model_json_schema(),
                schema_name="storyboard_artifact",
            )
            validated = validate_with_repair(
                payload=payload,
                model=StoryboardArtifact,
                llm_client=self.llm_client,
                repair_context=(
                    "The output must be a valid storyboard package with segment-level visual strategy, "
                    "emotion, attention reset, and coherent timed shots with required production fields."
                ),
                schema_name="storyboard_artifact_repair",
                system_prompt=system_prompt,
            )
            capture = self.llm_client.last_generation
            if capture is not None:
                self.last_llm_artifacts = LLMStageArtifacts(
                    stage_name=self.name,
                    raw_text=capture.raw_text,
                    parsed_json=capture.parsed_json,
                    validated_model=validated,
                )
            else:
                self.last_llm_artifacts = LLMStageArtifacts(
                    stage_name=self.name,
                    raw_text=json.dumps(payload, ensure_ascii=False),
                    parsed_json=payload,
                    validated_model=validated,
                )
            return validated

        segments: list[StoryboardSegment] = []
        shot_counter = 1
        for seg in script.segments:
            seg_start = seg.start_sec
            seg_end = seg.end_sec
            seg_duration = max(seg_end - seg_start, 1)
            a_end = seg_start + max(seg_duration // 3, 1)
            b_end = a_end + max(seg_duration // 3, 1)
            shots = [
                StoryboardShot(
                    shot_id=f"shot_{shot_counter:03d}",
                    start_sec=seg_start,
                    end_sec=min(a_end, seg_end),
                    duration_sec=float(max(min(a_end, seg_end) - seg_start, 1)),
                    shot_type="A_ROLL",
                    camera_view="medium talking-head",
                    description=f"Creator delivers core point for {seg.purpose}",
                    subject="creator",
                    location="studio",
                    motion="static with slight push-in",
                    on_screen_text=seg.purpose.title(),
                    transition_in="hard cut",
                    transition_out="match cut",
                    sound_design="room tone + light impact",
                    asset_type="RECORDED_A_ROLL",
                    priority="required",
                ),
                StoryboardShot(
                    shot_id=f"shot_{shot_counter+1:03d}",
                    start_sec=min(a_end, seg_end),
                    end_sec=min(b_end, seg_end),
                    duration_sec=float(max(min(b_end, seg_end) - min(a_end, seg_end), 1)),
                    shot_type="AI_BROLL",
                    camera_view="dynamic cinematic",
                    description=f"Visual metaphor illustrating {seg.retention_device}",
                    subject="workflow metaphor",
                    location="abstract digital environment",
                    motion="slow parallax move",
                    on_screen_text="",
                    transition_in="match cut",
                    transition_out="zoom cut",
                    sound_design="subtle whoosh",
                    asset_type="AI_GENERATED",
                    priority="recommended",
                ),
                StoryboardShot(
                    shot_id=f"shot_{shot_counter+2:03d}",
                    start_sec=min(b_end, seg_end),
                    end_sec=seg_end,
                    duration_sec=float(max(seg_end - min(b_end, seg_end), 1)),
                    shot_type="SCREEN_CAPTURE",
                    camera_view="screen recording",
                    description="On-screen proof, metrics, or workflow evidence",
                    subject="tool interface",
                    location="desktop capture",
                    motion="cursor-guided movement",
                    on_screen_text="Proof / Metrics",
                    transition_in="zoom cut",
                    transition_out="hard cut",
                    sound_design="ui clicks",
                    asset_type="SCREEN_CAPTURE",
                    priority="required",
                ),
            ]
            segments.append(
                StoryboardSegment(
                    segment_id=seg.segment_id,
                    start_sec=seg.start_sec,
                    end_sec=seg.end_sec,
                    segment_goal=seg.purpose,
                    emotional_beat=seg.emotion,
                    visual_strategy=seg.visual_intent,
                    attention_reset=seg.retention_device,
                    shots=shots,
                )
            )
            shot_counter += 3

        return StoryboardArtifact(
            video_title=script.video_title,
            style_direction=brief.visual_style,
            editing_rhythm="fast open, controlled middle escalation, clear payoff finish",
            energy_map=["0-30s: high", "30-70%: oscillating", "final 30s: resolve"],
            segments=segments,
        )
