"""The decision Worker uses the shared engine and refuses untrusted snapshots."""

from __future__ import annotations

import ast
import asyncio
import gzip
import importlib.util
import json
import sys
from datetime import date
from pathlib import Path
from time import perf_counter
from types import SimpleNamespace

import pytest
from typer.testing import CliRunner

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKER_ROOT = REPO_ROOT / "api" / "worker"
WORKER_SRC = WORKER_ROOT / "src"
sys.path.insert(0, str(REPO_ROOT))

from cli.modelspec import cli as cli_mod  # noqa: E402
from decision.excluded import excluded_sources  # noqa: E402
from decision.registry import default as default_registry  # noqa: E402
from decision.snapshot import (  # noqa: E402
    SnapshotInputs,
    SnapshotIntegrityError,
    build_snapshot,
    collect_repo,
    load_built_snapshot,
    load_premier,
    load_snapshot_bytes,
)
from tests.snapshot_records import (  # noqa: E402
    SOURCES,
    evidence,
    fact,
    model,
    offering,
    thirty_models,
)
from tests.test_x402 import _entry_env, _Req, entry  # noqa: E402, F401

KEY = b"model-151-test-key"
COLD_DOMAIN_DECISION_BUDGET_MS = 1_000


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
                fact(
                    "model",
                    "lab/" + name,
                    "model.weights_openness",
                    "open_weights" if name == "a" else "closed_weights",
                ),
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


def test_worker_and_cli_agree_on_a_value_preference(
    tmp_path: Path, service, snapshot_bytes: bytes, snapshot,
) -> None:
    payload = {
        "spec_version": 1,
        "where": ["model.max_output_tokens >= 8000"],
        "optimize": {"weights": {
            "model.max_output_tokens": 0.2,
            "model.weights_openness": {"prefer": "open_weights", "weight": 0.8},
        }},
        "explain": "summary",
        "limit": 2,
    }
    snapshot_path = tmp_path / "snapshot.json.gz"
    snapshot_path.write_bytes(snapshot_bytes)
    spec_path = tmp_path / "prefer.yaml"
    spec_path.write_text(json.dumps(payload), encoding="utf-8")

    cli = CliRunner().invoke(
        cli_mod.app,
        ["decide", str(spec_path), "--snapshot-file", str(snapshot_path), "--json"],
        env={"MODELSPEC_SNAPSHOT_KEY": KEY.decode()},
    )
    status, body = service.decide(payload, snapshot)

    assert cli.exit_code == 0, cli.output
    assert status == 200
    assert [row["offering"]["model"] for row in body["results"]] == ["lab/a", "lab/b"]
    assert service.serialise(body) == cli.stdout.encode("utf-8")


def test_worker_and_cli_agree_on_a_boolean_preference(
    tmp_path: Path, service,
) -> None:
    def sold(provider: str, value, *, state: str = "known"):
        oid = f"{provider}/lab/m/global/standard"
        return offering("lab/m", provider, facts=[
            fact("offering", oid, "offering.price.input", 1.0, source="src-pricing"),
            fact("offering", oid, "offering.data.zero_retention", value, state=state),
        ])

    built = build_snapshot(
        SnapshotInputs(
            models=[model("lab/m")],
            offerings=[
                sold("p-false", False),
                sold("p-true", True),
                sold("p-unknown", None, state="unknown"),
            ],
            evidence=[],
            sources=SOURCES,
        ),
        gate=False,
        as_of=date(2026, 9, 25),
    )
    raw = built.to_bytes(key=KEY)
    snapshot = load_snapshot_bytes(raw, key=KEY, source="boolean preference snapshot")
    payload = {
        "spec_version": 1,
        "optimize": {"weights": {
            "offering.data.zero_retention": {"prefer": True, "weight": 1},
        }},
        "explain": "summary",
    }
    snapshot_path = tmp_path / "snapshot.json.gz"
    snapshot_path.write_bytes(raw)
    spec_path = tmp_path / "boolean.yaml"
    spec_path.write_text(json.dumps(payload), encoding="utf-8")

    cli = CliRunner().invoke(
        cli_mod.app,
        ["decide", str(spec_path), "--snapshot-file", str(snapshot_path), "--json"],
        env={"MODELSPEC_SNAPSHOT_KEY": KEY.decode()},
    )
    status, body = service.decide(payload, snapshot)

    assert cli.exit_code == 0, cli.output
    assert status == 200
    assert [row["offering"]["provider"] for row in body["results"]][0] == "p-true"
    values = {
        row["offering"]["provider"]: row["contributions"][0]["value"]
        for row in body["results"]
    }
    assert values == {"p-true": 1, "p-false": 0, "p-unknown": 0}
    unknown = next(r for r in body["results"] if r["offering"]["provider"] == "p-unknown")
    assert unknown["warnings"] == ["unknown_preference_value"]
    assert service.serialise(body) == cli.stdout.encode("utf-8")


def test_value_preference_with_evidence_qualifier_is_a_400(service, snapshot) -> None:
    payload = _payload() | {"optimize": {"weights": {
        "model.weights_openness @independent": {"prefer": "open_weights", "weight": 1},
    }}}

    status, body = service.decide(payload, snapshot)

    assert status == 400
    assert body["error"]["code"] == "invalid_spec"
    [issue] = body["error"]["issues"]
    assert issue["field"] == "model.weights_openness"
    assert issue["reason"] == "evidence qualifiers are only valid on evidence facets"


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


def test_unknown_preference_facet_is_a_clean_bad_request(service, snapshot) -> None:
    payload = _payload() | {
        "optimize": {
            "weights": {"model.not_a_facet": {"prefer": True, "weight": 1.0}}
        }
    }

    status, body = service.decide(payload, snapshot)

    assert status == 400
    assert body["error"]["code"] == "invalid_spec"
    assert body["error"]["issues"] == [
        {
            "path": "optimize.weights",
            "field": "model.not_a_facet",
            "condition": None,
            "reason": "unknown facet 'model.not_a_facet': not in registry/facets.yaml",
        }
    ]


def test_unknown_excluded_benchmark_is_a_clean_400(service, snapshot) -> None:
    status, body = service.decide(
        _payload() | {"exclude_benchmarks": ["made_up_benchmark"]},
        snapshot,
    )

    assert status == 400
    assert body["error"]["code"] == "invalid_spec"
    assert body["error"]["issues"] == [
        {
            "path": "exclude_benchmarks[0]",
            "condition": None,
            "field": "made_up_benchmark",
            "reason": "unknown benchmark ID in this snapshot",
        }
    ]


def test_a_refinement_weight_the_snapshot_cannot_rank_is_an_invalid_spec(
    service, snapshot
) -> None:
    """Refinements rank since MODEL-190, but only those the snapshot carries."""
    payload = _payload() | {
        "optimize": {
            "weights": {
                "software_engineering": 0.5,
                "software_engineering/python": 0.5,
            }
        }
    }

    status, body = service.decide(payload, snapshot)

    assert status == 400
    assert body["contract_version"] == "2.10"
    assert body["error"]["code"] == "invalid_spec"
    [issue] = body["error"]["issues"]
    assert issue["field"] == "software_engineering/python"
    assert issue["path"] == "optimize.weights"
    assert "not a registered refinement in this snapshot" in issue["reason"]


def test_a_requested_snapshot_must_be_the_loaded_snapshot(service, snapshot) -> None:
    status, body = service.decide(_payload() | {"snapshot": "snap_0123456789abcdef"}, snapshot)
    assert status == 409
    assert body["error"]["code"] == "snapshot_not_loaded"
    assert body["snapshot"] == snapshot.snapshot_id


def test_worker_compare_returns_an_http_comparison_from_two_snapshots(service) -> None:
    def make(context: int, when: date):
        built = build_snapshot(SnapshotInputs(
            models=[model("lab/a", facts=[
                fact("model", "lab/a", "model.context_window", context),
            ])],
            offerings=[offering("lab/a", "p1")],
            sources=SOURCES,
        ), gate=False, as_of=when)
        return load_built_snapshot(
            built, include_archive=True, source="worker compare test build"
        )

    old, new = make(100, date(2026, 9, 26)), make(200, date(2026, 9, 27))
    status, body = service.compare({
        "compare_to": old.snapshot_id,
        "spec": {
            "spec_version": 1,
            "snapshot": new.snapshot_id,
            "where": ["model.context_window >= 150"],
            "optimize": {"max": "model.context_window"},
        },
    }, old, new)

    assert status == 200
    assert body["endpoint"] == "compare"
    assert body["result"]["snapshot"] == {
        "old": {"id": old.snapshot_id, "as_of": "2026-09-26"},
        "new": {"id": new.snapshot_id, "as_of": "2026-09-27"},
    }
    assert body["result"]["models"][0]["model"] == "lab/a"
    assert body["result"]["spec_snapshot_ignored"] is True


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

    compare_status, compare_body = service.no_snapshot(
        "the published decision snapshot does not exist", endpoint="compare"
    )
    assert compare_status == 503
    assert compare_body["endpoint"] == "compare"


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


def test_fresh_snapshot_load_and_first_domain_decision_stay_under_budget(service) -> None:
    """Guard the Worker cold path with the repository's published data shape."""
    built = build_snapshot(
        collect_repo(REPO_ROOT),
        registry=default_registry(),
        premier=load_premier(REPO_ROOT / "premier" / "slice-1.yaml"),
        as_of=date(2026, 9, 25),
        guard=excluded_sources(),
        gate=False,
    )
    raw = built.to_bytes(key=KEY)
    payload = {
        "spec_version": 1,
        "capabilities": {"software_engineering": "required"},
        "optimize": {"max": "software_engineering"},
        "explain": "full",
        "limit": 20,
    }

    start = perf_counter()
    loaded = service.load_snapshot(raw, key=KEY)
    loaded_at = perf_counter()
    status, body = service.decide(payload, loaded)
    service.serialise(body)
    decided_at = perf_counter()

    load_ms = (loaded_at - start) * 1_000
    decision_ms = (decided_at - loaded_at) * 1_000
    total_ms = (decided_at - start) * 1_000
    assert status == 200
    assert body["results"]
    assert total_ms < COLD_DOMAIN_DECISION_BUDGET_MS, (
        f"fresh Worker snapshot load plus first domain decision took {total_ms:.2f} ms "
        f"(load {load_ms:.2f} ms, decision and serialization {decision_ms:.2f} ms)"
    )

    excluded_payload = payload | {"exclude_benchmarks": ["swe_bench_pro"]}
    excluded_start = perf_counter()
    excluded_status, excluded_body = service.decide(excluded_payload, loaded)
    service.serialise(excluded_body)
    excluded_ms = (perf_counter() - excluded_start) * 1_000
    assert excluded_status == 200
    assert excluded_body["benchmark_exclusions"]["benchmarks"] == ["swe_bench_pro"]
    assert excluded_ms < 10_000, (
        f"lineup-scale benchmark exclusion and refit took {excluded_ms:.2f} ms"
    )

    warm_samples = []
    for _ in range(20):
        warm_start = perf_counter()
        status, body = service.decide(excluded_payload, loaded)
        service.serialise(body)
        warm_samples.append((perf_counter() - warm_start) * 1_000)
        assert status == 200
    warm_p95 = sorted(warm_samples)[int(len(warm_samples) * 0.95) - 1]
    print(f"benchmark exclusion cold {excluded_ms:.2f} ms; cached warm p95 {warm_p95:.2f} ms")
    assert warm_p95 < COLD_DOMAIN_DECISION_BUDGET_MS, (
        f"cached lineup-scale benchmark exclusion p95 was {warm_p95:.2f} ms"
    )


def test_vendor_copies_the_shared_decision_engine_and_registry(tmp_path: Path) -> None:
    spec = importlib.util.spec_from_file_location(
        "decision_worker_vendor", WORKER_ROOT / "vendor.py"
    )
    vendor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(vendor)
    bundle = vendor.build(tmp_path / "python_modules")

    required = {
        Path("api/classes.py"),
        Path("decision/capability.py"),
        Path("decision/contract.py"),
        Path("decision/engine.py"),
        Path("decision/explain.py"),
        Path("decision/snapshot.py"),
        Path("decision/vocabulary.py"),
        Path("registry/facets.yaml"),
        Path("registry/domains.yaml"),
        Path("registry/refinements.yaml"),
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


def test_entry_routes_compare_through_the_existing_access_gate() -> None:
    source = (WORKER_SRC / "entry.py").read_text(encoding="utf-8")
    assert '"POST /v1/compare"' in source
    assert '"/v1/compare"' in source
    assert "await access.gate(" in source
    assert "await self._compare(" in source


def test_entry_imports_the_decision_stack_only_for_decision_routes() -> None:
    source = (WORKER_SRC / "entry.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    top_level_imports = {
        alias.name
        for node in tree.body
        if isinstance(node, ast.Import)
        for alias in node.names
    }

    assert "decide_service" not in top_level_imports
    assert 'if path in ("/v1/decide", "/v1/compare"):' in source
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


@pytest.mark.parametrize("human_access", [False, True])
def test_server_timing_reports_only_snapshot_work(
    entry, service, snapshot_bytes, snapshot, monkeypatch, human_access,  # noqa: F811
):
    elapsed = [0.0]
    clock = [0.0]
    refresh = ["cold"]

    async def fetch_snapshot(etag):
        elapsed[0] += 0.0123
        if refresh[0] == "failed":
            raise OSError("origin unavailable")
        return SimpleNamespace(status=200 if etag is None else 304,
                               etag='"snapshot"', body=snapshot_bytes)

    holder = service.SnapshotHolder(fetch_snapshot, clock=lambda: clock[0])
    monkeypatch.setattr(entry, "_decide_service", lambda: service)
    monkeypatch.setattr(entry, "_decision_holder", lambda origin: holder)
    monkeypatch.setattr(entry.time, "perf_counter", lambda: elapsed[0])
    decide = service.decide
    serialise = service.serialise

    def measured_decide(*args, **kwargs):
        elapsed[0] += 0.001
        return decide(*args, **kwargs)

    def measured_serialise(body):
        elapsed[0] += 0.0025
        return serialise(body)

    monkeypatch.setattr(service, "decide", measured_decide)
    monkeypatch.setattr(service, "serialise", measured_serialise)
    gate = entry.access.gate

    async def slow_gate(**kwargs):
        result = await gate(**kwargs)
        elapsed[0] += 10
        return result

    async def admit(*args):
        elapsed[0] += 10
        return 200, None, None, {}

    monkeypatch.setattr(entry.access, "gate", slow_gate)
    monkeypatch.setattr(entry.human_gate, "admit", admit)
    worker = entry.Default()
    worker.env = _entry_env(MODELSPEC_SNAPSHOT_KEY=KEY.decode(),
                            X402_ENABLED="false",
                            HUMAN_GATE_ENABLED=str(human_access).lower())
    expected_bytes = serialise(decide(_payload(), snapshot)[1])
    for state, now, expected_timing in (
        ("cold", 0, "snapshot;dur=12.3"),
        ("warm", 1, None),
        ("revalidated", 61, "snapshot;dur=12.3"),
        ("failed", 122, "snapshot;dur=12.3"),
    ):
        refresh[0], clock[0] = state, now
        request = _Req("/v1/decide", _payload(),
                       headers={"Origin": "https://modelspec.dev"})
        response = asyncio.run(worker.fetch(request))
        assert response.status == 200
        assert response.body.encode("utf-8") == expected_bytes
        assert response.headers.get("Server-Timing") == expected_timing
        exposed = response.headers["access-control-expose-headers"].lower().split(", ")
        assert "server-timing" in exposed


def test_access_and_billing_switches_stay_off() -> None:
    config = (WORKER_ROOT / "wrangler.jsonc").read_text(encoding="utf-8")
    for name in ("ACCESS_ENFORCED", "BILLING_ENABLED", "X402_ENABLED"):
        assert f'"{name}": "false"' in config


def test_an_evidence_row_without_measured_by_is_kept_out_and_no_decision_breaks():
    """MODEL-239: a refresh can admit a verified row whose card never said who
    measured it. Admission drops it as ``unclassified`` instead of letting the
    contract's required ``measured_by`` fail every decision that cites it.

    Runs under the Worker's own pinned pydantic too (rank-api.yml lists this
    file), the pair the 2026-09-29 corpus drift was found on."""
    import dataclasses

    from tests.corpus import corpus

    inputs = collect_repo(REPO_ROOT)
    stripped = [
        {**dict(row), "measured_by": None} if position % 4 == 0 else row
        for position, row in enumerate(inputs.evidence)
    ]
    dropped = sum(1 for a, b in zip(inputs.evidence, stripped, strict=True) if a is not b)
    assert dropped > 0
    tampered = build_snapshot(
        dataclasses.replace(inputs, evidence=stripped), registry=default_registry(),
        premier=load_premier(REPO_ROOT / "premier" / "slice-1.yaml"),
        as_of=corpus.AS_OF, guard=excluded_sources(), gate=False,
    )
    assert 0 < tampered.content["excluded"]["unclassified"] <= dropped
    snapshot = load_snapshot_bytes(tampered.to_bytes(key=corpus.KEY), key=corpus.KEY,
                                   include_archive=True, source="model-239 test")
    rows = [row for _, row in snapshot.corpus_evidence()]
    assert rows and all(row.measured_by for row in rows)

    service = corpus.worker_service()
    cases = corpus.load_cases()
    loaded = {}
    failed = []
    for case in cases:
        if case.snapshot == "repo":
            answer = corpus.run_worker(case, snapshot, service)
        else:
            if case.snapshot not in loaded:
                loaded[case.snapshot] = corpus.load(corpus.snapshot_bytes(case.snapshot))
            answer = corpus.run_worker(case, loaded[case.snapshot], service)
        if b"worker_exception" in answer[1]:
            failed.append((case.id, answer[1][:200]))
    assert len(cases) > 0
    assert failed == []


def test_timed_bytes_are_never_served_for_a_rewritten_body(entry, service, monkeypatch):  # noqa: F811
    # x402's unfunded fallback answers with a copy of the decision that adds
    # credits.exhausted; the bytes timed for the original must not stand in.
    monkeypatch.setattr(entry, "_decide_service", lambda: service)
    original = {"decision": "x"}
    transport = entry._DecisionTransport()
    transport.body = original
    transport.serialised = service.serialise(original)
    transport.headers["Server-Timing"] = "decide;dur=1.0"
    rewritten = {**original, "credits": {"exhausted": True}}
    response = entry._decision_response(service.HTTP_OK, rewritten, None, transport)
    assert json.loads(response.body)["credits"] == {"exhausted": True}
    same = entry._decision_response(service.HTTP_OK, original, None, transport)
    assert json.loads(same.body) == original
