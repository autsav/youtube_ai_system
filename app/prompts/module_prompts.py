from __future__ import annotations

from pathlib import Path

from app.schemas.models import ChannelBrief, ConceptBatch, ScriptArtifact, SelectedConcept, TrendReport
from app.utils.json_tools import pretty_json
from app.utils.prompt_loader import load_prompt_template

_TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"

TREND_SYSTEM_PROMPT = """You are a YouTube Trend Intelligence System.
Return structured insight for current winning formats, declining formats, hook patterns, thumbnail patterns, and opportunity gaps."""

VOICE_SYSTEM_PROMPT = """You are an elite voiceover director.
Polish for performance, breath control, emphasis, and readability."""

STORYBOARD_SYSTEM_PROMPT = """You are a production planner.
Turn script segments into executable shots with asset types, transitions, and sound cues."""

KLING_SYSTEM_PROMPT = """You are an expert motion prompt engineer for cinematic AI video generation.
Only generate prompts for AI_BROLL shots. Preserve continuity, motion realism, and clean transitions."""

THUMBNAIL_SYSTEM_PROMPT = """You are a thumbnail psychologist.
Generate high-CTR thumbnail concepts aligned with the selected video concept and brand colors."""

METADATA_SYSTEM_PROMPT = """You are a YouTube metadata strategist.
Return final title, description, tags, and chapters aligned with the final script and concept."""


def build_trend_user_prompt(brief: ChannelBrief) -> str:
    return load_prompt_template(
        _TEMPLATE_DIR / "trend_user.txt",
        brief_json=pretty_json(brief.model_dump(mode="json")),
    )


def load_trend_system_prompt() -> str:
    return load_prompt_template(_TEMPLATE_DIR / "trend_system.txt")


def load_concept_system_prompt() -> str:
    return load_prompt_template(_TEMPLATE_DIR / "concept_system.txt")


def build_concept_user_prompt(*, brief: ChannelBrief, trends: TrendReport) -> str:
    return load_prompt_template(
        _TEMPLATE_DIR / "concept_user.txt",
        brief_json=pretty_json(brief.model_dump(mode="json")),
        trend_json=pretty_json(trends.model_dump(mode="json")),
    )


def build_selector_user_prompt(concept_batch: ConceptBatch) -> str:
    return "\n\n".join(
        [
            "Score the 5 concepts and select one winner.",
            "Scores must use the concept_id values as keys and use a 0-10 scale with decimals allowed.",
            "Choose the winner with the highest score and explain the decision with a concise production-oriented reason.",
            "Concept batch JSON:",
            pretty_json(concept_batch.model_dump(mode="json")),
        ]
    )


def load_script_system_prompt() -> str:
    """Load the system prompt used for structured script generation."""
    return load_prompt_template(_TEMPLATE_DIR / "script_system.txt")


def build_script_user_prompt(*, brief: ChannelBrief, selected_concept: SelectedConcept) -> str:
    """Render the script-generation user prompt from the brief and winning concept."""
    return load_prompt_template(
        _TEMPLATE_DIR / "script_user.txt",
        brief_json=pretty_json(brief.model_dump(mode="json")),
        selected_concept_json=pretty_json(selected_concept.model_dump(mode="json")),
    )


def load_voice_system_prompt() -> str:
    return load_prompt_template(_TEMPLATE_DIR / "voice_system.txt")


def build_voice_user_prompt(*, brief: ChannelBrief, script: ScriptArtifact) -> str:
    return load_prompt_template(
        _TEMPLATE_DIR / "voice_user.txt",
        brief_json=pretty_json(brief.model_dump(mode="json")),
        script_json=pretty_json(script.model_dump(mode="json")),
    )
