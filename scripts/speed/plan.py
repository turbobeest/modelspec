"""A run plan: which offerings, which calls, and what they can cost.

Prices come from the offerings' own verified price facts, in US dollars per
million tokens. The spend cap is checked against a worst-case bound: every
input token is at least one UTF-8 byte, and output is capped by ``max_tokens``
plus any output the provider may bill beyond it. The bound assumes current
prices and a provider that honours its own limits; ``run.py`` also checks the
reported spend before every call.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from scripts.speed.method import (
    HEADLINE_WORKLOAD,
    WORKLOADS,
    Workload,
    nonce_line,
    workload,
)
from scripts.speed.providers import APIS

ROOT = Path(__file__).resolve().parents[2]
PILOT = Path(__file__).with_name("pilot.yaml")

#: Bytes in a nonce line (16 hex characters), and tokens of message framing.
NONCE_BYTES = len(nonce_line("0" * 16).encode("utf-8"))
FRAMING_TOKENS = 64
#: Planning estimate only: English prose averages about four bytes a token.
BYTES_PER_TOKEN_EXPECTED = 4


class PlanError(ValueError):
    pass


@dataclass(frozen=True)
class Entry:
    offering: str
    api: str
    api_model: str
    effort: str
    price_input: float
    price_output: float
    params: dict[str, Any] = field(default_factory=dict)
    output_bound_extra: int = 0
    #: The pinned effort claims no reasoning. Aggregation holds the offering's
    #: numbers if its streams report reasoning tokens anyway.
    reasoning_off: bool = False
    #: Smoke sends it; the pilot slot does not.
    smoke_only: bool = False


@dataclass(frozen=True)
class Plan:
    name: str
    entries: tuple[Entry, ...]
    repetitions: int
    warmups: int

    @property
    def env(self) -> tuple[str, ...]:
        return tuple(sorted({APIS[e.api].env for e in self.entries}))


@dataclass(frozen=True)
class Call:
    entry: Entry
    workload: Workload
    sample: int
    warmup: bool


def _prices(root: Path, offering: str) -> tuple[float, float]:
    provider, lab, model, region, tier = offering.split("/")
    path = root / "offerings" / provider / lab / f"{model}.yaml"
    if not path.is_file():
        raise PlanError(f"{offering}: no offering file at {path}")
    for row in yaml.safe_load(path.read_text(encoding="utf-8")) or []:
        if row.get("region") == region and row.get("tier") == tier:
            facts = {f["facet"]: f for f in row.get("facts") or []}
            prices = []
            for facet in ("offering.price.input", "offering.price.output"):
                fact = facts.get(facet) or {}
                if fact.get("state") != "known" or not isinstance(fact.get("value"), int | float):
                    raise PlanError(f"{offering}: {facet} is not known, so spend has no bound")
                prices.append(float(fact["value"]))
            return prices[0], prices[1]
    raise PlanError(f"{offering}: no {region}/{tier} row in {path}")


def load_plan(path: Path = PILOT, root: Path = ROOT, *, smoke: bool = False) -> Plan:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    entries = []
    for row in data["offerings"]:
        if row.get("smoke_only") and not smoke:
            continue
        if row["api"] not in APIS:
            raise PlanError(f"{row['offering']}: unknown api {row['api']!r}")
        price_input, price_output = _prices(root, row["offering"])
        entries.append(Entry(
            offering=row["offering"], api=row["api"], api_model=row["api_model"],
            effort=row["effort"], price_input=price_input, price_output=price_output,
            params=dict(row.get("params") or {}),
            output_bound_extra=int(row.get("output_bound_extra") or 0),
            reasoning_off=bool(row.get("reasoning_off", False)),
            smoke_only=bool(row.get("smoke_only", False)),
        ))
    return Plan(str(data["plan"]), tuple(entries), int(data["repetitions_per_slot"]),
                int(data["warmups_per_slot"]))


def calls(plan: Plan, seed: str) -> list[Call]:
    """One slot's calls: warm-ups first, then round-robin over a shuffled lineup.

    Round-robin spreads each offering's samples across the slot, so a burst of
    provider load does not land on one offering's whole sample.
    """
    order = list(plan.entries)
    random.Random(seed).shuffle(order)
    out = [Call(e, workload(HEADLINE_WORKLOAD), i, True)
           for e in order for i in range(plan.warmups)]
    for rep in range(plan.repetitions):
        for e in order:
            for w in WORKLOADS:
                out.append(Call(e, w, rep, False))
    return out


def _usd(entry: Entry, input_tokens: float, output_tokens: float) -> float:
    return (input_tokens * entry.price_input + output_tokens * entry.price_output) / 1e6


def call_bound_usd(call: Call) -> float:
    """The most one call can cost."""
    prompt_bytes = len(call.workload.prompt().encode("utf-8")) + NONCE_BYTES
    output = call.workload.max_output_tokens + call.entry.output_bound_extra
    return _usd(call.entry, prompt_bytes + FRAMING_TOKENS, output)


def call_expected_usd(call: Call) -> float:
    prompt_bytes = len(call.workload.prompt().encode("utf-8")) + NONCE_BYTES
    return _usd(call.entry, prompt_bytes / BYTES_PER_TOKEN_EXPECTED + FRAMING_TOKENS,
                call.workload.max_output_tokens)


def usage_usd(entry: Entry, input_tokens: int, billed_output_tokens: int) -> float:
    return _usd(entry, input_tokens, billed_output_tokens)


@dataclass(frozen=True)
class Cost:
    calls: int
    expected_usd: float
    bound_usd: float


def slot_cost(plan: Plan) -> Cost:
    planned = calls(plan, "cost")
    return Cost(len(planned), sum(map(call_expected_usd, planned)),
                sum(map(call_bound_usd, planned)))


def entry_cost(plan: Plan) -> dict[str, Cost]:
    planned = calls(plan, "cost")
    out = {}
    for e in plan.entries:
        mine = [c for c in planned if c.entry is e]
        out[e.offering] = Cost(len(mine), sum(map(call_expected_usd, mine)),
                               sum(map(call_bound_usd, mine)))
    return out
