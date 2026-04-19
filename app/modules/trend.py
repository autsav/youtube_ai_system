from __future__ import annotations

from app.llm.base import LLMClient
from app.modules.base import PipelineModule
from app.prompts.module_prompts import build_trend_user_prompt, load_trend_system_prompt
from app.schemas.models import ChannelBrief, TrendReport
from app.utils.artifact_store import LLMStageArtifacts
from app.utils.validator import validate_with_repair


class TrendModule(PipelineModule):
    name = "trend"
    output_filename = "01_trends.json"

    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self.llm_client = llm_client
        self.last_llm_artifacts: LLMStageArtifacts | None = None

    def run(self, **kwargs) -> TrendReport:
        brief: ChannelBrief = kwargs["brief"]
        if self.llm_client is not None:
            system_prompt = load_trend_system_prompt()
            payload = self.llm_client.generate_structured(
                build_trend_user_prompt(brief),
                system_prompt=system_prompt,
                schema=TrendReport.model_json_schema(),
                schema_name="trend_report",
            )
            validated = validate_with_repair(
                payload=payload,
                model=TrendReport,
                llm_client=self.llm_client,
                repair_context="The output must be a valid trend report for a YouTube channel strategy pipeline.",
                schema_name="trend_report_repair",
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

        niche = brief.niche
        return TrendReport(
            winning_formats=[
                f"result-first experiments in {niche}",
                f"tool comparisons with measurable outcomes in {niche}",
                f"before-vs-after breakdowns for {brief.target_audience}",
            ],
            declining_formats=[
                "generic top-10 lists with no test data",
                "broad intros with no immediate payoff",
            ],
            hook_patterns=[
                "I tested this so you do not waste money",
                "This changed the result in less than a week",
                "I thought this would fail, but it did not",
            ],
            thumbnail_patterns=[
                "one face plus one bold metric",
                "clean split-screen before versus after",
            ],
            content_gaps=[
                f"practical workflows for {brief.target_audience}",
                f"budget-conscious {niche} systems",
            ],
            exploit_list=[
                "show a concrete outcome early",
                "use stakes, not explanation, in the first 15 seconds",
            ],
            avoid_list=[
                "slow context-heavy intros",
                "titles that sound like tutorials without urgency",
            ],
            opportunity_map=[
                f"Own the intersection of {niche} and fast implementation",
                "Lean on proof, screenshots, timing, and cost savings",
            ],
        )
