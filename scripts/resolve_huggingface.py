#!/usr/bin/env python3
"""Resolve each model card to its Hugging Face repository.

Nothing in the corpus knows where a model lives: `availability.huggingface.url`
is the bare `https://huggingface.co/` on every card and `model_id` is empty. So
no enrichment — geometry, expert counts, benchmark scores — has an address to
fetch from. This produces those addresses.

**The top search hit is frequently wrong.** Searching "Qwen3 32B" returns three
community quantisations before `Qwen/Qwen3-32B`, which has five million
downloads. Taking the first result would attach another model's layer count and
expert count to the card, arriving as structured, correctly-typed, confident
data that nothing downstream would question. That is worse than the empty field
it replaces.

So a match must earn its place on four signals, and anything that does not clear
the bar is left unresolved and reported. An unresolved card is a known gap; a
wrongly resolved one is a fabricated fact.

    python scripts/resolve_huggingface.py --dry-run --limit 40
    python scripts/resolve_huggingface.py
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import httpx  # noqa: E402
import yaml  # noqa: E402

from schema.card import ModelCard  # noqa: E402

API = "https://huggingface.co/api/models"

#: A repository whose name carries one of these is a derivative — a
#: quantisation, a conversion, a merge — not the model the card describes. Its
#: config.json may differ from the original in exactly the fields we want.
DERIVATIVE_MARKERS = (
    "gguf", "exl2", "exl3", "bpw", "awq", "gptq", "nvfp4", "fp8-dynamic",
    "-int4", "-int8", "-w4a16", "-w8a8", "mlx", "onnx", "openvino", "-hf-",
    "abliterated", "uncensored", "heretic", "lora", "-merge", "distill-",
)

#: Card provider slug -> the organisation that publishes on Hugging Face. Only
#: needed where the two differ; an exact match is tried first.
ORG_ALIASES = {
    "qwen": "Qwen", "alibaba": "Qwen", "mistral": "mistralai",
    "meta": "meta-llama", "google": "google", "microsoft": "microsoft",
    "deepseek": "deepseek-ai", "zhipu": "zai-org", "01-ai": "01-ai",
    "nous-research": "NousResearch", "allen-ai": "allenai", "baai": "BAAI",
    "cohere": "CohereLabs", "nvidia": "nvidia", "ibm": "ibm-granite",
    "stability-ai": "stabilityai", "tii": "tiiuae", "upstage": "upstage",
    "baichuan": "baichuan-inc", "intfloat": "intfloat", "jina": "jinaai",
    "liquid": "LiquidAI", "moonshot": "moonshotai", "minimax": "MiniMaxAI",
    "ai21": "ai21labs", "salesforce": "Salesforce", "stability": "stabilityai",
    "tencent": "tencent", "black-forest-labs": "black-forest-labs",
    "rwkv": "RWKV", "sentence-transformers": "sentence-transformers",
    "unsloth": "unsloth", "nomic": "nomic-ai", "bytedance": "ByteDance",
    "openbmb": "openbmb", "internlm": "internlm", "xai": "xai-org",
    "cerebras": "cerebras", "databricks": "databricks", "snowflake": "Snowflake",
    "apple": "apple", "amazon": "amazon", "inception": "inclusionAI",
}

#: Below this a match is refused. Set so that an organisation match plus a
#: strong name match clears it and little else does.
CONFIDENCE_FLOOR = 0.72


def normalise(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", text.lower())


@dataclass
class Candidate:
    repo_id: str
    downloads: int
    score: float = 0.0
    reasons: list[str] = field(default_factory=list)


def score_candidate(repo_id: str, downloads: int, card_org: str,
                    card_name: str) -> Candidate:
    """Four signals: organisation, name, derivative penalty, popularity."""
    candidate = Candidate(repo_id=repo_id, downloads=downloads)
    org, _, name = repo_id.partition("/")
    lower = repo_id.lower()

    # 1. Organisation. The strongest signal by far: the publisher of a model is
    #    not usually in doubt, and a mismatch usually means a third-party copy.
    expected = ORG_ALIASES.get(card_org, card_org)
    if normalise(org) == normalise(expected):
        candidate.score += 0.45
        candidate.reasons.append("org matches")
    elif normalise(card_org) in normalise(org) or normalise(org) in normalise(card_org):
        candidate.score += 0.20
        candidate.reasons.append("org partially matches")

    # 2. Name.
    target, actual = normalise(card_name), normalise(name)
    if actual == target:
        candidate.score += 0.45
        candidate.reasons.append("name matches exactly")
    elif target and (target in actual or actual in target):
        ratio = min(len(target), len(actual)) / max(len(target), len(actual))
        candidate.score += 0.30 * ratio
        candidate.reasons.append(f"name contains ({ratio:.2f})")

    # 3. Derivatives — but only ones the card is not itself asking for.
    #
    #    Many cards describe a quantisation: qwen/qwen3-32b-awq is an AWQ build,
    #    and its correct repository is an AWQ repository. Penalising every
    #    derivative marker rejected exactly the right match for those cards and
    #    refused all 90 Qwen, 54 Mistral and 50 NVIDIA models. Only markers the
    #    card does not carry itself count against a candidate.
    card_lower = card_name.lower()
    unwanted = [m for m in DERIVATIVE_MARKERS
                if m in lower and m.strip("-") not in card_lower]
    if unwanted:
        candidate.score -= 0.60
        candidate.reasons.append(f"unrequested derivative ({unwanted[0]})")

    # 4. Popularity, as a tie-break only. It corroborates; it never decides.
    if downloads >= 100_000:
        candidate.score += 0.10
        candidate.reasons.append("widely downloaded")
    elif downloads >= 10_000:
        candidate.score += 0.05

    return candidate


def resolve(client: httpx.Client, card: ModelCard) -> Candidate | None:
    org = (card.identity.provider or "").strip()
    name = card.identity.model_id.split("/", 1)[-1]
    query = (card.identity.display_name or name).strip()
    try:
        response = client.get(API, params={"search": query, "limit": 10})
        response.raise_for_status()
        results = response.json()
    except Exception:
        return None
    scored = [
        score_candidate(m.get("id", ""), int(m.get("downloads") or 0), org, name)
        for m in results if m.get("id")
    ]
    if not scored:
        return None
    best = max(scored, key=lambda c: c.score)
    return best if best.score >= CONFIDENCE_FLOOR else None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int, default=0, help="only the first N cards")
    parser.add_argument("--report", default="benchmarks/_census/hf_resolution.json")
    args = parser.parse_args()

    paths = [p for p in sorted((PROJECT_ROOT / "models").rglob("*.md"))
             if p.name != "LICENSE.md"]
    cards = [(p, ModelCard.from_yaml_file(p)) for p in paths]
    targets = [(p, c) for p, c in cards if c.licensing.open_weights]
    if args.limit:
        targets = targets[:args.limit]

    resolved: dict[str, dict] = {}
    refused: list[str] = []

    with httpx.Client(timeout=30, follow_redirects=True,
                      headers={"User-Agent": "ModelSpec-Resolver/1.0"}) as client:
        for index, (path, card) in enumerate(targets, 1):
            best = resolve(client, card)
            if best is None:
                refused.append(card.identity.model_id)
            else:
                resolved[card.identity.model_id] = {
                    "repo_id": best.repo_id,
                    "confidence": round(best.score, 3),
                    "downloads": best.downloads,
                    "why": best.reasons,
                }
                if not args.dry_run:
                    _write_repo_id(path, best.repo_id)
            if index % 25 == 0:
                print(f"  {index}/{len(targets)}  resolved={len(resolved)} refused={len(refused)}")
            time.sleep(0.12)  # be a good citizen of someone else's API

    report = {
        "considered": len(targets),
        "resolved": len(resolved),
        "refused": len(refused),
        "confidence_floor": CONFIDENCE_FLOOR,
        "resolutions": resolved,
        "refused_ids": refused,
    }
    out = PROJECT_ROOT / args.report
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=1, sort_keys=True), encoding="utf-8")

    print(f"\nconsidered {len(targets)}  resolved {len(resolved)}  "
          f"refused {len(refused)}  ({100*len(resolved)//max(1,len(targets))}%)")
    print(f"report: {out.relative_to(PROJECT_ROOT)}")
    return 0


def _write_repo_id(path: Path, repo_id: str) -> None:
    text = path.read_text(encoding="utf-8")
    front_raw, body = text.split("---", 2)[1], text.split("---", 2)[2]
    front = yaml.safe_load(front_raw)
    hf = (front.setdefault("availability", {}) or {}).setdefault("huggingface", {}) or {}
    hf["model_id"] = repo_id
    hf["url"] = f"https://huggingface.co/{repo_id}"
    hf["available"] = True
    front["availability"]["huggingface"] = hf
    path.write_text(
        "---\n" + yaml.safe_dump(front, sort_keys=False, allow_unicode=True) + "---" + body,
        encoding="utf-8")
    ModelCard.from_yaml_file(path)


if __name__ == "__main__":
    raise SystemExit(main())
