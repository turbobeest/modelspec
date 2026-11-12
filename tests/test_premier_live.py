"""Live premier proposals use private records and the existing admission clauses."""

import json
import subprocess
import sys
from datetime import date
from pathlib import Path

import pytest
import yaml

from scripts import premier_live, premier_slice1
from scripts.premier_slice1 import rank_board
from tests.snapshot_records import SOURCES, evidence, fact

TODAY = date(2026, 10, 4)
BENCH = "terminal_bench_v4_0"


def write_yaml(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(value, sort_keys=False))


def write_card(root, model_id, *, release="2026-01-01", rows=(), status="active", facts=(),
               availability=None):
    path = root / "models" / f"{model_id}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "model_id": model_id, "display_name": model_id, "provider": model_id.split("/")[0],
        "model_type": "llm-chat", "release_date": release, "status": status,
        "licensing": {"open_weights": False},
        "facts": [fact("model", model_id, "model.weights_openness", "closed_weights"), *facts],
        "benchmarks": {"evidence": list(rows)},
    }
    if availability:
        payload = {
            **{key: value for key, value in payload.items() if key != "benchmarks"},
            "availability": availability,
            "benchmarks": payload["benchmarks"],
        }
    path.write_text("---\n" + yaml.safe_dump(payload, sort_keys=False) + "---\nFixture.\n")
    return path


def write_benchmark(root, bench_id, *, domain="software_engineering", direction="higher_is_better"):
    path = root / "benchmarks" / f"{bench_id}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("---\n" + yaml.safe_dump({
        "id": bench_id, "domains": [{"id": domain, "directness": "direct"}],
        "metric": {"unit": "percent", "min_score": 0, "max_score": 100, "direction": direction},
    }) + "---\nFixture board.\n")


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
    write_benchmark(root, BENCH)
    return root


GUARANTEED_VALUES = {
    "model.class": "text-generator",
    "model.input_modalities": ["text"],
    "model.output_modalities": ["text"],
    "model.context_window": 128000,
    "model.max_output_tokens": 8192,
    "model.weights_openness": "closed_weights",
    "licence.commercial_use": "permitted",
    "licence.user_cap": "unbounded",
    "licence.output_training": "prohibited",
    "licence.fine_tuning": "prohibited",
    "origin.lab_jurisdiction": ["US"],
    "origin.base_lineage": [],
    "origin.weights_hosting": ["US"],
    "model.release_date": "2026-01-01",
    "model.lifecycle": "active",
    "feature.tool_calling": True,
    "feature.structured_output": True,
    "feature.effort_controls": False,
    "feature.batch": False,
    "feature.streaming": True,
}


def major_availability(*names, lab_api=False):
    block = {}
    if lab_api:
        block["primary_provider"] = {
            "api_endpoint": "https://lab.example/v1",
            "model_id_on_platform": "wide",
        }
    for name in names:
        block[name] = {"available": True}
    return block


def guaranteed_facts(model_id, *, source="src-lab-docs"):
    return [
        fact("model", model_id, facet, value, source=source)
        for facet, value in GUARANTEED_VALUES.items()
        if facet != "model.weights_openness"
    ]


def log_guaranteed(root, model_id):
    from decision.model import value_hash

    path = root / "verification/log.jsonl"
    lines = []
    for facet, value in GUARANTEED_VALUES.items():
        lines.append(json.dumps({
            "outcome": "verified",
            "date": "2026-09-20",
            "collector": {"agent": "collector-a", "model_family": "family-a", "method": "read"},
            "verifier": {"agent": "verifier-b", "model_family": "family-b", "method": "re-read"},
            "method": "re-read the cited region",
            "target": {
                "kind": "fact",
                "id": f"{model_id}#{facet}",
                "value_hash": value_hash(value),
            },
        }))
    path.write_text(path.read_text() + "\n".join(lines) + "\n")


def add_source(root, source_id, url):
    path = root / "registry/sources.yaml"
    data = yaml.safe_load(path.read_text())
    data["sources"].append({"id": source_id, "url": url})
    write_yaml(path, data)


def write_clause3_card(root, model_id, *, availability, source="src-lab-docs"):
    write_card(
        root, model_id, availability=availability,
        facts=guaranteed_facts(model_id, source=source),
    )
    log_guaranteed(root, model_id)


def clause_numbers(document, model_id):
    row = next(row for row in document["models"] if row["model_id"] == model_id)
    return {clause["clause"] for clause in row["clauses"]}


def pad_board(root, count=10, *, bench=BENCH, status="sunset", lab="pad", base=1):
    """Extra rows so a named board is long enough for a top 10 to exclude someone."""
    for number in range(count):
        mid = f"{lab}/pad-{number:02d}"
        write_card(
            root, mid, status=status,
            rows=[evidence(mid, bench, base + number)],
        )


def test_live_cli_proposes_recent_lab_release_with_clause_2_and_noop(tmp_path):
    root = catalogue(tmp_path)
    write_card(root, "lab/leader", rows=[evidence("lab/leader", BENCH, 90)])
    pad_board(root)
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
        write_card(root, mid, rows=[evidence(mid, BENCH, 90 - number)])
    before = premier_slice1.build(data_dir=root, as_of=TODAY)
    assert len(before["models"]) == 10
    write_card(root, "lab/model-10", rows=[evidence("lab/model-10", BENCH, 95)])
    after = premier_slice1.build(data_dir=root, as_of=TODAY)
    changes = premier_slice1.membership_diff(after, before)
    assert [r["model_id"] for r in changes["added"]] == ["lab/model-10"]
    assert [r["model_id"] for r in changes["removed"]] == ["lab/model-09"]
    assert changes["added"][0]["clauses"][0]["clause"] == 1
    write_card(root, "lab/model-09", rows=[evidence("lab/model-09", BENCH, 82)])
    tied = premier_slice1.build(data_dir=root, as_of=TODAY)
    assert len(tied["models"]) == 11


@pytest.mark.parametrize("bad", [
    {"outcome": None}, {"outcome": "mismatch"}, {"day": "2025-10-03"},
    {"day": "2026-10-05"}, {"source": "unregistered"},
    {"source_url": "https://zap" "ier.com/x"},
])
def test_live_ignores_unverified_stale_future_or_excluded_scores(tmp_path, bad):
    root = catalogue(tmp_path)
    write_card(root, "lab/leader", rows=[evidence("lab/leader", BENCH, 80)])
    pad_board(root)
    write_card(root, "other/unqualified", rows=[
        evidence("other/unqualified", BENCH, 99, **bad),
    ])
    document = premier_slice1.build(data_dir=root, as_of=TODAY)
    assert [row["model_id"] for row in document["models"]] == ["lab/leader"]


def test_live_retires_models_and_preserves_only_explicit_reviewer_additions(tmp_path):
    root = catalogue(tmp_path)
    write_card(root, "lab/retired", status="sunset", rows=[
        evidence("lab/retired", BENCH, 90),
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
        evidence("lab/old-leader", BENCH, 90),
    ])
    pad_board(root)
    write_card(root, "lab/new-release", release="2026-09-29")
    document = premier_slice1.build(data_dir=root, as_of=TODAY)
    assert [row["model_id"] for row in document["models"]] == ["lab/new-release"]
    assert [clause["clause"] for clause in document["models"][0]["clauses"]] == [2]


def test_unregistered_offering_tier_cannot_block_other_admission_clauses(tmp_path):
    root = catalogue(tmp_path)
    write_card(root, "lab/leader", rows=[evidence("lab/leader", BENCH, 90)])
    pad_board(root)
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
        write_card(root, mid, rows=[evidence(mid, BENCH, 90 - number)])
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
    write_card(root, mid, rows=[evidence(mid, BENCH, 80, day="2025-01-01")])
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
    benchmark = root / "benchmarks" / f"{BENCH}.md"
    benchmark.write_text(benchmark.read_text().replace("higher_is_better", "lower_is_better"))
    for number in range(11):
        mid = f"lab/model-{number:02}"
        write_card(root, mid, rows=[evidence(mid, BENCH, number + 1)])
    # Same slug, different model, different recorded version: one named board.
    row = evidence("other/model-00", BENCH, 0)
    row["benchmark_version"] = "2.0"
    write_card(root, "other/model-00", rows=[row])
    document = premier_slice1.build(data_dir=root, as_of=TODAY)
    ids = {row["model_id"] for row in document["models"]}
    assert "other/model-00" in ids and "lab/model-00" in ids
    assert "lab/model-09" not in ids and "lab/model-10" not in ids
    assert len(ids) == 10
    boards = {
        clause["board"]
        for row in document["models"]
        for clause in row["clauses"]
        if clause["clause"] == 1
    }
    assert boards == {"terminal-bench-4.0"}


def test_live_vision_domain_keeps_the_existing_vision_quota(tmp_path):
    root = catalogue(tmp_path)
    write_benchmark(root, "arena_sc_vision")
    write_card(
        root, "lab/vision-leader",
        rows=[evidence("lab/vision-leader", "arena_sc_vision", 90)],
    )
    pad_board(root, bench="arena_sc_vision")
    document = premier_slice1.build(data_dir=root, as_of=TODAY)
    assert document["models"][0]["slice1_group"] == "vision"
    assert document["models"][0]["clauses"][0]["domain"] == "vision"
    assert document["models"][0]["clauses"][0]["board"] == "arena-vision"


def _rows(board_id, count, *, score_of):
    return {
        "id": board_id,
        "domain": "software-engineering",
        "url": "https://board.example.org/results",
        "rows": [
            {
                "name": f"model-{number:02d}",
                "model_id": f"lab/model-{number:02d}",
                "score": score_of(number),
                "date": "2026-08-01",
                "org": "lab",
            }
            for number in range(count)
        ],
    }


def test_board_shorter_than_the_top_10_admits_nobody(monkeypatch):
    monkeypatch.setattr(premier_slice1, "STRICT_BOARD_ROWS", True)
    ranked = rank_board(_rows("terminal-bench-4.0", 10, score_of=lambda n: 100 - n))
    assert len(ranked) == 10
    assert [row["top10"] for row in ranked] == [False] * 10
    approved = rank_board(
        _rows("mteb-eng-v2-rerank", 2, score_of=lambda n: 50 - n),
        minimum_rows=premier_slice1.APPROVED_LINEUP_MINIMUM_ROWS,
    )
    assert [row["top10"] for row in approved] == [True, True]


def test_five_row_board_admits_its_five_by_default():
    ranked = rank_board(_rows("terminal-bench-4.0", 5, score_of=lambda n: 100 - n))
    assert len(ranked) == 5
    assert [row["top10"] for row in ranked] == [True] * 5


def test_live_five_row_board_selects_its_five_by_default(tmp_path):
    root = catalogue(tmp_path)
    for number in range(5):
        mid = f"lab/model-{number:02d}"
        write_card(root, mid, rows=[evidence(mid, BENCH, 100 - number)])
    document = premier_slice1.build(data_dir=root, as_of=TODAY)
    assert [row["model_id"] for row in document["models"]] == [
        f"lab/model-{number:02d}" for number in range(5)
    ]
    assert document["counts"]["clause_1_cards"] == 5


def test_eleven_rows_keep_the_top_10_and_a_tie_at_the_cutoff():
    ranked = rank_board(_rows("terminal-bench-4.0", 11, score_of=lambda n: 100 - n))
    assert [row["top10"] for row in ranked] == [True] * 10 + [False]
    tied = _rows("terminal-bench-4.0", 11, score_of=lambda n: 80 if n >= 9 else 100 - n)
    ranked = rank_board(tied)
    assert sum(row["top10"] for row in ranked) == 11


def test_unmapped_benchmark_does_not_open_a_board(tmp_path):
    root = catalogue(tmp_path)
    write_benchmark(root, "side-quest")
    for number in range(11):
        mid = f"lab/side-{number:02d}"
        write_card(root, mid, rows=[evidence(mid, "side-quest", 100 - number)])
    document = premier_slice1.build(data_dir=root, as_of=TODAY)
    assert document["models"] == []
    assert document["counts"]["clause_1_cards"] == 0


def test_named_board_with_ten_rows_selects_nobody(tmp_path, monkeypatch):
    monkeypatch.setattr(premier_slice1, "STRICT_BOARD_ROWS", True)
    root = catalogue(tmp_path)
    for number in range(10):
        mid = f"lab/model-{number:02d}"
        write_card(root, mid, rows=[evidence(mid, BENCH, 100 - number)])
    document = premier_slice1.build(data_dir=root, as_of=TODAY)
    assert document["models"] == []
    assert document["counts"]["clause_1_cards"] == 0


def test_mapped_boards_are_the_named_slice1_set():
    named = {board["id"] for board in premier_slice1.leaderboards()}
    mapped = set(premier_slice1.SLICE1_BENCHMARK_BOARDS.values()) | {
        "epoch-swe-bench-verified",
        "swe-bench-verified-bash",
    }
    assert mapped <= named
    assert named - mapped == {"matharena-expected", "mteb-multilingual-v2-rerank"}
    assert premier_slice1.slice1_board_id(
        "swe_bench_verified",
        source_url="https://epoch.ai/benchmarks/swe-bench-verified",
    ) == "epoch-swe-bench-verified"
    assert premier_slice1.slice1_board_id(
        "swe_bench_verified",
        source_url="https://www.swebench.com/verified",
        harness="unregistered",
        version="SWE-bench Verified, bash-only (mini-SWE-agent), official leaderboard",
    ) == "swe-bench-verified-bash"
    assert premier_slice1.slice1_board_id(
        "swe_bench_verified",
        source_url="https://www.swebench.com/verified",
        harness="unregistered",
    ) is None
    assert premier_slice1.slice1_board_id(
        "swe_bench_verified",
        source_url="https://www.anthropic.com/news",
    ) is None
    assert premier_slice1.slice1_board_id("aime_2026") is None


def test_card_recorded_providers_satisfy_clause_3(tmp_path):
    root = catalogue(tmp_path)
    write_clause3_card(root, "shelf/wide-model", availability=major_availability(
        "aws_bedrock", "google_vertex_ai", lab_api=True,
    ))
    document = premier_slice1.build(data_dir=root, as_of=TODAY)
    assert clause_numbers(document, "shelf/wide-model") == {3}


def test_lab_api_switch_drops_a_card_that_reaches_three_only_through_it(tmp_path, monkeypatch):
    root = catalogue(tmp_path)
    write_clause3_card(root, "shelf/wide-model", availability=major_availability(
        "aws_bedrock", "google_vertex_ai", lab_api=True,
    ))
    monkeypatch.setattr(premier_live, "COUNT_LAB_API", False)
    document = premier_slice1.build(data_dir=root, as_of=TODAY)
    assert document["models"] == []
    assert document["counts"]["clause_3_pool"] == 0


def test_an_offering_fills_out_the_card_providers(tmp_path):
    root = catalogue(tmp_path)
    mid = "shelf/wide-model"
    write_clause3_card(root, mid, availability=major_availability(
        "aws_bedrock", "google_vertex_ai",
    ))
    write_yaml(root / "offerings/sambanova/shelf/wide-model.yaml", [{
        "model": mid, "provider": "sambanova", "region": "global", "tier": "standard",
        "facts": [],
    }])
    document = premier_slice1.build(data_dir=root, as_of=TODAY)
    assert clause_numbers(document, mid) == {3}


def test_cite_only_guaranteed_facts_follow_the_approved_switch(tmp_path, monkeypatch):
    root = catalogue(tmp_path)
    add_source(root, "src-cite", "https://www.anthropic.com/docs/models")
    mid = "shelf/cited-model"
    write_clause3_card(
        root, mid, source="src-cite",
        availability=major_availability("aws_bedrock", "google_vertex_ai", "groq"),
    )
    admitted = premier_slice1.build(data_dir=root, as_of=TODAY)
    assert clause_numbers(admitted, mid) == {3}
    monkeypatch.setattr(premier_live, "CITE_ONLY_FACTS_COUNT_AS_VERIFIED", False)
    refused = premier_slice1.build(data_dir=root, as_of=TODAY)
    assert refused["models"] == []
    assert refused["counts"]["clause_3_pool"] == 0


def test_snapshot_cited_fact_without_log_verification_does_not_count(tmp_path):
    root = catalogue(tmp_path)
    add_source(root, "src-cite", "https://www.anthropic.com/docs/models")
    mid = "shelf/unlogged-cited"
    write_card(
        root, mid,
        availability=major_availability("aws_bedrock", "google_vertex_ai", "groq"),
        facts=guaranteed_facts(mid, source="src-cite"),
    )
    document = premier_slice1.build(data_dir=root, as_of=TODAY)
    assert document["models"] == []
    assert document["counts"]["clause_3_pool"] == 0


def test_fixture_follows_the_approved_rule(tmp_path):
    root = catalogue(tmp_path)
    for number in range(11):
        mid = f"lab/seat-{number:02d}"
        write_card(root, mid, rows=[evidence(mid, BENCH, 100 - number)])
    write_benchmark(root, "side-quest")
    for number in range(11):
        mid = f"quest/side-{number:02d}"
        write_card(root, mid, rows=[evidence(mid, "side-quest", 100 - number)])
    write_card(root, "lab/fresh", release="2026-09-29")
    write_clause3_card(root, "shelf/wide-model", availability=major_availability(
        "aws_bedrock", "google_vertex_ai", lab_api=True,
    ))
    document = premier_slice1.build(data_dir=root, as_of=TODAY)
    expected = {f"lab/seat-{number:02d}" for number in range(10)} | {
        "lab/fresh", "shelf/wide-model",
    }
    assert {row["model_id"] for row in document["models"]} == expected
    for number in range(10):
        assert 1 in clause_numbers(document, f"lab/seat-{number:02d}")
    assert 2 in clause_numbers(document, "lab/fresh")
    assert 3 in clause_numbers(document, "shelf/wide-model")


# Frontier quota is 12. Fifteen active clause-1 cards is quota + 3.
# The three the quota cuts are the worst sort_key: ranks 8, 9 and 10 on
# the terminal-bench board. Arena ranks 1-5 sort ahead of those.
_TOP10 = {f"lab/seat-{number:02d}" for number in range(15)}
_QUOTA_CUT = {"lab/seat-07", "lab/seat-08", "lab/seat-09"}
_QUOTA_WHY = "clause 1 on frontier-generation; outside that group's slice-1 quota"
_CLAUSE2_WHY = (
    "clause 2; among the three newest lab releases in the "
    "window and not needed to fill a quota"
)
_APPROVED_RULE = (
    "Top 10 of its class on a slice-1 board, after collapsing effort "
    "settings of the same model."
)
_LIVE_RULE = (
    _APPROVED_RULE
    + " A current top 10 stays when its group quota is full."
    + " The quota limits only seats with no board row."
)


def _overfull_frontier(tmp_path):
    root = catalogue(tmp_path)
    write_benchmark(root, "arena_elo_style_control")
    write_benchmark(root, "swe_bench_pro")
    for number in range(10):
        mid = f"lab/seat-{number:02d}"
        write_card(root, mid, rows=[evidence(mid, BENCH, 100 - number)])
    for number in range(10, 15):
        mid = f"lab/seat-{number:02d}"
        write_card(
            root, mid,
            rows=[evidence(mid, "arena_elo_style_control", 110 - number)],
        )
    write_card(
        root, "lab/retired", status="sunset",
        rows=[evidence("lab/retired", "swe_bench_pro", 99)],
    )
    # 2026-08-15 is inside the 90-day clause 2 window and outside the five-day
    # protection, so a full frontier quota leaves this card a near-miss.
    write_card(root, "lab/recent", release="2026-08-15")
    return root


def _ids(document):
    return {row["model_id"] for row in document["models"]}


def test_live_keeps_every_current_top_10_past_a_full_quota(tmp_path):
    document = premier_slice1.build(data_dir=_overfull_frontier(tmp_path), as_of=TODAY)
    assert _ids(document) == _TOP10
    assert "lab/recent" not in _ids(document)
    assert "lab/retired" not in _ids(document)
    assert {row["model_id"] for row in document["archived"]} == {"lab/retired"}
    assert document["counts"]["over_quota_top10"] == 3
    assert document["counts"]["over_quota_top10_by_group"] == {"frontier-generation": 3}
    assert document["rule"][0] == _LIVE_RULE
    assert [row["why"] for row in document["near_misses"]] == [_CLAUSE2_WHY]
    assert all(_QUOTA_WHY not in row["why"] for row in document["near_misses"])
    recent = next(row for row in document["near_misses"] if row["model_id"] == "lab/recent")
    assert recent["why"] == _CLAUSE2_WHY
    assert recent["slice1_group"] == "frontier-generation"


def test_quota_cuts_top10_reproduces_the_approval_time_cut(tmp_path, monkeypatch):
    monkeypatch.setattr(premier_slice1, "KEEP_EVERY_CURRENT_TOP10", False)
    root = _overfull_frontier(tmp_path)
    document = premier_slice1.build(data_dir=root, as_of=TODAY)
    assert _ids(document) == _TOP10 - _QUOTA_CUT
    reasons = {row["model_id"]: row["why"] for row in document["near_misses"]}
    assert set(reasons) == _QUOTA_CUT | {"lab/recent"}
    for model_id in _QUOTA_CUT:
        assert reasons[model_id] == _QUOTA_WHY
    assert reasons["lab/recent"] == _CLAUSE2_WHY
    assert document["counts"]["over_quota_top10"] == 0
    assert document["counts"]["over_quota_top10_by_group"] == {}
    assert document["rule"][0] == _APPROVED_RULE
    assert "lab/retired" not in _ids(document)

    output = tmp_path / "proposal.yaml"
    diff = tmp_path / "diff.json"
    result = subprocess.run([
        sys.executable, str(Path(premier_slice1.__file__)),
        "--data-dir", str(root),
        "--as-of", TODAY.isoformat(),
        "--quota-cuts-top10",
        "--output", str(output),
        "--diff", str(diff),
    ], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    proposed = yaml.safe_load(output.read_text())
    assert {row["model_id"] for row in proposed["models"]} == _TOP10 - _QUOTA_CUT
    assert proposed["counts"]["over_quota_top10"] == 0
    assert proposed["rule"][0] == _APPROVED_RULE


def test_over_quota_count_skips_a_top10_another_clause_keeps(tmp_path, monkeypatch):
    """The count is seats this rule keeps. The time window already keeps the new one."""
    monkeypatch.setitem(premier_slice1.QUOTA, "frontier-generation", 1)
    root = catalogue(tmp_path)
    write_card(root, "lab/best", rows=[evidence("lab/best", BENCH, 90)])
    write_card(root, "lab/old-extra", rows=[evidence("lab/old-extra", BENCH, 80)])
    write_card(
        root, "lab/new-top", release="2026-09-20",
        rows=[evidence("lab/new-top", BENCH, 70)],
    )
    kept = premier_slice1.build(data_dir=root, as_of=TODAY)
    assert _ids(kept) == {"lab/best", "lab/old-extra", "lab/new-top"}
    assert kept["counts"]["over_quota_top10"] == 1
    assert kept["counts"]["over_quota_top10_by_group"] == {"frontier-generation": 1}
    monkeypatch.setattr(premier_slice1, "KEEP_EVERY_CURRENT_TOP10", False)
    cut = premier_slice1.build(data_dir=root, as_of=TODAY)
    assert _ids(cut) == {"lab/best", "lab/new-top"}
    assert cut["counts"]["over_quota_top10"] == 0
    reasons = {row["model_id"]: row["why"] for row in cut["near_misses"]}
    assert reasons["lab/old-extra"] == _QUOTA_WHY
