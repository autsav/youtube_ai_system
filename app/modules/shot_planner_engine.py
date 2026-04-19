from __future__ import annotations

import json

from app.llm.base import LLMClient
from app.modules.base import PipelineModule
from app.prompts.module_prompts import build_shot_plan_user_prompt, load_shot_plan_system_prompt
from app.schemas.models import (
    AssetRequirement,
    ChannelBrief,
    ProductionSummaryArtifact,
    QuickBrollIdea,
    ShotPlanArtifact,
    StoryboardArtifact,
    TimelineBlock,
)
from app.utils.artifact_store import LLMStageArtifacts
from app.utils.validator import validate_with_repair


class ShotPlannerModule(PipelineModule):
    name = "shot_plan"
    output_filename = "07_shot_plan.json"

    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self.llm_client = llm_client
        self.last_llm_artifacts: LLMStageArtifacts | None = None

    def run(self, **kwargs) -> ShotPlanArtifact:
        brief: ChannelBrief = kwargs["brief"]
        storyboard: StoryboardArtifact = kwargs["storyboard"]

        if self.llm_client is not None:
            system_prompt = load_shot_plan_system_prompt()
            payload = self.llm_client.generate_structured(
                build_shot_plan_user_prompt(brief=brief, storyboard=storyboard),
                system_prompt=system_prompt,
                schema=ShotPlanArtifact.model_json_schema(),
                schema_name="shot_plan_artifact",
            )
            validated = validate_with_repair(
                payload=payload,
                model=ShotPlanArtifact,
                llm_client=self.llm_client,
                repair_context=(
                    "The output must be a valid shot plan with realistic category estimates, "
                    "timeline blocks, concrete quick b-roll ideas, and actionable asset requirements."
                ),
                schema_name="shot_plan_artifact_repair",
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
            else:
                self.last_llm_artifacts = LLMStageArtifacts(
                    stage_name=self.name,
                    raw_text=json.dumps(payload, ensure_ascii=False),
                    parsed_json=payload,
                    validated_model=validated,
                )
            return validated

        all_shots = [shot for segment in storyboard.segments for shot in segment.shots]
        a_roll = [shot for shot in all_shots if shot.shot_type == "A_ROLL"]
        b_roll = [shot for shot in all_shots if shot.shot_type == "B_ROLL"]
        ai_roll = [shot for shot in all_shots if shot.shot_type == "AI_BROLL"]
        stock = [shot for shot in all_shots if shot.shot_type == "STOCK"]

        timeline_blocks = [
            TimelineBlock(
                block_id=f"block_{idx+1:02d}",
                start_sec=segment.start_sec,
                end_sec=segment.end_sec,
                purpose=segment.segment_goal,
                pace="fast" if idx == 0 else "medium",
                visual_density="high" if idx in (0, len(storyboard.segments) - 1) else "medium",
                primary_assets=[shot.asset_type for shot in segment.shots],
                notes=f"Drive {segment.emotional_beat} while reinforcing {segment.attention_reset}.",
            )
            for idx, segment in enumerate(storyboard.segments)
        ]

        quick_broll_ideas = [
            QuickBrollIdea(
                idea_id=f"idea_{idx+1:02d}",
                description=f"Insert 2-second visual proof beat for {segment.segment_goal}",
                intended_segment_id=segment.segment_id,
                suggested_asset_type="SCREEN_CAPTURE",
                why_it_helps="Adds concrete evidence to reduce drop-off risk.",
            )
            for idx, segment in enumerate(storyboard.segments)
        ]

        asset_requirements = [
            AssetRequirement(
                asset_id=f"asset_{idx+1:03d}",
                related_shot_id=shot.shot_id,
                asset_type=shot.asset_type,
                description=shot.description,
                source_preference=(
                    "in-house record" if shot.asset_type.startswith("RECORDED") else brief.asset_preferences.stock_sites[0] if brief.asset_preferences.stock_sites else "internal library"
                ),
                status="pending",
            )
            for idx, shot in enumerate(all_shots)
        ]

        return ShotPlanArtifact(
            estimated_total_shots=len(all_shots),
            estimated_a_roll_shots=len(a_roll),
            estimated_b_roll_shots=len(b_roll),
            estimated_ai_shots=len(ai_roll),
            estimated_stock_shots=len(stock),
            production_notes=[
                "Lock A-roll first for story spine.",
                "Collect screen captures before final VO pass.",
                "Queue AI shots after timeline lock.",
            ],
            timeline_blocks=timeline_blocks,
            quick_broll_ideas=quick_broll_ideas,
            asset_requirements=asset_requirements,
        )


def build_production_summary(*, shot_plan: ShotPlanArtifact) -> ProductionSummaryArtifact:
    required_assets = sum(1 for asset in shot_plan.asset_requirements if asset.status in ("pending", "in_progress"))
    return ProductionSummaryArtifact(
        total_assets=len(shot_plan.asset_requirements),
        required_assets=required_assets,
        high_priority_actions=[
            "Record required A-roll setups",
            "Capture proof-driven screen sequences",
            "Approve AI-generated inserts",
        ],
        production_risks=[
            "Missing proof visuals can reduce retention payoff.",
            "Late AI shot approvals can delay edit lock.",
        ],
    )
