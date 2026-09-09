"""The free path: a local snapshot of the published export, usable offline.

The CLI's graph commands need FalkorDB on localhost:6382. That is fine for
someone exploring the graph locally and useless for everyone else, including
dpf's ticket author, who needs an answer on a machine that has never run a
database.

This module downloads the versioned export from modelspec.dev, caches it, and
answers from the cache. No credential, no account, no network once fetched.

The continuity rule matters more than freshness: an answer from a snapshot three
weeks old, clearly labelled as three weeks old, is far more useful than an error.
Callers are told the age and decide for themselves.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_ORIGIN = "https://modelspec.dev"

#: Files that make a usable snapshot. Kept small on purpose — the whole point is
#: that this works on a laptop tethered to a phone.
PARTS = {
    "index": "/api/index.json",
    "candidates": "/api/rank/candidates.json",
    "profiles": "/api/rank/profiles.json",
    "hardware": "/api/graph/views/hardware.json",
}

#: Past this, the snapshot is still served but every answer says it is stale.
#: Model releases move weekly, so a month-old snapshot is a different world.
STALE_AFTER_DAYS = 30


def cache_dir() -> Path:
    """Respects XDG, so a user can point it somewhere else or clear it."""
    override = os.environ.get("MODELSPEC_CACHE")
    if override:
        return Path(override).expanduser()
    base = os.environ.get("XDG_CACHE_HOME") or "~/.cache"
    return Path(base).expanduser() / "modelspec"


@dataclass(frozen=True)
class Snapshot:
    path: Path
    fetched_at: datetime
    origin: str
    build_commit: str
    build_at: str
    data: dict[str, Any]

    @property
    def age_days(self) -> float:
        return (datetime.now(timezone.utc) - self.fetched_at).total_seconds() / 86400

    @property
    def is_stale(self) -> bool:
        return self.age_days > STALE_AFTER_DAYS

    def freshness(self) -> dict[str, Any]:
        """What every machine-readable answer carries, so nobody has to guess."""
        return {
            "fetched_at": self.fetched_at.isoformat(),
            "age_days": round(self.age_days, 2),
            "stale": self.is_stale,
            "stale_after_days": STALE_AFTER_DAYS,
            "origin": self.origin,
            "build_commit": self.build_commit,
            "built_at": self.build_at,
        }


class SnapshotMissing(RuntimeError):
    """No snapshot has been fetched yet."""


def fetch(origin: str = DEFAULT_ORIGIN, target: Path | None = None) -> Snapshot:
    """Download the export. The only command that needs the network."""
    import httpx

    directory = target or cache_dir()
    directory.mkdir(parents=True, exist_ok=True)
    payload: dict[str, Any] = {}
    with httpx.Client(timeout=60.0, follow_redirects=True) as client:
        for name, route in PARTS.items():
            response = client.get(origin + route)
            response.raise_for_status()
            payload[name] = response.json()

    build = (payload.get("index") or {}).get("build") or {}
    meta = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "origin": origin,
        "build_commit": build.get("commit", "unknown"),
        "built_at": build.get("built_at", "unknown"),
    }
    # Write to a temporary name and move, so an interrupted fetch cannot leave a
    # half-written snapshot that later reads as valid.
    tmp = directory / f".snapshot.{os.getpid()}.tmp"
    tmp.write_text(json.dumps({"meta": meta, "data": payload}), encoding="utf-8")
    tmp.replace(directory / "snapshot.json")
    return load(directory)


def load(directory: Path | None = None) -> Snapshot:
    """Read the cached snapshot. Never touches the network."""
    path = (directory or cache_dir()) / "snapshot.json"
    if not path.is_file():
        raise SnapshotMissing(
            f"no snapshot at {path}. Run `modelspec snapshot fetch` once; "
            "everything after that works offline."
        )
    raw = json.loads(path.read_text(encoding="utf-8"))
    meta = raw["meta"]
    return Snapshot(
        path=path,
        fetched_at=datetime.fromisoformat(meta["fetched_at"]),
        origin=meta["origin"],
        build_commit=meta["build_commit"],
        build_at=meta["built_at"],
        data=raw["data"],
    )


def status(directory: Path | None = None) -> dict[str, Any]:
    try:
        snap = load(directory)
    except SnapshotMissing as exc:
        return {"present": False, "message": str(exc)}
    size = snap.path.stat().st_size
    return {"present": True, "size_bytes": size, "path": str(snap.path), **snap.freshness()}


def age_of(path: Path) -> float:
    return (time.time() - path.stat().st_mtime) / 86400
