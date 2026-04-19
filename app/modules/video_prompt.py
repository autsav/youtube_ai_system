from __future__ import annotations

import json
from pathlib import Path

from app.llm.base import LLMClient
from app.modules.base import PipelineModule
from app.prompts.module_prompts import build_video_prompt_user_prompt, load_video_prompt_system_prompt
from app.schemas.models import (
    ChannelBrief,
    GlobalVisualRules,
    ScenePrompt,
    ScriptArtifact,
    ScriptSegment,
    SelectedConcept,
    VideoPromptArtifact,
)
from app.utils.artifact_store import LLMStageArtifacts
from app.utils.io import ensure_dir, write_json
from app.utils.validator import validate_with_repair


class VideoPromptModule(PipelineModule):
    """Generate structured video prompts from script for AI video generation."""

    name = "video_prompt"
    output_dirname = "video_prompts"
    output_filename = "05_video_prompts.json"  # Legacy root-level filename

    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self.llm_client = llm_client
        self.last_llm_artifacts: LLMStageArtifacts | None = None

    def _ensure_segment_coverage(
        self,
        scene_prompts: list[ScenePrompt],
        script_segments: list[ScriptSegment],
        brief: ChannelBrief,
    ) -> list[ScenePrompt]:
        """Ensure every script segment has at least one scene. Generate fallback scenes for missing segments."""
        segment_ids = {seg.segment_id for seg in script_segments}
        covered_segments = {scene.related_segment_id for scene in scene_prompts}
        missing = segment_ids - covered_segments

        if not missing:
            return scene_prompts

        # Generate fallback scenes for missing segments
        existing_ids = {s.scene_id for s in scene_prompts}
        scene_counter = len(scene_prompts) + 1
        new_scenes: list[ScenePrompt] = []

        # Map segments by ID for lookup
        segment_map = {seg.segment_id: seg for seg in script_segments}

        for seg_id in sorted(missing):
            segment = segment_map[seg_id]

            # Generate unique scene_id
            while f"scene_{scene_counter:03d}" in existing_ids:
                scene_counter += 1
            scene_id = f"scene_{scene_counter:03d}"
            existing_ids.add(scene_id)

            scene = ScenePrompt(
                scene_id=scene_id,
                related_segment_id=segment.segment_id,
                start_sec=float(segment.start_sec),
                end_sec=float(segment.end_sec),
                scene_goal=f"Cover {segment.purpose}",
                prompt=f"{segment.visual_intent}, {brief.visual_style} aesthetic. {segment.emotion} mood.",
                camera_direction="Medium shot, stable framing",
                lighting="Natural cinematic lighting",
                action=f"Visual supporting {segment.retention_device}",
                environment=f"Contextual setting for {brief.niche}",
                negative_prompt="amateur, poorly lit, distracting",
                audio_suggestion=f"Music supporting {segment.emotion} tone",
                priority="recommended",
                transition_in="hard cut",
                transition_out="hard cut",
                subject_description="Contextual visuals matching narration",
                continuity_notes=f"Maintain {segment.emotion} tone",
            )
            new_scenes.append(scene)
            scene_counter += 1

        # Combine and sort by start_sec
        combined = scene_prompts + new_scenes
        combined.sort(key=lambda s: s.start_sec)
        return combined

    def _write_artifacts(
        self,
        output_dir: Path,
        raw_text: str | None,
        parsed_json: dict,
        validated: VideoPromptArtifact,
    ) -> None:
        """Write raw, parsed, and validated artifacts to video_prompts directory."""
        artifact_dir = output_dir / self.output_dirname
        ensure_dir(artifact_dir)

        # Raw LLM output
        if raw_text is not None:
            (artifact_dir / "video_prompts_raw.txt").write_text(raw_text, encoding="utf-8")

        # Parsed JSON
        write_json(artifact_dir / "video_prompts_parsed.json", parsed_json)

        # Validated model
        write_json(artifact_dir / "video_prompts_validated.json", validated.model_dump(mode="json"))

    def run(
        self,
        *,
        brief: ChannelBrief,
        selected_concept: SelectedConcept,
        script: ScriptArtifact,
        output_dir: Path | None = None,
    ) -> VideoPromptArtifact:
        """Return schema-validated video prompts based on script segments."""
        system_prompt = load_video_prompt_system_prompt()
        user_prompt = build_video_prompt_user_prompt(
            brief=brief,
            selected_concept=selected_concept,
            script=script,
        )

        if self.llm_client is not None:
            # Generate with structured output
            payload = self.llm_client.generate_structured(
                user_prompt,
                system_prompt=system_prompt,
                schema=VideoPromptArtifact.model_json_schema(),
                schema_name="video_prompt_package",
            )

            # Capture raw output
            capture = self.llm_client.last_generation
            raw_text = capture.raw_text if capture else json.dumps(payload, ensure_ascii=False)

            # Validate with repair
            validated = validate_with_repair(
                payload=payload,
                model=VideoPromptArtifact,
                llm_client=self.llm_client,
                repair_context="""
                    The output must be a valid VideoPromptPackage with:
                    - GlobalVisualRules (aspect_ratio, quality_target, frame_rate, visual_style, continuity_notes)
                    - ScenePrompts sorted by start_sec with unique scene_ids
                    - Each scene covering timing, camera, lighting, action, environment, negative_prompt, audio_suggestion
                    - Priority must be "required", "recommended", or "optional"
                    - end_sec must be greater than start_sec for all scenes
                """,
                schema_name="video_prompt_package_repair",
                system_prompt=system_prompt,
            )

            # Track artifacts
            self.last_llm_artifacts = LLMStageArtifacts(
                stage_name=self.name,
                raw_text=raw_text,
                parsed_json=payload,
                validated_model=validated,
            )

            # Ensure segment coverage (generate fallback scenes if needed)
            validated.scene_prompts = self._ensure_segment_coverage(
                validated.scene_prompts, script.segments, brief
            )

            # Write artifacts if output_dir provided
            if output_dir is not None:
                self._write_artifacts(output_dir, raw_text, payload, validated)

            return validated

        # Fallback mode: generate deterministic video prompts from script
        scene_prompts: list[ScenePrompt] = []
        scene_counter = 1

        for segment in script.segments:
            seg_duration = segment.end_sec - segment.start_sec

            # Hook segment gets 2 scenes
            if segment.segment_id == "seg_01":
                scenes = [
                    ScenePrompt(
                        scene_id=f"scene_{scene_counter:03d}",
                        related_segment_id=segment.segment_id,
                        start_sec=float(segment.start_sec),
                        end_sec=float(segment.start_sec + max(seg_duration // 2, 5)),
                        scene_goal=f"Establish {segment.purpose}",
                        prompt=f"Cinematic wide shot of creator in modern studio, confident posture, shallow depth of field. {brief.visual_style} aesthetic.",
                        camera_direction="Wide establishing shot, slow push-in",
                        lighting="Soft key light with rim lighting, high contrast",
                        action="Creator steps forward, gestures toward camera",
                        environment=f"Clean studio space with {brief.niche} themed background",
                        negative_prompt="blurry, low quality, amateur, shaky, poor lighting",
                        audio_suggestion="Uplifting cinematic score with subtle ambience",
                        priority="required",
                        transition_in="fade in",
                        transition_out="match cut",
                        subject_description=f"Creator, professional attire, {brief.tone} energy",
                        continuity_notes="Establish visual tone for entire video",
                    ),
                    ScenePrompt(
                        scene_id=f"scene_{scene_counter + 1:03d}",
                        related_segment_id=segment.segment_id,
                        start_sec=float(segment.start_sec + max(seg_duration // 2, 5)),
                        end_sec=float(segment.end_sec),
                        scene_goal="Intense hook delivery",
                        prompt=f"Medium close-up creator face, intense eye contact, {brief.visual_style} grading. Emotional intensity matching '{segment.emotion}'.",
                        camera_direction="Medium close-up, slight handheld texture",
                        lighting="Dramatic side lighting, high contrast",
                        action="Creator delivers hook line with precise hand gesture",
                        environment="Same studio, tighter framing",
                        negative_prompt="flat lighting, boring composition, static",
                        audio_suggestion="Beat drop, silence for impact",
                        priority="required",
                        transition_in="match cut",
                        transition_out="hard cut",
                        subject_description="Creator face, expressive, engaged",
                        continuity_notes="Match eyeline from previous shot",
                    ),
                ]
            # Payoff segments get 1 strong scene
            elif "payoff" in segment.purpose.lower():
                scenes = [
                    ScenePrompt(
                        scene_id=f"scene_{scene_counter:03d}",
                        related_segment_id=segment.segment_id,
                        start_sec=float(segment.start_sec),
                        end_sec=float(segment.end_sec),
                        scene_goal=f"Deliver {segment.purpose}",
                        prompt=f"Hero shot of final result, cinematic lighting, {brief.visual_style} aesthetic. Satisfying resolution imagery.",
                        camera_direction="Dramatic low angle or product hero shot",
                        lighting="Cinematic three-point lighting, warm tones",
                        action="Slow reveal of final outcome",
                        environment="Clean, aspirational setting",
                        negative_prompt="cluttered, messy, unprofessional",
                        audio_suggestion="Triumphant resolution score",
                        priority="required",
                        transition_in="fade up",
                        transition_out="fade out",
                        subject_description="Final result, achievement, product",
                        continuity_notes="Visual payoff matching hook promise",
                    ),
                ]
            else:
                # Standard segment gets 1 scene
                scenes = [
                    ScenePrompt(
                        scene_id=f"scene_{scene_counter:03d}",
                        related_segment_id=segment.segment_id,
                        start_sec=float(segment.start_sec),
                        end_sec=float(segment.end_sec),
                        scene_goal=segment.purpose,
                        prompt=f"{segment.visual_intent}, {brief.visual_style} aesthetic. {segment.emotion} mood with appropriate lighting.",
                        camera_direction="Medium shot, stable framing",
                        lighting="Natural cinematic lighting",
                        action=f"Visual supporting {segment.retention_device}",
                        environment=f"Contextual setting for {brief.niche}",
                        negative_prompt="amateur, poorly lit, distracting",
                        audio_suggestion=f"Music supporting {segment.emotion} tone",
                        priority="recommended",
                        transition_in="hard cut",
                        transition_out="hard cut",
                        subject_description="Contextual visuals matching narration",
                        continuity_notes=f"Maintain {segment.emotion} tone",
                    ),
                ]

            scene_prompts.extend(scenes)
            scene_counter += len(scenes)

        # Ensure segment coverage
        scene_prompts = self._ensure_segment_coverage(scene_prompts, script.segments, brief)

        validated = VideoPromptArtifact(
            video_title=script.video_title,
            style_direction=brief.visual_style,
            global_visual_rules=GlobalVisualRules(
                aspect_ratio="16:9",
                quality_target="4K cinematic",
                frame_rate="24fps",
                visual_style=brief.visual_style,
                continuity_notes=f"Maintain consistent {brief.visual_style} aesthetic throughout.",
            ),
            scene_prompts=scene_prompts,
        )

        # Write artifacts if output_dir provided
        if output_dir is not None:
            raw_text = json.dumps(validated.model_dump(mode="json"), indent=2)
            self._write_artifacts(
                output_dir,
                raw_text,
                validated.model_dump(mode="json"),
                validated,
            )

        return validated

    def save(self, output_dir: Path, artifact: VideoPromptArtifact) -> Path:
        """Save validated artifact to output directory (root level for backwards compatibility)."""
        path = output_dir / self.output_filename
        write_json(path, artifact.model_dump(mode="json"))
        return path
