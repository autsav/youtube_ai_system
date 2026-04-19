from __future__ import annotations

import pytest

from app.utils.prompt_loader import PromptTemplateError, load_prompt_template


def test_load_prompt_template_interpolates_variables(tmp_path):
    template_path = tmp_path / "prompt.txt"
    template_path.write_text("Hello {name}\nTopic: {topic}\n", encoding="utf-8")

    rendered = load_prompt_template(template_path, name="Utsab", topic="AI tools")

    assert rendered == "Hello Utsab\nTopic: AI tools\n"


def test_load_prompt_template_fails_on_missing_variables(tmp_path):
    template_path = tmp_path / "prompt.txt"
    template_path.write_text("Hello {name}\nTopic: {topic}\n", encoding="utf-8")

    with pytest.raises(PromptTemplateError, match="topic"):
        load_prompt_template(template_path, name="Utsab")
