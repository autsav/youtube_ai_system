from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from fastapi import APIRouter, Depends, HTTPException, status

from api.dependencies import get_project_store
from schemas.api_models import (
    CreateProjectRequest,
    ProjectDetailResponse,
    ProjectListResponse,
    ProjectResponse,
)
from services.project_store import ProjectStore

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    request: CreateProjectRequest,
    store: ProjectStore = Depends(get_project_store),
) -> ProjectResponse:
    """Create a new project with channel brief."""
    project_id = store.create_project(request.name, request.brief)
    project = store.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=500, detail="Failed to create project")

    return ProjectResponse(
        id=project["id"],
        name=project["name"],
        status=project["status"],
        current_step=project["current_step"],
        created_at=project["created_at"],
        updated_at=project["updated_at"],
    )


@router.get("", response_model=ProjectListResponse)
def list_projects(
    store: ProjectStore = Depends(get_project_store),
) -> ProjectListResponse:
    """List all projects."""
    projects = store.list_projects()
    return ProjectListResponse(
        projects=[
            ProjectResponse(
                id=p["id"],
                name=p["name"],
                status=p["status"],
                current_step=p["current_step"],
                created_at=p["created_at"],
                updated_at=p["updated_at"],
            )
            for p in projects
        ]
    )


@router.get("/{project_id}", response_model=ProjectDetailResponse)
def get_project(
    project_id: str,
    store: ProjectStore = Depends(get_project_store),
) -> ProjectDetailResponse:
    """Get project details with brief."""
    project = store.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    brief = store.get_project_brief(project_id)
    if brief is None:
        raise HTTPException(status_code=404, detail="Project brief not found")

    return ProjectDetailResponse(
        id=project["id"],
        name=project["name"],
        status=project["status"],
        current_step=project["current_step"],
        brief=brief,
        created_at=project["created_at"],
        updated_at=project["updated_at"],
    )
