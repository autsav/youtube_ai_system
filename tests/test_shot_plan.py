from __future__ import annotations

import json

import pytest

from app.llm.base import StructuredGenerationCapture
from app.modules.shot_planner_engine import ShotPlannerModule, build_production_summary
from app.modules.storyboard import StoryboardModule
from app.modules.script import ScriptModule
from app.schemas.models import (
    ChannelBrief,
    SelectedConcept,
    ShotPlanArtifact,
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


def test_shot_plan_schema_validation_accepts_valid_data():
    payload = {
        "estimated_total_shots": 15,
        "estimated_a_roll_shots": 5,
        "estimated_b_roll_shots": 3,
        "estimated_ai_shots": 4,
        "estimated_stock_shots": 3,
        "production_notes": ["Lock A-roll first", "Queue AI shots after timeline lock"],
        "timeline_blocks": [
            {
                "block_id": "block_01",
                "start_sec": 0,
                "end_sec": 120,
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
                "description": "Quick overlay",
                "intended_segment_id": "seg_01",
                "suggested_asset_type": "GRAPHIC",
                "why_it_helps": "reinforces hook",
            }
        ],
        "asset_requirements": [
            {
                "asset_id": "asset_001",
                "related_shot_id": "shot_001",
                "asset_type": "RECORDED_A_ROLL",
                "description": "Creator opening",
                "source_preference": "in-house",
                "status": "pending",
            }
        ],
    }
    artifact = ShotPlanArtifact.model_validate(payload)
    assert artifact.estimated_total_shots == 15
    assert len(artifact.timeline_blocks) == 1


def test_shot_plan_schema_validation_rejects_negative_shot_counts():
    invalid_payload = {
        "estimated_total_shots": -1,
        "estimated_a_roll_shots": 0,
        "estimated_b_roll_shots": 0,
        "estimated_ai_shots": 0,
        "estimated_stock_shots": 0,
        "production_notes": [],
        "timeline_blocks": [],
        "quick_broll_ideas": [],
        "asset_requirements": [],
    }
    with pytest.raises(ValueError):
        ShotPlanArtifact.model_validate(invalid_payload)


def test_shot_planner_module_with_mocked_llm_returns_structured_output():
    brief = _brief()
    selected = _selected_concept()
    script = ScriptModule(llm_client=None).run(brief=brief, selected_concept=selected)
    voiceover = _voice_payload(script)
    storyboard = StoryboardModule(llm_client=None).run(
        brief=brief, selected_concept=selected, script=script, voiceover=voiceover
    )

    shot_plan_payload = {
        "estimated_total_shots": 15,
        "estimated_a_roll_shots": 5,
        "estimated_b_roll_shots": 3,
        "estimated_ai_shots": 4,
        "estimated_stock_shots": 3,
        "production_notes": ["Lock A-roll first"],
        "timeline_blocks": [
            {
                "block_id": "block_01",
                "start_sec": 0,
                "end_sec": 120,
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
                "description": "Quick overlay",
                "intended_segment_id": "seg_01",
                "suggested_asset_type": "GRAPHIC",
                "why_it_helps": "reinforces hook",
            }
        ],
        "asset_requirements": [
            {
                "asset_id": "asset_001",
                "related_shot_id": "shot_001",
                "asset_type": "RECORDED_A_ROLL",
                "description": "Creator opening",
                "source_preference": "in-house",
                "status": "pending",
            }
        ],
    }

    llm = FakeLLM(shot_plan_payload)
    module = ShotPlannerModule(llm_client=llm)
    shot_plan = module.run(brief=brief, storyboard=storyboard)

    assert shot_plan.estimated_total_shots == 15
    assert shot_plan.estimated_a_roll_shots == 5
    assert llm.calls == 1
    assert module.last_llm_artifacts is not None


def test_shot_planner_module_fallback_mode_without_llm():
    brief = _brief()
    selected = _selected_concept()
    script = ScriptModule(llm_client=None).run(brief=brief, selected_concept=selected)
    voiceover = _voice_payload(script)
    storyboard = StoryboardModule(llm_client=None).run(
        brief=brief, selected_concept=selected, script=script, voiceover=voiceover
    )

    module = ShotPlannerModule(llm_client=None)
    shot_plan = module.run(brief=brief, storyboard=storyboard)

    assert shot_plan.estimated_total_shots > 0
    assert len(shot_plan.timeline_blocks) == len(storyboard.segments)
    assert len(shot_plan.asset_requirements) == shot_plan.estimated_total_shots
    assert module.last_llm_artifacts is None


def test_build_production_summary_from_shot_plan():
    brief = _brief()
    selected = _selected_concept()
    script = ScriptModule(llm_client=None).run(brief=brief, selected_concept=selected)
    voiceover = _voice_payload(script)
    storyboard = StoryboardModule(llm_client=None).run(
        brief=brief, selected_concept=selected, script=script, voiceover=voiceover
    )
    shot_plan = ShotPlannerModule(llm_client=None).run(brief=brief, storyboard=storyboard)

    summary = build_production_summary(shot_plan=shot_plan)

    assert summary.total_assets == shot_plan.estimated_total_shots
    assert summary.required_assets > 0
    assert len(summary.high_priority_actions) >= 1
    assert len(summary.production_risks) >= 1
