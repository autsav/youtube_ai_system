from __future__ import annotations

import json

import pytest

from app.llm.base import StructuredGenerationCapture
from app.modules.video_prompt import VideoPromptModule
from app.modules.script import ScriptModule
from app.schemas.models import (
    ChannelBrief,
    GlobalVisualRules,
    ScenePrompt,
    SelectedConcept,
    VideoPromptArtifact,
    VideoConcept,
)


class FakeVideoPromptLLM:
    def __init__(self, payload: dict) -> None:
        self.payload = payload
        self.calls = 0
        self._last_generation: StructuredGenerationCapture | None = None

    @property
    def last_generation(self):
        return self._last_generation

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
        self._last_generation = StructuredGenerationCapture(
            raw_text=json.dumps(self.payload),
            parsed_json=self.payload,
        )
        return self.payload


def _brief() -> ChannelBrief:
    return ChannelBrief.model_validate(
        {
            "channel_name": "Creator Systems Lab",
            "niche": "AI tools",
            "target_audience": "tech-savvy freelancers",
            "tone": "high-energy but analytical",
            "target_length_min": 10,
            "brand_colors": ["#00FF66", "#000000"],
            "format_preferences": ["experiment", "challenge"],
            "visual_style": "cinematic tech documentary",
            "cta_goal": "Subscribe and watch the next workflow breakdown.",
            "asset_preferences": {
                "stock_sites": ["Artgrid"],
                "ai_video_tool": "Kling 3.0",
                "editor": "Premiere Pro",
            },
        }
    )


def _selected_concept() -> SelectedConcept:
    winner = VideoConcept(
        concept_id="concept_03",
        format="challenge",
        title_options=["A", "B", "C"],
        premise="Premise",
        hook_script="Hook",
        thumbnail_seed="seed",
        predicted_ctr_range="8-12%",
        predicted_avd_range="40-52%",
        why_it_should_work="Reason",
    )
    return SelectedConcept(
        winner_id=winner.concept_id,
        winner=winner,
        weights={},
        score_breakdown={},
        scores={winner.concept_id: 7.0},
        winner_reason="Highest total score.",
    )


def test_video_prompt_schema_validation_accepts_valid_data():
    payload = {
        "video_title": "Test Video",
        "style_direction": "cinematic documentary",
        "global_visual_rules": {
            "aspect_ratio": "16:9",
            "quality_target": "4K cinematic",
            "frame_rate": "24fps",
            "visual_style": "cinematic tech documentary",
            "continuity_notes": "Maintain consistent lighting",
        },
        "scene_prompts": [
            {
                "scene_id": "scene_001",
                "related_segment_id": "seg_01",
                "start_sec": 0.0,
                "end_sec": 30.0,
                "scene_goal": "Hook the viewer",
                "prompt": "Cinematic wide shot of creator in studio",
                "camera_direction": "Wide establishing shot",
                "lighting": "Soft key light",
                "action": "Creator steps forward",
                "environment": "Modern studio",
                "negative_prompt": "blurry, low quality",
                "audio_suggestion": "Uplifting score",
                "priority": "required",
                "transition_in": "fade in",
                "transition_out": "hard cut",
                "subject_description": "Creator, professional",
                "continuity_notes": "Establish tone",
            }
        ],
    }
    artifact = VideoPromptArtifact.model_validate(payload)
    assert artifact.video_title == "Test Video"
    assert len(artifact.scene_prompts) == 1
    assert artifact.global_visual_rules.aspect_ratio == "16:9"
    # Check float timing
    assert artifact.scene_prompts[0].start_sec == 0.0
    assert isinstance(artifact.scene_prompts[0].start_sec, float)


def test_video_prompt_schema_validation_rejects_empty_scenes():
    invalid_payload = {
        "video_title": "Test",
        "style_direction": "cinematic",
        "global_visual_rules": {
            "aspect_ratio": "16:9",
            "quality_target": "4K",
            "frame_rate": "24fps",
            "visual_style": "cinematic",
            "continuity_notes": "notes",
        },
        "scene_prompts": [],
    }
    with pytest.raises(ValueError):
        VideoPromptArtifact.model_validate(invalid_payload)


def test_video_prompt_schema_validation_rejects_invalid_timing():
    """Test that end_sec <= start_sec is rejected."""
    invalid_payload = {
        "video_title": "Test",
        "style_direction": "cinematic",
        "global_visual_rules": {
            "aspect_ratio": "16:9",
            "quality_target": "4K",
            "frame_rate": "24fps",
            "visual_style": "cinematic",
            "continuity_notes": "notes",
        },
        "scene_prompts": [
            {
                "scene_id": "scene_001",
                "related_segment_id": "seg_01",
                "start_sec": 30.0,
                "end_sec": 10.0,  # Invalid: end <= start
                "scene_goal": "Test",
                "prompt": "Test prompt",
                "camera_direction": "Wide shot",
                "lighting": "Natural",
                "action": "Test",
                "environment": "Studio",
                "negative_prompt": "blurry",
                "audio_suggestion": "Music",
                "priority": "required",
            }
        ],
    }
    with pytest.raises(ValueError):
        VideoPromptArtifact.model_validate(invalid_payload)


def test_video_prompt_schema_validation_rejects_duplicate_scene_ids():
    """Test that duplicate scene_ids are rejected."""
    invalid_payload = {
        "video_title": "Test",
        "style_direction": "cinematic",
        "global_visual_rules": {
            "aspect_ratio": "16:9",
            "quality_target": "4K",
            "frame_rate": "24fps",
            "visual_style": "cinematic",
            "continuity_notes": "notes",
        },
        "scene_prompts": [
            {
                "scene_id": "scene_001",  # Duplicate
                "related_segment_id": "seg_01",
                "start_sec": 0.0,
                "end_sec": 10.0,
                "scene_goal": "Test",
                "prompt": "Test prompt",
                "camera_direction": "Wide shot",
                "lighting": "Natural",
                "action": "Test",
                "environment": "Studio",
                "negative_prompt": "blurry",
                "audio_suggestion": "Music",
                "priority": "required",
            },
            {
                "scene_id": "scene_001",  # Duplicate
                "related_segment_id": "seg_02",
                "start_sec": 10.0,
                "end_sec": 20.0,
                "scene_goal": "Test",
                "prompt": "Test prompt 2",
                "camera_direction": "Medium shot",
                "lighting": "Studio",
                "action": "Test",
                "environment": "Studio",
                "negative_prompt": "blurry",
                "audio_suggestion": "Music",
                "priority": "required",
            }
        ],
    }
    with pytest.raises(ValueError):
        VideoPromptArtifact.model_validate(invalid_payload)


def test_video_prompt_schema_validation_rejects_unsorted_scenes():
    """Test that scenes not sorted by start_sec are rejected."""
    invalid_payload = {
        "video_title": "Test",
        "style_direction": "cinematic",
        "global_visual_rules": {
            "aspect_ratio": "16:9",
            "quality_target": "4K",
            "frame_rate": "24fps",
            "visual_style": "cinematic",
            "continuity_notes": "notes",
        },
        "scene_prompts": [
            {
                "scene_id": "scene_001",
                "related_segment_id": "seg_02",
                "start_sec": 60.0,  # Starts later
                "end_sec": 90.0,
                "scene_goal": "Test",
                "prompt": "Test prompt",
                "camera_direction": "Wide shot",
                "lighting": "Natural",
                "action": "Test",
                "environment": "Studio",
                "negative_prompt": "blurry",
                "audio_suggestion": "Music",
                "priority": "required",
            },
            {
                "scene_id": "scene_002",
                "related_segment_id": "seg_01",
                "start_sec": 0.0,  # Starts earlier but comes second
                "end_sec": 30.0,
                "scene_goal": "Test",
                "prompt": "Test prompt 2",
                "camera_direction": "Medium shot",
                "lighting": "Studio",
                "action": "Test",
                "environment": "Studio",
                "negative_prompt": "blurry",
                "audio_suggestion": "Music",
                "priority": "required",
            }
        ],
    }
    with pytest.raises(ValueError):
        VideoPromptArtifact.model_validate(invalid_payload)


def _make_scene_dict(scene_id: str, segment_id: str, start_sec: float, end_sec: float) -> dict:
    """Helper to create a valid scene dict for testing."""
    return {
        "scene_id": scene_id,
        "related_segment_id": segment_id,
        "start_sec": start_sec,
        "end_sec": end_sec,
        "scene_goal": f"Scene for {segment_id}",
        "prompt": f"Cinematic shot for {segment_id}",
        "camera_direction": "Wide shot",
        "lighting": "Natural",
        "action": "Creator presents",
        "environment": "Studio",
        "negative_prompt": "blurry, low quality",
        "audio_suggestion": "Background music",
        "priority": "required",
        "transition_in": "fade in",
        "transition_out": "fade out",
        "subject_description": "Creator",
        "continuity_notes": "Maintain continuity",
    }


def test_video_prompt_module_with_mocked_llm_returns_structured_output():
    brief = _brief()
    selected = _selected_concept()
    script = ScriptModule(llm_client=None).run(brief=brief, selected_concept=selected)

    # Build scene prompts for all script segments
    scene_prompts = []
    scene_counter = 1
    for i, segment in enumerate(script.segments):
        scene_prompts.append(_make_scene_dict(
            scene_id=f"scene_{scene_counter:03d}",
            segment_id=segment.segment_id,
            start_sec=float(segment.start_sec),
            end_sec=float(segment.end_sec),
        ))
        scene_counter += 1

    video_prompt_payload = {
        "video_title": script.video_title,
        "style_direction": brief.visual_style,
        "global_visual_rules": {
            "aspect_ratio": "16:9",
            "quality_target": "4K cinematic",
            "frame_rate": "24fps",
            "visual_style": brief.visual_style,
            "continuity_notes": "Maintain consistent style",
        },
        "scene_prompts": scene_prompts,
    }

    llm = FakeVideoPromptLLM(video_prompt_payload)
    module = VideoPromptModule(llm_client=llm)
    video_prompts = module.run(brief=brief, selected_concept=selected, script=script, output_dir=None)

    assert video_prompts.video_title == script.video_title
    assert video_prompts.style_direction == brief.visual_style
    assert len(video_prompts.scene_prompts) == len(script.segments)
    assert video_prompts.global_visual_rules.aspect_ratio == "16:9"
    # Check float timing
    assert isinstance(video_prompts.scene_prompts[0].start_sec, float)
    assert llm.calls == 1
    assert module.last_llm_artifacts is not None


def test_video_prompt_module_fallback_mode_without_llm():
    brief = _brief()
    selected = _selected_concept()
    script = ScriptModule(llm_client=None).run(brief=brief, selected_concept=selected)

    module = VideoPromptModule(llm_client=None)
    video_prompts = module.run(brief=brief, selected_concept=selected, script=script, output_dir=None)

    assert video_prompts.video_title == script.video_title
    assert video_prompts.style_direction == brief.visual_style
    assert len(video_prompts.scene_prompts) > 0
    assert video_prompts.global_visual_rules is not None
    assert video_prompts.global_visual_rules.aspect_ratio == "16:9"
    assert module.last_llm_artifacts is None

    # Verify scenes are linked to segments
    segment_ids = {seg.segment_id for seg in script.segments}
    for scene in video_prompts.scene_prompts:
        assert scene.related_segment_id in segment_ids
        assert scene.scene_id.startswith("scene_")
        assert scene.prompt
        assert scene.camera_direction
        assert scene.lighting
        # Check float timing
        assert isinstance(scene.start_sec, float)
        assert isinstance(scene.end_sec, float)
        assert scene.end_sec > scene.start_sec

    # Verify all segments are covered
    covered_segments = {scene.related_segment_id for scene in video_prompts.scene_prompts}
    assert segment_ids == covered_segments


def test_global_visual_rules_schema():
    rules = GlobalVisualRules.model_validate({
        "aspect_ratio": "16:9",
        "quality_target": "4K cinematic",
        "frame_rate": "24fps",
        "visual_style": "cinematic documentary",
        "continuity_notes": "Maintain consistent lighting and color grading",
    })
    assert rules.aspect_ratio == "16:9"
    assert rules.quality_target == "4K cinematic"


def test_scene_prompt_schema():
    scene = ScenePrompt.model_validate({
        "scene_id": "scene_001",
        "related_segment_id": "seg_01",
        "start_sec": 0.0,
        "end_sec": 30.0,
        "scene_goal": "Hook viewer",
        "prompt": "Cinematic shot of creator",
        "camera_direction": "Wide shot",
        "lighting": "Natural",
        "action": "Creator speaks",
        "environment": "Studio",
        "negative_prompt": "blurry",
        "audio_suggestion": "Music",
        "priority": "required",
        "transition_in": "fade",
        "transition_out": "cut",
        "subject_description": "Creator",
        "continuity_notes": "Match eyeline",
    })
    assert scene.scene_id == "scene_001"
    assert scene.related_segment_id == "seg_01"
    assert scene.priority == "required"
    assert scene.start_sec == 0.0
    assert isinstance(scene.start_sec, float)


def test_scene_prompt_optional_fields():
    """Test that optional fields can be None."""
    scene = ScenePrompt.model_validate({
        "scene_id": "scene_001",
        "related_segment_id": "seg_01",
        "start_sec": 0.0,
        "end_sec": 30.0,
        "scene_goal": "Hook viewer",
        "prompt": "Cinematic shot",
        "camera_direction": "Wide shot",
        "lighting": "Natural",
        "action": "Creator speaks",
        "environment": "Studio",
        "negative_prompt": "blurry",
        "audio_suggestion": "Music",
        "priority": "required",
        # Optional fields omitted
    })
    assert scene.transition_in is None
    assert scene.transition_out is None
    assert scene.subject_description is None
    assert scene.continuity_notes is None
