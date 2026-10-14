"""Trimmed 2026-10-14 page projections for the MODEL-235 offline re-read."""

from datetime import date
from pathlib import Path

import pytest

from decision.model import SourceRef, TargetRef, VerificationActor
from decision.verify import Claim, deterministic_extractors, verify

PAGES = Path(__file__).parent / "fixtures" / "model_235_readers"


class Page:
    def __init__(self, text):
        self.page = text

    def text(self, source_id, copy_ref, region_id):
        return self.page


def claim(value):
    return Claim(
        target=TargetRef(
            kind="fact",
            id="mistral/subscription/pro#offering.subscription.programmatic_or_agent_use",
        ),
        subject="mistral/subscription/pro",
        names=("Mistral Pro", "Pro", "pro"),
        field="offering.subscription.programmatic_or_agent_use",
        value=value,
        collector=VerificationActor(
            agent="claude-model-201-collector",
            model_family="anthropic",
            method="primary-source-read@2026-09-29",
        ),
        sources=(
            SourceRef(
                source_id="model-201-mistral-pricing",
                snapshot_ref="sha256:" + "0" * 64,
                cited_regions=["page"],
            ),
        ),
    )


def test_mistral_pro_reads_coding_access_before_api_credit_feature():
    text = (PAGES / "mistral-pro.txt").read_text()
    result = verify(
        claim("All-day coding in the CLI, IDE, or on web."),
        Page(text),
        deterministic_extractors(),
        today=date(2026, 10, 14),
    )
    assert result.outcome == "verified", result


def test_mistral_pro_does_not_borrow_team_feature():
    text = (PAGES / "mistral-pro.txt").read_text()
    result = verify(
        claim("Domain name verification."),
        Page(text),
        deterministic_extractors(),
        today=date(2026, 10, 14),
    )
    assert result.outcome == "mismatch", result


@pytest.mark.parametrize(
    "fixture,subject,names,field,value",
    [
        (
            "gemini-flash-lite.txt",
            "google-gemini-api/google/gemini-3-5-flash/global/standard",
            ("Gemini 3.5 Flash",),
            "offering.price.input",
            1.5,
        ),
        (
            "vertex-cited-table-38.txt",
            "google-vertex-ai/anthropic/claude-sonnet-5-5/global/standard",
            ("Claude Sonnet 5.5", "Sonnet 5.5"),
            "offering.price.input",
            2.0,
        ),
        (
            "minimax-m-plan.txt",
            "minimax/subscription/token-plus",
            ("MiniMax Token Plan Plus", "Plus", "token-plus"),
            "offering.subscription.price",
            22,
        ),
        (
            "moonshot-current-plans.txt",
            "moonshot/subscription/andante",
            ("Kimi Andante", "Andante", "andante"),
            "offering.subscription.price_cny",
            49,
        ),
    ],
)
def test_saved_page_does_not_verify_an_absent_model_or_plan(
    fixture,
    subject,
    names,
    field,
    value,
):
    filed = Claim(
        target=TargetRef(kind="fact", id=f"{subject}#{field}"),
        subject=subject,
        names=names,
        field=field,
        value=value,
        unit="usd_per_1m_tokens" if field.startswith("offering.price.") else None,
        collector=VerificationActor(
            agent="filed-collector", model_family="anthropic", method="primary-source-read@1"
        ),
        sources=(
            SourceRef(
                source_id="saved-page", snapshot_ref="sha256:" + "0" * 64, cited_regions=["page"]
            ),
        ),
    )
    result = verify(
        filed,
        Page((PAGES / fixture).read_text()),
        deterministic_extractors(),
        today=date(2026, 10, 14),
    )
    assert result.outcome == "mismatch", result
    assert result.diffs[0].found is None


@pytest.mark.parametrize(
    "tier,value",
    [
        ("Go", "Usage relative to Go: 1x (baseline)"),
        ("Explore", "Usage relative to Go: 3x"),
        ("Build", "Usage relative to Go: 7.5x"),
    ],
)
def test_minimax_faq_reads_exact_tier_allowance_beside_api_key_placeholder(tier, value):
    field = "offering.subscription.usage_allowance"
    subject = f"minimax/subscription/{tier.lower()}"
    filed = Claim(
        target=TargetRef(kind="fact", id=f"{subject}#{field}"),
        subject=subject,
        names=(f"MiniMax M Plan {tier}", tier),
        field=field,
        value=value,
        collector=VerificationActor(
            agent="filed-collector", model_family="anthropic", method="primary-source-read@1"
        ),
        sources=(
            SourceRef(
                source_id="saved-page", snapshot_ref="sha256:" + "0" * 64, cited_regions=["page"]
            ),
        ),
    )
    text = (PAGES / "minimax-faq.txt").read_text()
    result = verify(filed, Page(text), deterministic_extractors(), today=date(2026, 10, 14))
    assert result.outcome == "verified", result

    markup = "<div>" + text + "</div>"
    result = verify(filed, Page(markup), deterministic_extractors(), today=date(2026, 10, 14))
    assert result.outcome != "verified", result
