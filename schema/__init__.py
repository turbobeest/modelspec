"""Value-free diagnostics when parsing private catalogue files."""

from __future__ import annotations

import os
from pathlib import Path


def private_data(path: Path | None = None) -> bool:
    if os.environ.get("MODELSPEC_REQUIRE_DATA_DIR") or os.environ.get("MODELSPEC_DATA_DIR"):
        return True
    if path is None:
        return False
    root = Path(__file__).resolve().parent.parent
    return not path.absolute().is_relative_to(root) or not path.resolve().is_relative_to(root)


def redacted_error(
    exc: Exception,
    path: Path | None = None,
    *,
    line_offset: int = 0,
    content: str | None = None,
    field_prefix: tuple[str | int, ...] = (),
) -> str:
    """Keep location and error class, never exception text or input values."""
    mark = getattr(exc, "problem_mark", None)
    line = mark.line + 1 + line_offset if mark is not None else 1
    if mark is None and content is not None and hasattr(exc, "errors"):
        import yaml

        parts = content.split("---", 2)
        node = yaml.compose(parts[1] if len(parts) >= 3 else content)
        errors = exc.errors(include_input=False, include_context=False, include_url=False)
        if errors:
            fields = list(field_prefix) + list(errors[0]["loc"])
            if fields and fields[0] == "identity":
                fields.pop(0)
            for field in fields:
                if isinstance(node, yaml.MappingNode):
                    pair = next(
                        ((key, value) for key, value in node.value if key.value == field), None
                    )
                    if pair is None:
                        break
                    key, node = pair
                    line = key.start_mark.line + 1
                elif (
                    isinstance(node, yaml.SequenceNode)
                    and isinstance(field, int)
                    and field < len(node.value)
                ):
                    node = node.value[field]
                    line = node.start_mark.line + 1
                else:
                    break
    location = str(path) if path is not None else "front matter"
    return f"{location}: line {line}: invalid data ({type(exc).__name__}); values redacted"
