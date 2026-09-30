"""MODEL-246: a public workflow that can read the private data must not leak it.

Actions logs on a public repository are public and any signed-in user can
download an uploaded artifact. A job that holds `MODELSPEC_DATA_TOKEN` (or checks
out `modelspec-data`) therefore never uploads an artifact and never prints data.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

from pipeline.data_source import DATA_PATHS

WORKFLOWS = sorted((Path(__file__).resolve().parent.parent / ".github" / "workflows").glob("*.yml"))
MARKERS = ("MODELSPEC_DATA_TOKEN", "modelspec-data")
# A shell line that prints file content or a diff.
PRINTS = re.compile(r"\b(cat|head|tail|less|more|echo|printf|git\s+(diff|show|log|blame))\b|::(notice|warning|error)::")
DATA_WORDS = tuple(p.split("/")[-1] if "." in p else p for p in DATA_PATHS) + ("modelspec-data",)


def _reaches_data(job: dict) -> bool:
    text = yaml.safe_dump(job)
    return any(m in text for m in MARKERS)


def leaks(job: dict) -> list[str]:
    """Problems in one job, empty when it cannot leak."""
    if not _reaches_data(job):
        return []
    problems = []
    for step in job.get("steps", []):
        if "upload-artifact" in str(step.get("uses", "")):
            problems.append(f"uploads an artifact ({step.get('name', 'unnamed step')})")
        for line in str(step.get("run", "")).splitlines():
            if PRINTS.search(line) and any(word in line for word in DATA_WORDS):
                problems.append(f"prints data: {line.strip()[:80]}")
    return problems


def _jobs():
    for path in WORKFLOWS:
        doc = yaml.safe_load(path.read_text())
        for name, job in (doc.get("jobs") or {}).items():
            yield pytest.param(job, id=f"{path.name}:{name}")


@pytest.mark.parametrize("job", _jobs())
def test_a_job_that_reaches_the_private_data_does_not_leak_it(job):
    assert leaks(job) == []


def test_the_guard_catches_an_artifact_upload():
    job = {"steps": [
        {"uses": "actions/checkout@v4", "with": {"repository": "turbobeest/modelspec-data",
                                                   "token": "${{ secrets.MODELSPEC_DATA_TOKEN }}"}},
        {"name": "keep", "uses": "actions/upload-artifact@v4", "with": {"path": "dist"}},
    ]}
    assert any("uploads an artifact" in p for p in leaks(job))


def test_the_guard_catches_printed_data():
    job = {"steps": [
        {"uses": "actions/checkout@v4", "with": {"token": "${{ secrets.MODELSPEC_DATA_TOKEN }}"}},
        {"run": "cat modelspec-data/models/a.md\necho done"},
    ]}
    assert len(leaks(job)) == 1


def test_a_job_that_never_touches_the_data_is_left_alone():
    job = {"steps": [{"uses": "actions/upload-artifact@v4"}, {"run": "cat models/a.md"}]}
    assert leaks(job) == []
