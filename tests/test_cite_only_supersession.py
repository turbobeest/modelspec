"""A newer cite-only read of a newly cited region supersedes a stale mismatch (MODEL-415).

All sources, page hashes and records are synthetic and built here. No page
text from any cite-only host is used.
"""

from __future__ import annotations

import hashlib
import json
import logging
import subprocess
import sys
from dataclasses import replace
from datetime import UTC, date, datetime

import pytest

from decision.bounded import project
from decision.contract import ResponseOptions, parse_spec
from decision.engine import decide
from decision.explain import checked_record
from decision.model import value_hash
from decision.registry import facet
from decision.snapshot import (
    SnapshotBuildError,
    SnapshotInputs,
    build_snapshot,
    collect_repo,
    load_built_snapshot,
)
from decision.verify import Verification, VerificationLog
from tests.snapshot_records import SOURCES, fact, model, subscription, verification

TODAY = date(2026, 10, 19)
CITE_URL = "https://www.perplexity.ai/pro"
PLAIN_URL = "https://lab.example.com/plans"
#: Where the cited page's fetch was redirected from: the same page under another URL.
ALIAS_URL = "https://lab.example.com/pro-plan"
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


def cited_fact(*, region="faq", snapshot_ref=NEW_PAGE, read_at=READ_AT, source=SOURCE,
               resolved_urls=None):
    row = fact("offering", SID, FACET, VALUE, source=source, outcome=None)
    row["sources"][0].update(snapshot_ref=snapshot_ref, cited_regions=[region],
                             retrieved_at=read_at.isoformat())
    if resolved_urls is not None:
        row["sources"][0]["resolved_urls"] = resolved_urls
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
def test_missing_or_invalid_page_hash_fails_the_build(snapshot_ref):
    with pytest.raises(SnapshotBuildError,
                       match=r"supersession row 1: invalid supersession record \(read\.snapshot_ref"):
        loaded(inputs(records=[record(snapshot_ref=snapshot_ref)]))


@pytest.mark.parametrize("field", ["retrieved_at", "url"])
def test_read_without_fetch_time_or_url_fails_the_build(field):
    row = record()
    del row["read"][field]
    with pytest.raises(SnapshotBuildError, match=rf"read\.{field}: missing"):
        loaded(inputs(records=[row]))


def test_naive_fetch_time_fails_the_build():
    row = record()
    row["read"]["retrieved_at"] = "2026-10-19T17:51:11"
    with pytest.raises(SnapshotBuildError, match=r"read\.retrieved_at: timezone_aware"):
        loaded(inputs(records=[row]))


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


def test_redirect_alias_of_the_cited_page_is_the_same_region(caplog):
    """The reviewer's probe: the mismatch read ``faq`` on a URL the citation redirected through."""
    row = record(mismatch_region="faq")
    row["mismatch"].update(source_id="src-old", url=ALIAS_URL)
    built = replace(inputs(records=[row], resolved_urls=[ALIAS_URL]),
                    sources={**SOURCES, SOURCE: CITE_URL, "src-old": ALIAS_URL})
    with caplog.at_level(logging.WARNING, logger="decision.snapshot"):
        assert plan_fact(loaded(built)) is None
    assert "same region" in caplog.text


def test_redirect_alias_of_another_region_still_supersedes():
    row = record()
    row["mismatch"].update(source_id="src-old", url=ALIAS_URL)
    built = replace(inputs(records=[row], resolved_urls=[ALIAS_URL]),
                    sources={**SOURCES, SOURCE: CITE_URL, "src-old": ALIAS_URL})
    assert plan_fact(loaded(built)) is not None


def test_a_card_redirect_to_a_cite_only_host_is_not_cite_only_proof():
    """Only the registered URL makes a read cite-only, never a card's ``resolved_urls``."""
    built = inputs(records=[record(url=PLAIN_URL)], url=PLAIN_URL, resolved_urls=[CITE_URL])
    assert plan_fact(loaded(built)) is None


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
    from decision import supersession

    base = "a\nb\n"
    assert supersession.append_only_violation(base, "a\nb\nc\n") is None
    assert supersession.append_only_violation(base, base) is None
    assert supersession.append_only_violation(base, "a\nB\nc\n") == "line 2 was changed"
    assert supersession.append_only_violation(base, "a\n") == "line 2 was removed"


def test_record_cannot_predate_its_read_or_target_evidence():
    from decision import supersession

    early = record()
    early["recorded_at"] = "2026-10-19T00:00:00+00:00"
    with pytest.raises(ValueError):
        supersession.MismatchSupersession.model_validate(early)
    evidence_target = record()
    evidence_target["target"]["kind"] = "evidence"
    with pytest.raises(ValueError):
        supersession.MismatchSupersession.model_validate(evidence_target)


def test_snapshot_import_does_not_load_the_supersession_module():
    """The Worker imports decision.snapshot but never compiles; keep its heap flat."""
    probe = ("import sys, decision.snapshot, decision.explain, decision.engine; "
             "print('decision.supersession' in sys.modules)")
    out = subprocess.run([sys.executable, "-c", probe], capture_output=True, text=True,
                         check=True)
    assert out.stdout.strip() == "False"


def test_compile_without_records_never_loads_the_supersession_module():
    probe = (
        "import sys; from tests.test_cite_only_supersession import inputs, loaded; "
        "loaded(inputs()); print('decision.supersession' in sys.modules)"
    )
    out = subprocess.run([sys.executable, "-c", probe], capture_output=True, text=True,
                         check=True)
    assert out.stdout.strip() == "False"


# ── a malformed store fails loudly ─────────────────────────────────────────


def store(tmp_path, *lines):
    (tmp_path / "verification").mkdir(exist_ok=True)
    path = tmp_path / "verification" / "supersessions.jsonl"
    path.write_text("".join(line + "\n" for line in lines), encoding="utf-8")
    return path


def orphan_with_bad_schema():
    row = record(fact_id="gone/subscription/plan#offering.subscription.price")
    row["schema_version"] = 9
    return row


@pytest.mark.parametrize(("bad", "why"), [
    (json.dumps({"hello": 1}), "must name its target fact id"),
    (json.dumps({**record(), "target": "x"}), "must name its target fact id"),
    (json.dumps({**record(), "target": {"kind": "fact", "id": " "}}),
     "must name its target fact id"),
    (json.dumps([record()]), "must be a JSON object"),
    (json.dumps("a record"), "must be a JSON object"),
    (json.dumps(orphan_with_bad_schema()), r"invalid supersession record \(schema_version"),
], ids=["no-target", "string-target", "blank-id", "array-row", "string-row",
        "orphan-bad-schema"])
def test_malformed_store_row_fails_at_load_with_its_line(tmp_path, bad, why):
    store(tmp_path, json.dumps(record()), bad)
    with pytest.raises(ValueError, match=rf"supersessions\.jsonl: line 2: .*{why}"):
        collect_repo(tmp_path)


def test_malformed_row_message_names_fields_never_values(tmp_path):
    row = orphan_with_bad_schema()
    row["reason"] = "private page text"
    row["recorded_by"] = 7
    store(tmp_path, json.dumps(row))
    with pytest.raises(ValueError) as caught:
        collect_repo(tmp_path)
    assert str(caught.value).endswith(
        "supersessions.jsonl: line 1: invalid supersession record "
        "(schema_version: literal_error; recorded_by: string_type)")


def test_invalid_json_line_fails_at_load_with_its_line(tmp_path):
    store(tmp_path, json.dumps(record()), "{not json")
    with pytest.raises(ValueError, match=r"supersessions\.jsonl: line 2"):
        collect_repo(tmp_path)


@pytest.mark.parametrize("bad", [{"hello": 1}, ["row"], "row", orphan_with_bad_schema()],
                         ids=["no-target", "array-row", "string-row", "orphan-bad-schema"])
def test_malformed_input_row_fails_the_build_even_when_no_fact_needs_it(bad):
    with pytest.raises(SnapshotBuildError, match="supersession row 2"):
        build_snapshot(inputs(records=[record(), bad]), as_of=TODAY)


def test_orphan_record_for_a_missing_fact_is_allowed(tmp_path):
    orphan = record(fact_id="gone/subscription/plan#offering.subscription.price")
    store(tmp_path, json.dumps(orphan))
    assert collect_repo(tmp_path).supersessions == [orphan]
    assert plan_fact(loaded(inputs(records=[orphan]))) is None


def test_line_separators_inside_a_json_string_are_not_line_breaks(tmp_path):
    row = record()
    row["reason"] = "the plan card\u2028moved\u0085to the questions"
    path = store(tmp_path, json.dumps(row, ensure_ascii=False))
    assert collect_repo(tmp_path).supersessions == [row]
    from decision import supersession

    text = path.read_text(encoding="utf-8")
    assert supersession.append_only_violation(text, text + "{}\n") is None


# ── the store beside the verification log ──────────────────────────────────


def logged(tmp_path):
    row = mismatch()
    (tmp_path / "verification").mkdir(exist_ok=True)
    (tmp_path / "verification" / "log.jsonl").write_text(json.dumps(row) + "\n",
                                                         encoding="utf-8")
    return Verification.model_validate(row)


def test_verification_log_reads_only_the_log_beside_a_store(tmp_path):
    expected = logged(tmp_path)
    store(tmp_path, json.dumps(record()), json.dumps(record(read_region="pricing")))
    log = VerificationLog(tmp_path / "verification")
    assert log.records() == [expected]
    assert list(log.latest().values()) == [expected]
    assert log.requarantined() == []
    assert log.is_quarantined(f"fact:{FACT_ID}")


def test_verification_log_without_a_log_file_is_empty_beside_a_store(tmp_path):
    store(tmp_path, json.dumps(record()))
    assert VerificationLog(tmp_path / "verification").records() == []


def test_verify_cli_runs_with_a_store_beside_the_log(tmp_path, monkeypatch):
    from typer.testing import CliRunner

    from cli.modelspec.verify_cmd import app
    from decision.verify import Queue
    from tests.test_cite_only_verification import CITE_URL as QUEUED_URL
    from tests.test_cite_only_verification import claim

    expected = logged(tmp_path)
    path = store(tmp_path, json.dumps(record()))
    before = path.read_text(encoding="utf-8")
    (tmp_path / "registry").mkdir()
    (tmp_path / "registry" / "sources.yaml").write_text(
        "schema_version: 1\nsources:\n- id: src-lab-docs\n  url: " + QUEUED_URL + "\n")
    Queue(tmp_path / "verification").file(claim(), at=datetime(2026, 10, 19, tzinfo=UTC))
    monkeypatch.setenv("MODELSPEC_SOURCE_CACHE", str(tmp_path / "copies"))
    result = CliRunner().invoke(app, ["--root", str(tmp_path)])
    assert result.exit_code == 0, result.output
    assert "cited: 1" in result.output
    assert VerificationLog(tmp_path / "verification").records() == [expected]
    assert path.read_text(encoding="utf-8") == before
