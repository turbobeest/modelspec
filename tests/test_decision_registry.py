"""MODEL-133: the facet, provider, harness and domain registries.

Design §4.1 and §8 (`docs/design/decision-engine.md` on the design branch):
facets, providers, harnesses and domains are open, registered sets. Adding one
is a registry entry, never an engine change (ADR 0002), and an unknown ID fails
loudly rather than being silently ignored (§6.1).
"""

from __future__ import annotations

import re
import shutil
from functools import cache
from pathlib import Path

import pytest
import yaml

from decision import registry as reg
from decision.registry import RegistryError, UnknownIdError
from pipeline.load import load_benchmarks
from schema.benchmark import BenchmarkCard

ROOT = Path(__file__).resolve().parent.parent

#: Every guaranteed facet in design §8, by the ID this registry gives it. The
#: test fails if one is missing or has been downgraded to best effort.
GUARANTEED = {
    # Model: class and output; modalities; context; maximum output
    "model.class", "model.input_modalities", "model.output_modalities",
    "model.context_window", "model.max_output_tokens",
    # Model: open or closed weights (G); parameters and architecture are B
    "model.weights_openness",
    # Model: licence rights
    "licence.commercial_use", "licence.user_cap", "licence.output_training",
    "licence.fine_tuning",
    # Model: origin, each defined separately
    "origin.lab_jurisdiction", "origin.base_lineage", "origin.weights_hosting",
    # Model: release and lifecycle (knowledge cutoff and deprecation are B)
    "model.release_date", "model.lifecycle",
    # Model: features
    "feature.tool_calling", "feature.structured_output",
    "feature.effort_controls", "feature.batch", "feature.streaming",
    # Offering: provider, region, tier
    "offering.provider", "offering.region", "offering.tier",
    # Offering: price (input, output, cached, batch)
    "offering.price.input", "offering.price.output",
    "offering.price.cached_input", "offering.price.batch_input",
    "offering.price.batch_output",
    # Offering: data handling
    "offering.data.retention", "offering.data.trains_on_customer_data",
    "offering.data.zero_retention",
    # Offering: attestations SOC 2 and BAA availability
    "offering.attestation.soc2", "offering.attestation.baa",
    # Estimate: capability per domain, G for the premier set
    "estimate.capability",
}

BEST_EFFORT = {
    "model.parameters_total", "model.parameters_active", "model.architecture",
    "model.knowledge_cutoff", "model.deprecation_date", "model.languages",
    "model.fits_hardware", "offering.speed.time_to_first_token",
    "offering.speed.throughput", "offering.rate_limit.requests",
    "offering.rate_limit.tokens", "offering.sla_uptime",
    "offering.attestation.fedramp", "offering.attestation.iso_27001",
    "offering.fine_tuning", "offering.private_deployment",
    "offering.harness_compatibility", "evidence.benchmark", "evidence.outcome",
}

#: §8's launch domains plus the slice-1 domains this ticket tags.
DOMAINS = {
    "software_engineering", "engineering_stem", "maths", "reasoning", "legal",
    "medical", "finance", "writing", "marketing_seo", "agentic_tool_use",
    "vision_documents", "multilingual", "chat_preference", "retrieval",
}

HARNESSES = {"claude-code", "codex-cli", "aider", "openhands", "cursor-agent", "dpf-native"}


@pytest.fixture(scope="module")
def registry() -> reg.Registry:
    return reg.load()


# ── the shipped registries ─────────────────────────────────────────────────


def test_every_guaranteed_facet_in_section_8_is_registered_as_guaranteed(registry):
    ids = {f.id for f in registry.facets()}
    assert GUARANTEED <= ids, sorted(GUARANTEED - ids)
    assert {f.id for f in registry.facets() if f.tier == "guaranteed"} == GUARANTEED


def test_every_best_effort_facet_in_section_8_is_registered(registry):
    ids = {f.id for f in registry.facets() if f.tier == "best_effort"}
    assert BEST_EFFORT <= ids, sorted(BEST_EFFORT - ids)


def test_every_facet_has_an_exact_definition(registry):
    for f in registry.facets():
        # A sentence or more, not a label.
        assert len(f.definition.split()) >= 12, f.id


def test_every_numeric_facet_has_a_registered_unit(registry):
    units = {u.id for u in registry.units()}
    for f in registry.facets():
        if f.value_type.kind in ("number", "range"):
            assert f.unit in units, f.id


def test_price_speed_and_context_units_are_precise(registry):
    for i in ("input", "output", "cached_input", "batch_input", "batch_output"):
        assert registry.facet(f"offering.price.{i}").unit == "usd_per_1m_tokens"
    assert registry.facet("offering.speed.throughput").unit == "tokens_per_second"
    assert registry.facet("offering.speed.time_to_first_token").unit == "milliseconds"
    assert registry.facet("model.context_window").unit == "tokens"
    assert registry.facet("model.max_output_tokens").unit == "tokens"
    assert "1,000,000" in registry.unit("usd_per_1m_tokens").definition


def test_origin_is_three_separately_defined_facets(registry):
    origin = [f for f in registry.facets() if f.id.startswith("origin.")]
    assert {f.id for f in origin} >= {
        "origin.lab_jurisdiction", "origin.base_lineage", "origin.weights_hosting"}
    assert len({f.definition for f in origin}) == len(origin)
    assert all(f.risk == "governance" for f in origin)


def test_unknown_policy_follows_risk(registry):
    assert registry.facet("model.context_window").unknown_policy == "may_qualify"
    assert registry.facet("offering.data.trains_on_customer_data").unknown_policy == "not_satisfied"
    for f in registry.facets():
        expected = "may_qualify" if f.risk == "capability" else "not_satisfied"
        assert f.unknown_policy == expected, f.id


def test_licence_data_handling_and_attestations_are_governance(registry):
    for f in registry.facets():
        if f.id.startswith(("licence.", "origin.", "offering.data.", "offering.attestation.")):
            assert f.risk == "governance", f.id


def test_permitted_source_kinds_are_registered(registry):
    kinds = {k.id for k in registry.source_kinds()}
    for f in registry.facets():
        assert f.permitted_source_kinds, f.id
        assert set(f.permitted_source_kinds) <= kinds, f.id


def test_seeded_providers(registry):
    ids = {p.id for p in registry.providers()}
    assert {
        "openai", "anthropic", "google-gemini-api", "xai", "mistral", "deepseek",
        "aws-bedrock", "google-vertex-ai", "azure-ai-foundry", "groq",
        "together-ai", "fireworks-ai", "deepinfra", "cerebras", "sambanova",
        "nvidia-nim", "openrouter",
    } <= ids
    # App-only platforms are not providers of offerings.
    assert not ids & {"chatgpt", "claude-ai", "gemini-app", "cursor", "poe", "perplexity"}


def test_provider_facts_are_sourced_or_unknown(registry):
    for p in registry.providers():
        for fact in (p.jurisdiction, *p.attestations.values()):
            if fact.known:
                assert fact.source.startswith("https://"), p.id
                assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", fact.read), p.id


def test_offering_provider_facet_draws_on_the_provider_registry(registry):
    facet = registry.facet("offering.provider")
    assert facet.value_type.values_from == "registry:providers"
    assert "anthropic" in registry.allowed_values(facet)


def test_seeded_harnesses_and_canonical_ids(registry):
    assert HARNESSES <= {h.id for h in registry.harnesses()}
    for h in registry.harnesses():
        for v in h.versions:
            assert re.fullmatch(rf"{re.escape(h.id)}@\d+\.\d+", v), v
    assert "dpf-native@1.0" in registry.harness("dpf-native").versions


def test_harness_ids_resolve_or_are_unregistered(registry):
    assert registry.resolve_harness("dpf-native@1.0") == "dpf-native@1.0"
    # A patch version resolves to its registered major.minor.
    assert registry.resolve_harness("dpf-native@1.0.7") == "dpf-native@1.0"
    assert registry.resolve_harness("dpf-native@9.9") == reg.UNREGISTERED
    assert registry.resolve_harness("some-new-agent@1.0") == reg.UNREGISTERED
    assert registry.resolve_harness("free text, not an id") == reg.UNREGISTERED
    assert registry.resolve_harness("") == reg.UNREGISTERED


def test_launch_domains_are_registered(registry):
    assert DOMAINS <= {d.id for d in registry.domains()}
    assert registry.domain("marketing_seo").proxy_only is True


# ── unknown IDs fail loudly ────────────────────────────────────────────────


@pytest.mark.parametrize("accessor,bad", [
    ("facet", "model.contxt_window"),
    ("provider", "open-ai"),
    ("harness", "claude_code"),
    ("domain", "software-engineering"),
    ("unit", "usd"),
])
def test_unknown_ids_fail_loudly(registry, accessor, bad):
    with pytest.raises(UnknownIdError) as exc:
        getattr(registry, accessor)(bad)
    message = str(exc.value)
    assert bad in message and accessor in message
    assert isinstance(exc.value, KeyError)


def test_unknown_id_error_suggests_the_near_miss(registry):
    with pytest.raises(UnknownIdError, match="model.context_window"):
        registry.facet("model.contxt_window")


# ── validation ─────────────────────────────────────────────────────────────


def _copy(tmp_path: Path) -> Path:
    dest = tmp_path / "registry"
    shutil.copytree(ROOT / "registry", dest)
    return dest


def _edit(root: Path, name: str, fn) -> None:
    path = root / f"{name}.yaml"
    data = yaml.safe_load(path.read_text())
    fn(data)
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True))


def _load(root: Path) -> reg.Registry:
    return reg.load(root, repo_root=ROOT)


def _facet(**over):
    base = {
        "id": "model.example", "subject": "model",
        "value_type": {"kind": "boolean"},
        "definition": "True when the example property holds for the model, as documented by its lab.",
        "tier": "best_effort", "risk": "capability",
        "permitted_source_kinds": ["lab_documentation"],
    }
    base.update(over)
    return base


@pytest.mark.parametrize("entry,needle", [
    (_facet(subject="lab"), "subject"),
    (_facet(tier="core"), "tier"),
    (_facet(risk="safety"), "risk"),
    (_facet(value_type={"kind": "number"}), "unit"),
    (_facet(value_type={"kind": "number"}, unit="furlongs"), "furlongs"),
    (_facet(value_type={"kind": "enum"}), "values"),
    (_facet(value_type={"kind": "enum", "values_from": "registry:nowhere"}), "registry:nowhere"),
    (_facet(value_type={"kind": "colour"}), "kind"),
    (_facet(permitted_source_kinds=["a_blog"]), "a_blog"),
    (_facet(permitted_source_kinds=[]), "permitted_source_kinds"),
    (_facet(definition="Short."), "definition"),
    (_facet(id="Model Example"), "id"),
    (_facet(surprise=True), "surprise"),
    (_facet(id="model.context_window"), "duplicate"),
])
def test_invalid_facets_are_rejected(tmp_path, entry, needle):
    root = _copy(tmp_path)
    _edit(root, "facets", lambda d: d["facets"].append(entry))
    with pytest.raises(RegistryError, match=re.escape(needle)):
        _load(root)


def test_provider_attestation_must_be_sourced_or_unknown(tmp_path):
    root = _copy(tmp_path)

    def add(d):
        d["providers"].append({
            "id": "example-cloud", "name": "Example Cloud", "url": "https://example.com/",
            "kind": "inference", "jurisdiction": "unknown",
            "attestations": {"soc2": {"value": "type_2"}},
        })
    _edit(root, "providers", add)
    with pytest.raises(RegistryError, match="source"):
        _load(root)


def test_harness_version_must_be_canonical(tmp_path):
    root = _copy(tmp_path)

    def add(d):
        d["harnesses"].append({
            "id": "example-agent", "name": "Example agent", "url": "https://example.com/",
            "versions": [{"id": "example-agent@1.2.3", "source": "https://example.com/", "read": "2026-09-24"}],
        })
    _edit(root, "harnesses", add)
    with pytest.raises(RegistryError, match="major.minor"):
        _load(root)


# ── adding needs only a registry entry ─────────────────────────────────────


def test_adding_a_facet_provider_harness_and_domain_needs_only_registry_entries(tmp_path):
    root = _copy(tmp_path)
    _edit(root, "facets", lambda d: d["facets"].append(_facet(
        id="offering.example_latency", subject="offering",
        value_type={"kind": "number"}, unit="milliseconds")))
    _edit(root, "providers", lambda d: d["providers"].append({
        "id": "example-cloud", "name": "Example Cloud", "url": "https://example.com/",
        "kind": "cloud",
        "jurisdiction": {"value": "US", "entity": "Example Cloud, Inc.",
                         "shown_by": "address", "basis": "service_terms",
                         "source": "https://example.com/terms", "read": "2026-09-24"},
        "attestations": {"soc2": "unknown"},
    }))
    _edit(root, "harnesses", lambda d: d["harnesses"].append({
        "id": "example-agent", "name": "Example agent", "url": "https://example.com/",
        "versions": [{"id": "example-agent@3.1", "source": "https://example.com/", "read": "2026-09-24"}],
    }))
    _edit(root, "domains", lambda d: d["domains"].append({
        "id": "example_domain", "name": "Example",
        "definition": "Capability at an example task family, defined here only to prove the registry is open.",
    }))

    r = _load(root)
    assert r.facet("offering.example_latency").unknown_policy == "may_qualify"
    assert r.provider("example-cloud").jurisdiction.value == "US"
    assert "example-cloud" in r.allowed_values(r.facet("offering.provider"))
    assert r.resolve_harness("example-agent@3.1.4") == "example-agent@3.1"
    assert r.domain("example_domain").proxy_only is False


# ── domain tags on benchmark pages ─────────────────────────────────────────


def test_benchmark_domains_field_is_optional_and_additive():
    minimal = {"id": "example_bench", "name": "Example", "category": "coding"}
    assert BenchmarkCard.model_validate(minimal).domains == []
    card = BenchmarkCard.model_validate({
        **minimal, "domains": [{"id": "software_engineering", "directness": "direct"}]})
    assert card.domains[0].directness == "direct"


@pytest.mark.parametrize("domains,needle", [
    ([{"id": "maths", "directness": "indirect"}], "directness"),
    ([{"id": "maths", "directness": "direct"}, {"id": "maths", "directness": "proxy"}], "maths"),
    ([{"id": "maths"}], "directness"),
])
def test_benchmark_domains_field_rejects_bad_tags(domains, needle):
    with pytest.raises(ValueError, match=needle):
        BenchmarkCard.model_validate(
            {"id": "example_bench", "name": "Example", "category": "coding", "domains": domains})


@cache
def _tagged():
    return tuple(b for b in load_benchmarks() if "domains" in b.front)


def test_every_benchmark_domain_tag_is_registered(registry):
    tagged = 0
    for b in _tagged():
        for tag in BenchmarkCard.model_validate(b.front).domains:
            registry.domain(tag.id)  # raises on an unregistered domain
            tagged += 1
    assert tagged > 0


def test_proxy_only_domains_are_never_tagged_direct(registry):
    for b in _tagged():
        for tag in BenchmarkCard.model_validate(b.front).domains:
            if registry.domain(tag.id).proxy_only:
                assert tag.directness == "proxy", (b.benchmark_id, tag.id)


@pytest.mark.parametrize("benchmark,domain", [
    ("swe_bench_verified", "software_engineering"),
    ("aime_2025", "maths"),
    ("arena_elo_overall", "chat_preference"),
    ("mteb_v2_retrieval", "retrieval"),
    ("docvqa", "vision_documents"),
])
def test_slice_1_domains_have_direct_benchmarks(benchmark, domain):
    card = next(BenchmarkCard.model_validate(b.front) for b in _tagged() if b.benchmark_id == benchmark)
    assert {"id": domain, "directness": "direct"} in [t.model_dump() for t in card.domains]
