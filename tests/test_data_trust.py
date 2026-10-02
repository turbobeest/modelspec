"""MODEL-267 uses synthetic data and HTTP responses, never the private checkout."""

from __future__ import annotations

import copy
import gzip
import json
from datetime import date

import httpx
import pytest
import yaml

from decision.registry import load as load_registry
from decision.sources import FetchResult
from scripts.data_trust import invariants, sample
from scripts.data_trust.catalogue import Catalogue, _records, calibrate, load
from scripts.data_trust.report import append_defects, summary, write
from tests.snapshot_records import fact

TODAY = date(2026, 9, 20)
MID = "test/model"


@pytest.fixture
def registry():
    return load_registry()


@pytest.fixture
def catalogue():
    c = Catalogue(
        models={MID: {"model_id": MID, "display_name": "Test Model", "provider": "test"}},
        sources={
            "src-lab-docs": {
                "id": "src-lab-docs",
                "url": "https://example.test/docs",
                "normaliser": "text-default",
                "cited_regions": [{"id": "r1", "locator": {"kind": "page"}}],
            }
        },
    )
    _records(
        c,
        [
            fact("model", MID, "model.weights_openness", "open_weights"),
            fact("model", MID, "model.context_window", 128000),
        ],
        MID,
        "fact",
        c.models[MID],
    )
    return c


def rules(c, registry):
    return {f["rule"] for f in invariants.run(c, registry, TODAY)["findings"]}


def test_clean_sourced_open_model(catalogue, registry):
    assert invariants.run(catalogue, registry, TODAY)["findings"] == []


@pytest.mark.parametrize(
    "change,expected",
    [
        ({"sources": []}, "source_required"),
        ({"read_date": None}, "read_date_required"),
        ({"read_date": "2026-09-21"}, "read_date_future"),
        ({"value": -1}, "nonnegative"),
        ({"value": 1e12}, "plausible_magnitude"),
        ({"value": float("inf")}, "finite_number"),
        ({"field": "model.missing_facet", "facet": "model.missing_facet"}, "facet_resolves"),
        ({"unit": "usd_per_1m_tokens"}, "unit_matches_facet"),
        ({"state": "INVALID"}, "fact_schema"),
        ({"subject_id": "test/missing"}, "subject_resolves"),
    ],
)
def test_fact_invariants(catalogue, registry, change, expected):
    catalogue.facts[1].update(change)
    assert expected in rules(catalogue, registry)


def test_excluded_and_unresolved_sources(catalogue, registry):
    catalogue.sources["src-lab-docs"]["url"] = "https://docs.zapier.com/models"
    assert "excluded_source" in rules(catalogue, registry)
    catalogue.sources.clear()
    assert {"source_id_resolves", "source_required"} <= rules(catalogue, registry)


@pytest.mark.parametrize(
    "value,outcome,family",
    [
        ("closed_weights", "verified", "family-b"),
        ("open_weights", "mismatch", "family-b"),
        ("open_weights", "verified", "family-a"),
    ],
)
def test_no_route_requires_verified_independent_open_weights(
    catalogue, registry, value, outcome, family
):
    f = catalogue.facts[0]
    f["value"] = value
    f["verification"]["outcome"] = outcome
    f["verification"]["verifier"]["model_family"] = family
    assert "offering_or_verified_open_weights" in rules(catalogue, registry)


def test_unknown_is_not_a_claim(catalogue, registry):
    f = catalogue.facts[1]
    f.update(state="unknown", value=None, sources=[], read_date=None, verification={})
    assert invariants.run(catalogue, registry, TODAY)["findings"] == []


def test_discount_and_freshness(catalogue, registry):
    oid = "test-api/test/model/global/standard"
    catalogue.offerings[oid] = {"provider": "test-api", "model": MID}
    raw = [
        fact("offering", oid, "offering.price.input", 2),
        fact("offering", oid, "offering.price.cached_input", 3),
        fact("offering", oid, "offering.price.batch_input", 4),
        fact("offering", oid, "offering.price.output", 1),
        fact("offering", oid, "offering.price.batch_output", 2),
    ]
    _records(catalogue, raw, oid, "fact", catalogue.offerings[oid])
    for f in catalogue.facts[2:]:
        f["read_date"] = "2026-09-12"
    findings = invariants.run(catalogue, registry, TODAY)["findings"]
    assert sum(f["rule"] == "discount_le_standard" for f in findings) == 3
    assert sum(f["rule"] == "field_slo" and f["severity"] == "warning" for f in findings) == 5


def test_contradictions_and_duplicates(catalogue, registry):
    other = copy.deepcopy(catalogue.facts[1])
    other.update(id="other", value=64000)
    catalogue.sources["other-source"] = {"url": "https://example.test/other"}
    other["sources"][0]["source_id"] = "other-source"
    catalogue.facts.append(other)
    assert "cross_source_contradiction" in rules(catalogue, registry)
    other["id"] = catalogue.facts[1]["id"]
    assert "duplicate_id" in rules(catalogue, registry)


def test_board_range_date_and_id(catalogue, registry):
    catalogue.boards["test_board"] = {"metric": {"max_score": 10}}
    catalogue.facts.append(
        {
            **catalogue.facts[1],
            "id": "evidence-1",
            "kind": "evidence",
            "field": "test_board",
            "value": 11,
            "evidence_date": "",
        }
    )
    assert "benchmark_range" in rules(catalogue, registry)
    assert "benchmark_date_required" not in rules(catalogue, registry)
    catalogue.facts[-1]["evidence_date"] = "not-a-date"
    assert "benchmark_date_valid" in rules(catalogue, registry)
    catalogue.facts[-1]["field"] = "missing_board"
    assert "benchmark_resolves" in rules(catalogue, registry)


def test_snapshot_reference_and_enum(catalogue, registry):
    result = invariants.run(
        catalogue,
        registry,
        TODAY,
        {
            "lineup": {"candidates": [{"kind": "model", "id": "test/missing"}]},
            "facet_subjects": {"model.missing": "model"},
        },
    )
    assert {"snapshot_id_resolves", "facet_resolves"} <= {f["rule"] for f in result["findings"]}
    catalogue.facts[0]["value"] = "invalid_openness"
    assert "fact_schema" in rules(catalogue, registry)


def test_load_legacy_and_invalid_rows(tmp_path):
    (tmp_path / "models").mkdir()
    (tmp_path / "models/README.md").write_text("Editorial prose")
    (tmp_path / "models/card.md").write_text(
        "---\nmodel_id: test/model\ncost:\n  input: -2\nfacts:\n  - bad-row\n---\n"
    )
    (tmp_path / "models/broken.md").write_text("---\nbad: [\n---\n")
    c = load(tmp_path)
    assert c.models[MID]["cost"]["input"] == -2
    assert any(f["field"] == "cost.input" for f in c.facts)
    assert {f.rule for f in c.findings} == {"parse", "missing_id"}
    assert all(f.id != "models/README.md" for f in c.findings)


def test_stale_verification_cannot_date_changed_value(tmp_path):
    (tmp_path / "models").mkdir()
    raw = fact("model", MID, "model.context_window", 128000)
    raw["value"] = 64000
    (tmp_path / "models/card.md").write_text(
        "---\n" + yaml.safe_dump({"model_id": MID, "facts": [raw]}) + "---\n"
    )
    row = next(f for f in load(tmp_path).facts if f["kind"] == "fact")
    assert row["read_date"] is None
    assert row["verification"] == {}


def test_strata_seed_and_without_replacement(catalogue):
    rows = []
    for provider in ("one", "two", "three"):
        for i in range(20):
            rows.append(
                {
                    **catalogue.facts[i % 2],
                    "id": f"{provider}/{i}",
                    "provider": provider,
                    "field": "offering.price.input" if i % 2 else "model.context_window",
                    "read_date": "2026-08-01" if i % 3 else "2026-09-20",
                }
            )
    a = sample.select(rows, 24, "week-1", TODAY)
    assert a == sample.select(list(reversed(rows)), 24, "week-1", TODAY)
    assert a != sample.select(rows, 24, "week-2", TODAY)
    assert len({r["id"] for r in a}) == 24
    assert {r["provider"] for r in a} == {"one", "two", "three"}
    assert {sample.stratum(r, TODAY)[2] for r in a} == {"0-7d", "31+d"}
    assert len(sample.select(rows, 1000, "week", TODAY)) == 60


def test_wilson():
    assert sample.wilson(0, 0) == {"estimate": None, "low": None, "high": None, "readable": 0}
    assert sample.wilson(0, 60)["high"] == pytest.approx(0.06017185)
    assert sample.wilson(3, 60)["estimate"] == 0.05


@pytest.mark.parametrize(
    "body,expected",
    [
        (b"Model: Test Model\nmodel.context window: 128000 tokens\n", "matched"),
        (b"Model: Test Model\nmodel.context window: 64000 tokens\n", "mismatched"),
        (b"JavaScript required", "unreadable"),
        (b"Model: Sibling Model\nmodel.context window: 128000 tokens\n", "mismatched"),
    ],
)
def test_plain_http_readers(catalogue, registry, body, expected):
    class HTTP:
        def fetch(self, url):
            assert url == "https://example.test/docs"
            return FetchResult("ok", status=200, body=body)

    catalogue.facts = catalogue.facts[1:]
    report = sample.run(catalogue, registry, n=60, seed="week", as_of=TODAY, fetcher=HTTP())
    assert report["counts"][expected] == 1
    assert report["error_rate"]["readable"] == (0 if expected == "unreadable" else 1)


def test_primary_source_fetch_once(catalogue, registry):
    class HTTP:
        calls = 0

        def fetch(self, url):
            self.calls += 1
            return FetchResult("unreachable", error="secret-that-must-not-be-stored")

    http = HTTP()
    report = sample.run(catalogue, registry, n=60, seed="week", as_of=TODAY, fetcher=http)
    assert http.calls == 1
    assert report["counts"] == {"matched": 0, "mismatched": 0, "unreadable": 2}
    assert "secret-that-must-not-be-stored" not in json.dumps(report)


@pytest.mark.parametrize(
    "url",
    [
        "https://artificialanalysis.ai/test",
        "https://zapier.com/test",
        "https://user:password@example.test/docs",
        "https://example.test/?token=secret",
    ],
)
def test_refused_sources_never_fetched(catalogue, registry, url):
    class HTTP:
        def fetch(self, url):
            pytest.fail("refused source reached HTTP")

    catalogue.sources["src-lab-docs"]["url"] = url
    report = sample.run(catalogue, registry, n=60, seed="week", as_of=TODAY, fetcher=HTTP())
    assert report["counts"]["unreadable"] == 2
    assert url not in json.dumps(report)


def test_report_and_append_only_defects(catalogue, registry, tmp_path):
    inv = invariants.run(catalogue, registry, TODAY)
    inv["findings"] = [
        {"id": MID, "field": "model.context_window", "rule": "source_required", "severity": "error"}
    ]
    inv["errors"] = 1

    def reader(f, *args):
        return (
            ("unreadable", "no_reading")
            if f["field"] == "model.weights_openness"
            else ("mismatched", "difference")
        )

    sampled = sample.run(catalogue, registry, n=60, seed="week", as_of=TODAY, reader=reader)
    report = {
        "as_of": TODAY.isoformat(),
        "engine_commit": "synthetic",
        "invariants": inv,
        "sample": sampled,
    }
    defects = tmp_path / "defects.jsonl"
    assert append_defects(defects, report) == 2
    first = defects.read_bytes()
    assert append_defects(defects, report) == 0
    assert defects.read_bytes() == first
    assert all(row["guard"] is None for row in map(json.loads, defects.read_text().splitlines()))
    md, payload = write(report, tmp_path)
    assert json.loads(payload.read_text())["sample"]["error_rate"]["estimate"] == 1
    assert "source_required" in md.read_text()
    assert MID not in summary(report)
    assert "mismatched: 1; unreadable: 1" in summary(report)
    with gzip.open(tmp_path / f"{TODAY}.findings.jsonl.gz", "rt") as f:
        assert list(map(json.loads, f)) == inv["findings"]


def test_defect_rotation_preserves_all_errors(catalogue, registry, tmp_path, monkeypatch):
    from scripts.data_trust import report as reporting

    monkeypatch.setattr(reporting, "MAX_DEFECT_BYTES", 400)
    findings = [
        {"id": str(i), "field": "field", "rule": "parse", "severity": "error"} for i in range(20)
    ]
    report = {"as_of": str(TODAY), "invariants": {"findings": findings}, "sample": {"results": []}}
    path = tmp_path / "defects.jsonl"
    assert append_defects(path, report) == 20
    logs = sorted(tmp_path.glob("defects*.jsonl"))
    before = {p.name: p.read_bytes() for p in logs}
    assert len(logs) > 1
    assert all(p.stat().st_size <= 400 for p in logs)
    assert append_defects(path, report) == 0
    assert {p.name: p.read_bytes() for p in logs} == before
    entries = [json.loads(line) for p in logs for line in p.read_text().splitlines()]
    assert {e["model/fact id"] for e in entries} == {str(i) for i in range(20)}


def test_redirect_to_excluded_source_never_sent():
    calls = []

    def respond(request):
        calls.append(str(request.url))
        return httpx.Response(302, headers={"location": "https://zapier.com/docs"})

    with httpx.Client(
        transport=httpx.MockTransport(respond), event_hooks={"request": [sample.guard_request]}
    ) as client:
        with pytest.raises(ValueError, match="refused source"):
            client.get("https://example.test/docs", follow_redirects=True)
    assert calls == ["https://example.test/docs"]


def test_command_outputs_report_before_error_exit(tmp_path, registry, monkeypatch, capsys):
    from scripts.data_trust import __main__ as command

    monkeypatch.setattr(command, "load_registry", lambda *a, **kw: registry)
    (tmp_path / "models").mkdir()
    (tmp_path / "benchmarks").mkdir()
    raw = fact("model", MID, "model.context_window", -2)
    (tmp_path / "models/card.md").write_text(
        "---\n"
        + yaml.safe_dump({"model_id": MID, "facts": [raw], "cost": {"input": -999}})
        + "---\n"
    )
    (tmp_path / "registry").mkdir()
    (tmp_path / "registry/sources.yaml").write_text(
        yaml.safe_dump(
            {
                "schema_version": 1,
                "sources": [
                    {
                        "id": "src-lab-docs",
                        "url": "https://example.test/docs",
                        "cited_regions": [{"id": "r1", "locator": {"kind": "page"}}],
                    }
                ],
            }
        )
    )
    assert (
        command.main(
            [
                "data",
                "--data-dir",
                str(tmp_path),
                "--json",
                "--date",
                str(TODAY),
                "--output-dir",
                str(tmp_path / "reports"),
            ]
        )
        == 1
    )
    payload = json.loads(capsys.readouterr().out)
    assert payload["invariants"]["errors"] > 0
    assert "nonnegative" in {f["rule"] for f in payload["invariants"]["findings"]}
    assert (tmp_path / "reports" / f"{TODAY}.json").exists()
    assert len(payload["audit_code_sha256"]) == 64


def test_sample_mismatch_does_not_fail_command(tmp_path, catalogue, registry, monkeypatch, capsys):
    from scripts.data_trust import __main__ as command

    monkeypatch.setattr(command, "load_registry", lambda *a, **kw: registry)
    monkeypatch.setattr(command, "load", lambda *a: catalogue)
    monkeypatch.setattr(command, "calibrate", lambda *a: None)
    original = sample.run

    def fake_run(c, r, **kwargs):
        return original(c, r, **kwargs, reader=lambda *args: ("mismatched", "difference"))

    monkeypatch.setattr(command.sample, "run", fake_run)
    (tmp_path / "models").mkdir()
    (tmp_path / "benchmarks").mkdir()
    assert (
        command.main(["sample", "--data-dir", str(tmp_path), "--json", "--date", str(TODAY)]) == 0
    )
    assert json.loads(capsys.readouterr().out)["sample"]["counts"]["mismatched"] == 2


def test_registry_source_and_board_enums(catalogue, registry):
    catalogue.sources["src-lab-docs"]["fetch"] = "firecrawl"
    catalogue.boards["test_board"] = {"metric": {"direction": "invalid"}}
    catalogue.models[MID]["lifecycle"] = "invalid"
    assert {"source_schema", "benchmark_schema", "model_schema"} <= rules(catalogue, registry)


def test_editorial_card_metadata_is_not_a_research_claim(tmp_path):
    (tmp_path / "models").mkdir()
    raw = {
        "model_id": MID,
        "card_schema_version": "3.0",
        "card_author": "editor",
        "card_created": "2026-09-01",
        "card_updated": "2026-09-20",
        "cost": {"input": 2},
    }
    (tmp_path / "models/card.md").write_text("---\n" + yaml.safe_dump(raw) + "---\n")
    assert [(f["field"], f["value"]) for f in load(tmp_path).facts] == [("cost.input", 2)]


def test_url_only_source_uses_page_reader(catalogue, registry):
    class HTTP:
        def fetch(self, url):
            return FetchResult(
                "ok",
                body=b"Model: Test Model\nmodel.context window: 128000 tokens\n",
                content_type="text/plain",
            )

    catalogue.facts = catalogue.facts[1:]
    catalogue.facts[0]["sources"] = []
    catalogue.facts[0]["source_url"] = "https://example.test/docs"
    assert (
        sample.run(catalogue, registry, n=60, seed="week", as_of=TODAY, fetcher=HTTP())["counts"][
            "matched"
        ]
        == 1
    )


def test_legacy_is_coverage_only(catalogue, registry):
    from scripts.data_trust.catalogue import _legacy

    _legacy(catalogue, {"cost": {"input": -5}, "benchmarks": {"scores": {"old": 999}}}, MID)
    result = invariants.run(catalogue, registry, TODAY)
    assert result["errors"] == 0
    assert result["facts"] == 2
    assert result["legacy_provenance"]["fields"] == 2
    assert result["legacy_provenance"]["sourced"] == 0
    assert result["legacy_provenance"]["by_family"]["cost"]["share"] == 0
    assert not any("#legacy:" in f["id"] for f in result["findings"])


def test_offering_rule_is_warning_until_model_266(catalogue, registry):
    catalogue.facts = catalogue.facts[1:]
    result = invariants.run(catalogue, registry, TODAY)
    assert result["errors"] == 0
    assert result["findings"] == [
        {
            "id": MID,
            "field": "model.weights_openness",
            "rule": "offering_or_verified_open_weights",
            "severity": "warning",
        }
    ]
    assert "#456" in result["offering_rule_status"]


def test_sample_excludes_legacy_unsourced_and_unknown(catalogue, registry):
    from scripts.data_trust.catalogue import _legacy

    _legacy(catalogue, {"context": 100}, MID)
    catalogue.facts[0]["sources"] = []
    result = sample.run(
        catalogue, registry, n=60, seed="week", as_of=TODAY, reader=lambda *a: ("matched", "read")
    )
    assert result["sampled"] == 1
    assert result["results"][0]["field"] == "model.context_window"


def test_collector_metadata_is_preserved(catalogue, registry):
    from dataclasses import replace

    f = catalogue.facts[1]
    original = replace(
        sample.claim_for(f, catalogue, registry), label="Context window", names=("Published Alias",)
    )
    catalogue.claims[("fact", f["id"])] = original
    assert sample.claim_for(f, catalogue, registry).label == "Context window"
    assert sample.claim_for(f, catalogue, registry).names == ("Published Alias",)
    f["value"] = 256000
    assert sample.claim_for(f, catalogue, registry).value == 256000


def test_reader_coverage_probes_llm_facts(catalogue, registry, monkeypatch, tmp_path):
    from decision.sources import CopyStore
    from scripts.data_trust import sample as sampling

    store = CopyStore(tmp_path)
    ref = store.put(
        b"Model: Test Model\nmodel.context window: 128000 tokens\n"
        b"model.weights openness: open_weights\n"
    )
    for f in catalogue.facts:
        f["sources"][0]["snapshot_ref"] = ref
    monkeypatch.setattr(sampling, "CopyStore", lambda *a: store)
    result = sampling.reader_coverage(catalogue, registry, TODAY)
    assert result["served"] == 2
    assert result["with_reader"] == 2
    assert result["share"] == 1


def test_projections_reuse_existing_extractors(catalogue, registry, monkeypatch):
    from dataclasses import replace

    from scripts.accuracy import _PROJECTIONS

    claim = replace(
        sample.claim_for(catalogue.facts[1], catalogue, registry),
        collector=sample.VerificationActor(
            agent="collector", model_family="family-a", method="hf-result-projection@1"
        ),
    )
    monkeypatch.setitem(_PROJECTIONS, "hf-result-projection@1", lambda url, body: b"projected")
    assert sample.project(claim, "https://example.test/results.json", b"raw", TODAY) == b"projected"


def test_calibration_uses_engine_admission(catalogue, registry, monkeypatch, tmp_path):
    from decision import snapshot
    from scripts.data_trust.catalogue import _legacy

    held = copy.deepcopy(catalogue.facts[1])
    held.update(id="held", field="model.max_output_tokens", facet="model.max_output_tokens")
    held["verification"]["outcome"] = "unreachable"
    catalogue.facts.append(held)
    _legacy(catalogue, {"benchmarks": {"scores": {"old": 999}}}, MID)
    inputs = snapshot.SnapshotInputs(
        models=[
            {
                "id": MID,
                "lifecycle": "active",
                "facts": [
                    {
                        k: f[k]
                        for k in (
                            "id",
                            "subject",
                            "facet",
                            "state",
                            "value",
                            "sources",
                            "verification",
                        )
                    }
                    for f in catalogue.facts
                    if f["kind"] == "fact"
                ],
            }
        ],
        sources={sid: row["url"] for sid, row in catalogue.sources.items()},
    )
    monkeypatch.setattr(snapshot, "collect_repo", lambda root: inputs)
    calibrate(catalogue, tmp_path, registry, TODAY)
    assert {f["field"] for f in catalogue.facts} == {
        "model.weights_openness",
        "model.context_window",
    }
    assert {f["id"] for f in catalogue.legacy} == {"held", f"{MID}#legacy:benchmarks.scores.old"}
    result = invariants.run(catalogue, registry, TODAY)
    assert result["errors"] == 0
    assert result["legacy_provenance"]["fields"] == 2
    assert result["legacy_provenance"]["sourced"] == 1


def test_fresh_html_uses_html_normaliser(catalogue, registry):
    class HTTP:
        def fetch(self, url):
            return FetchResult(
                "ok",
                content_type="text/html",
                body=b"<html><body><p>Model: Test Model</p>"
                b"<p>model.context window: 128000 tokens</p></body></html>",
            )

    catalogue.facts = catalogue.facts[1:]
    result = sample.run(catalogue, registry, n=60, seed="week", as_of=TODAY, fetcher=HTTP())
    assert result["counts"]["matched"] == 1


def test_primary_fallback_and_fetch_cache(catalogue, registry):
    catalogue.sources["fallback"] = {
        **catalogue.sources["src-lab-docs"],
        "id": "fallback",
        "url": "https://example.test/fallback",
    }
    f = catalogue.facts[1]
    f["sources"].append({**f["sources"][0], "source_id": "fallback"})
    catalogue.facts = [f]
    calls = []

    class HTTP:
        def fetch(self, url):
            calls.append(url)
            body = (
                b"Nothing to read"
                if url.endswith("docs")
                else b"Model: Test Model\nmodel.context window: 128000 tokens\n"
            )
            return FetchResult("ok", body=body)

    result = sample.run(catalogue, registry, n=60, seed="week", as_of=TODAY, fetcher=HTTP())
    assert result["counts"]["matched"] == 1
    assert len(calls) == 2


def test_ignored_prose_cannot_fail_calibrated_audit(catalogue, registry, monkeypatch, tmp_path):
    from decision import snapshot
    from scripts.data_trust.catalogue import Finding

    catalogue.findings.append(Finding("models/editorial.md", "model_id", "missing_id"))
    inputs = snapshot.SnapshotInputs(models=[{"id": MID, "lifecycle": "active", "facts": []}])
    monkeypatch.setattr(snapshot, "collect_repo", lambda root: inputs)
    calibrate(catalogue, tmp_path, registry, TODAY)
    assert invariants.run(catalogue, registry, TODAY)["errors"] == 0


@pytest.mark.parametrize(
    "score,volatility,date_type,outcome",
    [
        (0.9, "live", "evaluated", "matched"),
        (0.9, "live", "published", "matched"),
        (0.8, "live", "evaluated", "mismatched"),
        (0.9, "static", "published", "mismatched"),
    ],
)
def test_live_observation_date_is_not_a_value_error(
    catalogue, registry, score, volatility, date_type, outcome
):
    from dataclasses import replace

    from tests.snapshot_records import evidence

    row = evidence(MID, "mteb_eng_v2", 90, source="src-lab-docs", day="2026-09-01")
    row["date_type"] = date_type
    catalogue.facts = []
    _records(catalogue, [row], MID, "evidence", catalogue.models[MID])
    f = catalogue.facts[0]
    claim = replace(sample.claim_for(f, catalogue, registry), label="mean_task")
    catalogue.claims[("evidence", f["id"])] = claim
    catalogue.sources["src-lab-docs"].update(
        url="https://mteb-leaderboard-backend.hf.space/v1/test", volatility=volatility
    )

    class HTTP:
        def fetch(self, url):
            return FetchResult(
                "ok",
                body=json.dumps(
                    {"rows": [{"model": {"name": "Test Model"}, "meanTask": score}]}
                ).encode(),
            )

    report = sample.run(catalogue, registry, n=60, seed="week", as_of=TODAY, fetcher=HTTP())
    assert report["counts"][outcome] == 1
    if outcome == "matched":
        assert report["results"][0]["reason"] == "observation_date_advanced"
