"""Structural validation using the published request schema, without an engine."""

from __future__ import annotations

import json
import sys
from importlib.resources import files
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator

from .errors import ClientError

SCHEMA = json.loads(files(__package__).joinpath("spec.schema.json").read_text(encoding="utf-8"))
VALIDATOR = Draft202012Validator(SCHEMA)
MAX_BYTES = 64 * 1024
# Duplicated from decision.bounded so this wheel stays engine-free.
# tests/test_decide_agent_budget.py asserts the tuples match.
DEFAULT_ROW_FIELDS = ("model_rank", "cost_per_task", "estimates", "p_best")
EXPLAIN_ROW_FIELDS = ("contributions", "evidence")


def load_spec(source: str) -> dict[str, Any]:
    try:
        if source == "-":
            text = sys.stdin.read(MAX_BYTES + 1)
        else:
            with Path(source).open(encoding="utf-8") as stream:
                text = stream.read(MAX_BYTES + 1)
        if len(text.encode("utf-8")) > MAX_BYTES:
            raise ClientError("spec_too_large", recovery="spec")
        try:
            value = json.loads(text)
        except ValueError:
            value = yaml.safe_load(text)
    except (OSError, UnicodeError, yaml.YAMLError, ValueError, RecursionError):
        raise ClientError("spec_unreadable", recovery="spec") from None
    validate_spec(value)
    return value


def validate_spec(value: Any) -> None:
    try:
        encoded = json.dumps(value, ensure_ascii=False, allow_nan=False)
        if len(encoded.encode("utf-8")) > MAX_BYTES:
            raise ClientError("spec_too_large", recovery="spec")
        issues = [
            {
                "path": ".".join(str(part) for part in error.absolute_path) or "$",
                "rule": error.validator,
            }
            for error in VALIDATOR.iter_errors(value)
        ]
    except (TypeError, ValueError, RecursionError):
        raise ClientError("invalid_spec", recovery="spec") from None
    if issues:
        raise ClientError("invalid_spec", recovery="spec", issues=issues)


def bound_decide_request(spec: dict[str, Any]) -> dict[str, Any]:
    """Add the bounded row list when the caller did not set ``fields``.

    An explicit ``fields`` value, including null, is sent unchanged. Explain
    and limit are left to the spec: an omitted explain is the server default,
    summary, so the list includes the explanation row fields.
    """
    if "fields" in spec:
        return spec
    explain = spec.get("explain", "summary")
    fields = list(DEFAULT_ROW_FIELDS)
    if explain in ("summary", "full"):
        fields.extend(EXPLAIN_ROW_FIELDS)
    return {**spec, "fields": fields}
