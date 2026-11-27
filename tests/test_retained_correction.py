"""MODEL-573: a logged two-reader agreement may correct a served value read from a retaining page.

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
    correction_problem,
    filed_fact,
    is_correction,
    owner_only,
)

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


@pytest.mark.parametrize("held", ["new_value", "old_value", "inline"])
def test_a_held_fact_is_not_corrected(held):
    attempt = agreement()
    row, log = corrected_row(attempt), [OLD]
    if held == "new_value":
        log.append(verification("fact", f"{MID}#{FACET}", "mismatch", day="2026-10-01",
                                value=VALUE))
    elif held == "old_value":
        log = [verification("fact", f"{MID}#{FACET}", "mismatch", day="2026-10-01", value=FILED)]
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
