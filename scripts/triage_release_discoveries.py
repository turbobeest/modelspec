#!/usr/bin/env python3
"""Classify an exported discovery issue list without contacting GitHub.

This command only reads local files and writes a dry-run report. It has no
apply mode. Pass a private catalogue explicitly to check for carded releases.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from release_signals.contract import ReleaseSignal, SignalError  # noqa: E402
from release_signals.watch import load_catalogue  # noqa: E402
from scripts.release_watch_filter import canonical_release, rejection_reason  # noqa: E402

CLASSIFICATIONS = ("duplicate", "superseded", "real", "noise")
JSON_FENCE = re.compile(r"^```json[ \t]*\r?\n(.*?)^```[ \t]*$", re.MULTILINE | re.DOTALL)
SAMPLE_LIMIT = 5


def _signal(body: str) -> ReleaseSignal:
    blocks = JSON_FENCE.findall(body)
    if len(blocks) != 1:
        raise SignalError("expected exactly one JSON signal block")
    try:
        value = json.loads(blocks[0])
    except json.JSONDecodeError as exc:
        raise SignalError("signal block is not valid JSON") from exc
    try:
        return ReleaseSignal.parse(value, discovered=True)
    except ValueError as exc:
        raise SignalError(str(exc)) from exc


def _read_issues(path: Path) -> list[dict[str, Any]]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, list):
        raise ValueError("issues input must be a JSON array")
    numbers: set[int] = set()
    for row in value:
        if not isinstance(row, dict):
            raise ValueError("each issue must be a JSON object")
        number = row.get("number")
        if type(number) is not int or number <= 0 or number in numbers:
            raise ValueError("issue numbers must be unique positive integers")
        numbers.add(number)
        for key in ("title", "url", "createdAt", "body"):
            if not isinstance(row.get(key), str):
                raise ValueError(f"issue #{number} must have a string {key}")
        try:
            created = datetime.fromisoformat(row["createdAt"].replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError(f"issue #{number} has an invalid createdAt") from exc
        if created.tzinfo is None:
            raise ValueError(f"issue #{number} createdAt must have a UTC offset")
    return value


def triage(issues: list[dict[str, Any]], *, catalogue_root: Path | None = None) -> dict:
    carded: set[tuple[str, str]] = set()
    if catalogue_root is not None:
        if not (catalogue_root / "models").is_dir():
            raise ValueError("catalogue root must contain a models directory")
        catalogue = load_catalogue(catalogue_root)
        carded = {
            canonical_release(provider, name)
            for provider, aliases in catalogue.aliases.items()
            for name in aliases
        }

    chosen: dict[tuple[str, str], int] = {}
    rows = []
    ordered = sorted(issues, key=lambda row: (
        datetime.fromisoformat(row["createdAt"].replace("Z", "+00:00")), row["number"],
    ))
    for issue in ordered:
        row = {key: issue[key] for key in ("number", "title", "url", "createdAt")}
        row.update(classification="real", reason="", canonical_id=None, duplicate_of=None)
        try:
            signal = _signal(issue["body"])
        except SignalError as exc:
            row["reason"] = f"Manual review: {exc}; retained as a possible release."
            rows.append(row)
            continue

        identity = canonical_release(signal.provider, signal.model_name)
        row["canonical_id"] = ":".join(identity)
        rejected = rejection_reason(signal.provider, signal.model_name)
        if rejected:
            row.update(classification="noise", reason=rejected)
        elif identity in chosen:
            row.update(
                classification="duplicate",
                reason="Another open issue represents the same canonical release.",
                duplicate_of=chosen[identity],
            )
        else:
            chosen[identity] = issue["number"]
            if identity in carded:
                row.update(
                    classification="superseded",
                    reason="An exact canonical release or alias is already carded.",
                )
            else:
                row["reason"] = "Distinct possible model release; keep for review."
        rows.append(row)

    counted = Counter(row["classification"] for row in rows)
    return {
        "schema_version": 1,
        "dry_run": True,
        "catalogue_checked": catalogue_root is not None,
        "counts": {category: counted[category] for category in CLASSIFICATIONS},
        "issues": rows,
        "samples": {
            category: [
                row for row in rows if row["classification"] == category
            ][:SAMPLE_LIMIT]
            for category in CLASSIFICATIONS
        },
    }


def markdown(report: dict) -> str:
    lines = [
        "# Release discovery triage: DRY RUN",
        "",
        "No issues were closed or labeled. Review this report before applying any changes.",
        "",
        "| Classification | Count |",
        "| --- | ---: |",
        *[f"| {category} | {report['counts'][category]} |" for category in CLASSIFICATIONS],
        "",
        f"Catalogue checked: {'yes' if report['catalogue_checked'] else 'no'}.",
        "Superseded means an exact release or alias is already carded; newer versions "
        "do not supersede older ones automatically.",
    ]
    for category in CLASSIFICATIONS:
        lines.extend(["", f"## {category.capitalize()} samples", ""])
        for row in report["samples"][category]:
            title = " ".join(row["title"].split())
            detail = row["reason"]
            if row["duplicate_of"] is not None:
                detail += f" Keep #{row['duplicate_of']}."
            lines.append(f"- [#{row['number']}]({row['url']}) {title}. {detail}")
        if not report["samples"][category]:
            lines.append("None.")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--issues", type=Path, required=True, help="Local gh issue list JSON export",
    )
    parser.add_argument("--catalogue-root", type=Path, help="Optional local private catalogue")
    parser.add_argument("--report", type=Path, help="Write the full JSON dry-run report")
    parser.add_argument("--summary", type=Path, help="Write counts and samples as Markdown")
    args = parser.parse_args(argv)
    paths = [
        path.resolve() for path in (args.issues, args.report, args.summary) if path is not None
    ]
    if len(paths) != len(set(paths)):
        parser.error("--issues, --report and --summary must name different files")
    try:
        report = triage(_read_issues(args.issues), catalogue_root=args.catalogue_root)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    summary = markdown(report)
    if args.report is not None:
        args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if args.summary is not None:
        args.summary.write_text(summary, encoding="utf-8")
    print(summary, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
