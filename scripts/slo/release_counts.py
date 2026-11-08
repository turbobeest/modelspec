"""Bounded counts-only transfer from a private Actions artifact to a public job."""

from __future__ import annotations

import io
import json
import zipfile
from datetime import datetime
from typing import Any

import httpx

from scripts.slo.report import RELEASE_STAGES, load_config, public_release_report

DATA_REPO = "turbobeest/modelspec-data"
API = f"https://api.github.com/repos/{DATA_REPO}/actions"
ARTIFACT = "release-coverage-counts"
MAX_COUNT = 1_000_000
MAX_PAYLOAD = 16_384
MAX_ARCHIVE = 65_536
MAX_RESPONSE = 131_072


def unavailable(now: datetime) -> dict[str, Any]:
    return {
        "as_of": now.date().isoformat(),
        "release_coverage": {"counts_only": True, "stages": {
            stage: {"measured": 0, "completed": 0, "pending": 0,
                    "unknown": 0, "late": 0, "errors": 1}
            for stage in RELEASE_STAGES
        }},
    }


def counts_payload(data: Any, *, now: datetime) -> dict[str, Any]:
    """Copy a fixed schema, never strings, dates or metadata from private inputs."""
    if not isinstance(data, dict):
        raise ValueError("release counts must be an object")
    report = public_release_report(data, load_config(), now=now)
    coverage = report.release_coverage
    if any(value > MAX_COUNT for stage in coverage["stages"].values() for value in stage.values()):
        raise ValueError("release count exceeds its bound")
    return {"as_of": now.date().isoformat(), "release_coverage": coverage}


def read_counts(raw: str | bytes, *, now: datetime) -> dict[str, Any]:
    try:
        if len(raw) > MAX_PAYLOAD:
            raise ValueError("release counts file exceeds its bound")
        return counts_payload(json.loads(raw), now=now)
    except (ValueError, KeyError, TypeError):
        return unavailable(now)


def _get(client: httpx.Client, url: str, *, token: str = "", limit: int = MAX_RESPONSE,
         redirect: bool = False) -> tuple[bytes, str | None]:
    headers = ({"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28"} if token else {})
    with client.stream("GET", url, headers=headers, follow_redirects=False) as response:
        if redirect and response.status_code == 302:
            location = httpx.URL(response.headers["location"])
            if location.scheme != "https" or not location.host or location.userinfo:
                raise ValueError("invalid artifact redirect")
            return b"", str(location)
        response.raise_for_status()
        content = bytearray()
        for chunk in response.iter_bytes(chunk_size=8192):
            content.extend(chunk)
            if len(content) > limit:
                raise ValueError("artifact response exceeds its bound")
        return bytes(content), None


def fetch_counts(token: str, *, now: datetime, client: httpx.Client) -> dict[str, Any]:
    """Read the latest main scheduled/manual run; failure returns fixed error counts.

    All private metadata, bodies and errors remain in memory. The signed
    storage download receives no GitHub Authorization header. No earlier run
    is substituted when the newest run lacks usable counts.
    """
    if not token:
        return unavailable(now)
    try:
        raw, _ = _get(client, f"{API}/workflows/release-coverage.yml/runs?branch=main&per_page=1",
                      token=token)
        runs = json.loads(raw)["workflow_runs"]
        if not runs:
            return unavailable(now)
        run = runs[0]
        if (run["head_branch"] != "main" or run["event"] not in {"schedule", "workflow_dispatch"}
                or run["head_repository"]["full_name"] != DATA_REPO):
            return unavailable(now)
        run_id = run["id"]
        if type(run_id) is not int or run_id <= 0:
            return unavailable(now)
        raw, _ = _get(client, f"{API}/runs/{run_id}/artifacts?per_page=100", token=token)
        listing = json.loads(raw)
        if listing["total_count"] > 100:
            return unavailable(now)
        matches = [a for a in listing["artifacts"] if a["name"] == ARTIFACT and not a["expired"]]
        if len(matches) != 1:
            return unavailable(now)
        artifact = matches[0]
        artifact_id = artifact["id"]
        if (type(artifact_id) is not int or artifact_id <= 0
                or not 0 < artifact["size_in_bytes"] <= MAX_ARCHIVE):
            return unavailable(now)
        raw, location = _get(client, f"{API}/artifacts/{artifact_id}/zip", token=token,
                             limit=MAX_ARCHIVE, redirect=True)
        if location:
            raw, _ = _get(client, location, limit=MAX_ARCHIVE)
        with zipfile.ZipFile(io.BytesIO(raw)) as zipped:
            if zipped.namelist() != ["coverage.json"]:
                return unavailable(now)
            info = zipped.getinfo("coverage.json")
            if info.file_size > MAX_PAYLOAD:
                return unavailable(now)
            return read_counts(zipped.read(info), now=now)
    except Exception:  # a private response or exception must never reach the public job log
        return unavailable(now)
