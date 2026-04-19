from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

# Re-export existing pipeline models
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from app.schemas.models import (
    AssetPreferences,
    ChannelBrief,
    ConceptBatch,
    FinalPackage,
    ScenePrompt,
    ScriptArtifact,
    ScriptHook,
    ScriptSegment,
    ScriptCTA,
    ScriptRetentionSummary,
    SelectedConcept,
    TrendReport,
    VideoConcept,
    VideoPromptArtifact,
)


# API Request/Response Models

class CreateProjectRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    brief: ChannelBrief


class ProjectResponse(BaseModel):
    id: str
    name: str
    status: str
    current_step: int
    created_at: str
    updated_at: str


class ProjectDetailResponse(BaseModel):
    id: str
    name: str
    status: str
    current_step: int
    brief: ChannelBrief
    created_at: str
    updated_at: str


class ProjectListResponse(BaseModel):
    projects: list[ProjectResponse]


class ProjectStatus(BaseModel):
    step: Literal["created", "trends", "concepts", "selected", "script", "video_prompts", "complete"]
    has_trends: bool
    has_concepts: bool
    has_selection: bool
    has_script: bool
    has_video_prompts: bool
    has_final_package: bool


# Pipeline Step Responses

class GenerateConceptsResponse(BaseModel):
    success: bool
    concepts: ConceptBatch | None
    error: str | None


class SelectConceptRequest(BaseModel):
    concept_id: str


class SelectConceptResponse(BaseModel):
    success: bool
    selection: SelectedConcept | None
    error: str | None


class GenerateScriptResponse(BaseModel):
    success: bool
    script: ScriptArtifact | None
    error: str | None


class GenerateVideoPromptsResponse(BaseModel):
    success: bool
    video_prompts: VideoPromptArtifact | None
    error: str | None


# Data fetch responses

class TrendsDataResponse(BaseModel):
    exists: bool
    trends: TrendReport | None


class ConceptsDataResponse(BaseModel):
    exists: bool
    concepts: ConceptBatch | None


class SelectionDataResponse(BaseModel):
    exists: bool
    selection: SelectedConcept | None


class ScriptDataResponse(BaseModel):
    exists: bool
    script: ScriptArtifact | None


class VideoPromptsDataResponse(BaseModel):
    exists: bool
    video_prompts: VideoPromptArtifact | None


class FinalPackageDataResponse(BaseModel):
    exists: bool
    final_package: FinalPackage | None


class ErrorResponse(BaseModel):
    detail: str
