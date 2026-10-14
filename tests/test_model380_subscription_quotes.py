"""Synthetic plan wording regressions for MODEL-380."""

from datetime import date

import pytest

from decision.model import SourceRef, TargetRef, VerificationActor
from decision.verify import Claim, Diff, Queue, SubscriptionPageExtractor, VerificationLog, compare
from scripts.accuracy import verify_fidelity_sample


def plan_claim(field, value):
    return Claim(
        target=TargetRef(kind="fact", id=f"example/subscription/premium#{field}"),
        subject="example/subscription/premium",
        names=("Premium",),
        field=f"offering.subscription.{field}",
        value=value,
        collector=VerificationActor(agent="synthetic-collector", model_family="synthetic",
                                    method="synthetic@1"),
        sources=(SourceRef(source_id="plan", snapshot_ref="sha256:" + "0" * 64,
                           cited_regions=["page"]),),
    )


class PlanRegion:
    def __init__(self, text):
        self.page = text

    def text(self, source_id, copy_ref, region_id):
        return self.page


@pytest.mark.parametrize("field,value,page", [
    ("coverage_quote", "Includes Example models", "Pricing\nPremium\n$37/mo\n"),
    ("coverage_quote", "Includes Example models", "<!DOCTYPE html><html><p>Pricing</p></html>"),
    ("usage_allowance", "500 monthly credits", "Premium\n$37\n/mo\n$74\nGet Premium\n"),
    ("programmatic_or_agent_use", "Includes Example Agent", "Premium\n$37\n/mo\nGet Premium\n"),
])
def test_absent_plan_wording_is_undetermined(tmp_path, field, value, page):
    claim = plan_claim(field, value)
    extractor = SubscriptionPageExtractor()
    assert extractor.extract(claim, page) == []
    result = verify_fidelity_sample(
        [claim], regions=PlanRegion(page), extractors=[extractor],
        queue=Queue(tmp_path), log=VerificationLog(tmp_path), today=date(2026, 10, 13),
        source_urls={},
    )
    assert result.details[0]["outcome"] == "undetermined"


def test_coverage_quote_is_read_when_the_page_states_it():
    claim = plan_claim("coverage_quote", "Includes Example models")
    readings = SubscriptionPageExtractor().extract(
        claim, "Pricing\nPremium\n$37/mo\nIncludes Example models\n"
    )
    assert compare(claim, readings) == []
    assert {reading.value for reading in readings} == {"Includes Example models"}


def test_a_changed_plan_allowance_still_disagrees():
    claim = plan_claim("usage_allowance", "500 monthly credits")
    readings = SubscriptionPageExtractor().extract(
        claim, "Premium\n$37/month\n200 monthly credits\n"
    )
    assert readings
    assert compare(claim, readings) == [
        Diff("value", "500 monthly credits", "200 monthly credits")
    ]
