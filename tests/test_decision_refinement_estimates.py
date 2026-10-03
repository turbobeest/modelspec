"""Nested refinement estimates: the domain estimate plus a pooled adjustment (MODEL-190)."""

from __future__ import annotations

import importlib.util
import json
import sys
from datetime import date, timedelta
from pathlib import Path

import pytest
from typer.testing import CliRunner

from decision.capability import BenchmarkSpec, CapabilityObservation, fit_capabilities
from decision.contract import SpecError, parse_spec
from decision.engine import decide
from decision.registry import default as default_registry
from decision.snapshot import (
    SnapshotInputs,
    build_snapshot,
    load_snapshot_bytes,
)
from tests.snapshot_records import SOURCES, evidence, fact, model

AS_OF = date(2026, 9, 25)
KEY = b"model-190-refinements"
RUST = "software_engineering/rust"

# General coding and a Rust suite. lab/a is best at general coding and worst
# at Rust. lab/b has no Rust score.
GENERAL = {"lab/a": 95.0, "lab/b": 84.0, "lab/c": 70.0, "lab/d": 62.0, "lab/e": 50.0}
RUST_SUITE = {"lab/a": 20.0, "lab/c": 88.0, "lab/d": 80.0, "lab/e": 45.0}


def _text_generator(mid: str) -> dict:
    return model(mid, facts=[
        fact("model", mid, "model.class", "text-generator"),
        fact("model", mid, "model.context_window", 128_000),
        fact("model", mid, "model.weights_openness", "open_weights"),
        fact("model", mid, "model.input_modalities", ["text"]),
        fact("model", mid, "licence.user_cap", "unbounded"),
    ])


def _built():
    rows = [evidence(mid, "code_general", score) for mid, score in GENERAL.items()]
    rows += [evidence(mid, "rust_suite", score) for mid, score in RUST_SUITE.items()]
    metadata = {"random_baseline": 0, "sample_size": 500, "direction": "higher_is_better"}
    return build_snapshot(
        SnapshotInputs(
            models=[_text_generator(mid) for mid in GENERAL],
            evidence=rows,
            sources=SOURCES,
            benchmark_domains={
                "code_general": [("software_engineering", "direct")],
                "rust_suite": [("software_engineering", "direct")],
                "java_suite": [("software_engineering", "direct")],
            },
            benchmark_refinements={
                "rust_suite": [("rust", "direct")],
                # Tagged, but no model has a score: not yet measured.
                "java_suite": [("java", "direct")],
            },
            benchmark_metadata={
                name: metadata for name in ("code_general", "rust_suite", "java_suite")
            },
        ),
        registry=default_registry(),
        as_of=AS_OF,
    )


@pytest.fixture(scope="module")
def snapshot_bytes() -> bytes:
    return _built().to_bytes(key=KEY)


@pytest.fixture(scope="module")
def index(snapshot_bytes):
    return load_snapshot_bytes(snapshot_bytes, key=KEY, source="refinement test")


def _decide(index, optimize, *, explain="none", **extra):
    registry = default_registry()
    spec = parse_spec(
        {"spec_version": 1, "optimize": optimize, "explain": explain, "limit": 10, **extra},
        facets=registry.facet,
    )
    return decide(spec, index, facets=registry.facet)


def _order(decision) -> list[str]:
    return [result.offering.model for result in decision.results]


def test_a_rust_weighted_spec_reorders_models_with_rust_evidence(index):
    general = _order(_decide(index, {"weights": {"software_engineering": 1}}))
    rust = _order(_decide(index, {"weights": {RUST: 1}}))

    # lab/d outscores lab/a in Rust; lab/c's Rust score lifts it past lab/b,
    # which has no Rust evidence and keeps its domain value.
    assert general.index("lab/a") < general.index("lab/d")
    assert rust.index("lab/d") < rust.index("lab/a")
    assert general.index("lab/b") < general.index("lab/c")
    assert rust.index("lab/c") < rust.index("lab/b")
    assert set(rust) == set(GENERAL)


def test_a_model_without_rust_evidence_stays_listed_on_its_domain_estimate(index):
    decision = _decide(index, {"weights": {RUST: 1}},
                       capabilities={"software_engineering": "required"})
    result = next(r for r in decision.results if r.offering.model == "lab/b")

    [domain] = result.estimates
    [nested] = result.refinement_estimates
    assert nested.key == RUST
    assert (nested.domain, nested.refinement) == ("software_engineering", "rust")
    assert nested.evidence_count == 0
    assert nested.value == pytest.approx(domain.value)
    assert nested.interval[1] - nested.interval[0] > domain.interval[1] - domain.interval[0]
    assert all(m.model != "lab/b" for m in decision.may_qualify)


def test_rust_evidence_is_counted_and_narrows_the_fallback_interval(index):
    decision = _decide(index, {"weights": {RUST: 1}})
    nested = {r.offering.model: r.refinement_estimates[0] for r in decision.results}

    assert nested["lab/c"].evidence_count == 1
    assert nested["lab/b"].evidence_count == 0
    width = {mid: e.interval[1] - e.interval[0] for mid, e in nested.items()}
    assert width["lab/c"] < width["lab/b"]


def test_refinement_and_parent_weights_combine(index):
    decision = _decide(index, {"weights": {"software_engineering": 0.5, RUST: 0.5}})

    assert decision.status == "answered"
    assert len(decision.results) == len(GENERAL)
    assert decision.answer is not None


def test_a_domain_only_spec_carries_no_refinement_estimates(index):
    decision = _decide(index, {"weights": {"software_engineering": 1}})

    assert all(result.refinement_estimates is None for result in decision.results)
    assert "refinement_estimates" not in decision.model_dump(mode="json")["results"][0]


def test_explanations_name_the_parent_dimension_and_the_refinement(index):
    decision = _decide(index, {"weights": {"software_engineering": 0.5, RUST: 0.5}},
                       explain="summary")
    parts = decision.results[0].contributions

    assert [(p.dimension, p.refinement) for p in parts] == [
        ("software_engineering", None), ("software_engineering", "rust"),
    ]
    rust_c = next(r for r in decision.results if r.offering.model == "lab/c").contributions[1]
    assert {item.benchmark for item in rust_c.evidence} == {"rust_suite"}
    fallback = next(r for r in decision.results if r.offering.model == "lab/b").contributions[1]
    assert "no rust evidence" in fallback.formula.lower()


@pytest.mark.parametrize(("key", "reason"), [
    ("software_engineering/java", "not_measured"),
    ("software_engineering/go", "no_benchmark"),
])
def test_unrankable_refinements_are_refused_as_invalid_spec(index, key, reason):
    with pytest.raises(SpecError) as caught:
        _decide(index, {"weights": {key: 1}})
    [issue] = caught.value.issues
    assert issue.path == "optimize.weights"
    assert issue.field == key
    assert reason in issue.reason


def test_an_unregistered_refinement_is_refused(index):
    with pytest.raises(SpecError) as caught:
        _decide(index, {"weights": {"software_engineering/cobol": 1}})
    assert "software_engineering/cobol" in caught.value.issues[0].reason


def test_a_refinement_under_an_unknown_parent_is_refused_at_parse():
    with pytest.raises(SpecError):
        parse_spec({"spec_version": 1, "optimize": {"weights": {"cooking/rust": 1}}},
                   facets=default_registry().facet)


def test_a_refinement_takes_a_numeric_weight_not_a_value_preference():
    with pytest.raises(SpecError):
        parse_spec(
            {"spec_version": 1,
             "optimize": {"weights": {RUST: {"prefer": True, "weight": 1}}}},
            facets=default_registry().facet,
        )


def _decide_service():
    src = Path(__file__).resolve().parents[1] / "api" / "worker" / "src"
    spec = importlib.util.spec_from_file_location("refinement_decide_service",
                                                  src / "decide_service.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules.setdefault("refinement_decide_service", module)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("explain", ["none", "summary"])
def test_cli_and_worker_answers_are_byte_identical(snapshot_bytes, index, tmp_path, explain):
    from cli.modelspec import cli as cli_mod

    payload = {"spec_version": 1, "explain": explain, "limit": 10,
               "optimize": {"weights": {"software_engineering": 0.4, RUST: 0.6}}}
    snapshot_path = tmp_path / "snapshot.json.gz"
    snapshot_path.write_bytes(snapshot_bytes)
    spec_path = tmp_path / "spec.json"
    spec_path.write_text(json.dumps(payload), encoding="utf-8")

    cli = CliRunner().invoke(
        cli_mod.app,
        ["decide", str(spec_path), "--snapshot-file", str(snapshot_path), "--json"],
        env={"MODELSPEC_SNAPSHOT_KEY": KEY.decode()},
    )
    assert cli.exit_code == 0, cli.output
    service = _decide_service()
    status, body = service.decide(payload, index)
    assert status == 200, body.get("error")
    assert service.serialise(body) == cli.stdout.encode("utf-8")
    assert body["results"][0]["refinement_estimates"][0]["key"] == RUST


def test_the_worker_refuses_an_unrankable_refinement_with_invalid_spec(index):
    service = _decide_service()
    status, body = service.decide(
        {"spec_version": 1, "optimize": {"weights": {"software_engineering/java": 1}}}, index)

    assert status == 400
    assert body["error"]["code"] == "invalid_spec"


def test_excluding_the_rust_benchmark_falls_back_to_the_domain(index):
    decision = _decide(index, {"weights": {RUST: 1}}, exclude_benchmarks=["code_general"])
    nested = {r.offering.model: r.refinement_estimates[0] for r in decision.results}

    assert nested["lab/c"].evidence_count == 1
    assert _order(decision).index("lab/c") < _order(decision).index("lab/a")


# ── the fit ────────────────────────────────────────────────────────────────


def _observation(mid, benchmark, value, refinements=()):
    return CapabilityObservation(
        model_id=mid, benchmark_id=benchmark, value=value, unit="percent",
        measured_by="independent_evaluator", date=AS_OF - timedelta(days=10),
        record_id=f"{mid}#{benchmark}", version="1.0",
        domains=(("software_engineering", "direct"),), refinements=tuple(refinements),
    )


def test_the_fit_pools_the_refinement_adjustment_toward_the_domain():
    rows = [_observation(mid, "code_general", score) for mid, score in GENERAL.items()]
    rows += [_observation(mid, "rust_suite", score, [(RUST, "direct")])
             for mid, score in RUST_SUITE.items()]
    specs = {name: BenchmarkSpec(0, 500) for name in ("code_general", "rust_suite")}
    fit = fit_capabilities(rows, specs, as_of=AS_OF)

    domain_b = fit.estimate("lab/b", "software_engineering")
    rust_b = fit.refinement_estimate("lab/b", RUST)
    assert rust_b.evidence_count == 0
    assert rust_b.value == pytest.approx(domain_b.value)
    assert rust_b.sd > domain_b.sd

    rust_c, rust_a = fit.refinement_estimate("lab/c", RUST), fit.refinement_estimate("lab/a", RUST)
    assert rust_c.evidence_count == 1
    assert rust_c.value > rust_a.value
    # Pooled: a single Rust score moves lab/c toward it, not all the way.
    assert fit.estimate("lab/c", "software_engineering").value < rust_c.value
    assert fit.refinement_estimate("lab/unknown", RUST) is None


def test_the_fit_without_refinement_tags_is_unchanged():
    rows = [_observation(mid, "code_general", score) for mid, score in GENERAL.items()]
    tagged = [_observation(mid, "code_general", score, [(RUST, "proxy")])
              for mid, score in GENERAL.items()]
    specs = {"code_general": BenchmarkSpec(0, 500)}

    plain = fit_capabilities(rows, specs, as_of=AS_OF).to_payload()
    with_tags = fit_capabilities(tagged, specs, as_of=AS_OF).to_payload()
    for key in ("estimates", "drivers", "items", "domain_sd"):
        assert with_tags[key] == plain[key]


def test_a_full_explanation_renders_the_refinement(index):
    from decision.explain import render_html

    decision = _decide(index, {"weights": {"software_engineering": 0.5, RUST: 0.5}},
                       explain="full", where=["model.context_window >= 1000"])

    assert any(point.refinement == "rust" for point in decision.tipping_points)
    html = render_html(decision, index)
    assert "software_engineering/rust" in html
