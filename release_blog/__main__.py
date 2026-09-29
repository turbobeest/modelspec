"""``python -m release_blog``: write a breakdown, render it, or both.

    python -m release_blog breakdown --model M --after S1 [--before S0] \\
        --accuracy report.json [--vocabulary vocabulary.json] \\
        [--revision N --first-revision r1.json] --out breakdown.json
    python -m release_blog render --breakdown breakdown.json --out post.md
    python -m release_blog draft  (breakdown's arguments) --out-dir DIR
        # DIR/breakdown.json, DIR/post.md and DIR/charts/*.svg

Reads local files only. A refusal writes nothing and exits 2 with the reason.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

from release_blog.breakdown import build_breakdown, to_bytes
from release_blog.gates import BreakdownError, accuracy, check_publishable, load_signed
from release_blog.model import Breakdown
from release_blog.render import write


def _build(args: argparse.Namespace) -> Breakdown:
    after = load_signed(args.after)
    reasons = check_publishable(after, args.model)
    if reasons:
        raise BreakdownError("; ".join(reasons))
    before = None if args.before is None else load_signed(args.before)
    first = (None if args.first_revision is None else Breakdown.model_validate_json(
        args.first_revision.read_text(encoding="utf-8")))
    return build_breakdown(
        model_id=args.model, after=after, before=before,
        accuracy=accuracy(args.accuracy, after.snapshot_id), revision=args.revision,
        first_revision=first, name=args.name, first_published=args.first_published,
        early_access=args.early_access,
        vocabulary=None if args.vocabulary is None else args.vocabulary.read_bytes())


def _inputs(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--model", required=True, help="the model ID, e.g. lab/model")
    parser.add_argument("--after", type=Path, required=True,
                        help="S1: the first signed snapshot the model is in")
    parser.add_argument("--before", type=Path,
                        help="S0: the last signed snapshot without it; omit for a backfill")
    parser.add_argument("--accuracy", type=Path, required=True,
                        help="the pr-profile accuracy report for S1")
    parser.add_argument("--revision", type=int, default=1)
    parser.add_argument("--first-revision", type=Path, help="r1's breakdown.json")
    parser.add_argument("--name", help="the model's display name (default: its ID)")
    parser.add_argument("--first-published", type=date.fromisoformat,
                        help="r1's publication date (default: S1's as_of)")
    parser.add_argument("--vocabulary", type=Path,
                        help="S1's published decision vocabulary, for display names")
    parser.add_argument("--early-access",
                        help="the post.yaml early_access statement, when there is one")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m release_blog", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    one = commands.add_parser("breakdown", help="write breakdown.json")
    _inputs(one)
    one.add_argument("--out", type=Path, required=True)
    two = commands.add_parser("render", help="render breakdown.json as post.md and charts")
    two.add_argument("--breakdown", type=Path, required=True)
    two.add_argument("--out", type=Path, required=True)
    both = commands.add_parser("draft", help="breakdown.json, post.md and charts in one folder")
    _inputs(both)
    both.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "render":
            breakdown = Breakdown.model_validate_json(args.breakdown.read_text(encoding="utf-8"))
            print(json.dumps(write(breakdown, args.out), indent=2))
            return 0
        breakdown = _build(args)
        if args.command == "breakdown":
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_bytes(to_bytes(breakdown))
            print(args.out)
            return 0
        args.out_dir.mkdir(parents=True, exist_ok=True)
        (args.out_dir / "breakdown.json").write_bytes(to_bytes(breakdown))
        print(json.dumps(write(breakdown, args.out_dir / "post.md"), indent=2))
        return 0
    except (BreakdownError, ValueError) as exc:
        print(f"release_blog: refused: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
