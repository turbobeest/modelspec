"""`ModelCard.to_yaml()` must produce what `ModelCard.from_yaml_string()` reads.

The on-disk card format is identity fields flat at the top level, every
other section nested, plain string enum values. A card built in Python and
written with `to_yaml()` has to come back as the same card.
"""

from __future__ import annotations

import yaml

from schema.card import (
    Architecture,
    Availability,
    Downselect,
    Identity,
    Licensing,
    Lineage,
    Modalities,
    ModelCard,
    PolicySource,
    PrimaryProvider,
    RiskGovernance,
)
from schema.enums import (
    ArchitectureType,
    AttentionType,
    BaseModelRelation,
    DisclosureState,
    EvalStatus,
    LicenseType,
    Modality,
    ModelStatus,
    ModelType,
    ResistanceLevel,
    RiskTier,
    TrainingMethod,
    UsePermission,
)

PROSE = "# Widget 1\n\nA reasoning model.\n\n## Notes\n\n- Ships with GQA attention.\n- Licensed under the Llama community licence."


def _card() -> ModelCard:
    return ModelCard(
        identity=Identity(
            model_id="acme/widget-1",
            display_name="Widget 1",
            provider="acme",
            version="widget-1.0",
            status=ModelStatus.BETA,
            model_type=ModelType.LLM_REASONING,
            model_subtypes=[ModelType.LLM_CODE, ModelType.AGENT_MODEL],
        ),
        architecture=Architecture(type=ArchitectureType.MOE, attention_type=AttentionType.GQA),
        lineage=Lineage(
            base_model_relation=BaseModelRelation.FINETUNE,
            training_method=TrainingMethod.GRPO,
        ),
        licensing=Licensing(
            license_type=LicenseType.LLAMA_COMMUNITY,
            commercial_use=UsePermission.RESTRICTED,
            commercial_use_source=PolicySource(
                kind="license",
                url="https://acme.example/licence",
                read_on="2026-09-01",
            ),
            commercial_use_conditions="free below 700M MAU; a licence is required above it",
            academic_use=UsePermission.ALLOWED,
        ),
        modalities=Modalities(input=[Modality.TEXT, Modality.IMAGE], output=[Modality.TEXT]),
        availability=Availability(
            primary_provider=PrimaryProvider(
                name="Acme",
                data_residency=["us", "eu"],
                data_residency_disclosure=DisclosureState.PUBLISHED,
                data_residency_source=PolicySource(
                    kind="terms_of_service",
                    url="https://acme.example/terms",
                    read_on="2026-09-02",
                ),
            ),
        ),
        risk_governance=RiskGovernance(adversarial_robustness=ResistanceLevel.MODERATE),
        downselect=Downselect(eval_status=EvalStatus.EVAL_PENDING, risk_tier=RiskTier.HIGH),
        card_author="test",
        prose_body=PROSE,
    )


def test_to_yaml_emits_plain_values_with_identity_flat():
    text = _card().to_yaml()

    assert "!!python/object" not in text
    assert "\nstatus: beta\n" in text
    assert "\nmodel_type: llm-reasoning\n" in text
    assert text.startswith("---\nmodel_id: acme/widget-1\n")
    assert "\nidentity:\n" not in text

    frontmatter = yaml.safe_load(text.split("---", 2)[1])
    assert frontmatter["model_subtypes"] == ["llm-code", "agent-model"]
    assert frontmatter["architecture"]["type"] == "MoE"
    assert frontmatter["licensing"]["commercial_use"] == "restricted"
    assert frontmatter["modalities"]["input"] == ["text", "image"]
    assert frontmatter["availability"]["primary_provider"]["data_residency_disclosure"] == "published"
    assert frontmatter["risk_governance"]["adversarial_robustness"] == "moderate"
    assert frontmatter["downselect"]["eval_status"] == "eval-pending"

    expected_top_level = set(Identity.model_fields) | (
        set(ModelCard.model_fields) - {"identity", "prose_body", "authoring_guide"}
    )
    assert set(frontmatter) == expected_top_level
    assert text.endswith(f"---\n\n{PROSE}")


def test_to_yaml_round_trips_through_from_yaml_string():
    card = _card()

    again = ModelCard.from_yaml_string(card.to_yaml())

    assert again.identity.status is ModelStatus.BETA
    assert again.identity.model_type is ModelType.LLM_REASONING
    assert again.identity.model_subtypes == [ModelType.LLM_CODE, ModelType.AGENT_MODEL]
    assert again.architecture.type is ArchitectureType.MOE
    assert again.architecture.attention_type is AttentionType.GQA
    assert again.lineage.base_model_relation is BaseModelRelation.FINETUNE
    assert again.lineage.training_method is TrainingMethod.GRPO
    assert again.licensing.license_type is LicenseType.LLAMA_COMMUNITY
    assert again.licensing.commercial_use is UsePermission.RESTRICTED
    assert again.licensing.academic_use is UsePermission.ALLOWED
    assert again.licensing.commercial_use_source.read_on == "2026-09-01"
    assert again.modalities.input == [Modality.TEXT, Modality.IMAGE]
    assert again.modalities.output == [Modality.TEXT]
    provider = again.availability.primary_provider
    assert provider.data_residency_disclosure is DisclosureState.PUBLISHED
    assert provider.data_residency == ["us", "eu"]
    assert again.risk_governance.adversarial_robustness is ResistanceLevel.MODERATE
    assert again.downselect.eval_status is EvalStatus.EVAL_PENDING
    assert again.downselect.risk_tier is RiskTier.HIGH
    assert again.prose_body == PROSE
    assert again == card
