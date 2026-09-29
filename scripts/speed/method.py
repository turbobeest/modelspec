"""The speed method, speed-v1, as code (MODEL-212).

Everything a published number depends on is fixed here and in
``docs/method/speed-measurement.md``: the workloads and their exact prompts,
the sampling schedule, the publication gates and the statistics. A change to
any of them is a new method version, never an edit to speed-v1.
"""

from __future__ import annotations

import hashlib
import math
import random
import statistics
from dataclasses import dataclass
from pathlib import Path

METHOD_ID = "speed-v1"
METHOD_URL = (
    "https://github.com/turbobeest/modelspec/blob/main/docs/method/speed-measurement.md"
)

#: The workload whose medians become the offering's speed facts. The other
#: workloads are published beside it in the measurement file.
HEADLINE_WORKLOAD = "short_chat"

#: Scheduled UTC hours. One run is one slot: every offering, every workload.
SLOT_HOURS_UTC = (0, 6, 12, 18)
#: Measured requests per offering, workload and slot, after one warm-up.
REPETITIONS_PER_SLOT = 2
WARMUPS_PER_SLOT = 1

#: Publication gates. A workload that misses any of them publishes nothing.
#: Samples within one slot share provider load, so at most
#: ``REPETITIONS_PER_SLOT`` count from each slot, and the slots must span every
#: scheduled hour: the interval then rests on many independent slots.
MIN_SAMPLES = 20
MIN_SLOTS = 8
MIN_DAYS = 2
MAX_WINDOW_DAYS = 7
MAX_FAILURE_RATE = 0.2
#: A throughput from fewer visible tokens is dominated by chunking.
MIN_VISIBLE_TOKENS = 32
#: Below this many content events, the chunk correction in ``throughput`` is
#: too coarse to trust.
MIN_CONTENT_EVENTS = 16

#: The level of the median's distribution-free interval.
INTERVAL_LEVEL = 0.95

_PROMPTS = Path(__file__).with_name("prompts")


@dataclass(frozen=True)
class Workload:
    id: str
    max_output_tokens: int
    description: str

    def prompt(self) -> str:
        if self.id == "long_context":
            return long_context_prompt()
        return (_PROMPTS / f"{self.id}.txt").read_text(encoding="utf-8")

    def prompt_sha256(self) -> str:
        return "sha256:" + hashlib.sha256(self.prompt().encode("utf-8")).hexdigest()


WORKLOADS = (
    Workload("short_chat", 256, "About 150 input tokens; asks for a long plain-language answer."),
    Workload("coding", 512, "About 1,800 input tokens of Python; asks for a pytest module."),
    Workload("long_context", 256, "About 30,000 input tokens of ledger text; asks for a summary."),
)
WORKLOAD_IDS = tuple(w.id for w in WORKLOADS)


def workload(workload_id: str) -> Workload:
    for w in WORKLOADS:
        if w.id == workload_id:
            return w
    raise KeyError(workload_id)


_PLACES = ("north", "south", "east", "west", "harbour", "river", "hill", "market")
_GOODS = ("bolts", "rope", "timber", "glass", "cloth", "paint", "wire", "nails",
          "tiles", "pipes", "lamps", "chalk", "brushes", "hinges", "valves", "gaskets")
_ACTIONS = ("received from", "sent to", "counted at", "returned to", "moved within")
_NOTES = ("the pallet was damaged on arrival and set aside for inspection",
          "the count matched the delivery note exactly",
          "two boxes were relabelled because the supplier code was wrong",
          "the driver arrived late, so the goods waited in the yard overnight",
          "a supervisor signed off the variance after a second count",
          "the order was split across two bays to make room for the new racking",
          "quality control asked for a sample to be kept for testing",
          "the goods were reserved for a customer order due next week")


def long_context_prompt(lines: int = 1150) -> str:
    """A fixed ledger of about 30,000 tokens. The seed and text are part of speed-v1."""
    rng = random.Random(212)
    body = []
    for i in range(1, lines + 1):
        body.append(
            f"Line {i}. {rng.choice(_GOODS).capitalize()} {rng.choice(_ACTIONS)} the "
            f"{rng.choice(_PLACES)} store; {rng.choice(_NOTES)}."
        )
    return (
        "The following is a warehouse movement log. Read all of it.\n\n"
        + "\n".join(body)
        + "\n\nSummarise this log for the warehouse manager: describe the main patterns "
        "by store and by kind of goods, then list every recurring problem with examples. "
        "Write at least 800 words and do not stop early.\n"
    )


def throughput(visible_tokens: int, content_events: int, first_s: float, last_s: float
               ) -> float:
    """Visible tokens a second after the first content event.

    The first event carries its share of the tokens before the clock starts.
    With ``e`` events of about ``N / e`` tokens each, the tokens after it are
    ``N * (e - 1) / e``. Counting ``N - 1`` instead reads a provider that sends
    32 tokens an event about 14% fast, a bias that differs by provider.
    """
    return visible_tokens * (content_events - 1) / content_events / (last_s - first_s)


def nonce_line(nonce: str) -> str:
    """The first line of every request: a unique prefix defeats prompt caches."""
    return f"Request {nonce}.\n"


# ── statistics ─────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class Summary:
    n: int
    median: float
    iqr: tuple[float, float]
    interval: tuple[float, float]


def median_interval(values: list[float], level: float = INTERVAL_LEVEL) -> tuple[float, float]:
    """The distribution-free interval of the median from order statistics.

    It is the narrowest symmetric pair of order statistics whose binomial tail
    on each side is at most (1 - level) / 2, so it covers the true median with
    probability at least ``level`` whatever the distribution. Below six samples
    no pair qualifies; the full range is returned and covers less than ``level``.
    """
    xs = sorted(values)
    n = len(xs)
    alpha = (1 - level) / 2
    j = 0
    tail = 0.0
    for i in range(n):
        tail += math.comb(n, i) / 2**n
        if tail > alpha:
            break
        j = i + 1
    if j == 0:
        return xs[0], xs[-1]
    return xs[j - 1], xs[n - j]


def summarise(values: list[float]) -> Summary:
    if not values:
        raise ValueError("no samples to summarise")
    xs = sorted(values)
    if len(xs) == 1:
        q1 = q3 = xs[0]
    else:
        q1, _, q3 = statistics.quantiles(xs, n=4, method="inclusive")
    return Summary(
        n=len(xs),
        median=statistics.median(xs),
        iqr=(q1, q3),
        interval=median_interval(xs),
    )
