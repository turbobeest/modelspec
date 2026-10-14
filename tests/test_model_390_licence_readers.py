"""MODEL-390 deterministic legal readings, using synthetic clause fixtures."""

from datetime import date
from pathlib import Path

import pytest

from decision import verify
from decision.model import SourceRef, TargetRef, VerificationActor


class TermsRegions:
    def __init__(self, text: str, kind: str = "provider_terms", *, bound: bool = True):
        self.terms = text
        self.kind = kind
        self.bound = bound

    def text(self, source_id: str, _copy_ref: str, _region_id: str) -> str:
        if source_id == "terms":
            return self.terms
        if self.bound:
            return "Nimbus 3 API is subject to these terms: https://example.test/terms"
        return "Nimbus 3 API documentation."

    def source_kind(self, source_id: str) -> str:
        return self.kind if source_id == "terms" else "lab_documentation"

    def source_url(self, source_id: str) -> str:
        return "https://example.test/terms" if source_id == "terms" else "https://example.test/model"


def check(field: str, value, text: str, kind: str = "provider_terms", *, bound: bool = True,
          unit: str | None = None):
    claim = verify.Claim(
        target=TargetRef(kind="fact", id=f"lab/nimbus-3#{field}"),
        subject="lab/nimbus-3", names=("Nimbus 3",), field=field, value=value,
        collector=VerificationActor(agent="fixture", model_family="openai", method="collect"),
        sources=tuple(SourceRef(source_id=source, snapshot_ref="sha256:" + "a" * 64,
                                cited_regions=["page"]) for source in ("terms", "model")),
        unit=unit or ("monthly_active_users" if field == "licence.user_cap" else None),
    )
    return verify.verify(claim, TermsRegions(text, kind, bound=bound),
                         verify.deterministic_extractors(), today=date(2026, 10, 14))


@pytest.mark.parametrize(("field", "value"), [
    ("licence.commercial_use", "permitted"),
    ("licence.fine_tuning", "permitted"),
    ("licence.output_training", None),
    ("licence.user_cap", "unbounded"),
])
def test_complete_apache_terms_without_optional_appendix(field, value):
    text = (Path(__file__).parent / "fixtures/licences/apache-2.0.txt").read_text()
    operative = text.split("APPENDIX:", 1)[0].strip()
    result = check(field, value, operative, "licence_text")
    assert result.outcome == "verified", result


@pytest.mark.parametrize("extra", [
    "Commercial use is forbidden.",
    "A separate agreement is required above 500 monthly active users.",
])
def test_apache_without_appendix_still_rejects_added_terms(extra):
    text = (Path(__file__).parent / "fixtures/licences/apache-2.0.txt").read_text()
    result = check("licence.commercial_use", "permitted",
                   text.split("APPENDIX:", 1)[0] + extra, "licence_text")
    assert result.outcome == "skipped", result


@pytest.mark.parametrize("kind", ["licence_text", "provider_terms"])
def test_provider_terms_can_state_a_monthly_user_agreement_cap(kind):
    text = "If you exceed 200 million monthly active users, you must obtain a separate licence."
    result = check("licence.user_cap", 200_000_000, text, kind)
    assert result.outcome == "verified", result


@pytest.mark.parametrize("text", [
    "At 200 million monthly active users you must display our brand.",
    "If revenue exceeds 200 million dollars, a separate licence is required.",
    "The service allows 200 requests per minute.",
    "Our service has 200 million monthly active users.",
    "You do not need a separate licence above 200 million monthly active users.",
])
def test_non_agreement_thresholds_and_silence_do_not_read_a_user_cap(text):
    for value in (200_000_000, "unbounded", None):
        result = check("licence.user_cap", value, text)
        assert result.outcome == "skipped", result


@pytest.mark.parametrize("text", [
    "Subject to these terms, you may use the services in your applications.",
    "We grant you a right to access and use the services, subject to this agreement.",
    "You may use the API for business purposes in compliance with these terms.",
])
def test_conditional_service_grants_read_commercial_use(text):
    assert check("licence.commercial_use", "permitted_with_conditions", text).outcome == "verified"
    wrong = check("licence.commercial_use", "permitted", text)
    assert wrong.outcome == "mismatch", wrong
    assert wrong.diffs[0].field == "value"


@pytest.mark.parametrize("text", [
    "Subject to these terms, you may not use the services in your applications.",
    "We do not grant you a right to access and use the services under this agreement.",
    "Your use of the services is governed by these terms.",
    "You own the output. We retain ownership of the services.",
    "You may use the API only for non-commercial purposes under these terms.",
    "You may use the services for evaluation purposes under this agreement.",
])
def test_ownership_and_noncommercial_or_negated_grants_do_not_verify_commercial_use(text):
    assert check("licence.commercial_use", "permitted_with_conditions", text).outcome == "skipped"


@pytest.mark.parametrize("text", [
    "You may not use output to develop models that compete with our models.",
    "Customer shall not use outputs to train or improve a competing AI model.",
    "You must not train machine learning models on grounded results and search suggestions.",
    "You may not use Google Maps data from outputs to train an AI model.",
])
def test_output_training_subset_restrictions(text):
    result = check("licence.output_training", "restricted", text)
    assert result.outcome == "verified", result
    assert check("licence.output_training", "prohibited", text).outcome == "mismatch"


@pytest.mark.parametrize("text", [
    "We do not use your outputs to train our models.",
    "You may not use the services to develop competing models.",
    "You own all outputs and may create derivative works of the services.",
    "You are not prohibited from using output to train competing models.",
    "You may use outputs. Competitors may not train our staff.",
    "You may not use outputs to develop software that competes with our services.",
])
def test_unrelated_training_or_modification_clauses_do_not_read_output_training(text):
    assert check("licence.output_training", "restricted", text).outcome == "skipped"


def test_model_modification_prohibition_reads_fine_tuning():
    text = "Customer shall not modify or create derivative works of the model weights."
    assert check("licence.fine_tuning", "prohibited", text).outcome == "verified"
    assert check("licence.output_training", "restricted", text).outcome == "skipped"


@pytest.mark.parametrize("text", [
    "We do not modify the services using your inputs.",
    "Customer may modify the services.",
    "Customer shall not modify the documentation.",
    "Customer shall not modify or create derivative works of the services.",
    "Fine-tuning is available as an API feature.",
])
def test_unrelated_modification_and_product_features_do_not_read_fine_tuning(text):
    for value in ("prohibited", None):
        assert check("licence.fine_tuning", value, text).outcome == "skipped"


@pytest.mark.parametrize("text", [
    "Subject to these terms, Acme grants Customer a non-exclusive right to access and use "
    "the Services. Customer may use the API to integrate the services into Customer "
    "Applications for End Users.",
    "Subject to this agreement, Acme grants to Customer a limited licence during the Term "
    "to: (a) access and use the Services; (b) integrate the API into Customer Applications "
    "for End Users.",
    "Use of the Services is for developers building with AI models for professional or "
    "business purposes. Use must comply with the prohibited-use policy.",
])
def test_provider_grant_and_customer_application_clause_families(text):
    result = check("licence.commercial_use", "permitted_with_conditions", text)
    assert result.outcome == "verified", result


@pytest.mark.parametrize("text", [
    "Customer will not, and will not permit End Users to: (a) reverse engineer the service; "
    "(b) except under a separate authorization, use Output to develop AI models that compete "
    "with our models.",
    "You shall not do the following: (i) misuse the service; (ii) use Outputs of the Services "
    "to train, fine-tune or otherwise improve a model that competes with our models.",
    "Customer shall not (or allow others to): (a) resell access; (b) use any Output "
    "(defined below) to perform model distillation or develop a competing product.",
    "You will not, and will not allow your users to, train on, or otherwise learn from "
    "Grounded Results or Search Suggestions.",
])
def test_prohibition_list_and_grounded_output_clause_families(text):
    result = check("licence.output_training", "restricted", text)
    assert result.outcome == "verified", result


def test_prohibition_prefix_covers_adjacent_enumerated_paragraphs():
    text = (
        "You agree that you will not do the following:\n"
        "(i) Resell the service.\n"
        "(ii) Use Outputs of the Services to train models that compete with ours.\n"
        "(iii) Misuse account credentials.\n"
        "The following section describes payment."
    )
    result = check("licence.output_training", "restricted", text)
    assert result.outcome == "verified", result


@pytest.mark.parametrize("text", [
    "Customer will not: (a) resell the services.\n"
    "Permitted uses include:\n(a) use output to train competing models; (b) archive output.",
    "You agree that you will not do the following:\n(i) Resell the service.\n"
    "Our research team uses Outputs of the Services to train competing models.",
    "Acme does not grant Customer a non-exclusive right to access and use the Services. "
    "The API can integrate into Customer Applications for End Users, subject to these terms.",
])
def test_prohibition_and_grant_scopes_do_not_extend_to_unrelated_paragraphs(text):
    for field in ("licence.commercial_use", "licence.output_training"):
        assert check(field, "restricted" if field == "licence.output_training" else
                     "permitted_with_conditions", text).outcome == "skipped"


GEMMA_TERMS = (
    "Gemma Terms of Use. You may use, reproduce, modify, distribute Gemma and Model "
    "Derivatives, subject to these Terms. You must comply with the Gemma Prohibited Use "
    "Policy. Model Derivatives include models trained on synthetic data Outputs of Gemma "
    "or by distillation. Model Derivatives remain subject to these Terms. "
    "No separate agreement is required at any number of monthly active users."
)


@pytest.mark.parametrize(("field", "value"), [
    ("licence.commercial_use", "permitted_with_conditions"),
    ("licence.fine_tuning", "permitted_with_conditions"),
    ("licence.output_training", "restricted"),
    ("licence.user_cap", "unbounded"),
])
def test_gemma_clause_families(field, value):
    result = check(field, value, GEMMA_TERMS, "licence_text")
    assert result.outcome == "verified", result


@pytest.mark.parametrize("text", [
    GEMMA_TERMS.replace("You may use, reproduce, modify, distribute", "You may not use"),
    GEMMA_TERMS.replace("You must comply", "We must comply"),
])
def test_gemma_negated_grant_or_unbound_policy_does_not_read_commercial_use(text):
    assert check("licence.commercial_use", "permitted_with_conditions", text,
                 "licence_text").outcome == "skipped"


@pytest.mark.parametrize("text", [
    GEMMA_TERMS.replace("Model Derivatives remain subject to these Terms.", ""),
    GEMMA_TERMS.replace("models trained on synthetic data Outputs of Gemma or by distillation",
                        "modifications of the original weights"),
])
def test_gemma_derivative_definition_alone_does_not_restrict_output_training(text):
    assert check("licence.output_training", "restricted", text, "licence_text").outcome == "skipped"


GEMMA_DISTRIBUTION = (
    '"Model Derivatives" means models made by distillation or synthetic data Outputs by '
    "Gemma for training that model. You may use, reproduce, modify, distribute and display "
    "Gemma Services only in accordance with this Agreement. You must not use Gemma Services "
    "for uses restricted by the Gemma Prohibited Use Policy. You must notify recipients "
    "that Gemma or Model Derivatives are subject to the use restrictions in Section 3.2."
)


@pytest.mark.parametrize(("field", "value"), [
    ("licence.commercial_use", "permitted_with_conditions"),
    ("licence.fine_tuning", "permitted_with_conditions"),
    ("licence.output_training", "restricted"),
])
def test_gemma_use_grant_and_distribution_restrictions(field, value):
    result = check(field, value, GEMMA_DISTRIBUTION, "licence_text")
    assert result.outcome == "verified", result


@pytest.mark.parametrize("text", [
    GEMMA_DISTRIBUTION.replace("You may use", "You may not use"),
    GEMMA_DISTRIBUTION.replace("You must not use", "We must not use"),
])
def test_gemma_use_grant_requires_customer_permission_and_policy(text):
    for field in ("licence.commercial_use", "licence.fine_tuning"):
        assert check(field, "permitted_with_conditions", text, "licence_text").outcome == "skipped"


@pytest.mark.parametrize("text", [
    "If you exceed 200 million monthly active users, you must obtain.",
    "If you exceed 20,0 million monthly active users, you must obtain a separate licence.",
    "If you exceed 2,,00 million monthly active users, you must obtain a separate licence.",
    "If you exceed ,,, million monthly active users, you must obtain a separate licence.",
])
def test_incomplete_or_malformed_cap_clauses_remain_unread(text):
    assert check("licence.user_cap", 200_000_000, text).outcome == "skipped"


@pytest.mark.parametrize(("field", "value", "text"), [
    ("licence.commercial_use", "permitted_with_conditions", "Commercial use is prohibited. "
     "Subject to these terms, you may use the services in your applications."),
    ("licence.commercial_use", "permitted_with_conditions", "For evaluation use only. "
     "We grant you a right to access and use the services, subject to this agreement."),
    ("licence.output_training", "restricted", "You may not use output to develop models "
     "that compete with our models. This restriction has been revoked."),
    ("licence.user_cap", 200_000_000, "If you exceed 200 million monthly active users, "
     "you must obtain a separate licence. This threshold does not apply to API customers."),
])
def test_conflicting_or_repealed_clauses_remain_unread(field, value, text):
    assert check(field, value, text).outcome == "skipped"


@pytest.mark.parametrize("unit", ["tokens", "usd_per_task"])
def test_cap_reading_uses_the_published_unit(unit):
    text = "If you exceed 200 million monthly active users, you must obtain a separate licence."
    result = check("licence.user_cap", 200_000_000, text, unit=unit)
    assert result.outcome == "mismatch", result
    assert any(diff.field == "unit" for diff in result.diffs)


def test_explicit_clause_still_requires_model_binding_and_permitted_source_kind():
    text = "Subject to these terms, you may use the services in your applications."
    result = check("licence.commercial_use", "permitted_with_conditions", text, bound=False)
    assert result.outcome == "mismatch", result
    assert result.diffs[0].field == "model"
    result = check("licence.user_cap", None, text, "lab_documentation")
    assert result.outcome == "mismatch", result
    assert result.diffs[0].field == "source_kind"
