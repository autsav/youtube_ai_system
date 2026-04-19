from __future__ import annotations

import json

import pytest

from app.llm.base import StructuredGenerationCapture
from app.modules.script import ScriptModule
from app.modules.shot_planner_engine import ShotPlannerModule
from app.modules.storyboard import StoryboardModule
from app.schemas.models import (
    ChannelBrief,
    SelectedConcept,
    StoryboardArtifact,
    VideoConcept,
    VoiceoverArtifact,
)


class FakeLLM:
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


def _voice_payload(script):
    return VoiceoverArtifact.model_validate(
        {
            "voice_style": "high-energy but analytical with clean conversational delivery",
            "music_direction": "modern cinematic pulse with subtle tech texture",
            "sfx_cues": [],
            "voiceover_segments": [
                {
                    "segment_id": seg.segment_id,
                    "vo_text": seg.spoken_script,
                    "emotion": seg.emotion,
                    "pace": "medium",
                    "emphasis_words": ["focus"],
                    "breath_points": [5],
                    "timing_notes": "notes",
                }
                for seg in script.segments
            ],
        }
    )


def test_storyboard_schema_validation_accepts_valid_data():
    payload = {
        "video_title": "Test Video",
        "style_direction": "cinematic documentary",
        "editing_rhythm": "fast open, controlled middle, strong finish",
        "energy_map": ["0-30s: high", "30-70%: oscillating", "final 30s: resolve"],
        "segments": [
            {
                "segment_id": "seg_01",
                "start_sec": 0,
                "end_sec": 45,
                "segment_goal": "hook",
                "emotional_beat": "curiosity",
                "visual_strategy": "fast montage",
                "attention_reset": "stakes reveal",
                "shots": [
                    {
                        "shot_id": "shot_001",
                        "start_sec": 0,
                        "end_sec": 15,
                        "duration_sec": 15.0,
                        "shot_type": "A_ROLL",
                        "camera_view": "medium",
                        "description": "Creator hook",
                        "subject": "creator",
                        "location": "studio",
                        "motion": "static",
                        "on_screen_text": "",
                        "transition_in": "hard cut",
                        "transition_out": "hard cut",
                        "sound_design": "room tone",
                        "asset_type": "RECORDED_A_ROLL",
                        "priority": "required",
                    }
                ],
            }
        ],
    }
    artifact = StoryboardArtifact.model_validate(payload)
    assert artifact.video_title == "Test Video"
    assert len(artifact.segments) == 1
    assert len(artifact.segments[0].shots) == 1


def test_storyboard_schema_validation_rejects_empty_segments():
    with pytest.raises(ValueError):
        StoryboardArtifact.model_validate(
            {
                "video_title": "A",
                "style_direction": "cinematic",
                "editing_rhythm": "fast",
                "energy_map": ["high"],
                "segments": [],
            }
        )


def test_storyboard_and_shot_plan_modules_with_mocked_llm():
    brief = _brief()
    selected = _selected_concept()
    script = ScriptModule().run(brief=brief, selected_concept=selected)
    voiceover = _voice_payload(script)

    storyboard_payload = {
        "video_title": script.video_title,
        "style_direction": brief.visual_style,
        "editing_rhythm": "fast open, steady middle, clear finish",
        "energy_map": ["high", "medium", "high"],
        "segments": [
            {
                "segment_id": script.segments[0].segment_id,
                "start_sec": script.segments[0].start_sec,
                "end_sec": script.segments[0].end_sec,
                "segment_goal": script.segments[0].purpose,
                "emotional_beat": script.segments[0].emotion,
                "visual_strategy": script.segments[0].visual_intent,
                "attention_reset": script.segments[0].retention_device,
                "shots": [
                    {
                        "shot_id": "shot_001",
                        "start_sec": script.segments[0].start_sec,
                        "end_sec": script.segments[0].end_sec,
                        "duration_sec": float(script.segments[0].end_sec - script.segments[0].start_sec),
                        "shot_type": "A_ROLL",
                        "camera_view": "medium",
                        "description": "Opening explanation",
                        "subject": "creator",
                        "location": "studio",
                        "motion": "static",
                        "on_screen_text": "",
                        "transition_in": "hard cut",
                        "transition_out": "hard cut",
                        "sound_design": "room tone",
                        "asset_type": "RECORDED_A_ROLL",
                        "priority": "required",
                    }
                ],
            }
        ],
    }
    shot_plan_payload = {
        "estimated_total_shots": 1,
        "estimated_a_roll_shots": 1,
        "estimated_b_roll_shots": 0,
        "estimated_ai_shots": 0,
        "estimated_stock_shots": 0,
        "production_notes": ["Lock intro first"],
        "timeline_blocks": [
            {
                "block_id": "block_01",
                "start_sec": 0,
                "end_sec": 45,
                "purpose": "hook",
                "pace": "fast",
                "visual_density": "high",
                "primary_assets": ["RECORDED_A_ROLL"],
                "notes": "Open strong",
            }
        ],
        "quick_broll_ideas": [
            {
                "idea_id": "idea_01",
                "description": "quick overlay",
                "intended_segment_id": script.segments[0].segment_id,
                "suggested_asset_type": "GRAPHIC",
                "why_it_helps": "reinforces hook",
            }
        ],
        "asset_requirements": [
            {
                "asset_id": "asset_001",
                "related_shot_id": "shot_001",
                "asset_type": "RECORDED_A_ROLL",
                "description": "Intro shot",
                "source_preference": "in-house",
                "status": "pending",
            }
        ],
    }

    storyboard_module = StoryboardModule(llm_client=FakeLLM(storyboard_payload))
    shot_planner_module = ShotPlannerModule(llm_client=FakeLLM(shot_plan_payload))

    storyboard = storyboard_module.run(
        brief=brief,
        selected_concept=selected,
        script=script,
        voiceover=voiceover,
    )
    shot_plan = shot_planner_module.run(brief=brief, storyboard=storyboard)

    assert storyboard.video_title == script.video_title
    assert storyboard_module.last_llm_artifacts is not None
    assert shot_plan.estimated_total_shots == 1
    assert shot_planner_module.last_llm_artifacts is not None
