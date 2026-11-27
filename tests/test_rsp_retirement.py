"""MODEL-491: retained-source-proof@1 stops counting, and a label matcher's "verified" on a null
value is no verification (E5).

Every build from the private data retires both (``SnapshotInputs.retire_rsp``, set by
``collect_repo`` from the checkout's ``.engine-pin``). The engine's frozen public image keeps
the rule as filed. Every record here is synthetic.
"""

from __future__ import annotations

import copy
from datetime import date
from pathlib import Path

import pytest
from decision.model import Verification, verification_row_counts
from decision.snapshot import SnapshotInputs, build_snapshot, load_built_snapshot

from tests.snapshot_records import SOURCES, fact, model, verification

MID, FACET = "lab/alpha", "model.context_window"
FID = f"{MID}#{FACET}"
NULL_FACET = "feature.tool_calling"
NULL_FID = f"{MID}#{NULL_FACET}"


def counts(row, *, retire=True):
    """The private-data rule (``retire=True``); ``retire=False`` is the public image's."""
    return verification_row_counts(row, retire=retire)


def row(method, *, outcome="verified", day="2026-09-25", value=128000, fid=FID,
        agent="codex-model-143"):
    v = verification("fact", fid, outcome, day=day, value=value)
    v["method"] = method
    v["verifier"] = {**v["verifier"], "method": method}
    v["collector"] = {**v["collector"], "agent": agent}
    return v


def shown(facts, log, *, retire=True, sources=None):
    inputs = SnapshotInputs(models=[model(MID, facts=facts)],
                            sources={**SOURCES, **(sources or {})},
                            verifications=list(log), retire_rsp=retire)
    return load_built_snapshot(build_snapshot(inputs))


def fact_on_log(facet=FACET, value=128000, state="known"):
    return fact("model", MID, facet, value, state=state, outcome=None)


def test_a_retained_source_proof_row_no_longer_verifies():
    proof = row("retained-source-proof@1")
    index = shown([fact_on_log()], [proof])
    assert index.fact(MID, FACET).state != "known"
    # The engine's frozen public image keeps the rule as filed.
    assert shown([fact_on_log()], [proof], retire=False).fact(MID, FACET).state == "known"
    # A real reading of the same value still verifies it.
    assert shown([fact_on_log()], [row("key-value-match@1")]).fact(MID, FACET).state == "known"


def test_a_retained_source_proof_row_no_longer_displaces_a_mismatch():
    log = [row("key-value-match@1", outcome="mismatch"), row("retained-source-proof@1")]
    assert shown([fact_on_log()], log).fact(MID, FACET).state != "known"
    assert shown([fact_on_log()], log, retire=False).fact(MID, FACET).state == "known"


def test_the_retired_method_is_found_on_the_row_or_its_verifier(tmp_path, monkeypatch):
    proof = row("retained-source-proof@1")
    by_verifier = copy.deepcopy(proof)
    by_verifier["method"] = "multi-source-primary-audit@2"
    for r in (proof, by_verifier):
        assert not counts(r)
        assert counts(r, retire=False)
        # ``Verification.counts`` is the public rule; a private reader passes retire=True.
        assert Verification.model_validate(r).counts


@pytest.mark.parametrize("matcher", ["model-page-label-match@1", "key-value-match@1"])
def test_a_label_matcher_never_verifies_a_null_value(matcher):
    # E5: the round-1 label matchers "verified" a not_disclosed value on a page that names the
    # model; that shows nothing about a value the page does not state.
    null = fact_on_log(NULL_FACET, None, state="not_disclosed")
    label = row(matcher, value=None, fid=NULL_FID)
    assert not counts(label)
    assert shown([null], [label]).fact(MID, NULL_FACET).state != "not_disclosed"
    assert shown([null], [label], retire=False).fact(MID, NULL_FACET).state == "not_disclosed"
    # The same matcher on a stated value still counts, and so does another reader on a null.
    assert counts(row(matcher, value=128000))
    other = row("absence-reading@1", value=None, fid=NULL_FID)
    assert counts(other)
    assert shown([null], [other]).fact(MID, NULL_FACET).state == "not_disclosed"


@pytest.mark.parametrize("change", ["later_day", "other_collector"])
def test_a_later_absence_reading_by_a_label_matcher_still_counts(change):
    # E5 is MODEL-143 round 1 only: a later absence reading by the same readers is not affected.
    kw = {"day": "2026-11-24"} if change == "later_day" else {"agent": "model-491-builder"}
    for matcher in ("model-page-label-match@1", "key-value-match@1"):
        assert counts(row(matcher, value=None, fid=NULL_FID, **kw))


@pytest.mark.parametrize("matcher", ["model-page-label-match@1", "key-value-match@1",
                                     "table-header-match@1"])
def test_a_round_one_null_label_row_counts_neither_way(matcher):
    # E5, both directions: round 1 filed null claims, so its label matcher's null rows show
    # nothing. A "mismatch" on null no longer holds a fact whose value is now stated, and a
    # "verified" on null no longer admits a not_disclosed one.
    mismatch = row(matcher, outcome="mismatch", value=None, fid=FID)
    assert not counts(mismatch)
    # A cited fact is held by a verdict on any value of its ids: before E5 the round-1 null
    # mismatch held it, now it does not.
    stated = fact_on_log()
    stated["sources"] = [{"source_id": "src-cite", "snapshot_ref": "sha256:" + "6" * 64,
                          "cited_regions": ["page"], "retrieved_at": "2026-10-10T09:00:00+00:00"}]
    cite = {"src-cite": "https://www.perplexity.ai/pro"}
    assert shown([stated], [mismatch], sources=cite).fact(MID, FACET).state == "known"
    assert shown([stated], [mismatch], sources=cite, retire=False).fact(
        MID, FACET).state != "known"
    null = fact_on_log(NULL_FACET, None, state="not_disclosed")
    assert shown([null], [row(matcher, value=None, fid=NULL_FID)]).fact(
        MID, NULL_FACET).state != "not_disclosed"
    # A later reader's mismatch on null still holds.
    later = row(matcher, outcome="mismatch", value=None, fid=FID, day="2026-11-24")
    assert counts(later)


def test_a_same_family_verified_row_still_does_not_count():
    same = row("key-value-match@1")
    same["verifier"]["model_family"] = same["collector"]["model_family"]
    assert not counts(same) and not counts(same, retire=False)


def test_collect_repo_retires_only_when_its_caller_says_the_data_is_private(tmp_path,
                                                                           monkeypatch):
    # Codex review 4: the switch is the caller's explicit argument. A stray ``.engine-pin`` or a
    # data directory in the environment turns nothing on.
    from decision.snapshot import collect_repo

    (tmp_path / "models").mkdir()
    (tmp_path / ".engine-pin").write_text("0" * 40 + "\n")
    monkeypatch.setenv("MODELSPEC_DATA_DIR", str(tmp_path))
    assert collect_repo(tmp_path).retire_rsp is False
    assert collect_repo(tmp_path, private=True).retire_rsp is True


def test_a_round_one_table_header_mismatch_on_null_no_longer_holds_a_stated_fact():
    # Symmetric E5 drops round 1's null "verified" label rows, which had masked earlier round-1
    # table-header mismatches on the same null key. A table header match is a label matcher
    # too: its null mismatch shows only that the page states a value, so it holds nothing.
    stated = fact_on_log()
    stated["sources"] = [{"source_id": "src-cite", "snapshot_ref": "sha256:" + "6" * 64,
                          "cited_regions": ["page"], "retrieved_at": "2026-10-10T09:00:00+00:00"}]
    cite = {"src-cite": "https://www.perplexity.ai/pro"}
    log = [row("table-header-match@1", outcome="mismatch", value=None),
           row("key-value-match@1", value=None)]
    assert shown([stated], log, sources=cite).fact(MID, FACET).state == "known"
    # Another method's round-1 null row still counts.
    other = row("structured-row-match@1", outcome="mismatch", value=None)
    assert counts(other)


def test_the_counting_rule_takes_the_switch_from_its_caller_only(tmp_path, monkeypatch):
    # Nothing looks the switch up: neither the environment nor a file turns it on.
    proof = row("retained-source-proof@1")
    (tmp_path / ".engine-pin").write_text("0" * 40 + "\n")
    monkeypatch.setenv("MODELSPEC_DATA_DIR", str(tmp_path))
    assert verification_row_counts(proof) and Verification.model_validate(proof).counts
    assert not verification_row_counts(proof, retire=True)


def test_the_verification_log_counts_by_its_callers_rule(tmp_path):
    # Codex review 5: VerificationLog.latest (the accuracy audit, the drafters, the price
    # re-read) counts by the rule its caller states, so a private reader never accepts a
    # retired row.
    import json

    from decision.verify import VerificationLog

    (tmp_path / "log.jsonl").write_text(json.dumps(row("retained-source-proof@1")) + "\n")
    assert len(VerificationLog(tmp_path).latest()) == 1  # the public rule, as filed
    assert VerificationLog(tmp_path, private=True).latest() == {}
    assert VerificationLog(tmp_path, private=True).requarantined() != []


def test_the_private_accuracy_audit_reads_the_private_rule(tmp_path, monkeypatch):
    import scripts.accuracy as accuracy

    seen = []

    class Log:
        def __init__(self, directory, *, private=False):
            seen.append((Path(directory).parent.name, private))

        def latest(self):
            return {}

    import decision.verify as verify

    monkeypatch.setattr(verify, "VerificationLog", Log)
    for name in ("public", "private"):
        for rel in ("verification/log.jsonl", "verification/queue/events.jsonl"):
            (tmp_path / name / rel).parent.mkdir(parents=True, exist_ok=True)
            (tmp_path / name / rel).write_text("")
    accuracy._private_corrections(tmp_path / "public", tmp_path / "private", date(2026, 11, 27))
    assert ("public", False) in seen and ("private", False) in seen  # main's rule by default
    seen.clear()
    accuracy._private_corrections(tmp_path / "public", tmp_path / "private", date(2026, 11, 27),
                                  rules=True)  # --private-data
    assert ("public", False) in seen and ("private", True) in seen
