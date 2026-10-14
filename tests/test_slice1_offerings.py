"""MODEL-144's slice-1 offering data invariants."""

from pathlib import Path
from urllib.parse import urlparse

import pytest
import yaml

from decision.model import load_offerings
from decision.sources import load_sources
from tests.snapshot_records import fact, offering


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
    "moonshot": ("kimi.ai",),
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
        assert GUARANTEED <= set(facets)
        assert all(facets.count(facet) == 1 for facet in GUARANTEED)


def test_governance_facts_only_use_the_serving_providers_own_documents() -> None:
    sources = load_sources(ROOT / "registry/sources.yaml")
    for offering in _offerings():
        assert offering.provider in GOVERNANCE_DOMAINS, (
            f"{offering.provider}: add the provider's own document domains to GOVERNANCE_DOMAINS"
        )
        suffixes = GOVERNANCE_DOMAINS[offering.provider]
        for fact in offering.facts:
            if not fact.facet.startswith(("offering.data.", "offering.attestation.")):
                continue
            for ref in fact.sources:
                host = urlparse(str(sources[ref.source_id].url)).hostname or ""
                assert any(host == suffix or host.endswith("." + suffix)
                           for suffix in suffixes)


def _write_governance_documents(root, provider, host):
    path = root / "offerings" / provider / "test" / "model.yaml"
    path.parent.mkdir(parents=True)
    oid = f"{provider}/test/model/global/standard"
    path.write_text(yaml.safe_dump([
        offering("test/model", provider, facts=[
            fact("offering", oid, "offering.data.trains_on_customer_data", False)
        ])
    ]))
    registry = root / "registry"
    registry.mkdir()
    (registry / "sources.yaml").write_text(yaml.safe_dump({
        "schema_version": 1,
        "sources": [{
            "id": "src-lab-docs", "url": f"https://{host}/privacy",
            "normaliser": "text-default",
            "cited_regions": [{"id": "r1", "locator": {"kind": "page"}}],
        }],
    }))


@pytest.mark.parametrize("host", ["kimi.ai", "platform.kimi.ai"])
def test_moonshot_governance_accepts_kimi_documents(tmp_path, monkeypatch, host):
    _write_governance_documents(tmp_path, "moonshot", host)
    monkeypatch.setattr(f"{__name__}.ROOT", tmp_path)
    test_governance_facts_only_use_the_serving_providers_own_documents()


@pytest.mark.parametrize("host", [
    "not-kimi.ai", "platform.kimi.ai.example.test", "deepseek.com",
])
def test_moonshot_governance_rejects_other_domains(tmp_path, monkeypatch, host):
    _write_governance_documents(tmp_path, "moonshot", host)
    monkeypatch.setattr(f"{__name__}.ROOT", tmp_path)
    with pytest.raises(AssertionError):
        test_governance_facts_only_use_the_serving_providers_own_documents()


def test_unknown_governance_provider_has_a_clear_failure(tmp_path, monkeypatch):
    _write_governance_documents(tmp_path, "sambanova", "example.test")
    monkeypatch.setattr(f"{__name__}.ROOT", tmp_path)
    with pytest.raises(AssertionError, match="sambanova.*GOVERNANCE_DOMAINS"):
        test_governance_facts_only_use_the_serving_providers_own_documents()


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
