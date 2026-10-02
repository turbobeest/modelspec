"""Print before/after agent vocabulary sizes from a captured HTTP vocabulary.

    python scripts/vocabulary_sizes.py /tmp/vocabulary.json

Capture with GET /v1/vocabulary without query parameters. This command prints
sizes only, never the captured names, definitions or model facts.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from api.worker.src.display_vocabulary import SECTIONS, lookup


def token_counter():
    try:
        import tiktoken
    except ImportError:
        return "chars/4, rounded up", lambda text: math.ceil(len(text) / 4)
    encoding = tiktoken.get_encoding("cl100k_base")
    return "tiktoken cl100k_base", lambda text: len(encoding.encode(text))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    vocabulary = json.loads(args.input.read_text())
    method, count = token_counter()

    def size(value):
        return count(json.dumps(value, ensure_ascii=False, separators=(",", ":")))

    print(f"Token proxy: {method}. JSON bodies, compact serialization, first page of at most 20 rows.")
    print("\n| Section | Before | After |")
    print("| --- | ---: | ---: |")
    for section in SECTIONS:
        before = f"{size(vocabulary[section]):,}" if section in vocabulary else "absent"
        after = size(lookup(vocabulary, section=section)[section])
        print(f"| {section} | {before} | {after:,} |")
    print(f"\nDefault MCP body: {size(vocabulary):,} → {size(lookup(vocabulary)['starter']):,}.")
    print("HTTP with no query parameters retains its full response byte for byte. MCP explicitly opts into the section lookup.")


if __name__ == "__main__":
    main()
