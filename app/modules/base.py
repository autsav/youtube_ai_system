from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from pydantic import BaseModel

from app.utils.io import write_json


class PipelineModule(ABC):
    name: str
    output_filename: str

    @abstractmethod
    def run(self, **kwargs) -> BaseModel:
        raise NotImplementedError

    def save(self, output_dir: Path, artifact: BaseModel) -> Path:
        path = output_dir / self.output_filename
        write_json(path, artifact.model_dump(mode="json"))
        return path
