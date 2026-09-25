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
    "anthropic": ("claude.com",),
    "aws-bedrock": ("aws.amazon.com",),
    "google-gemini-api": ("google.dev", "google.com"),
    "google-vertex-ai": ("google.com",),
    "openai": ("openai.com",),
    "azure-ai-foundry": ("microsoft.com",),
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
