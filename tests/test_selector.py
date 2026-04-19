from __future__ import annotations

from app.modules.concept import SelectorModule
from app.schemas.models import ConceptBatch, VideoConcept


def _concept(
    concept_id: str,
    *,
    format: str,
    ctr: str,
    avd: str,
    hook_script: str,
    thumbnail_seed: str,
    why_it_should_work: str,
) -> VideoConcept:
    return VideoConcept(
        concept_id=concept_id,
        format=format,
        title_options=[
            f"I Tested {concept_id}",
            f"{concept_id} Saved Me Hours",
            f"Can {concept_id} Actually Work?",
        ],
        premise="A clear premise built for practical viewers and measurable payoff.",
        hook_script=hook_script,
        thumbnail_seed=thumbnail_seed,
        predicted_ctr_range=ctr,
        predicted_avd_range=avd,
        why_it_should_work=why_it_should_work,
    )


def test_selector_returns_deterministic_score_report():
    selector = SelectorModule()
    batch = ConceptBatch(
        concepts=[
            _concept(
                "concept_01",
                format="experiment",
                ctr="7-11%",
                avd="42-55%",
                hook_script="I tested this under pressure and something broke.",
                thumbnail_seed="face, logos, metric",
                why_it_should_work="Strong payoff and practical relevance.",
            ),
            _concept(
                "concept_02",
                format="educational",
                ctr="6-9%",
                avd="45-58%",
                hook_script="Most people do this backwards, so here is the fix.",
                thumbnail_seed="desk, workflow diagram",
                why_it_should_work="Useful structure helps practical viewers stay engaged.",
            ),
            _concept(
                "concept_03",
                format="challenge",
                ctr="8-12%",
                avd="40-52%",
                hook_script="I gave myself 24 hours and failure would ruin the whole test.",
                thumbnail_seed="timer, stressed face, half-built system",
                why_it_should_work="Urgency and challenge structure create strong momentum.",
            ),
            _concept(
                "concept_04",
                format="case_study",
                ctr="7-10%",
                avd="44-57%",
                hook_script="Three hidden mistakes were quietly killing the result.",
                thumbnail_seed="before/after board, red errors",
                why_it_should_work="Transformation and diagnosis create a clear payoff.",
            ),
            _concept(
                "concept_05",
                format="ranking",
                ctr="7-11%",
                avd="41-54%",
                hook_script="One cheap option beat the expensive picks by a lot.",
                thumbnail_seed="price tags, split comparison",
                why_it_should_work="Price tension and comparison make this widely relevant.",
            ),
        ]
    )

    selected = selector.run(concept_batch=batch)

    assert selected.winner_id == selected.winner.concept_id
    assert set(selected.scores) == {concept.concept_id for concept in batch.concepts}
    assert set(selected.score_breakdown) == set(selected.scores)
    assert selected.weights == selector.DEFAULT_WEIGHTS
    assert max(selected.scores, key=selected.scores.get) == selected.winner_id
    assert "highest total score" in selected.winner_reason


def test_selector_honors_custom_weights():
    selector = SelectorModule(weights={"click_potential": 1.0, "retention_potential": 0.0, "audience_fit": 0.0, "production_practicality": 0.0})
    batch = ConceptBatch(
        concepts=[
            _concept(
                "concept_01",
                format="educational",
                ctr="5-6%",
                avd="55-60%",
                hook_script="Useful but calm opening.",
                thumbnail_seed="desk setup",
                why_it_should_work="Useful and practical.",
            ),
            _concept(
                "concept_02",
                format="challenge",
                ctr="10-12%",
                avd="35-40%",
                hook_script="I had 24 hours and everything could fail.",
                thumbnail_seed="timer, face, metric",
                why_it_should_work="High urgency creates clicks.",
            ),
            _concept("concept_03", format="experiment", ctr="6-8%", avd="42-45%", hook_script="I tested this.", thumbnail_seed="face", why_it_should_work="Clear test."),
            _concept("concept_04", format="case_study", ctr="6-7%", avd="42-43%", hook_script="I rebuilt this.", thumbnail_seed="board", why_it_should_work="Clear rebuild."),
            _concept("concept_05", format="ranking", ctr="6-7%", avd="42-43%", hook_script="I ranked these.", thumbnail_seed="split", why_it_should_work="Clear comparison."),
        ]
    )

    selected = selector.run(concept_batch=batch)

    assert selected.winner_id == "concept_02"
