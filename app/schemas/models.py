from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field, model_validator


class AssetPreferences(BaseModel):
    stock_sites: list[str] = Field(default_factory=list)
    ai_video_tool: str = "Kling 3.0"
    editor: str = "Premiere Pro"


class ChannelBrief(BaseModel):
    channel_name: str
    niche: str
    target_audience: str
    tone: str
    target_length_min: int = Field(ge=1, le=180)
    brand_colors: list[str] = Field(default_factory=list)
    format_preferences: list[str] = Field(default_factory=list)
    visual_style: str
    cta_goal: str
    asset_preferences: AssetPreferences


class TrendReport(BaseModel):
    winning_formats: list[str] = Field(default_factory=list)
    declining_formats: list[str] = Field(default_factory=list)
    hook_patterns: list[str] = Field(default_factory=list)
    thumbnail_patterns: list[str] = Field(default_factory=list)
    content_gaps: list[str] = Field(default_factory=list)
    exploit_list: list[str] = Field(default_factory=list)
    avoid_list: list[str] = Field(default_factory=list)
    opportunity_map: list[str] = Field(default_factory=list)


class VideoConcept(BaseModel):
    concept_id: str
    format: str
    title_options: list[str] = Field(min_length=3, max_length=5)
    premise: str
    hook_script: str
    thumbnail_seed: str
    predicted_ctr_range: str
    predicted_avd_range: str
    why_it_should_work: str


class ConceptBatch(BaseModel):
    concepts: list[VideoConcept] = Field(default_factory=list, min_length=5, max_length=5)

    @model_validator(mode="after")
    def validate_unique_ids(self) -> "ConceptBatch":
        concept_ids = [concept.concept_id for concept in self.concepts]
        if len(set(concept_ids)) != len(concept_ids):
            raise ValueError("Concept IDs must be unique")
        return self


class ScoreComponent(BaseModel):
    raw_score: float = Field(ge=0.0, le=10.0)
    weight: float = Field(ge=0.0)
    weighted_score: float = Field(ge=0.0)


class ConceptScoreReport(BaseModel):
    concept_id: str
    components: dict[str, ScoreComponent] = Field(default_factory=dict)
    total_score: float = Field(ge=0.0)


class SelectedConcept(BaseModel):
    winner_id: str
    winner: VideoConcept
    weights: dict[str, float] = Field(default_factory=dict)
    score_breakdown: dict[str, ConceptScoreReport] = Field(default_factory=dict)
    scores: dict[str, float] = Field(default_factory=dict)
    winner_reason: str


class ScriptHook(BaseModel):
    start_sec: int = Field(ge=0)
    end_sec: int = Field(gt=0)
    spoken_words: str
    hook_type: str


class ScriptSegment(BaseModel):
    segment_id: str
    start_sec: int = Field(ge=0)
    end_sec: int = Field(gt=0)
    purpose: str
    spoken_script: str
    retention_device: str
    emotion: str
    visual_intent: str
    drop_risk: Literal["low", "medium", "high"]
    why_viewer_stays: str


class MidVideoHook(BaseModel):
    time_sec: int = Field(ge=0)
    line: str
    purpose: str


class ScriptCTA(BaseModel):
    time_sec: int = Field(ge=0)
    line: str
    goal: str


class ScriptRetentionSummary(BaseModel):
    opening_strategy: str
    reengagement_points: list[str] = Field(default_factory=list)
    payoff_strategy: str


class ScriptArtifact(BaseModel):
    video_title: str
    target_length_min: int = Field(ge=1, le=180)
    hook: ScriptHook
    segments: list[ScriptSegment] = Field(default_factory=list, min_length=1)
    mid_video_hooks: list[MidVideoHook] = Field(default_factory=list)
    cta: ScriptCTA
    retention_summary: ScriptRetentionSummary

    @model_validator(mode="after")
    def validate_script_structure(self) -> "ScriptArtifact":
        if self.hook.start_sec >= self.hook.end_sec:
            raise ValueError("Hook must end after it starts")
        first_segment = self.segments[0]
        if self.hook.start_sec != first_segment.start_sec:
            raise ValueError("Hook must start at the first segment start")
        if self.hook.end_sec > first_segment.end_sec:
            raise ValueError("Hook must fit within the first segment")
        previous_end = -1
        for segment in self.segments:
            if segment.start_sec >= segment.end_sec:
                raise ValueError(f"Segment {segment.segment_id} must end after it starts")
            if segment.start_sec < previous_end:
                raise ValueError(f"Segment {segment.segment_id} overlaps a previous segment")
            previous_end = segment.end_sec
        total_duration_sec = self.target_length_min * 60
        if self.cta.time_sec > total_duration_sec:
            raise ValueError("CTA time must be within target runtime")
        return self


class SFXCue(BaseModel):
    time_sec: int = Field(ge=0)
    cue: str
    purpose: str


class VoiceoverSegment(BaseModel):
    segment_id: str
    vo_text: str
    emotion: str
    pace: str
    emphasis_words: list[str] = Field(default_factory=list)
    breath_points: list[int] = Field(default_factory=list)
    timing_notes: str


class VoiceoverArtifact(BaseModel):
    voice_style: str
    music_direction: str
    sfx_cues: list[SFXCue] = Field(default_factory=list)
    voiceover_segments: list[VoiceoverSegment] = Field(default_factory=list)


class Shot(BaseModel):
    shot_id: str
    duration_sec: float
    type: Literal["A-roll", "AI_BROLL", "STOCK", "SCREEN_CAPTURE"]
    description: str
    on_screen_text: str = ""
    transition: str = "hard cut"
    sound_design: str = ""


class StoryboardSegment(BaseModel):
    segment_id: str
    shots: list[Shot] = Field(default_factory=list)


class StoryboardArtifact(BaseModel):
    segments: list[StoryboardSegment] = Field(default_factory=list)
    estimated_total_shots: int
    editing_rhythm: dict[str, str] = Field(default_factory=dict)


class KlingJob(BaseModel):
    shot_id: str
    prompt: str
    duration_sec: float
    start_frame_guide: str
    end_frame_guide: str
    audio_suggestion: str


class KlingArtifact(BaseModel):
    kling_jobs: list[KlingJob] = Field(default_factory=list)


class ThumbnailVariant(BaseModel):
    id: str
    visual: str
    text: str
    emotion: str
    predicted_ctr: str
    psychological_angle: str


class ThumbnailArtifact(BaseModel):
    thumbnail_variants: list[ThumbnailVariant] = Field(default_factory=list)
    test_order: list[str] = Field(default_factory=list)


class Chapter(BaseModel):
    time: str
    label: str


class MetadataArtifact(BaseModel):
    final_title: str
    description: str
    tags: list[str] = Field(default_factory=list)
    chapters: list[Chapter] = Field(default_factory=list)


class ConceptPackage(BaseModel):
    project_name: str
    brief: ChannelBrief
    trends: TrendReport
    concepts: ConceptBatch
    selected_concept: SelectedConcept
    script: ScriptArtifact
    voiceover: VoiceoverArtifact


class ScriptVoicePackage(BaseModel):
    project_name: str
    brief: ChannelBrief
    selected_concept: SelectedConcept
    script: ScriptArtifact
    voiceover: VoiceoverArtifact


class FinalPackage(BaseModel):
    project_name: str
    selected_concept: SelectedConcept
    script: ScriptArtifact
    voiceover: VoiceoverArtifact


class PublishPack(BaseModel):
    project_name: str
    brief: ChannelBrief
    selected_concept: SelectedConcept
    script: ScriptArtifact
    voiceover: VoiceoverArtifact
    storyboard: StoryboardArtifact
    kling: KlingArtifact
    thumbnails: ThumbnailArtifact
    metadata: MetadataArtifact
