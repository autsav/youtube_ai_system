from __future__ import annotations

import json

import pytest

from app.llm.base import StructuredGenerationCapture
from app.modules.script import ScriptModule
from app.schemas.models import ChannelBrief, ScriptArtifact, SelectedConcept, VideoConcept




class FakeScriptLLM:
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




def test_script_schema_validation_rejects_overlap():
    invalid_payload = {
        "video_title": "Bad timeline",
        "target_length_min": 10,
        "hook": {
            "start_sec": 0,
            "end_sec": 20,
            "spoken_words": "Hook line",
            "hook_type": "curiosity",
        },
        "segments": [
            {
                "segment_id": "seg_01",
                "start_sec": 0,
                "end_sec": 60,
                "purpose": "intro",
                "spoken_script": "Intro",
                "retention_device": "gap",
                "emotion": "curious",
                "visual_intent": "intro visuals",
                "drop_risk": "low",
                "why_viewer_stays": "Promise",
            },
            {
                "segment_id": "seg_02",
                "start_sec": 50,
                "end_sec": 120,
                "purpose": "body",
                "spoken_script": "Body",
                "retention_device": "challenge",
                "emotion": "tense",
                "visual_intent": "body visuals",
                "drop_risk": "medium",
                "why_viewer_stays": "Conflict",
            },
        ],
        "mid_video_hooks": [{"time_sec": 70, "line": "reset", "purpose": "re-engage"}],
        "cta": {"time_sec": 580, "line": "Subscribe", "goal": "Subscribe"},
        "retention_summary": {
            "opening_strategy": "open strong",
            "reengagement_points": ["1:10 reset"],
            "payoff_strategy": "resolve clearly",
        },
    }

    with pytest.raises(ValueError):
        ScriptArtifact.model_validate(invalid_payload)


def test_script_module_with_mocked_llm_returns_structured_output():
    payload = {
        "video_title": "Title from LLM",
        "target_length_min": 10,
        "hook": {
            "start_sec": 0,
            "end_sec": 30,
            "spoken_words": "Hook from llm",
            "hook_type": "stakes",
        },
        "segments": [
            {
                "segment_id": "seg_01",
                "start_sec": 0,
                "end_sec": 120,
                "purpose": "hook",
                "spoken_script": "Hook from llm",
                "retention_device": "curiosity",
                "emotion": "high curiosity",
                "visual_intent": "fast montage",
                "drop_risk": "low",
                "why_viewer_stays": "Strong promise",
            },
            {
                "segment_id": "seg_02",
                "start_sec": 120,
                "end_sec": 600,
                "purpose": "payoff",
                "spoken_script": "Payoff details",
                "retention_device": "payoff reveal",
                "emotion": "resolution",
                "visual_intent": "results board",
                "drop_risk": "low",
                "why_viewer_stays": "Gets clear answer",
            },
        ],
        "mid_video_hooks": [{"time_sec": 240, "line": "Plot twist", "purpose": "re-engage"}],
        "cta": {"time_sec": 580, "line": "Subscribe", "goal": "Subscribe"},
        "retention_summary": {
            "opening_strategy": "Open with stakes",
            "reengagement_points": ["4:00 twist"],
            "payoff_strategy": "Deliver ranked recommendation",
        },
    }

    llm = FakeScriptLLM(payload)
    module = ScriptModule(llm_client=llm)

    script = module.run(brief=_brief(), selected_concept=_selected_concept())

    assert script.video_title == "Title from LLM"
    assert script.segments[0].segment_id == "seg_01"
    assert llm.calls == 1
    assert module.last_llm_artifacts is not None
