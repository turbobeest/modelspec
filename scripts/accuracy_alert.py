"""Write the `alert` issue body for a failing accuracy nightly (MODEL-335).

The orchestrator's heartbeat reads open issues labelled `alert`. A red run in
Actions alone notifies no one, and the coverage report's bundled breach issue
(MODEL-215) stays open for unrelated reasons. The workflow opens one `alert`
issue for a failing nightly, comments on it each further failing night, and
closes it on the next green run. This module only writes the text. The
workflow makes the `gh` calls.

The issue is public. Its body is the public form of the report (layer status,
gate, and counts) plus where to read the detail. MODELSPEC_DATA_TOKEN cannot
open an issue in the private repository.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.accuracy import public_nightly_report  # noqa: E402

TITLE = "Accuracy nightly failed"
LABEL = "alert"
_UNPUBLISHED = (
    "details are not published; run the nightly profile locally against the private data"
)


def body(report: Mapping[str, Any] | None, run_url: str) -> str:
    """The public issue: the layer table, and no per-draw rows.

    A missing report (the script crashed before writing one) is still an alert.
    """
    if report is None:
        return f"The nightly wrote no report: it failed before or during the run.\n\nRun: {run_url}\n"
    table = public_nightly_report(report).rstrip("\n")
    return f"{table}\n\n{_UNPUBLISHED}\n\nRun: {run_url}\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--run-url", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    report = json.loads(args.report.read_text(encoding="utf-8")) if args.report.exists() else None
    args.output.write_text(body(report, args.run_url), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
