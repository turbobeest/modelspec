"""MODEL-537: the claim scorecard's "strongest model left out" helper."""

from __future__ import annotations

import pytest

from scripts.claim_scorecard import leaders, resolve, scorecard, strongest_left_out, tokens

URL = "https://example.test/release"


def row(bench="gpqa_diamond", score=50.0, day="2026-08-01", **extra):
    return {"benchmark_id": bench, "model_id_as_evaluated": "x", "score": score, "unit": "percent",
            "source_url": URL, "source_kind": "independent_evaluator", "evidence_date": day,
            "date_type": "published", "verified_at": day, **extra}


def card(mid, name, *rows, release="2026-07-01"):
    return {"model_id": mid, "display_name": name, "release_date": release,
            "benchmarks": {"evidence": list(rows)}}


BASE = {"kind": "named_model", "label": "Opus-5.0, GPT-5.6 Sol, DS-V4-Flash", "source": URL}
SUBJECT = card("deepseek/deepseek-v4-1-flash", "DeepSeek V4.1 Flash",
               row(score=88.0, day="2026-09-10", source_kind="provider_self_report",
                   measured_by="provider_self_report", baseline=BASE), release="2026-09-10")
OPUS = card("anthropic/claude-opus-5", "Claude Opus 5", row(score=86.0))
SOL = card("openai/gpt-5-6-sol", "GPT-5.6 Sol", row(score=84.0))
FLASH = card("deepseek/deepseek-v4-flash", "DeepSeek V4 Flash", row(score=80.0))
ASTRA = card("openai/gpt-6-astra", "GPT-6 Astra", row(score=92.0, day="2026-09-03"))
LATER = card("google/gemini-4", "Gemini 4", row(score=99.0, day="2026-10-01"))


def test_tokens_drop_effort_words_and_trailing_zero():
    assert tokens("Opus-5.0 (Max)".replace("-", " ")) == {"opus", "5"}
    assert tokens("DS V4 Pro") == {"deepseek", "v4", "pro"}
    assert tokens("GPT 5.6 Sol xHigh") == {"gpt", "5.6", "sol"}


def test_labels_resolve_to_the_closest_card_only():
    cards = [OPUS, SOL, FLASH, card("anthropic/claude-opus-5-5", "Claude Opus 5.5")]
    assert resolve("Opus-5.0", cards) == ["anthropic/claude-opus-5"]
    assert resolve("DS-V4-Flash", cards) == ["deepseek/deepseek-v4-flash"]
    assert resolve("DeepSeek-V4-Flash-0731", cards) == ["deepseek/deepseek-v4-flash"]
    assert resolve("Unknown Model 9", cards) == []


def test_leader_left_out_is_reported():
    out = strongest_left_out([SUBJECT, OPUS, SOL, FLASH, ASTRA, LATER], SUBJECT, SUBJECT["benchmarks"]["evidence"][0])
    assert out.as_of == "2026-09-10"
    assert out.leader.model_id == "openai/gpt-6-astra"
    assert out.leader_included is False
    assert out.strongest_left_out.model_id == "openai/gpt-6-astra"
    assert out.comparable_models == 4  # the later reading and the subject itself are out
    assert out.unresolved == []


def test_leader_included_then_next_best_left_out():
    out = strongest_left_out([SUBJECT, OPUS, SOL, FLASH], SUBJECT, SUBJECT["benchmarks"]["evidence"][0])
    assert out.leader.model_id == "anthropic/claude-opus-5"
    assert out.leader_included is True
    assert out.strongest_left_out is None


def test_unresolved_label_is_listed_not_guessed():
    reading = {**SUBJECT["benchmarks"]["evidence"][0],
               "baseline": {"kind": "named_model", "label": "Mystery-1", "source": URL}}
    out = strongest_left_out([SUBJECT, OPUS], SUBJECT, reading)
    assert out.unresolved == ["Mystery-1"]
    assert out.strongest_left_out.model_id == "anthropic/claude-opus-5"


def test_setup_unit_and_publication_filter_comparable_rows():
    reading = {**SUBJECT["benchmarks"]["evidence"][0], "harness": "mini-swe-agent"}
    other_harness = card("a/b", "B", row(score=99.0, harness="claude-code"))
    unregistered = card("a/c", "C", row(score=98.0, harness="unregistered"))
    other_unit = card("a/d", "D", row(score=97.0, unit="elo"))
    withdrawn = card("a/e", "E", row(score=96.0, not_published_since="2026-08-15"))
    ranked = leaders([other_harness, unregistered, other_unit, withdrawn, OPUS], reading, "2026-09-10")
    assert [r.model_id for r in ranked] == ["a/c", "anthropic/claude-opus-5"]


def test_lower_is_better_and_best_row_per_model():
    two = card("a/b", "B", row(score=10.0), row(score=4.0))
    one = card("a/c", "C", row(score=6.0))
    ranked = leaders([two, one], row(), "2026-09-10", higher_is_better=False)
    assert [(r.model_id, r.score) for r in ranked] == [("a/b", 4.0), ("a/c", 6.0)]


def test_scorecard_skips_absent_and_none_stated_baselines():
    plain = card("a/p", "P", row(), row(baseline={"kind": "none_stated"}))
    results = scorecard([SUBJECT, OPUS, plain], {})
    assert [r.subject for r in results] == ["deepseek/deepseek-v4-1-flash"]
    with pytest.raises(ValueError):
        strongest_left_out([plain], plain, plain["benchmarks"]["evidence"][1])
