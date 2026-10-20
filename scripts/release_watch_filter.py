"""Deterministic release grouping shared by the watcher and offline triage.

These are discovery identities, not catalogue facts. Group members retain
their names and URLs so a curator can split a release series into model cards.
"""

from __future__ import annotations

import json
import re
import subprocess
from collections.abc import Iterable, Sequence
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import yaml

from release_signals.contract import ReleaseSignal
from release_signals.watch import Registry, Seen, SourceRun, signal_id

PROVIDERS = {
    "qwen": "alibaba-qwen-team", "alibaba": "alibaba-qwen-team",
    "mistralai": "mistral", "x-ai": "xai", "stepfun-ai": "stepfun",
    "liquidai": "liquid", "coherelabs": "cohere", "meta-llama": "meta",
}

# Only these mirror namespaces inherit an upstream lab from a model prefix.
MIRRORS = {"unsloth", "primeintellect"}
UPSTREAM_PREFIXES = {
    "lfm": "liquid", "embeddinggemma-": "google", "gemma-": "google",
    "nvidia-": "nvidia", "nemotron-": "nvidia", "flux-": "black-forest-labs",
    "deepseek-": "deepseek", "muse-spark-": "meta", "sam3": "meta",
}

ALIASES = {
    ("anthropic", "claude-sonnet-4-5-20250929"): "claude-sonnet-4-5",
    ("nvidia", "nemotron-3-5-super-vl"): "nemotron-3-5-super-vl-120b-a12b",
    ("mistral", "mistral-large-4-0"): "mistral-large-4",
    ("mistral", "mistral-ocr-4-0"): "mistral-ocr-4",
}
NON_MODEL = {
    "sdk", "client", "blog", "blogpost", "doc", "docs", "documentation",
    "guide", "readme", "changelog", "release-notes", "tutorial", "example", "examples",
}


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")


def rejection_reason(provider: str, model_name: str) -> str | None:
    """Reject explicit non-model names; unknown names stay visible for review."""
    name = _slug(model_name)
    lab = _slug(provider)
    if any(name in {token, f"{lab}-{token}", f"{token}-{lab}"} for token in NON_MODEL):
        return "non-model documentation, blog or software item"
    if _slug(provider) == "ibm" and name == "ensemble-forecasting-with-ibm-granite-time-series":
        return "forecasting example repository"
    return None


def canonical_release(provider: str, model_name: str) -> tuple[str, str]:
    """Collapse known aliases, packaging and release-series variants.

    Never strip arbitrary numeric suffixes: model size, named minor versions
    and base/instruct/reasoning distinctions remain part of the identity.
    """
    lab = PROVIDERS.get(_slug(provider), _slug(provider))
    name = _slug(model_name)
    if lab in MIRRORS:
        for prefix, upstream in UPSTREAM_PREFIXES.items():
            if name.startswith(prefix):
                lab = upstream
                break
    if lab == "nvidia":
        name = name.removeprefix("nvidia-")
    name = re.sub(r"^lfm-?(?=\d)", "lfm-", name)
    name = re.sub(r"-(?:bf16|fp16|mxfp8)$", "", name)
    # Preserve dated revisions unless an explicit alias establishes equivalence.
    if lab == "anthropic":
        name = re.sub(r"-v1(?:-0)?$", "", name)
    # Training endpoints of one recipe, not different architectures or sizes.
    if lab == "ifm" and name.startswith("loopedlm-p1-"):
        name = re.sub(r"-(?:336b|500b)$", "", name)
    if lab == "nvidia":
        name = re.sub(r"^(agile-one-s-[a-z]+-ssd-n\d+)-\d+$", r"\1", name)
    return lab, ALIASES.get((lab, name), name)


def canonical_signal_id(identifier: str) -> str:
    parts = identifier.split(":", 2)
    if len(parts) != 3 or parts[0] != "watch":
        return identifier
    return signal_id(*canonical_release(parts[1], parts[2]))


def draft_card(signal: ReleaseSignal, evidence: list[dict]) -> dict:
    """A review stub, deliberately without inferred dates, sizes or scores."""
    return {
        "status": "draft",
        "model_name": signal.model_name,
        "provider": signal.provider,
        "release_date": None,
        "model_type": None,
        "total_parameters": None,
        "source_urls": sorted({row["url"] for row in evidence}),
        "variants": sorted({row["model_name"] for row in evidence}),
    }


def filter_releases(runs: Iterable[SourceRun], now: datetime) -> dict:
    """Group successful source observations in registry order, without I/O."""
    stamp = now.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    groups: dict[str, dict] = {}
    rejected = []
    observations = []
    for run in runs:
        if run.status != "ok":
            continue
        for seen in sorted(run.new, key=lambda row: row.key):
            evidence = {
                "source_id": run.source.id, "source_key": seen.key,
                "model_name": seen.model_name, "provider": seen.provider, "url": seen.url,
                "created": seen.created.isoformat() if seen.created else None,
                "confidence": run.source.confidence,
            }
            observations.append(evidence)
            reason = rejection_reason(seen.provider, seen.model_name)
            if reason:
                rejected.append({**evidence, "reason": reason})
                continue
            lab, name = canonical_release(seen.provider, seen.model_name)
            identifier = signal_id(lab, name)
            if identifier not in groups:
                signal = ReleaseSignal.parse({
                    "model_name": seen.model_name, "provider": lab,
                    "first_seen_url": seen.url, "timestamp": stamp,
                    "confidence": run.source.confidence, "signal_id": identifier,
                }, discovered=True)
                groups[identifier] = {"signal": signal, "evidence": []}
            if evidence not in groups[identifier]["evidence"]:
                groups[identifier]["evidence"].append(evidence)
    return {
        "signals": [group["signal"] for group in groups.values()],
        "groups": [
            {
                "signal_id": identifier, "evidence": group["evidence"],
                "draft_card": draft_card(group["signal"], group["evidence"]),
            }
            for identifier, group in groups.items()
        ],
        "rejected": rejected,
        "observations": observations,
    }


def replay_reports(paths: Sequence[Path], registry: Registry) -> tuple[list[SourceRun], datetime]:
    """Read normalized observations only; replay never fetches a source."""
    sources = {source.id: source for source in registry.sources}
    reports = [json.loads(path.read_text(encoding="utf-8")) for path in paths]
    runs = []
    stamps = []
    for report in reports:
        stamp = datetime.fromisoformat(report["observed_at"].replace("Z", "+00:00"))
        if stamp.tzinfo is None:
            raise ValueError("replay observed_at must include a UTC offset")
        stamps.append(stamp)
        observations = report["observations"]
        for row in observations:
            if row["source_id"] not in sources:
                raise ValueError(f"unregistered replay source: {row['source_id']}")
        for source in registry.sources:
            seen = []
            for row in observations:
                if row["source_id"] != source.id:
                    continue
                seen.append(Seen(
                    key=row["source_key"], model_name=row["model_name"],
                    provider=row["provider"], url=row["url"],
                    created=datetime.fromisoformat(row["created"]) if row["created"] else None,
                ))
            if seen:
                runs.append(SourceRun(source, "ok", new=tuple(seen), listed=len(seen)))
    return runs, max(stamps)


def recall_reports(
    paths: Sequence[Path], registry: Registry, end: date,
) -> tuple[list[SourceRun], datetime, dict]:
    """Select a half-open 30-day UTC window and preserve archive coverage gaps."""
    start = end - timedelta(days=30)
    selected = []
    days = set()
    source_failures = []
    for path in dict.fromkeys(path.resolve() for path in paths):
        report = json.loads(path.read_text(encoding="utf-8"))
        stamp = datetime.fromisoformat(report["observed_at"].replace("Z", "+00:00"))
        if stamp.tzinfo is None:
            raise ValueError("recall observed_at must include a UTC offset")
        day = stamp.astimezone(UTC).date()
        if not start <= day < end:
            continue
        if report.get("replay"):
            raise ValueError("recall requires original run artifacts, not replay outputs")
        selected.append(path)
        days.add(day)
        source_failures.extend(
            {"observed_at": report["observed_at"], **row}
            for row in report["sources"] if row["status"] != "ok"
        )
    runs, now = replay_reports(selected, registry) if selected else (
        [], datetime.combine(end, datetime.min.time(), UTC),
    )
    return runs, now, {
        "window_start": start.isoformat(), "window_end_exclusive": end.isoformat(),
        "artifact_count": len(selected),
        "missing_artifact_days": [
            day.isoformat() for offset in range(30)
            if (day := start + timedelta(days=offset)) not in days
        ],
        "source_failures": source_failures,
    }


def compare_card_additions(root: Path, window: dict, filtered: dict) -> dict:
    """Compare accepted replay identities with first additions on catalogue HEAD.

    Committer dates on first-parent history define card-added dates. Read each
    card at its addition commit so later edits cannot change this denominator.
    """
    def git(*args: str) -> str:
        result = subprocess.run(
            ["git", "-C", str(root), *args], capture_output=True, text=True, check=False,
        )
        if result.returncode:
            raise ValueError(f"cannot read catalogue history: {result.stderr.strip()}")
        return result.stdout.strip()

    if git("rev-parse", "--is-shallow-repository") != "false":
        raise ValueError("recall requires complete catalogue history, not a shallow clone")
    revision = git("rev-parse", "HEAD")
    if git("cat-file", "-t", f"{revision}:models") != "tree":
        raise ValueError("catalogue revision must contain a models directory")
    history = git(
        "log", "--first-parent", "--diff-merges=first-parent", "--reverse",
        "--find-renames", "--diff-filter=A", "--format=%H%x09%cI", "--name-only",
        revision, "--", "models",
    )
    accepted = {signal.signal_id for signal in filtered["signals"]}
    rejected: dict[str, list[dict]] = {}
    for row in filtered["rejected"]:
        identifier = signal_id(*canonical_release(row["provider"], row["model_name"]))
        rejected.setdefault(identifier, []).append(row)
    cards = []
    seen = set()
    commit = added_at = ""
    for line in history.splitlines():
        if "\t" in line:
            commit, added_at = line.split("\t")
            continue
        path = Path(line)
        if len(path.parts) != 3 or path.suffix != ".md" or line in seen:
            continue
        seen.add(line)
        added_day = datetime.fromisoformat(added_at).astimezone(UTC).date().isoformat()
        if not window["window_start"] <= added_day < window["window_end_exclusive"]:
            continue
        parts = git("show", f"{commit}:{line}").split("---", 2)
        front = yaml.safe_load(parts[1]) if len(parts) == 3 else None
        if not isinstance(front, dict) or not front.get("model_id"):
            raise ValueError(f"card addition has no model_id frontmatter: {line}")
        provider = str(front.get("provider") or path.parent.name)
        identities = {
            signal_id(*canonical_release(provider, str(value)))
            for value in (
                front.get("display_name"), front.get("version"),
                str(front["model_id"]).rsplit("/", 1)[-1], path.stem,
            ) if value
        }
        cards.append({
            "path": line, "added_at": added_at, "addition_commit": commit,
            "matched_signal_ids": sorted(identities & accepted),
            "rejected": [
                row for identifier in sorted(identities) for row in rejected.get(identifier, [])
            ],
        })
    matched = sum(bool(row["matched_signal_ids"]) for row in cards)
    return {
        **window, "catalogue_revision": revision, "cards_added": len(cards),
        "matched_cards": matched, "recall": matched / len(cards) if cards else None,
        "cards": cards,
    }
