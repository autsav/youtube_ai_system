from __future__ import annotations

import json
from json import JSONDecodeError
from typing import Any


def parse_json_object(raw_text: str) -> dict[str, Any]:
    text = raw_text.strip()
    if not text:
        raise ValueError("LLM returned an empty response")

    try:
        parsed = json.loads(text)
    except JSONDecodeError:
        candidate = _extract_first_json_object(text)
        try:
            parsed = json.loads(candidate)
        except JSONDecodeError as exc:
            raise ValueError("LLM response was not valid JSON") from exc

    if not isinstance(parsed, dict):
        raise ValueError("Structured response must be a JSON object")
    return parsed


def _extract_first_json_object(text: str) -> str:
    start = text.find("{")
    if start == -1:
        raise ValueError("No JSON object found in LLM response")

    depth = 0
    in_string = False
    escape = False
    for index in range(start, len(text)):
        char = text[index]
        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                in_string = False
            continue

        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start : index + 1]

    raise ValueError("No complete JSON object found in LLM response")
