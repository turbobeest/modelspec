"""Shared operator commands for API-key records in Workers KV."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKER_ROOT = REPO_ROOT / "api" / "worker"
WORKER_SRC = WORKER_ROOT / "src"
DEFAULT_WRANGLER_CONFIG = WORKER_ROOT / "wrangler.jsonc"
ACCESS_BINDING = "ACCESS"


class OperatorKeyError(ValueError):
    """The operator command cannot safely construct the requested operation."""


def _without_json_comments(text: str) -> str:
    """Remove JSONC line comments without changing strings that contain `//`."""
    output: list[str] = []
    in_string = False
    escaped = False
    index = 0
    while index < len(text):
        char = text[index]
        if in_string:
            output.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            index += 1
            continue
        if char == '"':
            in_string = True
            output.append(char)
            index += 1
            continue
        if char == "/" and index + 1 < len(text) and text[index + 1] == "/":
            newline = text.find("\n", index + 2)
            if newline == -1:
                break
            output.append("\n")
            index = newline + 1
            continue
        output.append(char)
        index += 1
    return "".join(output)


def access_binding(config: Path = DEFAULT_WRANGLER_CONFIG) -> str:
    """Return the Worker's API-key KV binding from its Wrangler config."""
    try:
        decoded: Any = json.loads(_without_json_comments(config.read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError) as exc:
        raise OperatorKeyError(f"cannot read Wrangler config {config}: {exc}") from None
    namespaces = decoded.get("kv_namespaces") if isinstance(decoded, dict) else None
    if not isinstance(namespaces, list):
        raise OperatorKeyError(f"Wrangler config {config} has no kv_namespaces list")
    bindings = [
        row.get("binding")
        for row in namespaces
        if isinstance(row, dict) and row.get("binding") == ACCESS_BINDING and row.get("id")
    ]
    if bindings != [ACCESS_BINDING]:
        raise OperatorKeyError(
            f"Wrangler config {config} must contain one {ACCESS_BINDING} KV binding with an id"
        )
    return ACCESS_BINDING


def wrangler_target(config: Path = DEFAULT_WRANGLER_CONFIG) -> list[str]:
    """Arguments that target the deployed API-key namespace."""
    return ["--binding", access_binding(config), "--remote", "--config", str(config)]
