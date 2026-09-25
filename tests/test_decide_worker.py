"""The decision Worker uses the shared engine and refuses untrusted snapshots."""

from __future__ import annotations

import ast
import gzip
import importlib.util
import json
import sys
from datetime import date
from pathlib import Path
from time import perf_counter

import pytest
from typer.testing import CliRunner

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKER_ROOT = REPO_ROOT / "api" / "worker"
WORKER_SRC = WORKER_ROOT / "src"
sys.path.insert(0, str(REPO_ROOT))

from cli.modelspec import cli as cli_mod  # noqa: E402
from decision.snapshot import (  # noqa: E402
    SnapshotInputs,
    SnapshotIntegrityError,
    build_snapshot,
    load_snapshot_bytes,
)
from tests.snapshot_records import SOURCES, evidence, fact, model, thirty_models  # noqa: E402

KEY = b"model-151-test-key"


def _load_service():
    spec = importlib.util.spec_from_file_location(
        "modelspec_decide_service", WORKER_SRC / "decide_service.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def service():
    return _load_service()


@pytest.fixture(scope="module")
def snapshot_bytes() -> bytes:
    models = [
        model(
            "lab/" + name,
            facts=[
                fact("model", "lab/" + name, "model.context_window", context),
                fact("model", "lab/" + name, "model.max_output_tokens", output),
            ],
        )
        for name, context, output in [("a", 128_000, 8_000), ("b", 64_000, 16_000)]
    ]
    rows = [
        evidence("lab/a", "swe_bench_pro", 70, measured_by="independent"),
        evidence("lab/b", "swe_bench_pro", 60, measured_by="independent"),
    ]
    built = build_snapshot(
        SnapshotInputs(
            models=models,
            evidence=rows,
            sources=SOURCES,
            benchmark_domains={"swe_bench_pro": [("software_engineering", "direct")]},
        ),
        as_of=date(2026, 9, 25),
    )
    return built.to_bytes(key=KEY)


@pytest.fixture(scope="module")
def snapshot(snapshot_bytes):
    return load_snapshot_bytes(snapshot_bytes, key=KEY, source="test snapshot")


def _payload(level: str = "none") -> dict:
    return {
        "spec_version": 1,
        "capabilities": {"software_engineering": "required"},
        "where": ["model.max_output_tokens >= 8000"],
        "optimize": {"max": "swe_bench_pro"},
        "explain": level,
        "limit": 2,
    }


@pytest.mark.parametrize("level", ["none", "summary", "full"])
def test_worker_decision_is_byte_identical_to_modelspect_decide(
    tmp_path: Path, service, snapshot_bytes: bytes, snapshot, level: str
) -> None:
    snapshot_path = tmp_path / "snapshot.json.gz"
    snapshot_path.write_bytes(snapshot_bytes)
    spec_path = tmp_path / "spec.yaml"
    spec_path.write_text(json.dumps(_payload(level)), encoding="utf-8")

    cli = CliRunner().invoke(
        cli_mod.app,
        ["decide", str(spec_path), "--snapshot-file", str(snapshot_path), "--json"],
        env={"MODELSPEC_SNAPSHOT_KEY": KEY.decode()},
    )
    assert cli.exit_code == 0, cli.output

    status, body = service.decide(_payload(level), snapshot)
    assert status == 200
    assert service.serialise(body) == cli.stdout.encode("utf-8")
    assert service.serialise(body).count(b"\n") == 1, "the body is compact JSON"
    assert body["snapshot"] == snapshot.snapshot_id
    assert body["explain"] == level


def test_every_recall_contract_spec_has_worker_cli_parity(
    tmp_path: Path, service, snapshot_bytes: bytes, snapshot
) -> None:
    """MODEL-139 may add specs without needing another endpoint test edit."""
    paths = sorted((REPO_ROOT / "tests" / "recall").glob("**/*.spec.yaml"))
    if not paths:
        pytest.skip("MODEL-139 has not added decision-contract recall specs yet")
    snapshot_path = tmp_path / "snapshot.json.gz"
    snapshot_path.write_bytes(snapshot_bytes)
    for path in paths:
        raw = path.read_text(encoding="utf-8")
        cli = CliRunner().invoke(
            cli_mod.app,
            ["decide", str(path), "--snapshot-file", str(snapshot_path), "--json"],
            env={"MODELSPEC_SNAPSHOT_KEY": KEY.decode()},
        )
        assert cli.exit_code == 0, f"{path}: {cli.output}"
        payload = json.loads(json.dumps(__import__("yaml").safe_load(raw)))
        status, body = service.decide(payload, snapshot)
        assert status == 200
        assert service.serialise(body) == cli.stdout.encode("utf-8"), path


def test_unsigned_snapshot_is_refused(service, snapshot_bytes: bytes) -> None:
    envelope = json.loads(gzip.decompress(snapshot_bytes))
    envelope["signature"] = None
    unsigned = gzip.compress(json.dumps(envelope).encode("utf-8"))
    with pytest.raises(SnapshotIntegrityError, match="unsigned snapshot"):
        load_snapshot_bytes(unsigned, key=KEY, source="unsigned fixture")
    with pytest.raises(service.SnapshotRefusalError, match="unsigned snapshot"):
        service.load_snapshot(unsigned, key=KEY)


def test_tampered_snapshot_is_refused(service, snapshot_bytes: bytes) -> None:
    envelope = json.loads(gzip.decompress(snapshot_bytes))
    envelope["content"]["as_of"] = "2099-01-01"
    tampered = gzip.compress(json.dumps(envelope).encode("utf-8"))
    with pytest.raises(SnapshotIntegrityError, match="content hash mismatch"):
        load_snapshot_bytes(tampered, key=KEY, source="tampered fixture")
    with pytest.raises(service.SnapshotRefusalError, match="content hash mismatch"):
        service.load_snapshot(tampered, key=KEY)


def test_a_snapshot_verification_key_is_mandatory(service, snapshot_bytes: bytes) -> None:
    with pytest.raises(service.SnapshotRefusalError, match="verification key"):
        service.load_snapshot(snapshot_bytes, key=None)


def test_invalid_specs_name_every_contract_issue(service, snapshot) -> None:
    status, body = service.decide(_payload() | {"unknown": True}, snapshot)
    assert status == 400
    assert body["error"]["code"] == "invalid_spec"
    assert body["snapshot"] == snapshot.snapshot_id
    assert body["error"]["issues"][0]["path"] == "unknown"


def test_a_requested_snapshot_must_be_the_loaded_snapshot(service, snapshot) -> None:
    status, body = service.decide(_payload() | {"snapshot": "snap_0123456789abcdef"}, snapshot)
    assert status == 409
    assert body["error"]["code"] == "snapshot_not_loaded"
    assert body["snapshot"] == snapshot.snapshot_id


def test_missing_published_snapshot_is_retryable(service) -> None:
    status, body = service.no_snapshot("the published decision snapshot does not exist")

    assert status == 503
    assert body == {
        "contract_version": service.contract.CONTRACT_VERSION,
        "endpoint": "decide",
        "snapshot": None,
        "error": "no_snapshot",
        "message": "the published decision snapshot does not exist",
    }
    assert service.RETRY_AFTER_SECONDS > 0


def test_explain_none_p95_is_under_200_ms(service) -> None:
    raw = build_snapshot(thirty_models()).to_bytes(key=KEY)
    snapshot = service.load_snapshot(raw, key=KEY)
    payload = {
        "spec_version": 1,
        "where": ["model.weights_openness = open_weights"],
        "optimize": {"max": "evidence.benchmark"},
        "explain": "none",
        "limit": 20,
    }
    for _ in range(10):
        service.decide(payload, snapshot)
    samples = []
    for _ in range(200):
        start = perf_counter()
        status, body = service.decide(payload, snapshot)
        service.serialise(body)
        samples.append((perf_counter() - start) * 1000)
        assert status == 200
    p95 = sorted(samples)[int(len(samples) * 0.95) - 1]
    assert p95 < 200, f"warm in-process p95 was {p95:.2f} ms"


def test_vendor_copies_the_shared_decision_engine_and_registry(tmp_path: Path) -> None:
    spec = importlib.util.spec_from_file_location(
        "decision_worker_vendor", WORKER_ROOT / "vendor.py"
    )
    vendor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(vendor)
    bundle = vendor.build(tmp_path / "python_modules")

    required = {
        Path("api/classes.py"),
        Path("decision/contract.py"),
        Path("decision/engine.py"),
        Path("decision/snapshot.py"),
        Path("registry/facets.yaml"),
        Path("registry/domains.yaml"),
    }
    assert required <= set(vendor.SOURCES)
    for source in required:
        assert (bundle / vendor.SOURCES[source]).read_bytes() == (REPO_ROOT / source).read_bytes()


def test_entry_routes_decide_through_the_existing_access_gate() -> None:
    source = (WORKER_SRC / "entry.py").read_text(encoding="utf-8")
    assert '"POST /v1/decide"' in source
    assert '"/v1/decide"' in source
    assert "await access.gate(" in source
    assert "await self._decide(" in source


def test_entry_imports_the_decision_stack_only_for_the_decide_route() -> None:
    source = (WORKER_SRC / "entry.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    top_level_imports = {
        alias.name
        for node in tree.body
        if isinstance(node, ast.Import)
        for alias in node.names
    }

    assert "decide_service" not in top_level_imports
    assert 'if path == "/v1/decide":' in source
    assert "decider = _decide_service()" in source
    assert 'headers["retry-after"] = str(decider.RETRY_AFTER_SECONDS)' in source


def test_cors_is_for_the_production_site_and_the_preview_only() -> None:
    """The live decide page on modelspec.dev must reach the API (a flip to
    SITE_MODE=live without it served a page that could not answer), and no
    wildcard origin is allowed."""
    source = (WORKER_SRC / "entry.py").read_text(encoding="utf-8")
    for origin in ("https://modelspec.dev", "https://www.modelspec.dev",
                   "https://internal.modelspec-7np.pages.dev"):
        assert f'"{origin}"' in source
    assert '"access-control-allow-origin": "*"' not in source.lower()


def test_access_and_billing_switches_stay_off() -> None:
    config = (WORKER_ROOT / "wrangler.jsonc").read_text(encoding="utf-8")
    for name in ("ACCESS_ENFORCED", "BILLING_ENABLED", "X402_ENABLED"):
        assert f'"{name}": "false"' in config
