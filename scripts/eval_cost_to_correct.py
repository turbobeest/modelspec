#!/usr/bin/env python3
"""Cost-to-correct: one task, identical inputs, a decision model and LLMs (MODEL-99).

LIVE and PAID: this calls the TypeSafe API and an OpenAI-compatible endpoint.
It is never run by the test suite or by CI. Run it by hand, with the keys in
the environment (or in a file outside this repository, via ``--env-file``):

    python scripts/eval_cost_to_correct.py \\
        --api-json api.json --out run.jsonl.gz --max-usd 0.25 --limit 20

Re-derive the table from a stored run, with no call and no key:

    python scripts/eval_cost_to_correct.py --analyse scripts/cost_to_correct_2026-09-20.jsonl.gz

What it measures
----------------
MMLU and SWE-bench score *generated answers*, so a decision model has no score
on them and never will. One metric does span the classes, and it is the one an
engineer needs: **for this task, what does a correct answer cost, in money and
in time?**

The task is the creator-attribution judgment of MODEL-82: given a models.dev
listing and the same model's ids on other platforms, which organisation trained
and released it — or ``cannot_establish``? Ground truth is
``scripts/eval_attribution.py``'s: cards whose creator is established by
something other than a models.dev page. Only the ``real`` variant is used here
(the evidence exactly as production gathers it); the adversarial variants stay
in ``eval_attribution.py``, which this script does not modify.

Method discipline
-----------------
- The case set is built **once** and every arm is handed the *same* state and
  the *same* questions. Each row carries ``request_sha256`` over
  ``{state, questions}``; a sceptic can confirm the arms saw identical bytes.
- The LLM arms receive Jev's own state and Jev's own questions, verbatim, as
  JSON. The only addition is the sentence that names the reply format, because
  an LLM has no typed answer channel. That is the adapter, not a better prompt.
- A malformed, truncated, refused or out-of-vocabulary answer is a **wrong
  answer**, recorded and counted. Dropping failures flatters an arm.
- Prices are read from the provider at run time and published with the date and
  the source URL.

Disclosure: ModelSpec pays for TypeSafe and depends on Jev (MODEL-101). A
result that flatters a supplier and cannot be re-run by a stranger is worth
nothing, so the harness, the case construction and the raw rows are all here.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import random
import re
import statistics
import sys
import threading
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

import httpx

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts import attribution as A  # noqa: E402, N812
from scripts import eval_attribution as E  # noqa: E402, N812
from scripts.seed_models_dev import PROVIDER_MAP  # noqa: E402

# TypeSafe publishes one input-token price per model; there is no output charge.
# https://docs.typesafe.ai/models — jev-1.13.0, $42 per Btok / $0.042 per Mtok.
JEV_PRICE_SOURCE = "https://docs.typesafe.ai/models"

REPLY_FORMAT = (
    "Answer with one JSON object and nothing else, in this shape:\n"
    '{"creator": {"choice": "<exactly one key from the creator question\'s criteria>"}, '
    '"reseller": {"noul": <number from 0 to 1>}}'
)

SYSTEM_PROMPT = (
    "You answer questions about the state you are given. "
    "Judge only from the state. Do not use outside knowledge of the models named."
)

REFUSAL = re.compile(
    r"\b(i (?:can(?:no|')t|am unable|won't)|as an ai|i'm sorry|cannot comply)\b", re.I
)


# ── Arms ──────────────────────────────────────────────────────────


@dataclass
class Arm:
    """One thing being measured: a name, how to ask it, and what it costs."""

    name: str
    kind: str  # "jev" | "llm"
    model: str
    price_in_usd_per_token: float = 0.0
    price_out_usd_per_token: float = 0.0
    price_source: str = ""
    price_read_utc: str = ""

    def cost(self, tokens_in: int, tokens_out: int) -> float:
        return tokens_in * self.price_in_usd_per_token + tokens_out * self.price_out_usd_per_token

    def as_dict(self) -> dict:
        return {
            "arm": self.name,
            "kind": self.kind,
            "model": self.model,
            "price_in_usd_per_mtok": round(self.price_in_usd_per_token * 1e6, 6),
            "price_out_usd_per_mtok": round(self.price_out_usd_per_token * 1e6, 6),
            "price_source": self.price_source,
            "price_read_utc": self.price_read_utc,
        }


def parse_arm_spec(spec: str) -> tuple[str, str]:
    """``jev`` or ``llm:<model-id>`` -> (kind, model)."""
    if spec == "jev":
        return "jev", ""
    if spec.startswith("llm:") and len(spec) > 4:
        return "llm", spec[4:]
    raise ValueError(f"unrecognised arm {spec!r}: use 'jev' or 'llm:<model-id>'")


def load_env_file(path: Path) -> None:
    """Read KEY=VALUE lines into the environment. Values are never logged."""
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if key and key not in os.environ:
            os.environ[key] = value.strip().strip('"').strip("'")


def openrouter_prices(base_url: str, api_key: str, models: list[str]) -> dict[str, dict]:
    """List prices straight from the endpoint, so the date read is the run's own."""
    read_utc = datetime.now(UTC).isoformat(timespec="seconds")
    url = base_url.rstrip("/") + "/models"
    resp = httpx.get(url, headers={"Authorization": f"Bearer {api_key}"}, timeout=60)
    resp.raise_for_status()
    catalogue = {m["id"]: m for m in resp.json()["data"]}
    out = {}
    for model in models:
        entry = catalogue.get(model)
        if entry is None:
            raise SystemExit(f"{model} is not listed at {url}; pick a model that is")
        pricing = entry.get("pricing") or {}
        out[model] = {
            "price_in": float(pricing["prompt"]),
            "price_out": float(pricing["completion"]),
            "source": url,
            "read_utc": read_utc,
        }
    return out


# ── The case set: built once, shared by every arm ─────────────────


def build_cases(api_data: dict, config: A.Config, per_card: int, seed: int) -> list[dict]:
    """The ``real`` variant of ``eval_attribution.py``, with its ground truth.

    The random draws that variant does not need (the ``withheld`` decoy, the
    relisted host) are still taken, in the same order, so that for a given seed
    and api.json this set is exactly the ``real`` subset of an
    ``eval_attribution.py`` run — the two scripts stay comparable.
    """
    models_dir = PROJECT_ROOT / "models"
    page_orgs = {pid: cfg["slug"] for pid, cfg in PROVIDER_MAP.items()}
    registry = A.load_registry(models_dir, PROVIDER_MAP)
    index = A.ListingIndex.build(api_data, config)
    cards = E.established_cards(models_dir, api_data, config, registry, page_orgs)
    rng = random.Random(seed)
    sizes = Counter(p.parent.name for p in models_dir.glob("*/*.md"))
    big_orgs = sorted(o for o, _ in sizes.most_common(20) if o in registry)

    cases: list[dict] = []
    for card in cards:
        found = E.listings_for(card, index, api_data, config)
        if not found:
            continue
        truth = card["provider"]

        def vendor(pid: str) -> str | None:
            return page_orgs.get(pid) or config.creator_namespaces.get(pid.lower())

        rng.shuffle(found)
        found.sort(key=lambda f: (vendor(f[0]) in (None, truth), f[0]))
        seen_pids: set[str] = set()
        for pid, lid, raw in found:
            if pid in seen_pids:
                continue
            seen_pids.add(pid)
            listing = A.Listing(
                pid,
                str(api_data[pid].get("name", pid)),
                lid,
                str(raw.get("name", "")),
                str(raw.get("family", "")),
            )
            ev = A.gather_evidence(listing, index, config, registry, page_orgs)
            det = A.decide_deterministically(ev, registry)
            rng.choice([o for o in big_orgs if o != truth])  # the withheld decoy draw
            if ev.candidates:
                state = A.build_state(ev)
                questions = A.build_questions(ev.candidates, registry, config)
                blob = json.dumps({"state": state, "questions": questions}, sort_keys=True)
                cases.append(
                    {
                        "case_id": hashlib.sha256(
                            f"{card['path']}|{pid}|{lid}".encode()
                        ).hexdigest()[:16],
                        "request_sha256": hashlib.sha256(blob.encode()).hexdigest(),
                        "card": card["path"],
                        "truth": truth,
                        "why": card["why"],
                        "platform": pid,
                        "listed_id": lid,
                        "vendor": ev.vendor,
                        "deterministic": det.creator if det else None,
                        "deterministic_status": det.status if det else "ambiguous",
                        "variant": "real",
                        "candidates": ev.candidates,
                        # The answer a correct arm gives: the creator when it is
                        # on the list, otherwise the honest abstention.
                        "expected": truth if truth in ev.candidates else A.CANNOT_ESTABLISH,
                        "state": state,
                        "questions": questions,
                    }
                )
            if len(seen_pids) >= per_card:
                break
        hosts = [p for p in page_orgs if p in api_data and page_orgs[p] != truth]
        rng.choice(hosts)  # the relisted host draw
    return cases


# ── Asking one arm one case ───────────────────────────────────────


@dataclass
class Answer:
    choice: str | None
    tokens_in: int
    tokens_out: int
    latency_ms: float
    attempts: int
    failure: str | None = None
    detail: str = ""
    extra: dict = field(default_factory=dict)


def ask_jev(judge: A.TypeSafeJudge, case: dict) -> Answer:
    started = time.perf_counter()
    try:
        body = judge.evaluate(case["state"], case["questions"])
    except A.JudgeUnavailable as exc:
        return Answer(None, 0, 0, (time.perf_counter() - started) * 1000, 1, "api_error", str(exc))
    latency = (time.perf_counter() - started) * 1000
    usage = body.get("usage") or {}
    tokens_in = int(usage.get("input_tokens") or 0)
    tokens_out = int(usage.get("output_tokens") or 0)
    try:
        answers = A.parse_answers(body, case["candidates"])
    except A.JudgeUnavailable as exc:
        return Answer(None, tokens_in, tokens_out, latency, 1, "parse_failure", str(exc))
    choice = answers["choice"]
    if choice not in case["candidates"] and choice != A.CANNOT_ESTABLISH:
        return Answer(
            choice,
            tokens_in,
            tokens_out,
            latency,
            1,
            "invalid_choice",
            choice,
            {"confidence": answers["confidence"]},
        )
    return Answer(
        choice,
        tokens_in,
        tokens_out,
        latency,
        1,
        None,
        "",
        {"confidence": answers["confidence"], "reseller": answers["reseller"]},
    )


def llm_prompt(case: dict) -> list[dict]:
    """Jev's state and Jev's questions, verbatim, plus the reply format."""
    payload = json.dumps(
        {"state": case["state"], "questions": case["questions"]}, indent=2, sort_keys=True
    )
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"{payload}\n\n{REPLY_FORMAT}"},
    ]


JSON_BLOCK = re.compile(r"\{.*\}", re.S)


def extract_choice(text: str) -> tuple[str | None, str]:
    """Pull the creator choice out of a reply. Returns (choice, failure_kind)."""
    if not text.strip():
        return None, "empty_reply"
    body = text.strip()
    if body.startswith("```"):
        body = re.sub(r"^```[a-zA-Z]*\n?|```$", "", body).strip()
    match = JSON_BLOCK.search(body)
    if match is None:
        return None, "refusal" if REFUSAL.search(body) else "no_json"
    try:
        parsed = json.loads(match.group(0))
    except json.JSONDecodeError:
        return None, "bad_json"
    creator = parsed.get("creator") if isinstance(parsed, dict) else None
    if isinstance(creator, dict) and "choice" in creator:
        return str(creator["choice"]), ""
    if isinstance(parsed, dict) and isinstance(parsed.get("choice"), str):
        return str(parsed["choice"]), ""  # a shape that still answers the question
    return None, "missing_choice"


def ask_llm(
    client: httpx.Client, arm: Arm, case: dict, api_key: str, max_tokens: int, retries: int
) -> Answer:
    body = {
        "model": arm.model,
        "messages": llm_prompt(case),
        "max_tokens": max_tokens,
        "usage": {"include": True},
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    delay, last, latency = 1.0, "", 0.0
    for attempt in range(retries + 1):
        started = time.perf_counter()
        try:
            resp = client.post("/chat/completions", json=body, headers=headers)
        except httpx.HTTPError as exc:
            latency = (time.perf_counter() - started) * 1000
            last = type(exc).__name__
        else:
            latency = (time.perf_counter() - started) * 1000
            if resp.status_code == 200:
                data = resp.json()
                if "error" in data and not data.get("choices"):
                    last = f"upstream: {str(data['error'])[:120]}"
                else:
                    return _from_completion(data, latency, attempt + 1, case)
            else:
                last = f"HTTP {resp.status_code}"
                if resp.status_code not in (408, 429, 500, 502, 503, 504, 529):
                    break
        if attempt < retries:
            time.sleep(delay)
            delay *= 2
    return Answer(None, 0, 0, latency, retries + 1, "api_error", last)


def _from_completion(data: dict, latency: float, attempts: int, case: dict) -> Answer:
    usage = data.get("usage") or {}
    tokens_in = int(usage.get("prompt_tokens") or 0)
    tokens_out = int(usage.get("completion_tokens") or 0)
    extra: dict = {}
    if usage.get("cost") is not None:
        extra["provider_reported_cost_usd"] = float(usage["cost"])
    choice_obj = (data.get("choices") or [{}])[0]
    finish = str(choice_obj.get("finish_reason") or "")
    text = str((choice_obj.get("message") or {}).get("content") or "")
    choice, failure = extract_choice(text)
    if choice is None:
        kind = "truncated" if finish == "length" else failure
        return Answer(None, tokens_in, tokens_out, latency, attempts, kind, text[:200], extra)
    if choice not in case["candidates"] and choice != A.CANNOT_ESTABLISH:
        return Answer(
            choice, tokens_in, tokens_out, latency, attempts, "invalid_choice", choice[:200], extra
        )
    return Answer(choice, tokens_in, tokens_out, latency, attempts, None, "", extra)


# ── Scoring ───────────────────────────────────────────────────────


def failure_kind(row: dict) -> str:
    """Why an answer was wrong. Right answers get ``correct``."""
    if row["correct"]:
        return "correct"
    if row["failure"]:
        return row["failure"]
    expected, chosen = row["expected"], row["choice"]
    if chosen == A.CANNOT_ESTABLISH:
        return "abstained_when_answerable"
    if expected == A.CANNOT_ESTABLISH:
        return "named_an_org_when_unestablishable"
    return "wrong_org"


def summarise(rows: list[dict], arms: dict[str, dict]) -> list[dict]:
    out = []
    for name, meta in arms.items():
        mine = [r for r in rows if r["arm"] == name]
        if not mine:
            continue
        correct = sum(1 for r in mine if r["correct"])
        latencies = sorted(r["latency_ms"] for r in mine if r["failure"] != "api_error")
        cost = sum(r["cost_usd"] for r in mine)
        answered = [r for r in mine if r["failure"] != "api_error"]
        summary = dict(meta)
        summary.update(
            {
                "n": len(mine),
                "correct": correct,
                "accuracy": round(correct / len(mine), 4),
                "accuracy_excluding_api_errors": (
                    round(correct / len(answered), 4) if answered else None
                ),
                "p50_latency_ms": round(_pct(latencies, 0.50), 1),
                "p95_latency_ms": round(_pct(latencies, 0.95), 1),
                "total_cost_usd": round(cost, 6),
                "cost_per_1000_correct_usd": (round(cost / correct * 1000, 4) if correct else None),
                "mean_input_tokens": round(
                    statistics.mean([r["tokens_in"] for r in mine]) if mine else 0, 1
                ),
                "mean_output_tokens": round(
                    statistics.mean([r["tokens_out"] for r in mine]) if mine else 0, 1
                ),
                "failure_kinds": dict(Counter(failure_kind(r) for r in mine).most_common()),
                "provider_reported_cost_usd": round(
                    sum(float(r.get("provider_reported_cost_usd") or 0) for r in mine), 6
                ),
            }
        )
        out.append(summary)
    return out


def _pct(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    idx = min(len(values) - 1, max(0, int(round(q * (len(values) - 1)))))
    return values[idx]


def render_table(summaries: list[dict]) -> str:
    head = (
        "| arm | model | n | accuracy | p50 ms | p95 ms | total $ | $ / 1,000 correct |\n"
        "| --- | --- | --: | --: | --: | --: | --: | --: |\n"
    )
    lines = []
    for s in summaries:
        per_k = s["cost_per_1000_correct_usd"]
        lines.append(
            f"| {s['arm']} | `{s['model'] or s['arm']}` | {s['n']} | "
            f"{s['accuracy'] * 100:.1f}% | {s['p50_latency_ms']:.0f} | {s['p95_latency_ms']:.0f} | "
            f"${s['total_cost_usd']:.4f} | "
            f"{'—' if per_k is None else f'${per_k:.3f}'} |"
        )
    return head + "\n".join(lines)


# ── Runner ────────────────────────────────────────────────────────


def open_out(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix == ".gz":
        return gzip.open(path, "wt", encoding="utf-8")
    return path.open("w", encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--api-json", type=Path, help="a saved https://models.dev/api.json")
    ap.add_argument("--out", type=Path, help="per-item rows, one JSON per line (.gz allowed)")
    ap.add_argument(
        "--arms",
        default="jev,llm:openai/gpt-5-nano,llm:openai/gpt-5-mini",
        help="comma-separated: 'jev' and/or 'llm:<model-id>'",
    )
    ap.add_argument("--per-card", type=int, default=2, help="listings judged per card")
    ap.add_argument("--limit", type=int, default=0, help="first N cases only (0 = all)")
    ap.add_argument("--max-usd", type=float, default=0.0, help="hard spend cap; aborts before it")
    ap.add_argument("--workers", type=int, default=4, help="concurrent requests per arm")
    ap.add_argument("--max-tokens", type=int, default=2000, help="LLM output ceiling")
    ap.add_argument("--retries", type=int, default=3)
    ap.add_argument("--seed", type=int, default=82)
    ap.add_argument("--env-file", type=Path, help="KEY=VALUE file, read into the environment")
    ap.add_argument("--plan-only", action="store_true", help="count and project; call nothing")
    ap.add_argument("--analyse", type=Path, help="recompute the table from a stored run")
    args = ap.parse_args()

    if args.analyse:
        opener = gzip.open if args.analyse.suffix == ".gz" else open
        rows, stored = [], None
        with opener(args.analyse, "rt", encoding="utf-8") as handle:
            for line in handle:
                row = json.loads(line)
                (rows.append(row) if row.get("record") == "item" else None)
                if row.get("record") == "summary":
                    stored = row
        arms = {a["arm"]: a for a in (stored or {}).get("arms", [])}
        summaries = summarise(rows, arms)
        print(render_table(summaries))
        print(json.dumps(summaries, indent=2))
        return

    if not args.api_json or (not args.plan_only and not args.out):
        sys.exit("--api-json is required, and --out unless --plan-only")
    if args.env_file:
        load_env_file(args.env_file)

    config = A.load_config()
    api_data = json.loads(args.api_json.read_bytes())
    cases = build_cases(api_data, config, args.per_card, args.seed)
    if args.limit:
        cases = cases[: args.limit]
    specs = [parse_arm_spec(s.strip()) for s in args.arms.split(",") if s.strip()]

    # A rough projection, from the prompt's own size. Four characters to the
    # token is the usual English ratio; it is a projection, not a bill.
    est_in = [len(json.dumps(c["state"])) + len(json.dumps(c["questions"])) for c in cases]
    mean_in = (sum(est_in) / len(est_in) / 4) if cases else 0.0

    if args.plan_only:
        print(
            json.dumps(
                {
                    "cases": len(cases),
                    "arms": [f"{k}:{m}" if m else k for k, m in specs],
                    "mean_estimated_input_tokens": round(mean_in),
                    "note": "per-arm cost needs the live prices; run without --plan-only",
                },
                indent=2,
            )
        )
        return

    if args.max_usd <= 0:
        sys.exit("--max-usd must be set above 0: this run spends money")

    llm_models = [m for k, m in specs if k == "llm"]
    base_url = os.environ.get("TEXT_MODEL_BASE_URL", "").strip().rstrip("/")
    llm_key = os.environ.get("TEXT_MODEL_API_KEY", "").strip()
    prices: dict[str, dict] = {}
    if llm_models:
        if not (base_url and llm_key):
            sys.exit("TEXT_MODEL_BASE_URL and TEXT_MODEL_API_KEY are not set")
        prices = openrouter_prices(base_url, llm_key, llm_models)

    judge = None
    arms: list[Arm] = []
    for kind, model in specs:
        if kind == "jev":
            judge = A.TypeSafeJudge.from_env(config)
            if judge is None:
                sys.exit("TYPESAFE_API_KEY is not set")
            arms.append(
                Arm(
                    "jev",
                    "jev",
                    config.model,
                    price_in_usd_per_token=0.042 / 1e6,
                    price_out_usd_per_token=0.0,
                    price_source=JEV_PRICE_SOURCE,
                    price_read_utc=datetime.now(UTC).isoformat(timespec="seconds"),
                )
            )
        else:
            p = prices[model]
            arms.append(
                Arm(
                    model,
                    "llm",
                    model,
                    price_in_usd_per_token=p["price_in"],
                    price_out_usd_per_token=p["price_out"],
                    price_source=p["source"],
                    price_read_utc=p["read_utc"],
                )
            )

    projection = {
        a.name: round(len(cases) * a.cost(int(mean_in * 1.35), 120 if a.kind == "llm" else 0), 4)
        for a in arms
    }
    total_projection = round(sum(projection.values()), 4)
    print(
        f"cases: {len(cases)}; arms: {[a.name for a in arms]}; "
        f"projection: {projection} total ${total_projection:.4f}; cap ${args.max_usd:.2f}",
        file=sys.stderr,
    )
    if total_projection > args.max_usd:
        sys.exit(
            f"projected ${total_projection:.4f} exceeds --max-usd ${args.max_usd:.2f}; "
            "nothing was called"
        )

    lock = threading.Lock()
    spent = {"usd": 0.0, "calls": 0, "capped": 0}
    started_utc = datetime.now(UTC).isoformat(timespec="seconds")
    handle = open_out(args.out)
    client = httpx.Client(base_url=base_url, timeout=120.0) if llm_models else None

    def run_one(arm: Arm, case: dict) -> None:
        reserve = arm.cost(int(mean_in * 2), 400 if arm.kind == "llm" else 0)
        with lock:
            if spent["usd"] + reserve > args.max_usd:
                spent["capped"] += 1
                return
        if arm.kind == "jev":
            answer = ask_jev(judge, case)
        else:
            answer = ask_llm(client, arm, case, llm_key, args.max_tokens, args.retries)
        cost = arm.cost(answer.tokens_in, answer.tokens_out)
        row = {
            "record": "item",
            "arm": arm.name,
            "model": arm.model,
            "case_id": case["case_id"],
            "request_sha256": case["request_sha256"],
            "card": case["card"],
            "platform": case["platform"],
            "listed_id": case["listed_id"],
            "variant": case["variant"],
            "why": case["why"],
            "truth": case["truth"],
            "expected": case["expected"],
            "n_candidates": len(case["candidates"]),
            "deterministic_status": case["deterministic_status"],
            "choice": answer.choice,
            "correct": answer.choice == case["expected"] and answer.failure is None,
            "failure": answer.failure,
            "failure_detail": answer.detail,
            "latency_ms": round(answer.latency_ms, 1),
            "attempts": answer.attempts,
            "tokens_in": answer.tokens_in,
            "tokens_out": answer.tokens_out,
            "cost_usd": cost,
            **answer.extra,
        }
        with lock:
            spent["usd"] += cost
            spent["calls"] += 1
            handle.write(json.dumps(row, sort_keys=True) + "\n")
            handle.flush()  # a paid row reaches the disk before the next call

    rows: list[dict] = []
    for arm in arms:
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            list(pool.map(lambda c, a=arm: run_one(a, c), cases))

    handle.close()
    # Read the rows back to summarise: the file is the record, not memory.
    opener = gzip.open if args.out.suffix == ".gz" else open
    with opener(args.out, "rt", encoding="utf-8") as fh:
        rows = [json.loads(line) for line in fh]

    summaries = summarise(rows, {a.name: a.as_dict() for a in arms})
    summary = {
        "record": "summary",
        "ticket": "MODEL-99",
        "task": "creator-attribution (MODEL-82), variant=real",
        "started_utc": started_utc,
        "finished_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "api_json_sha256": hashlib.sha256(args.api_json.read_bytes()).hexdigest(),
        "api_json_source": "https://models.dev/api.json",
        "cases": len(cases),
        "seed": args.seed,
        "per_card": args.per_card,
        "workers": args.workers,
        "max_tokens": args.max_tokens,
        "max_usd": args.max_usd,
        "spent_usd": round(spent["usd"], 6),
        "calls": spent["calls"],
        "skipped_by_cap": spent["capped"],
        "identical_inputs": len({r["request_sha256"] for r in rows})
        == len({r["case_id"] for r in rows}),
        "arms": summaries,
    }
    with (
        gzip.open(args.out, "at", encoding="utf-8")
        if args.out.suffix == ".gz"
        else args.out.open("a", encoding="utf-8")
    ) as fh:
        fh.write(json.dumps(summary, sort_keys=True) + "\n")

    print(render_table(summaries))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
