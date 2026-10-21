"""Exercise the six input restorations with synthetic public test records only."""

from __future__ import annotations

import importlib.util
from dataclasses import replace
from datetime import date
from pathlib import Path
from types import SimpleNamespace

from decision import snapshot
from tests.snapshot_records import SOURCES, evidence, model


def main():
    path = Path(__file__).with_name("audit_exports.py")
    loader = importlib.util.spec_from_file_location("audit_exports", path)
    audit = importlib.util.module_from_spec(loader)
    loader.loader.exec_module(audit)
    rows = snapshot.SnapshotInputs(
        models=[model("lab/alpha")],
        evidence=[evidence("lab/alpha", "swe_bench_pro", 55.0)],
        sources=SOURCES,
        benchmark_domains={"swe_bench_pro": [("software_engineering", "direct")]},
        benchmark_metadata={
            "swe_bench_pro": {
                "sample_size": 100,
                "random_baseline": 0,
                "direction": "higher_is_better",
            }
        },
    )
    verified = snapshot.build_snapshot(rows, as_of=date(2026, 10, 21)).content
    cited = snapshot.build_snapshot(
        replace(rows, sources=dict.fromkeys(SOURCES, "https://docs.x.ai/docs/models")),
        as_of=date(2026, 10, 21),
    ).content
    captured = []

    def capture(built, **kwargs):
        captured.append(built.content)
        return snapshot.load_built_snapshot(built, **kwargs)

    proxy = SimpleNamespace(**vars(snapshot))
    proxy.load_built_snapshot = capture
    runs = 0
    for candidate, baseline in ((cited, verified), (verified, cited)):
        before = audit.unpack(candidate, snapshot)
        target = audit.unpack(baseline, snapshot)
        assert all("kind" not in row for row in before.values())
        for facts, benchmarks in ((False, True), (True, False), (True, True)):
            restored = audit.restore(candidate, baseline, proxy, facts=facts, benchmarks=benchmarks)
            content = captured[-1]
            for rid, record in before.items():
                selected = ("facet" in record and facts) or (
                    "benchmark_id" in record and benchmarks
                )
                assert restored.record(rid) == (target[rid] if selected else record)
            for field, key in (
                ("facet", "cited_fact_records"),
                ("benchmark_id", "cited_evidence_records"),
            ):
                expected = sorted(
                    rid
                    for rid in before
                    if field in before[rid]
                    and (restored.record(rid).get("citation") or {}).get("status") == "cited"
                )
                assert (key in content) == bool(expected)
                assert content.get(key, []) == expected
            score = restored.evidence("lab/alpha", "swe_bench_pro")[0]
            expected_score = target[score.record_id] if benchmarks else before[score.record_id]
            assert score.verified == (expected_score["verification"] is not None)
            assert score.cited == (expected_score["verification"] is None)
            expected_capability = baseline["capability"] if benchmarks else candidate["capability"]
            assert content["capability"] == expected_capability
            expected_cited_facts = content.get("cited_fact_records", [])
            assert list(restored.cited_facts("lab/alpha")) == expected_cited_facts
            runs += 1
    print(
        f"PASS: {runs} directional restorations; exact record metadata, separate citation indexes, "
        "absent empty keys, runtime evidence verified/cited flags, and fitted capability payload"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
