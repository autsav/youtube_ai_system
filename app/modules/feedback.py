from __future__ import annotations

from pydantic import BaseModel, Field


class FeedbackReport(BaseModel):
    what_worked: list[str] = Field(default_factory=list)
    what_failed: list[str] = Field(default_factory=list)
    prompt_updates: dict[str, str] = Field(default_factory=dict)
