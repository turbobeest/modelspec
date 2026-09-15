#!/usr/bin/env python3
"""One-off corpus fix for MODEL-53.

`scripts/seed_huggingface.py::determine_model_type` used to default every
unmatched `pipeline_tag` to `llm-chat`. Cards whose `pipeline_tag` is one of
the non-token categories in `NON_TOKEN_PIPELINE_TYPE_MAP` (time-series
forecasting, vision perception, vision/text encoders) got typed as an LLM
purely because nothing else claimed them — not because anyone looked at the
model and decided it generates tokens.

This script finds every existing card whose `model_type` is still one of the
old LLM defaults but whose own `pipeline_tag` implies a non-token model, and
retypes it from that pipeline_tag. It touches only the `model_type:` line —
everything else in the card is left exactly as it was researched.

Cards whose pipeline_tag is a genuine token-generating tag (text-generation,
image-text-to-text, or anything not in the map) are never touched: this is a
retype, not a re-guess.

Usage:
    python scripts/retype_non_token_cards.py [--apply]

Without --apply, prints the plan (per-tag counts, old -> new) and does not
write anything. With --apply, rewrites the cards and re-validates each one
with ModelCard.from_yaml_file.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.seed_huggingface import NON_TOKEN_PIPELINE_TYPE_MAP  # noqa: E402
from schema.card import ModelCard  # noqa: E402

MODELS_DIR = PROJECT_ROOT / "models"

#: model_type values MODEL-47-and-earlier code could have defaulted a card to.
#: Only cards currently sitting on one of these are candidates for retyping —
#: a card someone has since hand-corrected to something else is left alone.
OLD_LLM_DEFAULTS = {"llm-chat", "llm-reasoning", "llm-code", "llm-base"}

MODEL_TYPE_RE = re.compile(r"^model_type:\s*(\S+)\s*$", re.MULTILINE)
PIPELINE_TAG_RE = re.compile(r"^pipeline_tag:\s*(\S+)\s*$", re.MULTILINE)


def plan() -> list[tuple[Path, str, str, str]]:
    """Return (path, pipeline_tag, old_type, new_type) for every card to fix."""
    changes = []
    for path in sorted(MODELS_DIR.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        mt_match = MODEL_TYPE_RE.search(text)
        pt_match = PIPELINE_TAG_RE.search(text)
        if not mt_match or not pt_match:
            continue
        old_type = mt_match.group(1)
        pipeline_tag = pt_match.group(1)
        if old_type not in OLD_LLM_DEFAULTS:
            continue
        new_type = NON_TOKEN_PIPELINE_TYPE_MAP.get(pipeline_tag)
        if new_type is None:
            continue
        if new_type.value == old_type:
            continue
        changes.append((path, pipeline_tag, old_type, new_type.value))
    return changes


def apply(changes: list[tuple[Path, str, str, str]]) -> None:
    for path, _pipeline_tag, old_type, new_type in changes:
        text = path.read_text(encoding="utf-8")
        new_text, count = MODEL_TYPE_RE.subn(f"model_type: {new_type}", text, count=1)
        if count != 1:
            raise RuntimeError(f"{path}: expected exactly one model_type line, patched {count}")
        path.write_text(new_text, encoding="utf-8")
        # Re-validate: the retype must still round-trip as a valid card.
        loaded = ModelCard.from_yaml_file(path)
        if loaded.identity.model_type is None or loaded.identity.model_type.value != new_type:
            raise RuntimeError(f"{path}: retype did not take effect after write")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Write the changes (default: dry run).")
    args = parser.parse_args()

    changes = plan()
    by_tag: Counter[str] = Counter(tag for _p, tag, _o, _n in changes)
    by_transition: Counter[tuple[str, str]] = Counter((o, n) for _p, _t, o, n in changes)

    print(f"{len(changes)} card(s) to retype")
    print("\nBy pipeline_tag:")
    for tag, n in sorted(by_tag.items(), key=lambda kv: (-kv[1], kv[0])):
        print(f"  {tag:<32} {n}")
    print("\nBy old_type -> new_type:")
    for (old, new), n in sorted(by_transition.items(), key=lambda kv: (-kv[1], kv[0])):
        print(f"  {old:<16} -> {new:<20} {n}")

    if args.apply:
        apply(changes)
        print(f"\nApplied {len(changes)} retype(s).")
    else:
        print("\nDry run only. Re-run with --apply to write these changes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
