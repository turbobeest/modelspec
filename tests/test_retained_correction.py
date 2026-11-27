"""MODEL-573: a logged two-reader agreement may correct a served value read from a retaining page.
MODEL-491 E1 and E2: a rule-16 confirmation is served as cited, and a correction is not held by a
mismatch on the value it replaced.

The gate (``retained_agreement(correct=True)``), the snapshot build and the site loader decide
through one test (``decision.retained_correction.correction_problem``). Bypass tests in the
MODEL-552 style: same family, an earlier epoch, a disagreement in the epoch, a licence fact, a
forged line, a held row. Every page, hash, verdict and attempt is synthetic and built here.
"""

from __future__ import annotations

import copy
import json
import socket
from datetime import UTC, date, datetime

import pytest
from decision.cited_change import REFUSALS, RETAINED_RULE, reread, retained_agreement
from decision.cited_reader import ATTEMPTS_FILE
from decision.quarantine_clearing import AttemptLog, line_hash
from decision.retained_correction import (
    RULE,
    confirmation_citation,
    confirmation_problem,
    correction_problem,
    filed_fact,
    is_confirmation,
    is_correction,
    owner_only,
)
from decision.snapshot import _Compiler

from tests import test_retained_agreement as gate
from tests.snapshot_records import verification

_PATCH: list = []


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    monkeypatch.setattr(socket.socket, "connect", lambda *a: pytest.fail("Network attempted"))
    _PATCH[:] = [monkeypatch]


def own(request):
    """Install ``request`` as the gate's own transport (``cited_change._http_once``)."""
    import decision.cited_change as gate_module

    _PATCH[0].setattr(gate_module, "_http_once", request)


# --- the gate -------------------------------------------------------------------------------------

AGREED = ["text", "image"]  # the documented value; the filed one is gate.FILED


@pytest.fixture
def data(tmp_path, monkeypatch):
    return gate.Data(tmp_path / "data", monkeypatch)


def run(*, caller=False, **kw):
    """The gate on its own fetch (``request`` becomes its own transport), or on the caller's."""
    request = kw.pop("request", None) or gate.serve()
    if not caller:
        own(request)
    args = dict(subject=gate.SUBJECT, facet=gate.FACET, source_id="readme",
                readers=gate.pair(AGREED), request=request if caller else None, correct=True)
    args.update(kw)
    return retained_agreement(**args)


def rr(readers, page=gate.PAGE):
    own(gate.serve({gate.URL: page}))
    return reread({"subject": gate.SUBJECT, "facet": gate.FACET}, source_id="readme",
                  readers=readers)


def refused(reason, **kw):
    out = run(**kw)
    assert out.outcome == "refused" and out.reason == reason, (out.reason, out.detail)
    assert out.record is None and reason in REFUSALS
    return out


def file_record(data, record):
    """Write the record into the card as a writer files it (``filed_fact``)."""
    fact = filed_fact(data.fact, record)
    data.fact.clear()
    data.fact.update(fact)
    data.write()


def raw_lines(data):
    return (data.root / ATTEMPTS_FILE).read_text().splitlines()


def test_an_agreed_other_value_corrects_the_filed_one_when_asked(data):
    out = run()
    assert out.changed, (out.reason, out.detail)
    rec = out.record
    block = rec["derivation"]["cited_change"]
    assert rec["value"] == AGREED and rec["state"] == "known"
    assert block["rule"] == RULE != RETAINED_RULE and "MODEL-573" in block["decided_by"]
    assert block["previous_value"] == gate.FILED and block["epoch"] == "initial"
    assert block["agreement"] == line_hash(raw_lines(data)[-1])
    assert "SECRET-PAGE-MARKER" not in json.dumps(rec)


def test_without_the_flag_an_agreed_other_value_is_still_refused(data):
    gate.refused("value_differs", readers=gate.pair(AGREED))


def test_a_confirmation_stays_a_retained_agreement(data):
    out = run(readers=gate.pair())
    assert out.changed and out.record["derivation"]["cited_change"]["rule"] == RETAINED_RULE


def test_an_earlier_logged_agreement_on_the_same_value_counts_with_the_new_one(data):
    # The logged attempt that was refused (value_differs) and a later read agree: no
    # disagreement in the epoch, so the later read corrects.
    gate.refused("value_differs", readers=gate.pair(AGREED))
    out = run()
    assert out.changed and len(gate.Data.attempts(data)) == 2


@pytest.mark.parametrize("readers", [
    [gate.reader("codex", "gpt-5", AGREED), gate.reader("codex-2", "openai", AGREED)],
    [gate.reader("claude", "claude-sonnet-5", AGREED), gate.reader("c2", "anthropic", AGREED)],
])
def test_same_family_readers_are_refused_before_any_read(data, readers):
    request = gate.serve()
    refused("reader_families_not_distinct", readers=readers, request=request)
    assert request.calls == [] and data.attempts() == []


def test_a_disagreement_in_the_epoch_blocks_the_correction(data):
    gate.seed(data, complete=True, agreed=False, readers=[
        {"reader_id": "codex", "family": "gpt-5", "version": "1", "value": AGREED},
        {"reader_id": "claude", "family": "claude-sonnet-5", "version": "1", "value": ["text"]}])
    refused("prior_attempt_disagreed")


def test_an_answer_for_another_value_in_an_incomplete_attempt_blocks(data):
    gate.seed(data, readers=[{"reader_id": "codex", "family": "gpt-5", "version": "1",
                              "value": ["video"]}])
    refused("prior_attempt_disagreed")


def test_an_earlier_agreement_on_another_value_blocks(data):
    gate.refused("value_differs", readers=gate.pair(["video"]))
    refused("prior_attempt_disagreed")


def _held(data, value):
    data.log_rows = [verification("fact", f"{gate.SUBJECT}#{gate.FACET}", "mismatch",
                                  day="2026-11-01", value=value)]
    data.write()


@pytest.mark.parametrize("value", [gate.FILED, AGREED])
def test_a_held_fact_is_refused_before_any_read(data, value):
    _held(data, value)
    request = gate.serve()
    refused("quarantined", request=request)
    assert request.calls == [] and data.attempts() == []


def test_a_licence_fact_is_not_corrected(data):
    data.sources[0]["kind"] = "provider_terms"
    data.fact.update(facet="licence.user_cap", value=1000, id=f"{gate.SUBJECT}#licence.user_cap")
    data.write()
    page = b"# Widget terms\n\nThe terms set out how many monthly users a licensee may serve.\n"
    out = refused("value_differs", facet="licence.user_cap", readers=gate.pair(2000),
                  request=gate.serve({gate.URL: page}))
    assert "licence" in out.detail


def test_a_ruled_fact_is_not_corrected(data):
    data.fact["derivation"] = {"owner_ruling": {"rule": "owner-ruling@1"}}
    data.write()
    assert not run().changed


def test_a_cite_only_page_is_still_left_to_cited_change(data):
    refused("host_cite_only", source_id="docs", request=gate.serve({gate.CITE_ONLY: gate.PAGE}))


def test_the_gate_asks_the_builds_own_test_of_the_record_as_filed(data):
    out = run()
    fact = filed_fact(data.fact, out.record)
    log = AttemptLog.read(data.root / ATTEMPTS_FILE)
    sources = {s["id"]: s["url"] for s in data.sources}
    today = datetime.now(UTC).date()
    assert correction_problem(fact, gate.SUBJECT, log=log, verdicts={}, sources=sources,
                              cutoff=today) is None


def test_reread_of_a_correction_stays_on_the_correction_rule(data):
    file_record(data, run().record)
    assert rr(gate.pair(AGREED)).outcome == "current"
    changed = gate.PAGE + b"More text.\n"
    out = rr(gate.pair(AGREED), changed)
    assert out.outcome == "confirmed", (out.reason, out.detail)
    assert out.record["derivation"]["cited_change"]["rule"] == RULE
    file_record(data, out.record)
    out = rr(gate.pair(["text"]), changed + b"x")
    assert out.outcome == "changed" and out.record["value"] == ["text"]
    # A caller's transport re-reads nothing into a correction.
    file_record(data, out.record)
    fact = {"subject": gate.SUBJECT, "facet": gate.FACET}
    out = reread(fact, source_id="readme", readers=gate.pair(["text"]),
                 request=gate.serve({gate.URL: changed + b"xy"}))
    assert out.outcome == "flagged" and out.reason == "correction_not_admitted"


def test_the_gates_correction_is_served_as_cited_by_the_build_and_the_site(data):
    from decision.snapshot import build_snapshot, collect_repo, load_built_snapshot
    from pipeline.load import load_models

    file_record(data, run().record)
    (data.root / "benchmarks").mkdir(exist_ok=True)
    index = load_built_snapshot(build_snapshot(collect_repo(data.root)))
    shown = index.fact(gate.SUBJECT, gate.FACET)
    assert shown.state == "known" and sorted(shown.value) == sorted(AGREED)
    record = index.record(shown.record_id)
    assert record["verification"] is None and record["citation"]["status"] == "cited"
    assert "derivation" not in record
    (card,) = load_models(data.root)
    (cited,) = card.cited_facts
    assert cited["citation"]["status"] == "cited" and "derivation" not in cited
    # The same card with the agreement gone from the log, and a cite-only reference added
    # beside it: withheld on the site, out of the build.
    (data.root / ATTEMPTS_FILE).write_text("")
    data.fact["sources"].append({"source_id": "docs", "snapshot_ref": "sha256:" + "1" * 64,
                                 "cited_regions": ["model-spec"]})
    data.write()
    (card,) = load_models(data.root)
    assert card.cited_facts == [] and card.withheld_facets == (gate.FACET,)
    index = load_built_snapshot(build_snapshot(collect_repo(data.root)))
    assert index.fact(gate.SUBJECT, gate.FACET).state != "known"


# --- the build: a correction enters only through its logged agreement -----------------------------

MID, FACET = "lab/alpha", "model.max_output_tokens"
URL = "https://lab.example.com/docs/models"  # src-lab-docs: a host that retains copies
PAGE, TEXT, PROMPT, REGION = "3" * 64, "a" * 64, "4" * 64, "5" * 64
AT = "2026-10-10T09:00:00+00:00"
FILED, VALUE = 4096, 8192
TODAY = date(2026, 10, 19)
OLD = verification("fact", f"{MID}#{FACET}", "verified", day="2026-09-20", value=FILED)


def agreement(epoch="initial", *, at=AT, values=(VALUE, VALUE), families=("openai", "anthropic"),
              facet=FACET, **kw):
    return {"subject": MID, "facet": facet, "epoch": epoch, "url": URL, "complete": True,
            "agreed": values[0] == values[1], "agreed_value": values[0], "harness": True,
            "page_sha256": PAGE, "text_sha256": TEXT, "prompt_sha256": PROMPT, "at": at,
            "region_sha256": REGION, "own_fetch": True,
            "readers": [{"reader_id": "a", "family": families[0], "version": "1",
                         "value": values[0]},
                        {"reader_id": "b", "family": families[1], "version": "1",
                         "value": values[1]}], **kw}


def raw(attempt):
    """The attempt's line as the gate's ``log_attempt`` writes it."""
    return json.dumps(attempt, sort_keys=True, ensure_ascii=False)


def corrected_row(attempt, *, value=VALUE, facet=FACET, line=None):
    from tests.snapshot_records import fact

    row = fact("model", MID, facet, value, source="src-lab-docs", outcome=None)
    row["sources"] = [{"source_id": "src-lab-docs",
                       "snapshot_ref": f"sha256:{attempt['page_sha256']}",
                       "retrieved_at": attempt["at"], "cited_regions": ["r1"]}]
    row["derivation"] = {"cited_change": {
        "rule": RULE, "sha256": attempt["page_sha256"], "text_sha256": attempt["text_sha256"],
        "url": attempt["url"], "previous_value": FILED, "epoch": attempt["epoch"],
        "agreement": line_hash(raw(attempt) if line is None else line),
        "region_sha256": attempt.get("region_sha256"),
        "readers": [{**r, "prompt_sha256": attempt["prompt_sha256"]} for r in attempt["readers"]]}}
    return row


CITE = "https://www.perplexity.ai/pro"  # a cite-only host


def build(row, attempts, log=(OLD,), *, as_of=TODAY, extra_sources=None):
    from decision.snapshot import SnapshotInputs, build_snapshot, load_built_snapshot

    from tests.snapshot_records import SOURCES, model

    inputs = SnapshotInputs(models=[model(MID, facts=[row])],
                            sources={**SOURCES, **(extra_sources or {})},
                            verifications=list(log),
                            cited_attempt_lines=[a if isinstance(a, str) else raw(a)
                                                 for a in attempts])
    return load_built_snapshot(build_snapshot(inputs, as_of=as_of))


def admitted(index, value=VALUE, facet=FACET):
    shown = index.fact(MID, facet)
    return shown.state == "known" and shown.value == value


def test_the_build_serves_a_correction_as_cited_never_as_verified():
    attempt = agreement()
    index = build(corrected_row(attempt), [attempt])
    assert admitted(index)
    record = index.record(index.fact(MID, FACET).record_id)
    assert record["verification"] is None and record["citation"]["status"] == "cited"
    assert [s["source_id"] for s in record["citation"]["sources"]] == ["src-lab-docs"]
    served = json.dumps(record)
    assert "two-readers" not in served and "agreement" not in served and "derivation" not in served


def test_a_correction_without_its_logged_agreement_is_not_admitted():
    attempt = agreement()
    assert not admitted(build(corrected_row(attempt), []))


@pytest.mark.parametrize("forge", ["respelled", "never_logged", "not_harness", "no_hashes",
                                   "edited_value", "edited_reader"])
def test_a_forged_line_admits_nothing(forge):
    attempt = agreement()
    row, lines = corrected_row(attempt), [raw(attempt)]
    if forge == "respelled":  # the same fields in another spelling: not the logged line
        row = corrected_row(attempt, line=json.dumps(attempt))
    elif forge == "never_logged":  # hashes recomputed for a read that was never logged
        row = corrected_row(agreement(at="2026-10-12T09:00:00+00:00"))
    elif forge == "not_harness":
        seeded = agreement(harness=False)
        row, lines = corrected_row(seeded), [raw(seeded)]
    elif forge == "no_hashes":
        seeded = agreement(prompt_sha256="")
        row, lines = corrected_row(seeded), [raw(seeded)]
    elif forge == "edited_value":
        row["value"] = 16384
    elif forge == "edited_reader":
        row["derivation"]["cited_change"]["readers"][1]["family"] = "google"
    assert not admitted(build(row, lines)) and not admitted(build(row, lines), value=16384)


def test_same_family_readers_correct_nothing_in_the_build():
    attempt = agreement(families=("openai", "openai"))
    assert not admitted(build(corrected_row(attempt), [attempt]))
    attempt = agreement(families=("claude-sonnet-5", "anthropic"))
    assert not admitted(build(corrected_row(attempt), [attempt]))


def test_an_agreement_from_an_earlier_epoch_corrects_nothing():
    attempt = agreement()
    later = agreement("reread:" + "b" * 64, at="2026-10-11T09:00:00+00:00", values=(FILED, FILED),
                      text_sha256="b" * 64)
    assert not admitted(build(corrected_row(attempt), [attempt, later]))
    # An attempt in the corrected record's own re-read epoch is its rolling re-read: it stands.
    own = agreement("reread:" + TEXT, at="2026-10-11T09:00:00+00:00")
    assert admitted(build(corrected_row(attempt), [attempt, own]))


@pytest.mark.parametrize("other", ["disagreed", "other_value", "incomplete_other"])
def test_a_disagreement_in_the_epoch_undoes_the_correction(other):
    attempt = agreement()
    if other == "disagreed":
        extra = agreement(values=(VALUE, FILED), at="2026-10-09T09:00:00+00:00")
    elif other == "other_value":
        extra = agreement(values=(FILED, FILED), at="2026-10-09T09:00:00+00:00")
    else:
        extra = {**agreement(at="2026-10-09T09:00:00+00:00"), "complete": False, "agreed": None,
                 "readers": [{"reader_id": "a", "family": "openai", "version": "1",
                              "value": FILED}]}
        extra.pop("agreed_value")
    for lines in ([extra, attempt], [attempt, extra]):
        assert not admitted(build(corrected_row(attempt), lines))


def test_a_licence_fact_or_identity_field_is_never_corrected():
    assert owner_only("licence.user_cap") and owner_only("offering.api_model_id")
    assert not owner_only(FACET)
    attempt = agreement(facet="licence.user_cap", values=(2000, 2000))
    row = corrected_row(attempt, value=2000, facet="licence.user_cap")
    old = verification("fact", f"{MID}#licence.user_cap", "verified", value=FILED)
    assert not admitted(build(row, [attempt], log=(old,)), value=2000, facet="licence.user_cap")


@pytest.mark.parametrize("held", ["new_value", "third_value", "inline"])
def test_a_held_fact_is_not_corrected(held):
    # A mismatch on the replaced value no longer holds a correction (MODEL-491 E2, below); a
    # verdict on the corrected value, on a third value, or an ``unreachable`` still does.
    attempt = agreement()
    row, log = corrected_row(attempt), [OLD]
    if held == "new_value":
        log.append(verification("fact", f"{MID}#{FACET}", "mismatch", day="2026-10-01",
                                value=VALUE))
    elif held == "third_value":
        log.append(verification("fact", f"{MID}#{FACET}", "mismatch", day="2026-10-01",
                                value=16384))
    else:
        row["verification"] = verification("fact", f"{MID}#{FACET}", "unreachable",
                                            day="2026-10-01", value=FILED)
    assert not admitted(build(row, [attempt], log=log))


def test_a_ruled_or_cleared_record_is_not_a_correction():
    attempt = agreement()
    log = AttemptLog([raw(attempt)])
    sources = {"src-lab-docs": URL}
    row = corrected_row(attempt)
    assert correction_problem(row, MID, log=log, verdicts={}, sources=sources, cutoff=TODAY) \
        is None
    ruled = copy.deepcopy(row)
    ruled["derivation"]["owner_ruling"] = {"rule": "owner-ruling@1"}
    cleared = copy.deepcopy(row)
    cleared["derivation"]["cited_change"]["clearing_epoch"] = "initial"
    for record in (ruled, cleared):
        assert correction_problem(record, MID, log=log, verdicts={}, sources=sources,
                                  cutoff=TODAY) is not None


def test_an_agreement_after_the_builds_cutoff_corrects_nothing():
    attempt = agreement()
    assert not admitted(build(corrected_row(attempt), [attempt], as_of=date(2026, 10, 9)))
    assert admitted(build(corrected_row(attempt), [attempt], as_of=date(2026, 10, 10)))


def test_a_correction_on_a_cite_only_page_takes_the_cite_only_path():
    attempt = {**agreement(), "url": "https://www.perplexity.ai/pro"}
    row = corrected_row(attempt)
    log = AttemptLog([raw(attempt)])
    assert correction_problem(row, MID, log=log, verdicts={},
                              sources={"src-lab-docs": attempt["url"]}, cutoff=TODAY) \
        == "the agreement did not read a page whose host retains copies"


def test_a_failed_correction_stays_out_whatever_else_would_admit_it():
    # Review fix 1: a corrected value is served only through the shared test. A verified verdict
    # on it, or a cite-only reference added beside it, never stands in for the test.
    attempt = agreement()
    row = corrected_row(attempt)
    assert is_correction(row)
    verified = verification("fact", f"{MID}#{FACET}", "verified", day="2026-10-12", value=VALUE)
    assert not admitted(build(row, [], log=(OLD, verified)))
    beside = copy.deepcopy(row)
    beside["sources"].append({"source_id": "src-cite", "snapshot_ref": "sha256:" + "6" * 64,
                              "cited_regions": ["r1"]})
    assert not admitted(build(beside, [], extra_sources={"src-cite": CITE}))
    assert admitted(build(beside, [attempt], extra_sources={"src-cite": CITE}))


def test_a_self_asserted_harness_row_is_not_the_gates_own_fetch():
    # Review fix 2: ``harness: true`` alone is never enough.
    for forged in (agreement(own_fetch=None), agreement(region_sha256=None),
                   agreement(region_sha256="z" * 64)):
        forged = {k: v for k, v in forged.items() if v is not None}
        assert not admitted(build(corrected_row(forged), [forged]))
    other = agreement()
    row = corrected_row(other)
    row["derivation"]["cited_change"]["region_sha256"] = "6" * 64  # not the region logged
    assert not admitted(build(row, [other]))


def test_a_copied_stale_agreement_does_not_move_the_scan_forward():
    # Review fix 3: only the first occurrence counts, and its epoch must be the current one.
    attempt = agreement()
    later = agreement("reread:" + "b" * 64, at="2026-10-11T09:00:00+00:00", values=(FILED, FILED),
                      text_sha256="b" * 64)
    assert not admitted(build(corrected_row(attempt), [attempt, later, attempt]))


def test_a_copied_older_epoch_line_does_not_suppress_a_valid_correction():
    # Review round 2: a byte-identical copy of an older epoch's line, appended after the
    # agreement, is that older line, not a later attempt.
    older = agreement("reread:" + "c" * 64, at="2026-10-01T09:00:00+00:00",
                      values=(FILED, FILED), text_sha256="c" * 64)
    attempt = agreement()
    assert admitted(build(corrected_row(attempt), [older, attempt]))
    assert admitted(build(corrected_row(attempt), [older, attempt, older]))
    # A new line in another epoch after the agreement still undoes it.
    fresh = {**older, "at": "2026-10-11T09:00:00+00:00"}
    assert not admitted(build(corrected_row(attempt), [older, attempt, fresh]))


def test_the_cutoff_is_compared_in_utc():
    # Review fix 4: 02:00 at +05:00 on the 10th is the 9th in UTC; 22:00 at -05:00 on the 9th
    # is the 10th.
    east = agreement(at="2026-10-10T02:00:00+05:00")
    assert admitted(build(corrected_row(east), [east], as_of=date(2026, 10, 9)))
    west = agreement(at="2026-10-09T22:00:00-05:00")
    assert not admitted(build(corrected_row(west), [west], as_of=date(2026, 10, 9)))


def test_every_identity_facet_in_the_registry_is_the_owners():
    # Review fix 5: read from the registry (``identity: true``), never a hand list.
    import yaml as _yaml
    from decision.registry import REGISTRY_DIR

    entries = _yaml.safe_load((REGISTRY_DIR / "facets.yaml").read_text())["facets"]
    identity = {e["id"] for e in entries if e.get("identity") is True}
    assert {"offering.provider", "offering.api_model_id", "offering.router_slug"} <= identity
    assert all(owner_only(f) for f in identity)
    assert not owner_only("model.max_output_tokens") and owner_only("not.a_facet")
    row = corrected_row(agreement(facet="offering.provider", values=("acme", "acme")),
                        value="acme", facet="offering.provider")
    log = AttemptLog([raw(agreement(facet="offering.provider", values=("acme", "acme")))])
    assert correction_problem(row, MID, log=log, verdicts={}, sources={"src-lab-docs": URL},
                              cutoff=TODAY) == "a licence fact or an identity field is the owner's"


def test_the_gate_corrects_only_from_its_own_fetch(data):
    out = run(caller=True)
    assert out.reason == "correction_not_admitted" and "own" in out.detail
    assert data.attempts()[-1].get("own_fetch") is None
    assert run().changed and data.attempts()[-1]["own_fetch"] is True


# --- MODEL-491 E2: a mismatch on the replaced value does not hold a correction -------------------

def _old_mismatch(day="2026-10-01", value=FILED, outcome="mismatch"):
    return verification("fact", f"{MID}#{FACET}", outcome, day=day, value=value)


def test_a_mismatch_on_the_replaced_value_no_longer_holds_the_correction():
    attempt = agreement()
    index = build(corrected_row(attempt), [attempt], log=[_old_mismatch()])
    assert admitted(index)
    record = index.record(index.fact(MID, FACET).record_id)
    assert record["verification"] is None and record["citation"]["status"] == "cited"
    log = AttemptLog([raw(attempt)])
    verdicts = {("fact", f"{MID}#{FACET}", _old_mismatch()["target"]["value_hash"]):
                ("2026-10-01", 1, _old_mismatch())}
    assert correction_problem(corrected_row(attempt), MID, log=log, verdicts=verdicts,
                              sources={"src-lab-docs": URL}, cutoff=TODAY) is None


@pytest.mark.parametrize("bypass", ["unreachable", "after_agreement", "previous_is_value",
                                    "no_previous", "not_a_correction"])
def test_only_an_earlier_mismatch_on_the_replaced_value_is_set_aside(bypass):
    attempt = agreement()
    row, log = corrected_row(attempt), [_old_mismatch()]
    if bypass == "unreachable":  # an unreachable source says nothing about the old value
        log = [_old_mismatch(outcome="unreachable")]
    elif bypass == "after_agreement":  # a verdict after the agreement is not on what it replaced
        log = [_old_mismatch(day="2026-10-11")]
    elif bypass == "previous_is_value":  # a block naming the corrected value releases nothing
        row["derivation"]["cited_change"]["previous_value"] = VALUE
        log.append(_old_mismatch(value=VALUE))
    elif bypass == "no_previous":
        row["derivation"]["cited_change"].pop("previous_value")
    else:  # a cite-only rule-15 change or a confirmation is not a correction
        row["derivation"]["cited_change"]["rule"] = RETAINED_RULE
    assert not admitted(build(row, [attempt], log=log))


def test_a_forged_previous_value_releases_only_a_verdict_older_than_the_agreement():
    # A block may name any previous value; only a mismatch on it from before the logged agreement
    # is set aside, and never one on the value the fact now has.
    attempt = agreement()
    row = corrected_row(attempt)
    row["derivation"]["cited_change"]["previous_value"] = 16384
    later = _old_mismatch(day="2026-10-12", value=16384)
    assert not admitted(build(row, [attempt], log=[later]))


# --- MODEL-491 E1: a rule-16 confirmation is served as cited -------------------------------------

def confirmed_row(attempt, *, value=FILED, facet=FACET):
    row = corrected_row(attempt, value=value, facet=facet)
    block = row["derivation"]["cited_change"]
    for key in ("epoch", "agreement", "region_sha256"):
        block.pop(key)
    block.update(rule=RETAINED_RULE, previous_value=value)
    return row


def confirming(**kw):
    """A confirmation's attempt: the filed value, logged before ``own_fetch`` existed."""
    attempt = agreement(values=kw.pop("values", (FILED, FILED)), **kw)
    attempt.pop("own_fetch")
    attempt.pop("region_sha256")
    return attempt


def test_a_confirmation_is_served_as_cited_when_nothing_else_admits_it():
    attempt = confirming()
    row = confirmed_row(attempt)
    assert is_confirmation(row) and not is_correction(row)
    assert not admitted(build(row, [], log=()), value=FILED)  # no logged agreement: nothing
    index = build(row, [attempt], log=())
    assert admitted(index, value=FILED)
    record = index.record(index.fact(MID, FACET).record_id)
    assert record["verification"] is None and record["citation"]["status"] == "cited"
    assert [s["source_id"] for s in record["citation"]["sources"]] == ["src-lab-docs"]


def test_the_verified_path_wins_over_a_confirmation():
    attempt = confirming()
    index = build(confirmed_row(attempt), [attempt], log=(OLD,))
    assert admitted(index, value=FILED)
    record = index.record(index.fact(MID, FACET).record_id)
    assert record["verification"] is not None and record.get("citation") is None
    assert confirmation_citation(confirmed_row(attempt), MID, log=AttemptLog([raw(attempt)]),
                                 verdicts={("fact", f"{MID}#{FACET}",
                                            OLD["target"]["value_hash"]): ("2026-09-20", 1, OLD)},
                                 sources={"src-lab-docs": URL}, cutoff=TODAY) is None


@pytest.mark.parametrize("bypass", [
    "same_family", "unknown_family", "other_value", "disagreed", "incomplete_other",
    "later_epoch", "held_same", "held_other", "inline_unreachable", "licence",
    "cite_only", "after_cutoff", "not_harness", "no_hashes", "edited_sha", "edited_reader",
    "edited_value", "ruled", "cleared", "not_disclosed", "respelled_other_subject"])
def test_a_confirmation_that_fails_the_shared_test_admits_nothing(bypass):
    attempt, lines, log, sources = confirming(), None, [], None
    facet, value = FACET, FILED
    if bypass == "same_family":
        attempt = confirming(families=("openai", "openai"))
    elif bypass == "unknown_family":
        attempt = confirming(families=("unknown", "anthropic"))
    elif bypass == "other_value":  # the readers agreed on another value than the filed one
        attempt = confirming(values=(VALUE, VALUE))
    elif bypass == "disagreed":
        lines = [confirming(values=(FILED, VALUE), at="2026-10-09T09:00:00+00:00"), attempt]
    elif bypass == "incomplete_other":
        extra = {**confirming(at="2026-10-09T09:00:00+00:00"), "complete": False, "agreed": None,
                 "readers": [{"reader_id": "a", "family": "openai", "version": "1",
                              "value": VALUE}]}
        extra.pop("agreed_value")
        lines = [attempt, extra]
    elif bypass == "later_epoch":
        lines = [attempt, confirming(epoch="reread:" + "b" * 64, text_sha256="b" * 64,
                                     at="2026-10-11T09:00:00+00:00")]
    elif bypass == "held_same":
        log = [_old_mismatch(value=FILED)]
    elif bypass == "held_other":
        log = [_old_mismatch(value=VALUE)]
    elif bypass == "licence":
        facet, value = "licence.user_cap", 2000
        attempt = confirming(facet=facet, values=(2000, 2000))
    elif bypass == "cite_only":
        attempt = {**confirming(), "url": CITE}
        sources = {"src-lab-docs": CITE}
    elif bypass == "not_harness":
        attempt = confirming(harness=False)
    elif bypass == "no_hashes":
        attempt = confirming(prompt_sha256="")
    row = confirmed_row(attempt, value=value, facet=facet)
    block = row["derivation"]["cited_change"]
    if bypass == "inline_unreachable":
        row["verification"] = _old_mismatch(outcome="unreachable")
    elif bypass == "after_cutoff":
        pass
    elif bypass == "edited_sha":
        block["sha256"] = "6" * 64
    elif bypass == "edited_reader":
        block["readers"][1]["family"] = "google"
    elif bypass == "edited_value":
        row["value"] = 2048
    elif bypass == "ruled":
        row["derivation"]["owner_ruling"] = {"rule": "owner-ruling@1"}
    elif bypass == "cleared":
        block["clearing_epoch"] = "initial"
    elif bypass == "not_disclosed":
        row.update(state="not_disclosed", value=None)
    elif bypass == "respelled_other_subject":
        attempt = {**attempt, "subject": "lab/beta"}
    lines = lines or [attempt]
    as_of = date(2026, 10, 9) if bypass == "after_cutoff" else TODAY
    problem = confirmation_problem(row, MID, log=AttemptLog([raw(a) for a in lines]),
                                   verdicts=_Compiler._verification_log(log),
                                   sources=sources or {"src-lab-docs": URL},
                                   cutoff=as_of)
    assert problem is not None
    if bypass == "cite_only":
        return  # a cite-only reference is rule 14's own cited path, not this one
    shown = build(row, lines, log=log, as_of=as_of).fact(MID, facet)
    assert not (shown.state == "known" and shown.value == row.get("value"))


def test_the_gate_the_build_and_the_site_take_one_decision(tmp_path):
    # The site loader shows a confirmation as cited exactly when the build serves it so.
    from pipeline.load import _confirmed_citation

    attempt = confirming()
    row = confirmed_row(attempt)
    log = AttemptLog([raw(attempt)])
    sources = {"src-lab-docs": URL}
    held = _Compiler._verification_log([_old_mismatch()])
    for verdicts, served in (({}, True), (held, False)):
        shown = _confirmed_citation(row, MID, (log, verdicts, TODAY), sources)
        assert (shown is not None) is served
        assert admitted(build(row, [attempt], log=[] if not verdicts else [_old_mismatch()]),
                        value=FILED) is served


def test_the_gate_refuses_a_confirmation_the_build_would_not_serve(data, monkeypatch):
    # The gate files a confirmation only when the build's own test admits it as filed.
    import decision.retained_correction as rc

    monkeypatch.setattr(rc, "confirmation_problem", lambda *a, **k: "a refusal from the test")
    out = run(readers=gate.pair())
    assert out.outcome == "refused" and out.reason == "confirmation_not_admitted"
    assert out.record is None


def test_a_card_without_a_stated_id_is_ranked_on_its_location_id():
    # The site loader reads the card as written; the build gives it its location id. Both must
    # see the same verified verdict, so the verified path wins on both.
    attempt = confirming()
    row = confirmed_row(attempt)
    row.pop("id")
    verdicts = _Compiler._verification_log([OLD])
    assert confirmation_citation(row, MID, log=AttemptLog([raw(attempt)]), verdicts=verdicts,
                                 sources={"src-lab-docs": URL}, cutoff=TODAY) is None
