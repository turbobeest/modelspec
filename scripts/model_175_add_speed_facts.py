#!/usr/bin/env python3
"""Add MODEL-175 unknown speed facts to every slice-1 offering.

The source mapping is deliberately explicit. It records the provider page and
model page checked for each offering without treating a rate limit, a status
metric, or a qualitative speed claim as a latency measurement.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml


SPEED_FACETS = (
    "offering.speed.time_to_first_token",
    "offering.speed.throughput",
)

PROVIDER_SOURCES = {
    "alibaba-model-studio": "alibaba-model-studio-pricing",
    "anthropic": "anthropic-pricing",
    "aws-bedrock": "aws-pricing",
    "azure-ai-foundry": "azure-pricing",
    "deepseek": "deepseek-v4-pricing",
    "google-gemini-api": "gemini-pricing",
    "google-vertex-ai": "vertex-pricing",
    "meta-model-api": "meta-model-api-pricing",
    "openai": "openai-data",
    "typesafe": "typesafe-models",
    "xai": "xai-grok-4-7",
    "zai": "zai-pricing",
}

MODEL_SOURCES = {
    "qwen/qwen3-8-max-0902": "model-143-qwen-qwen3-8-max-0902",
    "anthropic/claude-fable-5": "model-143-anthropic-claude-fable-5",
    "anthropic/claude-fable-5-1": "model-143-anthropic-claude-fable-5-1",
    "anthropic/claude-opus-4-6": "model-143-anthropic-claude-opus-4-6",
    "anthropic/claude-opus-4-7": "model-143-anthropic-claude-opus-4-7",
    "anthropic/claude-opus-5": "model-143-anthropic-claude-opus-5",
    "anthropic/claude-opus-5-5": "model-143-anthropic-claude-opus-5-5",
    "deepseek/deepseek-v4-pro": "model-143-deepseek-deepseek-v4-pro",
    "google/gemini-3-1-pro-preview": "model-143-google-gemini-3-1-pro-preview",
    "google/gemini-3-5-flash": "model-143-google-gemini-3-5-flash",
    "google/gemini-3-7-flash": "model-143-google-gemini-3-7-flash",
    "google/gemini-3-8-flash": "model-143-google-gemini-3-8-flash",
    "meta/muse-spark-1-1": "model-143-meta-muse-spark-1-1",
    "meta/muse-spark-1-3": "model-143-meta-muse-spark-1-3",
    "openai/gpt-5-4": "model-143-openai-gpt-5-4",
    "openai/gpt-5-6-sol": "model-143-openai-gpt-5-6-sol",
    "openai/gpt-6-astra": "model-143-openai-gpt-6-astra",
    "openai/gpt-6-sol": "model-143-openai-gpt-6-sol",
    "typesafe/jev-1-13": "model-143-typesafe-jev-1-13",
    "xai/grok-4-7": "model-143-xai-grok-4-7",
    "zhipu/glm-5-2": "model-143-zai-glm-5-2-guide",
    "zhipu/glm-5-3": "model-143-zai-glm-5-3-guide",
}


def fact_yaml(offering_id: str, facet: str, checked_sources: tuple[str, ...]) -> str:
    lines = [
        f"  - id: {offering_id}#{facet}",
        "    subject:",
        "      kind: offering",
        f"      id: {offering_id}",
        f"    facet: {facet}",
        "    value: null",
        "    state: unknown",
        "    checked_sources:",
    ]
    lines.extend(f"    - {source_id}" for source_id in checked_sources)
    return "\n".join(lines) + "\n"


def update(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    rows = yaml.safe_load(text)
    if not isinstance(rows, list) or len(rows) != 1:
        raise ValueError(f"{path}: expected one offering row")
    offering = rows[0]
    model = offering["model"]
    provider = offering["provider"]
    offering_id = f"{provider}/{model}/{offering['region']}/{offering['tier']}"
    existing = {fact["facet"] for fact in offering.get("facts") or []}
    present = existing & set(SPEED_FACETS)
    if present:
        if present != set(SPEED_FACETS):
            raise ValueError(f"{path}: only part of the speed pair exists")
        return False
    try:
        checked = tuple(dict.fromkeys((PROVIDER_SOURCES[provider], MODEL_SOURCES[model])))
    except KeyError as exc:
        raise ValueError(f"{path}: no checked-source mapping for {exc.args[0]}") from exc
    addition = "".join(fact_yaml(offering_id, facet, checked) for facet in SPEED_FACETS)
    path.write_text(text.rstrip() + "\n" + addition, encoding="utf-8")
    return True


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=Path(__file__).resolve().parents[1], type=Path)
    args = parser.parse_args()
    changed = sum(update(path) for path in sorted((args.root / "offerings").glob("*/*/*.yaml")))
    print(f"updated {changed} offering files")


if __name__ == "__main__":
    main()
