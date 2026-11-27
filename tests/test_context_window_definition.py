"""MODEL-491: `model.context_window` definition version 2 is the lab-stated window, and the input
limit when a lab states separate input and output limits (never their sum). A definition version
leaves earlier rule-15 attempts valid for their epoch and opens no epoch.

Synthetic pages and attempts only: no card, no page text, no private value."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC

import pytest

from decision import registry as reg
from decision.cited_reader import attempts, build_prompt, facet_definition, sha256
from decision.quarantine_clearing import agreement_problem
from tests import test_cited_change as gate

FACET = "model.context_window"
#: Version 1, as it read before 2026-11-27.
V1 = ("The maximum number of tokens the model accepts in one request, input and output together, "
      "as documented by its lab for its largest supported configuration. A provider that serves a "
      "smaller window records that on the offering, not here.")
#: The sha256 of version 2's normalised text. Rewording the definition without a new
#: ``definition_version`` fails here.
V2_SHA256 = "250b5ed5f2e4b836593978d6c453643744e0e9862ac1b80a5acda044d7e75870"
PAGE = b"<html><body><h1>Example Model</h1><p>Input token limit 1000. Output 100.</p></body></html>"
URL = "https://docs.example.test/models/example"


@pytest.fixture(scope="module")
def registry() -> reg.Registry:
    return reg.load()


def test_context_window_definition_is_version_2_and_states_the_rule(registry):
    facet = registry.facet(FACET)
    assert facet.definition_version == 2
    assert hashlib.sha256(facet.definition.encode()).hexdigest() == V2_SHA256
    text = facet.definition
    assert "the lab states for this model" in text
    assert "it is the input token limit; never add the two" in text
    assert "input and output together" not in text
    # The value type and unit do not change, so no contract field widens (MODEL-59).
    assert facet.value_type.kind == "number" and facet.unit == "tokens"


def test_the_reader_prompt_is_built_from_version_2():
    definition = facet_definition(FACET)
    assert "never add the two" in definition and "a bare number" in definition
    now = build_prompt(url=URL, facet_id=FACET, subject_name="Example Model", page_bytes=PAGE)
    before = build_prompt(url=URL, facet_id=FACET, subject_name="Example Model", page_bytes=PAGE,
                          definition=f"{FACET}: {V1} Type: number (a bare number, no units)")
    assert "never add the two" in now and "never add the two" not in before
    assert sha256(now) != sha256(before)


def _attempt(prompt: str, *, values=(1000, 1000), epoch: str = "initial") -> dict:
    return {
        "subject": "lab/example-model", "facet": FACET, "epoch": epoch, "complete": True,
        "agreed": values[0] == values[1], "agreed_value": values[0], "harness": True,
        "at": "2026-11-20T10:00:00+00:00", "prompt_sha256": sha256(prompt),
        "page_sha256": sha256(PAGE), "text_sha256": sha256("Example Model"),
        "readers": [
            {"reader_id": "codex-cli", "family": "openai", "version": "codex-cli 1",
             "value": values[0], "prompt_sha256": sha256(prompt)},
            {"reader_id": "claude-cli", "family": "anthropic", "version": "claude-cli 1",
             "value": values[1], "prompt_sha256": sha256(prompt)},
        ],
    }


def test_an_attempt_read_under_version_1_stays_evidence_for_its_epoch():
    before = build_prompt(url=URL, facet_id=FACET, subject_name="Example Model", page_bytes=PAGE,
                          definition=f"{FACET}: {V1}")
    assert agreement_problem(_attempt(before), 1000, FACET) is None


# --- E6 (MODEL-491): a definition version with epoch_version opens the facet's first epoch ------


def test_the_registry_versions_only_context_windows_first_epoch(registry):
    from decision.cited_reader import epoch_root

    split = {f.id: f.epoch_version for f in registry.facets() if f.epoch_version != 1}
    assert split == {FACET: 2}
    assert epoch_root(FACET) == "def2"
    # weights_openness is version 2 (#1198), but its version opens no epoch: its version 2 reads
    # were logged in ``initial`` epochs, and they still count there.
    assert registry.facet("model.weights_openness").definition_version == 2
    assert epoch_root("model.weights_openness") == "initial"
    assert epoch_root("model.max_output_tokens") == "initial"
    assert epoch_root("benchmark:swe-bench") == "initial"  # not a registry facet


def test_a_plain_fact_is_read_in_its_facets_first_epoch():
    from decision.cited_change import fact_epoch

    plain = {"facet": FACET, "value": 1000, "state": "known"}
    assert fact_epoch(plain) == "def2"
    assert fact_epoch({**plain, "facet": "model.weights_openness"}) == "initial"
    # A forged version in the data line changes nothing: the version is the registry's alone.
    for forged in ({"definition_version": 1}, {"epoch_version": 1}, {"epoch": "initial"},
                   {"definition_version": 3, "epoch_version": 3}):
        assert fact_epoch({**plain, **forged}) == "def2"
    # A ruled fact is in the first epoch in force on its ruling day; a block's is its own page's.
    for ruled_at, epoch in (("2026-10-12", "initial"), ("2026-11-27", "def2"),
                            ("2027-01-01", "def2"), ("not a day", "initial"), (None, "initial")):
        ruled = {**plain, "derivation": {"owner_ruling": {"subject": "x", "ruled_at": ruled_at}}}
        assert fact_epoch(ruled) == epoch, ruled_at
    block = {"text_sha256": "b" * 64}
    assert fact_epoch({**plain, "derivation": {"cited_change": block}}) == "reread:" + "b" * 64


def _seed(data, **entry):
    from decision.cited_reader import ATTEMPTS_FILE

    path = data.root / ATTEMPTS_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as fh:
        fh.write(json.dumps({"subject": gate.SUBJECT, "facet": gate.FACET, "url": gate.URL,
                             "at": "2026-11-20T10:00:00+00:00", **entry}) + "\n")


@pytest.fixture
def data(tmp_path, monkeypatch):
    return gate.Data(tmp_path / "data", monkeypatch)


def test_a_version_bump_opens_an_epoch_where_a_version_1_split_does_not_block(data):
    _seed(data, epoch="initial", complete=True, agreed=False, harness=True)
    # Also a forged line claiming the new version, in the old epoch: it is still in ``initial``.
    _seed(data, epoch="initial", complete=True, agreed=False, harness=True, definition_version=2)
    out = gate.run()
    assert out.changed, (out.reason, out.detail)
    assert [a["epoch"] for a in attempts(gate.SUBJECT, FACET, "def2")] == ["def2"]
    assert len(attempts(gate.SUBJECT, FACET, "initial")) == 2  # the old splits stay in their epoch


def test_a_split_in_the_new_epoch_still_blocks_it(data):
    gate.refused("readers_disagree",
                 readers=[gate.reader("codex", "gpt-5", 1), gate.reader("grok", "xai", 2)])
    gate.refused("prior_attempt_disagreed")
    assert {a["epoch"] for a in attempts(gate.SUBJECT, FACET, "def2")} == {"def2"}


def test_without_a_version_bump_no_new_epoch(data, monkeypatch):
    """The same split in ``initial`` blocks when the facet's first epoch is ``initial``: a facet
    whose epoch_version stays 1 (every other facet) keeps its epochs."""
    import decision.cited_change as cited_change
    import decision.cited_reader as cited_reader

    monkeypatch.setattr(cited_reader, "epoch_root", lambda facet_id, at=None: "initial")
    monkeypatch.setattr(cited_change, "epoch_root", lambda facet_id, at=None: "initial")
    _seed(data, epoch="initial", complete=True, agreed=False, harness=True)
    gate.refused("prior_attempt_disagreed")


def test_a_clearing_in_the_new_epoch_ignores_a_version_1_split_and_names_def2(data):
    from datetime import UTC, datetime

    from decision.quarantine_clearing import (
        AttemptLog,
        clearing_epoch,
        line_problem,
        verdict_epoch,
        verdict_sha256,
    )
    from tests import test_quarantine_clearing as qc

    verdict = qc.held_mismatch(data)
    old = clearing_epoch("initial", verdict_sha256(verdict))
    _seed(data, epoch=old, complete=True, agreed=False, harness=True)
    out = qc.run()
    assert out.changed, (out.reason, out.detail)
    [entry] = out.record["clearings"]
    new = clearing_epoch("def2", verdict_sha256(verdict))
    assert entry["epoch"] == new
    block = out.record["derivation"]["cited_change"]
    assert block["previous_epoch"] == "def2" and block["clearing_epoch"] == new
    from decision.cited_reader import ATTEMPTS_FILE

    log = AttemptLog.read(data.root / ATTEMPTS_FILE)
    kw = dict(verdict=verdict, subject=gate.SUBJECT, facet=FACET, ids=lambda rid: True, log=log,
              first="initial", history=qc.events(verdict), cutoff=datetime.now(UTC).date())
    assert line_problem(entry, **kw)[0] == ""
    # The verdict (2026-09-20) is judged by the version in force then: its record was in initial.
    assert verdict_epoch(verdict, history=qc.events(verdict), log=log, subject=gate.SUBJECT,
                         facet=FACET, first="initial") == "initial"
    # A line naming the old base, or a made-up version, is refused.
    for base in ("initial", "def3", "def1"):
        forged = {**entry, "epoch": clearing_epoch(base, verdict_sha256(verdict))}
        assert line_problem(forged, **kw)[0] != ""


def test_the_version_in_force_is_the_one_on_the_day_a_thing_was_made():
    from datetime import date, datetime

    from decision.cited_reader import epoch_root

    assert epoch_root(FACET, "2026-11-26") == "initial"
    assert epoch_root(FACET, "2026-11-26T23:59:59+00:00") == "initial"
    assert epoch_root(FACET, "2026-11-27T00:00:00+00:00") == "def2"
    assert epoch_root(FACET, "2026-11-26T20:00:00-05:00") == "def2"  # the UTC day counts
    assert epoch_root(FACET, date(2026, 9, 25)) == "initial"
    assert epoch_root(FACET, datetime(2026, 12, 1, tzinfo=UTC)) == "def2"
    assert epoch_root(FACET, "garbage") == "initial"


def test_a_later_version_never_re_judges_a_record_made_under_an_earlier_one(monkeypatch):
    """A future def3 does not move what def2 made: each thing is judged on its own day."""
    import dataclasses
    from datetime import date

    from decision import registry as registry_module
    from decision.cited_reader import epoch_root

    real = registry_module.default()
    facet = dataclasses.replace(real.facet(FACET), definition_version=3,
                                epoch_versions=((2, date(2026, 11, 27)), (3, date(2027, 3, 1))))

    class Registry:
        def facet(self, facet_id):
            return facet if facet_id == FACET else real.facet(facet_id)

    monkeypatch.setattr(registry_module, "default", lambda: Registry())
    assert epoch_root(FACET, "2026-11-01") == "initial"
    assert epoch_root(FACET, "2026-12-15") == "def2"
    assert epoch_root(FACET, "2027-03-01") == "def3"


def test_an_old_clearing_in_initial_stays_valid_after_the_version(data):
    """A clearing whose agreement was made before the version came into force is judged in
    initial, as it was made, and still passes the build's line check."""
    from datetime import UTC, datetime

    from decision.quarantine_clearing import (
        AttemptLog,
        clearing_epoch,
        line,
        line_problem,
        verdict_sha256,
    )
    from tests import test_quarantine_clearing as qc

    verdict = qc.held_mismatch(data)
    epoch = clearing_epoch("initial", verdict_sha256(verdict))
    attempt = {"subject": gate.SUBJECT, "facet": FACET, "epoch": epoch, "url": gate.URL,
               "complete": True, "agreed": True, "agreed_value": 262144, "harness": True,
               "page_sha256": "3" * 64, "text_sha256": "a" * 64, "prompt_sha256": "4" * 64,
               "at": "2026-11-20T09:00:00+00:00",
               "readers": [{"reader_id": "a", "family": "openai", "version": "1", "value": 262144},
                           {"reader_id": "b", "family": "anthropic", "version": "1",
                            "value": 262144}]}
    raw = json.dumps(attempt, sort_keys=True, ensure_ascii=False)
    target = verdict["target"]
    entry = line(key=(target["kind"], target["id"], target["value_hash"]), verdict=verdict,
                 subject=gate.SUBJECT, facet=FACET, epoch=epoch, attempt_line=raw, value=262144,
                 at=datetime(2026, 11, 20, 10, tzinfo=UTC))
    kw = dict(verdict=verdict, subject=gate.SUBJECT, facet=FACET, ids=lambda rid: True,
              log=AttemptLog([raw]), first="initial", history=qc.events(verdict),
              cutoff=datetime.now(UTC).date())
    assert line_problem(entry, **kw)[0] == ""


def test_a_ruling_on_a_def2_split_is_read_in_def2():
    """Codex on #1200: a ruling filed for a plain def2 split is found by the build in def2, and a
    ruling made in initial before the version stays valid there."""
    from datetime import date

    from tests import test_owner_ruling as owner

    for epoch, ruled_at, as_of in (("def2", "2026-11-27", date(2026, 11, 27)),
                                   ("initial", "2026-10-12", date(2026, 10, 19))):
        attempt = owner._attempt(epoch=epoch)
        ruling = owner._ruling(attempt, epoch=epoch, ruled_at=ruled_at)
        row = owner._ruled_fact(ruling)
        assert owner._build(row, [ruling], [attempt], as_of=as_of).fact(owner.MID, FACET).state \
            == "known", epoch
    # A def2 ruling dated before the version came into force is never read.
    attempt = owner._attempt(epoch="def2")
    ruling = owner._ruling(attempt, epoch="def2", ruled_at="2026-11-20")
    assert owner._build(owner._ruled_fact(ruling), [ruling], [attempt],
                        as_of=date(2026, 11, 27)).fact(owner.MID, FACET).state != "known"


def test_an_initial_clearing_agreement_made_after_def2_took_effect_is_refused(data):
    """Codex on #1200: the agreement must sit in the first epoch in force on its own day, even when
    the verdict's epoch is that same old one, so an initial agreement made after def2 took effect
    clears nothing; the same agreement made before it does."""
    from datetime import date, datetime

    from decision.quarantine_clearing import (
        AttemptLog,
        clearing_epoch,
        line,
        line_problem,
        verdict_sha256,
    )
    from tests import test_quarantine_clearing as qc

    verdict = qc.held_mismatch(data)
    target = verdict["target"]
    for base, at, ok in (("initial", "2026-11-20T09:00:00+00:00", True),
                         ("initial", "2026-11-28T09:00:00+00:00", False),
                         ("def2", "2026-11-28T09:00:00+00:00", True),
                         ("def2", "2026-11-20T09:00:00+00:00", False)):
        epoch = clearing_epoch(base, verdict_sha256(verdict))
        attempt = {"subject": gate.SUBJECT, "facet": FACET, "epoch": epoch, "url": gate.URL,
                   "complete": True, "agreed": True, "agreed_value": 262144, "harness": True,
                   "page_sha256": "3" * 64, "text_sha256": "a" * 64, "prompt_sha256": "4" * 64,
                   "at": at, "readers": [
                       {"reader_id": "a", "family": "openai", "version": "1", "value": 262144},
                       {"reader_id": "b", "family": "anthropic", "version": "1",
                        "value": 262144}]}
        raw = json.dumps(attempt, sort_keys=True, ensure_ascii=False)
        when = datetime.fromisoformat(at).astimezone(UTC).replace(hour=10)
        entry = line(key=(target["kind"], target["id"], target["value_hash"]), verdict=verdict,
                     subject=gate.SUBJECT, facet=FACET, epoch=epoch, attempt_line=raw,
                     value=262144, at=when)
        problem, _ = line_problem(entry, verdict=verdict, subject=gate.SUBJECT, facet=FACET,
                                  ids=lambda rid: True, log=AttemptLog([raw]), first="initial",
                                  history=qc.events(verdict), cutoff=date(2026, 12, 31))
        assert (problem == "") is ok, (base, at, problem)
