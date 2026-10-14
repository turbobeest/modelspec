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


def _claim(field: str, value: list[str]) -> verify.Claim:
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


def _fidelity(tmp_path: Path, field: str, value: list[str], page: str):
    claim = _claim(field, value)
    queue = verify.Queue(tmp_path / "verification")
    log = verify.VerificationLog(tmp_path / "verification")
    result = accuracy.verify_fidelity_sample(
        [claim], regions=_Regions(page), extractors=verify.deterministic_extractors(),
        queue=queue, log=log, today=date(2026, 10, 13),
        source_urls={"plans": "https://example.test/plans"},
    )
    return claim, result, queue, log


@pytest.mark.parametrize("page", [
    "Pro\n$20/month\n"
    "Pro includes broad model choice, command-line tools, and editor integrations.\n",
    "Features | Pro\nSupported models | A selection of leading models\n",
    "Features | Pro\nSupported models | <div>Model selector unavailable</div>\n",
])
def test_unidentified_model_list_is_undetermined(tmp_path: Path, page: str) -> None:
    _, result, queue, log = _fidelity(
        tmp_path, "offering.subscription.models_covered", ["openai/gpt-6-sol"], page,
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


def test_unsupported_open_tool_list_is_undetermined(tmp_path: Path) -> None:
    _, result, queue, log = _fidelity(
        tmp_path, "offering.subscription.surfaces",
        ["coding_tool:claude-code", "coding_tool:*"],
        "Lab Pro includes Claude Code and other coding tools.\n",
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
