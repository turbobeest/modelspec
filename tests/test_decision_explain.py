"""Decisions and reports disclose the snapshot measurements they use."""

from datetime import date

import pytest

from decision.contract import parse_spec
from decision.engine import decide
from decision.registry import facet as facets
from decision.snapshot import SnapshotInputs, build_snapshot, load_snapshot
from tests.test_decision_snapshot import SOURCES, evidence, fact, model


@pytest.fixture
def index(tmp_path):
    models = [
        model(
            "lab/" + name,
            facts=[
                fact("model", "lab/" + name, "model.context_window", price),
                fact("model", "lab/" + name, "model.max_output_tokens", context),
            ],
        )
        for name, price, context in [("a", 3, 100), ("b", 1, 80), ("c", 2, 60)]
    ]
    for m in models:
        for f in m["facts"]:
            f["unit"] = "tokens"
    rows = [
        evidence(
            "lab/" + name,
            "swe_bench_pro",
            value,
            measured_by=measurer,
            effort="default",
            harness="codex-cli@1.4",
        )
        for name, value, measurer in [
            ("a", 70, "independent"),
            ("b", 90, "provider_self_report"),
            ("c", 50, "independent"),
        ]
    ]
    built = build_snapshot(
        SnapshotInputs(
            models=models,
            evidence=rows,
            sources=SOURCES,
            benchmark_domains={"swe_bench_pro": [("software_engineering", "direct")]},
        ),
        as_of=date(2026, 9, 24),
    )
    return load_snapshot(built.write(tmp_path / "snapshot.gz", key=None), key=None)


def spec(level="full", **updates):
    return parse_spec(
        dict(
            spec_version=1,
            where=["model.max_output_tokens >= 90"],
            optimize={"min": "model.context_window"},
            capabilities={"software_engineering": "required"},
            explain=level,
        )
        | updates,
        facets=None,
    )


def test_full_decision_keeps_unblended_evidence_and_fact_provenance(index):
    result = decide(spec(), index, facets=facets)
    assert result.results[0].offering.model == "lab/a"
    item = result.results[0].evidence[0].items[0]
    assert (item.value, item.version, item.unit, item.directness) == (
        70,
        "1.0",
        "percent",
        "direct",
    )
    assert item.harness == "codex-cli@1.4"
    part = result.results[0].contributions[0]
    assert part.raw_value == 3
    assert part.records == ["lab/a#model.context_window"]
    assert index.record(part.records[0])["verification"]["outcome"] == "verified"


def test_costs_and_near_misses_measure_one_relaxed_condition(index):
    decision = decide(spec(), index, facets=facets)
    (cost,) = decision.constraint_costs
    assert cost.admits == 2
    assert cost.gain == {"-model.context_window": -2}
    assert cost.units == {"-model.context_window": "tokens"}
    assert [(m.offering.model, m.distance, m.unit) for m in decision.near_misses] == [
        ("lab/b", 10, "tokens"),
        ("lab/c", 30, "tokens"),
    ]
    both = decide(
        spec(where=["model.max_output_tokens >= 90", "model.context_window >= 2"]),
        index,
        facets=facets,
    )
    assert [m.offering.model for m in both.near_misses] == ["lab/c"]


def test_full_adds_all_values_and_reasons_while_none_skips_explanation(index):
    full = decide(spec(limit=1), index, facets=facets)
    assert {fact.value for fact in full.top[0].facts} == {3, 100}
    assert len(full.eliminated.models) == 2
    assert "<svg" in full.chart
    summary = decide(spec("summary"), index, facets=facets)
    assert summary.top == [] and summary.eliminated.models == []
    none = decide(spec("none"), index, facets=facets)
    assert none.results[0].evidence == []
    assert none.results[0].contributions == []
    assert none.constraint_costs == [] and none.chart is None


def test_every_presented_number_resolves_to_snapshot_sources_and_verification(index):
    """MODEL-145's guarantee, walked over the compact 1.4 form."""
    from decision.explain import presented_values

    decision = decide(spec(), index, facets=facets)
    data = decision.model_dump(mode="json")
    origins = {origin.path: origin for origin in decision.number_origins}
    table = {source.id: source.url for source in decision.sources}
    presented = list(presented_values(data))
    assert presented and set(origins) == {path for path, _ in presented}
    for path, value in presented:
        origin = origins[path]
        assert origin.basis
        assert origin.sources == []
        assert set(origin.source_ids) <= set(table)
        for rid in origin.records:
            record = index.record(rid)
            verification = record["verification"]
            assert verification["outcome"] == "verified"
            assert verification["collector"]["agent"] != verification["verifier"]["agent"]
            assert {s["source_id"] for s in record["sources"]} <= set(origin.source_ids)
            assert all(table[s["source_id"]] == index.source_url(s["source_id"])
                       for s in record["sources"])
        if origin.basis == "snapshot measurement":
            assert origin.records
            assert any(
                value == index.record(rid).get("score", index.record(rid).get("value"))
                for rid in origin.records
            )
    # A shown fact carries its provenance itself: record and source IDs.
    for row in decision.top:
        for shown in row.facts:
            record = index.record(shown.record_id)
            assert record["verification"]["outcome"] == "verified"
            assert record["value"] == shown.value
            assert [s["source_id"] for s in record["sources"]] == shown.source_ids
            assert all(sid in table for sid in shown.source_ids)


def test_html_is_self_contained_escaped_and_labels_lab_reports(index):
    from html.parser import HTMLParser

    from decision.explain import render_html

    decision = decide(spec(where=[]), index, facets=facets)
    html = render_html(decision, index)
    assert "<svg" in html and "prefers-color-scheme: dark" in html
    assert "Lab-reported" in html and "90 percent" in html
    assert "codex-cli@1.4" in html and "2026-08-01" in html

    class Links(HTMLParser):
        def handle_starttag(self, tag, attrs):
            for key, value in attrs:
                if key in ("href", "src"):
                    assert tag == "a" and key == "href" and value in SOURCES.values()

    Links().feed(html)
    assert "<script" not in html
    decision.results[0].contributions[0].unit = "<img src=x onerror=alert(1)>"
    assert "<img" not in render_html(decision, index)


def test_none_latency_is_within_noise_of_bypassed_explanation(index, monkeypatch):
    import gc
    import timeit
    from pathlib import Path

    import decision.engine as engine
    import decision.explain as explanation

    request = spec("none")
    # Compile the actual engine with only the explanation branch removed.
    source = Path(engine.__file__).read_text()
    start = source.index('    if spec.explain != "none":')
    end = source.index("    return decision", start)
    namespace = {"__name__": "decision.engine_bypassed"}
    exec(compile(source[:start] + source[end:], engine.__file__, "exec"), namespace)

    def forbidden(*args):
        raise AssertionError("none entered explanation code")

    monkeypatch.setattr(explanation, "explain", forbidden)

    def baseline():
        return namespace["decide"](request, index, facets=facets)

    def actual():
        return decide(request, index, facets=facets)

    assert actual() == baseline()
    enabled = gc.isenabled()
    gc.disable()
    try:
        samples = [
            (timeit.timeit(baseline, number=100), timeit.timeit(actual, number=100))
            for _ in range(15)
        ]
        base = min(b for b, _ in samples)
        elapsed = min(a for _, a in samples)
    finally:
        if enabled:
            gc.enable()
    assert elapsed <= base * 1.15


def test_cli_writes_full_html_from_local_snapshot(index, tmp_path, monkeypatch):
    import sys

    from typer.testing import CliRunner

    sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1] / "cli"))
    from modelspec import decide_cmd
    from modelspec.cli import app

    monkeypatch.setattr(decide_cmd, "_facet_lookup", lambda: facets)
    spec_path = tmp_path / "spec.yaml"
    spec_path.write_text(
        "spec_version: 1\noptimize: {min: model.context_window}\n"
        "capabilities: {software_engineering: required}\n"
    )
    report = tmp_path / "out.html"
    result = CliRunner().invoke(
        app,
        [
            "decide",
            str(spec_path),
            "--explain",
            "full",
            "--snapshot-file",
            str(tmp_path / "snapshot.gz"),
            "--html",
            str(report),
            "--json",
        ],
    )
    assert result.exit_code == 0, result.output
    assert report.exists()
    assert "Lab-reported" in report.read_text()
    assert __import__("json").loads(result.stdout)["results"][0]["offering"]["model"] == "lab/b"


def test_missing_provenance_and_unverified_measurements_do_not_get_explained(index):
    from dataclasses import replace

    from decision.explain import ExplanationError

    first = index._evidence["lab/a"][0]
    index._evidence["lab/a"] = (replace(first, record_id=None),)
    with pytest.raises(ExplanationError, match="provenance"):
        decide(spec("summary"), index, facets=facets)
    assert decide(spec("none"), index, facets=facets).results
    index._evidence["lab/a"] = (replace(first, value=999),)
    with pytest.raises(ExplanationError, match="differs"):
        decide(spec("summary"), index, facets=facets)


def test_benchmark_objective_uses_optimize_tipping_points(index):
    decision = decide(
        spec(
            where=[],
            optimize={"weights": {"swe_bench_pro": 2, "-model.context_window": 1}},
        ),
        index,
        facets=facets,
    )
    assert decision.results[0].offering.model == "lab/b"
    assert decision.results[0].contributions[1].evidence[0].value == 90
    assert decision.results[0].contributions[1].evidence[0].measured_by == "provider_self_report"
    assert decision.results[0].estimates is None


def test_objective_qualifiers_reach_the_optimiser(index):
    decision = decide(
        spec(where=[], optimize={"max": "swe_bench_pro @independent @default_effort"}),
        index,
        facets=facets,
    )
    assert decision.results[0].offering.model == "lab/a"
    assert decision.results[0].contributions[0].evidence[0].measured_by == "independent"


def test_fact_units_come_from_the_real_facet_registry(tmp_path):
    from decision.registry import facet

    built = build_snapshot(
        SnapshotInputs(models=[model("lab/a")], sources=SOURCES),
        as_of=date(2026, 9, 24),
    )
    snapshot = load_snapshot(built.write(tmp_path / "units.gz", key=None), key=None)
    request = parse_spec(
        {"spec_version": 1, "optimize": {"max": "model.context_window"}, "explain": "full"},
        facets=facet,
    )
    decision = decide(request, snapshot, facets=facet)
    assert decision.results[0].contributions[0].unit == "tokens"


def test_top_twenty_does_not_depend_on_result_limit(index):
    decision = decide(spec(where=[], limit=1), index, facets=facets)
    assert len(decision.results) == 1
    assert len(decision.top) == 3
    assert [row.offering.model for row in decision.top] == ["lab/b", "lab/c", "lab/a"]


def test_empty_feasible_set_and_domain_objectives_remain_honest(index):
    empty = decide(spec(where=["model.max_output_tokens > 1000"]), index, facets=facets)
    assert empty.status == "no_feasible"
    assert empty.relax == ["model.max_output_tokens > 1000"]
    assert empty.constraint_costs[0].gain == {}
    domain = decide(spec(optimize={"max": "software_engineering"}), index, facets=facets)
    assert domain.status == "no_feasible"
    assert "MODEL-129" in domain.relax[0]


def test_tipping_point_is_the_optimiser_weight_crossing(index):
    decision = decide(
        spec(
            where=[],
            optimize={"weights": {"swe_bench_pro": 2, "model.max_output_tokens": 1}},
        ),
        index,
        facets=facets,
    )
    assert decision.results[0].offering.model == "lab/b"
    assert [(p.dimension, p.threshold, p.new_top) for p in decision.tipping_points] == [
        ("model.max_output_tokens", 2, "lab/a"),
        ("swe_bench_pro", 1, "lab/a"),
    ]


def test_source_links_refuse_non_http_registered_urls(index):
    from decision.explain import ExplanationError

    index._sources["src-lab-docs"] = "javascript:alert(1)"
    with pytest.raises(ExplanationError, match="http"):
        decide(spec(), index, facets=facets)


def test_numeric_list_values_are_measurements_not_counts(tmp_path):
    from decision.contract import Decision, ModelElimination, OfferingRef
    from decision.explain import number_origins

    raw = fact("model", "lab/a", "sizes", [4, 8])
    built = build_snapshot(SnapshotInputs(models=[model("lab/a", facts=[raw])], sources=SOURCES))
    index = load_snapshot(built.write(tmp_path / "list.gz", key=None), key=None)
    decision = Decision(
        decision_id="dec_12345678",
        snapshot=index.snapshot_id,
        spec_hash="sha256:" + "0" * 64,
        status="answered",
        explain="full",
    )
    decision.eliminated.models.append(ModelElimination(
        model="lab/a", offering=OfferingRef(model="lab/a"), condition="sizes in [10, 20]",
        values=[4, 8], records=["lab/a#sizes"]))
    origins = list(number_origins(decision, index))
    assert [o.basis for o in origins] == ["snapshot measurement", "snapshot measurement"]
    assert all(o.records == ["lab/a#sizes"] for o in origins)
    assert all(o.source_ids == ["src-lab-docs"] for o in origins)


def test_full_explains_multiple_measurements_failing_an_evidence_window(tmp_path):
    rows = [
        evidence("lab/a", "swe_bench_pro", value, measured_by="independent")
        for value in (40, 50)
    ]
    built = build_snapshot(
        SnapshotInputs(
            models=[
                model(
                    "lab/a",
                    facts=[fact("model", "lab/a", "model.context_window", 1)],
                )
            ],
            evidence=rows,
            sources=SOURCES,
            benchmark_domains={"swe_bench_pro": [("software_engineering", "direct")]},
        )
    )
    index = load_snapshot(built.write(tmp_path / "multi.gz", key=None), key=None)
    decision = decide(
        spec(where=[{"facet": "swe_bench_pro", "between": [60, 90]}]),
        index,
        facets=facets,
    )
    (reason,) = decision.eliminated.models
    assert reason.value is None
    assert reason.values == [40, 50]
    assert len(reason.records) == 2
