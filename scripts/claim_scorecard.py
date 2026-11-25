"""Claim scorecard check 3: the strongest model a vendor left out (MODEL-537).

Internal and operator-run. It reads card front matter, never serves anything, and its
output is in no public contract. Given a vendor reading that carries a stated
`baseline`, it finds the leader on that benchmark in our own data as of the subject's
release date, and says whether the vendor's baselines include it.

Comparable readings:

* the same `benchmark_id` (the id is the exact variant, handoff rule 6) and `unit`;
* the same setup: when both readings name a registered harness, the harnesses match;
* published on or before the as-of date, and not marked no longer published by then.

Each model counts once, with its best comparable reading (effort settings collapse).
Baseline labels are the source's own column names, so they are matched to cards by
name tokens. A label that matches no card is reported as unresolved, never guessed.

    python scripts/claim_scorecard.py --data-dir ../modelspec-data [--model provider/id]

The command prints model ids and scores from the data directory: run it on the operator
machine only, never in CI (the repository and its logs are public).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections.abc import Iterable, Mapping
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

VENDOR = "provider_self_report"
#: Effort and mode words a source appends to a model name; they do not name a model.
NOISE = frozenset({"max", "xhigh", "high", "medium", "low", "minimal", "thinking", "think",
                   "reasoning", "nonthink", "instruct", "chat", "preview"})
#: Short forms sources print for a lab's name.
ABBREVIATIONS = {"ds": "deepseek"}
UNREGISTERED = {None, "", "unregistered"}


@dataclass(frozen=True)
class Row:
    model_id: str
    score: float
    evidence_date: str
    measured_by: str


@dataclass
class LeftOut:
    """The check-3 answer for one vendor reading."""

    subject: str
    benchmark_id: str
    as_of: str
    baselines: list[str]
    #: Baseline label -> the card ids it names. An empty list is an unresolved label.
    resolved: dict[str, list[str]]
    leader: Row | None
    #: True when the leader is one of the vendor's baselines; None with no leader.
    leader_included: bool | None
    #: The best model in our data that no baseline names; None when every model is named.
    strongest_left_out: Row | None
    comparable_models: int
    unresolved: list[str] = field(default_factory=list)

    def to_json(self) -> dict[str, Any]:
        return asdict(self)


def tokens(name: str) -> frozenset[str]:
    """Name tokens: lower case, parentheticals and effort words dropped, `5.0` read as `5`."""
    text = re.sub(r"\([^)]*\)", " ", name.lower())
    out = set()
    for raw in re.split(r"[^a-z0-9.]+", text):
        tok = raw.strip(".")
        if not tok or tok in NOISE:
            continue
        tok = re.sub(r"^(\d+)\.0$", r"\1", tok)
        out.add(ABBREVIATIONS.get(tok, tok))
    return frozenset(out)


def card_names(card: Mapping[str, Any]) -> list[frozenset[str]]:
    # An id slug spells a version with hyphens (claude-opus-5-5 is Opus 5.5).
    slug = re.sub(r"(?<=\d)-(?=\d)", ".", str(card.get("model_id", "")).split("/")[-1])
    names = {str(card.get("display_name") or ""), slug}
    for row in _evidence(card):
        names.add(str(row.get("model_id_as_evaluated") or ""))
    return [t for t in (tokens(n.replace("-", " ")) for n in names if n) if t]


def resolve(label: str, cards: Iterable[Mapping[str, Any]]) -> list[str]:
    """Card ids a baseline label names: the closest name-token match, ties kept."""
    want = tokens(label.replace("-", " "))
    if not want:
        return []
    best: dict[str, int] = {}
    for card in cards:
        for have in card_names(card):
            if want <= have:
                extra = len(have - want)
            elif have <= want and all(t.isdigit() for t in want - have):
                extra = len(want - have)  # a dated snapshot suffix such as 0731
            else:
                continue
            mid = str(card["model_id"])
            best[mid] = min(extra, best.get(mid, extra))
    if not best:
        return []
    low = min(best.values())
    return sorted(m for m, extra in best.items() if extra == low)


def split_label(label: str) -> list[str]:
    return [part.strip() for part in label.split(",") if part.strip()]


def _evidence(card: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    return [r for r in ((card.get("benchmarks") or {}).get("evidence") or []) if isinstance(r, Mapping)]


def _harness(row: Mapping[str, Any]) -> str | None:
    value = row.get("harness")
    return None if value in UNREGISTERED else str(value)


def comparable(reading: Mapping[str, Any], row: Mapping[str, Any], as_of: str) -> bool:
    if row.get("benchmark_id") != reading.get("benchmark_id") or row.get("unit") != reading.get("unit"):
        return False
    mine, theirs = _harness(reading), _harness(row)
    if mine and theirs and mine != theirs:
        return False
    day = str(row.get("evidence_date") or "")
    if not day or day > as_of:
        return False
    gone = row.get("not_published_since")
    return not (gone and str(gone) <= as_of)


def leaders(cards: Iterable[Mapping[str, Any]], reading: Mapping[str, Any], as_of: str,
            higher_is_better: bool = True, exclude: str = "") -> list[Row]:
    """Each other model's best comparable reading, best first."""
    best: dict[str, Row] = {}
    for card in cards:
        mid = str(card.get("model_id", ""))
        if not mid or mid == exclude:
            continue
        for row in _evidence(card):
            if not comparable(reading, row, as_of):
                continue
            cand = Row(mid, float(row["score"]), str(row["evidence_date"]),
                       str(row.get("measured_by") or row.get("source_kind") or ""))
            held = best.get(mid)
            if held is None or (cand.score > held.score if higher_is_better else cand.score < held.score):
                best[mid] = cand
    return sorted(best.values(), key=lambda r: (-r.score if higher_is_better else r.score, r.model_id))


def strongest_left_out(cards: list[Mapping[str, Any]], subject: Mapping[str, Any],
                       reading: Mapping[str, Any], higher_is_better: bool = True,
                       as_of: str | None = None) -> LeftOut:
    """Check 3 for one reading on `subject` that carries a stated baseline."""
    baseline = reading.get("baseline") or {}
    if not isinstance(baseline, Mapping) or baseline.get("kind") in (None, "none_stated"):
        raise ValueError("the reading carries no stated baseline")
    day = as_of or str(subject.get("release_date") or "") or str(reading.get("evidence_date"))
    labels = split_label(str(baseline.get("label") or ""))
    others = [c for c in cards if c.get("model_id") != subject.get("model_id")]
    resolved = {label: resolve(label, others) for label in labels}
    named = {mid for ids in resolved.values() for mid in ids}
    ranked = leaders(cards, reading, day, higher_is_better, exclude=str(subject.get("model_id")))
    leader = ranked[0] if ranked else None
    left = next((r for r in ranked if r.model_id not in named), None)
    return LeftOut(
        subject=str(subject.get("model_id")), benchmark_id=str(reading.get("benchmark_id")),
        as_of=day, baselines=labels, resolved=resolved, leader=leader,
        leader_included=None if leader is None else leader.model_id in named,
        strongest_left_out=left, comparable_models=len(ranked),
        unresolved=[label for label, ids in resolved.items() if not ids])


def load_cards(data_dir: Path) -> list[dict[str, Any]]:
    from pipeline.load import split_front_matter

    cards = []
    for path in sorted((data_dir / "models").rglob("*.md")):
        try:
            front, _ = split_front_matter(path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001 - a broken card is skipped, as the loaders do
            continue
        if isinstance(front, dict) and front.get("model_id"):
            cards.append(front)
    return cards


def directions(data_dir: Path) -> dict[str, bool]:
    from pipeline.load import split_front_matter

    out = {}
    for path in (data_dir / "benchmarks").glob("*.md"):
        try:
            front, _ = split_front_matter(path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            continue
        if isinstance(front, dict) and front.get("id"):
            out[str(front["id"])] = (front.get("metric") or {}).get("direction") != "lower_is_better"
    return out


def scorecard(cards: list[Mapping[str, Any]], higher: Mapping[str, bool],
              model: str | None = None) -> list[LeftOut]:
    out = []
    for card in cards:
        if model and card.get("model_id") != model:
            continue
        for row in _evidence(card):
            base = row.get("baseline")
            if isinstance(base, Mapping) and base.get("kind") not in (None, "none_stated"):
                out.append(strongest_left_out(cards, card, row, higher.get(str(row["benchmark_id"]), True)))
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--model")
    args = parser.parse_args(argv)
    cards = load_cards(args.data_dir)
    for result in scorecard(cards, directions(args.data_dir), args.model):
        print(json.dumps(result.to_json(), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
