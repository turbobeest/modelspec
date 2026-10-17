"""MODEL-402 exports one signed price successor without changing undated bytes."""

from __future__ import annotations

import base64
import gzip
import importlib.util
import json
import subprocess
from datetime import UTC, date, datetime
from pathlib import Path
from types import SimpleNamespace

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from decision import registry, snapshot
from tests.snapshot_records import SOURCES, fact, model, offering, verification

ROOT = Path(__file__).resolve().parents[1]
MODEL = "lab/argon"
OFFERING = f"sambanova/{MODEL}/global/standard"
KEY = b"model402-vendor-fixture-key"
BUILD_DAY = date(2026, 11, 30)
BOUNDARY = date(2026, 12, 1)
CURRENT = "decision/snapshot.json.gz"
SUCCESSOR = "decision/snapshot-successor.json.gz"
SUCCESSOR_VOCABULARY = "decision/vocabulary-successor.json"


class _BuildClock(datetime):
    @classmethod
    def now(cls, tz=None):
        assert tz is UTC, "the Worker build day must use UTC"
        return cls(2026, 11, 30, 12, tzinfo=UTC)


def _price(facet, value, start=None, until=None):
    row = fact("offering", OFFERING, facet, value, source="src-pricing")
    if start is not None:
        row["id"] += "@" + start
        row["effective_from"] = start
    if until is not None:
        row["effective_until"] = until
    expected = value if start is None and until is None else {
        "value": value, "effective_from": start, "effective_until": until,
    }
    row["verification"] = verification("fact", row["id"], value=expected)
    return row


def _inputs(*, scheduled):
    prices = []
    for facet, before, after in (
        ("offering.price.input", 2, 4),
        ("offering.price.output", 10, 20),
    ):
        if scheduled:
            prices.extend([
                _price(facet, before, "2026-10-14", "2026-11-30"),
                _price(facet, after, "2026-12-01"),
            ])
        else:
            prices.append(_price(facet, before))
    model_row = model(MODEL)
    offering_row = offering(MODEL, facts=prices)
    for subject, owner, row in (
        ("model", MODEL, model_row),
        ("offering", OFFERING, offering_row),
    ):
        authored = {item["facet"] for item in row["facts"]}
        for facet in registry.default().facets():
            if (facet.subject == subject and facet.tier == "guaranteed"
                    and not facet.computed_by and facet.id not in authored
                    and facet.id not in {"offering.provider", "offering.region", "offering.tier"}):
                row["facts"].append(fact(subject, owner, facet.id, None, state="not_disclosed"))
    return snapshot.SnapshotInputs(
        models=[model_row], offerings=[offering_row], sources=SOURCES,
    )


@pytest.fixture
def export_fixture(tmp_path, monkeypatch):
    """Keep the real snapshot compiler and signatures; isolate unrelated exports."""
    from decision.vocabulary import build_vocabulary
    from pipeline import build, data_source, export, hardware, load, policy_export, ranking
    from schema import graph

    spec = importlib.util.spec_from_file_location("model402_vendor", ROOT / "api/worker/vendor.py")
    vendor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(vendor)
    monkeypatch.setattr(vendor, "_show_coverage_log", lambda: None)
    root = tmp_path / "data"
    (root / "premier").mkdir(parents=True)
    (root / "premier/slice-1.yaml").write_text("models:\n- lab/argon\n", encoding="utf-8")
    private = Ed25519PrivateKey.from_private_bytes(bytes(range(32)))
    public = private.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    public_keys = {"model402-fixture": public}
    monkeypatch.setenv("MODELSPEC_SNAPSHOT_KEY", KEY.decode())
    monkeypatch.setenv("MODELSPEC_SNAPSHOT_ED25519_KEY", base64.b64encode(bytes(range(32))).decode())
    monkeypatch.setattr(snapshot, "load_public_keys", lambda *_: public_keys)
    monkeypatch.setattr("datetime.datetime", _BuildClock)
    monkeypatch.setattr(data_source, "overlay", lambda *_: root)
    monkeypatch.setattr(registry, "use_root", lambda *_: None)
    monkeypatch.setattr(load, "load_models", lambda *_: [])
    monkeypatch.setattr(load, "load_catalogue", lambda *_: None)
    identity = {"commit": "model402-fixture", "built_at": "2026-11-30T12:00:00+00:00"}
    monkeypatch.setattr(export, "make_build", lambda *_: SimpleNamespace(to_json=lambda: identity))
    monkeypatch.setattr(hardware, "load_devices", lambda *_: [])
    monkeypatch.setattr(graph, "derive_graph", lambda *_: {})
    monkeypatch.setattr(hardware, "compute", lambda *_: None)

    def write_rank(out, *_):
        out.mkdir(parents=True, exist_ok=True)
        for filename in ("candidates.json", "hardware.json"):
            (out / filename).write_text(json.dumps({"build": identity}), encoding="utf-8")

    def write_policy(out, *_):
        (out / "policy").mkdir(parents=True, exist_ok=True)
        (out / "policy/catalogue.json").write_text('{"models":[]}', encoding="utf-8")

    def write_vocabulary(_root, written, *, key):
        loaded = snapshot.load_snapshot(written, key=key)
        written.with_name("vocabulary.json").write_text(
            json.dumps(build_vocabulary(loaded)), encoding="utf-8",
        )

    monkeypatch.setattr(ranking, "write_export", write_rank)
    monkeypatch.setattr(policy_export, "write_export", write_policy)
    monkeypatch.setattr(build, "write_decision_vocabulary", write_vocabulary)

    def configure(*, scheduled=True):
        inputs = _inputs(scheduled=scheduled)

        def collect(checkout):
            assert checkout == root
            return inputs

        monkeypatch.setattr(snapshot, "collect_repo", collect)
        return SimpleNamespace(vendor=vendor, root=root, inputs=inputs, public_keys=public_keys)

    return configure


def _read_bundle(vendor, root, out, monkeypatch):
    """Run the export child in process so the synthetic input boundary is shared."""
    def run(command, **_):
        export_out = Path(command[command.index("--export-data") + 1])
        data_dir = Path(command[command.index("--data-dir") + 1])
        vendor.export_data(export_out, data_dir)
        return subprocess.CompletedProcess(command, 0, stdout=b"", stderr=b"")

    monkeypatch.setattr(vendor.subprocess, "run", run)
    out.mkdir(parents=True)
    vendor.bundle_data(out, root)
    namespace = {}
    exec((out / "bundled_data.py").read_text(encoding="utf-8"), namespace)
    return namespace["read"]


def _verified_prices(raw, public_keys):
    hmac = snapshot.load_snapshot_bytes(raw, key=KEY)
    ed25519 = snapshot.load_snapshot_bytes(raw, key=None, public_keys=public_keys)
    assert hmac.signature_verified is True
    assert ed25519.signature_verified is True
    assert ed25519.signature_key_id == "model402-fixture"
    return hmac


def test_export_builds_a_signed_successor_at_the_current_expiry(export_fixture, tmp_path):
    fixture = export_fixture()
    out = tmp_path / "exports"
    fixture.vendor.export_data(out, fixture.root)
    current = _verified_prices((out / CURRENT).read_bytes(), fixture.public_keys)
    assert current.valid_until == BOUNDARY
    assert current.fact(OFFERING, "offering.price.input").value == 2
    assert current.fact(OFFERING, "offering.price.output").value == 10
    assert (out / SUCCESSOR).exists(), "a dated primary must export its successor"
    successor = _verified_prices((out / SUCCESSOR).read_bytes(), fixture.public_keys)
    assert successor.valid_from == BOUNDARY
    assert successor.as_of == BOUNDARY
    assert successor.fact(OFFERING, "offering.price.input").value == 4
    assert successor.fact(OFFERING, "offering.price.output").value == 20
    assert successor.snapshot_id != current.snapshot_id


def test_bundle_embeds_both_signed_price_snapshots(export_fixture, tmp_path, monkeypatch):
    fixture = export_fixture()
    read = _read_bundle(fixture.vendor, fixture.root, tmp_path / "bundle", monkeypatch)
    assert read("/api/" + SUCCESSOR) is not None, "the successor must reach bundled_data"
    current = _verified_prices(read("/api/" + CURRENT), fixture.public_keys)
    successor = _verified_prices(read("/api/" + SUCCESSOR), fixture.public_keys)
    assert [current.fact(OFFERING, "offering.price.input").value,
            successor.fact(OFFERING, "offering.price.input").value] == [2, 4]


def test_successor_vocabulary_names_its_snapshot_and_reaches_the_bundle(export_fixture, tmp_path, monkeypatch):
    fixture = export_fixture()
    out = tmp_path / "exports"
    fixture.vendor.export_data(out, fixture.root)
    assert (out / SUCCESSOR_VOCABULARY).exists(), "the successor needs its matching vocabulary"
    current = _verified_prices((out / CURRENT).read_bytes(), fixture.public_keys)
    successor = _verified_prices((out / SUCCESSOR).read_bytes(), fixture.public_keys)
    assert json.loads((out / "decision/vocabulary.json").read_text())["snapshot"] == current.snapshot_id
    assert json.loads((out / SUCCESSOR_VOCABULARY).read_text())["snapshot"] == successor.snapshot_id
    read = _read_bundle(fixture.vendor, fixture.root, tmp_path / "bundle", monkeypatch)
    assert read("/api/" + SUCCESSOR_VOCABULARY) == (out / SUCCESSOR_VOCABULARY).read_bytes()
    assert json.loads(read("/api/decision/vocabulary.json"))["snapshot"] == current.snapshot_id


def test_real_vocabulary_builder_can_evaluate_future_price_templates(export_fixture, monkeypatch):
    from decision.contract import parse_spec
    from decision.engine import decide
    from decision.vocabulary import build_vocabulary

    fixture = export_fixture()
    built = snapshot.build_from_repo(
        fixture.root, premier=fixture.root / "premier/slice-1.yaml", as_of=BOUNDARY,
    )
    future = snapshot.load_snapshot_bytes(built.to_bytes(), key=KEY)
    monkeypatch.setattr(snapshot, "datetime", _BuildClock)
    spec = parse_spec({
        "spec_version": 1, "snapshot": "latest", "explain": "none",
        "optimize": {"min": "offering.price.input"},
    }, facets=registry.facet)
    with pytest.raises(snapshot.SnapshotError, match="not yet valid"):
        decide(spec, future, facets=registry.facet)
    vocabulary = build_vocabulary(future)
    assert vocabulary["snapshot"] == future.snapshot_id
    assert vocabulary["templates"]
    with pytest.raises(snapshot.SnapshotError, match="not yet valid"):
        decide(spec, future, facets=registry.facet)


def test_undated_export_keeps_current_bytes_and_omits_successor(export_fixture, tmp_path, monkeypatch):
    fixture = export_fixture(scheduled=False)
    out = tmp_path / "exports"
    build_from_repo = snapshot.build_from_repo
    build_dates = []

    def record_build(*args, **kwargs):
        build_dates.append(kwargs["as_of"])
        return build_from_repo(*args, **kwargs)

    monkeypatch.setattr(snapshot, "build_from_repo", record_build)
    fixture.vendor.export_data(out, fixture.root)
    assert build_dates == [BUILD_DAY]
    expected = snapshot.build_from_repo(
        fixture.root, premier=fixture.root / "premier/slice-1.yaml", as_of=BUILD_DAY,
    ).to_bytes()
    assert (out / CURRENT).read_bytes() == expected
    assert not (out / SUCCESSOR).exists()
    assert not (out / SUCCESSOR_VOCABULARY).exists()
    read = _read_bundle(fixture.vendor, fixture.root, tmp_path / "bundle", monkeypatch)
    assert read("/api/" + CURRENT) == expected
    assert read("/api/" + SUCCESSOR) is None
    assert read("/api/" + SUCCESSOR_VOCABULARY) is None


def test_undated_export_removes_a_previously_written_successor(export_fixture, tmp_path):
    fixture = export_fixture(scheduled=False)
    out = tmp_path / "exports"
    (out / SUCCESSOR).parent.mkdir(parents=True)
    (out / SUCCESSOR).write_bytes(b"stale successor from a previous export")
    (out / SUCCESSOR_VOCABULARY).write_bytes(b"stale successor vocabulary")
    fixture.vendor.export_data(out, fixture.root)
    assert not (out / SUCCESSOR).exists(), "an old successor must not survive an undated export"
    assert not (out / SUCCESSOR_VOCABULARY).exists()


def test_vendor_bundle_is_deterministic_with_fixed_date_build_and_keys(export_fixture, tmp_path, monkeypatch):
    fixture = export_fixture()
    first = tmp_path / "first"
    second = tmp_path / "second"
    first_read = _read_bundle(fixture.vendor, fixture.root, first, monkeypatch)
    second_read = _read_bundle(fixture.vendor, fixture.root, second, monkeypatch)
    assert first_read("/api/" + SUCCESSOR) is not None, "determinism must include a successor"
    assert (first / "bundled_data.py").read_bytes() == (second / "bundled_data.py").read_bytes()
    for path in (CURRENT, SUCCESSOR):
        assert first_read("/api/" + path) == second_read("/api/" + path)
        envelope = json.loads(gzip.decompress(first_read("/api/" + path)))
        assert envelope["signature"]["alg"] == "hmac-sha256"
        assert envelope["signatures"][0]["alg"] == "ed25519"
