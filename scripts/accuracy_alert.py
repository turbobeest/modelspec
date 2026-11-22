"""Write the `alert` issue body for a failing accuracy nightly (MODEL-335).

The orchestrator's heartbeat reads open issues labelled `alert`. A red run in
Actions alone notifies no one, and the coverage report's bundled breach issue
(MODEL-215) stays open for unrelated reasons. The workflow opens one `alert`
issue for a failing nightly, comments on it each further failing night, and
closes it on the next green run. This module only writes the text. The
workflow makes the `gh` calls.

The issue is public. Its body is the public form of the report (layer status,
gate, and counts) plus where to read the detail. MODELSPEC_DATA_TOKEN cannot
open an issue in the private repository. The detail goes to a separate token,
ACCURACY_ALERT_TOKEN, in one workflow step (MODEL-483 E), and is never printed.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.accuracy_public import public_nightly_report, public_report_location  # noqa: E402

TITLE = "Accuracy nightly failed"
LABEL = "alert"
_UNPUBLISHED = (
    "details are not published; run the nightly profile locally against the private data"
)


def body(
    report: Mapping[str, Any] | None, run_url: str, *, output_dir: Path | None = None,
) -> str:
    """The public issue: the layer table, and no per-draw rows.

    A missing report (the script crashed before writing one) is still an alert.
    """
    location = ""
    if output_dir is not None:
        location = public_report_location(output_dir) + "\n\n"
    if report is None:
        return f"the run failed before a report was written\n\n{location}Run: {run_url}\n"
    table = public_nightly_report(report).rstrip("\n")
    return f"{table}\n\n{location}{_UNPUBLISHED}\n\nRun: {run_url}\n"


# GitHub rejects an issue body or comment over 65536 characters.
DETAIL_LIMIT = 60000


def detail(report_path: Path, run_url: str) -> str:
    """The full report for the private sink: per-card ids, fields, values, URLs.

    This is the written `accuracy.md` next to the report, or the report JSON if
    that file is missing. The text is private. The workflow posts it to an issue
    in the private repository and never prints it.
    """
    markdown = report_path.parent / "accuracy.md"
    if markdown.exists():
        text = markdown.read_text(encoding="utf-8")
    elif report_path.exists():
        text = "```json\n" + report_path.read_text(encoding="utf-8") + "\n```\n"
    else:
        text = "the run failed before a report was written\n"
    if len(text) > DETAIL_LIMIT:
        text = text[:DETAIL_LIMIT] + "\n\n[truncated]\n"
    return f"{text}\nRun: {run_url}\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--run-url", required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--detail-output", type=Path)
    args = parser.parse_args(argv)
    if args.output is None and args.detail_output is None:
        parser.error("give --output, --detail-output, or both")
    if args.output is not None:
        report = (
            json.loads(args.report.read_text(encoding="utf-8")) if args.report.exists() else None
        )
        args.output.write_text(
            body(report, args.run_url, output_dir=args.report.parent), encoding="utf-8",
        )
    if args.detail_output is not None:
        args.detail_output.write_text(detail(args.report, args.run_url), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
