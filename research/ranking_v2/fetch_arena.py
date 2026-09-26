"""Fetch Arena rating snapshots from `lmarena-ai/leaderboard-dataset` (CC BY 4.0).

Plain HTTP against the Hugging Face datasets-server JSON API: no Firecrawl, no
pyarrow, standard library only. The output is a compact JSON snapshot committed
beside this file, so the fit and the backtests run offline and reproduce.

    .venv/bin/python -m research.ranking_v2.fetch_arena            # latest + history
    .venv/bin/python -m research.ranking_v2.fetch_arena --latest-only
    uv run --no-project --with pyarrow python -m research.ranking_v2.fetch_arena --parquet

The committed `data/arena.json.gz` was written with `--parquet` on 2026-09-24:
the JSON API answers HTTP 429 after a few hundred anonymous calls, which the
standard-library path survives only slowly (it backs off and retries). Both
paths write the same shape.

Attribution: LMArena, "leaderboard-dataset",
https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset, licensed CC BY 4.0.
Rows are ratings (Bradley-Terry fits on the Elo scale) with 95% intervals, per
category, per `leaderboard_publish_date`.

The datasets-server `/filter` endpoint takes ~25 s a call and `/rows` ~0.4 s.
The `full` split is sorted by (category, leaderboard_publish_date, rank), so
history is read with `/rows` alone: a binary search finds where a category's
rows reach `HISTORY_FROM`, and the rest of that category is paged in order.
"""

from __future__ import annotations

import argparse
import gzip
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

HF = "https://datasets-server.huggingface.co"
DATASET = "lmarena-ai/leaderboard-dataset"
OUT = Path(__file__).resolve().parent / "data" / "arena.json.gz"

#: config -> categories read. Style-controlled views are the Arena default; the
#: raw text view is left out so one set of votes is not counted twice.
BOARDS: dict[str, tuple[str, ...]] = {
    "text_style_control": ("overall", "coding", "math", "hard_prompts", "creative_writing",
                           "instruction_following", "multi_turn", "expert", "longer_query"),
    "vision_style_control": ("overall",),
    "webdev": ("overall",),
    "agent": ("overall",),
    "search_style_control": ("overall",),
    "document_style_control": ("overall",),
}

#: Boards kept historically, for the release-plus-7-days replay.
HISTORY: dict[str, tuple[str, ...]] = {
    "text_style_control": ("overall", "coding", "math", "hard_prompts", "creative_writing",
                           "instruction_following", "expert"),
    "vision_style_control": ("overall",),
    "webdev": ("overall",),
    "agent": ("overall",),
}
HISTORY_FROM = "2025-12-01"


def _get(url: str) -> dict:
    delay = 2.0
    for attempt in range(10):
        try:
            with urllib.request.urlopen(url, timeout=30) as resp:
                data = json.load(resp)
            if "rows" not in data:
                raise RuntimeError(str(data)[:200])
            return data
        except Exception:
            if attempt == 9:
                raise
            time.sleep(delay)
            delay = min(delay * 1.7, 30.0)
    raise AssertionError("unreachable")


def _rows(config: str, split: str, offset: int, length: int = 100) -> tuple[list[dict], int]:
    q = {"dataset": DATASET, "config": config, "split": split, "offset": offset, "length": length}
    data = _get(f"{HF}/rows?{urllib.parse.urlencode(q)}")
    return [dict(r["row"], _idx=r["row_idx"]) for r in data["rows"]], data.get("num_rows_total", 0)


def _compact(row: dict) -> list:
    """model, org, rating, lower, upper, votes — one shape for every config."""
    if "rating" in row:
        vals = [row["rating"], row["rating_lower"], row["rating_upper"]]
        votes = row.get("vote_count")
        digits = 2
    else:
        # The agent board publishes a score with a CI instead of a rating.
        vals = [row["score"], row["score_ci_lower"], row["score_ci_upper"]]
        votes = row.get("session_count")
        digits = 5
    return [row["model_name"], row["organization"],
            *[None if v is None else round(v, digits) for v in vals],
            None if votes is None else int(votes)]


def _first_at_or_after(config: str, total: int, key: tuple[str, str]) -> int:
    """Smallest offset whose (category, date) >= key, by binary search."""
    lo, hi = 0, total
    while lo < hi:
        mid = (lo + hi) // 2
        row = _rows(config, "full", mid, 1)[0][0]
        if (row["category"], row["leaderboard_publish_date"]) < key:
            lo = mid + 1
        else:
            hi = mid
    return lo


def _history(config: str, category: str, since: str) -> dict[str, list[list]]:
    """Every snapshot of one category from `since` on, keyed by date."""
    _, total = _rows(config, "full", 0, 1)
    offset = _first_at_or_after(config, total, (category, since))
    print(f"  {config}/{category}: from row {offset} of {total}", flush=True)
    out: dict[str, list[list]] = {}
    while offset < total:
        rows, _ = _rows(config, "full", offset)
        if not rows:
            break
        for r in rows:
            if r["category"] != category:
                return out
            out.setdefault(r["leaderboard_publish_date"], []).append(_compact(r))
        offset += len(rows)
    return out


def _history_parquet(config: str, categories: tuple[str, ...], since: str,
                     split: str = "full") -> dict[str, dict[str, list[list]]]:
    """The same history from the published parquet file, for when the JSON API
    rate-limits (it answers 429 after a few hundred calls without a token).
    Needs pyarrow, which the repo venv does not carry:

        uv run --with pyarrow python -m research.ranking_v2.fetch_arena --parquet
    """
    import io

    import pyarrow.parquet as pq  # optional; see docstring

    url = (f"https://huggingface.co/datasets/{DATASET}/resolve/main/"
           f"{config}/{split}-00000-of-00001.parquet")
    with urllib.request.urlopen(url, timeout=600) as resp:
        table = pq.read_table(io.BytesIO(resp.read()))
    out: dict[str, dict[str, list[list]]] = {}
    for r in table.to_pylist():
        if r["category"] in categories and r["leaderboard_publish_date"] >= since:
            out.setdefault(r["category"], {}).setdefault(
                r["leaderboard_publish_date"], []).append(_compact(r))
    return out


def fetch(latest_only: bool = False, parquet: bool = False) -> dict:
    out: dict = {"source": f"https://huggingface.co/datasets/{DATASET}", "license": "CC BY 4.0",
                 "fetched": time.strftime("%Y-%m-%d"), "boards": {}}
    for config, categories in BOARDS.items():
        if parquet:
            for category, snaps in _history_parquet(config, categories, "", "latest").items():
                for d, rows in snaps.items():
                    out["boards"].setdefault(f"{config}/{category}", {})[d] = rows
            print(config, "latest (parquet)", flush=True)
            continue
        offset, total = 0, 1
        while offset < total:
            rows, total = _rows(config, "latest", offset)
            if not rows:
                break
            offset += len(rows)
            for r in rows:
                if r["category"] in categories:
                    key = f"{config}/{r['category']}"
                    out["boards"].setdefault(key, {}).setdefault(
                        r["leaderboard_publish_date"], []).append(_compact(r))
        print(config, "latest", offset, flush=True)
    if latest_only:
        return out
    for config, categories in HISTORY.items():
        pre = _history_parquet(config, categories, HISTORY_FROM) if parquet else {}
        for category in categories:
            key = f"{config}/{category}"
            snaps = pre.get(category, {}) if parquet else _history(config, category, HISTORY_FROM)
            # One snapshot per ISO week (the week's last) is plenty for a
            # release-plus-7-days replay, and keeps the committed file small.
            weekly: dict[str, str] = {}
            for d in sorted(snaps):
                weekly[time.strftime("%G-%V", time.strptime(d, "%Y-%m-%d"))] = d
            for d in weekly.values():
                out["boards"].setdefault(key, {}).setdefault(d, snaps[d])
            print(key, "history", len(weekly), "snapshots", flush=True)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--latest-only", action="store_true")
    ap.add_argument("--parquet", action="store_true",
                    help="read history from the parquet files (needs pyarrow)")
    args = ap.parse_args()
    data = fetch(args.latest_only, args.parquet)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(data, separators=(",", ":"), sort_keys=True).encode("utf-8")
    OUT.write_bytes(gzip.compress(payload, mtime=0))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
