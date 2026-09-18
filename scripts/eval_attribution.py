#!/usr/bin/env python3
"""Measure the creator judgment against the catalogue's own cards (MODEL-82).

LIVE and PAID: this calls the TypeSafe API. It is never run by the test suite
or by CI. Run it by hand, with the key in the environment only:

    TYPESAFE_API_KEY="$(op read 'op://AI-LAN/<item>/credential')" \\
      python scripts/eval_attribution.py --api-json api.json --out eval.jsonl

Re-derive the bands from stored judgments, with no call and no key:

    python scripts/eval_attribution.py --analyse scripts/attribution_eval_2026-09-17.jsonl.gz

The committed run: models.dev api.json sha256 abc545da…e3f4 fetched
2026-09-17, jev-1.13.0, 3,510 judgments, 2,577,218 input tokens, $0.108.

What it measures
----------------
Ground truth is the provider on cards whose creator is established by
something other than a models.dev page:

- written or curated by a person (``card_author`` modelspec / manual /
  api-model-seeder);
- seeded from a Hugging Face repo whose namespace maps to the card's provider
  in ``creator_namespaces`` (``Qwen/Qwen3-8B`` for ``qwen/qwen3-8b``);
- seeded from models.dev, but corroborated independently: a product name or a
  creator prefix elsewhere names the same organisation.

Cards the corpus sweep flags are excluded, whatever their author.

Each established card is matched to models.dev listings of the same bare id on
any page, and each listing is judged in three shapes:

``real``      the evidence exactly as production gathers it;
``day_one``   no other platform lists it yet: only the listing itself, its
              name and family, and the page. The shape of a just-released
              model, which is when daily research meets it;
``withheld``  the real evidence with the true creator removed from the options
              and from the listed ids, and one large catalogue organisation
              added as a decoy. The only right answer is ``cannot_establish``.

And, once per card, the PR #92 shape built on purpose: the same listing moved,
bare, onto another seeded organisation's own page (Kimi K3 on Alibaba's):

``relisted``           real cross-listings, a wrong page;
``relisted_day_one``   no cross-listings: the page and the name only;
``relisted_withheld``  the true creator removed from the options, the page's
                       organisation still offered. Any pick is a
                       misattribution to the platform that lists it.

Every judgment is asked with the production questions (``build_questions``) and
stored raw, so the bands can be recomputed without another call.
"""

from __future__ import annotations

import argparse
import dataclasses
import hashlib
import json
import random
import sys
import threading
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts import attribution as A  # noqa: E402, N812
from scripts.seed_models_dev import PROVIDER_MAP  # noqa: E402

HUMAN_AUTHORS = {"modelspec", "manual", "api-model-seeder"}


def established_cards(
    models_dir: Path, api_data: dict, config: A.Config, registry, page_orgs
) -> list[dict]:
    index = A.ListingIndex.build(api_data, config)
    flagged = {h.path for h in A.sweep_corpus(models_dir, api_data, registry, page_orgs, config)}
    out = []
    for path in sorted(models_dir.glob("*/*.md")):
        rel = str(path.relative_to(models_dir.parent))
        if rel in flagged:
            continue
        data = yaml.safe_load(path.read_text(encoding="utf-8").split("---", 2)[1]) or {}
        provider = str(data.get("provider") or "")
        if provider not in registry:
            continue
        author = str(data.get("card_author") or "")
        slug = str(data.get("model_id", "")).split("/", 1)[-1]
        version = str(data.get("version") or "")
        why = None
        if author in HUMAN_AUTHORS:
            why = "curated"
        elif author == "huggingface-seeder":
            hf = str((data.get("sources") or {}).get("huggingface_url") or "")
            ns = hf.rstrip("/").split("/")[-2].lower() if hf.count("/") >= 4 else ""
            if config.creator_namespaces.get(ns) == provider:
                why = "hf-namespace"
        elif author == "models.dev-seeder":
            listing = A.Listing(
                "-",
                "-",
                version or slug,
                str(data.get("display_name") or ""),
                str(data.get("family") or ""),
            )
            ev = A.gather_evidence(listing, index, config, registry, page_orgs)
            if provider in ev.named_orgs or provider in ev.prefix_orgs:
                why = "corroborated"
        # Deterministic disagreement anywhere means the card is not ground truth.
        listing = A.Listing(
            "-",
            "-",
            version or slug,
            str(data.get("display_name") or ""),
            str(data.get("family") or ""),
        )
        ev = A.gather_evidence(listing, index, config, registry, page_orgs)
        settled = A.decide_deterministically(ev, registry)
        if settled and settled.creator and settled.creator != provider:
            why = None
        if why:
            out.append(
                {"path": rel, "provider": provider, "slug": slug, "version": version, "why": why}
            )
    return out


def listings_for(
    card: dict, index: A.ListingIndex, api_data: dict, config: A.Config
) -> list[tuple[str, str, dict]]:
    keys = {A.normalise(card["slug"])}
    if card["version"]:
        keys.add(A.normalise(A.split_id(card["version"], config)[1]))
    found = []
    for key in keys:
        for pid, lid in index.by_bare.get(key, []):
            if "/" in lid:
                continue  # a prefixed id is settled by code; the judgment never sees it
            models = api_data[pid]["models"]
            raw = next((r for k, r in models.items() if str(r.get("id", k)) == lid), None)
            if raw is not None:
                found.append((pid, lid, raw))
    return found


def day_one(ev: A.Evidence, registry) -> A.Evidence:
    ev = dataclasses.replace(
        ev, elsewhere=[], prefix_orgs={}, unregistered_prefixes=[], first_party_orgs=set()
    )
    ev.candidates = A.candidate_orgs(ev, registry)
    return ev


def withheld(
    ev: A.Evidence, truth: str, config: A.Config, registry, decoy: str | None = None
) -> A.Evidence | None:
    def names_truth(lid: str) -> bool:
        p, _ = A.split_id(lid, config)
        return bool(p) and config.creator_namespaces.get(p) == truth

    ev = dataclasses.replace(
        ev,
        elsewhere=[(p, lid) for p, lid in ev.elsewhere if not names_truth(lid)],
        prefix_orgs={o: v for o, v in ev.prefix_orgs.items() if o != truth},
        first_party_orgs=ev.first_party_orgs - {truth},
    )
    ev.candidates = sorted(
        {c for c in A.candidate_orgs(ev, registry) if c != truth} | ({decoy} if decoy else set())
    )
    return ev if ev.candidates else None


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument(
        "--api-json", type=Path, required=True, help="a saved https://models.dev/api.json"
    )
    ap.add_argument("--out", type=Path, required=True, help="raw judgments, one JSON per line")
    ap.add_argument("--per-card", type=int, default=2, help="listings judged per card")
    ap.add_argument("--max-input-tokens", type=int, default=6_000_000, help="hard spend cap")
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--seed", type=int, default=82)
    ap.add_argument("--plan-only", action="store_true", help="count the cases; call nothing")
    ap.add_argument(
        "--cache",
        type=Path,
        default=None,
        help="a judgment ledger; requests already in it are not paid for again",
    )
    args = ap.parse_args()

    config = A.load_config()
    judge = A.TypeSafeJudge.from_env(config)
    if judge is None and not args.plan_only:
        sys.exit("TYPESAFE_API_KEY is not set")
    raw_bytes = args.api_json.read_bytes()
    api_data = json.loads(raw_bytes)
    models_dir = PROJECT_ROOT / "models"
    page_orgs = {pid: cfg["slug"] for pid, cfg in PROVIDER_MAP.items()}
    registry = A.load_registry(models_dir, PROVIDER_MAP)
    index = A.ListingIndex.build(api_data, config)
    cards = established_cards(models_dir, api_data, config, registry, page_orgs)
    rng = random.Random(args.seed)
    from collections import Counter

    sizes = Counter(p.parent.name for p in models_dir.glob("*/*.md"))
    big_orgs = sorted(o for o, _ in sizes.most_common(20) if o in registry)

    cases = []
    matched = 0
    for card in cards:
        found = listings_for(card, index, api_data, config)
        if not found:
            continue
        matched += 1
        truth = card["provider"]

        # Prefer listings where the page's organisation is not the creator:
        # that is the failure MODEL-82 is about.
        def vendor(pid: str) -> str | None:
            return page_orgs.get(pid) or config.creator_namespaces.get(pid.lower())

        rng.shuffle(found)
        found.sort(key=lambda f: (vendor(f[0]) in (None, truth), f[0]))
        seen_pids = set()
        for pid, lid, raw in found:
            if pid in seen_pids:
                continue
            seen_pids.add(pid)
            name = str(api_data[pid].get("name", pid))
            listing = A.Listing(
                pid, name, lid, str(raw.get("name", "")), str(raw.get("family", ""))
            )
            ev = A.gather_evidence(listing, index, config, registry, page_orgs)
            det = A.decide_deterministically(ev, registry)
            base = {
                "card": card["path"],
                "truth": truth,
                "why": card["why"],
                "platform": pid,
                "listed_id": lid,
                "vendor": ev.vendor,
                "deterministic": det.creator if det else None,
                "deterministic_status": det.status if det else "ambiguous",
            }
            variants = [("real", ev), ("day_one", day_one(ev, registry))]
            # A decoy keeps the question honest when nothing else is left to
            # pick: one of the largest catalogue organisations, never the truth.
            decoy = rng.choice([o for o in big_orgs if o != truth])
            w = withheld(ev, truth, config, registry, decoy)
            if w is not None:
                variants.append(("withheld", w))
            for name_v, v in variants:
                if not v.candidates:
                    continue
                expected = truth if truth in v.candidates else A.CANNOT_ESTABLISH
                cases.append(
                    (
                        base
                        | {"variant": name_v, "expected": expected, "candidates": v.candidates},
                        v,
                    )
                )
            if len(seen_pids) >= args.per_card:
                break

        # The PR #92 shape, on purpose: the same model offered, bare, on a
        # different organisation's own page (Kimi K3 on Alibaba's). Real name,
        # family and cross-listings; only the page is moved.
        pid, lid, raw = found[0]
        hosts = [p for p in page_orgs if p in api_data and page_orgs[p] != truth]
        host = rng.choice(hosts)
        listing = A.Listing(
            host,
            str(api_data[host].get("name", host)),
            lid,
            str(raw.get("name", "")),
            str(raw.get("family", "")),
        )
        ev = A.gather_evidence(listing, index, config, registry, page_orgs)
        det = A.decide_deterministically(ev, registry)
        base = {
            "card": card["path"],
            "truth": truth,
            "why": card["why"],
            "platform": host,
            "listed_id": lid,
            "vendor": ev.vendor,
            "deterministic": det.creator if det else None,
            "deterministic_status": det.status if det else "ambiguous",
        }
        relisted = [("relisted", ev), ("relisted_day_one", day_one(ev, registry))]
        w = withheld(ev, truth, config, registry)
        if w is not None:
            relisted.append(("relisted_withheld", w))
        for name_v, v in relisted:
            if v.candidates:
                expected = truth if truth in v.candidates else A.CANNOT_ESTABLISH
                cases.append(
                    (
                        base
                        | {"variant": name_v, "expected": expected, "candidates": v.candidates},
                        v,
                    )
                )

    print(
        f"established cards: {len(cards)}; matched to a bare-id listing: {matched}; "
        f"judgments to make: {len(cases)}",
        file=sys.stderr,
    )

    if args.plan_only:
        print(
            Counter(m["variant"] for m, _ in cases),
            Counter(m["deterministic_status"] for m, _ in cases if m["variant"] == "real"),
            Counter(c["why"] for c in cards),
        )
        return

    lock = threading.Lock()
    spent = {"input": 0, "calls": 0, "failed": 0, "cached": 0}
    cache = A.Ledger(args.cache)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    out = args.out.open("w", encoding="utf-8")

    def run(item):
        meta, ev = item
        with lock:
            if spent["input"] >= args.max_input_tokens:
                return
        state = A.build_state(ev)
        questions = A.build_questions(ev.candidates, registry, config)
        key = A.request_key(judge.model, state, questions)
        with lock:
            cached = cache.get(key)
        if cached is not None:
            with lock:
                spent["cached"] += 1
                out.write(
                    json.dumps(
                        meta | {"answers": cached["answers"], "input_tokens": 0}, sort_keys=True
                    )
                    + "\n"
                )
            return
        try:
            body = judge.evaluate(state, questions)
            answers = A.parse_answers(body, ev.candidates)
        except A.JudgeUnavailable as exc:
            with lock:
                spent["failed"] += 1
            print(f"failed: {exc}", file=sys.stderr)
            return
        tokens = int((body.get("usage") or {}).get("input_tokens") or 0)
        with lock:
            cache.put({"key": key, "answers": answers, "usage": {"input_tokens": tokens}})
        row = meta | {"answers": answers, "input_tokens": tokens}
        with lock:
            spent["input"] += tokens
            spent["calls"] += 1
            out.write(json.dumps(row, sort_keys=True) + "\n")

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        list(pool.map(run, cases))
    out.close()
    summary = {
        "api_json_sha256": hashlib.sha256(raw_bytes).hexdigest(),
        "model": config.model,
        "established_cards": len(cards),
        "established_by": {
            k: sum(1 for c in cards if c["why"] == k)
            for k in ("curated", "hf-namespace", "corroborated")
        },
        "matched_cards": matched,
        "cases": len(cases),
        "calls": spent["calls"],
        "failed": spent["failed"],
        "cached": spent["cached"],
        "input_tokens": spent["input"],
        "cost_usd": round(spent["input"] * 0.042 / 1_000_000, 4),
    }
    print(json.dumps(summary, indent=2))


# ── Analysis: no calls, recomputed from stored judgments ─────────

BANDS = [(0.0, 0.5), (0.5, 0.6), (0.6, 0.7), (0.7, 0.8), (0.8, 0.9), (0.9, 0.95), (0.95, 1.01)]


def outcome(row: dict) -> str:
    choice, expected = row["answers"]["choice"], row["expected"]
    if choice == expected:
        return "right"
    if choice == A.CANNOT_ESTABLISH:
        return "abstained"  # the creator was among the options; no harm, lost coverage
    return "wrong_org"  # a published misattribution, if written


def vetoed(row: dict, veto: float) -> bool:
    a = row["answers"]
    return a["choice"] == row["vendor"] and a["reseller"] >= veto


def analyse(rows: list[dict], config: A.Config) -> str:
    lines = []
    th = config.thresholds

    def table(title, subset):
        lines.append(f"\n{title} (n={len(subset)})")
        lines.append(
            f"{'confidence':>12} {'n':>5} {'right':>6} {'abstain':>8} {'wrong':>6} {'acc':>7}"
        )
        for lo, hi in BANDS:
            b = [r for r in subset if lo <= r["answers"]["confidence"] < hi]
            if not b:
                continue
            o = defaultdict(int)
            for r in b:
                o[outcome(r)] += 1
            lines.append(
                f"{lo:>5.2f}-{min(hi, 1.0):<5.2f} {len(b):>5} {o['right']:>6} {o['abstained']:>8} "
                f"{o['wrong_org']:>6} {o['right'] / len(b):>7.1%}"
            )

    lines.append("Deterministic path (no model call), on the same listings:")
    for v in ("real", "relisted"):
        d = [r for r in rows if r["variant"] == v and r["deterministic_status"] == A.DETERMINISTIC]
        right = sum(1 for r in d if r["deterministic"] == r["truth"])
        lines.append(
            f"  {v:>9}: settled {len(d)} of {sum(1 for r in rows if r['variant'] == v)}, "
            f"right {right}, wrong {len(d) - right}"
        )
        for r in d:
            if r["deterministic"] != r["truth"]:
                lines.append(
                    f"      wrong: {r['platform']}/{r['listed_id']} -> {r['deterministic']}, "
                    f"card says {r['truth']}"
                )

    table("All judgments", rows)
    for v in ("real", "day_one", "withheld", "relisted", "relisted_day_one", "relisted_withheld"):
        table(f"Variant {v}", [r for r in rows if r["variant"] == v])
    table(
        "real, where code could not settle it (what production sends to Jev)",
        [r for r in rows if r["variant"] == "real" and r["deterministic_status"] == "ambiguous"],
    )

    lines.append(
        "\nWrite threshold sweep: picks of an organisation at or above t (reseller veto applied)"
    )
    lines.append(
        f"{'t':>5} {'written':>8} {'wrong':>6} {'precision':>10} {'of right picks kept':>20}"
    )
    picks = [
        r
        for r in rows
        if r["answers"]["choice"] != A.CANNOT_ESTABLISH and not vetoed(r, th.reseller_veto)
    ]
    right_total = sum(1 for r in picks if outcome(r) == "right")
    for t in (0.5, 0.6, 0.7, 0.8, 0.85, 0.9, 0.95, 0.98):
        w = [r for r in picks if r["answers"]["confidence"] >= t]
        wrong = sum(1 for r in w if outcome(r) == "wrong_org")
        right = len(w) - wrong
        lines.append(
            f"{t:>5.2f} {len(w):>8} {wrong:>6} {(right / len(w) if w else 0):>10.2%} "
            f"{right / right_total:>20.1%}"
        )

    veto_hits = [
        r
        for r in rows
        if r["answers"]["choice"] != A.CANNOT_ESTABLISH and vetoed(r, th.reseller_veto)
    ]
    lines.append(
        f"\nReseller veto at {th.reseller_veto}: blocked {len(veto_hits)} "
        "picks of the listing page's org, "
        f"{sum(1 for r in veto_hits if outcome(r) == 'wrong_org')} of them wrong."
    )

    lines.append(f"\nPolicy as configured (write >= {th.write}, review >= {th.review}):")
    policy = defaultdict(lambda: defaultdict(int))
    for r in rows:
        ev = A.Evidence(
            A.Listing(r["platform"], "", r["listed_id"], "", ""),
            "",
            r["vendor"],
            None,
            None,
            [],
            {},
            [],
            set(),
            set(),
        )
        res = A.apply_policy(ev, r["answers"], r["candidates"], th)
        created = res.creator is not None
        key = res.status
        policy[key]["n"] += 1
        policy[key]["wrong"] += int(created and res.creator != r["expected"])
        policy[key]["right"] += int(created and res.creator == r["expected"])
        policy[key]["null_correct"] += int(not created and r["expected"] == A.CANNOT_ESTABLISH)
    for key in (A.WRITTEN, A.REVIEW, A.WITHHELD):
        p = policy[key]
        lines.append(
            f"  {key:>9}: {p['n']:>5}  creator right {p['right']:>5}, wrong {p['wrong']:>3}, "
            f"null where nothing was right {p['null_correct']:>4}"
        )

    lines.append("\nWrong organisations picked at confidence >= review threshold:")
    for r in sorted(rows, key=lambda r: -r["answers"]["confidence"]):
        if (
            outcome(r) == "wrong_org"
            and r["answers"]["confidence"] >= th.review
            and not vetoed(r, th.reseller_veto)
        ):
            lines.append(
                f"  {r['variant']:>8} {r['platform']}/{r['listed_id']}: "
                f"picked {r['answers']['choice']} ({r['answers']['confidence']:.2f}), "
                f"expected {r['expected']}; options {r['candidates']}"
            )
    return "\n".join(lines)


def load_rows(path: Path) -> list[dict]:
    import gzip

    text = (
        gzip.decompress(path.read_bytes()).decode("utf-8")
        if path.suffix == ".gz"
        else path.read_text(encoding="utf-8")
    )
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def analyse_main(path: Path) -> None:
    print(analyse(load_rows(path), A.load_config()))


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--analyse":
        analyse_main(Path(sys.argv[2]))
    else:
        main()
