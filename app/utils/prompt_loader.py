from __future__ import annotations

from pathlib import Path
from string import Formatter
from typing import Any


_FORMATTER = Formatter()


class PromptTemplateError(ValueError):
    pass


def load_prompt_template(path: str | Path, **variables: Any) -> str:
    template_path = Path(path)
    try:
        template = template_path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"Prompt template not found: {template_path}") from exc

    missing_variables = sorted(_find_missing_variables(template, variables))
    if missing_variables:
        missing = ", ".join(missing_variables)
        raise PromptTemplateError(
            f"Missing variables for prompt template {template_path}: {missing}"
        )

    try:
        return template.format(**variables)
    except KeyError as exc:
        raise PromptTemplateError(
            f"Missing variable for prompt template {template_path}: {exc.args[0]}"
        ) from exc
    except ValueError as exc:
        raise PromptTemplateError(f"Invalid prompt template syntax in {template_path}: {exc}") from exc


def _find_missing_variables(template: str, variables: dict[str, Any]) -> set[str]:
    missing: set[str] = set()
    for _, field_name, _, _ in _FORMATTER.parse(template):
        if not field_name:
            continue

        root_name = field_name.split(".", 1)[0].split("[", 1)[0]
        if root_name not in variables:
            missing.add(root_name)

    return missing
