from __future__ import annotations

import json

import pytest

from app.llm.base import StructuredGenerationCapture
from app.modules.script import ScriptModule
from app.modules.voice import VoiceoverModule
from app.schemas.models import ChannelBrief, SelectedConcept, VideoConcept, VoiceoverArtifact


class FakeVoiceLLM:
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
        title_options=[
            "Can I Build a Full AI tools System in 24 Hours?",
            "I Gave Myself 24 Hours to Fix My AI tools Workflow",
            "A 1-Day AI tools Challenge With Real Stakes",
        ],
        premise="A time-boxed challenge with visible stakes and payoff for tech-savvy freelancers.",
        hook_script="I gave myself just 24 hours to build a complete system, and if it failed, the whole video fell apart.",
        thumbnail_seed="countdown timer, stressed face, half-built system",
        predicted_ctr_range="8-12%",
        predicted_avd_range="40-52%",
        why_it_should_work="Urgency and challenge structure create strong momentum.",
    )
    return SelectedConcept(
        winner_id=winner.concept_id,
        winner=winner,
        weights={},
        score_breakdown={},
        scores={winner.concept_id: 7.0},
        winner_reason="Highest total score.",
    )


def test_voiceover_schema_validation_rejects_missing_timing_notes():
    invalid_payload = {
        "voice_style": "clean creator delivery",
        "music_direction": "cinematic pulse",
        "sfx_cues": [{"time_sec": 3, "cue": "hit", "purpose": "open"}],
        "voiceover_segments": [
            {
                "segment_id": "seg_01",
                "vo_text": "Hook line",
                "emotion": "curious",
                "pace": "fast",
                "emphasis_words": ["Hook"],
                "breath_points": [6],
            }
        ],
    }

    with pytest.raises(ValueError):
        VoiceoverArtifact.model_validate(invalid_payload)


def test_voiceover_module_with_mocked_llm_returns_structured_output():
    script = ScriptModule().run(brief=_brief(), selected_concept=_selected_concept())
    payload = {
        "voice_style": "high-energy but analytical with clean conversational delivery",
        "music_direction": "modern cinematic pulse with subtle tech texture",
        "sfx_cues": [
            {"time_sec": 3, "cue": "subtle impact hit", "purpose": "signal opening hook"},
            {"time_sec": 120, "cue": "short riser", "purpose": "mark first re-engagement"},
        ],
        "voiceover_segments": [
            {
                "segment_id": script.segments[0].segment_id,
                "vo_text": script.segments[0].spoken_script,
                "emotion": script.segments[0].emotion,
                "pace": "fast",
                "emphasis_words": ["24", "hours", "failed"],
                "breath_points": [8, 16],
                "timing_notes": "Punch the first clause.",
            },
            {
                "segment_id": script.segments[1].segment_id,
                "vo_text": script.segments[1].spoken_script,
                "emotion": script.segments[1].emotion,
                "pace": "medium",
                "emphasis_words": ["rules", "success"],
                "breath_points": [15, 30],
                "timing_notes": "Keep a steady cadence.",
            },
        ],
    }

    llm = FakeVoiceLLM(payload)
    module = VoiceoverModule(llm_client=llm)

    artifact = module.run(brief=_brief(), script=script)

    assert artifact.voice_style.startswith("high-energy")
    assert artifact.voiceover_segments[0].segment_id == script.segments[0].segment_id
    assert llm.calls == 1
    assert module.last_llm_artifacts is not None
