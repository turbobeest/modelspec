"""The slice-1 premier list is the script's output, and every entry has a card."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
YAML_PATH = ROOT / "premier" / "slice-1.yaml"
SCRIPT = ROOT / "scripts" / "premier_slice1.py"


def test_script_reproduces_the_yaml() -> None:
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr


def test_every_entry_has_a_card_and_evidence() -> None:
    document = yaml.safe_load(YAML_PATH.read_text())
    assert document["status"] == "pending-jamie-approval"
    models = document["models"]
    assert 24 <= len(models) <= 50
    ids = [row["model_id"] for row in models]
    assert len(ids) == len(set(ids))
    assert "typesafe/jev-1-13" in ids
    archived = {row["model_id"] for row in document["archived"]}
    assert archived.isdisjoint(ids)
    for row in models:
        assert row["class"]
        assert row["clauses"]
        provider, name = row["model_id"].split("/", 1)
        path = ROOT / "models" / provider / f"{name}.md"
        text = path.read_text(encoding="utf-8")
        assert f"model_id: {row['model_id']}" in text
        for clause in row["clauses"]:
            if clause["clause"] == 1:
                assert clause["url"].startswith("https://")
                assert clause["read_date"] == "2026-09-24"
                assert clause["rank"] <= 10


def test_slice_2_adds_budget_local_and_embedding_coverage_by_rule() -> None:
    document = yaml.safe_load(YAML_PATH.read_text())
    ids = {row["model_id"] for row in document["models"]}

    # Recall names must enter through a general clause, never a reviewer list.
    expected = {
        "deepseek/deepseek-flash",
        "deepseek/deepseek-v3-1",
        "openai/gpt-6-luna",
        "google/gemma-4-26b-a4b-it",
        "google/gemma-4-31b-it",
        "google/gemma-4-e2b-it",
        "google/gemma-4-e4b-it",
        "microsoft/phi-4",
    }
    assert expected <= ids

    rows = {row["model_id"]: row for row in document["models"]}
    assert any(c["clause"] == 3 for c in rows["deepseek/deepseek-v3-1"]["clauses"])
    assert any(c["clause"] == 5 for c in rows["deepseek/deepseek-flash"]["clauses"])
    assert any(c["clause"] == 5 for c in rows["google/gemini-2-5-flash"]["clauses"])
    for model_id in expected & {
        "google/gemma-4-26b-a4b-it",
        "google/gemma-4-31b-it",
        "google/gemma-4-e2b-it",
        "google/gemma-4-e4b-it",
        "microsoft/phi-4",
    }:
        assert any(c["clause"] == 6 for c in rows[model_id]["clauses"])

    embeddings = [row for row in document["models"] if row["slice1_group"] == "embedding"]
    assert len(embeddings) >= 6
