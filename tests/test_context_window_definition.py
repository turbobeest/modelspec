"""MODEL-491: `model.context_window` definition version 2 is the lab-stated window, and the input
limit when a lab states separate input and output limits (never their sum). A definition version
leaves earlier rule-15 attempts valid for their epoch and opens no epoch.

Synthetic pages and attempts only: no card, no page text, no private value."""

from __future__ import annotations

import hashlib
import json

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
    # A ruled fact stays where its ruling was made, and a block's epoch is its own page's.
    assert fact_epoch({**plain, "derivation": {"owner_ruling": {"subject": "x"}}}) == "initial"
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

    monkeypatch.setattr(cited_reader, "epoch_root", lambda facet_id: "initial")
    monkeypatch.setattr(cited_change, "epoch_root", lambda facet_id: "initial")
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
    assert verdict_epoch(verdict, history=qc.events(verdict), log=log, subject=gate.SUBJECT,
                         facet=FACET, first="initial") == "def2"
    # A line naming the old base, or a made-up version, is refused.
    for base in ("initial", "def3", "def1"):
        forged = {**entry, "epoch": clearing_epoch(base, verdict_sha256(verdict))}
        assert line_problem(forged, **kw)[0] != ""
