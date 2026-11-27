"""MODEL-491: the listed held facts (``decision.held_list``, ``verification/held.jsonl``).

A standing listing is served as held (never cited or verified) and is not a gap, only when it
resolves to a real gate-written line of the right kind for that fact and value, or to the
verdicts that hold it. A forged hash, the wrong kind, the wrong fact or another value fails the
build, and an unlisted gap is still a gap. Every record here is synthetic.
"""

from __future__ import annotations

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


def attempt(*, facet=FACET, agreed=False, values=(262144, 131072), agreed_value=None):
    return {"subject": MID, "facet": facet, "epoch": "initial", "url": "https://lab.example.com",
            "complete": True, "agreed": agreed, "agreed_value": agreed_value, "harness": True,
            "page_sha256": "3" * 64, "text_sha256": "a" * 64, "prompt_sha256": "4" * 64,
            "at": "2026-11-27T08:00:00+00:00", "kind": "confirmation",
            "readers": [{"reader_id": "a", "family": "openai", "version": "1", "value": values[0]},
                        {"reader_id": "b", "family": "anthropic", "version": "1",
                         "value": values[1]}]}


def raw(a):
    return json.dumps(a, sort_keys=True, ensure_ascii=False)


def held_fact(value=262144):
    """A cited fact a mismatch holds: a gap unless it is listed."""
    f = fact("model", MID, FACET, value, outcome=None)
    f["sources"] = [{"source_id": "src-cite", "snapshot_ref": "sha256:" + "6" * 64,
                     "cited_regions": ["page"], "retrieved_at": "2026-11-27T08:00:00+00:00"}]
    return f


MISMATCH = verification("fact", FID, "mismatch", day="2026-10-01", value=262144)


def compiled(facts, attempts, held, log=(MISMATCH,)):
    from decision.registry import default

    inputs = SnapshotInputs(models=[model(MID, facts=facts)], sources={**SOURCES, **CITE},
                            verifications=list(log),
                            cited_attempt_lines=[raw(a) for a in attempts], held=list(held))
    return _compile(inputs, default(), None, AT.date(), False)


def gap_facets(c):
    return {g.facet for g in c.gaps([MID])}


def listing(a=None, *, reason="split", value=262144, verdicts=(), facet=FACET):
    from decision.model import value_hash

    return line(subject=MID, facet=facet, value_hash=value_hash(value), reason=reason,
                attempt_line=raw(a) if a is not None else None, verdicts=verdicts, at=AT)


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


def test_a_listed_fact_is_held_even_when_it_would_otherwise_be_cited():
    split = attempt()
    c = compiled([held_fact()], [split], [listing(split)], log=())
    assert FACET not in c.facts.get(MID, {}) and c.rejected[(MID, FACET)][0] == HELD_LISTED


def test_a_silent_read_justifies_a_silent_hold():
    silent = attempt(agreed=True, values=(None, None), agreed_value=None)
    c = compiled([held_fact()], [silent], [listing(silent, reason="silent")])
    assert FACET not in gap_facets(c)


@pytest.mark.parametrize("bad", ["forged_hash", "wrong_kind_split", "wrong_kind_silent",
                                 "wrong_fact", "other_value", "not_on_card", "extra_field",
                                 "no_time"])
def test_a_listing_that_does_not_resolve_fails_the_build(bad):
    split = attempt()
    lines, entry = [split], listing(split)
    if bad == "forged_hash":
        entry["line"] = "sha256:" + "9" * 64
    elif bad == "wrong_kind_split":  # an agreeing line named as a split
        agreeing = attempt(agreed=True, values=(262144, 262144), agreed_value=262144)
        lines, entry = [agreeing], listing(agreeing)
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
    with pytest.raises(SnapshotBuildError, match="held list"):
        compiled([held_fact()], lines, [entry]).held_listed()


def test_a_double_hold_is_justified_by_the_verdicts_that_hold_it():
    second = verification("fact", FID, "mismatch", day="2026-10-02", value=131072)
    log = [MISMATCH, second]
    shas = [verdict_sha256(MISMATCH), verdict_sha256(second)]
    c = compiled([held_fact()], [], [listing(reason="held_verdicts", verdicts=shas)], log=log)
    assert FACET not in gap_facets(c)
    with pytest.raises(SnapshotBuildError, match="held list"):
        compiled([held_fact()], [], [listing(reason="held_verdicts", verdicts=shas[:1])],
                 log=log).held_listed()  # one verdict is clearable, so no double hold
    with pytest.raises(SnapshotBuildError, match="held list"):
        compiled([held_fact()], [], [listing(reason="held_verdicts", verdicts=shas)],
                 log=[MISMATCH]).held_listed()  # a listed verdict no longer holds it


def test_a_later_clearing_ends_the_hold_and_the_latest_listing_decides():
    split = attempt()
    log = AttemptLog([raw(split)])
    entry = listing(split)
    fact_at = {(MID, FACET): held_fact()}.get
    verdicts = {("fact", FID, MISMATCH["target"]["value_hash"]): ("2026-10-01", 1, MISMATCH)}
    listed, problems = standing([entry], fact_at=lambda s, f: fact_at((s, f)), log=log,
                                verdicts=verdicts)
    assert listed == {(MID, FACET)} and problems == []
    later = {"subject": MID, "facet": FACET, "cleared_at": "2026-11-28T09:00:00+00:00"}
    earlier = {**later, "cleared_at": "2026-11-26T09:00:00+00:00"}
    assert standing([entry], fact_at=lambda s, f: fact_at((s, f)), log=log, verdicts=verdicts,
                    clearings=[later])[0] == set()
    assert standing([entry], fact_at=lambda s, f: fact_at((s, f)), log=log, verdicts=verdicts,
                    clearings=[earlier])[0] == {(MID, FACET)}
    forged = {**entry, "line": "sha256:" + "9" * 64}
    assert standing([forged, entry], fact_at=lambda s, f: fact_at((s, f)), log=log,
                    verdicts=verdicts)[0] == {(MID, FACET)}  # the latest listing decides


def test_the_site_loader_withholds_a_standing_listing(tmp_path):
    import yaml
    from decision.cited_reader import ATTEMPTS_FILE
    from pipeline.load import load_models

    from tests.test_retained_agreement import source

    root = tmp_path / "data"
    (root / "models" / "lab").mkdir(parents=True)
    (root / "registry").mkdir()
    (root / "verification").mkdir()
    f = held_fact()
    card = yaml.safe_dump({"display_name": "Alpha", "model_id": MID, "facts": [f]},
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
