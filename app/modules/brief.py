from __future__ import annotations

from pathlib import Path

from app.schemas.models import ChannelBrief
from app.utils.io import read_json


def load_brief(path: Path) -> ChannelBrief:
    return ChannelBrief.model_validate(read_json(path))
