"""MODEL-491: `model.weights_openness` definition version 2 states handoff rule 12 and the owner's
2026-11-25 ruling, and a definition version leaves earlier rule-15 attempts valid for their epoch.

Synthetic pages and attempts only: no card, no page text, no private value."""

from __future__ import annotations

import hashlib
import json

import pytest

from decision import registry as reg
from decision.cited_reader import attempts, build_prompt, facet_definition, sha256
from decision.quarantine_clearing import agreement_problem, clearing_epoch

FACET = "model.weights_openness"
#: Version 1, as it read before 2026-11-27.
V1 = ("`open_weights` when the lab publishes the trained weights for download under any licence, "
      "including a gated or restrictive one; `closed_weights` otherwise. Says nothing about the "
      "licence terms, which are the `licence.*` facets.")
#: The sha256 of version 2's normalised text. Rewording the definition without a new
#: ``definition_version`` fails here.
V2_SHA256 = "dd9c05488f52a87c1e464cdf582220ebda8981a29c953b1f127a92b5a8bdc1fa"
PAGE = b"<html><body><h1>Example Model</h1><p>Available through the API.</p></body></html>"
URL = "https://docs.example.test/models/example"


@pytest.fixture(scope="module")
def registry() -> reg.Registry:
    return reg.load()


def test_weights_definition_is_version_2_and_states_the_rule(registry):
    facet = registry.facet(FACET)
    assert facet.definition_version == 2
    assert hashlib.sha256(facet.definition.encode()).hexdigest() == V2_SHA256
    text = facet.definition
    assert "no registered page or weights repository offers this model's weights" in text
    assert "offers this model only as a hosted service" in text
    assert "A lab publishing weights for other models does not make this model open." in text
    assert "`not_disclosed`" in text and "`closed_weights` otherwise" not in text
    # The value set does not widen: not_disclosed is a state, never a value (MODEL-59).
    assert facet.value_type.kind == "enum"
    assert set(facet.value_type.values) == {"open_weights", "closed_weights"}


def test_every_other_facet_keeps_version_1(registry):
    versioned = {f.id: f.definition_version for f in registry.facets()
                 if f.definition_version != 1}
    assert versioned == {FACET: 2}


def test_the_reader_prompt_is_built_from_version_2():
    definition = facet_definition(FACET)
    assert "hosted service" in definition and "allowed values" in definition
    now = build_prompt(url=URL, facet_id=FACET, subject_name="Example Model", page_bytes=PAGE)
    before = build_prompt(url=URL, facet_id=FACET, subject_name="Example Model", page_bytes=PAGE,
                          definition=f"{FACET}: {V1} Type: enum, allowed values "
                                     "['closed_weights', 'open_weights']")
    assert "hosted service" in now and "hosted service" not in before
    assert sha256(now) != sha256(before)


def _attempt(prompt: str, *, epoch: str = "initial") -> dict:
    return {
        "subject": "lab/example-model", "facet": FACET, "epoch": epoch, "complete": True,
        "agreed": True, "agreed_value": "closed_weights", "harness": True,
        "at": "2026-11-20T10:00:00+00:00", "prompt_sha256": sha256(prompt),
        "page_sha256": sha256(PAGE), "text_sha256": sha256("Example Model"),
        "readers": [
            {"reader_id": "codex-cli", "family": "openai", "version": "codex-cli 1",
             "value": "closed_weights", "prompt_sha256": sha256(prompt)},
            {"reader_id": "claude-cli", "family": "anthropic", "version": "claude-cli 1",
             "value": "closed_weights", "prompt_sha256": sha256(prompt)},
        ],
    }


def test_an_attempt_read_under_version_1_stays_evidence_for_its_epoch():
    before = build_prompt(url=URL, facet_id=FACET, subject_name="Example Model", page_bytes=PAGE,
                          definition=f"{FACET}: {V1}")
    # The build checks the logged agreement as logged: it never rebuilds the prompt from the
    # current definition, so a version bump does not invalidate it.
    assert agreement_problem(_attempt(before), "closed_weights", FACET) is None


def test_a_definition_version_opens_no_epoch(tmp_path, monkeypatch):
    """The epoch is the record's own, never the definition's: a v1 attempt is counted with a v2
    read in the same epoch (so a v1 disagreement still blocks there), and a clearing epoch is named
    by the verdict alone."""
    log = tmp_path / "verification" / "cited-attempts.jsonl"
    log.parent.mkdir(parents=True)
    old = _attempt(build_prompt(url=URL, facet_id=FACET, subject_name="Example Model",
                                page_bytes=PAGE, definition=f"{FACET}: {V1}"))
    log.write_text(json.dumps(old) + "\n")
    monkeypatch.setenv("MODELSPEC_DATA_DIR", str(tmp_path))
    assert attempts("lab/example-model", FACET, "initial", data_dir=tmp_path) == [old]
    assert clearing_epoch("initial", "a" * 64) == "initial:clear:" + "a" * 64
