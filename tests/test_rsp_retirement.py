"""MODEL-491: retained-source-proof@1 stops counting, and a label matcher's "verified" on a null
value is no verification (E5).

Every build from the private data retires both (``SnapshotInputs.retire_rsp``, set by
``collect_repo`` from the checkout's ``.engine-pin``). The engine's frozen public image keeps
the rule as filed. Every record here is synthetic.
"""

from __future__ import annotations

import copy

import pytest
from decision.model import Verification, verification_row_counts
from decision.snapshot import SnapshotInputs, build_snapshot, load_built_snapshot

from tests.snapshot_records import SOURCES, fact, model, verification

MID, FACET = "lab/alpha", "model.context_window"
FID = f"{MID}#{FACET}"
NULL_FACET = "feature.tool_calling"
NULL_FID = f"{MID}#{NULL_FACET}"


def row(method, *, outcome="verified", day="2026-09-25", value=128000, fid=FID,
        agent="codex-model-143"):
    v = verification("fact", fid, outcome, day=day, value=value)
    v["method"] = method
    v["verifier"] = {**v["verifier"], "method": method}
    v["collector"] = {**v["collector"], "agent": agent}
    return v


def shown(facts, log, *, retire=True):
    inputs = SnapshotInputs(models=[model(MID, facts=facts)], sources=dict(SOURCES),
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


def test_the_retired_method_is_found_on_the_row_or_its_verifier():
    proof = row("retained-source-proof@1")
    by_verifier = copy.deepcopy(proof)
    by_verifier["method"] = "multi-source-primary-audit@2"
    for r in (proof, by_verifier):
        assert not verification_row_counts(r)
        assert verification_row_counts(r, retire=False)
        assert not Verification.model_validate(r).counts


@pytest.mark.parametrize("matcher", ["model-page-label-match@1", "key-value-match@1"])
def test_a_label_matcher_never_verifies_a_null_value(matcher):
    # E5: the round-1 label matchers "verified" a not_disclosed value on a page that names the
    # model; that shows nothing about a value the page does not state.
    null = fact_on_log(NULL_FACET, None, state="not_disclosed")
    label = row(matcher, value=None, fid=NULL_FID)
    assert not verification_row_counts(label)
    assert shown([null], [label]).fact(MID, NULL_FACET).state != "not_disclosed"
    assert shown([null], [label], retire=False).fact(MID, NULL_FACET).state == "not_disclosed"
    # The same matcher on a stated value still counts, and so does another reader on a null.
    assert verification_row_counts(row(matcher, value=128000))
    other = row("absence-reading@1", value=None, fid=NULL_FID)
    assert verification_row_counts(other)
    assert shown([null], [other]).fact(MID, NULL_FACET).state == "not_disclosed"


@pytest.mark.parametrize("change", ["later_day", "other_collector"])
def test_a_later_absence_reading_by_a_label_matcher_still_counts(change):
    # E5 is MODEL-143 round 1 only: a later absence reading by the same readers is not affected.
    kw = {"day": "2026-11-24"} if change == "later_day" else {"agent": "model-491-builder"}
    for matcher in ("model-page-label-match@1", "key-value-match@1"):
        assert verification_row_counts(row(matcher, value=None, fid=NULL_FID, **kw))


def test_a_label_matchers_mismatch_on_a_null_still_holds():
    # E5 only stops a label matcher's "verified" from admitting a null; its mismatch still counts.
    assert verification_row_counts(row("key-value-match@1", outcome="mismatch", value=None))


def test_a_same_family_verified_row_still_does_not_count():
    same = row("key-value-match@1")
    same["verifier"]["model_family"] = same["collector"]["model_family"]
    assert not verification_row_counts(same) and not verification_row_counts(same, retire=False)


def test_collect_repo_retires_for_the_private_data_only(tmp_path):
    from decision.snapshot import collect_repo

    (tmp_path / "models").mkdir()
    assert collect_repo(tmp_path).retire_rsp is False  # the engine's frozen public image
    (tmp_path / ".engine-pin").write_text("0" * 40 + "\n")
    assert collect_repo(tmp_path).retire_rsp is True  # the private data checkout
