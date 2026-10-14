"""A nightly re-read cannot infer licence disagreement from missing source metadata."""

from dataclasses import replace
from datetime import date
from pathlib import Path

import pytest

from decision.model import Source, SourceRef, TargetRef, VerificationActor
from decision.sources import CopyStore
from decision.verify import (
    Claim,
    KeyValueExtractor,
    Queue,
    StoredRegions,
    VerificationLog,
    deterministic_extractors,
    verify,
)
from scripts.accuracy import verify_fidelity_sample


TODAY = date(2026, 10, 13)


def _licence_case(tmp_path: Path, kind: str | None = None):
    source = Source(
        id="fixture-licence",
        url="https://example.test/fixture-licence",
        kind=kind,
        normaliser="text-default",
        cited_regions=[{"id": "page", "locator": {"kind": "page", "value": ""}}],
    )
    store = CopyStore(tmp_path / "copies")
    copy_ref = store.put(b"Licence for Fixture Model.\nUse requires permission.\n")
    claim = Claim(
        target=TargetRef(kind="fact", id="fixture/model#licence.user_cap"),
        subject="fixture/model",
        names=("Fixture Model",),
        field="licence.user_cap",
        value=None,
        collector=VerificationActor(agent="fixture", model_family="gpt", method="read"),
        sources=(SourceRef(
            source_id=source.id, snapshot_ref=copy_ref, cited_regions=["page"],
        ),),
    )
    return claim, StoredRegions(store, {source.id: source})


@pytest.mark.parametrize(
    ("unread_reason", "expected_reason"),
    [("source_changed", "source_changed"), ("mismatch", "source_unchanged")],
    ids=["changed-source", "same-bytes"],
)
def test_missing_licence_source_kind_is_undetermined(
    tmp_path: Path, unread_reason: str, expected_reason: str,
) -> None:
    claim, regions = _licence_case(tmp_path)
    queue = Queue(tmp_path / "verification")
    log = VerificationLog(tmp_path / "verification")

    result = verify_fidelity_sample(
        [claim], regions=regions, extractors=deterministic_extractors(),
        queue=queue, log=log, today=TODAY,
        source_urls={"fixture-licence": "https://example.test/fixture-licence"},
        unread={("fact", claim.target.id): unread_reason},
    )

    assert result.details[0]["outcome"] == "undetermined"
    assert result.details[0]["reason"] == expected_reason
    assert result.counts == {
        "verified": 0, "mismatch": 0, "unreachable": 0,
        "undetermined": 1, "public_image_lag": 0,
    }
    assert log.latest() == {}
    assert queue.recrawl_requests() == []


def test_core_verification_refuses_licence_absence_without_source_kind(tmp_path: Path) -> None:
    claim, regions = _licence_case(tmp_path)

    result = verify(claim, regions, deterministic_extractors(), today=TODAY)

    assert result.outcome == "mismatch"
    assert [diff.to_dict() for diff in result.diffs] == [{
        "field": "source_kind", "expected": ["licence_text", "provider_terms"],
        "found": "unknown",
    }]


@pytest.mark.parametrize("unread_reason", ["source_changed", "mismatch"])
def test_known_disallowed_licence_source_kind_remains_mismatch(
    tmp_path: Path, unread_reason: str,
) -> None:
    claim, regions = _licence_case(tmp_path, kind="weights_repository")
    queue = Queue(tmp_path / "verification")
    log = VerificationLog(tmp_path / "verification")

    result = verify_fidelity_sample(
        [claim], regions=regions, extractors=deterministic_extractors(),
        queue=queue, log=log, today=TODAY,
        source_urls={"fixture-licence": "https://example.test/fixture-licence"},
        unread={("fact", claim.target.id): unread_reason},
    )

    assert result.details[0]["outcome"] == "mismatch"
    assert result.details[0]["diff"] == [{
        "field": "source_kind", "expected": ["licence_text", "provider_terms"],
        "found": "weights_repository",
    }]
    assert queue.recrawl_requests() == [(claim.target, "mismatch")]
    assert log.latest()[("fact", claim.target.id)].outcome == "mismatch"


def test_missing_metadata_does_not_hide_a_value_disagreement(tmp_path: Path) -> None:
    claim, regions = _licence_case(tmp_path)
    copy_ref = regions.store.put(b"Model: Fixture Model\ncontext: 20\n")
    claim = replace(
        claim, target=TargetRef(kind="fact", id="fixture/model#model.context_window"),
        field="context", value=10,
        sources=(claim.sources[0].model_copy(update={"snapshot_ref": copy_ref}),),
    )
    queue = Queue(tmp_path / "verification")
    log = VerificationLog(tmp_path / "verification")

    result = verify_fidelity_sample(
        [claim], regions=regions, extractors=[KeyValueExtractor()],
        queue=queue, log=log, today=TODAY,
        source_urls={"fixture-licence": "https://example.test/fixture-licence"},
    )

    assert result.details[0]["outcome"] == "mismatch"
    assert result.details[0]["diff"] == [{
        "field": "value", "expected": "10", "found": "20",
    }]
    assert queue.recrawl_requests() == [(claim.target, "mismatch")]
    assert log.latest()[("fact", claim.target.id)].outcome == "mismatch"
