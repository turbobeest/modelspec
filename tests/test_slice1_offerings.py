"""MODEL-144's slice-1 offering data invariants."""

from pathlib import Path
from urllib.parse import urlparse

import yaml

from decision.model import load_offerings
from decision.sources import load_sources


ROOT = Path(__file__).parents[1]
GUARANTEED = {
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
}
GOVERNANCE_DOMAINS = {
    "alibaba-model-studio": ("alibabacloud.com",),
    "anthropic": ("claude.com",),
    "aws-bedrock": ("aws.amazon.com",),
    "deepseek": ("deepseek.com",),
    "google-gemini-api": ("google.dev", "google.com"),
    "google-vertex-ai": ("google.com",),
    "meta-model-api": ("meta.com",),
    "openai": ("openai.com",),
    "typesafe": ("typesafe.ai",),
    "xai": ("x.ai",),
    "azure-ai-foundry": ("microsoft.com",),
    "zai": ("z.ai",),
}


def _offerings():
    return [
        offering
        for path in sorted((ROOT / "offerings").glob("*/*/*.yaml"))
        for offering in load_offerings(path)
    ]


def test_slice1_offerings_have_every_guaranteed_facet_once() -> None:
    premier = {
        row["model_id"]
        for row in yaml.safe_load((ROOT / "premier/slice-1.yaml").read_text())["models"]
    }
    offerings = _offerings()
    assert offerings
    for offering in offerings:
        assert offering.model in premier
        facets = [fact.facet for fact in offering.facts]
        assert set(facets) == GUARANTEED
        assert len(facets) == len(GUARANTEED)


def test_governance_facts_only_use_the_serving_providers_own_documents() -> None:
    sources = load_sources(ROOT / "registry/sources.yaml")
    for offering in _offerings():
        suffixes = GOVERNANCE_DOMAINS[offering.provider]
        for fact in offering.facts:
            if not fact.facet.startswith(("offering.data.", "offering.attestation.")):
                continue
            for ref in fact.sources:
                host = urlparse(str(sources[ref.source_id].url)).hostname or ""
                assert any(host == suffix or host.endswith("." + suffix)
                           for suffix in suffixes)


def test_contract_only_zero_retention_is_not_filed_as_unconditional() -> None:
    contract_only_providers = {"anthropic", "openai"}
    for offering in _offerings():
        if offering.provider not in contract_only_providers:
            continue
        zero_retention = next(
            fact for fact in offering.facts
            if fact.facet == "offering.data.zero_retention"
        )
        assert zero_retention.state == "requires_contract"
        assert zero_retention.value is None


def test_client_rendered_cloud_sources_are_registered_as_rendered() -> None:
    sources = load_sources(ROOT / "registry/sources.yaml")
    for source_id in ("aws-pricing", "azure-pricing"):
        assert sources[source_id].fetch == "rendered"
