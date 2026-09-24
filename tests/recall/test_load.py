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
