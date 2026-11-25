"""Write the `alert` issue body for a red production Worker deploy (MODEL-487).

The workflow job that calls this has `issues: write` and nothing else. It
reads only `needs.deploy.result`. The failure class reaches it through the
deploy job's public check-run annotations, where `scripts/deploy_retry.py`
leaves one fixed line. Anything else found there, or no annotation at all,
is `unknown`.

The issue is public. Its body is four fixed fields: the workflow name, the run
URL, the commit of this public repository, and the failure class. No log text
reaches it.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.deploy_retry import ANNOTATION_KEY, CLASS_UNKNOWN, FAILURE_CLASSES  # noqa: E402

TITLE = "Rank Worker deploy failed"
LABEL = "alert"
JOB_NAME = "Deploy the rank Worker"

_WORKFLOW = re.compile(r"^[A-Za-z0-9 ._-]{1,64}$")
_COMMIT = re.compile(r"^[0-9a-f]{40}$")
_REPO = re.compile(r"^[A-Za-z0-9._-]+/[A-Za-z0-9._-]+$")
_RUN_ID = re.compile(r"^[0-9]{1,20}$")
_ANNOTATION = re.compile(rf"^{re.escape(ANNOTATION_KEY)}=([a-z-]+)$")

GhApi = Callable[[str], Any]


def failure_class(annotations: Sequence[Mapping[str, Any]]) -> str:
    """The one allow-listed class among the annotations, else `unknown`."""
    found = set()
    for annotation in annotations:
        message = annotation.get("message") if isinstance(annotation, Mapping) else None
        match = _ANNOTATION.match(message) if isinstance(message, str) else None
        if match:
            found.add(match.group(1))
    if len(found) == 1:
        (only,) = found
        if only in FAILURE_CLASSES:
            return only
    return CLASS_UNKNOWN


def body(workflow: str, run_url: str, commit: str, failure: str) -> str:
    """Four fixed fields. Each is validated; none is free text."""
    if not _WORKFLOW.match(workflow):
        raise ValueError("workflow name is not a plain name")
    if not re.match(r"^https://github\.com/[A-Za-z0-9._-]+/[A-Za-z0-9._-]+/actions/runs/[0-9]+$", run_url):
        raise ValueError("run URL is not a GitHub run URL")
    if not _COMMIT.match(commit):
        raise ValueError("commit is not a full SHA")
    failure = failure if failure in FAILURE_CLASSES else CLASS_UNKNOWN
    return (
        f"Workflow: {workflow}\n"
        f"Run: {run_url}\n"
        f"Commit: {commit}\n"
        f"Failure class: {failure}\n"
    )


def _gh_api(path: str) -> Any:
    done = subprocess.run(
        ["gh", "api", "-H", "Accept: application/vnd.github+json", path],
        capture_output=True, text=True, check=True,
    )
    return json.loads(done.stdout)


def fetch_annotations(repo: str, run_id: str, *, gh_api: GhApi = _gh_api) -> list[Mapping[str, Any]]:
    """Annotations of the failed deploy job. Any problem reading them gives []."""
    if not _REPO.match(repo) or not _RUN_ID.match(run_id):
        return []
    try:
        jobs = gh_api(f"repos/{repo}/actions/runs/{run_id}/jobs?per_page=100")["jobs"]
        failed = [
            job for job in jobs
            if job.get("name") == JOB_NAME and job.get("conclusion") == "failure"
        ]
        if len(failed) != 1 or not isinstance(failed[0].get("id"), int):
            return []
        annotations = gh_api(f"repos/{repo}/check-runs/{failed[0]['id']}/annotations?per_page=100")
    except (OSError, subprocess.CalledProcessError, ValueError, KeyError, TypeError, AttributeError):
        return []
    return annotations if isinstance(annotations, list) else []


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workflow", required=True)
    parser.add_argument("--run-url", required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    failure = failure_class(fetch_annotations(args.repo, args.run_id))
    args.output.write_text(
        body(args.workflow, args.run_url, args.commit, failure), encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
