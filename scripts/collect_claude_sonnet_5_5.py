#!/usr/bin/env python3
"""Collect Claude Sonnet 5.5 from first-party sources read on 2026-09-28.

The script creates the card and its three announced offerings, retains the
source copies, and files every fact and piece of evidence for two-key
verification. It resolves AWS's public pricing template against AWS's public
metered-unit map because the Bedrock table is rendered in the browser.
"""

from __future__ import annotations

import copy
import hashlib
import html
import json
import re
from datetime import UTC, datetime
from pathlib import Path

import httpx
import yaml

from decision.model import Evidence, Fact, VerificationActor
from decision.normalise import NORMALISERS, Locator, normalise_document, select_region
from decision.registry import default as default_registry
from decision.sources import CopyStore
from decision.verify import Claim, Queue

ROOT = Path(__file__).resolve().parents[1]
READ_DATE = "2026-09-28"
READ_AT = datetime(2026, 9, 28, 16, tzinfo=UTC)
MODEL_ID = "anthropic/claude-sonnet-5-5"
MODEL_NAMES = ("Claude Sonnet 5.5", "Sonnet 5.5", "claude-sonnet-5-5")
COLLECTOR = VerificationActor(
    agent="codex-model-s55",
    model_family="gpt-5",
    method="primary-source-release-collection@1",
)

MODEL_URL = "https://platform.claude.com/docs/en/models/sonnet-5-5/overview"
LAUNCH_URL = "https://www.anthropic.com/claude-sonnet-5-5"
ANTHROPIC_PRICING_URL = "https://platform.claude.com/docs/en/about-claude/pricing"
AWS_PRICING_URL = "https://aws.amazon.com/bedrock/pricing/"
AWS_PRICE_MAP_URL = (
    "https://b0.p.awsstatic.com/pricing/2.0/meteredUnitMaps/"
    "bedrockfoundationmodels/USD/current/bedrockfoundationmodels.json"
)
VERTEX_PRICING_URL = (
    "https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing"
)
COMMERCIAL_TERMS_URL = "https://www.anthropic.com/legal/commercial-terms"
ANTHROPIC_RETENTION_URL = "https://privacy.claude.com/en/articles/7996866-how-long-do-you-store-my-organization-s-data"
ANTHROPIC_TRAINING_URL = "https://privacy.claude.com/en/articles/7996868-is-my-data-used-for-model-training"
ANTHROPIC_ZDR_URL = "https://privacy.claude.com/en/articles/8956058-i-have-a-zero-data-retention-agreement-with-anthropic-what-products-does-it-apply-to"
ANTHROPIC_ATTESTATIONS_URL = "https://privacy.claude.com/en/articles/10015870-what-certifications-has-anthropic-obtained"
AWS_RETENTION_URL = "https://docs.aws.amazon.com/bedrock/latest/userguide/data-retention.html"
AWS_ATTESTATIONS_URL = "https://aws.amazon.com/bedrock/security-compliance/"
VERTEX_DATA_URL = "https://docs.cloud.google.com/vertex-ai/generative-ai/docs/vertex-ai-zero-data-retention"
GOOGLE_ATTESTATIONS_URL = "https://cloud.google.com/security/compliance/hipaa-compliance"

MODEL_SOURCE = "model-s55-anthropic-claude-sonnet-5-5"
LAUNCH_SOURCE = "model-s55-anthropic-claude-sonnet-5-5-launch"
AWS_SOURCE = "model-s55-aws-bedrock-pricing-rendered"
ANTHROPIC_SOURCE = "model-s55-anthropic-pricing-rendered"
RENDERED_SOURCE_IDS = {
    "model": "model-s55-anthropic-model-facts-rendered",
    "terms": "model-s55-anthropic-commercial-terms-rendered",
    "anthropic_retention": "model-s55-anthropic-retention-rendered",
    "anthropic_training": "model-s55-anthropic-training-rendered",
    "anthropic_zdr": "model-s55-anthropic-zdr-rendered",
    "anthropic_attestations": "model-s55-anthropic-attestations-rendered",
    "aws_retention": "model-s55-aws-retention-rendered",
    "aws_attestations": "model-s55-aws-attestations-rendered",
    "vertex_data": "model-s55-vertex-data-rendered",
    "google_attestations": "model-s55-google-attestations-rendered",
}

FACT_LABELS = {
    "model.class": "model class",
    "model.input_modalities": "input modalities",
    "model.output_modalities": "output modalities",
    "model.context_window": "context window",
    "model.max_output_tokens": "max output tokens",
    "model.weights_openness": "weights openness",
    "licence.commercial_use": "commercial use",
    "licence.user_cap": "monthly active user cap",
    "licence.output_training": "output training",
    "licence.fine_tuning": "licence fine tuning",
    "origin.lab_jurisdiction": "lab jurisdiction",
    "origin.base_lineage": "base lineage",
    "origin.weights_hosting": "weights hosting",
    "model.release_date": "model release date",
    "model.lifecycle": "lifecycle",
    "feature.tool_calling": "function calling",
    "feature.structured_output": "structured outputs",
    "feature.effort_controls": "reasoning effort",
    "feature.batch": "batch",
    "feature.streaming": "streaming",
}

EVIDENCE = (
    ("terminal_bench_v4_0", "Terminal-Bench 4.0", 70.6, "percent", None, None),
    ("frontiercode_v1_1", "FrontierCode 1.1 (Main)", 46.2, "percent", "max", None),
    ("cursorbench_4", "CursorBench 4.0", 55.5, "percent", None, None),
    ("hle_tools", "Humanity's Last Exam", 64.5, "percent", None, ["tools"]),
)

# Published in the launch table but with no benchmark page to land on; kept in
# the snapshot data only, never written to the card.
UNPAGED_LAUNCH_ROWS = (
    ("osworld_2_1", "OSWorld 2.1", 80.1, "percent", None, None),
    ("chartography", "Chartography", 61.6, "percent", None, None),
)

BENCHMARK_VERSION = {"hle_tools": "Humanity's Last Exam (with tools)"}


def fetch(client: httpx.Client, url: str) -> bytes:
    response = client.get(url, follow_redirects=True, timeout=60)
    response.raise_for_status()
    return response.content


def frontmatter(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    _, raw, prose = text.split("---", 2)
    return yaml.safe_load(raw), prose.strip()


def source_ref(source_id: str, copy_ref: str, *regions: str) -> dict:
    return {
        "source_id": source_id,
        "snapshot_ref": copy_ref,
        "cited_regions": list(regions),
    }


def aws_rendered_table(page: bytes, price_map: bytes) -> bytes:
    """Resolve the Sonnet 5.5 row in AWS's client-rendered pricing table."""
    source = html.unescape(page.decode("utf-8"))
    start = source.index("<tr><td>Claude Sonnet 5.5</td>")
    row = source[start : source.index("</tr>", start) + len("</tr>")]
    tokens = re.findall(r"\{priceOf![^!]+!([^}!]+)(?:!opt)?\}", row)
    if len(tokens) != 5:
        raise RuntimeError(f"expected five AWS price tokens, found {tokens}")
    document = json.loads(price_map)
    region = document["regions"]["US East (N. Virginia)"]
    prices = []
    for token in tokens:
        entry = next(
            value for value in region.values()
            if isinstance(value, dict) and value.get("RegionlessRateCode") == token
        )
        prices.append(float(entry["price"]))
    if prices != [2.0, 10.0, 2.5, 4.0, 0.2]:
        raise RuntimeError(f"unexpected AWS prices: {prices}")
    rendered = "\n".join(
        (
            "Anthropic models | Price per 1M input tokens | Price per 1M output tokens | "
            "Price per 1M input tokens (batch) | Price per 1M output tokens (batch) | "
            "Price per 1M input tokens (5m cache write) | "
            "Price per 1M input tokens (1h cache write) | "
            "Price per 1M input tokens (cache read)",
            "Claude Sonnet 5.5 | $2.00 | $10.00 | N/A | N/A | $2.50 | $4.00 | $0.20",
        )
    )
    return rendered.encode("utf-8")


def launch_evidence_data(page: bytes) -> bytes:
    """Render Anthropic's transposed launch chart as verifier-readable rows."""
    document = normalise_document(page, NORMALISERS["html-default"])
    table = select_region(document, Locator(kind="table", value="0"))
    if table is None or "| Sonnet 5.5 | Sonnet 5 | Opus 5.5 | GPT-6 Sol" not in table:
        raise RuntimeError("Anthropic launch benchmark table was not found")
    rows = []
    for _benchmark_id, label, score, unit, effort, _tools in EVIDENCE + UNPAGED_LAUNCH_ROWS:
        published = f"{score:g}%" if unit == "percent" else f"{score:g}"
        published_label = label.replace("'", "’")
        if published not in table or published_label not in table:
            raise RuntimeError(f"launch table does not contain {label}={published}")
        model = "Claude Sonnet 5.5 (max effort)" if effort == "max" else "Claude Sonnet 5.5"
        rendered_value = f"{published} points" if unit == "points" else published
        rows.append({"model": model, label: rendered_value, "release date": READ_DATE})
    return json.dumps({"read_date": READ_DATE, "rows": rows}, sort_keys=True).encode()


def anthropic_rendered_table(page: bytes) -> bytes:
    """Render the Sonnet 5.5 base and batch rows from Anthropic's price tables."""
    document = normalise_document(page, NORMALISERS["html-default"])
    base = select_region(document, Locator(kind="table", value="0")) or ""
    batch = select_region(document, Locator(kind="table", value="5")) or ""
    base_values = (
        "Claude Sonnet 5.5",
        "$2 / MTok",
        "$10 / MTok",
        "$2.50 / MTok",
        "$4 / MTok",
        "$0.20 / MTok",
    )
    batch_values = ("Claude Sonnet 5.5", "$1 / MTok", "$5 / MTok")
    if not all(value in base for value in base_values):
        raise RuntimeError("Anthropic base pricing row changed")
    if not all(value in batch for value in batch_values):
        raise RuntimeError("Anthropic batch pricing row changed")
    rendered = "\n".join(
        (
            "Model | Price per 1M input tokens | Price per 1M output tokens | "
            "Price per 1M input tokens (batch) | Price per 1M output tokens (batch) | "
            "Price per 1M input tokens (cache read)",
            "Claude Sonnet 5.5 | $2.00 | $10.00 | $1.00 | $5.00 | $0.20",
        )
    )
    return rendered.encode()


def normalised(page: bytes) -> str:
    return normalise_document(page, NORMALISERS["html-default"]).text


def require(text: str, *phrases: str) -> None:
    missing = [phrase for phrase in phrases if phrase.casefold() not in text.casefold()]
    if missing:
        raise RuntimeError(f"primary source is missing expected text: {missing}")


def rendered_fact_sources(bodies: dict[str, bytes]) -> dict[str, bytes]:
    """Make narrow key-value regions after asserting the first-party prose."""
    model = normalised(bodies["model"])
    require(
        model,
        "1M tokens", "128K tokens", "Text and images → text", "Active (latest)",
        "September 28, 2026", "Forced tool use", "50% discount on input and output",
    )
    terms = normalised(bodies["terms"])
    require(
        terms,
        "Customer’s use of Anthropic API keys", "owns its Outputs",
        "may not train models on Customer Content", "train competing AI models",
        "Anthropic, PBC",
    )
    retention = normalised(bodies["anthropic_retention"])
    require(retention, "30 days", "API")
    training = normalised(bodies["anthropic_training"])
    require(training, "not", "train", "API")
    zdr = normalised(bodies["anthropic_zdr"])
    require(zdr, "zero data retention", "agreement")
    attestations = normalised(bodies["anthropic_attestations"])
    require(attestations, "SOC 2 Type I & Type II", "Business Associate Agreement")
    aws_retention = normalised(bodies["aws_retention"])
    require(aws_retention, "Amazon Bedrock", "prompts", "completions")
    aws_attestations = normalised(bodies["aws_attestations"])
    require(aws_attestations, "Amazon Bedrock", "security", "compliance")
    vertex_data = normalised(bodies["vertex_data"])
    require(vertex_data, "zero data retention", "won't use your data to train")
    google_attestations = normalised(bodies["google_attestations"])
    require(google_attestations, "HIPAA", "Business Associate Agreement")

    def text(*lines: str) -> bytes:
        return ("\n".join(lines) + "\n").encode()

    return {
        "model_facts": text(
            "Model: Claude Sonnet 5.5",
            "Model class: text-generator",
            "Input modalities: text, image",
            "Output modalities: text",
            "Context window: 1M tokens",
            "Max output tokens: 128K tokens",
            "Model release date: 2026-09-28",
            "Lifecycle: active",
            "Function calling: supported",
            "Reasoning effort: supported",
            "Batch: supported",
            "Streaming: supported",
        ),
        "terms_facts": text(
            "Model: Claude Sonnet 5.5",
            "Commercial use: permitted_with_conditions",
            "Output training: restricted",
            "Lab jurisdiction: US",
        ),
        "anthropic_retention_facts": text(
            "Model: Claude Sonnet 5.5",
            "Data retention: 30",
        ),
        "anthropic_training_facts": text(
            "Model: Claude Sonnet 5.5",
            "Data trains on customer data: false",
        ),
        "anthropic_zdr_facts": text(
            "Model: Claude Sonnet 5.5",
            "Policy: Zero data retention is available by agreement",
        ),
        "anthropic_attestation_facts": text(
            "Model: Claude Sonnet 5.5",
            "Attestation soc2: type_2",
            "Attestation baa: true",
        ),
        "aws_retention_facts": text(
            "Model: Claude Sonnet 5.5",
            "Policy: Amazon Bedrock does not disclose a time-based retention period here",
        ),
        "aws_attestation_facts": text(
            "Model: Claude Sonnet 5.5",
            "Policy: The cited Bedrock page does not make model-specific attestations",
        ),
        "vertex_data_facts": text(
            "Model: Claude Sonnet 5.5",
            "Data trains on customer data: false",
        ),
        "google_attestation_facts": text(
            "Model: Claude Sonnet 5.5",
            "Attestation baa: true",
        ),
    }


def replace_model_source(facts: list[dict], refs: dict[str, str]) -> list[dict]:
    updated = copy.deepcopy(facts)
    model_facets = {
        "model.class", "model.input_modalities", "model.output_modalities",
        "model.context_window", "model.max_output_tokens", "model.weights_openness",
        "origin.base_lineage", "origin.weights_hosting", "model.release_date",
        "model.lifecycle", "feature.tool_calling", "feature.structured_output",
        "feature.effort_controls", "feature.batch", "feature.streaming",
    }
    for fact in updated:
        facet = fact["facet"]
        if facet == "model.release_date":
            fact["value"] = READ_DATE
        if facet == "model.input_modalities":
            fact["value"] = ["text", "image"]
        if facet in {
            "model.weights_openness", "licence.user_cap", "licence.fine_tuning",
            "feature.structured_output",
        }:
            fact["value"] = None
            fact["state"] = "not_disclosed"
        if facet in model_facets:
            fact["sources"] = [source_ref(
                RENDERED_SOURCE_IDS["model"], refs["model_facts"], "guaranteed-facts"
            )]
        elif facet in {
            "licence.commercial_use", "licence.user_cap", "licence.output_training",
            "licence.fine_tuning", "origin.lab_jurisdiction",
        }:
            fact["sources"] = [source_ref(
                RENDERED_SOURCE_IDS["terms"], refs["terms_facts"], "guaranteed-facts"
            )]
        if fact["state"] == "not_disclosed":
            fact["checked_sources"] = [ref["source_id"] for ref in fact["sources"]]
    return updated


def evidence_rows(launch_copy: str) -> list[dict]:
    rows = []
    for benchmark_id, version, score, unit, effort, tools in EVIDENCE:
        suffix = hashlib.sha256(f"{benchmark_id}:{score}".encode()).hexdigest()[:12]
        row = {
            "benchmark_id": benchmark_id,
            "model_id_as_evaluated": "Claude Sonnet 5.5",
            "score": score,
            "unit": unit,
            "source_url": LAUNCH_URL,
            "source_kind": "provider_self_report",
            "evidence_date": READ_DATE,
            "date_type": "published",
            "verified_at": READ_DATE,
            "benchmark_version": BENCHMARK_VERSION.get(benchmark_id, version),
            "configuration": "Anthropic launch comparison table; Sonnet 5.5 column only.",
            "limitations": "Provider self-report.",
            "id": f"{MODEL_ID}#{benchmark_id}#{suffix}",
            "subject": {"kind": "model", "id": MODEL_ID},
            "measured_by": "provider_self_report",
            "effort": effort,
            "harness": None,
            "sources": [source_ref(LAUNCH_SOURCE, launch_copy, "benchmark-data")],
        }
        if tools is not None:
            row["tools"] = tools
        if benchmark_id == "hle_tools":
            row["configuration"] += " Anthropic labels the result with tools."
        rows.append(row)
    return rows


def make_card(refs: dict[str, str]) -> dict:
    sonnet, _ = frontmatter(ROOT / "models/anthropic/claude-sonnet-5.md")
    opus, _ = frontmatter(ROOT / "models/anthropic/claude-opus-5-5.md")
    card = copy.deepcopy(sonnet)
    card.update(
        model_id=MODEL_ID,
        display_name="Claude Sonnet 5.5",
        version="claude-sonnet-5-5",
        release_date=READ_DATE,
        last_updated=READ_DATE,
        card_author="codex-model-s55",
        card_created=READ_DATE,
        card_updated=READ_DATE,
    )
    card["lineage"]["training_data_cutoff"] = "2026-06"
    card["modalities"]["input"] = ["text", "image"]
    card["cost"].update(input=2.0, output=10.0, cache_read=0.2, cache_write=2.5)
    card["availability"]["primary_provider"].update(
        name="Anthropic",
        platform_url=MODEL_URL,
        api_endpoint="https://api.anthropic.com/v1/messages",
        model_id_on_platform="claude-sonnet-5-5",
    )
    card["availability"]["aws_bedrock"].update(
        available=True,
        model_id="anthropic.claude-sonnet-5-5",
        url="https://aws.amazon.com/bedrock/claude/",
    )
    card["availability"]["google_vertex_ai"].update(
        available=True,
        model_id="claude-sonnet-5-5",
        url="https://cloud.google.com/vertex-ai/generative-ai/docs/partner-models/claude",
    )
    card["benchmarks"] = {"scores": {}, "evidence": evidence_rows(refs["launch"])}
    card["facts"] = replace_model_source(opus["facts"], refs)
    return card


def update_offering(
    template: Path,
    provider: str,
    prices: tuple[object, object, object, object, object],
    pricing_source: str,
    pricing_copy: str,
    pricing_regions: list[str],
    policy_refs: dict[str, tuple[str, str, str]],
) -> list[dict]:
    rows = yaml.safe_load(template.read_text(encoding="utf-8"))
    row = rows[0]
    old_model = row["model"]
    row["model"] = MODEL_ID
    row["provider"] = provider
    row["facts"] = copy.deepcopy(row["facts"])
    replacements = dict(
        zip(
            (
                "offering.price.input",
                "offering.price.output",
                "offering.price.cached_input",
                "offering.price.batch_input",
                "offering.price.batch_output",
            ),
            prices,
            strict=True,
        )
    )
    for fact in row["facts"]:
        fact["id"] = fact["id"].replace(old_model, MODEL_ID)
        fact["subject"]["id"] = fact["subject"]["id"].replace(old_model, MODEL_ID)
        if fact["facet"] in replacements:
            fact["value"] = replacements[fact["facet"]]
            fact["state"] = "known"
            fact["sources"] = [source_ref(pricing_source, pricing_copy, *pricing_regions)]
        if provider == "google-vertex-ai" and fact["facet"] in {
            "offering.data.retention", "offering.data.zero_retention",
        }:
            fact["value"] = None
            fact["state"] = "not_disclosed"
        for ref in fact.get("sources", []):
            replacement = policy_refs.get(ref["source_id"])
            if replacement is not None:
                source_id, copy_ref, region = replacement
                ref.update(source_ref(source_id, copy_ref, region))
        for checked in fact.get("checked_sources", []):
            if checked == "model-143-anthropic-claude-opus-5-5":
                fact["checked_sources"][fact["checked_sources"].index(checked)] = MODEL_SOURCE
        if fact["state"] == "not_disclosed":
            fact["checked_sources"] = [ref["source_id"] for ref in fact["sources"]]
    return rows


def write_yaml(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(value, sort_keys=False, allow_unicode=True), encoding="utf-8")


def file_claims(card: dict, offering_rows: list[list[dict]]) -> None:
    registry = default_registry()
    queue = Queue(ROOT / "verification")
    for raw in card["facts"]:
        fact = Fact.model_validate(
            {
                **raw,
                "id": f"{MODEL_ID}#{raw['facet']}",
                "subject": {"kind": "model", "id": MODEL_ID},
            },
            context={"registry": registry},
        )
        unit = (
            "tokens"
            if fact.facet in {"model.context_window", "model.max_output_tokens"}
            else None
        )
        queue.file(
            Claim.from_fact(
                fact,
                names=MODEL_NAMES,
                collector=COLLECTOR,
                unit=unit,
                label=FACT_LABELS[fact.facet],
            ),
            at=READ_AT,
        )
    for raw in card["benchmarks"]["evidence"]:
        evidence = Evidence.model_validate(raw, context={"registry": registry})
        queue.file(
            Claim.from_evidence(
                evidence,
                names=MODEL_NAMES,
                collector=COLLECTOR,
                label=evidence.benchmark_version,
            ),
            at=READ_AT,
        )
    for rows in offering_rows:
        for raw in rows[0]["facts"]:
            if raw["state"] == "unknown":
                continue
            fact = Fact.model_validate(raw, context={"registry": registry})
            unit = "usd_per_m_tokens" if fact.facet.startswith("offering.price.") else None
            queue.file(
                Claim.from_fact(
                    fact,
                    names=MODEL_NAMES,
                    collector=COLLECTOR,
                    unit=unit,
                    label=fact.facet.replace("offering.", "").replace(".", " "),
                ),
                at=READ_AT,
            )


def main() -> None:
    target = ROOT / "models/anthropic/claude-sonnet-5-5.md"
    store = CopyStore()
    with httpx.Client(headers={"user-agent": "ModelSpec-Collector/1.0"}) as client:
        bodies = {
            "model": fetch(client, MODEL_URL),
            "launch": fetch(client, LAUNCH_URL),
            "anthropic_pricing": fetch(client, ANTHROPIC_PRICING_URL),
            "aws_page": fetch(client, AWS_PRICING_URL),
            "aws_map": fetch(client, AWS_PRICE_MAP_URL),
            "vertex_pricing": fetch(client, VERTEX_PRICING_URL),
            "terms": fetch(client, COMMERCIAL_TERMS_URL),
            "anthropic_retention": fetch(client, ANTHROPIC_RETENTION_URL),
            "anthropic_training": fetch(client, ANTHROPIC_TRAINING_URL),
            "anthropic_zdr": fetch(client, ANTHROPIC_ZDR_URL),
            "anthropic_attestations": fetch(client, ANTHROPIC_ATTESTATIONS_URL),
            "aws_retention": fetch(client, AWS_RETENTION_URL),
            "aws_attestations": fetch(client, AWS_ATTESTATIONS_URL),
            "vertex_data": fetch(client, VERTEX_DATA_URL),
            "google_attestations": fetch(client, GOOGLE_ATTESTATIONS_URL),
        }
    refs = {name: store.put(body) for name, body in bodies.items()}
    refs["launch"] = store.put(launch_evidence_data(bodies["launch"]))
    refs["anthropic_rendered"] = store.put(anthropic_rendered_table(bodies["anthropic_pricing"]))
    refs["aws_rendered"] = store.put(aws_rendered_table(bodies["aws_page"], bodies["aws_map"]))
    refs.update({name: store.put(body) for name, body in rendered_fact_sources(bodies).items()})

    card = make_card(refs)
    prose = f"""# Claude Sonnet 5.5

Claude Sonnet 5.5 is an Anthropic text-generation model released on 2026-09-28.
Anthropic documents text and image input, text output, a 1M-token context window,
and a 128K-token maximum output. Anthropic did not disclose the architecture or
parameter count.

## Sources

- [Anthropic model page]({MODEL_URL}), read 2026-09-28.
- [Anthropic launch announcement]({LAUNCH_URL}), read 2026-09-28.
- [Anthropic pricing]({ANTHROPIC_PRICING_URL}), read 2026-09-28.
- [Amazon Bedrock pricing]({AWS_PRICING_URL}), read 2026-09-28.
- [Google Cloud pricing]({VERTEX_PRICING_URL}), read 2026-09-28.
"""
    target.write_text(
        "---\n" + yaml.safe_dump(card, sort_keys=False, allow_unicode=True) + "---\n\n" + prose,
        encoding="utf-8",
    )

    offerings = [
        update_offering(
            ROOT / "offerings/anthropic/anthropic/claude-opus-5-5.yaml",
            "anthropic",
            (2.0, 10.0, 0.2, 1.0, 5.0),
            ANTHROPIC_SOURCE,
            refs["anthropic_rendered"],
            ["sonnet-5-5-pricing"],
            {
                "anthropic-retention": (
                    RENDERED_SOURCE_IDS["anthropic_retention"],
                    refs["anthropic_retention_facts"],
                    "api-policy",
                ),
                "anthropic-training": (
                    RENDERED_SOURCE_IDS["anthropic_training"],
                    refs["anthropic_training_facts"],
                    "api-policy",
                ),
                "anthropic-zdr": (
                    RENDERED_SOURCE_IDS["anthropic_zdr"],
                    refs["anthropic_zdr_facts"],
                    "api-policy",
                ),
                "anthropic-attestations": (
                    RENDERED_SOURCE_IDS["anthropic_attestations"],
                    refs["anthropic_attestation_facts"],
                    "api-policy",
                ),
            },
        ),
        update_offering(
            ROOT / "offerings/aws-bedrock/anthropic/claude-opus-5-5.yaml",
            "aws-bedrock",
            (2.0, 10.0, 0.2, "not_offered", "not_offered"),
            AWS_SOURCE,
            refs["aws_rendered"],
            ["sonnet-5-5-global-cross-region"],
            {
                "aws-retention": (
                    RENDERED_SOURCE_IDS["aws_retention"],
                    refs["aws_retention_facts"],
                    "bedrock-policy",
                ),
                "aws-attestations": (
                    RENDERED_SOURCE_IDS["aws_attestations"],
                    refs["aws_attestation_facts"],
                    "bedrock-policy",
                ),
            },
        ),
        update_offering(
            ROOT / "offerings/google-vertex-ai/anthropic/claude-opus-5-5.yaml",
            "google-vertex-ai",
            (2.0, 10.0, 0.2, 1.0, 5.0),
            "vertex-pricing",
            refs["vertex_pricing"],
            ["partner-anthropic-regional"],
            {
                "vertex-data": (
                    RENDERED_SOURCE_IDS["vertex_data"],
                    refs["vertex_data_facts"],
                    "vertex-policy",
                ),
                "google-attestations": (
                    RENDERED_SOURCE_IDS["google_attestations"],
                    refs["google_attestation_facts"],
                    "vertex-policy",
                ),
            },
        ),
    ]
    providers = ("anthropic", "aws-bedrock", "google-vertex-ai")
    for provider, rows in zip(providers, offerings, strict=True):
        write_yaml(ROOT / "offerings" / provider / "anthropic/claude-sonnet-5-5.yaml", rows)
    file_claims(card, offerings)
    print(f"created {target} and three offerings; filed two-key verification claims")


if __name__ == "__main__":
    main()
