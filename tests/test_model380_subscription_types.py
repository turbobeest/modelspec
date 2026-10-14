"""MODEL-380: subscription readers compare identified lists, not plan prose."""

from datetime import date
from pathlib import Path

import pytest

from decision import verify
from decision.model import SourceRef, TargetRef, VerificationActor
from scripts import accuracy


class _Regions:
    def __init__(self, text: str):
        self.region = text

    def text(self, source_id: str, copy_ref: str, region_id: str) -> str:
        return self.region


def _claim(field: str, value: list[str] | str) -> verify.Claim:
    return verify.Claim(
        target=TargetRef(kind="fact", id=f"lab/subscription/pro#{field}"),
        subject="lab/subscription/pro",
        names=("Lab Pro", "Pro"),
        field=field,
        value=value,
        collector=VerificationActor(agent="collector", model_family="gpt", method="read"),
        sources=(SourceRef(
            source_id="plans", snapshot_ref="sha256:" + "a" * 64,
            cited_regions=["page"],
        ),),
    )


def _fidelity(
    tmp_path: Path, field: str, value: list[str] | str, page: str, *,
    unchanged_unread: bool = False,
):
    claim = _claim(field, value)
    queue = verify.Queue(tmp_path / "verification")
    log = verify.VerificationLog(tmp_path / "verification")
    result = accuracy.verify_fidelity_sample(
        [claim], regions=_Regions(page), extractors=verify.deterministic_extractors(),
        queue=queue, log=log, today=date(2026, 10, 13),
        source_urls={"plans": "https://example.test/plans"},
        unread={("fact", claim.target.id): "mismatch"} if unchanged_unread else None,
    )
    return claim, result, queue, log


@pytest.mark.parametrize("unchanged_unread", [False, True])
@pytest.mark.parametrize("page", [
    "Pro\n$20/month\n"
    "Pro includes broad model choice, command-line tools, and editor integrations.\n",
    "Features | Pro\nSupported models | A selection of leading models\n",
    "Features | Pro\nSupported models | <div>Model selector unavailable</div>\n",
])
def test_unidentified_model_list_is_undetermined(
    tmp_path: Path, page: str, unchanged_unread: bool,
) -> None:
    _, result, queue, log = _fidelity(
        tmp_path, "offering.subscription.models_covered", ["openai/gpt-6-sol"], page,
        unchanged_unread=unchanged_unread,
    )

    assert result.details[0]["outcome"] == "undetermined"
    assert result.counts["undetermined"] == 1
    assert queue.recrawl_requests() == []
    assert log.records() == []


def test_identified_model_list_compares_ids_with_names(tmp_path: Path) -> None:
    _, result, _, _ = _fidelity(
        tmp_path, "offering.subscription.models_covered",
        ["openai/gpt-6-sol", "anthropic/claude-opus-5-5"],
        "Features | Pro\nSupported models | GPT-6 Sol, Claude Opus 5.5\n",
    )

    assert result.details[0]["outcome"] == "verified"
    assert result.counts["verified"] == 1


def test_identified_model_subset_remains_a_mismatch(tmp_path: Path) -> None:
    claim, result, queue, log = _fidelity(
        tmp_path, "offering.subscription.models_covered",
        ["openai/gpt-6-sol", "anthropic/claude-opus-5-5"],
        "Features | Pro\nSupported models | GPT-6 Sol\n",
    )

    assert result.details[0]["outcome"] == "mismatch"
    assert result.details[0]["diff"] == [{
        "field": "value",
        "expected": ["openai/gpt-6-sol", "anthropic/claude-opus-5-5"],
        "found": "GPT-6 Sol",
    }]
    assert queue.recrawl_requests() == [(claim.target, "mismatch")]
    assert log.latest()[("fact", claim.target.id)].outcome == "mismatch"


def test_additional_identified_model_remains_a_mismatch(tmp_path: Path) -> None:
    claim, result, queue, log = _fidelity(
        tmp_path, "offering.subscription.models_covered", ["openai/gpt-6-sol"],
        "Features | Pro\nSupported models | GPT-6 Sol, Claude Opus 5.5\n",
    )

    assert result.details[0]["outcome"] == "mismatch"
    assert result.details[0]["diff"] == [{
        "field": "value", "expected": ["openai/gpt-6-sol"],
        "found": "GPT-6 Sol, Claude Opus 5.5",
    }]
    assert queue.recrawl_requests() == [(claim.target, "mismatch")]
    assert log.latest()[("fact", claim.target.id)].outcome == "mismatch"


def test_explicit_model_withdrawal_remains_a_mismatch(tmp_path: Path) -> None:
    claim, result, queue, log = _fidelity(
        tmp_path, "offering.subscription.models_covered", ["openai/gpt-6-sol"],
        "Features | Pro\nSupported models | None\n",
    )

    assert result.details[0]["outcome"] == "mismatch"
    assert result.details[0]["diff"] == [{
        "field": "value", "expected": ["openai/gpt-6-sol"], "found": "None",
    }]
    assert queue.recrawl_requests() == [(claim.target, "mismatch")]
    assert log.latest()[("fact", claim.target.id)].outcome == "mismatch"


def test_explicit_empty_model_list_verifies_an_empty_claim(tmp_path: Path) -> None:
    _, result, _, _ = _fidelity(
        tmp_path, "offering.subscription.models_covered", [],
        "Features | Pro\nSupported models | None\n",
    )

    assert result.details[0]["outcome"] == "verified"
    assert result.counts["verified"] == 1


@pytest.mark.parametrize("unchanged_unread", [False, True])
@pytest.mark.parametrize(("field", "value"), [
    ("offering.subscription.usage_allowance", "10 tasks per day"),
    ("offering.subscription.programmatic_or_agent_use", "CLI access"),
])
def test_unrelated_card_feature_is_undetermined(
    tmp_path: Path, field: str, value: str, unchanged_unread: bool,
) -> None:
    _, result, queue, log = _fidelity(
        tmp_path, field, value, "Pro\n$20/month\nPriority support\n",
        unchanged_unread=unchanged_unread,
    )

    assert result.details[0]["outcome"] == "undetermined"
    assert result.counts["undetermined"] == 1
    assert queue.recrawl_requests() == []
    assert log.records() == []


@pytest.mark.parametrize("unchanged_unread", [False, True])
@pytest.mark.parametrize(("field", "value", "markup"), [
    ("offering.subscription.usage_allowance", "10 tasks per day",
     "<span>10 tasks per day</span>"),
    ("offering.subscription.programmatic_or_agent_use", "CLI access",
     "<p>CLI access</p>"),
])
def test_raw_inline_markup_is_undetermined(
    tmp_path: Path, field: str, value: str, markup: str, unchanged_unread: bool,
) -> None:
    _, result, queue, log = _fidelity(
        tmp_path, field, value, f"Pro\n$20/month\n{markup}\n",
        unchanged_unread=unchanged_unread,
    )

    assert result.details[0]["outcome"] == "undetermined"
    assert result.counts["undetermined"] == 1
    assert queue.recrawl_requests() == []
    assert log.records() == []


@pytest.mark.parametrize(("field", "value", "statement"), [
    ("offering.subscription.usage_allowance", "20 tasks per day", "10 tasks per day"),
    ("offering.subscription.programmatic_or_agent_use", "CLI access included",
     "CLI access is not included"),
])
def test_changed_card_fact_remains_a_mismatch(
    tmp_path: Path, field: str, value: str, statement: str,
) -> None:
    claim, result, queue, log = _fidelity(
        tmp_path, field, value, f"Pro\n$20/month\n{statement}\n",
    )

    assert result.details[0]["outcome"] == "mismatch"
    assert result.details[0]["diff"] == [{
        "field": "value", "expected": value, "found": statement,
    }]
    assert queue.recrawl_requests() == [(claim.target, "mismatch")]
    assert log.latest()[("fact", claim.target.id)].outcome == "mismatch"


@pytest.mark.parametrize("unchanged_unread", [False, True])
def test_unsupported_open_tool_list_is_undetermined(
    tmp_path: Path, unchanged_unread: bool,
) -> None:
    _, result, queue, log = _fidelity(
        tmp_path, "offering.subscription.surfaces",
        ["coding_tool:claude-code", "coding_tool:*"],
        "Lab Pro includes Claude Code and other coding tools.\n",
        unchanged_unread=unchanged_unread,
    )

    assert result.details[0]["outcome"] == "undetermined"
    assert result.counts["undetermined"] == 1
    assert queue.recrawl_requests() == []
    assert log.records() == []


@pytest.mark.parametrize("unchanged_unread", [False, True])
def test_absent_coverage_quote_is_undetermined(
    tmp_path: Path, unchanged_unread: bool,
) -> None:
    _, result, queue, log = _fidelity(
        tmp_path, "offering.subscription.coverage_quote", "Pro includes GPT-6 Sol.",
        "Pro\n$20/month\nPriority support\n", unchanged_unread=unchanged_unread,
    )

    assert result.details[0]["outcome"] == "undetermined"
    assert result.counts["undetermined"] == 1
    assert queue.recrawl_requests() == []
    assert log.records() == []


def test_changed_closed_tool_list_remains_a_mismatch(tmp_path: Path) -> None:
    claim, result, queue, log = _fidelity(
        tmp_path, "offering.subscription.surfaces", ["coding_tool:claude-code"],
        "Lab Pro includes Codex CLI.\n",
    )

    assert result.details[0]["outcome"] == "mismatch"
    assert result.details[0]["diff"] == [{
        "field": "value", "expected": ["coding_tool:claude-code"],
        "found": "coding_tool:codex-cli",
    }]
    assert queue.recrawl_requests() == [(claim.target, "mismatch")]
    assert log.latest()[("fact", claim.target.id)].outcome == "mismatch"
