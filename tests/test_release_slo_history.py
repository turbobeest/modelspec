"""Release SLO observations come from merged history and retained artifacts."""
from __future__ import annotations

import json
import os
import subprocess
from datetime import UTC, datetime
from pathlib import Path

import yaml

from decision.model import value_hash


def git(root: Path, *args: str, day: str | None = None) -> str:
    env = dict(os.environ)
    if day:
        env.update(GIT_AUTHOR_DATE=f"{day}T12:00:00Z", GIT_COMMITTER_DATE=f"{day}T12:00:00Z")
    return subprocess.run(["git", "-C", str(root), *args], env=env,
                          check=True, capture_output=True, text=True).stdout.strip()


def commit(root: Path, day: str) -> None:
    git(root, "add", ".")
    git(root, "commit", "--allow-empty", "-m", "fixture", day=day)


def repo(tmp_path: Path) -> Path:
    root = tmp_path / "data"
    root.mkdir()
    git(root, "init", "-b", "main")
    git(root, "config", "user.email", "fixture@example.com")
    git(root, "config", "user.name", "Fixture")
    commit(root, "2026-01-01")
    return root


def write(root: Path, path: str, value: object) -> Path:
    dest = root / path
    dest.parent.mkdir(parents=True, exist_ok=True)
    if path.endswith(".md"):
        dest.write_text("---\n" + yaml.safe_dump(value) + "---\n")
    elif path.endswith(".json"):
        dest.write_text(json.dumps(value))
    elif path.endswith(".jsonl"):
        dest.write_text("".join(json.dumps(row) + "\n" for row in value))
    else:
        dest.write_text(yaml.safe_dump(value))
    return dest


def card() -> dict:
    return {"model_id": "lab/example", "provider": "lab", "display_name": "Example",
            "release_date": "2026-01-02", "benchmarks": {"evidence": []}}


def verdict(value=2, family="deterministic", outcome="verified") -> dict:
    return {"target": {"kind": "fact", "id": "price", "value_hash": value_hash(value)},
            "collector": {"agent": "collector", "model_family": "gpt", "method": "read"},
            "verifier": {"agent": "verifier", "model_family": family, "method": "read"},
            "method": "read", "outcome": outcome, "date": "2026-01-04",
            "diff": "different" if outcome == "mismatch" else None}


def test_merged_stages_use_discovery_value_bound_verification_and_snapshot(tmp_path):
    from scripts.slo.releases import read_release_history

    root = repo(tmp_path)
    model = card()
    write(root, "models/lab/example.md", model)
    write(root, "premier/slice-1.yaml", {"models": [
        {"model_id": "lab/other", "lab": "lab", "clauses": [{"clause": 1}]}]})
    commit(root, "2026-01-03")
    model["benchmarks"]["evidence"] = [{"benchmark_id": "sample", "score": 0}]
    write(root, "models/lab/example.md", model)
    write(root, "offerings/host/lab/example.yaml", [{"model": "lab/example",
          "provider": "host", "region": "global", "tier": "standard", "facts": [
              {"id": "price", "facet": "offering.price.input", "state": "known", "value": 2}]}])
    write(root, "verification/log.jsonl", [verdict(99), verdict(family="gpt")])
    commit(root, "2026-01-04")
    write(root, "verification/log.jsonl", [verdict()])
    commit(root, "2026-01-05")
    discovery = write(tmp_path, "watch.json", {"observed_at": "2026-01-02T00:00:00Z",
        "discoveries": [{"provider": "lab", "model_name": "Example",
                         "timestamp": "2026-01-01T12:00:00Z"}]})
    snapshot = write(tmp_path, "snapshot.json", {"built_at": "2026-01-06T12:00:00Z",
        "content": {"lineup": {"candidates": [{"kind": "model", "id": "lab/example"}]}}})
    history = read_release_history(root, discovery_paths=[discovery], snapshot_paths=[snapshot])
    assert not history.errors
    assert history.snapshot_history
    assert history.snapshot_observed_at == datetime(2026, 1, 6, 12, tzinfo=UTC)
    assert len(history.releases) == 1
    release = history.releases[0]
    assert release.discovered_at == datetime(2026, 1, 1, 12, tzinfo=UTC)
    assert release.card_at == datetime(2026, 1, 3, 12, tzinfo=UTC)
    assert release.score_at == datetime(2026, 1, 4, 12, tzinfo=UTC)
    assert release.price_at == datetime(2026, 1, 5, 12, tzinfo=UTC)
    assert release.decidable_at == datetime(2026, 1, 6, 12, tzinfo=UTC)
    assert release.premier_eligible


def test_imported_baseline_is_not_first_merge_or_decidable_evidence(tmp_path):
    from scripts.slo.releases import read_release_history

    root = tmp_path / "data"
    root.mkdir()
    git(root, "init", "-b", "main")
    git(root, "config", "user.email", "fixture@example.com")
    git(root, "config", "user.name", "Fixture")
    model = card()
    model["benchmarks"]["evidence"] = [{"score": 2}]
    write(root, "models/lab/example.md", model)
    write(root, "premier/slice-1.yaml", {"models": [
        {"model_id": "lab/example", "lab": "lab", "clauses": [{"clause": 2}]}]})
    commit(root, "2026-01-03")
    history = read_release_history(root)
    release = history.releases[0]
    assert release.card_at is None
    assert release.score_at is None
    assert release.decidable_at is None
    assert not release.premier_eligible
    assert not history.snapshot_history
    assert set(release.unknown_stages) == {"release-card-lag", "release-score-lag"}


def test_unmerged_branch_is_not_observed_and_explicit_uncarded_discovery_survives(tmp_path):
    from scripts.slo.releases import read_release_history

    root = repo(tmp_path)
    git(root, "checkout", "-b", "proposal")
    write(root, "models/lab/example.md", card())
    commit(root, "2026-01-03")
    git(root, "checkout", "main")
    discovery = write(tmp_path, "pending.json", {"signals": [{"model_id": "lab/example",
        "provider": "lab", "first_seen_at": "2026-01-02T00:00:00Z"}]})
    history = read_release_history(root, discovery_paths=[discovery])
    assert len(history.releases) == 1
    assert history.releases[0].card_at is None
    assert history.releases[0].discovery_source == "signal"
    assert read_release_history(root, ref="proposal").errors


def test_shallow_history_and_malformed_artifact_report_errors_without_private_text(tmp_path):
    from scripts.slo.releases import read_release_history

    root = repo(tmp_path)
    artifact = tmp_path / "private-name.json"
    artifact.write_text('{"secret":')
    result = read_release_history(root, discovery_paths=[artifact])
    assert result.errors
    assert "private-name" not in " ".join(result.errors)
    shallow = tmp_path / "shallow"
    subprocess.run(["git", "clone", "--depth=1", root.as_uri(), str(shallow)],
                   check=True, capture_output=True)
    assert read_release_history(shallow).errors


def test_watch_observed_at_fallback_and_unknown_release_dates(tmp_path):
    from scripts.slo.releases import read_release_history

    root = repo(tmp_path)
    model = card()
    model["release_date"] = "unknown"
    write(root, "models/lab/example.md", model)
    write(root, "premier/slice-1.yaml", {"models": [
        {"model_id": "lab/other", "lab": "lab", "clauses": [{"clause": 1}]}]})
    commit(root, "2026-01-03")
    before = read_release_history(root)
    assert not before.releases
    assert before.errors == ("1 cards lack a usable release date or discovery timestamp",)
    discovery = write(tmp_path, "watch.json", {"observed_at": "2026-01-02T00:00:00Z",
        "discoveries": [{"model_id": "lab/example"}]})
    after = read_release_history(root, discovery_paths=[discovery])
    assert not after.errors
    assert after.releases[0].discovered_at == datetime(2026, 1, 2, tzinfo=UTC)
    assert after.releases[0].card_at == datetime(2026, 1, 3, 12, tzinfo=UTC)
    assert after.releases[0].premier_eligible


def test_snapshot_watermark_uses_latest_observation_without_replacing_first_inclusion(tmp_path):
    from scripts.slo.releases import read_release_history

    root = repo(tmp_path)
    write(root, "models/lab/example.md", card())
    commit(root, "2026-01-03")
    first = write(tmp_path, "first.json", {"observed_at": "2026-01-04T00:00:00Z",
        "content": {"lineup": {"candidates": [{"kind": "model", "id": "lab/example"}]}}})
    latest = write(tmp_path, "latest.json", {"observed_at": "2026-01-06T00:00:00Z",
        "content": {"lineup": {"candidates": []}}})
    history = read_release_history(root, snapshot_paths=[latest, first])
    assert history.snapshot_history
    assert history.snapshot_observed_at == datetime(2026, 1, 6, tzinfo=UTC)
    assert history.releases[0].decidable_at == datetime(2026, 1, 4, tzinfo=UTC)


def test_malformed_artifact_rows_return_sanitized_errors(tmp_path):
    from scripts.slo.releases import read_release_history

    root = repo(tmp_path)
    discovery = write(tmp_path, "secret-discovery.json", {"discoveries": [None]})
    snapshot = write(tmp_path, "secret-snapshot.json", {"observed_at": "2026-01-06T00:00:00Z",
        "content": {"lineup": {"candidates": [None]}}})
    assert read_release_history(root, discovery_paths=[discovery]).errors == (
        "release history or supplied artifacts could not be read",)
    assert read_release_history(root, snapshot_paths=[snapshot]).errors == (
        "release history or supplied artifacts could not be read",)


def test_real_watch_signal_tracks_uncarded_release_and_later_merged_card(tmp_path):
    from scripts.slo.releases import read_release_history

    root = repo(tmp_path)
    write(root, "models/lab/example.md", card())
    commit(root, "2026-01-03")
    discovery = write(tmp_path, "watch.json", {
        "observed_at": "2026-01-04T00:00:00Z", "discoveries": [{
            "model_name": "New Model 2.0", "provider": "lab",
            "first_seen_url": "https://example.com/models/new",
            "timestamp": "2026-01-04T00:00:00Z", "confidence": 1.0,
            "signal_id": "watch-lab-new-model-2-0"}]})
    before = read_release_history(root, discovery_paths=[discovery])
    pending = {row.model_id: row for row in before.releases}.get("lab/new-model-2-0")
    assert pending is not None
    assert pending.card_at is None
    assert pending.discovered_at == datetime(2026, 1, 4, tzinfo=UTC)
    added = {**card(), "model_id": "lab/new-model-2-0", "display_name": "New Model 2.0",
             "release_date": "2026-01-05"}
    write(root, "models/lab/new-model-2-0.md", added)
    commit(root, "2026-01-06")
    after = read_release_history(root, discovery_paths=[discovery])
    joined = {row.model_id: row for row in after.releases}["lab/new-model-2-0"]
    assert not after.errors
    assert joined.discovered_at == datetime(2026, 1, 4, tzinfo=UTC)
    assert joined.card_at == datetime(2026, 1, 6, 12, tzinfo=UTC)


def test_unknown_provider_and_ambiguous_aliases_report_unmatched_counts(tmp_path):
    from scripts.slo.releases import read_release_history

    root = repo(tmp_path)
    write(root, "models/lab/example.md", {**card(), "provider_display": "Shared Lab"})
    write(root, "models/lab/duplicate.md", {**card(), "model_id": "lab/duplicate"})
    write(root, "models/second/example.md", {**card(), "model_id": "second/example",
        "provider": "second", "provider_display": "Shared Lab"})
    commit(root, "2026-01-03")
    discovery = write(tmp_path, "watch.json", {
        "observed_at": "2026-01-04T00:00:00Z", "discoveries": [
            {"provider": "unrecognised", "model_name": "New Model"},
            {"provider": "Shared Lab", "model_name": "New Model"},
            {"provider": "lab", "model_name": "Example"}]})
    history = read_release_history(root, discovery_paths=[discovery])
    assert history.errors == ("3 discoveries could not resolve to one catalogue identity",)
    assert len(history.releases) == 3
