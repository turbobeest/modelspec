"""Value-free diagnostics when parsing private catalogue files."""

from __future__ import annotations

import os
import sys
from contextlib import contextmanager
from pathlib import Path


def private_data(path: Path | None = None) -> bool:
    if any(arg == "--data-dir" or arg.startswith("--data-dir=") for arg in sys.argv):
        return True
    if os.environ.get("MODELSPEC_REQUIRE_DATA_DIR") or os.environ.get("MODELSPEC_DATA_DIR"):
        return True
    if path is None:
        path = Path(__file__).resolve().parent.parent
    try:
        for parent in (path, *path.parents):
            config = parent / ".git/config"
            if config.is_file() and "turbobeest/modelspec-data" in config.read_text():
                return True
        root = Path(__file__).resolve().parent.parent
        if "modelspec-data" in path.absolute().parts or "modelspec-data" in path.resolve().parts:
            return True
        return not path.absolute().is_relative_to(root) or not path.resolve().is_relative_to(root)
    except Exception:
        return True


def redacted_error(
    exc: Exception,
    path: Path | None = None,
    *,
    line_offset: int = 0,
    content: str | None = None,
    field_prefix: tuple[str | int, ...] = (),
) -> str:
    """Keep location and error class, never exception text or input values."""
    line = 1
    try:
        mark = getattr(exc, "problem_mark", None) or getattr(exc.__cause__, "problem_mark", None)
        line = mark.line + 1 + line_offset if mark is not None else 1
        if mark is None and content is not None and hasattr(exc, "errors"):
            import yaml

            content_offset = 0
            lines = content.splitlines()
            if lines and lines[0].strip() == "---":
                end = next(i for i, text in enumerate(lines[1:], 1) if text.strip() == "---")
                content = "\n".join(lines[1:end])
                content_offset = 1
            node = yaml.compose(content)
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
                        line = key.start_mark.line + 1 + content_offset
                    elif (
                        isinstance(node, yaml.SequenceNode)
                        and isinstance(field, int)
                        and field < len(node.value)
                    ):
                        node = node.value[field]
                        line = node.start_mark.line + 1 + content_offset
                    else:
                        break
    except Exception:
        line = 1
    location = str(path) if path is not None else "front matter"
    return f"{location}: line {line}: invalid data ({type(exc).__name__}); values redacted"


@contextmanager
def private_errors(path: Path, *, line: int | None = None, error_type=ValueError):
    """One diagnostic boundary for private file loaders, including validation failures."""
    try:
        yield
    except Exception as exc:
        if getattr(exc, "_modelspec_redacted", False) or not private_data(path):
            raise
        path = getattr(exc, "_modelspec_path", path)
        message = redacted_error(exc, path)
        if line is not None:
            message = f"{path}: line {line}: invalid data ({type(exc).__name__}); values redacted"
        error = error_type(message)
        error._modelspec_redacted = True
        raise error from None
