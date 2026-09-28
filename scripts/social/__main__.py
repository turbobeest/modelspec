"""Command-line entry point for ``python -m scripts.social``."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from scripts.social.generator import generate


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate offline social drafts from a signed ModelSpec decision snapshot."
    )
    parser.add_argument("model", help="Model ID, for example openai/gpt-6-astra")
    parser.add_argument("--snapshot", required=True, type=Path)
    parser.add_argument("--accuracy-report", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--previous-snapshot", type=Path)
    parser.add_argument("--device", help="Hardware registry ID for the local angle")
    args = parser.parse_args()
    manifest = generate(
        model_id=args.model,
        snapshot_path=args.snapshot,
        previous_snapshot_path=args.previous_snapshot,
        accuracy_report_path=args.accuracy_report,
        output_dir=args.out,
        device=args.device,
        snapshot_key=os.environ.get("MODELSPEC_SNAPSHOT_KEY"),
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
