from __future__ import annotations

import re

from app.llm.base import LLMClient
from app.modules.base import PipelineModule
from app.prompts.module_prompts import (
    build_concept_user_prompt,
    load_concept_system_prompt,
)
from app.schemas.models import (
    ChannelBrief,
    ConceptBatch,
    ConceptScoreReport,
    ScoreComponent,
    SelectedConcept,
    TrendReport,
    VideoConcept,
)
from app.utils.artifact_store import LLMStageArtifacts
from app.utils.validator import validate_with_repair


class ConceptModule(PipelineModule):
    name = "concept"
    output_filename = "02_concepts.json"

    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self.llm_client = llm_client
        self.last_llm_artifacts: LLMStageArtifacts | None = None

    def run(self, **kwargs) -> ConceptBatch:
        brief: ChannelBrief = kwargs["brief"]
        trends: TrendReport = kwargs["trends"]
        if self.llm_client is not None:
            system_prompt = load_concept_system_prompt()
            payload = self.llm_client.generate_structured(
                build_concept_user_prompt(brief=brief, trends=trends),
                system_prompt=system_prompt,
                schema=ConceptBatch.model_json_schema(),
                schema_name="concept_batch",
            )
            validated = validate_with_repair(
                payload=payload,
                model=ConceptBatch,
                llm_client=self.llm_client,
                repair_context=(
                    "The output must contain exactly five distinct video concepts with unique ids "
                    "and valid fields for the concept batch artifact."
                ),
                schema_name="concept_batch_repair",
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

        concepts = [
            VideoConcept(
                concept_id="concept_01",
                format="experiment",
                title_options=[
                    f"I Used 5 {brief.niche} Products for 7 Days — Here’s What Actually Worked",
                    f"These 5 {brief.niche} Picks Saved Me Hours in One Week",
                    f"I Rebuilt My Workflow With {brief.niche}",
                    f"I Tested 5 {brief.niche} Options So You Don’t Waste Money",
                    f"The {brief.niche} Stack I’d Use Again Tomorrow",
                ],
                premise=f"A real-world test of {brief.niche} solutions for {brief.target_audience}.",
                hook_script="I tested five tools back-to-back under real pressure, and one of them completely broke my workflow.",
                thumbnail_seed="shocked creator face, app logos, large time saved metric",
                predicted_ctr_range="7-11%",
                predicted_avd_range="42-55%",
                why_it_should_work="Experiment framing plus a concrete downside risk creates strong click tension and a believable payoff.",
            ),
            VideoConcept(
                concept_id="concept_02",
                format="educational",
                title_options=[
                    f"The Only {brief.niche} Workflow Beginners Actually Need",
                    f"Stop Overcomplicating {brief.niche} — Use This Instead",
                    f"A Simple {brief.niche} System That Actually Scales",
                    f"The Beginner {brief.niche} Stack I Wish I Had Earlier",
                    f"From Chaos to System: My {brief.niche} Setup",
                ],
                premise=f"A step-by-step workflow designed for {brief.target_audience}.",
                hook_script="Most people are building their setup backwards, so let me show you the version that actually saves time.",
                thumbnail_seed="clean desk, one workflow diagram, serious expression",
                predicted_ctr_range="6-9%",
                predicted_avd_range="45-58%",
                why_it_should_work="The concept promises simplification and immediate usefulness, which supports stronger completion from practical viewers.",
            ),
            VideoConcept(
                concept_id="concept_03",
                format="challenge",
                title_options=[
                    f"Can I Build a Full {brief.niche} System in 24 Hours?",
                    f"I Gave Myself 24 Hours to Fix My {brief.niche} Workflow",
                    f"A 1-Day {brief.niche} Challenge With Real Stakes",
                    f"I Tried to Automate My Entire Workflow in One Day",
                    f"24 Hours. One Goal. Full {brief.niche} Rebuild.",
                ],
                premise=f"A time-boxed challenge with visible stakes and payoff for {brief.target_audience}.",
                hook_script="I gave myself just 24 hours to build a complete system, and if it failed, the whole video fell apart.",
                thumbnail_seed="countdown timer, stressed face, half-built system",
                predicted_ctr_range="8-12%",
                predicted_avd_range="40-52%",
                why_it_should_work="The deadline creates urgency, while the visible challenge structure makes the video easy to follow moment by moment.",
            ),
            VideoConcept(
                concept_id="concept_04",
                format="case_study",
                title_options=[
                    f"I Rebuilt a Broken {brief.niche} Workflow From Scratch",
                    f"This {brief.niche} System Failed Until I Changed These 3 Things",
                    f"Fixing a Messy {brief.niche} Setup Step by Step",
                    f"How I Turned a Bad {brief.niche} Process Into a Repeatable System",
                    f"The {brief.niche} Workflow Audit That Changed Everything",
                ],
                premise=f"A teardown and rebuild of a flawed {brief.niche} workflow for {brief.target_audience}.",
                hook_script="This workflow looked fine on the surface, but three hidden mistakes were killing the result.",
                thumbnail_seed="before/after workflow board, red error marks, focused creator",
                predicted_ctr_range="7-10%",
                predicted_avd_range="44-57%",
                why_it_should_work="Diagnosis plus transformation gives the audience both a problem to relate to and a payoff to wait for.",
            ),
            VideoConcept(
                concept_id="concept_05",
                format="ranking",
                title_options=[
                    f"The Best {brief.niche} Investments Under a Tight Budget",
                    f"I Ranked Cheap vs Expensive {brief.niche} Options by Real Output",
                    f"What Actually Matters When Buying {brief.niche}",
                    f"The Smartest Budget {brief.niche} Upgrades Right Now",
                    f"I Tested Budget {brief.niche} Picks Against Premium Ones",
                ],
                premise=f"A budget-focused ranking built around outcome, tradeoffs, and purchase clarity for {brief.target_audience}.",
                hook_script="Some of the cheapest options performed way better than they had any right to, and one expensive pick was a complete miss.",
                thumbnail_seed="cheap vs premium split, bold price tags, skeptical expression",
                predicted_ctr_range="7-11%",
                predicted_avd_range="41-54%",
                why_it_should_work="Price tension and comparative outcomes make the concept broadly relevant and easy to package in title and thumbnail.",
            ),
        ]
        return ConceptBatch(concepts=concepts)


class SelectorModule(PipelineModule):
    name = "selector"
    output_filename = "03_selected_concept.json"

    DEFAULT_WEIGHTS = {
        "click_potential": 0.35,
        "retention_potential": 0.30,
        "audience_fit": 0.20,
        "production_practicality": 0.15,
    }

    def __init__(self, llm_client: LLMClient | None = None, weights: dict[str, float] | None = None) -> None:
        self.llm_client = llm_client
        self.last_llm_artifacts: LLMStageArtifacts | None = None
        self.weights = dict(weights or self.DEFAULT_WEIGHTS)

    def run(self, **kwargs) -> SelectedConcept:
        batch: ConceptBatch = kwargs["concept_batch"]
        concept_reports = {
            concept.concept_id: self._score_concept(concept)
            for concept in batch.concepts
        }
        scores = {
            concept_id: report.total_score
            for concept_id, report in concept_reports.items()
        }
        winner = max(batch.concepts, key=lambda c: scores.get(c.concept_id, 0.0))
        winner_report = concept_reports[winner.concept_id]
        return SelectedConcept(
            winner_id=winner.concept_id,
            winner=winner,
            weights=self.weights,
            score_breakdown=concept_reports,
            scores=scores,
            winner_reason=self._build_winner_reason(winner, winner_report),
        )

    def _score_concept(self, concept: VideoConcept) -> ConceptScoreReport:
        ctr_midpoint = _parse_percent_range_midpoint(concept.predicted_ctr_range)
        avd_midpoint = _parse_percent_range_midpoint(concept.predicted_avd_range)

        click_potential = _weighted_average(
            (_scale_range(ctr_midpoint, floor=4.0, ceiling=12.0), 0.55),
            (_score_title_options(concept.title_options), 0.30),
            (_score_thumbnail_seed(concept.thumbnail_seed), 0.15),
        )
        retention_potential = _weighted_average(
            (_scale_range(avd_midpoint, floor=35.0, ceiling=60.0), 0.55),
            (_score_hook_script(concept.hook_script), 0.30),
            (_score_explanation_clarity(concept.why_it_should_work), 0.15),
        )
        audience_fit = _weighted_average(
            (_score_explanation_clarity(concept.why_it_should_work), 0.55),
            (_score_premise_clarity(concept.premise), 0.25),
            (_score_format_fit(concept.format), 0.20),
        )
        production_practicality = _weighted_average(
            (_score_format_practicality(concept.format), 0.55),
            (_score_thumbnail_practicality(concept.thumbnail_seed), 0.25),
            (_score_premise_clarity(concept.premise), 0.20),
        )

        components = {
            "click_potential": _build_score_component(click_potential, self.weights["click_potential"]),
            "retention_potential": _build_score_component(retention_potential, self.weights["retention_potential"]),
            "audience_fit": _build_score_component(audience_fit, self.weights["audience_fit"]),
            "production_practicality": _build_score_component(
                production_practicality,
                self.weights["production_practicality"],
            ),
        }
        total_score = round(sum(component.weighted_score for component in components.values()), 3)

        return ConceptScoreReport(
            concept_id=concept.concept_id,
            components=components,
            total_score=total_score,
        )

    def _build_winner_reason(self, winner: VideoConcept, report: ConceptScoreReport) -> str:
        ranked_components = sorted(
            report.components.items(),
            key=lambda item: item[1].weighted_score,
            reverse=True,
        )
        top_labels = ", ".join(name for name, _ in ranked_components[:2])
        return (
            f"{winner.concept_id} won because it produced the strongest weighted mix of "
            f"{top_labels}, while maintaining the highest total score."
        )


def _build_score_component(raw_score: float, weight: float) -> ScoreComponent:
    return ScoreComponent(
        raw_score=round(raw_score, 3),
        weight=weight,
        weighted_score=round(raw_score * weight, 3),
    )


def _weighted_average(*items: tuple[float, float]) -> float:
    weighted_total = sum(score * weight for score, weight in items)
    total_weight = sum(weight for _, weight in items)
    return round(weighted_total / total_weight, 3)


def _parse_percent_range_midpoint(value: str) -> float:
    numbers = [float(match) for match in re.findall(r"\d+(?:\.\d+)?", value)]
    if not numbers:
        return 0.0
    if len(numbers) == 1:
        return numbers[0]
    return round(sum(numbers[:2]) / 2, 3)


def _scale_range(value: float, *, floor: float, ceiling: float) -> float:
    if ceiling <= floor:
        return 0.0
    normalized = (value - floor) / (ceiling - floor)
    return round(max(0.0, min(normalized * 10.0, 10.0)), 3)


def _score_title_options(title_options: list[str]) -> float:
    text = " ".join(title_options).lower()
    score = 5.5
    keywords = ("tested", "hours", "cheap", "best", "broken", "24", "only", "ranked", "failed")
    score += min(sum(text.count(keyword) for keyword in keywords) * 0.35, 2.0)
    if any("?" in title for title in title_options):
        score += 0.5
    if any("i " in title.lower() for title in title_options):
        score += 0.4
    return min(round(score, 3), 10.0)


def _score_thumbnail_seed(thumbnail_seed: str) -> float:
    text = thumbnail_seed.lower()
    score = 5.0
    visual_keywords = ("face", "logos", "timer", "before/after", "split", "metric", "error", "price")
    score += min(sum(keyword in text for keyword in visual_keywords) * 0.6, 3.0)
    return min(round(score, 3), 10.0)


def _score_thumbnail_practicality(thumbnail_seed: str) -> float:
    text = thumbnail_seed.lower()
    score = 6.0
    practical_keywords = ("split", "logos", "board", "timer", "price", "desk")
    score += min(sum(keyword in text for keyword in practical_keywords) * 0.45, 2.0)
    if len(thumbnail_seed.split(",")) > 4:
        score -= 0.5
    return max(0.0, min(round(score, 3), 10.0))


def _score_hook_script(hook_script: str) -> float:
    text = hook_script.lower()
    score = 5.5
    hook_keywords = ("broke", "failed", "just", "pressure", "unexpected", "mistakes", "cheap", "miss")
    score += min(sum(keyword in text for keyword in hook_keywords) * 0.5, 3.0)
    if any(char.isdigit() for char in hook_script):
        score += 0.5
    return min(round(score, 3), 10.0)


def _score_explanation_clarity(reason: str) -> float:
    word_count = len(reason.split())
    score = 6.0
    if 12 <= word_count <= 24:
        score += 1.5
    elif word_count < 8:
        score -= 1.0
    if any(keyword in reason.lower() for keyword in ("audience", "payoff", "tension", "relevant", "practical")):
        score += 1.0
    return max(0.0, min(round(score, 3), 10.0))


def _score_premise_clarity(premise: str) -> float:
    score = 6.5
    if len(premise.split()) >= 8:
        score += 1.0
    if any(keyword in premise.lower() for keyword in ("test", "workflow", "ranking", "rebuild", "challenge")):
        score += 1.0
    return min(round(score, 3), 10.0)


def _score_format_fit(format_name: str) -> float:
    return {
        "experiment": 9.0,
        "challenge": 8.8,
        "case_study": 8.4,
        "ranking": 8.0,
        "educational": 7.6,
    }.get(format_name, 7.0)


def _score_format_practicality(format_name: str) -> float:
    return {
        "educational": 9.0,
        "ranking": 8.6,
        "case_study": 8.2,
        "experiment": 7.9,
        "challenge": 7.4,
    }.get(format_name, 7.0)
