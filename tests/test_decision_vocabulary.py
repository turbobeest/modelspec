"""The decision vocabulary, published as data (MODEL-153).

`/api/decision/vocabulary.json` tells the decide page which facets and which
benchmarks exist, so the page never ships a hard-coded list. Facets come from
the registry; benchmarks only when the snapshot holds verified evidence for
them. Every condition and objective the page can build from it must be a valid
contract spec.
"""

from __future__ import annotations

import json
from dataclasses import replace
from datetime import date

import pytest

from decision.contract import CONTRACT_VERSION, DEFAULT_TASK_TOKENS, parse_spec
from decision.engine import decide
from decision.registry import default as registry
from decision.registry import facet as registry_facet
from decision.snapshot import SnapshotInputs, build_snapshot, load_snapshot_bytes
from decision.vocabulary import VOCABULARY_VERSION, build_vocabulary
from tests.snapshot_records import SOURCES, evidence, fact, model, offering

AS_OF = date(2026, 9, 24)
DOMAINS = {
    "swe_bench_verified": [("software_engineering", "direct")],
    "terminal_bench_v4_0": [("agentic_tool_use", "direct"), ("software_engineering", "proxy")],
    "swe_bench_pro": [("software_engineering", "direct")],
}
PAGES = {
    "swe_bench_verified": {"id": "swe_bench_verified", "name": "SWE-bench Verified",
                           "metric": {"direction": "higher_is_better", "unit": "%"}},
    "terminal_bench_v4_0": {"id": "terminal_bench_v4_0", "name": "Terminal-Bench 4.0"},
}


def generator(mid, openness="closed_weights"):
    return model(mid, facts=[
        fact("model", mid, "model.class", "text-generator"),
        fact("model", mid, "model.lifecycle", "active"),
        fact("model", mid, "model.context_window", 200000),
        fact("model", mid, "model.weights_openness", openness),
        fact("model", mid, "origin.lab_jurisdiction", ["US"]),
    ])


def sold(mid, provider, price_in, price_out=None):
    oid = f"{provider}/{mid}/global/standard"
    facts = [fact("offering", oid, "offering.price.input", price_in, source="src-pricing")]
    if price_out is not None:
        facts.append(fact("offering", oid, "offering.price.output", price_out, source="src-pricing"))
    return offering(mid, provider, facts=facts)


@pytest.fixture(scope="module")
def snapshot():
    inputs = SnapshotInputs(
        models=[generator("lab/a"), generator("lab/b", "open_weights"), generator("lab/c"),
                model("lab/old", lifecycle="retired")],
        offerings=[sold("lab/a", "p1", 1.0, 5.0), sold("lab/a", "p2", 1.2, 6.0),
                   sold("lab/b", "p1", 0.2, 0.8), sold("lab/c", "p1", 3.0)],
        evidence=[
            evidence("lab/a", "swe_bench_verified", 70.0),
            evidence("lab/b", "swe_bench_verified", 55.0),
            evidence("lab/a", "terminal_bench_v4_0", 40.0),
            evidence("lab/c", "swe_bench_pro", 30.0, outcome="mismatch"),
        ],
        sources=SOURCES,
        benchmark_domains=DOMAINS,
    )
    built = build_snapshot(inputs, gate=False, as_of=AS_OF)
    return load_snapshot_bytes(built.to_bytes(key=None), key=None, include_archive=True)


CARDS = {
    "lab/a": {"display_name": "Alpha 4.7", "provider": "lab", "provider_display": "Lab Inc."},
    "lab/old": {"display_name": "Old One", "provider": "lab", "provider_display": "Lab Inc."},
}


@pytest.fixture(scope="module")
def vocabulary(snapshot):
    return build_vocabulary(snapshot, pages=PAGES, cards=CARDS)


def by_id(rows):
    return {row["id"]: row for row in rows}


def test_it_names_the_snapshot_and_the_contract(snapshot, vocabulary):
    assert vocabulary["vocabulary_version"] == VOCABULARY_VERSION
    assert vocabulary["snapshot"] == snapshot.snapshot_id
    assert vocabulary["contract_version"] == CONTRACT_VERSION
    assert vocabulary["default_task_tokens"] == {
        "input": DEFAULT_TASK_TOKENS.input, "output": DEFAULT_TASK_TOKENS.output}
    json.dumps(vocabulary, allow_nan=False)


def test_every_lineup_and_archive_model_is_named_from_its_card(vocabulary):
    assert vocabulary["models"] == {
        "lab/a": {"display_name": "Alpha 4.7", "lab": "lab", "lab_name": "Lab Inc."},
        "lab/b": {"display_name": None, "lab": "lab", "lab_name": None},
        "lab/c": {"display_name": None, "lab": "lab", "lab_name": None},
        "lab/old": {"display_name": "Old One", "lab": "lab", "lab_name": "Lab Inc."},
    }


def test_a_model_without_a_card_is_never_named_from_its_slug(snapshot):
    rows = build_vocabulary(snapshot, pages=PAGES)["models"]
    assert all(row["display_name"] is None and row["lab_name"] is None for row in rows.values())


def test_every_registered_facet_is_listed_with_label_unit_subject_type_and_operators(vocabulary):
    facets = by_id(vocabulary["facets"])
    families = {f.id for f in registry().facets() if f.parameter is not None}
    assert set(facets) == {f.id for f in registry().facets()} - families
    for row in facets.values():
        assert row["label"] and row["subject"] in ("model", "offering")
        assert row["value_type"] in ("number", "enum", "boolean", "date", "set")
        assert "known" in row["operators"]
    price = facets["offering.price.input"]
    assert (price["label"], price["unit"], price["value_type"]) == (
        "Input price", "usd_per_1m_tokens", "number")
    assert {"<=", ">=", "between"} <= set(price["operators"])
    assert price["objective"] is True
    assert set(facets["origin.lab_jurisdiction"]["operators"]) == {"in", "not in", "known"}
    assert "<" not in facets["model.weights_openness"]["operators"]
    assert facets["model.weights_openness"]["objective"] is False


def test_coverage_counts_what_the_snapshot_actually_knows(vocabulary):
    facets = by_id(vocabulary["facets"])
    assert (facets["offering.price.input"]["known"], facets["offering.price.input"]["of"]) == (4, 4)
    assert facets["offering.speed.throughput"]["known"] == 0
    assert facets["model.context_window"]["known"] == 3
    assert facets["model.context_window"]["range"] == {"min": 200000, "max": 200000}
    assert facets["model.weights_openness"]["values"] == [
        {"value": "closed_weights", "count": 2, "label": "Closed weights"},
        {"value": "open_weights", "count": 1, "label": "Open weights"}]
    assert facets["origin.lab_jurisdiction"]["values"] == [{"value": "US", "count": 3}]
    assert facets["model.release_date"]["range"] is None


def test_lineup_coverage_is_counted_per_class_and_per_domain(vocabulary):
    """What an empty answer is measured against (MODEL-153): counted, never written."""
    coverage = vocabulary["coverage"]
    assert coverage["as_of"] == AS_OF.isoformat()
    # lab/old is retired; lab/c's only evidence failed verification.
    assert (coverage["models"], coverage["verified"]) == (3, 2)
    classes = by_id(coverage["classes"])
    assert set(classes) == set(registry().allowed_values(registry().facet("model.class")))
    assert classes["text-generator"] == {
        "id": "text-generator", "models": 3, "verified": 2,
        "domains": [{"id": "software_engineering", "verified": 2},
                    {"id": "agentic_tool_use", "verified": 1}]}
    assert classes["transcriber"] == {
        "id": "transcriber", "models": 0, "verified": 0, "domains": []}
    domains = by_id(coverage["domains"])
    assert {d.id for d in registry().domains()} == set(domains)
    assert domains["software_engineering"] == {
        "id": "software_engineering", "name": "Software engineering",
        "verified": 2, "direct": 2}
    # Terminal-Bench is direct for agentic tool use, a proxy for engineering.
    assert domains["agentic_tool_use"] == {
        "id": "agentic_tool_use", "name": "Agentic and tool use", "verified": 1, "direct": 1}
    assert domains["retrieval"] == {
        "id": "retrieval", "name": registry().domain("retrieval").name,
        "verified": 0, "direct": 0}


def test_proxy_evidence_counts_toward_a_domain_but_not_as_direct():
    built = build_snapshot(SnapshotInputs(
        models=[generator("lab/x")], offerings=[],
        evidence=[evidence("lab/x", "terminal_bench_v4_0", 40.0)],
        sources=SOURCES, benchmark_domains=DOMAINS,
    ), gate=False, as_of=AS_OF)
    coverage = build_vocabulary(load_snapshot_bytes(built.to_bytes(key=None), key=None))["coverage"]
    engineering = by_id(coverage["domains"])["software_engineering"]
    assert (engineering["verified"], engineering["direct"]) == (1, 0)


def test_providers_are_named_as_the_registry_names_them(vocabulary):
    providers = vocabulary["providers"]
    assert providers == {p.id: p.name for p in registry().providers()}
    assert providers["anthropic"] == "Anthropic API"
    assert providers["zai"] == "Z.ai API"


def test_cost_per_task_is_listed_as_computed_from_both_prices(vocabulary):
    cost = by_id(vocabulary["facets"])["offering.cost_per_task"]
    assert cost["computed_by"] == "MODEL-153"
    assert cost["unit"] == "usd_per_task"
    # lab/c's offering has no output price, so its cost per task is unknown.
    assert (cost["known"], cost["of"]) == (3, 4)
    # At the default 40k in / 4k out: lab/b 0.0112, lab/a p2 0.072.
    assert cost["range"] == {"min": pytest.approx(0.0112), "max": pytest.approx(0.072)}


def test_only_benchmarks_with_verified_evidence_are_listed(vocabulary):
    benchmarks = by_id(vocabulary["benchmarks"])
    assert set(benchmarks) == {"swe_bench_verified", "terminal_bench_v4_0"}
    swe = benchmarks["swe_bench_verified"]
    assert swe == {
        "id": "swe_bench_verified", "name": "SWE-bench Verified", "unit": "percent",
        "higher_is_better": True, "models": 2, "independent_models": 2,
        "range": {"min": 55.0, "max": 70.0},
        "domains": [{"id": "software_engineering", "directness": "direct"}],
    }
    assert benchmarks["terminal_bench_v4_0"]["name"] == "Terminal-Bench 4.0"
    assert benchmarks["terminal_bench_v4_0"]["domains"] == [
        {"id": "agentic_tool_use", "directness": "direct"},
        {"id": "software_engineering", "directness": "proxy"}]


def test_domains_list_their_benchmarks_direct_first_then_by_coverage(vocabulary):
    domains = by_id(vocabulary["domains"])
    assert domains["software_engineering"]["name"] == "Software engineering"
    assert domains["software_engineering"]["benchmarks"] == ["swe_bench_verified", "terminal_bench_v4_0"]
    assert "legal" not in domains


def conditions_for(row):
    """One condition per operator the vocabulary claims, with a value it lists."""
    if "operators" not in row:  # a benchmark: a number of evidence
        return [f"{row['id']} >= 1", f"{row['id']} >= 1 @independent", f"{row['id']} in [1, 2]"]
    kind, values = row["value_type"], [v["value"] for v in row.get("values", [])]
    sample = {"number": (row.get("range") or {}).get("min", 1), "date": "2026-01-01",
              "boolean": "true"}.get(kind, values[0] if values else "x")
    if isinstance(sample, bool):
        sample = "true" if sample else "false"
    out = []
    for op in row["operators"]:
        if op == "known":
            out.append(f"known({row['id']})")
        elif op == "between":
            out.append(f"{row['id']} in [{sample}, {sample}]")
        elif op in ("in", "not in"):
            out.append(f"{row['id']} {op} {{{sample}}}")
        else:
            out.append(f"{row['id']} {op} {sample}")
    return out


def lookup(snapshot):
    benchmarks = frozenset(snapshot.benchmark_ids())

    def facet(facet_id):
        if facet_id in benchmarks:
            return replace(registry_facet("evidence.benchmark"), id=facet_id)
        return registry_facet(facet_id)

    return facet


def test_every_condition_and_objective_the_page_can_build_is_a_valid_spec(snapshot, vocabulary):
    facets = lookup(snapshot)
    built = 0
    for row in [*vocabulary["facets"], *vocabulary["benchmarks"]]:
        for condition in conditions_for(row):
            parse_spec({"spec_version": 1, "where": [condition], "optimize": {"max": "swe_bench_verified"},
                        "task_tokens": vocabulary["default_task_tokens"]}, facets=facets)
            built += 1
        if row.get("objective", True):
            for signed in (row["id"], "-" + row["id"]):
                spec = parse_spec({"spec_version": 1, "optimize": {"weights": {signed: 1}}},
                                  facets=facets)
                decide(spec, snapshot, facets=facets)
                built += 1
    assert built > 100


def test_the_site_build_writes_the_vocabulary_beside_the_snapshot(tmp_path, monkeypatch):
    from decision import snapshot as snap
    from pipeline import build as site_build
    from tests.test_decision_snapshot import COMPLETENESS_REGISTRY, KEY, _mini_repo

    root = _mini_repo(tmp_path)
    monkeypatch.setattr(snap, "default_registry", lambda: COMPLETENESS_REGISTRY)
    monkeypatch.setenv(snap.KEY_ENV, KEY.decode())
    target = tmp_path / "site" / "api" / "decision" / "snapshot.json.gz"
    stale = target.parent / "vocabulary.json"
    stale.parent.mkdir(parents=True)
    stale.write_text("{}")

    published = site_build.write_decision_snapshot_if_ready(
        root, target, premier=root / "premier" / "slice-1.yaml", as_of=AS_OF)

    assert published is True
    written = json.loads(stale.read_text())
    assert written["snapshot"] == snap.load_snapshot(target, key=KEY).snapshot_id
    assert [b["id"] for b in written["benchmarks"]] == ["swe_bench_pro"]
    assert written["models"] == {
        "lab/alpha": {"display_name": None, "lab": "lab", "lab_name": None}}


def test_no_snapshot_means_no_vocabulary(tmp_path, monkeypatch):
    from decision import snapshot as snap
    from pipeline import build as site_build

    monkeypatch.delenv(snap.KEY_ENV, raising=False)
    target = tmp_path / "api" / "decision" / "snapshot.json.gz"
    target.parent.mkdir(parents=True)
    (target.parent / "vocabulary.json").write_text("{}")
    site_build.write_decision_snapshot_if_ready(
        tmp_path, target, premier=tmp_path / "premier.yaml", as_of=AS_OF)
    assert not (target.parent / "vocabulary.json").exists()


def test_enum_values_carry_the_registry_label(snapshot):
    """The page shows `label`, never the value token (MODEL-153)."""
    vocabulary = build_vocabulary(snapshot)
    rows = {row["id"]: row for row in vocabulary["facets"]}
    openness = {v["value"]: v.get("label") for v in rows["model.weights_openness"]["values"]}
    assert openness == {"closed_weights": "Closed weights", "open_weights": "Open weights"}
    for row in vocabulary["facets"]:
        for item in row.get("values") or []:
            token = isinstance(item["value"], str) and any(c in item["value"] for c in "_-")
            if token and row["id"] != "offering.provider":  # providers are named separately
                assert item.get("label"), (row["id"], item["value"])


def test_the_registry_default_benchmark_leads_only_with_verified_evidence(vocabulary):
    """software_engineering defaults to swe_bench_pro (registry/domains.yaml,
    Jamie 2026-09-25). Here its only row is a mismatch, so it has no verified
    evidence: the default is not applied and the most-covered direct benchmark
    leads."""
    domain = by_id(vocabulary["domains"])["software_engineering"]
    assert domain["default_benchmark"] is None
    assert domain["benchmarks"][0] == "swe_bench_verified"


def test_a_verified_default_benchmark_leads_its_domain():
    inputs = SnapshotInputs(
        models=[generator("lab/a"), generator("lab/b"), generator("lab/c")],
        offerings=[sold("lab/a", "p1", 1.0, 5.0)],
        evidence=[
            evidence("lab/a", "swe_bench_verified", 70.0),
            evidence("lab/b", "swe_bench_verified", 55.0),
            evidence("lab/c", "swe_bench_pro", 30.0),
        ],
        sources=SOURCES,
        benchmark_domains=DOMAINS,
    )
    built = build_snapshot(inputs, gate=False, as_of=AS_OF)
    snap = load_snapshot_bytes(built.to_bytes(key=None), key=None, include_archive=True)
    domain = by_id(build_vocabulary(snap, pages=PAGES, cards=CARDS)["domains"])["software_engineering"]
    assert domain["default_benchmark"] == "swe_bench_pro"
    assert domain["benchmarks"][0] == "swe_bench_pro"
