"""The recall YAML is data: it loads, and every expected entry is sourced."""

from __future__ import annotations

import re
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
IDS = [f"Q{n:02d}" for n in range(1, 21)]
ENTRY_LISTS = ("acceptable", "must_never", "must_flag", "missing_cards")


def _load(name: str) -> dict:
    return yaml.safe_load((HERE / name).read_text(encoding="utf-8"))


def _sources_ok(entry: dict, where: str) -> None:
    sources = entry.get("sources")
    assert isinstance(sources, list) and sources, f"{where} has no sources"
    for source in sources:
        assert isinstance(source, dict), where
        url = source.get("url")
        assert isinstance(url, str) and url.startswith("https://"), where
        assert DATE.match(str(source.get("read") or "")), where


def test_recall_questions_and_expected_load() -> None:
    questions = _load("questions.yaml")
    expected = _load("expected.yaml")
    q_ids = [row["id"] for row in questions["questions"]]
    e_ids = [row["id"] for row in expected["questions"]]
    assert q_ids == IDS
    assert e_ids == IDS
    for row in questions["questions"]:
        assert row["question"].strip()
        assert isinstance(row["constraints"], dict) and row["constraints"]


def test_every_expected_entry_has_a_source_and_an_iso_date() -> None:
    expected = _load("expected.yaml")
    for question in expected["questions"]:
        assert question["notes"].strip()
        for key in ENTRY_LISTS:
            for index, entry in enumerate(question[key]):
                where = f"{question['id']} {key}[{index}]"
                assert entry.get("reason", "").strip(), where
                _sources_ok(entry, where)
                assert entry.get("model_id") or entry.get("name") or entry.get("rule"), where


def test_model_164_approved_expected_answer_changes_are_preserved() -> None:
    questions = {row["id"]: row for row in _load("expected.yaml")["questions"]}

    approved_acceptable = {
        "Q03": {
            "anthropic/claude-opus-4-6",
            "anthropic/claude-opus-5",
            "anthropic/claude-fable-5-1",
            "openai/gpt-6-astra",
            "google/gemini-3-8-flash",
        },
        "Q04": {
            "anthropic/claude-fable-5-1",
            "anthropic/claude-opus-5",
            "anthropic/claude-opus-4-6",
            "anthropic/claude-fable-5",
            "google/gemini-3-8-flash",
        },
        "Q05": {
            "anthropic/claude-fable-5-1",
            "anthropic/claude-opus-5",
            "anthropic/claude-opus-4-6",
            "anthropic/claude-fable-5",
            "google/gemini-3-8-flash",
        },
        "Q08": {
            "openai/gpt-6-astra",
            "google/gemini-3-8-flash",
            "anthropic/claude-opus-5-5",
            "anthropic/claude-opus-5",
            "anthropic/claude-fable-5-1",
            "anthropic/claude-opus-4-6",
            "google/gemini-2-5-flash",
            "anthropic/claude-fable-5",
            "anthropic/claude-opus-4-7",
        },
        "Q09": {
            "anthropic/claude-opus-5",
            "anthropic/claude-fable-5-1",
            "anthropic/claude-opus-4-6",
            "openai/gpt-6-astra",
            "google/gemini-3-8-flash",
            "anthropic/claude-fable-5",
            "anthropic/claude-opus-4-7",
        },
        "Q13": {
            "no separated open-weights reasoning winner",
            "moonshot/kimi-k3",
            "zhipu/glm-5-2",
            "zhipu/glm-5-3",
        },
        "Q14": {
            "anthropic/claude-opus-5",
            "anthropic/claude-fable-5-1",
            "anthropic/claude-opus-4-6",
            "meta/muse-spark-1-3",
            "meta/muse-spark-1-1",
        },
        "Q15": {
            "IEITYuan/Yuan-embedding-2.0-en",
            "jcorners/ingot-8b-r3",
            "qwen/qwen3-embedding-8b",
            "kingsoft/qzhou-embedding",
        },
    }

    def members(question_id: str, category: str) -> set[str]:
        return {
            entry.get("model_id") or entry.get("name") or entry["rule"]
            for entry in questions[question_id][category]
        }

    for question_id, approved in approved_acceptable.items():
        assert members(question_id, "acceptable") == approved

    kalm = "tencent/kalm-embedding-gemma3-12b-2511"
    assert kalm in members("Q16", "acceptable")
    assert kalm not in members("Q16", "must_flag")
    assert "google/gemini-3-8-flash" not in members("Q19", "must_flag")

    assert "approved Arena dataset now supplies vision rows" in questions["Q14"]["notes"]
    assert "Harrier is first and KaLM is second" in questions["Q16"]["notes"]
    assert "only the third-place group remains unresolved" in questions["Q16"]["notes"]

    triage = "docs/recall/2026-09-25-model-161-triage.md"
    for question_id in (*approved_acceptable, "Q16", "Q19"):
        assert triage in questions[question_id]["notes"]
        assert "read 2026-09-25" in questions[question_id]["notes"]
