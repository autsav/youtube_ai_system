from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from fastapi import APIRouter, Depends, HTTPException, status

from api.dependencies import get_llm_client, get_project_store
from app.llm.base import LLMClient
from app.modules.concept import ConceptModule, SelectorModule
from app.modules.script import ScriptModule
from app.modules.trend import TrendModule
from app.modules.video_prompt import VideoPromptModule
from app.schemas.models import FinalPackage
from schemas.api_models import (
    ConceptsDataResponse,
    FinalPackageDataResponse,
    GenerateConceptsResponse,
    GenerateScriptResponse,
    GenerateVideoPromptsResponse,
    ScriptDataResponse,
    SelectConceptRequest,
    SelectConceptResponse,
    SelectionDataResponse,
    TrendsDataResponse,
    VideoPromptsDataResponse,
)
from services.project_store import ProjectStore

router = APIRouter(prefix="/projects", tags=["pipeline"])


@router.post("/{project_id}/generate-concepts", response_model=GenerateConceptsResponse)
def generate_concepts(
    project_id: str,
    store: ProjectStore = Depends(get_project_store),
    llm_client: LLMClient = Depends(get_llm_client),
) -> GenerateConceptsResponse:
    """Generate concepts for a project."""
    project = store.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    brief = store.get_project_brief(project_id)
    if brief is None:
        raise HTTPException(status_code=404, detail="Project brief not found")

    try:
        # Generate trends first (required for concepts)
        trend_module = TrendModule(llm_client=llm_client)
        trends = trend_module.run(brief=brief)

        # Save trends
        from app.utils.io import write_json
        from pathlib import Path
        project_path = Path(store.output_root) / project_id
        write_json(project_path / "01_trends.json", trends.model_dump(mode="json"))

        # Generate concepts
        concept_module = ConceptModule(llm_client=llm_client)
        concepts = concept_module.run(brief=brief, trends=trends)
        concept_module.save(project_path, concepts)

        # Update project status
        store.update_status(project_id, "concepts_generated", 1)

        return GenerateConceptsResponse(success=True, concepts=concepts, error=None)
    except Exception as e:
        return GenerateConceptsResponse(success=False, concepts=None, error=str(e))


@router.post("/{project_id}/select-concept", response_model=SelectConceptResponse)
def select_concept(
    project_id: str,
    request: SelectConceptRequest,
    store: ProjectStore = Depends(get_project_store),
    llm_client: LLMClient = Depends(get_llm_client),
) -> SelectConceptResponse:
    """Select a winning concept."""
    project = store.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    concepts = store.get_concepts(project_id)
    if concepts is None:
        raise HTTPException(status_code=400, detail="Concepts not generated yet")

    try:
        # Validate concept_id exists
        concept_ids = [c.concept_id for c in concepts.concepts]
        if request.concept_id not in concept_ids:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid concept_id. Must be one of: {concept_ids}"
            )

        # Use SelectorModule to get full selection with scores
        selector_module = SelectorModule(llm_client=llm_client)
        selection = selector_module.run(concept_batch=concepts)

        # Override with user's choice if different
        if selection.winner_id != request.concept_id:
            for concept in concepts.concepts:
                if concept.concept_id == request.concept_id:
                    selection.winner_id = request.concept_id
                    selection.winner = concept
                    selection.winner_reason = "User selected this concept"
                    break

        # Save selection
        from app.utils.io import write_json
        from pathlib import Path
        project_path = Path(store.output_root) / project_id
        write_json(project_path / "03_selected_concept.json", selection.model_dump(mode="json"))

        # Update project status
        store.update_status(project_id, "concept_selected", 2)

        return SelectConceptResponse(success=True, selection=selection, error=None)
    except HTTPException:
        raise
    except Exception as e:
        return SelectConceptResponse(success=False, selection=None, error=str(e))


@router.post("/{project_id}/generate-script", response_model=GenerateScriptResponse)
def generate_script(
    project_id: str,
    store: ProjectStore = Depends(get_project_store),
    llm_client: LLMClient = Depends(get_llm_client),
) -> GenerateScriptResponse:
    """Generate script for selected concept."""
    project = store.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    brief = store.get_project_brief(project_id)
    if brief is None:
        raise HTTPException(status_code=404, detail="Project brief not found")

    selection = store.get_selection(project_id)
    if selection is None:
        raise HTTPException(status_code=400, detail="Concept not selected yet")

    try:
        script_module = ScriptModule(llm_client=llm_client)
        script = script_module.run(brief=brief, selected_concept=selection)

        # Save script
        from app.utils.io import write_json
        from pathlib import Path
        project_path = Path(store.output_root) / project_id
        write_json(project_path / "04_script.json", script.model_dump(mode="json"))

        # Update project status
        store.update_status(project_id, "script_generated", 3)

        return GenerateScriptResponse(success=True, script=script, error=None)
    except Exception as e:
        return GenerateScriptResponse(success=False, script=None, error=str(e))


@router.post("/{project_id}/generate-video-prompts", response_model=GenerateVideoPromptsResponse)
def generate_video_prompts(
    project_id: str,
    store: ProjectStore = Depends(get_project_store),
    llm_client: LLMClient = Depends(get_llm_client),
) -> GenerateVideoPromptsResponse:
    """Generate video prompts from script."""
    project = store.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    brief = store.get_project_brief(project_id)
    if brief is None:
        raise HTTPException(status_code=404, detail="Project brief not found")

    selection = store.get_selection(project_id)
    if selection is None:
        raise HTTPException(status_code=400, detail="Concept not selected yet")

    script = store.get_script(project_id)
    if script is None:
        raise HTTPException(status_code=400, detail="Script not generated yet")

    try:
        video_prompt_module = VideoPromptModule(llm_client=llm_client)
        video_prompts = video_prompt_module.run(
            brief=brief,
            selected_concept=selection,
            script=script,
            output_dir=None,
        )

        # Save video prompts
        from app.utils.io import write_json
        from pathlib import Path
        project_path = Path(store.output_root) / project_id
        video_prompt_module.save(project_path, video_prompts)

        # Create and save final package
        trends = store.get_trends(project_id)
        concepts = store.get_concepts(project_id)

        final_package = FinalPackage(
            project_name=project["name"],
            trend_report=trends or TrendReport(),
            concepts=concepts or ConceptBatch(),
            selected_concept=selection,
            script=script,
            video_prompts=video_prompts,
        )
        write_json(project_path / "final_package.json", final_package.model_dump(mode="json"))

        # Update project status
        store.update_status(project_id, "complete", 4)

        return GenerateVideoPromptsResponse(success=True, video_prompts=video_prompts, error=None)
    except Exception as e:
        return GenerateVideoPromptsResponse(success=False, video_prompts=None, error=str(e))


# Data fetch endpoints

@router.get("/{project_id}/trends", response_model=TrendsDataResponse)
def get_trends(
    project_id: str,
    store: ProjectStore = Depends(get_project_store),
) -> TrendsDataResponse:
    """Get trends for a project."""
    trends = store.get_trends(project_id)
    return TrendsDataResponse(exists=trends is not None, trends=trends)


@router.get("/{project_id}/concepts", response_model=ConceptsDataResponse)
def get_concepts(
    project_id: str,
    store: ProjectStore = Depends(get_project_store),
) -> ConceptsDataResponse:
    """Get concepts for a project."""
    concepts = store.get_concepts(project_id)
    return ConceptsDataResponse(exists=concepts is not None, concepts=concepts)


@router.get("/{project_id}/selection", response_model=SelectionDataResponse)
def get_selection(
    project_id: str,
    store: ProjectStore = Depends(get_project_store),
) -> SelectionDataResponse:
    """Get concept selection for a project."""
    selection = store.get_selection(project_id)
    return SelectionDataResponse(exists=selection is not None, selection=selection)


@router.get("/{project_id}/script", response_model=ScriptDataResponse)
def get_script(
    project_id: str,
    store: ProjectStore = Depends(get_project_store),
) -> ScriptDataResponse:
    """Get script for a project."""
    script = store.get_script(project_id)
    return ScriptDataResponse(exists=script is not None, script=script)


@router.get("/{project_id}/video-prompts", response_model=VideoPromptsDataResponse)
def get_video_prompts(
    project_id: str,
    store: ProjectStore = Depends(get_project_store),
) -> VideoPromptsDataResponse:
    """Get video prompts for a project."""
    video_prompts = store.get_video_prompts(project_id)
    return VideoPromptsDataResponse(exists=video_prompts is not None, video_prompts=video_prompts)


@router.get("/{project_id}/final-package", response_model=FinalPackageDataResponse)
def get_final_package(
    project_id: str,
    store: ProjectStore = Depends(get_project_store),
) -> FinalPackageDataResponse:
    """Get final package for a project."""
    final_package = store.get_final_package(project_id)
    return FinalPackageDataResponse(exists=final_package is not None, final_package=final_package)
