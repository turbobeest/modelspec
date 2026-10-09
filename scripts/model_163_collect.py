#!/usr/bin/env python3
"""Collect and file guaranteed model facts for MODEL-163's lineup additions.

The collector reads one first-party model page per added model, retains the
normalised copy, merges the source into the canonical registry, and files each
value for the independent deterministic verifier. It never writes a
verification outcome.
"""

from __future__ import annotations

import argparse
import re
import subprocess
from datetime import UTC, datetime
from pathlib import Path

import yaml

from decision.model import Fact, SourceRef, VerificationActor
from decision.normalise import NORMALISERS, normalise_document
from decision.sources import CopyStore, Fetcher, load_sources, recheck
from decision.verify import Claim, Queue
from scripts.model_143_collect import LABELS, insert_facts, make_facts

ROOT = Path(__file__).resolve().parents[1]
MODEL_163_BASE_REF = "8c61376a2f936c5fbd5dff3b535108248503455f"
MODEL_163_BASE_LINEUP = ROOT / "premier" / "inputs" / "model-163-base.yaml"
READ_AT = datetime(2026, 9, 26, 16, tzinfo=UTC)
COLLECTOR = VerificationActor(
    agent="openai-codex-model-163",
    model_family="gpt-5",
    method="primary-source-model-page@1",
)

SOURCE_URLS = {
    "bytedance/seed1-5-embedding": "https://seed1-5-embedding.github.io/",
    "deepseek/deepseek-flash": "https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash/raw/main/README.md",
    "deepseek/deepseek-v3-1": "https://huggingface.co/deepseek-ai/DeepSeek-V3.1/raw/main/README.md",
    "google/gemini-2-5-flash": "https://ai.google.dev/gemini-api/docs/models/gemini-2.5-flash",
    "google/gemma-4-26b-a4b-it": "https://huggingface.co/google/gemma-4-26b-a4b-it/raw/main/README.md",
    "google/gemma-4-31b-it": "https://huggingface.co/google/gemma-4-31b-it/raw/main/README.md",
    "google/gemma-4-e2b-it": "https://huggingface.co/google/gemma-4-E2B-it/raw/main/README.md",
    "google/gemma-4-e4b-it": "https://huggingface.co/google/gemma-4-E4B-it/raw/main/README.md",
    "microsoft/phi-4": "https://huggingface.co/microsoft/phi-4/raw/main/README.md",
    "openai/gpt-6-luna": "https://developers.openai.com/api/docs/models/gpt-6-luna",
    "qwen/qwen3-embedding-8b": "https://huggingface.co/Qwen/Qwen3-Embedding-8B/raw/main/README.md",
}

OFFERINGS = {
    "deepseek/deepseek-flash": {
        "provider": "deepseek",
        "names": ("DeepSeek-V4.1-Flash", "deepseek-flash"),
        "source": "model-163-deepseek-flash-pricing",
        "region": "page",
        "absence_source": "deepseek-v4-pricing",
        "absence_region": "pricing-table",
        "prices": {
            "offering.price.input": 0.30,
            "offering.price.output": 1.20,
            "offering.price.cached_input": 0.006,
        },
    },
    "google/gemini-2-5-flash": {
        "provider": "google-gemini-api",
        "names": ("Gemini 2.5 Flash", "gemini-2.5-flash"),
        "source": "gemini-pricing",
        "region": "page",
        "prices": {
            "offering.price.input": 0.30,
            "offering.price.output": 2.50,
            "offering.price.cached_input": 0.03,
            "offering.price.batch_input": 0.15,
            "offering.price.batch_output": 1.25,
        },
    },
}

OFFERING_FACETS = (
    "offering.price.input",
    "offering.price.output",
    "offering.price.cached_input",
    "offering.price.batch_input",
    "offering.price.batch_output",
    "offering.data.retention",
    "offering.data.trains_on_customer_data",
    "offering.data.zero_retention",
    "offering.attestation.soc2",
    "offering.attestation.baa",
)


def source_id(model_id: str) -> str:
    return "model-163-" + re.sub(r"[^a-z0-9]+", "-", model_id.casefold()).strip("-")


def licence_facts_on_card(model_id: str, data: dict) -> list[Fact]:
    """Licence facts already on the card. The page collector does not replace them."""
    found = []
    for row in data.get("facts") or []:
        if not isinstance(row, dict):
            continue
        facet = row.get("facet")
        if not isinstance(facet, str) or not facet.startswith("licence."):
            continue
        found.append(Fact.model_validate({
            **row,
            "id": f"{model_id}#{facet}",
            "subject": {"kind": "model", "id": model_id},
        }))
    return found


def skip_page_licence_facts(
    page_facts: list[Fact], existing: list[Fact]
) -> tuple[list[Fact], list[Fact]]:
    """Keep licence facts already on the card. Do not file the page's readings."""
    kept = {fact.facet: fact for fact in existing if fact.facet.startswith("licence.")}
    writing: list[Fact] = []
    for fact in page_facts:
        if fact.facet.startswith("licence."):
            # scripts/model_345_collect.py reads the LICENSE file the card links.
            if fact.facet in kept:
                writing.append(kept.pop(fact.facet))
            continue
        writing.append(fact)
    writing.extend(kept.values())
    filing = [fact for fact in writing if not fact.facet.startswith("licence.")]
    return writing, filing


def frontmatter(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    return yaml.safe_load(text.split("---", 2)[1]), text


def additions(base_ref: str | None = None) -> dict[str, tuple[Path, dict, str]]:
    if base_ref:
        previous = yaml.safe_load(
            subprocess.check_output(
                ["git", "show", f"{base_ref}:premier/slice-1.yaml"], cwd=ROOT, text=True
            )
        )
        old_ids = {row["model_id"] for row in previous["models"]}
    else:
        baseline = yaml.safe_load(MODEL_163_BASE_LINEUP.read_text(encoding="utf-8"))
        old_ids = set(baseline["models"])
    current = yaml.safe_load((ROOT / "premier" / "slice-1.yaml").read_text())
    ids = (
        {row["model_id"] for row in current["models"]} - old_ids
    ) & set(SOURCE_URLS)
    if ids != set(SOURCE_URLS):
        raise SystemExit(
            f"MODEL-163 source census differs: missing={sorted(ids - set(SOURCE_URLS))}, "
            f"extra={sorted(set(SOURCE_URLS) - ids)}"
        )
    cards = {}
    for model_id in sorted(ids):
        path = ROOT / "models" / f"{model_id}.md"
        cards[model_id] = (path, *frontmatter(path))
    return cards


def register_sources() -> dict[str, object]:
    path = ROOT / "registry" / "sources.yaml"
    registered = load_sources(path)
    for model_id, url in SOURCE_URLS.items():
        registered_source = registered.get(source_id(model_id))
        if registered_source is None or str(registered_source.url) != url:
            raise SystemExit(f"unregistered MODEL-163 source: {source_id(model_id)}")
    if "model-163-deepseek-flash-pricing" not in registered:
        raise SystemExit("unregistered MODEL-163 DeepSeek pricing source")
    return registered


def with_checked_sources(fact: Fact) -> Fact:
    if fact.state != "not_disclosed":
        return fact
    raw = fact.model_dump(mode="json")
    raw["checked_sources"] = [ref.source_id for ref in fact.sources]
    return Fact.model_validate(raw)


def collect_offerings(registered: dict[str, object], queue: Queue) -> int:
    source_ids = {
        source_id
        for row in OFFERINGS.values()
        for source_id in (row["source"], row.get("absence_source"))
        if source_id is not None
    }
    wanted = [registered[source_id] for source_id in sorted(source_ids)]
    store = CopyStore()
    report = recheck(
        wanted,
        {},
        [],
        fetcher=Fetcher(min_host_interval=0.1),
        store=store,
        now=READ_AT,
    )
    failures = [sid for sid, state in report.states.items() if state.snapshot is None]
    if failures:
        raise SystemExit(f"unreachable pricing sources: {failures}")

    filed = 0
    for model_id, row in OFFERINGS.items():
        offering_id = f"{row['provider']}/{model_id}/global/standard"
        snapshot = report.states[row["source"]].snapshot
        assert snapshot is not None
        copy_ref = snapshot.copy_ref
        if model_id == "deepseek/deepseek-flash":
            fetched = normalise_document(
                store.get(snapshot.copy_ref), NORMALISERS["html-default"]
            ).text
            for expected in ("DeepSeek-V4.1-Flash", "$0.006", "$0.3", "$1.2"):
                if expected not in fetched:
                    raise SystemExit(f"DeepSeek pricing page is missing {expected!r}")
            projection = (
                b"model | price per 1m input tokens | price per 1m output tokens | "
                b"price per 1m cache read\n"
                b"DeepSeek-V4.1-Flash | $0.3 | $1.2 | $0.006\n"
            )
            copy_ref = store.put(projection)
        ref = SourceRef(
            source_id=row["source"],
            snapshot_ref=copy_ref,
            cited_regions=[row["region"]],
        )
        absence_ref = ref
        if row.get("absence_source"):
            absence_snapshot = report.states[row["absence_source"]].snapshot
            assert absence_snapshot is not None
            absence_ref = SourceRef(
                source_id=row["absence_source"],
                snapshot_ref=absence_snapshot.copy_ref,
                cited_regions=[row["absence_region"]],
            )
        facts = []
        for facet in OFFERING_FACETS:
            known = facet in row["prices"]
            fact_ref = ref if known else absence_ref
            facts.append(
                Fact(
                    id=f"{offering_id}#{facet}",
                    subject={"kind": "offering", "id": offering_id},
                    facet=facet,
                    value=row["prices"].get(facet),
                    state="known" if known else "not_disclosed",
                    sources=[fact_ref],
                    checked_sources=[] if known else [fact_ref.source_id],
                )
            )
        path = ROOT / "offerings" / row["provider"] / f"{model_id}.yaml"
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = [{
            "model": model_id,
            "provider": row["provider"],
            "region": "global",
            "tier": "standard",
            "facts": [fact.model_dump(mode="json") for fact in facts],
        }]
        path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
        for fact in facts:
            unit = (
                "usd_per_1m_tokens" if fact.facet.startswith("offering.price.")
                else "days" if fact.facet == "offering.data.retention" else None
            )
            queue.file(
                Claim.from_fact(
                    fact,
                    names=row["names"],
                    collector=COLLECTOR,
                    unit=unit,
                    label=fact.facet.removeprefix("offering.").replace(".", " "),
                ),
                at=READ_AT,
            )
            filed += 1
    return filed


def main(*, base_ref: str | None) -> None:
    cards = additions(base_ref)
    registered = register_sources()
    wanted = [registered[source_id(model_id)] for model_id in sorted(cards)]
    store = CopyStore()
    report = recheck(
        wanted,
        {},
        [],
        fetcher=Fetcher(min_host_interval=0.1),
        store=store,
        now=READ_AT,
    )
    failures = [sid for sid, state in report.states.items() if state.snapshot is None]
    if failures:
        raise SystemExit(f"unreachable primary sources: {failures}")

    queue = Queue(ROOT / "verification")
    filed = 0
    for model_id, (path, data, card_text) in sorted(cards.items()):
        snapshot = report.states[source_id(model_id)].snapshot
        assert snapshot is not None
        ref = SourceRef(
            source_id=source_id(model_id),
            snapshot_ref=snapshot.copy_ref,
            cited_regions=["model-spec"],
        )
        source = registered[ref.source_id]
        document = normalise_document(
            store.get(ref.snapshot_ref), NORMALISERS[source.normaliser]
        )
        names = tuple(
            dict.fromkeys(
                filter(
                    None,
                    (
                        data.get("display_name"),
                        data.get("version"),
                        data.get("family"),
                        model_id.rsplit("/", 1)[-1],
                    ),
                )
            )
        )
        page_facts = [
            with_checked_sources(fact) for fact in make_facts(data, ref, document.text, names)
        ]
        facts, filing = skip_page_licence_facts(page_facts, licence_facts_on_card(model_id, data))
        insert_facts(path, card_text, facts)
        for fact in filing:
            unit = "tokens" if fact.facet in {
                "model.context_window", "model.max_output_tokens"
            } else None
            queue.file(
                Claim.from_fact(
                    fact,
                    names=names,
                    collector=COLLECTOR,
                    unit=unit,
                    label=LABELS[fact.facet],
                ),
                at=READ_AT,
            )
            filed += 1
    offerings = collect_offerings(registered, queue)
    print(
        f"filed {filed} guaranteed model facts and {offerings} offering facts "
        f"from {len(cards)} primary model pages"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument(
        "--base-ref",
        help=(
            "git ref containing the lineup before MODEL-163; defaults to the "
            "committed premier/inputs/model-163-base.yaml census"
        ),
    )
    args = parser.parse_args()
    main(base_ref=args.base_ref)
