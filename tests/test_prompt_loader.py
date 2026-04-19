from __future__ import annotations

import pytest

from app.prompts.module_prompts import (
    build_shot_plan_user_prompt,
    build_storyboard_user_prompt,
    load_shot_plan_system_prompt,
    load_storyboard_system_prompt,
)
from app.schemas.models import (
    AssetPreferences,
    ChannelBrief,
    ScriptArtifact,
    ScriptCTA,
    ScriptHook,
    ScriptRetentionSummary,
    ScriptSegment,
    SelectedConcept,
    StoryboardArtifact,
    StoryboardSegment,
    StoryboardShot,
    VideoConcept,
    VoiceoverArtifact,
    VoiceoverSegment,
)
from app.utils.prompt_loader import PromptTemplateError, load_prompt_template


def test_load_prompt_template_interpolates_variables(tmp_path):
    template_path = tmp_path / "prompt.txt"
    template_path.write_text("Hello {name}\nTopic: {topic}\n", encoding="utf-8")

    rendered = load_prompt_template(template_path, name="Utsab", topic="AI tools")

    assert rendered == "Hello Utsab\nTopic: AI tools\n"




def test_storyboard_and_shot_plan_templates_load():
    brief = ChannelBrief(
        channel_name="Creator Lab",
        niche="AI tools",
        target_audience="builders",
        tone="high-energy",
        target_length_min=10,
        brand_colors=["#000", "#fff"],
        format_preferences=["challenge"],
        visual_style="cinematic",
        cta_goal="Subscribe",
        asset_preferences=AssetPreferences(stock_sites=["Artgrid"], ai_video_tool="Kling 3.0", editor="Premiere"),
    )
    concept = SelectedConcept(
        winner_id="concept_01",
        winner=VideoConcept(
            concept_id="concept_01",
            format="challenge",
            title_options=["A", "B", "C"],
            premise="Premise",
            hook_script="Hook",
            thumbnail_seed="seed",
            predicted_ctr_range="8-12%",
            predicted_avd_range="40-50%",
            why_it_should_work="Reason",
        ),
        weights={},
        score_breakdown={},
        scores={"concept_01": 8.0},
        winner_reason="Best",
    )
    script = ScriptArtifact(
        video_title="A",
        target_length_min=10,
        hook=ScriptHook(start_sec=0, end_sec=10, spoken_words="Hook", hook_type="stakes"),
        segments=[
            ScriptSegment(
                segment_id="seg_01",
                start_sec=0,
                end_sec=60,
                purpose="intro",
                spoken_script="Intro",
                retention_device="curiosity",
                emotion="tense",
                visual_intent="proof",
                drop_risk="low",
                why_viewer_stays="stakes",
            )
        ],
        mid_video_hooks=[],
        cta=ScriptCTA(time_sec=580, line="Subscribe", goal="Subscribe"),
        retention_summary=ScriptRetentionSummary(opening_strategy="open", reengagement_points=[], payoff_strategy="payoff"),
    )
    voiceover = VoiceoverArtifact(
        voice_style="style",
        music_direction="music",
        sfx_cues=[],
        voiceover_segments=[
            VoiceoverSegment(
                segment_id="seg_01",
                vo_text="Intro",
                emotion="tense",
                pace="fast",
                emphasis_words=["Intro"],
                breath_points=[5],
                timing_notes="notes",
            )
        ],
    )
    storyboard = StoryboardArtifact(
        video_title="A",
        style_direction="cinematic",
        editing_rhythm="fast",
        energy_map=["high"],
        segments=[
            StoryboardSegment(
                segment_id="seg_01",
                start_sec=0,
                end_sec=60,
                segment_goal="intro",
                emotional_beat="tense",
                visual_strategy="proof",
                attention_reset="curiosity",
                shots=[
                    StoryboardShot(
                        shot_id="shot_001",
                        start_sec=0,
                        end_sec=20,
                        duration_sec=20.0,
                        shot_type="A_ROLL",
                        camera_view="medium",
                        description="desc",
                        subject="creator",
                        location="studio",
                        motion="static",
                        on_screen_text="",
                        transition_in="hard cut",
                        transition_out="hard cut",
                        sound_design="",
                        asset_type="RECORDED_A_ROLL",
                        priority="required",
                    )
                ],
            )
        ],
    )

    assert load_storyboard_system_prompt()
    assert load_shot_plan_system_prompt()
    assert build_storyboard_user_prompt(
        brief=brief,
        selected_concept=concept,
        script=script,
        voiceover=voiceover,
    )
    assert build_shot_plan_user_prompt(brief=brief, storyboard=storyboard)


def test_load_prompt_template_fails_on_missing_variables(tmp_path):
    template_path = tmp_path / "prompt.txt"
    template_path.write_text("Hello {name}\nTopic: {topic}\n", encoding="utf-8")

    with pytest.raises(PromptTemplateError, match="topic"):
        load_prompt_template(template_path, name="Utsab")
