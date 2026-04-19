from __future__ import annotations

from app.llm.base import LLMClient
from app.modules.base import PipelineModule
from app.prompts.module_prompts import build_voice_user_prompt, load_voice_system_prompt
from app.schemas.models import ChannelBrief, SFXCue, ScriptArtifact, VoiceoverArtifact, VoiceoverSegment
from app.utils.artifact_store import LLMStageArtifacts
from app.utils.validator import validate_with_repair


class VoiceoverModule(PipelineModule):
    name = "voiceover"
    output_filename = "05_voiceover.json"

    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self.llm_client = llm_client
        self.last_llm_artifacts: LLMStageArtifacts | None = None

    def run(self, **kwargs) -> VoiceoverArtifact:
        brief: ChannelBrief = kwargs["brief"]
        script: ScriptArtifact = kwargs["script"]

        if self.llm_client is not None:
            system_prompt = load_voice_system_prompt()
            payload = self.llm_client.generate_structured(
                build_voice_user_prompt(brief=brief, script=script),
                system_prompt=system_prompt,
                schema=VoiceoverArtifact.model_json_schema(),
                schema_name="voiceover_artifact",
            )
            validated = validate_with_repair(
                payload=payload,
                model=VoiceoverArtifact,
                llm_client=self.llm_client,
                repair_context=(
                    "The output must be a valid voiceover package with voice style, music direction, "
                    "sfx cues, and voiceover segments aligned to script segment ids."
                ),
                schema_name="voiceover_artifact_repair",
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
            return validated

        voiceover_segments = []
        for seg in script.segments:
            pace = "fast" if seg.start_sec < 120 else "medium"
            duration = max(seg.end_sec - seg.start_sec, 1)
            voiceover_segments.append(
                VoiceoverSegment(
                    segment_id=seg.segment_id,
                    vo_text=f"{seg.spoken_script}",
                    emotion=seg.emotion,
                    pace=pace,
                    emphasis_words=seg.spoken_script.split()[:4],
                    breath_points=[max(duration // 3, 1), max((2 * duration) // 3, 1)],
                    timing_notes="Keep phrasing punchy; land final clause before next visual beat.",
                )
            )

        return VoiceoverArtifact(
            voice_style=f"{brief.tone} with clean conversational delivery",
            music_direction="modern cinematic pulse with subtle tech texture",
            sfx_cues=[
                SFXCue(time_sec=3, cue="subtle impact hit", purpose="signal opening hook"),
                SFXCue(time_sec=120, cue="short riser", purpose="mark first re-engagement"),
                SFXCue(time_sec=script.cta.time_sec, cue="resolve swell", purpose="support closing CTA"),
            ],
            voiceover_segments=voiceover_segments,
        )
