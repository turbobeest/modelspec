"""Frozen v1 output captured before MODEL-134 changes at 76eabc11."""

import importlib.util
import json
from pathlib import Path

from pipeline.ranking import build_candidates, rank_report
from schema.card import ModelCard
from schema.graph import CollectingSink

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/decision/v1-rank.json"


def v1_output():
    # Synthetic inputs exercise legacy scores, reviewed evidence and missing evidence.
    cards = [
        ModelCard.model_validate(
            {
                "identity": {
                    "model_id": f"fake-lab/{name}",
                    "display_name": name,
                    "provider": "fake-lab",
                    "model_type": "llm-chat",
                },
                "benchmarks": {"scores": scores, "evidence": evidence},
            }
        )
        for name, scores, evidence in [
            (
                "legacy",
                {"humaneval": 80, "scicode": 45, "swe_bench_verified": 40, "live_code_bench": 50},
                [],
            ),
            (
                "reviewed",
                {"humaneval": 60, "scicode": 35, "swe_bench_verified": 30, "live_code_bench": 40},
                [
                    {
                        "benchmark_id": "humaneval",
                        "model_id_as_evaluated": "Fake reviewed",
                        "score": 90,
                        "unit": "%",
                        "source_url": "https://example.invalid/result",
                        "source_kind": "benchmark_author",
                        "evidence_date": "2026-09-23",
                        "date_type": "published",
                        "verified_at": "2026-09-24",
                    }
                ],
            ),
            ("unknown", {}, []),
        ]
    ]
    candidates = build_candidates(cards, CollectingSink())
    spec = importlib.util.spec_from_file_location(
        "decision_compat_rank_service", ROOT / "api/worker/src/rank_service.py"
    )
    service = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(service)
    build = {
        "commit": "76eabc11",
        "built_at": "2026-09-24T00:00:00Z",
        "export_schema_version": "3.0",
    }
    status, answer = service.rank(
        {"use_case": "coding"},
        {"build": build, "candidates": [c.to_json() for c in candidates]},
        {"hardware": []},
        "76eabc11",
        "https://example.invalid",
    )
    return {"pipeline": rank_report(candidates, "coding"), "status": status, "answer": answer}


def test_v1_rank_output_matches_pre_change_golden():
    actual = v1_output()
    assert actual["status"] == 200
    assert actual["pipeline"]["ranked"]
    assert actual == json.loads(FIXTURE.read_text())
