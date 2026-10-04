"""Read the production Worker flags used while building static pages."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


WRANGLER_REL = Path("api/worker/wrangler.jsonc")
OFF_VALUES = {"", "0", "false", "no", "off"}


def _strip_jsonc_comments(text: str) -> str:
    """Remove JSONC comments without changing comment markers inside strings."""
    result: list[str] = []
    index = 0
    in_string = False
    escaped = False
    while index < len(text):
        char = text[index]
        following = text[index + 1] if index + 1 < len(text) else ""
        if in_string:
            result.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            index += 1
        elif char == '"':
            in_string = True
            result.append(char)
            index += 1
        elif char == "/" and following == "/":
            index += 2
            while index < len(text) and text[index] not in "\r\n":
                index += 1
        elif char == "/" and following == "*":
            index += 2
            while index + 1 < len(text) and text[index:index + 2] != "*/":
                index += 1
            index += 2
        else:
            result.append(char)
            index += 1
    return "".join(result)


def parse_jsonc(text: str) -> dict[str, Any]:
    """Parse the JSONC subset accepted by Wrangler."""
    without_comments = _strip_jsonc_comments(text)
    result: list[str] = []
    in_string = False
    escaped = False
    for index, char in enumerate(without_comments):
        if in_string:
            result.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
            result.append(char)
            continue
        if char == ",":
            following = without_comments[index + 1:].lstrip()
            if following.startswith(("}", "]")):
                continue
        result.append(char)
    without_trailing_commas = "".join(result)
    parsed = json.loads(without_trailing_commas)
    if not isinstance(parsed, dict):
        raise ValueError("Wrangler configuration must be a JSON object")
    return parsed


def production_vars(root: Path) -> dict[str, Any]:
    """Return only the top-level production vars, never an environment's vars."""
    config = parse_jsonc((Path(root) / WRANGLER_REL).read_text(encoding="utf-8"))
    variables = config.get("vars", {})
    if not isinstance(variables, dict):
        raise ValueError("Wrangler top-level vars must be a JSON object")
    return variables


def enabled(variables: dict[str, Any], name: str) -> bool:
    """Apply the Worker's flag rule. Missing and documented false values are off."""
    value = variables.get(name)
    return value is not None and str(value).strip().lower() not in OFF_VALUES


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Print whether a production Worker flag is enabled.")
    parser.add_argument("name")
    args = parser.parse_args()
    print(str(enabled(production_vars(Path(__file__).resolve().parents[1]), args.name)).lower())
