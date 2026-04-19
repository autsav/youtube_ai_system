from __future__ import annotations

from app.llm.base import LLMClient
from app.modules.base import PipelineModule
from app.prompts.module_prompts import build_script_user_prompt, load_script_system_prompt
from app.schemas.models import (
    ChannelBrief,
    MidVideoHook,
    ScriptArtifact,
    ScriptCTA,
    ScriptHook,
    ScriptRetentionSummary,
    ScriptSegment,
    SelectedConcept,
)
from app.utils.artifact_store import LLMStageArtifacts
from app.utils.validator import validate_with_repair


class ScriptModule(PipelineModule):
    """Generate a structured script artifact from the selected concept."""

    name = "script"
    output_filename = "04_script.json"

    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self.llm_client = llm_client
        self.last_llm_artifacts: LLMStageArtifacts | None = None

    def run(self, **kwargs) -> ScriptArtifact:
        """Return a schema-validated script artifact for the chosen winner."""
        brief: ChannelBrief = kwargs["brief"]
        selected: SelectedConcept = kwargs["selected_concept"]
        if not selected.winner.title_options:
            raise ValueError("selected_concept.winner.title_options must contain at least one title")
        if not selected.winner.hook_script.strip():
            raise ValueError("selected_concept.winner.hook_script must be non-empty")
        if selected.winner_id != selected.winner.concept_id:
            raise ValueError("selected_concept.winner_id must match selected_concept.winner.concept_id")
        if self.llm_client is not None:
            system_prompt = load_script_system_prompt()
            payload = self.llm_client.generate_structured(
                build_script_user_prompt(brief=brief, selected_concept=selected),
                system_prompt=system_prompt,
                schema=ScriptArtifact.model_json_schema(),
                schema_name="script_artifact",
            )
            validated = validate_with_repair(
                payload=payload,
                model=ScriptArtifact,
                llm_client=self.llm_client,
                repair_context=(
                    "The output must be a valid retention-aware YouTube script package with a hook in the opening, "
                    "coherent non-overlapping segments, re-engagement hooks, CTA object, and retention summary."
                ),
                schema_name="script_artifact_repair",
                system_prompt=system_prompt,
            )
            capture = self.llm_client.last_generation
            if capture is not None:
                self.last_llm_artifacts = LLMStageArtifacts(
                    stage_name=self.name,
                    raw_text=capture.raw_text,
                    parsed_json=capture.parsed_json,
                    validated_model=validated,
                )
            return validated

        title = selected.winner.title_options[0]
        target_sec = brief.target_length_min * 60
        segments = [
            ScriptSegment(
                segment_id="seg_01",
                start_sec=0,
                end_sec=45,
                purpose="hook and promise",
                spoken_script=selected.winner.hook_script,
                retention_device="curiosity gap",
                emotion="high curiosity",
                visual_intent="quick cuts of final outcome previews with creator on-camera stakes",
                drop_risk="low",
                why_viewer_stays="A concrete high-stakes promise is made immediately.",
            ),
            ScriptSegment(
                segment_id="seg_02",
                start_sec=45,
                end_sec=150,
                purpose="setup and rules",
                spoken_script="Here are the constraints, what success means, and how I will measure what actually works.",
                retention_device="challenge framing",
                emotion="tension",
                visual_intent="on-screen rules card and timeline markers",
                drop_risk="low",
                why_viewer_stays="The viewer understands exactly what outcome to wait for.",
            ),
            ScriptSegment(
                segment_id="seg_03",
                start_sec=150,
                end_sec=300,
                purpose="first test block and setback",
                spoken_script="The first pass looked strong, then one hidden failure almost broke the entire concept.",
                retention_device="surprise turn",
                emotion="surprise",
                visual_intent="contrast between expected result and failure evidence",
                drop_risk="medium",
                why_viewer_stays="Momentum shifts from likely success to unexpected risk.",
            ),
            ScriptSegment(
                segment_id="seg_04",
                start_sec=300,
                end_sec=495,
                purpose="escalation and comparison",
                spoken_script="Now I compare the options head-to-head on speed, output quality, and production friction.",
                retention_device="comparison ladder",
                emotion="analysis",
                visual_intent="scoreboard style overlays and side-by-side outcome clips",
                drop_risk="medium",
                why_viewer_stays="A ranked decision is building and the winner is still unclear.",
            ),
            ScriptSegment(
                segment_id="seg_05",
                start_sec=495,
                end_sec=target_sec,
                purpose="payoff and recommendation",
                spoken_script="Here is the setup I would actually run next week, who it is for, and what to avoid.",
                retention_device="payoff reveal",
                emotion="resolution",
                visual_intent="final ranked list with practical decision rubric",
                drop_risk="low",
                why_viewer_stays="The promised decision and practical next steps finally land.",
            ),
        ]
        return ScriptArtifact(
            video_title=title,
            target_length_min=brief.target_length_min,
            hook=ScriptHook(
                start_sec=0,
                end_sec=30,
                spoken_words=selected.winner.hook_script,
                hook_type="stakes + curiosity gap",
            ),
            segments=segments,
            mid_video_hooks=[
                MidVideoHook(
                    time_sec=110,
                    line="One result here completely changed the ranking.",
                    purpose="reset curiosity before first deep test",
                ),
                MidVideoHook(
                    time_sec=240,
                    line="At this point I realized my original assumption was wrong.",
                    purpose="reframe narrative before escalation",
                ),
                MidVideoHook(
                    time_sec=385,
                    line="The final comparison exposed a tradeoff nobody talks about.",
                    purpose="bridge into payoff setup",
                ),
            ],
            cta=ScriptCTA(
                time_sec=max(target_sec - 20, 1),
                line=brief.cta_goal,
                goal=brief.cta_goal,
            ),
            retention_summary=ScriptRetentionSummary(
                opening_strategy="Lead with the strongest stake and immediate promised payoff.",
                reengagement_points=[
                    "~1:50 narrative reset with unexpected ranking shift",
                    "~4:00 assumption reversal to restart viewer curiosity",
                    "~6:25 tradeoff reveal before final recommendation",
                ],
                payoff_strategy="Deliver the ranked winner with concrete use-case guidance and what to avoid.",
            ),
        )
