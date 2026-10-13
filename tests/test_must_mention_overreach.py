"""MODEL-351: must_mention names the claim each failing 2026-10-08 answer made.

The fixtures are the decide calls from the Claude-only subscription run on engine
2f544e37 (checkpoint ``scenarios-2026-10-08-21c2db2ccbd78211``). Each holds the
spec the agent sent and the parts of the Decision the summary reads, with
values replaced by placeholders. Rows the 16 KB trim dropped from the bounded
body (``restored_from_local_rerun``) come from a local re-run of the same spec
whose answer and may_qualify count match production. ``production_must_mention``
is what production returned; main's summary reproduced it exactly.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from decision.contract import Decision, parse_spec
from decision.summary import MUST_MENTION_ITEM_BYTES, MUST_MENTION_MAX, summarize

FIXTURES = Path(__file__).parent / "fixtures/decision/model-351-repros.json"
BASE = {
    "contract_version": "2.16",
    "snapshot": "snap_e2b358c1663dacb6",
    "spec_hash": "sha256:" + "0" * 64,
    "explain": "summary",
}
NOT_A_PICK = "; this is not a recommendation of any one of them."
CHECKED_ONLY = "ModelSpec checked only the stated requirements; other needs were not checked."
HEADROOM = (
    " is an estimate; fit for a specific quantization, context length "
    "or runtime headroom is not established."
)
OLD_HARDWARE = (
    "fits_hardware is an estimate, not a measured fit for a quantization or context workload."
)
OPUS_TIE = (
    "anthropic/claude-opus-5-5, anthropic/claude-sonnet-5-5, openai/gpt-6-astra, "
    "and anthropic/claude-opus-4-7 are tied" + NOT_A_PICK
)
MATHS_TIE = "openai/gpt-6-astra, openai/gpt-6-sol, and openai/gpt-5-6-sol are tied" + NOT_A_PICK
MATHS_UNKNOWN = (
    "No model is established as the best fit: maths is unknown for qwen/qwen3-8-max-0902, "
    "anthropic/claude-sonnet-5-5, openai/gpt-6-luna, and qwen/qwen3-8-flash-next."
)
CODING_UNKNOWN_TWO = (
    "No model is established as the best fit: software_engineering is unknown for "
    "deepseek/deepseek-flash and openai/gpt-6-luna."
)

# The claim each row's judges failed, and the item that now names it.
EXPECTED: dict[str, list[str]] = {
    # "Qwen3.8 Flash Next passed every gate the user stated"; 4-bit, 8192 tokens and
    # headroom on 128 GB are not facets, and fits_hardware is an estimate.
    "hardware-spark": [
        "No model is established as the best fit: model.fits_hardware and "
        "model.weights_openness are unknown for anthropic/claude-sonnet-5-5.",
        CHECKED_ONLY,
        "model.fits_hardware in {nvidia_dgx_spark}" + HEADROOM,
    ],
    # A not_separable three-way tie presented as "the pick", pointing at the cheapest.
    "prompt-maths": [MATHS_TIE, MATHS_UNKNOWN, CHECKED_ONLY],
    # Thread-safe code plus tests has no facet; task_type bug_fix was never applied.
    "prompt-code": [
        OPUS_TIE,
        "No model is established as the best fit: software_engineering is unknown for "
        "openai/gpt-6-luna.",
        "task_type = bug_fix was not applied; ModelSpec did not check it.",
        CHECKED_ONLY,
    ],
    # A proxy-based four-model tie recommended for multi-day repository editing.
    "recall-q01": [
        OPUS_TIE,
        CODING_UNKNOWN_TWO,
        "task_type = new_feature was not applied; ModelSpec did not check it.",
        CHECKED_ONLY,
    ],
    # A five-model estimated tie presented as the choice for a shell agent.
    "recall-q02": [
        "anthropic/claude-opus-5-5, anthropic/claude-sonnet-5-5, openai/gpt-6-astra, "
        "anthropic/claude-opus-4-7, and anthropic/claude-fable-5 are tied" + NOT_A_PICK,
        "No model is established as the best fit: software_engineering is unknown for "
        "deepseek/deepseek-flash, google/gemma-4-26b-a4b-it, and google/gemma-4-31b-it, "
        "and 3 more in may_qualify.",
        "task_type = new_feature was not applied; ModelSpec did not check it.",
        CHECKED_ONLY,
    ],
    # Defect review treated as patch generation; "no constraint was dropped".
    "recall-q03": [
        OPUS_TIE,
        CODING_UNKNOWN_TWO,
        "task_type = review was not applied; ModelSpec did not check it.",
        CHECKED_ONLY,
    ],
    # A tied top set recommended from web-dev evidence used as chat_preference.
    "recall-q05": [
        "anthropic/claude-opus-5-5 and anthropic/claude-fable-5 are tied" + NOT_A_PICK,
        "No model is established as the best fit: chat_preference is unknown for "
        "anthropic/claude-sonnet-5-5, deepseek/deepseek-flash, and google/gemma-4-26b-a4b-it, "
        "and 4 more in may_qualify.",
        CHECKED_ONLY,
    ],
    # A contest-maths tie recommended from research-maths estimates.
    "recall-q07": [MATHS_TIE, MATHS_UNKNOWN, CHECKED_ONLY],
    # "Nothing was dropped from the request"; high-volume throughput was never applied.
    "recall-q10": [CHECKED_ONLY],
    # "All requirements were applied"; runtime headroom was never addressed.
    "hardware-m4-gated": [CHECKED_ONLY, "model.fits_hardware in {apple_m4}" + HEADROOM],
    # The relaxed run's tie (fits_hardware gate dropped) used in the answer.
    "hardware-m4-relaxed": [
        "qwen/qwen3-8-flash-next and zhipu/glm-5-3 are tied" + NOT_A_PICK,
        "No model is established as the best fit: model.fits_hardware and "
        "model.weights_openness are unknown for one or more of "
        "anthropic/claude-sonnet-5-5, and 3 more in may_qualify.",
        CHECKED_ONLY,
        # The agent dropped the apple_m4 gate; the relaxed tie was never fitted to it.
        "model.fits_hardware was not required, so no model is established to fit "
        "the target hardware.",
    ],
}


def _fixtures() -> list[dict]:
    return json.loads(FIXTURES.read_text())


def _summarize(fixture: dict) -> tuple[str, list[str]]:
    decision = Decision.model_validate(
        BASE | {"decision_id": fixture["decision_id"]} | fixture["decision"]
    )
    return summarize(decision, parse_spec(fixture["spec"], facets=None))


def test_every_repro_row_has_a_fixture_and_an_expectation() -> None:
    names = [fixture["name"] for fixture in _fixtures()]
    assert names == list(EXPECTED)


@pytest.mark.parametrize("fixture", _fixtures(), ids=lambda fixture: fixture["name"])
def test_must_mention_names_the_unsupported_claim(fixture: dict) -> None:
    text, mentions = _summarize(fixture)
    for item in EXPECTED[fixture["name"]]:
        assert item in mentions
    assert len(mentions) <= MUST_MENTION_MAX
    assert all(len(item.encode("utf-8")) <= MUST_MENTION_ITEM_BYTES for item in mentions)
    # Every fact production already carried is still carried, except the
    # reworded hardware sentence, on a partial answer the may-qualify count
    # that the partial item now replaces with names, and the leaderboard
    # sentence, which MODEL-354 rewrote as a record count (the fixtures keep
    # one record per benchmark, so their counts are not production's).
    partial = fixture["decision"]["status"] == "partial"
    kept = [
        item for item in fixture["production_must_mention"]
        if item != OLD_HARDWARE
        and not (partial and " may qualify, but " in item)
        and " no leaderboard data for " not in item
    ]
    assert [item for item in mentions if item in kept] == kept
    assert OLD_HARDWARE not in mentions
    if partial:
        assert text.startswith("ModelSpec's answer is incomplete, so it names no pick.")
    if fixture["decision"]["answer"] and fixture["decision"]["answer"]["kind"] == "tied":
        # Every failing tie was partial: the paragraph agents quote says it too.
        assert NOT_A_PICK.lstrip("; ") in text
    assert CHECKED_ONLY in text
