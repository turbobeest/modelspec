"""The AEO prompt inventory's schema and loader (MODEL-254)."""

from __future__ import annotations

import copy
from pathlib import Path

import pytest
import yaml

from scripts.aeo import inventory
from scripts.aeo.inventory import Vocabulary, coverage_errors, validate

VOCAB = Vocabulary(
    facets=frozenset({"model.fits_hardware", "licence.commercial_use", "offering.cost_per_task"}),
    domains=frozenset({"software_engineering", "vision_documents"}),
    templates=frozenset({"budget-coding"}),
)


def _prompt(**overrides: object) -> dict[str, object]:
    prompt: dict[str, object] = {
        "id": "coding-24gb",
        "text": "best coding model I can run on a 24GB GPU",
        "cluster": "constrained",
        "icp": "builder",
        "intent": "discover",
        "locale": "en-US",
        "engines": ["openai", "perplexity"],
        "expected_entities": ["modelspec"],
        "success": "cited",
        "source": "jamie",
        "constraints": ["software_engineering", "model.fits_hardware"],
    }
    prompt.update(overrides)
    return prompt


def _doc(*prompts: dict[str, object]) -> dict[str, object]:
    return {"schema_version": 1, "prompts": list(prompts) or [_prompt()]}


def test_a_valid_inventory_has_no_errors() -> None:
    assert validate(_doc(), VOCAB) == []


@pytest.mark.parametrize("field", ["success", "cluster"])
def test_a_prompt_missing_success_or_cluster_is_rejected(field: str) -> None:
    prompt = _prompt()
    del prompt[field]
    assert validate(_doc(prompt), VOCAB) == [f"prompts/0: '{field}' is a required property"]


def test_a_keyword_tool_is_not_a_source() -> None:
    errors = validate(_doc(_prompt(source="keyword-tool")), VOCAB)
    assert len(errors) == 1 and errors[0].startswith("prompts/0/source: 'keyword-tool' is not one of")


def test_a_constrained_prompt_must_name_a_constraint() -> None:
    assert validate(_doc(_prompt(constraints=[])), VOCAB) == [
        "coding-24gb: a constrained prompt must name at least one constraint"]


def test_a_constraint_the_registry_does_not_know_is_rejected() -> None:
    assert validate(_doc(_prompt(constraints=["model.vibes"])), VOCAB) == [
        "coding-24gb: constraint 'model.vibes' is not a registry facet or domain"]


def test_an_unknown_template_is_rejected() -> None:
    assert validate(_doc(_prompt(template="coding-cheap")), VOCAB) == [
        "coding-24gb: template 'coding-cheap' is not in registry/templates.yaml"]


def test_disambiguated_belongs_only_to_the_disambiguation_cluster() -> None:
    wrong_cluster = _prompt(success="disambiguated")
    wrong_success = _prompt(id="vs-openai", cluster="disambiguation", success="cited", constraints=[])
    message = "success 'disambiguated' belongs to the disambiguation cluster, and only there"
    assert validate(_doc(wrong_cluster, wrong_success), VOCAB) == [
        f"coding-24gb: {message}", f"vs-openai: {message}"]


def test_duplicate_ids_are_rejected() -> None:
    assert validate(_doc(_prompt(), _prompt()), VOCAB) == ["coding-24gb: id is used 2 times"]


def test_coverage_needs_25_to_40_prompts_and_4_per_cluster() -> None:
    prompts = [_prompt(id=f"c{i}") for i in range(10)] + [
        _prompt(id=f"d{i}", cluster="disambiguation", success="disambiguated") for i in range(4)]
    assert coverage_errors(prompts) == [
        "14 prompts; need 25 to 40",
        "cluster 'category' has 0 prompts; need at least 4",
        "cluster 'agent' has 0 prompts; need at least 4",
    ]
    balanced = [_prompt(id=f"{c}{i}", cluster=c) for c in inventory.CLUSTERS for i in range(7)]
    assert coverage_errors(balanced) == []


def test_real_registry_ids_are_accepted() -> None:
    """The vocabulary is read from the registry, not restated here."""
    real = Vocabulary.from_registry()
    assert {"software_engineering", "vision_documents"} <= real.domains
    assert {"model.fits_hardware", "licence.commercial_use", "offering.cost_per_task"} <= real.facets
    assert "budget-coding" in real.templates
    assert validate(_doc(_prompt(template="budget-coding")), real) == []


def test_the_command_reports_counts_and_fails_on_thin_coverage(tmp_path: Path, capsys) -> None:
    path = tmp_path / "prompts.yaml"
    path.write_text(yaml.safe_dump(_doc()), encoding="utf-8")
    assert inventory.main([str(path)]) == 0
    assert capsys.readouterr().out == (
        "1 prompts: category 0, constrained 1, agent 0, disambiguation 0\nsources: jamie 1\n")
    assert inventory.main([str(path), "--coverage"]) == 1
    assert "coverage: 1 prompts; need 25 to 40" in capsys.readouterr().err

    bad = copy.deepcopy(_doc())
    del bad["prompts"][0]["success"]
    path.write_text(yaml.safe_dump(bad), encoding="utf-8")
    assert inventory.main([str(path)]) == 1
    assert "prompts/0: 'success' is a required property" in capsys.readouterr().err
