#!/usr/bin/env python3
"""Process one pending Grok Bot release signal.

The hourly workflow calls this script once. Processing one signal per branch
keeps a new-card change out of a score-only pull request.
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import date
from pathlib import Path

import httpx

from decision.sources import CopyStore
from release_signals.contract import ReleaseSignal
from release_signals.pipeline import FetchResult, draft_signal, resolve_signal
from scripts import model_160_evidence as leaderboard_readers
from scripts import refresh_leaderboards

ROOT = Path(__file__).resolve().parents[1]


def _fetch(url: str) -> FetchResult:
    response = httpx.get(
        url,
        headers={"User-Agent": "ModelSpec-Release-Signals/1.0"},
        follow_redirects=True,
        timeout=60,
    )
    response.raise_for_status()
    return FetchResult(
        url=str(response.url),
        body=response.content,
        content_type=response.headers.get("content-type", "application/octet-stream"),
    )


def _next_signal(payload: dict) -> tuple[ReleaseSignal | None, dict | None]:
    signals = payload.get("signals") or []
    if signals:
        return ReleaseSignal.parse(signals[0]), None
    rechecks = payload.get("rechecks") or []
    if rechecks:
        row = rechecks[0]
        return ReleaseSignal.parse(row["signal"]), row
    return None, None


def process(
    pending: Path,
    result_path: Path,
    *,
    root: Path = ROOT,
    audit_path: Path | None = None,
    report_path: Path | None = None,
) -> dict:
    payload = json.loads(pending.read_text(encoding="utf-8"))
    signal, recheck = _next_signal(payload)
    if signal is None:
        result = {"status": "empty"}
    else:
        resolution = resolve_signal(signal, root)
        result = {
            "status": resolution.status,
            "signal_id": signal.signal_id,
            "model_id": resolution.model_id,
            "candidates": list(resolution.candidates),
            "recheck_day": recheck.get("day") if recheck else None,
            "recheck_due": recheck.get("due") if recheck else None,
        }
        if resolution.status == "new":
            drafted = draft_signal(
                signal,
                root=root,
                fetch=_fetch,
                read_date=date.today(),
                discover_huggingface=True,
            )
            result["card"] = str(drafted.card_path.relative_to(root)) if drafted.card_path else None
            result["sources"] = list(drafted.evidence_urls)
            result["firecrawl_credits"] = drafted.firecrawl_credits
            result["gather_failures"] = list(drafted.gather_failures)
            boards, failures = refresh_leaderboards.collect_readings(
                date.today().isoformat(),
                CopyStore(Path(os.environ.get(
                    "MODELSPEC_SOURCE_CACHE", "/tmp/modelspec-source-copies"
                ))),
                (),
            )
            board_matches = []
            for board in boards:
                for row in board.rows:
                    if leaderboard_readers.normalise_name(
                        refresh_leaderboards._subject(row)
                    ) == leaderboard_readers.normalise_name(signal.model_name):
                        board_matches.append({
                            "board": board.key,
                            "benchmarks": sorted(board.benchmark_ids),
                            "source": board.source_url,
                        })
            result["live_board_matches"] = board_matches
            result["live_board_failures"] = [failure.__dict__ for failure in failures]
        elif resolution.status == "existing":
            report = refresh_leaderboards.run(
                observed_at=date.today().isoformat(),
                dry_run=False,
                root=root,
                source_cache=Path(
                    os.environ.get("MODELSPEC_SOURCE_CACHE", "/tmp/modelspec-source-copies")
                ),
            )
            if audit_path:
                refresh_leaderboards.write_audit(audit_path, report.changes)
            if report_path:
                refresh_leaderboards.write_report_json(report_path, report)
            result.update({
                "score_changes": len(report.changes),
                "reconfirmed": len(report.reconfirmed),
                "failures": len(report.failures),
                "quarantined": len(report.quarantined),
            })
    result_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pending", type=Path, required=True)
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--audit-json", type=Path)
    parser.add_argument("--report-json", type=Path)
    args = parser.parse_args()
    result = process(
        args.pending,
        args.result,
        root=args.root,
        audit_path=args.audit_json,
        report_path=args.report_json,
    )
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
