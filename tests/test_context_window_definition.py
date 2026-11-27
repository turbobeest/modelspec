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


def test_a_definition_version_opens_no_epoch(tmp_path, monkeypatch):
    """A split read under version 1 stays in its epoch, and a version 2 read there is counted with
    it: the version names no epoch of its own."""
    log = tmp_path / "verification" / "cited-attempts.jsonl"
    log.parent.mkdir(parents=True)
    split = _attempt(build_prompt(url=URL, facet_id=FACET, subject_name="Example Model",
                                  page_bytes=PAGE, definition=f"{FACET}: {V1}"),
                     values=(1100, 1000))
    log.write_text(json.dumps(split) + "\n")
    monkeypatch.setenv("MODELSPEC_DATA_DIR", str(tmp_path))
    assert attempts("lab/example-model", FACET, "initial", data_dir=tmp_path) == [split]
