#!/usr/bin/env python3
"""Process one pending Grok Bot release-signal work item.

The hourly workflow calls this script once per matrix item. Processing one item
per branch keeps unrelated card changes out of the same pull request.
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import date
from pathlib import Path

import httpx

from release_signals.contract import ReleaseSignal
from release_signals.pipeline import (
    FetchResult,
    draft_signal,
    gather_signal,
    require_allowed_source,
    resolve_signal,
    update_existing_card,
)
from scripts import refresh_leaderboards

ROOT = Path(__file__).resolve().parents[1]


def _fetch(url: str) -> FetchResult:
    require_allowed_source(url)
    response = httpx.get(
        url,
        headers={"User-Agent": "ModelSpec-Release-Signals/1.0"},
        follow_redirects=True,
        timeout=60,
    )
    response.raise_for_status()
    result = FetchResult(
        url=str(response.url),
        body=response.content,
        content_type=response.headers.get("content-type", "application/octet-stream"),
    )
    require_allowed_source(result.url)
    return result


def work_items(payload: dict) -> list[dict[str, object]]:
    """Return every pending signal and due re-check as an isolated work item."""
    items = [
        {
            "signal_id": ReleaseSignal.parse(row).signal_id,
            "recheck_day": 0,
            "pr_url": None,
        }
        for row in payload.get("signals") or []
    ]
    items.extend(
        {
            "signal_id": ReleaseSignal.parse(row["signal"]).signal_id,
            "recheck_day": int(row["day"]),
            "pr_url": row.get("pr_url"),
        }
        for row in payload.get("rechecks") or []
    )
    return items


def _select_signal(
    payload: dict, *, signal_id: str | None, recheck_day: int | None,
) -> tuple[ReleaseSignal | None, dict | None]:
    candidates: list[tuple[ReleaseSignal, dict | None]] = [
        (ReleaseSignal.parse(row), None) for row in payload.get("signals") or []
    ]
    candidates.extend(
        (ReleaseSignal.parse(row["signal"]), row)
        for row in payload.get("rechecks") or []
    )
    if signal_id is None:
        return candidates[0] if candidates else (None, None)
    matches = [
        (signal, recheck) for signal, recheck in candidates
        if signal.signal_id == signal_id
        and (0 if recheck is None else int(recheck["day"])) == (recheck_day or 0)
    ]
    if len(matches) != 1:
        raise ValueError(
            f"pending work item is not unique: signal_id={signal_id!r}, "
            f"recheck_day={recheck_day or 0}"
        )
    return matches[0]


def process(
    pending: Path,
    result_path: Path,
    *,
    root: Path = ROOT,
    audit_path: Path | None = None,
    report_path: Path | None = None,
    signal_id: str | None = None,
    recheck_day: int | None = None,
    closed_unmerged_pr: str | None = None,
) -> dict:
    payload = json.loads(pending.read_text(encoding="utf-8"))
    signal, recheck = _select_signal(
        payload, signal_id=signal_id, recheck_day=recheck_day
    )
    if signal is None:
        result = {"status": "empty"}
    elif closed_unmerged_pr:
        if recheck is None or recheck.get("pr_url") != closed_unmerged_pr:
            raise ValueError("a closed-unmerged PR must belong to the selected re-check")
        result = {
            "status": "closed_unmerged",
            "signal_id": signal.signal_id,
            "model_id": None,
            "candidates": [],
            "recheck_day": recheck.get("day"),
            "recheck_due": recheck.get("due"),
            "pr_url": closed_unmerged_pr,
            "reason": "the original new-model PR was closed without merge",
        }
    else:
        resolution = resolve_signal(signal, root)
        result = {
            "status": resolution.status,
            "signal_id": signal.signal_id,
            "model_id": resolution.model_id,
            "candidates": list(resolution.candidates),
            "recheck_day": recheck.get("day") if recheck else None,
            "recheck_due": recheck.get("due") if recheck else None,
            "pr_url": recheck.get("pr_url") if recheck else None,
        }
        if resolution.status == "uncertain":
            result["reason"] = resolution.reason
        if resolution.status == "new":
            drafted = draft_signal(
                signal,
                root=root,
                fetch=_fetch,
                read_date=date.today(),
                discover_huggingface=True,
            )
            if drafted.resolution.status == "uncertain":
                result.update({
                    "status": "uncertain",
                    "model_id": None,
                    "candidates": list(drafted.resolution.candidates),
                    "reason": drafted.resolution.reason,
                })
                result_path.write_text(
                    json.dumps(result, indent=2) + "\n", encoding="utf-8"
                )
                return result
            result["card"] = str(drafted.card_path.relative_to(root)) if drafted.card_path else None
            result["sources"] = list(drafted.evidence_urls)
            result["firecrawl_credits"] = drafted.firecrawl_credits
            result["gather_failures"] = list(drafted.gather_failures)
            report = refresh_leaderboards.run(
                observed_at=date.today().isoformat(),
                dry_run=False,
                root=root,
                source_cache=Path(os.environ.get(
                    "MODELSPEC_SOURCE_CACHE", "/tmp/modelspec-source-copies"
                )),
                model_ids=(resolution.model_id,),
                add_missing=True,
            )
            if report_path:
                refresh_leaderboards.write_report_json(report_path, report)
            result.update({
                "evidence_added": report.added,
                "failures": len(report.failures),
                "quarantined": len(report.quarantined),
            })
        elif resolution.status == "existing":
            gathered = gather_signal(
                signal,
                root=root,
                fetch=_fetch,
                discover_huggingface=True,
            )
            if gathered.resolution.status == "uncertain":
                result.update({
                    "status": "uncertain",
                    "model_id": None,
                    "candidates": list(gathered.resolution.candidates),
                    "reason": gathered.resolution.reason,
                })
                result_path.write_text(
                    json.dumps(result, indent=2) + "\n", encoding="utf-8"
                )
                return result
            result["sources"] = list(gathered.evidence_urls)
            result["gather_failures"] = list(gathered.gather_failures)
            result["card"] = str(update_existing_card(
                gathered, root=root, read_date=date.today()
            ).relative_to(root))
            report = refresh_leaderboards.run(
                observed_at=date.today().isoformat(),
                dry_run=False,
                root=root,
                source_cache=Path(
                    os.environ.get("MODELSPEC_SOURCE_CACHE", "/tmp/modelspec-source-copies")
                ),
                model_ids=(resolution.model_id,),
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
    parser.add_argument("--signal-id")
    parser.add_argument("--recheck-day", type=int)
    parser.add_argument("--closed-unmerged-pr")
    args = parser.parse_args()
    result = process(
        args.pending,
        args.result,
        root=args.root,
        audit_path=args.audit_json,
        report_path=args.report_json,
        signal_id=args.signal_id,
        recheck_day=args.recheck_day,
        closed_unmerged_pr=args.closed_unmerged_pr,
    )
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
