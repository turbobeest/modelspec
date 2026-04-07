#!/usr/bin/env python3
"""Migrate YAML model cards from fixed benchmark fields to scores dict.

Before:
  benchmarks:
    mmlu_pro: 85.2
    gpqa_diamond: null
    humaneval: 93.2
    extra_scores:
      multipl_e_rust: 82.1
    benchmark_source: lmarena.ai

After:
  benchmarks:
    scores:
      mmlu_pro: 85.2
      humaneval: 93.2
      multipl_e_rust: 82.1
    benchmark_source: lmarena.ai
"""

import re
import sys
from pathlib import Path

# Metadata fields that stay at the top level of benchmarks (not in scores)
META_FIELDS = {"benchmark_source", "benchmark_as_of", "benchmark_notes"}


def migrate_file(path: Path) -> bool:
    """Migrate a single YAML model card. Returns True if changed."""
    text = path.read_text()

    # Find the benchmarks section
    match = re.search(r'^benchmarks:\n', text, re.MULTILINE)
    if not match:
        return False

    start = match.start()

    # Find where benchmarks section ends (next top-level key or EOF)
    # Top-level keys start at column 0 with no indentation
    rest = text[match.end():]
    end_match = re.search(r'^[a-z_]+:', rest, re.MULTILINE)
    if end_match:
        bench_end = match.end() + end_match.start()
    else:
        bench_end = len(text)

    bench_section = text[match.end():bench_end]

    # Parse the benchmark fields
    scores = {}
    meta = {}
    in_extra_scores = False

    for line in bench_section.split('\n'):
        stripped = line.strip()
        if not stripped:
            continue

        # Detect extra_scores block
        if stripped == 'extra_scores:' or stripped == 'extra_scores: {}':
            in_extra_scores = True
            if stripped == 'extra_scores: {}':
                in_extra_scores = False
            continue

        # Lines inside extra_scores have 4-space indent (relative to benchmarks 2-space)
        if in_extra_scores:
            # Check if we've exited extra_scores (back to 2-space indent)
            if line.startswith('  ') and not line.startswith('    '):
                in_extra_scores = False
                # Fall through to process this line as a regular field
            else:
                # Parse extra_scores entry
                m = re.match(r'^\s+(\w+):\s*(.+)$', line)
                if m:
                    key, val = m.group(1), m.group(2).strip()
                    try:
                        scores[key] = float(val)
                    except ValueError:
                        pass
                continue

        # Regular benchmark field
        m = re.match(r'^  (\w+):\s*(.*)$', line)
        if not m:
            continue

        key, val = m.group(1), m.group(2).strip()

        if key in META_FIELDS:
            # Preserve metadata with multi-line values
            meta[key] = val
        elif key == 'extra_scores':
            in_extra_scores = True
            if val == '{}':
                in_extra_scores = False
        elif val and val != 'null':
            # Non-null benchmark score
            try:
                scores[key] = float(val)
            except ValueError:
                # Could be an int (openrouter_usage_rank)
                try:
                    scores[key] = float(int(val))
                except ValueError:
                    pass

    # Also handle multi-line metadata values (benchmark_source can wrap)
    # Re-parse more carefully for metadata
    meta = {}
    lines = bench_section.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r'^  (\w+):\s*(.*)$', line)
        if m and m.group(1) in META_FIELDS:
            key = m.group(1)
            val_parts = [m.group(2).strip()]
            # Check for continuation lines (indented more than 2 spaces, not a key)
            while i + 1 < len(lines):
                next_line = lines[i + 1]
                if next_line.startswith('    ') and not re.match(r'^\s+\w+:', next_line):
                    val_parts.append(next_line.strip())
                    i += 1
                else:
                    break
            meta[key] = ' '.join(p for p in val_parts if p)
        i += 1

    # Build new benchmarks section
    new_lines = ['benchmarks:\n']

    if scores:
        new_lines.append('  scores:\n')
        for key in sorted(scores.keys()):
            val = scores[key]
            # Format: use int if it's a whole number, else 1 decimal
            if val == int(val) and abs(val) < 1e15:
                new_lines.append(f'    {key}: {int(val)}\n')
            else:
                new_lines.append(f'    {key}: {val}\n')
    else:
        new_lines.append('  scores: {}\n')

    for key in ['benchmark_source', 'benchmark_as_of', 'benchmark_notes']:
        if key in meta and meta[key] and meta[key] != "''":
            new_lines.append(f'  {key}: {meta[key]}\n')

    new_text = text[:start] + ''.join(new_lines) + text[bench_end:]

    if new_text != text:
        path.write_text(new_text)
        return True
    return False


def main():
    models_dir = Path(__file__).parent.parent / "models"
    if not models_dir.exists():
        print(f"Models directory not found: {models_dir}")
        sys.exit(1)

    files = list(models_dir.rglob("*.md"))
    print(f"Found {len(files)} model cards to migrate")

    changed = 0
    skipped = 0
    errors = 0

    for f in sorted(files):
        try:
            if migrate_file(f):
                changed += 1
            else:
                skipped += 1
        except Exception as e:
            print(f"  ERROR {f.relative_to(models_dir)}: {e}")
            errors += 1

    print(f"\nDone: {changed} migrated, {skipped} skipped, {errors} errors")


if __name__ == "__main__":
    main()
