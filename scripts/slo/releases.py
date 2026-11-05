"""Read release milestones from main history and explicitly retained artifacts.

The initial commit is an imported baseline, not proof of first publication.
A snapshot observation requires an actual candidate list and a timestamp;
premier selection alone never establishes availability on /decide.
"""
from __future__ import annotations

import io
import json
import os
import subprocess
from collections.abc import Mapping, Sequence
from contextlib import contextmanager
from dataclasses import replace
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from typing import Any

import yaml

from decision.model import Verification, fact_verification_value, value_hash
from release_signals.pipeline import resolve_signal
from scripts.slo.report import Release, ReleaseHistory

_PATHS = ("models", "offerings", "verification/log.jsonl", "premier/slice-1.yaml")
_LOADER = getattr(yaml, "CSafeLoader", yaml.SafeLoader)


def _git(root: Path, *args: str, data: bytes | None = None) -> bytes:
    result = subprocess.run(["git", "-C", str(root), *args], input=data,
                            capture_output=True, check=False,
                            env={k: v for k, v in os.environ.items()
                                 if not k.startswith("GIT_")})
    if result.returncode:
        raise ValueError("release git history could not be read")
    return result.stdout


def _instant(value: object, *, date_only: bool = False) -> datetime:
    parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        if date_only and len(str(value)) == 10:
            return parsed.replace(tzinfo=UTC)
        raise ValueError("observation timestamp needs a timezone")
    return parsed.astimezone(UTC)


def _blobs(root: Path, sha: str, paths: Sequence[str]):
    stream = io.BytesIO(_git(root, "cat-file", "--batch",
                           data="".join(f"{sha}:{p}\n" for p in paths).encode()))
    for path in paths:
        header = stream.readline().decode().strip()
        if header.endswith(" missing"):
            yield path, None
            continue
        _, kind, size = header.split()
        if kind != "blob":
            raise ValueError("release history expected a file")
        content = stream.read(int(size))
        stream.read(1)
        yield path, content


def _documents(root: Path, sha: str, paths: Sequence[str]) -> dict[str, Any]:
    docs = {}
    for path, content in _blobs(root, sha, paths):
        if content is None:
            docs[path] = None
            continue
        text = content.decode()
        if path.endswith(".jsonl"):
            docs[path] = [json.loads(line) for line in text.splitlines() if line.strip()]
        elif path.endswith(".md"):
            parts = text.split("---", 2)
            docs[path] = yaml.load(parts[1], Loader=_LOADER) if len(parts) == 3 else None
        else:
            docs[path] = yaml.load(text, Loader=_LOADER)
    return docs


@contextmanager
def _identity_catalogue(root: Path, sha: str):
    """Give the pipeline its exact files at the measured ref, never the checkout."""
    known = "scripts/models_dev_known_identities.yaml"
    paths = _git(root, "ls-tree", "-r", "--name-only", sha, "--", "models", known)
    selected = [p for p in paths.decode().splitlines()
                if p == known or (p.endswith(".md") and len(Path(p).parts) == 3)]
    with TemporaryDirectory(prefix="modelspec-release-identity-") as directory:
        catalogue = Path(directory)
        for path, content in _blobs(root, sha, selected):
            if content is None:
                raise ValueError("release identity catalogue could not be read")
            dest = catalogue / path
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(content)
        yield catalogue


def _priced(offerings: Mapping[str, Any], verification: Sequence[dict],
            at: datetime) -> set[str]:
    latest: dict[tuple[str, str], tuple[Any, int, Verification]] = {}
    for position, raw in enumerate(verification):
        row = Verification.model_validate(raw)
        if row.target.kind != "fact" or not row.counts or row.date > at.date():
            continue
        key = (row.target.id, row.target.value_hash)
        value = (row.date, position, row)
        if key not in latest or value[:2] >= latest[key][:2]:
            latest[key] = value
    priced = set()
    for rows in offerings.values():
        for offering in rows or ():
            if not offering.get("model"):
                continue
            for fact in offering.get("facts") or ():
                if not str(fact.get("facet", "")).startswith("offering.price.") \
                        or fact.get("state") != "known" or fact.get("value") is None:
                    continue
                expected = value_hash(fact_verification_value(fact))
                winner = latest.get((fact.get("id"), expected))
                inline = fact.get("verification")
                if inline:
                    row = Verification.model_validate(inline)
                    if row.target.kind == "fact" and row.target.id == fact.get("id") \
                            and row.target.value_hash == expected and row.counts \
                            and row.date <= at.date() \
                            and (winner is None or row.date > winner[0]):
                        winner = (row.date, -1, row)
                if winner is not None and not winner[2].quarantined:
                    priced.add(str(offering["model"]))
    return priced


def _discovery_rows(payload: object) -> tuple[str, Sequence[dict]]:
    if not isinstance(payload, dict):
        raise ValueError("discovery artifact must be an object")
    if "discoveries" in payload:
        return "release-watch", payload["discoveries"]
    if "signals" in payload:
        return "signal", payload["signals"]
    raise ValueError("discovery artifact needs discoveries or signals")


def _observations(paths: Sequence[Path], catalogue: Path,
                  releases: dict[str, Release]) -> None:
    found: dict[str, Release] = {}
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        source, rows = _discovery_rows(payload)
        if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
            raise ValueError("discovery rows must be objects")
        for raw in rows:
            row = raw.get("signal", raw)
            if not isinstance(row, dict):
                raise ValueError("queued signal must be an object")
            provider = str(row.get("provider") or "")
            mid = row.get("model_id")
            identity_unknown = False
            if not mid:
                name = str(row.get("model_name") or "")
                if not provider.strip() or not name.strip():
                    raise ValueError("discovery needs a provider and model name")
                resolution = resolve_signal(SimpleNamespace(provider=provider, model_name=name),
                                            catalogue)
                mid = resolution.model_id
                if resolution.status == "uncertain":
                    identity_unknown = True
                    key = json.dumps([provider, name], separators=(",", ":")).encode()
                    mid = f"unresolved/{sha256(key).hexdigest()}"
            if not isinstance(mid, str) or "/" not in mid:
                raise ValueError("discovery identity must be a catalogue model ID")
            stamp = (row.get("first_seen_at") or row.get("received_at")
                     or row.get("timestamp") or raw.get("received_at")
                     or payload.get("observed_at"))
            at = _instant(stamp)
            if mid not in found or at < found[mid].discovered_at:
                found[mid] = Release(mid, at, source, identity_unknown=identity_unknown)
    for mid, observation in found.items():
        if mid in releases:
            releases[mid] = replace(releases[mid], discovered_at=observation.discovered_at,
                                    discovery_source=observation.discovery_source)
        else:
            releases[mid] = observation


def _snapshots(paths: Sequence[Path], releases: dict[str, Release]) -> datetime | None:
    observed = None
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("snapshot artifact must be an object")
        content = payload.get("content", payload)
        candidates = content["lineup"]["candidates"]
        if not isinstance(candidates, list) or any(not isinstance(row, dict) for row in candidates):
            raise ValueError("snapshot candidates must be objects")
        at = _instant(payload.get("observed_at") or payload.get("built_at")
                      or payload.get("generated_at"))
        observed = at if observed is None else max(observed, at)
        for row in candidates:
            mid = row.get("id") if row.get("kind") == "model" else row.get("model")
            if mid in releases and (releases[mid].decidable_at is None
                                   or at < releases[mid].decidable_at):
                releases[mid] = replace(releases[mid], decidable_at=at)
    return observed


def read_release_history(root: Path, *, ref: str = "HEAD",
                         discovery_paths: Sequence[Path] = (),
                         snapshot_paths: Sequence[Path] = ()) -> ReleaseHistory:
    """Observe first milestones on main; errors contain no input names or values.

    Date-only card releases mean midnight UTC. Discovery rows use their first
    recorded timestamp and the release pipeline's resolver at the selected ref.
    Ambiguous discoveries remain individual unknown releases. Snapshot files
    contain ``content.lineup`` and an ``observed_at``, ``built_at`` or
    ``generated_at`` timestamp with an offset.
    """
    releases: dict[str, Release] = {}
    try:
        if _git(root, "rev-parse", "--is-shallow-repository").strip() != b"false":
            return ReleaseHistory(errors=("complete release git history is required",))
        sha = _git(root, "rev-parse", "--verify", f"{ref}^{{commit}}").decode().strip()
        branches = _git(root, "for-each-ref", "--format=%(refname)",
                        "refs/remotes/origin/main", "refs/heads/main").decode().splitlines()
        main = ("refs/remotes/origin/main" if "refs/remotes/origin/main" in branches
                else "refs/heads/main")
        if sha not in _git(root, "rev-list", "--first-parent", main).decode().splitlines():
            return ReleaseHistory(errors=("release ref must be on main's first-parent history",))
        history = _git(root, "log", "--first-parent", "--reverse", "--format=%H %ct", sha)
        cards: dict[str, dict] = {}
        offerings: dict[str, Any] = {}
        verification: Sequence[dict] = ()
        premier: dict = {}
        card_times: dict[str, datetime | None] = {}
        score_times: dict[str, datetime | None] = {}
        price_times: dict[str, datetime | None] = {}
        previous = None
        for entry in history.decode().splitlines():
            revision, timestamp = entry.split()
            at = datetime.fromtimestamp(int(timestamp), UTC)
            if previous is None:
                paths = _git(root, "ls-tree", "-r", "--name-only", revision, "--", *_PATHS)
            else:
                paths = _git(root, "diff", "--name-only", previous, revision, "--", *_PATHS)
            selected = [p for p in paths.decode().splitlines()
                        if p.endswith((".md", ".yaml", ".yml", ".jsonl"))]
            docs = _documents(root, revision, selected) if selected else {}
            for path, doc in docs.items():
                if path.startswith("models/"):
                    if not isinstance(doc, dict) or not doc.get("model_id"):
                        continue
                    mid = str(doc["model_id"])
                    cards[mid] = doc
                    card_times.setdefault(mid, at if previous else None)
                    scores = (doc.get("benchmarks") or {}).get("evidence") or ()
                    if any(row.get("score") is not None for row in scores):
                        score_times.setdefault(mid, at if previous else None)
                elif path.startswith("offerings/"):
                    offerings[path] = doc
                elif path == "verification/log.jsonl":
                    verification = doc or ()
                elif path == "premier/slice-1.yaml":
                    premier = doc or {}
            if any(p.startswith("offerings/") or p == "verification/log.jsonl" for p in docs):
                priced = _priced(offerings, verification, at)
                for mid in priced:
                    price_times.setdefault(mid, at if previous else None)
            previous = revision
        eligible = {str(row["lab"]).casefold() for row in premier.get("models", ())
                    if row.get("lab") and any(c.get("clause") == 1 for c in row.get("clauses", ()))}
        for mid, card in cards.items():
            try:
                discovered = _instant(card.get("release_date"), date_only=True)
            except ValueError:
                continue
            releases[mid] = Release(mid, discovered)
        if discovery_paths:
            with _identity_catalogue(root, sha) as catalogue:
                _observations(discovery_paths, catalogue, releases)
        for mid, release in releases.items():
            card = cards.get(mid, {})
            labs = {str(card.get("provider") or "").casefold(),
                    str(card.get("provider_display") or "").casefold(),
                    mid.split("/")[0].casefold()}
            times = {"card": card_times, "price": price_times, "score": score_times}
            unknown = tuple(f"release-{stage}-lag" for stage, values in times.items()
                            if mid in values and values[mid] is None)
            releases[mid] = replace(release, card_at=card_times.get(mid),
                                    price_at=price_times.get(mid), score_at=score_times.get(mid),
                                    premier_eligible=bool(labs & eligible), unknown_stages=unknown)
        observed = _snapshots(snapshot_paths, releases)
        undated = len(cards.keys() - releases.keys())
        errors = ((f"{undated} cards lack a usable release date or discovery timestamp",)
                  if undated else ())
        ordered = tuple(sorted(releases.values(), key=lambda r: (r.discovered_at, r.model_id)))
        return ReleaseHistory(ordered,
                              errors=errors, snapshot_history=observed is not None,
                              snapshot_observed_at=observed)
    except (ValueError, KeyError, TypeError, OSError, yaml.YAMLError):
        return ReleaseHistory(errors=("release history or supplied artifacts could not be read",))
