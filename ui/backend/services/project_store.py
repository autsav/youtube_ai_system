from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from app.schemas.models import (
    ChannelBrief,
    ConceptBatch,
    FinalPackage,
    ScriptArtifact,
    SelectedConcept,
    TrendReport,
    VideoPromptArtifact,
)
from app.utils.io import ensure_dir, read_json, write_json


class ProjectStore:
    """File-based project storage."""

    def __init__(self, output_root: Path) -> None:
        self.output_root = Path(output_root)

    def _project_path(self, project_id: str) -> Path:
        return self.output_root / project_id

    def _project_meta_path(self, project_id: str) -> Path:
        return self._project_path(project_id) / ".project.json"

    def create_project(self, name: str, brief: ChannelBrief) -> str:
        """Create a new project and return its ID."""
        project_id = str(uuid.uuid4())[:8]
        project_path = self._project_path(project_id)
        ensure_dir(project_path)

        now = datetime.now().isoformat()
        meta = {
            "id": project_id,
            "name": name,
            "status": "created",
            "current_step": 0,
            "created_at": now,
            "updated_at": now,
        }

        write_json(self._project_meta_path(project_id), meta)
        write_json(project_path / "brief.json", brief.model_dump(mode="json"))

        return project_id

    def get_project(self, project_id: str) -> dict[str, Any] | None:
        """Get project metadata."""
        meta_path = self._project_meta_path(project_id)
        if not meta_path.exists():
            return None
        return read_json(meta_path)

    def get_project_brief(self, project_id: str) -> ChannelBrief | None:
        """Get project brief."""
        brief_path = self._project_path(project_id) / "brief.json"
        if not brief_path.exists():
            return None
        return ChannelBrief.model_validate(read_json(brief_path))

    def list_projects(self) -> list[dict[str, Any]]:
        """List all projects."""
        projects = []
        if not self.output_root.exists():
            return projects

        for project_dir in self.output_root.iterdir():
            if project_dir.is_dir():
                meta_path = project_dir / ".project.json"
                if meta_path.exists():
                    projects.append(read_json(meta_path))
        return sorted(projects, key=lambda p: p.get("created_at", ""), reverse=True)

    def update_status(self, project_id: str, status: str, step: int) -> None:
        """Update project status."""
        meta = self.get_project(project_id)
        if meta:
            meta["status"] = status
            meta["current_step"] = step
            meta["updated_at"] = datetime.now().isoformat()
            write_json(self._project_meta_path(project_id), meta)

    # Pipeline artifact methods

    def get_trends(self, project_id: str) -> TrendReport | None:
        path = self._project_path(project_id) / "01_trends.json"
        if path.exists():
            return TrendReport.model_validate(read_json(path))
        return None

    def get_concepts(self, project_id: str) -> ConceptBatch | None:
        path = self._project_path(project_id) / "02_concepts.json"
        if path.exists():
            return ConceptBatch.model_validate(read_json(path))
        return None

    def get_selection(self, project_id: str) -> SelectedConcept | None:
        path = self._project_path(project_id) / "03_selected_concept.json"
        if path.exists():
            return SelectedConcept.model_validate(read_json(path))
        return None

    def get_script(self, project_id: str) -> ScriptArtifact | None:
        path = self._project_path(project_id) / "04_script.json"
        if path.exists():
            return ScriptArtifact.model_validate(read_json(path))
        return None

    def get_video_prompts(self, project_id: str) -> VideoPromptArtifact | None:
        path = self._project_path(project_id) / "05_video_prompts.json"
        if path.exists():
            return VideoPromptArtifact.model_validate(read_json(path))
        return None

    def get_final_package(self, project_id: str) -> FinalPackage | None:
        path = self._project_path(project_id) / "final_package.json"
        if path.exists():
            return FinalPackage.model_validate(read_json(path))
        return None

    def check_artifacts_exist(self, project_id: str) -> dict[str, bool]:
        """Check which artifacts exist for a project."""
        project_path = self._project_path(project_id)
        return {
            "trends": (project_path / "01_trends.json").exists(),
            "concepts": (project_path / "02_concepts.json").exists(),
            "selection": (project_path / "03_selected_concept.json").exists(),
            "script": (project_path / "04_script.json").exists(),
            "video_prompts": (project_path / "05_video_prompts.json").exists(),
            "final_package": (project_path / "final_package.json").exists(),
        }
