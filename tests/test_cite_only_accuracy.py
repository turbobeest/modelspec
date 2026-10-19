"""Nightly fidelity reports citations without claiming a successful verification."""

from dataclasses import replace
from datetime import UTC, date, datetime

import pytest
from typer.testing import CliRunner

from decision.model import Source
from decision.sources import CopyStore, FetchResult
from decision.verify import Queue, VerificationLog
from scripts import accuracy
from tests.test_cite_only_verification import CITE_URL, CiteRegions, claim


@pytest.mark.parametrize("private_correction", [False, True])
def test_fidelity_cite_only_remains_cited_without_verification_or_private_upgrade(
    tmp_path, private_correction,
):
    request = claim()
    key = (request.target.kind, request.target.id)
    queue, log = Queue(tmp_path), VerificationLog(tmp_path)
    corrections = ({key: (replace(request, value=64000), date(2026, 9, 1), date(2026, 10, 1))}
                   if private_correction else None)
    result = accuracy.verify_fidelity_sample(
        [request], regions=CiteRegions(), extractors=(), queue=queue, log=log,
        today=date(2026, 10, 19), source_urls={"src-lab-docs": CITE_URL},
        unread={key: "source_unchanged"}, private_corrections=corrections,
    )
    assert result.counts["cited"] == 1
    assert result.counts["verified"] == result.counts["public_image_lag"] == 0
    assert result.details[0]["outcome"] == "cited"
    assert result.details[0]["verifier"] is None
    assert "not machine-verified" in result.summary
    assert not log.records()
    assert queue.recrawl_requests() == []


def test_fidelity_citations_do_not_count_as_assessed_or_dilute_unknown_share():
    config = accuracy.load_config().data_fidelity
    counts = dict.fromkeys(accuracy.FIDELITY_OUTCOMES, 0)
    counts.update(verified=2, undetermined=2, cited=20)
    status, summary, share = accuracy.fidelity_verdict(counts, drawn=24, wanted=12, config=config)
    assert status == "fail"
    assert share == 0.5
    assert "Only 2 of 12" in summary
    assert "20" in summary and "not machine-verified" in summary


def test_fidelity_fetch_preserves_hash_date_and_redirect_origin(tmp_path):
    source = Source(id="src-lab-docs", url="https://example.org/redirect", normaliser="text-default",
                    cited_regions=[{"id": "r1", "locator": {"kind": "page", "value": ""}}])

    class Fetcher:
        def fetch(self, *_args, **_kwargs):
            return FetchResult("ok", 200, body=b"synthetic source content",
                               content_type="text/plain", resolved_urls=(CITE_URL,))

    store = CopyStore(tmp_path / "copies")
    diagnostics = {}
    current, _ = accuracy._current_copies(
        [(claim(), "fixture")], sources={source.id: source}, store=store, fetcher=Fetcher(),
        as_of=date(2026, 10, 19), nightly_methods=frozenset(), fetch_diagnostics=diagnostics,
    )
    ref = current[0].sources[0]
    assert ref.retrieved_at == datetime(2026, 10, 19, tzinfo=UTC)
    assert list(map(str, ref.resolved_urls)) == [CITE_URL]
    assert store.citation(ref.snapshot_ref) is not None
    assert not store.path(ref.snapshot_ref).exists()
    report = diagnostics[(current[0].target.kind, current[0].target.id)][0]
    assert report["retrieved_at"] == "2026-10-19T00:00:00+00:00"
    assert report["resolved_urls"] == [CITE_URL]


def test_verify_cli_does_not_call_a_cited_check_verified(tmp_path, monkeypatch):
    from cli.modelspec.verify_cmd import app

    (tmp_path / "registry").mkdir()
    (tmp_path / "registry" / "sources.yaml").write_text(
        "schema_version: 1\nsources:\n- id: src-lab-docs\n  url: " + CITE_URL + "\n")
    Queue(tmp_path / "verification").file(claim(), at=datetime(2026, 10, 19, tzinfo=UTC))
    monkeypatch.setenv("MODELSPEC_SOURCE_CACHE", str(tmp_path / "copies"))
    result = CliRunner().invoke(app, ["--root", str(tmp_path)])
    assert result.exit_code == 0, result.output
    assert "cited: 1" in result.output
    assert "Verified what was" not in result.output
