"""Publish only frozen pages and the public policy when data splitting is on."""
from pathlib import Path
import re
import shutil

# Deny new exports by default. Class-fit examples use only the frozen image.
KEEP_API = {"build.json", "rank/profiles.json", "rank/class-fit.json", "feedback/v1.schema.json"}


def restrict(tree: Path) -> None:
    """Remove bulk API routes. Graph assets are explicitly the frozen image."""
    api = tree / "api"
    graph = api / "graph"
    if graph.exists():
        shutil.copytree(graph, tree / "graph" / "data", dirs_exist_ok=True)
    for path in api.rglob("*"):
        if path.is_file() and path.relative_to(api).as_posix() not in KEEP_API:
            path.unlink()
    # Discovery must describe the remaining serving path. All generated pages
    # here were built from the public checkout, including llms-full.txt.
    for path in tree.rglob("*"):
        if not path.is_file() or path.suffix not in {".html", ".md", ".txt", ".json", ".yaml"}:
            continue
        text = path.read_text(encoding="utf-8")
        text = text.replace("/api/graph/", "/graph/data/")
        text = re.sub(r"(?:https://modelspec\.dev)?/api/(?:models|benchmarks)/[^\s\"'<>)`\]]+",
                      "https://api.modelspec.dev/v1/decide", text)
        # Match routes once instead of scanning thousands of removed paths.
        text = re.sub(
            r"(?:https://modelspec\.dev)?(/api/[^\s\"'<>)`\]]+)",
            lambda match: match.group(0) if match.group(1)[len("/api/"):] in KEEP_API
            else "https://api.modelspec.dev/v1/decide",
            text,
        )
        path.write_text(text, encoding="utf-8")
