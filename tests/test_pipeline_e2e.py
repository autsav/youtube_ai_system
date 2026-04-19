from __future__ import annotations

import json
from pathlib import Path

from app.llm.base import StructuredGenerationCapture
from app.orchestrator import PipelineOrchestrator


class FakeLLMClient:
    def __init__(self, responses):
        self.responses = list(responses)
        self._last_generation = None

    @property
    def last_generation(self):
        return self._last_generation

    def generate_text(self, prompt: str, *, system_prompt: str | None = None) -> str:
        raise NotImplementedError

    def generate_structured(
        self,
        prompt: str,
        *,
        schema: dict,
        system_prompt: str | None = None,
        schema_name: str = "structured_response",
    ) -> dict:
        payload = self.responses.pop(0)
        self._last_generation = StructuredGenerationCapture(
            raw_text=json.dumps(payload),
            parsed_json=payload,
        )
        return payload


def test_mocked_end_to_end_concept_pipeline(tmp_path, monkeypatch):
    trend_payload = {
        "winning_formats": ["result-first experiments"],
        "declining_formats": ["generic top-10 lists"],
        "hook_patterns": ["I tested this so you do not waste money"],
        "thumbnail_patterns": ["one face plus one bold metric"],
        "content_gaps": ["practical workflows for freelancers"],
        "exploit_list": ["show a concrete outcome early"],
        "avoid_list": ["slow context-heavy intros"],
        "opportunity_map": ["Own fast implementation content"],
    }
    concept_payload = {
        "concepts": [
            {
                "concept_id": f"concept_0{i}",
                "format": "experiment" if i == 1 else "challenge",
                "title_options": [
                    f"Title {i}A",
                    f"Title {i}B",
                    f"Title {i}C",
                ],
                "premise": f"Premise {i} for practical viewers with clear payoff.",
                "hook_script": f"Hook {i} with a concrete stake and surprise.",
                "thumbnail_seed": f"face, metric, concept {i}",
                "predicted_ctr_range": "7-11%" if i != 3 else "8-12%",
                "predicted_avd_range": "42-55%",
                "why_it_should_work": f"Reason {i} explains why this should work for the audience.",
            }
            for i in range(1, 6)
        ]
    }
    script_payload = {
        "video_title": "Title 3A",
        "target_length_min": 10,
        "hook": {
            "start_sec": 0,
            "end_sec": 30,
            "spoken_words": "Hook 3 with a concrete stake and surprise.",
            "hook_type": "stakes + curiosity gap",
        },
        "segments": [
            {
                "segment_id": "seg_01",
                "start_sec": 0,
                "end_sec": 30,
                "purpose": "hook and promise",
                "spoken_script": "Hook 3 with a concrete stake and surprise.",
                "retention_device": "curiosity gap",
                "emotion": "high curiosity",
                "visual_intent": "opening montage plus creator framing",
                "drop_risk": "low",
                "why_viewer_stays": "The promise lands immediately with clear stakes.",
            },
            {
                "segment_id": "seg_02",
                "start_sec": 30,
                "end_sec": 120,
                "purpose": "set stakes",
                "spoken_script": "Here are the rules, the deadline, and what success means.",
                "retention_device": "challenge framing",
                "emotion": "tension",
                "visual_intent": "timeline and constraints card",
                "drop_risk": "low",
                "why_viewer_stays": "The viewer understands how the challenge will be judged.",
            },
            {
                "segment_id": "seg_03",
                "start_sec": 120,
                "end_sec": 300,
                "purpose": "first complications",
                "spoken_script": "The early setup looked easy until the first real failure appeared.",
                "retention_device": "surprise turn",
                "emotion": "surprise",
                "visual_intent": "failure proof and reaction beats",
                "drop_risk": "medium",
                "why_viewer_stays": "The apparent win turns into a problem that needs solving.",
            },
            {
                "segment_id": "seg_04",
                "start_sec": 300,
                "end_sec": 540,
                "purpose": "deeper escalation",
                "spoken_script": "The clock got tighter, and every shortcut created a new tradeoff.",
                "retention_device": "stakes escalation",
                "emotion": "pressure",
                "visual_intent": "side-by-side comparison progression",
                "drop_risk": "medium",
                "why_viewer_stays": "The audience wants to see whether the deadline can still be met.",
            },
            {
                "segment_id": "seg_05",
                "start_sec": 540,
                "end_sec": 600,
                "purpose": "payoff and takeaway",
                "spoken_script": "Here is what actually worked, what failed, and what I would reuse.",
                "retention_device": "payoff reveal",
                "emotion": "resolution",
                "visual_intent": "final winner reveal and recommendation card",
                "drop_risk": "low",
                "why_viewer_stays": "The promised result finally arrives with practical takeaways.",
            },
        ],
        "mid_video_hooks": [
            {
                "time_sec": 135,
                "line": "The first setback changed the whole challenge.",
                "purpose": "re-engage after setup",
            },
            {
                "time_sec": 360,
                "line": "At this point the deadline started to matter.",
                "purpose": "reset stakes before payoff",
            },
        ],
        "cta": {
            "time_sec": 580,
            "line": "Subscribe and watch the next workflow breakdown.",
            "goal": "Subscribe and watch the next workflow breakdown.",
        },
        "retention_summary": {
            "opening_strategy": "Lead with consequence-driven promise.",
            "reengagement_points": [
                "2:15 setback reveal",
                "6:00 deadline pressure reset"
            ],
            "payoff_strategy": "Resolve with ranked winner and practical next step."
        },
    }
    voice_payload = {
        "voice_style": "high-energy but analytical with clean conversational delivery",
        "music_direction": "modern cinematic pulse with subtle tech texture",
        "sfx_cues": [
            {"time_sec": 3, "cue": "subtle impact hit", "purpose": "signal opening hook"},
            {"time_sec": 120, "cue": "short riser", "purpose": "mark first re-engagement"},
            {"time_sec": 580, "cue": "resolve swell", "purpose": "support closing CTA"},
        ],
        "voiceover_segments": [
            {
                "segment_id": "seg_01",
                "vo_text": "Hook 3 with a concrete stake and surprise.",
                "emotion": "high curiosity",
                "pace": "fast",
                "emphasis_words": ["Hook", "concrete", "surprise"],
                "breath_points": [8, 18],
                "timing_notes": "Punch the opener and pause before the consequence.",
            },
            {
                "segment_id": "seg_02",
                "vo_text": "Here are the rules, the deadline, and what success means.",
                "emotion": "tension",
                "pace": "medium",
                "emphasis_words": ["rules", "deadline", "success"],
                "breath_points": [30, 60],
                "timing_notes": "Keep cadence crisp to preserve momentum.",
            },
            {
                "segment_id": "seg_03",
                "vo_text": "The early setup looked easy until the first real failure appeared.",
                "emotion": "surprise",
                "pace": "medium",
                "emphasis_words": ["easy", "failure"],
                "breath_points": [50, 110],
                "timing_notes": "Increase intensity at the reversal line.",
            },
            {
                "segment_id": "seg_04",
                "vo_text": "The clock got tighter, and every shortcut created a new tradeoff.",
                "emotion": "pressure",
                "pace": "medium",
                "emphasis_words": ["clock", "shortcut", "tradeoff"],
                "breath_points": [70, 140],
                "timing_notes": "Slightly quicken pace into each new tradeoff.",
            },
            {
                "segment_id": "seg_05",
                "vo_text": "Here is what actually worked, what failed, and what I would reuse.",
                "emotion": "resolution",
                "pace": "medium",
                "emphasis_words": ["worked", "failed", "reuse"],
                "breath_points": [20, 45],
                "timing_notes": "Slow down on the final recommendation.",
            },
        ],
    }
    fake_llm = FakeLLMClient([trend_payload, concept_payload, script_payload, voice_payload])

    monkeypatch.setattr("app.orchestrator.create_llm_client", lambda settings: fake_llm)

    orchestrator = PipelineOrchestrator(output_root=tmp_path)
    package = orchestrator.run(
        brief_path=Path("examples/channel_brief.json"),
        project_name="demo_run",
    )

    output_dir = tmp_path / "demo_run"
    assert package.project_name == "demo_run"
    assert (output_dir / "01_trends.json").exists()
    assert (output_dir / "02_concepts.json").exists()
    assert (output_dir / "03_selected_concept.json").exists()
    assert (output_dir / "04_script.json").exists()
    assert (output_dir / "05_voiceover.json").exists()
    assert (output_dir / "06_final_package.json").exists()
    assert (output_dir / "07_script_voice_package.json").exists()
    assert (output_dir / "08_concept_package.json").exists()
    assert package.script.video_title == "Title 3A"
    assert (output_dir / "_artifacts" / "trend" / "trend.latest.raw.txt").exists()
    assert (output_dir / "_artifacts" / "concept" / "concept.latest.validated.json").exists()
    assert (output_dir / "_artifacts" / "script" / "script.latest.validated.json").exists()
    assert (output_dir / "_artifacts" / "voiceover" / "voiceover.latest.validated.json").exists()
