"""Publish only frozen pages and the public policy when data splitting is on."""
from pathlib import Path

# Deny new exports by default. Class-fit examples use only the frozen image.
KEEP_API = {"build.json", "rank/profiles.json", "rank/class-fit.json", "feedback/v1.schema.json"}


def restrict(tree: Path) -> None:
    """Remove bulk API routes."""
    api = tree / "api"
    for path in api.rglob("*"):
        if path.is_file() and path.relative_to(api).as_posix() not in KEEP_API:
            path.unlink()


def enabled() -> bool:
    """The operator-controlled serving switch, read at the build boundary."""
    import os
    return os.environ.get("DATA_SPLIT_ENABLED") == "true"
