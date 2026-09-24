"""The data layer: cards and Arena snapshots -> dated, attributed observations.

Everything the capability model sees passes through `observations()`. It keeps
each measurement as its own record — raw value, unit, benchmark version,
configuration (harness, effort), source URL, source kind and date — so the
explanation can cite it, and it applies every exclusion and quarantine rule in
one place:

* **Excluded sources (MODEL-117).** Every row from artificialanalysis.ai or
  zapier.com, every AA-owned key (`aa_*`, `*_aa`, `artificial_analysis_*`) and
  `automationbench*` is dropped before anything else happens.
* **Sibling-copy quarantine (independent audit, Critical 2).** A flat block that
  shares four or more identical `(key, value)` pairs, making up at least 80% of
  the smaller block, with another card's flat block is quarantined on both
  cards. The flat block has no per-score provenance, so nothing distinguishes
  the original from the copy. Evidence rows are never quarantined this way:
  they carry `model_id_as_evaluated`.
* **Effort variants (Jamie's rule).** When one source reports several effort
  settings for one product, the max-effort row is the product row.
* **Live readings.** Arena is a live board: per board, only the newest
  snapshot on or before the as-of date is read. A model missing from it falls
  back to its newest older snapshot, shifted by the median offset between the
  two snapshots over the models they share, and dated by that older snapshot.
* **One set of votes, one signal.** Card rows copied from Arena are replaced by
  the dataset itself, and METR's 80% horizon is dropped beside the 50% one
  (both come from the same fitted curve). A flat value is dropped wherever the
  same card has a sourced row for the same benchmark.
"""

from __future__ import annotations

import json
import math
import re
import statistics
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Iterable

from research.ranking_v2.domains import ARENA_BOARDS, tags_for

ROOT = Path(__file__).resolve().parents[2]
ARENA_PATH = Path(__file__).resolve().parent / "data" / "arena.json.gz"
ARENA_URL = "https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset"

_AA_KEY = re.compile(r"^(aa_|artificial_analysis_)|_aa$")
_EXCLUDED_HOSTS = ("artificialanalysis.ai", "zapier.com")


def excluded(benchmark_id: str, url: str = "") -> bool:
    """MODEL-117: Artificial Analysis and Zapier/AutomationBench are purged."""
    host = url.split("/")[2] if url.count("/") >= 2 else ""
    return (bool(_AA_KEY.search(benchmark_id)) or benchmark_id.startswith("automationbench")
            or any(host.endswith(h) for h in _EXCLUDED_HOSTS))


# ── observations ─────────────────────────────────────────────────────────────


@dataclass
class Obs:
    model_id: str
    item: str               # benchmark id, or an Arena board id, or flat:<id>
    value: float            # raw value on the benchmark's own unit
    link: str               # "pct" (bounded percent), "lin" (Elo), "log" (minutes)
    source_kind: str        # independent_evaluator | benchmark_author | provider_self_report | flat_unsourced
    date: str               # ISO date the value is dated by
    source_url: str
    as_evaluated: str = ""
    version: str = ""
    configuration: str = ""
    se: float | None = None  # reported standard error on the raw unit, if any
    live: bool = False
    tags: tuple[str, ...] = ()
    family: str = ""         # same-run subtask family, for the design-effect weight

    def cite(self) -> dict[str, Any]:
        return {"item": self.item, "value": self.value, "unit": self.link,
                "version": self.version, "configuration": self.configuration[:160],
                "as_evaluated": self.as_evaluated, "source_kind": self.source_kind,
                "source_url": self.source_url, "date": self.date}


# ── catalogue ────────────────────────────────────────────────────────────────


def load_cards(root: Path = ROOT) -> list[dict[str, Any]]:
    """Every card as the plain fields the prototype needs (about 30 s)."""
    from api.classes import class_for_model_type
    from schema.card import ModelCard

    out = []
    for p in sorted((root / "models").rglob("*.md")):
        if p.name == "LICENSE.md":
            continue
        c = ModelCard.from_yaml_file(p)
        i = c.identity
        mtype = i.model_type.value if i.model_type else None
        relation = getattr(c.lineage.base_model_relation, "value", c.lineage.base_model_relation)
        inputs = {getattr(m, "value", m) for m in c.modalities.input}
        out.append({
            "model_id": i.model_id, "name": i.display_name or i.model_id,
            "provider": i.provider or "", "type": mtype,
            "class_id": class_for_model_type(mtype),
            "release": str(i.release_date or "").strip(),
            "rehost_of": c.lineage.base_model if relation == "repackaged" and c.lineage.base_model else None,
            "open_weights": bool(c.licensing.open_weights),
            "cost_input": c.cost.input,
            "context_window": c.modalities.text.context_window,
            "image_input": "image" in inputs or bool(c.modalities.vision.supported),
            "flat": {k: float(v) for k, v in c.benchmarks.scores.items() if isinstance(v, (int, float))},
            "flat_as_of": str(c.benchmarks.benchmark_as_of or ""),
            "evidence": [e.model_dump() for e in c.benchmarks.evidence],
        })
    return out


def load_pages(root: Path = ROOT) -> dict[str, dict[str, Any]]:
    """Benchmark page frontmatter by id: category, unit, baseline, family, size."""
    import yaml

    pages = {}
    for p in (root / "benchmarks").glob("*.md"):
        text = p.read_text(encoding="utf-8")
        if not text.startswith("---"):
            continue
        fm = yaml.safe_load(text.split("---", 2)[1])
        if isinstance(fm, dict):
            pages[str(fm.get("id") or p.stem)] = fm
    return pages


def load_arena(path: Path = ARENA_PATH) -> dict[str, dict[str, list]]:
    import gzip

    if not path.exists():
        return {}
    return json.loads(gzip.decompress(path.read_bytes()))["boards"]


# ── effort and name matching ────────────────────────────────────────────────

EFFORT_RANK = {"minimal": 1, "low": 2, "medium": 3, "thinking": 4, "reasoning": 4,
               "high": 5, "xhigh": 6, "max": 7}
_EFFORT_TAIL = re.compile(
    r"-(?:(max|xhigh|high|medium|low|minimal)(?:-effort)?|(thinking|reasoning)(?:-\d+k)?)$")


def norm(name: str) -> str:
    s = re.sub(r"[\s._/()\[\]:,]+", "-", name.lower())
    return re.sub(r"-+", "-", s).strip("-")


def effort_of(text: str) -> int:
    """Effort rank named in an evaluated-model label or configuration (0: none)."""
    t = norm(text)
    best = 0
    for word, rank in EFFORT_RANK.items():
        if re.search(rf"(^|-){word}(-|$)", t):
            best = max(best, rank)
    return best


class Matcher:
    """Arena model names -> card ids, exact first, then with effort stripped."""

    def __init__(self, cards: list[dict[str, Any]]):
        self.index: dict[str, list[dict]] = {}
        for c in cards:
            for key in {norm(c["model_id"].split("/", 1)[-1]), norm(c["name"])}:
                self.index.setdefault(key, []).append(c)
        # Curated pairs: the evaluated names on cards' own Arena evidence rows.
        self.alias: dict[str, str] = {}
        for c in cards:
            for e in c["evidence"]:
                if "lmarena" in e["source_url"]:
                    self.alias[norm(e["model_id_as_evaluated"])] = c["model_id"]

    def _pick(self, key: str, org: str) -> str | None:
        found = self.index.get(key) or []
        if not found:
            return None
        found = sorted(found, key=lambda c: (c["rehost_of"] is not None,
                                             norm(c["provider"]) != norm(org), c["model_id"]))
        return found[0]["model_id"]

    def match(self, name: str, org: str = "") -> tuple[str | None, int]:
        """(card id, effort rank). The effort is read from the name itself, so
        `x-max` outranks `x-high` whichever path matched it."""
        key, effort = norm(name), effort_of(name)
        for _ in range(3):
            if key in self.alias:
                return self.alias[key], effort
            hit = self._pick(key, org)
            if hit:
                return hit, effort
            m = _EFFORT_TAIL.search(key)
            if not m:
                break
            key = key[:m.start()]
        return None, 0


# ── the observation builder ─────────────────────────────────────────────────


def _iso(d: str) -> str | None:
    d = (d or "").strip()
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", d):
        return d
    if re.fullmatch(r"\d{4}-\d{2}", d):
        return d + "-15"
    if re.fullmatch(r"\d{4}", d):
        return d + "-07-01"
    return None


def _pct_value(value: float, page: dict) -> float | None:
    """A bounded score as a percentage, or None when it is not one."""
    metric = page.get("metric") or {}
    unit = str(metric.get("unit") or "").lower()
    top = metric.get("max_score")
    if unit in ("minutes", "tokens/second") or "elo" in unit:
        return None
    if isinstance(top, (int, float)) and top and top != 100:
        if value <= top * 1.0001:
            value = value / top * 100.0
    if unit in ("", "points", "score") and not isinstance(top, (int, float)):
        return None
    if 0.0 <= value <= 100.0:
        return value
    return None


def quarantine_flat(cards: list[dict[str, Any]], min_shared: int = 4,
                    min_share: float = 0.8) -> dict[str, list[str]]:
    """Cards whose flat block is a sibling copy -> the cards it matches."""
    inverted: dict[tuple[str, float], list[str]] = {}
    size = {}
    for c in cards:
        block = {k: v for k, v in c["flat"].items() if not excluded(k)}
        size[c["model_id"]] = len(block)
        for k, v in block.items():
            inverted.setdefault((k, round(v, 4)), []).append(c["model_id"])
    shared: dict[tuple[str, str], int] = {}
    for ids in inverted.values():
        if len(ids) < 2 or len(ids) > 60:
            continue
        for i, a in enumerate(ids):
            for b in ids[i + 1:]:
                shared[(a, b)] = shared.get((a, b), 0) + 1
    rehost = {c["model_id"]: c["rehost_of"] for c in cards}
    out: dict[str, list[str]] = {}
    for (a, b), n in shared.items():
        if n < min_shared or n < min_share * min(size[a], size[b]):
            continue
        if rehost.get(a) == b or rehost.get(b) == a:
            continue  # a declared re-host carries the same weights
        out.setdefault(a, []).append(b)
        out.setdefault(b, []).append(a)
    return out


@dataclass
class Build:
    obs: list[Obs]
    dropped: dict[str, int] = field(default_factory=dict)
    quarantined: dict[str, list[str]] = field(default_factory=dict)
    arena_unmatched: int = 0


def observations(cards: list[dict[str, Any]], pages: dict[str, dict], arena: dict,
                 as_of: str, include_flat: bool = False,
                 quarantine: dict[str, list[str]] | None = None) -> Build:
    """Every usable observation dated on or before `as_of`."""
    dropped: dict[str, int] = {}

    def drop(reason: str) -> None:
        dropped[reason] = dropped.get(reason, 0) + 1

    obs: list[Obs] = []
    best: dict[tuple[str, str, str], tuple[int, str, Obs]] = {}
    for c in cards:
        mid = c["model_id"]
        for e in c["evidence"]:
            bid = e["benchmark_id"]
            if excluded(bid, e["source_url"]):
                drop("excluded_source")
                continue
            if bid.startswith("arena_"):
                drop("arena_row_replaced_by_dataset")
                continue
            if bid == "metr_time_horizon_80":
                drop("same_run_duplicate")
                continue
            d = e["evidence_date"]
            if d > as_of:
                drop("after_as_of")
                continue
            page = pages.get(bid, {})
            unit = e["unit"]
            if unit == "minutes":
                if e["score"] <= 0:
                    drop("nonpositive_minutes")
                    continue
                link, value = "log", float(e["score"])
            else:
                v = _pct_value(float(e["score"]), page)
                if v is None:
                    drop("not_a_bounded_score")
                    continue
                link, value = "pct", v
            o = Obs(mid, bid, value, link, e["source_kind"], d, e["source_url"],
                    e["model_id_as_evaluated"], e.get("benchmark_version", ""),
                    e.get("configuration", ""), tags=tags_for(bid, page),
                    family=_family(bid, page))
            if not o.tags:
                drop("untagged")
                continue
            key = (mid, bid, e["source_kind"])
            rank = (effort_of(e["model_id_as_evaluated"] + " " + e.get("configuration", "")[:60]), d)
            if key not in best or rank > best[key][:2]:
                best[key] = (*rank, o)
        if include_flat and c["flat"]:
            if quarantine and mid in quarantine:
                dropped["flat_quarantined_sibling_copy"] = dropped.get(
                    "flat_quarantined_sibling_copy", 0) + len(c["flat"])
                continue
            d = _iso(c["flat_as_of"]) or _iso(c["release"]) or "2024-01-01"
            if d > as_of:
                drop("after_as_of")
                continue
            # The same benchmark with a sourced row wins outright: a flat value
            # beside it is usually that very number, copied without a source,
            # and counting both would count one measurement twice.
            sourced_ids = {e["benchmark_id"] for e in c["evidence"]
                           if not excluded(e["benchmark_id"], e["source_url"])}
            for bid, raw in c["flat"].items():
                if excluded(bid):
                    drop("excluded_source")
                    continue
                if bid in sourced_ids:
                    drop("flat_shadowed_by_evidence")
                    continue
                page = pages.get(bid, {})
                if bid.startswith("arena_elo"):
                    tags = {"arena_elo_overall": ("chat",), "arena_elo_style_control": ("chat",),
                            "arena_elo_coding": ("chat", "coding"),
                            "arena_elo_math": ("chat", "math"),
                            "arena_elo_hard_prompts": ("chat", "reasoning"),
                            "arena_elo_vision": ("vision", "chat")}.get(bid, ("chat",))
                    o = Obs(mid, "flat:" + bid, raw, "lin", "flat_unsourced", d, "",
                            tags=tags, family="flat_arena")
                else:
                    v = _pct_value(raw, page)
                    tags = tags_for(bid, page)
                    if v is None or not tags:
                        drop("flat_unusable")
                        continue
                    o = Obs(mid, bid, v, "pct", "flat_unsourced", d, "",
                            tags=tags, family=_family(bid, page))
                key = (mid, o.item, "flat_unsourced")
                best[key] = (0, d, o)
    obs.extend(v[2] for v in best.values())

    arena_obs, unmatched = arena_observations(cards, arena, as_of)
    obs.extend(arena_obs)
    return Build(obs, dropped, quarantine or {}, unmatched)


def _family(bid: str, page: dict) -> str:
    """Subtask families whose members come from one run and share its errors."""
    for prefix in ("mmlu_", "multipl_e", "mteb_", "flores"):
        if bid.startswith(prefix) and bid not in ("mmlu_pro",):
            return prefix.rstrip("_")
    return ""


def arena_observations(cards: list[dict[str, Any]], arena: dict,
                       as_of: str) -> tuple[list[Obs], int]:
    matcher = Matcher(cards)
    out: list[Obs] = []
    unmatched = 0
    for board, snapshots in arena.items():
        if board not in ARENA_BOARDS:
            continue
        dates = sorted((d for d in snapshots if d <= as_of), reverse=True)
        if not dates:
            continue
        newest = dates[0]

        def product_rows(d: str) -> dict[str, tuple[int, list]]:
            nonlocal unmatched
            rows: dict[str, tuple[int, list]] = {}
            for r in snapshots[d]:
                mid, eff = matcher.match(r[0], r[1])
                if mid is None:
                    unmatched += d == newest
                    continue
                if mid not in rows or eff > rows[mid][0]:
                    rows[mid] = (eff, r)
            return rows

        latest = product_rows(newest)
        seen = set(latest)
        for mid, (_, r) in latest.items():
            out.append(_arena_obs(mid, board, r, newest, 0.0))
        for d in dates[1:]:
            older = product_rows(d)
            common = [m for m in older if m in latest]
            if len(common) < 10:
                continue
            shift = statistics.median(latest[m][1][2] - older[m][1][2] for m in common)
            for mid, (_, r) in older.items():
                if mid not in seen:
                    seen.add(mid)
                    out.append(_arena_obs(mid, board, r, d, shift))
    return out, unmatched


def _arena_obs(mid: str, board: str, r: list, d: str, shift: float) -> Obs:
    name, _org, rating, lo, hi, votes = r
    se = abs(hi - lo) / 3.92 if hi is not None and lo is not None else None
    return Obs(mid, board, rating + shift, "lin", "independent_evaluator", d, ARENA_URL,
               as_evaluated=name, version=board + (" (aligned)" if shift else ""),
               configuration=f"leaderboard_publish_date {d}; votes {votes}", se=se, live=True,
               tags=ARENA_BOARDS[board], family="arena_text" if board.startswith("text_") else "")


def days_between(a: str, b: str) -> int:
    return (date.fromisoformat(b) - date.fromisoformat(a)).days


def plus_days(d: str, n: int) -> str:
    return (date.fromisoformat(d) + timedelta(days=n)).isoformat()


def summarise(obs: Iterable[Obs]) -> dict[str, Any]:
    obs = list(obs)
    return {
        "observations": len(obs),
        "models": len({o.model_id for o in obs}),
        "items": len({o.item for o in obs}),
        "by_source_kind": _count(o.source_kind for o in obs),
        "by_link": _count(o.link for o in obs),
    }


def _count(xs: Iterable[str]) -> dict[str, int]:
    out: dict[str, int] = {}
    for x in xs:
        out[x] = out.get(x, 0) + 1
    return dict(sorted(out.items(), key=lambda kv: -kv[1]))


__all__ = ["Obs", "Build", "observations", "load_cards", "load_pages", "load_arena",
           "quarantine_flat", "excluded", "Matcher", "effort_of", "days_between",
           "plus_days", "summarise"]
