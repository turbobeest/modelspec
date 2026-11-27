"""MODEL-491: the listed held facts (``decision.held_list``, ``verification/held.jsonl``).

A standing listing is served as held (never cited or verified) and is not a gap, only when it
resolves: to an attempt line the gate tagged with the reason (split or silent) under its hash,
with its two readers' answers from distinct known families and its filed value the fact's; or to
two or more distinct verdicts from two readers on the fact's own id and value. A clearing ends a
hold only when it passes the shared release test. A forged hash, a hand-appended line, the wrong
kind, fact or value fails the build, and an unlisted gap is still a gap. Every record here is
synthetic.
"""

from __future__ import annotations

import copy
import json
from datetime import UTC, datetime

import pytest
from decision.held_list import HELD_FILE, line, standing
from decision.quarantine_clearing import AttemptLog, line_hash, verdict_sha256
from decision.snapshot import HELD_LISTED, SnapshotBuildError, SnapshotInputs, _compile

from tests.snapshot_records import SOURCES, fact, model, verification

MID, FACET, OTHER = "lab/alpha", "model.context_window", "model.max_output_tokens"
FID = f"{MID}#{FACET}"
CITE = {"src-cite": "https://www.perplexity.ai/pro"}
AT = datetime(2026, 11, 27, 9, tzinfo=UTC)
VALUE = 262144


def attempt(*, facet=FACET, kind="split", values=(VALUE, 131072), filed=VALUE,
            families=("openai", "anthropic")):
    from decision.cited_change import fact_epoch

    agreed = values[0] == values[1]
    epoch = fact_epoch(fact("model", MID, facet, VALUE, outcome=None))
    line_ = {"subject": MID, "facet": facet, "epoch": epoch,
             "url": "https://lab.example.com", "complete": True, "agreed": agreed,
             "agreed_value": values[0] if agreed else None, "harness": True,
             "page_sha256": "3" * 64, "text_sha256": "a" * 64, "prompt_sha256": "4" * 64,
             "at": "2026-11-27T08:00:00+00:00", "filed_value": filed,
             "readers": [{"reader_id": "a", "family": families[0], "version": "1",
                          "value": values[0]},
                         {"reader_id": "b", "family": families[1], "version": "1",
                          "value": values[1]}]}
    if kind is not None:
        line_["kind"] = kind
    return line_


def silent():
    return attempt(kind="silent", values=(None, None))


def raw(a):
    return json.dumps(a, sort_keys=True, ensure_ascii=False)


def held_fact(value=VALUE):
    """A cited fact a mismatch holds: a gap unless it is listed."""
    f = fact("model", MID, FACET, value, outcome=None)
    f["sources"] = [{"source_id": "src-cite", "snapshot_ref": "sha256:" + "6" * 64,
                     "cited_regions": ["page"], "retrieved_at": "2026-11-27T08:00:00+00:00"}]
    return f


def mismatch(day="2026-10-01", value=VALUE, verifier=("verifier-b", "re-read")):
    v = verification("fact", FID, "mismatch", day=day, value=value)
    v["verifier"] = {**v["verifier"], "agent": verifier[0], "method": verifier[1]}
    v["method"] = verifier[1]
    return v


MISMATCH = mismatch()


def compiled(facts, attempts, held, log=(MISMATCH,), legacy=(), refusals=()):
    from decision.registry import default

    inputs = SnapshotInputs(models=[model(MID, facts=facts)], sources={**SOURCES, **CITE},
                            verifications=list(log),
                            cited_attempt_lines=[raw(a) for a in attempts], held=list(held),
                            cited_attempt_legacy=[raw(a) for a in legacy],
                            cited_refusal_lines=list(refusals))
    return _compile(inputs, default(), None, AT.date(), False)


def gap_facets(c):
    return {g.facet for g in c.gaps([MID])}


def listing(a=None, *, reason="split", value=VALUE, verdicts=(), facet=FACET):
    from decision.model import value_hash

    return line(subject=MID, facet=facet, value_hash=value_hash(value), reason=reason,
                attempt_line=raw(a) if a is not None else None, verdicts=verdicts, at=AT)


def refused(facts, attempts, held, log=(MISMATCH,), **kw):
    with pytest.raises(SnapshotBuildError, match="held list"):
        compiled(facts, attempts, held, log, **kw).held_listed()


def test_an_unlisted_held_fact_is_still_a_gap():
    c = compiled([held_fact()], [], [])
    assert FACET in gap_facets(c)
    assert c.rejected[(MID, FACET)][0].startswith("quarantined")


def test_a_listed_split_is_served_as_held_and_is_not_a_gap():
    split = attempt()
    c = compiled([held_fact()], [split], [listing(split)])
    assert FACET not in gap_facets(c)
    assert c.rejected[(MID, FACET)][0] == HELD_LISTED
    assert FACET not in c.facts.get(MID, {})  # never cited, though it cites a cite-only page
    c = compiled([held_fact()], [split], [listing(split)], log=())
    assert FACET not in c.facts.get(MID, {})  # held even where it would otherwise be cited


def test_a_silent_read_justifies_a_silent_hold():
    s = silent()
    assert FACET not in gap_facets(compiled([held_fact()], [s], [listing(s, reason="silent")]))


# --- Codex review 1: only a gate-tagged line, with reader evidence and the fact's value -----------

@pytest.mark.parametrize("bad", ["hand_appended", "other_tag", "same_family", "unknown_family",
                                 "one_reader", "no_prompt_hash", "agreeing_split",
                                 "valued_silent", "filed_other_value", "no_filed_value"])
def test_a_split_or_silent_hold_needs_the_gates_tagged_evidence(bad):
    a, reason = attempt(), "split"
    if bad == "hand_appended":  # self-declared flags, no tag the gate wrote
        a = attempt(kind=None)
    elif bad == "other_tag":
        a = attempt(kind="confirmation")
    elif bad == "same_family":
        a = attempt(families=("openai", "openai"))
    elif bad == "unknown_family":
        a = attempt(families=("unknown", "anthropic"))
    elif bad == "one_reader":
        a = attempt()
        a["readers"] = a["readers"][:1]
    elif bad == "no_prompt_hash":
        a = attempt()
        a["prompt_sha256"] = ""
    elif bad == "agreeing_split":  # tagged split, but the readers agreed
        a = attempt(values=(VALUE, VALUE))
        a["agreed"] = False
    elif bad == "valued_silent":
        a, reason = attempt(kind="silent", values=(VALUE, VALUE)), "silent"
    elif bad == "filed_other_value":  # read against another value of the fact
        a = attempt(filed=131072)
    else:
        a = attempt()
        a.pop("filed_value")
    refused([held_fact()], [a], [listing(a, reason=reason)])


@pytest.mark.parametrize("bad", ["forged_hash", "wrong_kind_silent", "wrong_fact",
                                 "other_value", "not_on_card", "extra_field", "no_time"])
def test_a_listing_that_does_not_resolve_fails_the_build(bad):
    split = attempt()
    lines, entry = [split], listing(split)
    if bad == "forged_hash":
        entry["line"] = "sha256:" + "9" * 64
    elif bad == "wrong_kind_silent":  # a split named as a silent read
        entry["reason"] = "silent"
    elif bad == "wrong_fact":  # a split logged for another facet
        other = attempt(facet=OTHER)
        lines, entry = [other], listing(other)
    elif bad == "other_value":  # the listing names a value the fact no longer has
        entry = listing(split, value=131072)
    elif bad == "not_on_card":
        entry = listing(split, facet="model.release_date")
    elif bad == "extra_field":
        entry["note"] = "x"
    else:
        entry["recorded_at"] = "2026-11-27"
    refused([held_fact()], lines, [entry])


# --- Codex review 2: two distinct verdicts, two readers, the fact's own id and value --------------

def test_a_double_hold_is_justified_by_two_readers_verdicts_on_its_value():
    # The build keeps the latest verdict per (id, value hash): two readers' verdicts on one
    # value stand together only on two spellings of an unordered value.
    from decision.model import value_hash

    facet = "model.input_modalities"
    fid = f"{MID}#{facet}"
    f = fact("model", MID, facet, ["text", "image"], outcome=None)
    one = verification("fact", fid, "mismatch", day="2026-10-01", value=["text", "image"])
    two = verification("fact", fid, "mismatch", day="2026-10-02", value=["image", "text"])
    two["verifier"] = {**two["verifier"], "agent": "verifier-c", "method": "key-value-match@1"}
    entry = line(subject=MID, facet=facet, value_hash=value_hash(["text", "image"]),
                 reason="held_verdicts", attempt_line=None,
                 verdicts=[verdict_sha256(one), verdict_sha256(two)], at=AT)
    c = compiled([f], [], [entry], log=[one, two])
    assert facet not in gap_facets(c)
    assert c.rejected[(MID, facet)][0] == HELD_LISTED


@pytest.mark.parametrize("bad", ["repeated", "one_verdict", "other_value", "same_reader",
                                 "not_holding"])
def test_a_double_hold_that_is_not_two_readers_on_this_value_fails(bad):
    other_value = mismatch(day="2026-10-02", value=131072,
                           verifier=("verifier-c", "key-value-match@1"))
    log = [MISMATCH, other_value]
    shas = {"repeated": [verdict_sha256(MISMATCH)] * 2,
            "one_verdict": [verdict_sha256(MISMATCH)],
            "other_value": [verdict_sha256(MISMATCH), verdict_sha256(other_value)],
            "same_reader": [verdict_sha256(MISMATCH), verdict_sha256(MISMATCH)],
            "not_holding": [verdict_sha256(MISMATCH), "sha256:" + "8" * 64]}[bad]
    refused([held_fact()], [], [listing(reason="held_verdicts", verdicts=shas)], log=log)


def test_standing_accepts_a_double_hold_on_two_readers_verdicts():
    # Two readers' verdicts on the fact's id and value, kept as the latest of their own keys:
    # the location id and a value-hash spelling of the same members (an unordered set).
    from decision.model import value_hash

    facet = "model.input_modalities"
    fid = f"{MID}#{facet}"
    f = fact("model", MID, facet, ["text", "image"], outcome=None)
    one = verification("fact", fid, "mismatch", day="2026-10-01", value=["text", "image"])
    two = verification("fact", fid, "mismatch", day="2026-10-02", value=["image", "text"])
    two["verifier"] = {**two["verifier"], "agent": "verifier-c", "method": "key-value-match@1"}
    verdicts = {("fact", fid, one["target"]["value_hash"]): ("2026-10-01", 1, one),
                ("fact", fid, two["target"]["value_hash"]): ("2026-10-02", 2, two)}
    entry = line(subject=MID, facet=facet, value_hash=value_hash(["text", "image"]),
                 reason="held_verdicts", attempt_line=None,
                 verdicts=[verdict_sha256(one), verdict_sha256(two)], at=AT)
    listed, problems = standing([entry], fact_at=lambda s, fa: f if fa == facet else None,
                                log=AttemptLog([]), verdicts=verdicts)
    assert problems == [] and listed == {(MID, facet)}
    same = copy.deepcopy(two)
    same["verifier"] = dict(one["verifier"])
    verdicts[("fact", fid, two["target"]["value_hash"])] = ("2026-10-02", 2, same)
    entry2 = {**entry, "verdicts": [verdict_sha256(one), verdict_sha256(same)]}
    assert standing([entry2], fact_at=lambda s, fa: f if fa == facet else None,
                    log=AttemptLog([]), verdicts=verdicts)[1]  # one reader: refused


# --- Codex review 3: a clearing ends a hold only through the shared release test ------------------

def test_a_clearing_ends_a_hold_only_when_it_releases_the_fact():
    split = attempt()
    log = AttemptLog([raw(split)])
    entry = listing(split)
    verdicts = {("fact", FID, MISMATCH["target"]["value_hash"]): ("2026-10-01", 1, MISMATCH)}

    def held_now(clearings):
        return standing([entry], fact_at=lambda s, f: held_fact(), log=log, verdicts=verdicts,
                        clearings=clearings, sources={**SOURCES, **CITE}, history={},
                        cutoff=AT.date())[0]

    assert held_now([]) == {(MID, FACET)}
    # A line that names the fact, its value, the verdict and a later time, but releases
    # nothing (no agreement, no block it made): the hold stands.
    named = {"subject": MID, "facet": FACET, "value": VALUE,
             "verdict_sha256": verdict_sha256(MISMATCH), "cleared_at": "2026-11-28T09:00:00+00:00"}
    assert held_now([named]) == {(MID, FACET)}
    assert held_now([{**named, "value": 131072}]) == {(MID, FACET)}


def test_a_valid_clearing_after_the_listing_releases_the_hold(monkeypatch):
    import decision.quarantine_clearing as qc

    split = attempt()
    log = AttemptLog([raw(split)])
    entry = listing(split)
    verdicts = {("fact", FID, MISMATCH["target"]["value_hash"]): ("2026-10-01", 1, MISMATCH)}
    seen = []

    def released(fact, subject, **kw):
        seen.append((subject, kw["verdict"] == MISMATCH))
        return True

    monkeypatch.setattr(qc, "fact_released", released)
    clearing = {"subject": MID, "facet": FACET, "value": VALUE,
                "verdict_sha256": verdict_sha256(MISMATCH),
                "cleared_at": "2026-11-28T09:00:00+00:00"}
    kw = dict(fact_at=lambda s, f: held_fact(), log=log, verdicts=verdicts, sources={},
              history={}, cutoff=AT.date())
    assert standing([entry], clearings=[clearing], **kw)[0] == set()
    assert seen == [(MID, True)]  # the shared test was asked, for the verdict that holds it
    earlier = {**clearing, "cleared_at": "2026-11-26T09:00:00+00:00"}
    assert standing([entry], clearings=[earlier], **kw)[0] == {(MID, FACET)}


def test_the_latest_listing_decides():
    split = attempt()
    log = AttemptLog([raw(split)])
    entry = listing(split)
    forged = {**entry, "line": "sha256:" + "9" * 64}
    verdicts = {("fact", FID, MISMATCH["target"]["value_hash"]): ("2026-10-01", 1, MISMATCH)}
    listed, problems = standing([forged, entry], fact_at=lambda s, f: held_fact(), log=log,
                                verdicts=verdicts)
    assert listed == {(MID, FACET)} and problems == []


def test_the_site_loader_withholds_a_standing_listing(tmp_path):
    import yaml
    from decision.cited_reader import ATTEMPTS_FILE
    from pipeline.load import load_models

    from tests.test_retained_agreement import source

    root = tmp_path / "data"
    (root / "models" / "lab").mkdir(parents=True)
    (root / "registry").mkdir()
    (root / "verification").mkdir()
    card = yaml.safe_dump({"display_name": "Alpha", "model_id": MID, "facts": [held_fact()]},
                          sort_keys=False)
    (root / "models/lab/alpha.md").write_text(f"---\n{card}---\nbody\n")
    (root / "registry/sources.yaml").write_text(yaml.safe_dump(
        {"schema_version": 1, "sources": [source("src-cite", CITE["src-cite"])]}))
    (root / "verification/log.jsonl").write_text(json.dumps(MISMATCH) + "\n")
    split = attempt()
    (root / ATTEMPTS_FILE).write_text(raw(split) + "\n")
    (root / HELD_FILE).write_text(json.dumps(listing(split), sort_keys=True) + "\n")
    (card_,) = load_models(root)
    assert card_.cited_facts == [] and card_.withheld_facets == (FACET,)
    assert line_hash(raw(split)) == listing(split)["line"]


# --- #1206: a legacy read, a refusal before any read, the fact's epoch ---------------------------

def legacy_split(**kw):
    a = attempt(kind=None, **kw)
    a.pop("filed_value")  # a cite-only read logged before the tags carried no filed value
    return a


def test_an_untagged_split_in_the_legacy_prefix_justifies_a_split_hold():
    old = legacy_split()
    c = compiled([held_fact()], [old], [listing(old)], legacy=[old])
    assert FACET not in gap_facets(c) and c.rejected[(MID, FACET)][0] == HELD_LISTED
    refused([held_fact()], [old], [listing(old)])  # the same line past the prefix: refused


def test_a_legacy_line_in_another_epoch_does_not_justify_a_hold():
    old = legacy_split()
    old["epoch"] = "initial-before"
    refused([held_fact()], [old], [listing(old)], legacy=[old])


def test_a_tagged_line_of_a_known_fact_needs_its_filed_value():
    tagged = attempt()
    tagged.pop("filed_value")
    refused([held_fact()], [tagged], [listing(tagged)], legacy=[tagged])


def refusal_raw(**kw):
    from decision.cited_change import fact_epoch
    from decision.hold_evidence import refusal_line
    from decision.model import value_hash

    entry = refusal_line(subject=MID, facet=FACET, value_hash=value_hash(VALUE),
                         reason="quarantined", epoch=fact_epoch(held_fact()),
                         source_id="src-cite", fetched=False, at=AT)
    return json.dumps({**entry, **kw}, sort_keys=True)


def refusal_listing(raw_line):
    entry = listing(None, reason="refused")
    entry["line"] = line_hash(raw_line)
    return entry


def test_a_refusal_before_any_read_justifies_a_refused_hold():
    r = refusal_raw()
    c = compiled([held_fact()], [], [refusal_listing(r)], refusals=[r])
    assert FACET not in gap_facets(c) and c.rejected[(MID, FACET)][0] == HELD_LISTED


@pytest.mark.parametrize("bad", ["not_logged", "other_value", "other_epoch", "other_fact",
                                 "wrong_rule", "extra_field", "no_reason"])
def test_a_refused_hold_needs_the_gates_refusal_of_this_fact_and_value(bad):
    from decision.model import value_hash

    change = {"other_value": {"value_hash": value_hash(131072)},
              "other_epoch": {"epoch": "reread:x"},
              "other_fact": {"facet": OTHER, "fact_id": f"{MID}#{OTHER}"},
              "wrong_rule": {"rule": "gate-refusal@0"}, "extra_field": {"note": "x"},
              "no_reason": {"reason": ""}}.get(bad, {})
    r = refusal_raw(**change)
    refused([held_fact()], [], [refusal_listing(r)], refusals=[] if bad == "not_logged" else [r])


# --- the gate writes the tag a listing rests on --------------------------------------------------

@pytest.fixture
def gate_data(tmp_path, monkeypatch):
    import socket

    from tests import test_retained_agreement as gate

    def blocked(*_a, **_k):
        raise AssertionError("no network in tests")

    monkeypatch.setattr(socket, "create_connection", blocked)
    return gate, gate.Data(tmp_path / "data", monkeypatch)


SPLIT, SILENT, AGREED = (None, ["text"]), (None, None), ("filed", "filed")


def _readers(gate, answers):
    a, b = (gate.FILED if v == "filed" else v for v in answers)
    return [gate.reader("codex", "gpt-5", a), gate.reader("claude", "claude-sonnet-5", b)]


@pytest.mark.parametrize("answers, kind", [(SPLIT, "split"), (SILENT, "silent")])
def test_the_retaining_gate_tags_a_split_or_silent_read(gate_data, answers, kind):
    gate, data = gate_data
    gate.run(readers=_readers(gate, answers))
    (line_,) = data.attempts()
    assert line_["kind"] == kind and line_["filed_value"] == gate.FILED


@pytest.mark.parametrize("answers, kind", [(SPLIT, "split"), (SILENT, "silent"), (AGREED, None)])
def test_the_cite_only_gate_tags_a_split_or_silent_read_and_logs_its_filed_value(
        gate_data, answers, kind):
    from decision.cited_change import cited_change

    gate, data = gate_data
    data.fact["sources"] = [dict(source_id="docs", snapshot_ref="sha256:" + "0" * 64,
                                 cited_regions=["model-spec"])]
    data.write()
    cited_change(subject=gate.SUBJECT, facet=gate.FACET, source_id="docs",
                 readers=_readers(gate, answers), request=gate.serve({gate.CITE_ONLY: gate.PAGE}))
    (line_,) = data.attempts()
    if kind is None:  # an agreed value on a cite-only page: as before, no tag and no filed value
        assert "kind" not in line_ and "filed_value" not in line_
    else:
        assert line_["kind"] == kind and line_["filed_value"] == gate.FILED


def test_a_split_in_a_holding_verdicts_clearing_epoch_justifies_a_hold():
    from decision.cited_change import fact_epoch
    from decision.quarantine_clearing import clearing_epoch

    base = fact_epoch(held_fact())
    cleared = attempt()
    cleared["epoch"] = clearing_epoch(base, verdict_sha256(MISMATCH))
    c = compiled([held_fact()], [cleared], [listing(cleared)])
    assert FACET not in gap_facets(c)
    other = attempt()
    other["epoch"] = clearing_epoch(base, "sha256:" + "7" * 64)  # a verdict that holds nothing
    refused([held_fact()], [other], [listing(other)])
