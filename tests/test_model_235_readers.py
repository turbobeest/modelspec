"""Trimmed 2026-10-14 page projections for the MODEL-235 offline re-read."""

from dataclasses import replace
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


def test_mistral_pro_does_not_borrow_team_feature():
    text = (PAGES / "mistral-pro.txt").read_text()
    result = verify(
        claim("Domain name verification."),
        Page(text),
        deterministic_extractors(),
        today=date(2026, 10, 14),
    )
    assert result.outcome == "mismatch", result


@pytest.mark.parametrize("feature", ["Generate Spreadsheets", "Free"])
def test_mistral_heading_like_feature_keeps_pinned_mismatch(feature):
    text = f"""\
Pro
$14.99
/mo
Faster responses.
{feature}
All-day coding in the CLI, IDE, or on web.
Generate spreadsheets and slides.
Better image generation and editing.
$25.5 /mo in API credits.
"""
    result = verify(
        claim("All-day coding in the CLI, IDE, or on web."),
        Page(text),
        deterministic_extractors(),
        today=date(2026, 10, 14),
    )
    assert result.outcome == "mismatch", result


PROBE_A = """\
Pro
$14.99
/mo
Faster responses.
Generate spreadsheets and slides.
Scale
$25.5 /mo in API credits.
All-day coding in the CLI, IDE, and on web.
Extra coding tools for this neighbouring plan.
One more neighbouring feature.
Team
$24.99
/user/mo
All-day coding in the CLI, IDE, or on web.
Domain name verification.
"""

PROBE_B = """\
Pro
$14.99
/mo
Faster responses.
Team
$25.5 /mo in API credits.
All-day coding in the CLI, IDE, or on web.
Shared coding workspace details.
Another feature line here.
$24.99
/user/mo
"""


@pytest.mark.parametrize(
    "text,neighbour_sentence",
    [
        (PROBE_A, "All-day coding in the CLI, IDE, and on web."),
        (PROBE_B, "All-day coding in the CLI, IDE, or on web."),
    ],
    ids=["probe_a", "probe_b"],
)
def test_mistral_pro_does_not_borrow_card_with_api_credit_currency(text, neighbour_sentence):
    result = verify(
        claim(neighbour_sentence), Page(text), deterministic_extractors(), today=date(2026, 10, 14)
    )
    assert result.outcome == "mismatch", result

    team = replace(
        claim("All-day coding in the CLI, IDE, or on web."),
        target=TargetRef(
            kind="fact",
            id="mistral/subscription/team#offering.subscription.programmatic_or_agent_use",
        ),
        subject="mistral/subscription/team",
        names=("Mistral Team", "Team", "team"),
    )
    result = verify(team, Page(text), deterministic_extractors(), today=date(2026, 10, 14))
    assert result.outcome == "verified", result


@pytest.mark.parametrize("scale", ["Scale", "## Scale"])
def test_mistral_card_boundary_control_keeps_bare_price_and_markdown_heading(scale):
    text = PROBE_A.replace("Scale\n$25.5", f"{scale}\n$19\n$25.5")
    near = "All-day coding in the CLI, IDE, and on web."
    exact = "All-day coding in the CLI, IDE, or on web."
    for value in (near, exact):
        result = verify(
            claim(value), Page(text), deterministic_extractors(), today=date(2026, 10, 14)
        )
        assert result.outcome == "mismatch", result
    for value, expected in ((exact, "verified"), (near, "mismatch")):
        team = replace(
            claim(value),
            target=TargetRef(
                kind="fact",
                id="mistral/subscription/team#offering.subscription.programmatic_or_agent_use",
            ),
            subject="mistral/subscription/team",
            names=("Mistral Team", "Team", "team"),
        )
        result = verify(team, Page(text), deterministic_extractors(), today=date(2026, 10, 14))
        assert result.outcome == expected, result


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
