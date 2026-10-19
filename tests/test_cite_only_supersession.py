"""A newer cite-only read of a newly cited region supersedes a stale mismatch (MODEL-415).

All sources, page hashes and records are synthetic and built here. No page
text from any cite-only host is used.
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import replace
from datetime import UTC, date, datetime

import pytest

from decision import supersession
from decision.bounded import project
from decision.contract import ResponseOptions, parse_spec
from decision.engine import decide
from decision.explain import checked_record
from decision.model import value_hash
from decision.registry import facet
from decision.snapshot import (
    SnapshotInputs,
    build_snapshot,
    collect_repo,
    load_built_snapshot,
)
from tests.snapshot_records import SOURCES, fact, model, subscription, verification

TODAY = date(2026, 10, 19)
CITE_URL = "https://www.perplexity.ai/pro"
PLAIN_URL = "https://lab.example.com/plans"
SOURCE = "src-plan-page"
SID = "sambanova/subscription/pro"
FACET = "offering.subscription.models_covered"
FACT_ID = f"{SID}#{FACET}"
VALUE = ["lab/alpha"]
METHOD = "subscription-page@1"
MISMATCH_DAY = "2026-10-14"
READ_AT = datetime(2026, 10, 19, 17, 51, 11, tzinfo=UTC)
WARNING = "cite_only_not_machine_verified"


def page_hash(label: str) -> str:
    return "sha256:" + hashlib.sha256(f"synthetic {label} page".encode()).hexdigest()


OLD_PAGE = page_hash("plan card")
NEW_PAGE = page_hash("questions")


def mismatch(fact_id=FACT_ID, value=VALUE, day=MISMATCH_DAY):
    row = verification("fact", fact_id, "mismatch", day=day, value=value)
    row["verifier"] = {"agent": "modelspec-verify", "model_family": "deterministic",
                       "method": METHOD}
    row["method"] = METHOD
    row["diff"] = json.dumps([{"field": "value", "expected": value, "found": None}])
    return row


def record(fact_id=FACT_ID, value=VALUE, *, mismatch_region="pricing", read_region="faq",
           read_at=READ_AT, read_hash=NEW_PAGE, url=CITE_URL, day=MISMATCH_DAY, **extra):
    row = {
        "schema_version": 1,
        "target": {"kind": "fact", "id": fact_id, "value_hash": value_hash(value)},
        "mismatch": {"date": day, "method": METHOD, "source_id": SOURCE, "url": url,
                     "region": mismatch_region, "snapshot_ref": OLD_PAGE},
        "read": {"source_id": SOURCE, "url": url, "region": read_region,
                 "retrieved_at": read_at.isoformat(), "snapshot_ref": read_hash},
        "recorded_at": max(read_at, READ_AT).isoformat(),
        "recorded_by": "fixture-curator",
        "reason": "the plan card no longer lists models; the questions region does",
    }
    for key, value_ in extra.items():
        if value_ is None:
            row["read"].pop(key, None)
        else:
            row["read"][key] = value_
    return row


def cited_fact(*, region="faq", snapshot_ref=NEW_PAGE, read_at=READ_AT, source=SOURCE):
    row = fact("offering", SID, FACET, VALUE, source=source, outcome=None)
    row["sources"][0].update(snapshot_ref=snapshot_ref, cited_regions=[region],
                             retrieved_at=read_at.isoformat())
    return row


def inputs(*, records=(), url=CITE_URL, log=None, **fact_kwargs):
    return SnapshotInputs(
        models=[model("lab/alpha")],
        subscriptions=[subscription(facts=[cited_fact(**fact_kwargs)])],
        sources={**SOURCES, SOURCE: url},
        verifications=log if log is not None else [
            verification("fact", FACT_ID, "verified", day="2026-09-29", value=VALUE),
            mismatch(),
        ],
        supersessions=list(records),
    )


def loaded(snapshot_inputs):
    return load_built_snapshot(build_snapshot(snapshot_inputs, as_of=TODAY))


def plan_fact(index):
    plan = next(row for row in index.subscription_offerings() if row["id"] == SID)
    return plan["facts"].get(FACET)


# ── the MODEL-368 shape ────────────────────────────────────────────────────


def test_stale_mismatch_quarantines_without_a_supersession():
    assert plan_fact(loaded(inputs())) is None


def test_newer_read_of_newly_cited_region_admits_the_fact_as_cited():
    index = loaded(inputs(records=[record()]))
    admitted = plan_fact(index)
    assert admitted is not None
    assert (admitted.state, admitted.value) == ("known", VALUE)
    assert admitted.record_id in index.cited_facts(SID)
    retained = index.record(admitted.record_id)
    assert retained["verification"] is None
    assert retained["citation"] == {"status": "cited", "sources": [{
        "source_id": SOURCE, "url": CITE_URL, "snapshot_ref": NEW_PAGE,
        "retrieved_at": READ_AT.isoformat(),
    }]}


def test_a_new_source_id_for_the_new_region_also_supersedes():
    row = record()
    row["read"]["source_id"] = "src-plan-questions"
    built = replace(inputs(records=[row], source="src-plan-questions"),
                    sources={**SOURCES, SOURCE: CITE_URL, "src-plan-questions": CITE_URL})
    assert plan_fact(loaded(built)) is not None


def test_superseded_mismatch_stays_in_provenance():
    index = loaded(inputs(records=[record()]))
    retained = index.record(plan_fact(index).record_id)
    [entry] = retained["superseded_mismatches"]
    trace = entry["verification"]
    assert trace["outcome"] == "mismatch"
    assert trace["date"] == MISMATCH_DAY
    assert trace["method"] == METHOD
    assert trace["target"] == {"kind": "fact", "id": FACT_ID, "value_hash": value_hash(VALUE)}
    assert "diff" not in trace
    assert trace["diff_sha256"] == "sha256:" + hashlib.sha256(
        mismatch()["diff"].encode()).hexdigest()
    named = entry["supersession"]
    assert (named["mismatch"]["region"], named["read"]["region"]) == ("pricing", "faq")
    assert named["mismatch"]["snapshot_ref"] == OLD_PAGE
    assert named["read"]["snapshot_ref"] == NEW_PAGE
    assert named["read"]["retrieved_at"] == READ_AT.isoformat()
    assert entry["supersession_hash"].startswith("sha256:")


def test_superseded_fact_never_reports_verified():
    index = loaded(inputs(records=[record()]))
    retained = index.record(plan_fact(index).record_id)
    assert '"verified"' not in json.dumps(retained)
    assert retained["citation"]["status"] == "cited"
    checked_record(index, plan_fact(index).record_id)


# ── refusals ───────────────────────────────────────────────────────────────


def test_same_region_mismatch_stays_quarantined(caplog):
    with caplog.at_level(logging.WARNING, logger="decision.snapshot"):
        index = loaded(inputs(records=[record(read_region="pricing")], region="pricing"))
    assert plan_fact(index) is None
    assert "same region" in caplog.text


def test_same_region_through_an_alias_source_stays_quarantined():
    row = record(read_region="pricing")
    row["read"]["source_id"] = "src-alias"
    built = replace(inputs(records=[row], region="pricing", source="src-alias"),
                    sources={**SOURCES, SOURCE: CITE_URL, "src-alias": CITE_URL})
    assert plan_fact(loaded(built)) is None


def test_citing_both_old_and_new_regions_stays_quarantined():
    built = inputs(records=[record()])
    built.subscriptions[0]["facts"][0]["sources"][0]["cited_regions"] = ["pricing", "faq"]
    assert plan_fact(loaded(built)) is None


@pytest.mark.parametrize("read_at", [
    datetime(2026, 10, 13, 9, tzinfo=UTC),
    datetime(2026, 10, 14, 23, 59, tzinfo=UTC),
])
def test_read_older_than_or_same_day_as_mismatch_does_not_supersede(read_at, caplog):
    with caplog.at_level(logging.WARNING, logger="decision.snapshot"):
        index = loaded(inputs(records=[record(read_at=read_at)], read_at=read_at))
    assert plan_fact(index) is None
    assert "not newer" in caplog.text


def test_newer_mismatch_after_the_read_is_not_superseded():
    log = [mismatch(), mismatch(day="2026-10-20")]
    assert plan_fact(loaded(inputs(records=[record()], log=log))) is None


@pytest.mark.parametrize("snapshot_ref", [None, "sha256:" + "z" * 64, "sha256:abc", "md5:00"])
def test_missing_or_invalid_page_hash_does_not_supersede(snapshot_ref, caplog):
    with caplog.at_level(logging.WARNING, logger="decision.snapshot"):
        index = loaded(inputs(records=[record(snapshot_ref=snapshot_ref)]))
    assert plan_fact(index) is None
    assert "invalid record" in caplog.text


@pytest.mark.parametrize("field", ["retrieved_at", "url"])
def test_read_without_fetch_time_or_url_does_not_supersede(field):
    row = record()
    del row["read"][field]
    assert plan_fact(loaded(inputs(records=[row]))) is None


def test_naive_fetch_time_does_not_supersede():
    row = record()
    row["read"]["retrieved_at"] = "2026-10-19T17:51:11"
    assert plan_fact(loaded(inputs(records=[row]))) is None


def test_read_hash_differing_from_the_citation_does_not_supersede():
    assert plan_fact(loaded(inputs(records=[record(read_hash=OLD_PAGE)]))) is None


def test_read_time_differing_from_the_citation_does_not_supersede():
    later = datetime(2026, 10, 19, 18, tzinfo=UTC)
    assert plan_fact(loaded(inputs(records=[record(read_at=later)]))) is None


def test_record_for_another_value_does_not_supersede():
    other = record(value=["lab/beta"])
    assert plan_fact(loaded(inputs(records=[other]))) is None


def test_non_cite_only_fact_with_a_mismatch_is_unaffected():
    built = inputs(records=[record(url=PLAIN_URL)], url=PLAIN_URL)
    assert plan_fact(loaded(built)) is None


def test_unreachable_is_never_superseded():
    unreachable = verification("fact", FACT_ID, "unreachable", day=MISMATCH_DAY, value=VALUE)
    assert plan_fact(loaded(inputs(records=[record()], log=[unreachable]))) is None


def test_one_valid_record_applies_beside_a_refused_one():
    index = loaded(inputs(records=[record(read_region="pricing"), record()]))
    assert plan_fact(index) is not None


def test_snapshot_without_supersessions_keeps_its_bytes():
    plain = build_snapshot(inputs(), as_of=TODAY)
    unrelated = record(fact_id="sambanova/subscription/pro#offering.subscription.price")
    assert build_snapshot(inputs(records=[unrelated]), as_of=TODAY).content_hash \
        == plain.content_hash


# ── decisions ──────────────────────────────────────────────────────────────


def test_superseded_model_fact_is_cited_in_decisions_never_verified():
    cid, context = "lab/cited", 8000
    row = fact("model", cid, "model.context_window", context, source=SOURCE, outcome=None)
    row["sources"][0].update(snapshot_ref=NEW_PAGE, cited_regions=["faq"],
                             retrieved_at=READ_AT.isoformat())
    built = SnapshotInputs(
        models=[model(cid, facts=[row, fact("model", cid, "model.class", "text-generator"),
                                  fact("model", cid, "model.max_output_tokens", 4000)])],
        sources={**SOURCES, SOURCE: CITE_URL},
        verifications=[mismatch(fact_id=row["id"], value=context)],
        supersessions=[record(fact_id=row["id"], value=context)],
    )
    index = loaded(built)
    assert index.fact(cid, "model.context_window").value == context
    spec = parse_spec({"spec_version": 1, "where": [],
                       "optimize": {"max": "model.context_window"},
                       "explain": "full", "limit": 1}, facets=facet)
    answer = decide(spec, index, facets=facet)
    bounded = project(answer, ResponseOptions(fields=["model_rank"]), not_applied=[], spec=spec)
    assert WARNING in answer.warnings
    assert WARNING in bounded["warnings"]
    shown = [f for f in answer.top[0].facts if f.facet == "model.context_window"]
    assert shown and shown[0].citation is not None
    assert shown[0].citation.status == "cited"
    body = answer.model_dump_json()
    assert '"outcome":"verified"' not in body
    assert "superseded_mismatches" not in body


# ── the store ──────────────────────────────────────────────────────────────


def test_collect_repo_reads_the_supersession_store(tmp_path):
    (tmp_path / "verification").mkdir()
    rows = [record(), record(read_region="pricing")]
    (tmp_path / "verification" / "supersessions.jsonl").write_text(
        "".join(json.dumps(row) + "\n" for row in rows) + "\n", encoding="utf-8")
    assert collect_repo(tmp_path).supersessions == rows


def test_collect_repo_without_a_store_has_no_supersessions(tmp_path):
    assert collect_repo(tmp_path).supersessions == []


def test_append_only_violation_names_edited_or_removed_lines():
    base = "a\nb\n"
    assert supersession.append_only_violation(base, "a\nb\nc\n") is None
    assert supersession.append_only_violation(base, base) is None
    assert supersession.append_only_violation(base, "a\nB\nc\n") == "line 2 was changed"
    assert supersession.append_only_violation(base, "a\n") == "line 2 was removed"


def test_record_cannot_predate_its_read_or_target_evidence():
    early = record()
    early["recorded_at"] = "2026-10-19T00:00:00+00:00"
    with pytest.raises(ValueError):
        supersession.MismatchSupersession.model_validate(early)
    evidence_target = record()
    evidence_target["target"]["kind"] = "evidence"
    with pytest.raises(ValueError):
        supersession.MismatchSupersession.model_validate(evidence_target)
