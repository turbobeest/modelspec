"""MODEL-225: offline release/recheck replays through the draft PR boundary."""

from __future__ import annotations

import importlib
import json
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import pytest
import yaml

from decision.snapshot import SnapshotInputs, build_snapshot
from release_blog.gates import accuracy, load_signed
from release_blog.model import Breakdown
from release_blog.render import render
from scripts.accuracy import PROFILES
from tests.test_release_blog import (
    NEW, PUBLIC, SIGNER, SOURCES_ALL, TAGS, _model, _new_rows, _offering, _others, _plans,
)

ROOT = Path(__file__).resolve().parents[1]
LAUNCH = date(2026, 9, 26)


def _snapshot(path, *, day=LAUNCH, new=True, price=2.0):
    mids = ["lab/beta", "lab/gamma", *([NEW] if new else [])]
    built = build_snapshot(SnapshotInputs(
        models=[_model(mid) for mid in mids],
        offerings=[_offering(mid, price if mid == NEW else 1.0) for mid in mids],
        evidence=_others() + (_new_rows() if new else []),
        subscriptions=_plans() if new else [], sources=SOURCES_ALL,
        benchmark_domains=TAGS,
        benchmark_metadata={b: {"direction": "higher_is_better"} for b in TAGS},
    ), gate=False, as_of=day)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(built.to_bytes(key=None, ed25519_signer=SIGNER))
    return load_signed(path, public_keys=PUBLIC)


def _report(path, snapshot):
    path.write_text(json.dumps({
        "snapshot": snapshot.snapshot_id, "profile": "pr", "status": "pass",
        "layers": [{"name": layer, "status": "pass"} for layer in PROFILES["pr"]],
    }))


@pytest.fixture(scope="module")
def inputs(tmp_path_factory):
    root = tmp_path_factory.mktemp("pipeline-inputs")
    _snapshot(root / "before.gz", new=False)
    _snapshot(root / "after.gz")
    _snapshot(root / "week.gz", day=LAUNCH + timedelta(days=7), price=3.0)
    return root


@pytest.fixture
def replay(tmp_path, inputs):
    import shutil

    snapshots = tmp_path / "blog" / "snapshots"
    snapshots.mkdir(parents=True)
    refs = {}
    for name in ("before", "after", "week"):
        loaded = load_signed(inputs / f"{name}.gz", public_keys=PUBLIC)
        path = snapshots / f"{loaded.snapshot_id}.json.gz"
        shutil.copy2(inputs / f"{name}.gz", path)
        refs[name] = path.relative_to(tmp_path).as_posix()
    releases = tmp_path / "blog" / "releases"
    releases.mkdir()
    signal = releases / "fixture-release.yaml"
    data = {
        "signal_id": "fixture-release", "model": NEW,
        "announced_at": "2026-09-26T12:00:00Z", "after": refs["after"],
        "before": refs["before"], "accuracy": "blog/releases/fixture-accuracy.json",
    }
    signal.write_text(yaml.safe_dump(data))
    _report(tmp_path / data["accuracy"], load_signed(tmp_path / refs["after"], public_keys=PUBLIC))
    standard = tmp_path / "docs" / "method" / "release-breakdown-standard.md"
    standard.parent.mkdir(parents=True)
    shutil.copy2(ROOT / "docs" / "method" / standard.name, standard)
    return tmp_path, signal, data, refs


def _pipeline():
    return importlib.import_module("release_blog.pipeline")


def _prepare(replay, *, now=None):
    root, signal, _, _ = replay
    return _pipeline().prepare_release(
        root=root, signal_path=signal,
        now=now or datetime(2026, 9, 26, 13, tzinfo=UTC), public_keys=PUBLIC,
    )


def _publish_first(replay, proposal):
    root, _, _, _ = replay
    path = root / "blog" / "posts" / proposal.slug / "post.yaml"
    meta = yaml.safe_load(path.read_text())
    meta["status"] = "published"
    meta["revisions"][0].update(
        published=LAUNCH, approved_by="fixture-reviewer",
        approval="https://github.com/turbobeest/modelspec/pull/0#fixture",
    )
    path.write_text(yaml.safe_dump(meta))


def _week_input(replay):
    root, signal, data, refs = replay
    data["after"] = refs["week"]
    signal.write_text(yaml.safe_dump(data))
    _report(root / data["accuracy"], load_signed(root / refs["week"], public_keys=PUBLIC))


def test_actual_pr_accuracy_report_is_accepted(tmp_path):
    path = tmp_path / "accuracy.json"
    _report(path, type("Snapshot", (), {"snapshot_id": "snap_fixture"})())
    assert accuracy(path, "snap_fixture")["layers"][2]["name"] == "frozen_image_engine_recall"


def test_replayed_release_produces_gated_draft_pr_within_one_day(replay):
    proposal = _prepare(replay)
    assert proposal is not None
    receipts = []
    _pipeline().review_draft(
        root=replay[0], proposal=proposal, public_keys=PUBLIC,
        run_corpus=lambda: receipts.append("corpus passed"),
        open_pr=lambda draft: receipts.append(draft),
    )
    assert receipts[0] == "corpus passed"
    draft = receipts[1]
    assert draft.draft is True
    assert draft.revision == 1
    assert draft.coverage_hours == 1.0
    assert draft.coverage_hours <= 24
    assert "Pending" in draft.body
    assert "cursorbench" in draft.body
    assert "platform" in draft.body.lower()
    assert "held_back" in draft.body
    assert "check_publishable: pass" in draft.body
    assert draft.decisions and all(ref in draft.body for ref in draft.decisions)
    meta = yaml.safe_load((replay[0] / "blog/posts" / draft.slug / "post.yaml").read_text())
    assert meta["status"] == "draft"
    assert meta["revisions"] == [
        {"revision": 1, "published": None, "approved_by": None, "approval": None}]


def test_replayed_seven_day_check_appends_dated_update_pr(replay):
    first = _prepare(replay)
    assert first is not None
    _publish_first(replay, first)
    root = replay[0]
    r1 = root / "blog/posts" / first.slug / "r1"
    frozen = {p.relative_to(r1): p.read_bytes() for p in r1.rglob("*") if p.is_file()}
    _week_input(replay)
    update = _prepare(replay, now=datetime(2026, 10, 3, 13, tzinfo=UTC))
    assert update is not None and update.revision == 2 and update.recheck_day == 7
    receipts = []
    _pipeline().review_draft(
        root=root, proposal=update, public_keys=PUBLIC,
        run_corpus=lambda: None, open_pr=receipts.append,
    )
    assert len(receipts) == 1 and receipts[0].draft is True
    assert "update" in update.title.lower() and "+7" in update.body
    assert "## Update 2026-10-03" in (r1.parent / "r2/post.md").read_text()
    assert {p.relative_to(r1): p.read_bytes() for p in r1.rglob("*") if p.is_file()} == frozen
    meta = yaml.safe_load((r1.parent / "post.yaml").read_text())
    assert meta["status"] == "published"
    assert meta["revisions"][0]["published"] == LAUNCH
    assert meta["revisions"][1] == {
        "revision": 2, "published": None, "approved_by": None, "approval": None}


@pytest.mark.parametrize("day", [1, 7, 30])
def test_recheck_schedule_uses_first_publication(day):
    pipeline = _pipeline()
    assert pipeline.due_recheck(LAUNCH, LAUNCH + timedelta(days=day), LAUNCH) == day
    assert pipeline.due_recheck(LAUNCH, LAUNCH, LAUNCH) is None
    assert pipeline.due_recheck(LAUNCH, LAUNCH + timedelta(days=day),
                                LAUNCH + timedelta(days=day)) is None


def test_replaying_same_signal_does_not_create_another_revision(replay):
    first = _prepare(replay)
    assert first is not None
    assert _prepare(replay) is None


def test_no_recheck_before_publication(replay):
    assert _prepare(replay) is not None
    _week_input(replay)
    assert _prepare(replay, now=datetime(2026, 10, 3, 13, tzinfo=UTC)) is None


def test_snapshot_identity_alone_is_not_material(replay):
    first = _prepare(replay)
    assert first is not None
    path = replay[0] / "blog/posts" / first.slug / "r1/breakdown.json"
    original = Breakdown.model_validate_json(path.read_bytes())
    changed = original.model_copy(update={"revision": 2, "changes_since_r1": []})
    assert _pipeline().material_changes(original, changed) == ()
    standing = original.standing[0]
    changed = original.model_copy(update={"standing": [
        standing.model_copy(update={"band": "rest" if standing.band != "rest" else "best"}),
        *original.standing[1:]]})
    assert _pipeline().material_changes(original, changed) == ("standing",)


@pytest.mark.parametrize("failure", ["corpus", "page"])
def test_failed_quality_gate_opens_no_pr(replay, failure):
    proposal = _prepare(replay)
    assert proposal is not None
    opened = []
    def corpus():
        if failure == "corpus":
            raise ValueError("corpus failed")
    if failure == "page":
        path = replay[0] / "blog/posts" / proposal.slug / "r1/post.md"
        path.write_text(path.read_text() + "An untraced number: 9999.\n")
    with pytest.raises(ValueError):
        _pipeline().review_draft(root=replay[0], proposal=proposal, public_keys=PUBLIC,
                                 run_corpus=corpus, open_pr=opened.append)
    assert opened == []


def test_bad_accuracy_writes_no_post(replay):
    root, _, data, _ = replay
    report = json.loads((root / data["accuracy"]).read_text())
    report["layers"][0]["status"] = "fail"
    (root / data["accuracy"]).write_text(json.dumps(report))
    with pytest.raises(ValueError, match="did not pass"):
        _prepare(replay)
    assert not (root / "blog/posts").exists()


def test_unsigned_snapshot_writes_no_post(replay):
    import gzip

    root, _, data, _ = replay
    path = root / data["after"]
    envelope = json.loads(gzip.decompress(path.read_bytes()))
    envelope.pop("signature", None)
    envelope.pop("signatures", None)
    path.write_bytes(gzip.compress(json.dumps(envelope).encode()))
    with pytest.raises(ValueError, match="signature"):
        _prepare(replay)
    assert not (root / "blog/posts").exists()


@pytest.mark.parametrize("path", ["../private.gz", "/tmp/private.gz", "models/private.md"])
def test_release_inputs_cannot_reach_private_or_unrelated_paths(replay, path):
    _, signal, data, _ = replay
    data["after"] = path
    signal.write_text(yaml.safe_dump(data))
    with pytest.raises(ValueError, match="public blog"):
        _prepare(replay)


def test_optional_platform_import_failure_is_stated(replay, monkeypatch):
    pipeline = _pipeline()
    real = importlib.import_module
    def absent(name):
        if name == "release_blog.platforms":
            raise ModuleNotFoundError(name="release_blog.platforms")
        return real(name)
    monkeypatch.setattr(pipeline.importlib, "import_module", absent)
    proposal = _prepare(replay)
    assert proposal is not None
    assert "release_blog.platforms unavailable" in proposal.body


def test_update_renderer_adds_a_dated_section(replay):
    proposal = _prepare(replay)
    assert proposal is not None
    b = Breakdown.model_validate_json(
        (replay[0] / "blog/posts" / proposal.slug / "r1/breakdown.json").read_bytes())
    b = b.model_copy(update={"revision": 2})
    post, _ = render(b)
    assert "## Update 2026-09-26" in post


def test_workflow_gates_before_draft_and_uses_only_public_inputs():
    path = ROOT / ".github/workflows/release-breakdown.yml"
    assert path.is_file(), "release pipeline workflow is missing"
    workflow = yaml.safe_load(path.read_text())
    job = workflow["jobs"]["draft"]
    assert "turbobeest/modelspec-data" not in yaml.safe_dump(job)
    assert "MODELSPEC_DATA_TOKEN" not in yaml.safe_dump(job)
    scripts = "\n".join(str(s.get("run", "")) for s in job["steps"])
    assert "release_blog.pipeline" in scripts
    assert "--draft" in scripts
    assert scripts.index("release_blog.pipeline") < scripts.index("gh pr create")
    assert "gh pr merge" not in scripts
