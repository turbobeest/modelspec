"""Synthetic membership layouts for MODEL-431; no retained provider page text."""

from datetime import date

import pytest

from decision import verify
from decision.model import SourceRef, TargetRef, VerificationActor


def claim(plan, field, value):
    subject = f"moonshot/subscription/{plan.casefold()}"
    field = f"offering.subscription.{field}"
    return verify.Claim(
        target=TargetRef(kind="fact", id=f"{subject}#{field}"),
        subject=subject,
        names=(f"Kimi {plan}", plan),
        field=field,
        value=value,
        collector=VerificationActor(agent="collector", model_family="collector", method="fixture"),
        sources=(SourceRef(source_id="membership", snapshot_ref="sha256:" + "0" * 64,
                           cited_regions=["page"]),),
    )


class Regions:
    def __init__(self, page):
        self.page = page

    def text(self, *_args):
        return self.page

    def source_kind(self, *_args):
        return "provider_documentation"


def result(item, page):
    return verify.verify(item, Regions(page), [verify.SubscriptionPageExtractor()],
                         today=date(2026, 10, 20))


LEGACY = "Andante, Moderato, Allegretto, and Allegro are legacy plans."


@pytest.mark.parametrize("plan", ["Andante", "Moderato", "Allegretto", "Allegro"])
def test_legacy_list_verifies_each_named_plan(plan):
    item = claim(plan, "availability", "existing_subscribers_only")
    assert result(item, LEGACY).outcome == "verified"
    assert verify.SubscriptionPageExtractor().extract(item, LEGACY) == [
        verify.Reading(f"Kimi {plan}", "existing_subscribers_only")]


@pytest.mark.parametrize("plan", ["Go", "Plus", "Pro", "Max", "Ultra", "Andante Plus"])
def test_legacy_list_does_not_close_an_unlisted_plan(plan):
    assert verify.SubscriptionPageExtractor().extract(
        claim(plan, "availability", "existing_subscribers_only"), LEGACY) == []


@pytest.mark.parametrize("page", [
    "Andante and Moderato are not legacy plans.",
    "Andante and Moderato will become legacy plans.",
    "Andante and Moderato were legacy plans.",
    "Andante and Moderato are legacy plans?",
    "Andante and Moderato are legacy plans, but accept new subscribers.",
    "Go replaces Andante and Moderato as legacy plans.",
    "Andante Plus and Moderato are legacy plans.",
])
def test_legacy_wording_requires_an_unqualified_current_statement(page):
    assert verify.SubscriptionPageExtractor().extract(
        claim("Andante", "availability", "existing_subscribers_only"), page) == []


@pytest.mark.parametrize("page", [
    "It is false that Andante and Moderato are legacy plans.",
    "The page asks whether Andante, Moderato, and Allegro are legacy plans.",
    "Neither Andante nor Moderato are legacy plans.",
])
def test_legacy_list_rejects_reported_or_negated_propositions(page):
    assert verify.SubscriptionPageExtractor().extract(
        claim("Moderato", "availability", "existing_subscribers_only"), page) == []


@pytest.mark.parametrize("prices", [
    "¥57 | ¥43", "¥43 | ¥57",
    "¥57/month | ¥43/month", "¥43/month | ¥57/month",
    "¥57 | ¥43/month", "¥43/month | ¥57",
])
def test_unlabelled_price_alternatives_produce_no_reading(prices):
    page = f"Plan | Option A | Option B\nGo | {prices}"
    for value in (57, 43):
        assert verify.SubscriptionPageExtractor().extract(
            claim("Go", "price_cny", value), page) == []


@pytest.mark.parametrize("columns", [
    "Monthly billing | Annual total | Monthly equivalent with annual billing\n"
    "Go | ¥57/month | ¥516/year | ¥43/month",
    "Monthly equivalent with annual billing | Annual total | Monthly billing\n"
    "Go | ¥43/month | ¥516/year | ¥57/month",
])
def test_price_table_uses_billing_headers_to_exclude_annual_equivalent(columns):
    page = f"Plan | {columns}"
    item = claim("Go", "price_cny", 57)
    assert verify.SubscriptionPageExtractor().extract(item, page) == [
        verify.Reading("Kimi Go", "57")]
    assert result(item, page).outcome == "verified"
    assert result(claim("Go", "price_cny", 43), page).outcome == "mismatch"
    assert result(claim("Go", "billing_period", "monthly"), page).outcome == "verified"


@pytest.mark.parametrize("prices", [
    "¥57",
    "¥57 | ¥57",
    "¥57/month | ¥43/month billed annually",
    "¥43/month billed annually | ¥57/month",
])
def test_price_reader_keeps_unambiguous_amounts(prices):
    readings = verify.SubscriptionPageExtractor().extract(
        claim("Go", "price_cny", 57), f"Plan | Price\nGo | {prices}")
    assert readings
    assert {reading.value for reading in readings} == {"57"}


PLAN_LINES = {
    "Go": "Go: Draft presentations and publish a website. Kimi Code is excluded.",
    "Plus": "Plus: Kimi Code and Agent Swarm are included.",
    "Pro": "Pro: Extra credits, Goal Mode, and a dedicated Kimi Claw.",
    "Max": "Max: Additional credits and higher Agent task concurrency.",
    "Ultra": "Ultra: More credits and scheduled tasks. Up to 12 parallel Agent tasks.",
}
PLAN_PAGE = "Plan | Monthly billing\nGo | ¥57/month\n\nChoosing a plan\n" + "\n".join(
    PLAN_LINES.values())


@pytest.mark.parametrize("plan", PLAN_LINES)
def test_named_plan_line_preserves_agent_entitlement_and_restrictions(plan):
    item = claim(plan, "programmatic_or_agent_use", PLAN_LINES[plan])
    assert verify.SubscriptionPageExtractor().extract(item, PLAN_PAGE) == [
        verify.Reading(f"Kimi {plan}", PLAN_LINES[plan])]
    assert result(item, PLAN_PAGE).outcome == "verified"


@pytest.mark.parametrize("plan", ["Pro", "Max", "Ultra"])
def test_named_plan_line_reads_its_own_allowance(plan):
    item = claim(plan, "usage_allowance", PLAN_LINES[plan])
    assert verify.SubscriptionPageExtractor().extract(item, PLAN_PAGE) == [
        verify.Reading(f"Kimi {plan}", PLAN_LINES[plan])]
    assert result(item, PLAN_PAGE).outcome == "verified"


@pytest.mark.parametrize("plan", ["Go", "Plus"])
def test_features_without_usage_wording_do_not_become_allowances(plan):
    assert verify.SubscriptionPageExtractor().extract(
        claim(plan, "usage_allowance", None), PLAN_PAGE) == []


@pytest.mark.parametrize("field", ["usage_allowance", "programmatic_or_agent_use"])
@pytest.mark.parametrize("line", [
    "Pro Plus: More credits and Kimi Code.",
    "Other Pro: More credits and Kimi Code.",
    "Plus: More credits and Kimi Code than Pro.",
    "Available in Pro: More credits and Kimi Code.",
    "Guide: Pro has more credits and Kimi Code.",
    "Pro benefits appear below.\nPlus: More credits and Kimi Code.",
    "## Pro\nNo benefits published.\n## Plus\nPlus: More credits and Kimi Code.",
])
def test_named_plan_line_does_not_borrow_sibling_benefits(field, line):
    page = f"Plan | Monthly billing\nGo | ¥57/month\n\n{line}"
    assert verify.SubscriptionPageExtractor().extract(claim("Pro", field, None), page) == []


def test_agent_exclusion_does_not_verify_positive_access():
    assert result(claim("Go", "programmatic_or_agent_use", "Kimi Code is included."),
                  PLAN_PAGE).outcome == "mismatch"
