"""A `full` explanation stays small as the snapshot grows (contract 1.4).

Since the snapshot carried hundreds of verified evidence rows, `explain: full`
listed every number in the decision with its source URLs repeated, and every
value of every top candidate. The Worker ran out of resources. The compact
form lists each source once, gives origins only to the numbers a decision
presents, and shows a top candidate's relevant facets only. Every presented
number still traces to a verified record and a registered source (MODEL-145).
"""

from __future__ import annotations

import json
from datetime import date

import pytest

from decision.contract import Decision, parse_spec
from decision.engine import decide
from decision.explain import DISPLAY_FACETS, presented_values
from decision.registry import facet as facets
from decision.snapshot import SnapshotInputs, build_snapshot, load_snapshot_bytes
from tests.snapshot_records import SOURCES, evidence, fact, model, offering

BENCH = "swe_bench_pro"
OTHER = "mmlu_pro"
MODELS = ("lab/a", "lab/b", "lab/c")


def _model(mid, context):
    return model(mid, facts=[
        fact("model", mid, "model.class", "text-generator"),
        fact("model", mid, "model.lifecycle", "active"),
        fact("model", mid, "model.context_window", context),
        fact("model", mid, "model.max_output_tokens", context // 2),
        fact("model", mid, "model.weights_openness", "closed_weights"),
        fact("model", mid, "licence.user_cap", "unbounded"),
    ])


def _offering(mid, price_in, price_out):
    oid = f"p1/{mid}/global/standard"
    return offering(mid, "p1", facts=[
        fact("offering", oid, "offering.price.input", price_in, source="src-pricing"),
        fact("offering", oid, "offering.price.output", price_out, source="src-pricing"),
        fact("offering", oid, "offering.price.batch_input", "not_offered", source="src-pricing"),
    ])


def snapshot(extra_benchmarks=0):
    """Three models sold by one provider; ``extra_benchmarks`` adds unrelated evidence."""
    rows = [evidence(mid, BENCH, score) for mid, score in zip(MODELS, (70.0, 60.0, 50.0))]
    rows += [evidence(mid, OTHER, score) for mid, score in zip(MODELS, (80.0, 81.0, 82.0))]
    domains = {BENCH: [("software_engineering", "direct")], OTHER: [("reasoning", "direct")]}
    sources = dict(SOURCES)
    for i in range(extra_benchmarks):
        bench, source = f"noise_{i}", f"src-noise-{i}"
        sources[source] = f"https://noise.example.org/{i}"
        domains[bench] = [(f"noise_domain_{i % 5}", "direct")]
        rows += [evidence(mid, bench, 10.0 + i, source=source) for mid in MODELS]
    built = build_snapshot(
        SnapshotInputs(
            models=[_model(mid, context) for mid, context in
                    zip(MODELS, (400_000, 300_000, 100_000))],
            offerings=[_offering("lab/a", 5.0, 25.0), _offering("lab/b", 1.0, 5.0),
                       _offering("lab/c", 0.5, 2.0)],
            evidence=rows,
            sources=sources,
            benchmark_domains=domains,
        ),
        gate=False,
        as_of=date(2026, 9, 25),
    )
    return load_snapshot_bytes(built.to_bytes(key=None), key=None, include_archive=True)


def spec(**updates):
    return parse_spec({
        "spec_version": 1,
        "capabilities": {"software_engineering": "required"},
        "task_tokens": {"input": 40000, "output": 4000},
        "where": ["model.class = text-generator", "model.context_window >= 200000"],
        "optimize": {"weights": {BENCH: 0.78, "-offering.cost_per_task": 0.22}},
        "explain": "full",
        **updates,
    }, facets=facets)


@pytest.fixture(scope="module")
def index():
    return snapshot()


def test_sources_are_listed_once_and_origins_name_them_by_id(index):
    decision = decide(spec(), index, facets=facets)
    ids = [source.id for source in decision.sources]
    assert len(ids) == len(set(ids))
    assert {source.url for source in decision.sources} <= set(SOURCES.values())
    table = {source.id: source for source in decision.sources}
    cited = {sid for origin in decision.number_origins for sid in origin.source_ids}
    cited |= {sid for row in decision.top for f in row.facts for sid in f.source_ids}
    assert cited == set(table)
    assert all(origin.sources == [] for origin in decision.number_origins)
    assert all(source.date == date(2026, 9, 20) for source in decision.sources)
    assert all(source.title is None for source in decision.sources)
    assert '"https://' not in json.dumps(
        [o.model_dump(mode="json") for o in decision.number_origins])


def test_origins_cover_the_presented_numbers_and_nothing_else(index):
    decision = decide(spec(), index, facets=facets)
    presented = dict(presented_values(decision.model_dump(mode="json")))
    origins = {origin.path: origin for origin in decision.number_origins}
    assert set(origins) == set(presented)
    sections = ("results", "top", "near_misses", "constraint_costs", "tipping_points",
                "eliminated")
    assert all(path.split("/")[1] in sections for path in origins)
    assert any("/evidence/" in path for path in origins if path.startswith("/top/"))
    for skipped in ("/eliminated/funnel", "/out_of_lineup"):
        assert not any(path.startswith(skipped) for path in origins)
    for untraced in ("/rank", "/weight", "/soft_penalty", "/admits"):
        assert not any(path.endswith(untraced) for path in origins)
    # A top candidate's facts and contributions carry their own records.
    assert not any("/facts/" in path or "/contributions/" in path
                   for path in origins if path.startswith("/top/"))


def test_a_shown_fact_names_its_verified_record_and_sources(index):
    decision = decide(spec(), index, facets=facets)
    table = {source.id: source.url for source in decision.sources}
    for row in decision.top:
        for shown in row.facts:
            records = shown.records or [shown.record_id]
            assert records and shown.source_ids
            for rid in records:
                record = index.record(rid)
                assert record["verification"]["outcome"] == "verified"
                assert {s["source_id"] for s in record["sources"]} <= set(shown.source_ids)
            assert all(table[sid] == index.source_url(sid) for sid in shown.source_ids)
            if shown.record_id:
                assert index.record(shown.record_id)["value"] == shown.value


def test_top_shows_the_facets_the_spec_names_and_the_display_set(index):
    decision = decide(spec(), index, facets=facets)
    shown = {f.facet for row in decision.top for f in row.facts}
    assert {"model.class", "model.context_window", "model.lifecycle", "model.weights_openness",
            "offering.price.input", "offering.price.output",
            "offering.cost_per_task"} <= shown
    assert shown <= set(DISPLAY_FACETS)
    assert "licence.user_cap" not in shown
    assert "offering.price.batch_input" not in shown
    assert "model.max_output_tokens" not in shown
    named = decide(spec(where=["model.max_output_tokens >= 1000"]), index, facets=facets)
    assert "model.max_output_tokens" in {f.facet for row in named.top for f in row.facts}


def test_top_evidence_is_the_benchmarks_the_spec_names(index):
    decision = decide(spec(), index, facets=facets)
    benchmarks = {item.benchmark for row in decision.top for group in row.evidence
                  for item in group.items}
    assert benchmarks == {BENCH}
    floor = decide(spec(where=["model.class = text-generator", f"{OTHER} >= 1"]),
                   index, facets=facets)
    assert {item.benchmark for row in floor.top for group in row.evidence
            for item in group.items} == {BENCH, OTHER}


def test_an_offering_lists_its_models_evidence_once(index):
    decision = decide(spec(), index, facets=facets)
    for result in decision.results:
        ids = [item.record_id for group in result.evidence for item in group.items]
        assert ids and len(ids) == len(set(ids))
        for part in result.contributions:
            ids = [item.record_id for item in part.evidence]
            assert len(ids) == len(set(ids))


def test_unrelated_snapshot_content_does_not_grow_a_full_decision():
    small = decide(spec(), snapshot(), facets=facets)
    large = decide(spec(), snapshot(extra_benchmarks=40), facets=facets)
    assert len(large.number_origins) == len(small.number_origins)
    assert len(large.sources) == len(small.sources)
    assert len(large.model_dump_json()) == len(small.model_dump_json())


def test_the_compact_decision_round_trips_through_the_contract(index):
    decision = decide(spec(), index, facets=facets)
    again = Decision.model_validate(json.loads(decision.model_dump_json()))
    assert again == decision
    assert decision.contract_version == "1.5"


def test_summary_carries_no_sources_table(index):
    summary = decide(spec(explain="summary"), index, facets=facets)
    assert summary.sources == [] and summary.number_origins == [] and summary.top == []


def test_top_leaves_a_ranked_candidates_contributions_to_results(index):
    from decision.explain import render_html, top_contributions

    decision = decide(spec(limit=1), index, facets=facets)
    assert len(decision.results) == 1 and len(decision.top) == 2
    ranked, beyond = decision.top
    assert ranked.offering == decision.results[0].offering
    assert ranked.contributions == [] and decision.results[0].contributions
    assert beyond.contributions
    assert [parts for _, parts in top_contributions(decision)] == [
        decision.results[0].contributions, beyond.contributions]
    # The chart and the report still show every top candidate's contributions.
    assert decision.chart.count("<rect") == 2 * len(decision.top)
    html = render_html(decision, index)
    assert html.count("normalised value") == 2 * len(decision.results) + 2 * len(decision.top)
