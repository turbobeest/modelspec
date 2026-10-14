"""Compound team plans must not read an individual tier's wording."""

from datetime import date

import pytest

from decision.model import SourceRef, TargetRef, VerificationActor
from decision.verify import Claim, Queue, SubscriptionPageExtractor, VerificationLog
from scripts.accuracy import verify_fidelity_sample


class PlanPage:
    def __init__(self, text: str) -> None:
        self.page = text

    def text(self, source_id: str, copy_ref: str, region_id: str) -> str:
        return self.page


def _team_claim(value: str) -> Claim:
    return Claim(
        target=TargetRef(
            kind="fact",
            id="example/subscription/teams-premium#offering.subscription.programmatic_or_agent_use",
        ),
        subject="example/subscription/teams-premium",
        names=("Example Teams (Premium seat)", "Premium", "Teams", "teams-premium"),
        field="offering.subscription.programmatic_or_agent_use",
        value=value,
        collector=VerificationActor(
            agent="synthetic-collector", model_family="synthetic", method="synthetic@1",
        ),
        sources=(SourceRef(
            source_id="plan", snapshot_ref="sha256:" + "0" * 64, cited_regions=["page"],
        ),),
    )


INDIVIDUAL_CARD = """\
Premium
$40/month
Get Premium
Agent runs
Personal projects
Priority support
Account settings
Email updates
Compare features
Feature | Premium $40/month | Teams $60/user/month
Agents | Yes | Yes
"""


@pytest.mark.parametrize(
    "stored_wording", ["Project agents with team sharing", "Agent runs"],
    ids=["different-individual-wording", "matching-individual-wording"],
)
def test_team_plan_without_its_own_wording_is_undetermined(tmp_path, stored_wording: str) -> None:
    claim = _team_claim(stored_wording)
    queue = Queue(tmp_path / "verification")
    log = VerificationLog(tmp_path / "verification")

    result = verify_fidelity_sample(
        [claim], regions=PlanPage(INDIVIDUAL_CARD), extractors=[SubscriptionPageExtractor()],
        queue=queue, log=log, today=date(2026, 10, 13), source_urls={},
    )

    assert result.details[0]["outcome"] == "undetermined"
    assert result.counts["mismatch"] == result.counts["verified"] == 0
    assert log.latest() == {}
    assert queue.recrawl_requests() == []


def test_team_plan_stated_agent_restriction_remains_a_mismatch(tmp_path) -> None:
    claim = _team_claim("Project agents enabled")
    page = "Teams\n$60/month\nGet Teams\nNo project agents\n"

    result = verify_fidelity_sample(
        [claim], regions=PlanPage(page), extractors=[SubscriptionPageExtractor()],
        queue=Queue(tmp_path), log=VerificationLog(tmp_path),
        today=date(2026, 10, 13), source_urls={},
    )

    assert result.details[0]["outcome"] == "mismatch"
    assert result.details[0]["diff"] == [{
        "field": "value", "expected": "Project agents enabled", "found": "No project agents",
    }]
