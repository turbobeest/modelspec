"""Live premier proposals use private records and the existing admission clauses."""

import json
import subprocess
import sys
from datetime import date
from pathlib import Path

import pytest
import yaml

from scripts import premier_slice1
from tests.snapshot_records import SOURCES, evidence, fact

TODAY = date(2026, 10, 4)


def write_yaml(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(value, sort_keys=False))


def write_card(root, model_id, *, release="2026-01-01", rows=(), status="active", facts=()):
    path = root / "models" / f"{model_id}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("---\n" + yaml.safe_dump({
        "model_id": model_id, "display_name": model_id, "provider": model_id.split("/")[0],
        "model_type": "llm-chat", "release_date": release, "status": status,
        "licensing": {"open_weights": False},
        "facts": [fact("model", model_id, "model.weights_openness", "closed_weights"), *facts],
        "benchmarks": {"evidence": list(rows)},
    }, sort_keys=False) + "---\nFixture.\n")
    return path


def catalogue(tmp_path):
    root = tmp_path / "data"
    write_yaml(root / "registry/sources.yaml", {
        "schema_version": 1, "sources": [{"id": k, "url": v} for k, v in SOURCES.items()],
    })
    (root / "verification").mkdir()
    (root / "verification/log.jsonl").write_text("")
    write_yaml(root / "premier/inputs/slice-2.yaml", {
        "budget": {"quota_per_class": 3},
        "widely_offered": {"minimum_major_providers": 3},
        "local": {"max_memory_gb": 24, "candidates": []},
    })
    write_yaml(root / "premier/slice-1.yaml", {"models": []})
    path = root / "benchmarks/quality.md"
    path.parent.mkdir()
    path.write_text("---\n" + yaml.safe_dump({
        "id": "quality", "domains": [{"id": "software_engineering", "directness": "direct"}],
        "metric": {"unit": "percent", "min_score": 0, "max_score": 100,
                   "direction": "higher_is_better"},
    }) + "---\nFixture board.\n")
    return root


def test_live_cli_proposes_recent_lab_release_with_clause_2_and_noop(tmp_path):
    root = catalogue(tmp_path)
    write_card(root, "lab/leader", rows=[evidence("lab/leader", "quality", 90)])
    write_card(root, "lab/new-release", release="2026-09-29")
    output, diff = tmp_path / "proposal.yaml", tmp_path / "diff.json"
    command = [sys.executable, str(Path(premier_slice1.__file__)), "--data-dir", str(root),
               "--as-of", TODAY.isoformat(), "--output", str(output), "--diff", str(diff)]
    before = (root / "premier/slice-1.yaml").read_bytes()
    result = subprocess.run(command, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    changes = json.loads(diff.read_text())
    added = {row["model_id"]: row for row in changes["added"]}
    assert set(added) == {"lab/leader", "lab/new-release"}
    assert [c["clause"] for c in added["lab/new-release"]["clauses"]] == [2]
    assert changes["removed"] == []
    assert changes["changed"] is True
    assert (root / "premier/slice-1.yaml").read_bytes() == before
    (root / "premier/slice-1.yaml").write_bytes(output.read_bytes())
    result = subprocess.run(command, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert json.loads(diff.read_text()) == {"added": [], "removed": [], "changed": False}


@pytest.mark.parametrize("flag", ["--output", "--diff"])
def test_live_cli_cannot_overwrite_the_reviewed_input(tmp_path, flag):
    root = catalogue(tmp_path)
    target = root / "premier/slice-1.yaml"
    before = target.read_bytes()
    result = subprocess.run([
        sys.executable, str(Path(premier_slice1.__file__)), "--data-dir", str(root),
        flag, str(target),
    ], capture_output=True, text=True)
    assert result.returncode == 2
    assert target.read_bytes() == before


def test_live_score_change_moves_a_seat_and_keeps_cutoff_ties(tmp_path):
    root = catalogue(tmp_path)
    for number in range(11):
        mid = f"lab/model-{number:02}"
        write_card(root, mid, rows=[evidence(mid, "quality", 90 - number)])
    before = premier_slice1.build(data_dir=root, as_of=TODAY)
    assert len(before["models"]) == 10
    write_card(root, "lab/model-10", rows=[evidence("lab/model-10", "quality", 95)])
    after = premier_slice1.build(data_dir=root, as_of=TODAY)
    changes = premier_slice1.membership_diff(after, before)
    assert [r["model_id"] for r in changes["added"]] == ["lab/model-10"]
    assert [r["model_id"] for r in changes["removed"]] == ["lab/model-09"]
    assert changes["added"][0]["clauses"][0]["clause"] == 1
    write_card(root, "lab/model-09", rows=[evidence("lab/model-09", "quality", 82)])
    tied = premier_slice1.build(data_dir=root, as_of=TODAY)
    assert len(tied["models"]) == 11


@pytest.mark.parametrize("bad", [
    {"outcome": None}, {"outcome": "mismatch"}, {"day": "2025-10-03"},
    {"day": "2026-10-05"}, {"source": "unregistered"},
    {"source_url": "https://zap" "ier.com/x"},
])
def test_live_ignores_unverified_stale_future_or_excluded_scores(tmp_path, bad):
    root = catalogue(tmp_path)
    write_card(root, "lab/leader", rows=[evidence("lab/leader", "quality", 80)])
    write_card(root, "other/unqualified", rows=[
        evidence("other/unqualified", "quality", 99, **bad),
    ])
    document = premier_slice1.build(data_dir=root, as_of=TODAY)
    assert [row["model_id"] for row in document["models"]] == ["lab/leader"]


def test_live_retires_models_and_preserves_only_explicit_reviewer_additions(tmp_path):
    root = catalogue(tmp_path)
    write_card(root, "lab/retired", status="sunset", rows=[
        evidence("lab/retired", "quality", 90),
    ])
    write_card(root, "lab/reviewed")
    write_card(root, "lab/packet")
    baseline = {"models": [
        {"model_id": "lab/reviewed", "clauses": [{"clause": 4, "reason": "Jamie added it."}]},
        {"model_id": "lab/packet", "clauses": [
            {"clause": 4, "reason": "Admission packet for human review"},
        ]},
        {"model_id": "lab/retired", "clauses": [{"clause": 1}]},
    ]}
    write_yaml(root / "premier/slice-1.yaml", baseline)
    document = premier_slice1.build(data_dir=root, as_of=TODAY)
    assert [row["model_id"] for row in document["models"]] == ["lab/reviewed"]
    changes = premier_slice1.membership_diff(document, baseline)
    assert [row["model_id"] for row in changes["removed"]] == ["lab/packet", "lab/retired"]
    assert all(row["clauses"] and row["reason"] for row in changes["removed"])


def test_recent_release_qualifies_through_a_retired_labs_past_year_leader(tmp_path):
    root = catalogue(tmp_path)
    write_card(root, "lab/old-leader", status="sunset", rows=[
        evidence("lab/old-leader", "quality", 90),
    ])
    write_card(root, "lab/new-release", release="2026-09-29")
    document = premier_slice1.build(data_dir=root, as_of=TODAY)
    assert [row["model_id"] for row in document["models"]] == ["lab/new-release"]
    assert [clause["clause"] for clause in document["models"][0]["clauses"]] == [2]


def test_unregistered_offering_tier_cannot_block_other_admission_clauses(tmp_path):
    root = catalogue(tmp_path)
    write_card(root, "lab/leader", rows=[evidence("lab/leader", "quality", 90)])
    write_card(root, "lab/new-release", release="2026-09-29")
    write_yaml(root / "offerings/sambanova/lab/leader.yaml", [{
        "model": "lab/leader", "provider": "sambanova", "region": "global",
        "tier": "Tier0", "facts": [],
    }])
    document = premier_slice1.build(data_dir=root, as_of=TODAY)
    assert {row["model_id"] for row in document["models"]} == {"lab/leader", "lab/new-release"}


def test_live_uses_current_verified_prices_for_budget_seats(tmp_path):
    root = catalogue(tmp_path)
    for number in range(14):
        mid = f"lab/model-{number:02}"
        write_card(root, mid, rows=[evidence(mid, "quality", 90 - number)])
        oid = f"sambanova/{mid}/global/standard"
        write_yaml(root / "offerings/sambanova" / f"{mid}.yaml", [{
            "model": mid, "provider": "sambanova", "region": "global", "tier": "standard",
            "facts": [fact("offering", oid, f"offering.price.{kind}", float(number + 1))
                      for kind in ("input", "output")],
        }])
    before = premier_slice1.build(data_dir=root, as_of=TODAY)
    assert "lab/model-13" not in {row["model_id"] for row in before["models"]}
    mid = "lab/model-13"
    oid = f"sambanova/{mid}/global/standard"
    path = root / "offerings/sambanova" / f"{mid}.yaml"
    offers = yaml.safe_load(path.read_text())
    offers[0]["facts"] = [fact("offering", oid, f"offering.price.{kind}", 0.01)
                          for kind in ("input", "output")]
    write_yaml(path, offers)
    after = premier_slice1.build(data_dir=root, as_of=TODAY)
    added = premier_slice1.membership_diff(after, before)["added"]
    assert [row["model_id"] for row in added] == [mid]
    assert [clause["clause"] for clause in added[0]["clauses"]] == [5]


def test_budget_clause_does_not_add_the_frontier_one_year_cutoff(tmp_path):
    root = catalogue(tmp_path)
    mid = "lab/budget-model"
    write_card(root, mid, rows=[evidence(mid, "quality", 80, day="2025-01-01")])
    oid = f"sambanova/{mid}/global/standard"
    write_yaml(root / "offerings/sambanova" / f"{mid}.yaml", [{
        "model": mid, "provider": "sambanova", "region": "global", "tier": "standard",
        "facts": [fact("offering", oid, f"offering.price.{kind}", 0.1)
                  for kind in ("input", "output")],
    }])
    document = premier_slice1.build(data_dir=root, as_of=TODAY)
    assert [row["model_id"] for row in document["models"]] == [mid]
    assert [clause["clause"] for clause in document["models"][0]["clauses"]] == [5]


def test_live_board_respects_direction_versions_and_model_identity(tmp_path):
    root = catalogue(tmp_path)
    benchmark = root / "benchmarks/quality.md"
    benchmark.write_text(benchmark.read_text().replace("higher_is_better", "lower_is_better"))
    for number in range(11):
        mid = f"lab/model-{number:02}"
        write_card(root, mid, rows=[evidence(mid, "quality", number + 1)])
    # The same slug at a different lab is a different model, on another version.
    row = evidence("other/model-00", "quality", 99)
    row["benchmark_version"] = "2.0"
    write_card(root, "other/model-00", rows=[row])
    document = premier_slice1.build(data_dir=root, as_of=TODAY)
    ids = {row["model_id"] for row in document["models"]}
    assert "lab/model-00" in ids and "other/model-00" in ids
    assert "lab/model-10" not in ids
    assert len(ids) == 11
