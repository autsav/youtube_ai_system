from __future__ import annotations

from pathlib import Path
from rich.console import Console

from app.config import settings
from app.llm.factory import create_llm_client
from app.modules.video_prompt import VideoPromptModule
from app.schemas.models import FinalPackage
from app.modules.brief import load_brief
from app.modules.trend import TrendModule
from app.modules.concept import ConceptModule, SelectorModule
from app.modules.script import ScriptModule
from app.utils.io import ensure_dir, write_json
from app.utils.artifact_store import save_llm_stage_artifacts

console = Console()


class PipelineOrchestrator:
    def __init__(self, output_root: Path) -> None:
        self.output_root = output_root

    def run(self, *, brief_path: Path, project_name: str) -> FinalPackage:
        output_dir = self.output_root / project_name
        ensure_dir(output_dir)

        console.print(f"[bold cyan]Loading brief[/bold cyan]: {brief_path}")
        brief = load_brief(brief_path)
        llm_client = create_llm_client(settings)

        trend_module = TrendModule(llm_client=llm_client)
        concept_module = ConceptModule(llm_client=llm_client)
        selector_module = SelectorModule(llm_client=llm_client)
        script_module = ScriptModule(llm_client=llm_client)
        video_prompt_module = VideoPromptModule(llm_client=llm_client)

        trends = trend_module.run(brief=brief)
        trend_module.save(output_dir, trends)
        if trend_module.last_llm_artifacts is not None:
            save_llm_stage_artifacts(output_dir, trend_module.last_llm_artifacts)

        concepts = concept_module.run(brief=brief, trends=trends)
        concept_module.save(output_dir, concepts)
        if concept_module.last_llm_artifacts is not None:
            save_llm_stage_artifacts(output_dir, concept_module.last_llm_artifacts)

        selected = selector_module.run(concept_batch=concepts)
        selector_module.save(output_dir, selected)
        if selector_module.last_llm_artifacts is not None:
            save_llm_stage_artifacts(output_dir, selector_module.last_llm_artifacts)

        script = script_module.run(brief=brief, selected_concept=selected)
        script_module.save(output_dir, script)
        if script_module.last_llm_artifacts is not None:
            save_llm_stage_artifacts(output_dir, script_module.last_llm_artifacts)

        video_prompts = video_prompt_module.run(
            brief=brief,
            selected_concept=selected,
            script=script,
            output_dir=output_dir,
        )
        # Also save legacy format for backwards compatibility
        video_prompt_module.save(output_dir, video_prompts)
        if video_prompt_module.last_llm_artifacts is not None:
            save_llm_stage_artifacts(output_dir, video_prompt_module.last_llm_artifacts)

        final_package = FinalPackage(
            project_name=project_name,
            trend_report=trends,
            concepts=concepts,
            selected_concept=selected,
            script=script,
            video_prompts=video_prompts,
        )
        write_json(output_dir / "final_package.json", final_package.model_dump(mode="json"))
        console.print(f"[bold green]Done[/bold green]. Output written to {output_dir}")
        return final_package
