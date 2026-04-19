from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from app.config import settings
from app.llm.factory import create_llm_client
from fastapi import Depends

from services.project_store import ProjectStore


# Singleton project store
_project_store: ProjectStore | None = None


def get_project_store() -> ProjectStore:
    """Dependency to get project store."""
    global _project_store
    if _project_store is None:
        # Use absolute path to repo root outputs directory
        repo_root = Path(__file__).parent.parent.parent.parent
        output_root = repo_root / "outputs"
        _project_store = ProjectStore(output_root)
    return _project_store


def get_llm_client():
    """Dependency to get LLM client."""
    return create_llm_client(settings)
