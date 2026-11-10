"""Card-audit diagnostics for benchmark coverage.

The ranking candidate reader copies ``benchmarks.evidence`` into its score
map. The audit used to read only the legacy ``benchmarks.scores`` cache.
"""

from pathlib import Path
from tempfile import TemporaryDirectory

from pipeline.load import NOT_CONTENT
from pipeline.ranking import build_candidates
from schema.card import ModelCard
from schema.graph import CollectingSink
from scripts.audit_data_quality import audit_card, run_audit


def _evidence(benchmark_id="example_score", score=55, url="https://example.test/results"):
    return {
        "benchmark_id": benchmark_id,
        "model_id_as_evaluated": "Example",
        "score": score,
        "unit": "%",
        "source_url": url,
        "source_kind": "benchmark_author",
        "evidence_date": "2026-11-01",
        "date_type": "evaluated",
        "verified_at": "2026-11-01",
    }


def _card(scores=None, evidence=None, model_type="llm-chat"):
    return ModelCard.model_validate({
        "identity": {
            "model_id": "example/model",
            "display_name": "Example",
            "provider": "example",
            "model_type": model_type,
        },
        "benchmarks": {"scores": scores or {}, "evidence": evidence or []},
    })


def _benchmark_findings(card):
    return [item for item in audit_card(card, Path("example.md")) if item["field"] == "benchmarks"]


def _coverage_message(legacy_count, authored_count):
    return (
        f"Legacy cached scores: {legacy_count}. "
        f"Authored evidence records: {authored_count}. "
        "Evidence admission is not decided by this audit. "
        "Query qualification is not decided by this audit."
    )


def test_audit_does_not_call_evidence_only_model_scoreless():
    card = ModelCard.model_validate({
        "identity": {
            "model_id": "example/model",
            "display_name": "Example",
            "provider": "example",
            "model_type": "llm-chat",
        },
        "benchmarks": {"scores": {}, "evidence": [{
            "benchmark_id": "example_score",
            "model_id_as_evaluated": "Example",
            "score": 55,
            "unit": "%",
            "source_url": "https://example.test/results",
            "source_kind": "benchmark_author",
            "evidence_date": "2026-11-01",
            "date_type": "evaluated",
            "verified_at": "2026-11-01",
        }]},
    })
    candidates = build_candidates([card], CollectingSink())
    assert len(candidates) == 1
    assert candidates[0].benchmark_scores == {"example_score": 55.0}
    findings = audit_card(card, Path("example.md"))
    assert not any(item["field"] == "benchmarks" and item["category"] == "missing" for item in findings)
    coverage = _benchmark_findings(card)
    assert coverage == [{
        "model_id": "example/model",
        "provider": "example",
        "severity": "info",
        "category": "sparse",
        "field": "benchmarks",
        "message": _coverage_message(0, 1),
    }]
    assert "zero benchmark scores" not in coverage[0]["message"]
    assert "invisible" not in coverage[0]["message"]


def test_audit_distinguishes_cache_evidence_and_empty_benchmark_coverage():
    empty = _benchmark_findings(_card())
    cache_only = _benchmark_findings(_card(scores={"example_score": 40}))
    evidence_only = _benchmark_findings(_card(evidence=[_evidence()]))
    both = _benchmark_findings(_card(scores={"cached_score": 10}, evidence=[_evidence()]))

    assert [item["category"] for item in empty] == ["missing"]
    assert empty[0]["message"] == _coverage_message(0, 0)
    assert cache_only[0]["message"] == _coverage_message(1, 0)
    assert evidence_only[0]["message"] == _coverage_message(0, 1)
    assert both[0]["message"] == _coverage_message(1, 1)
    assert len({item["message"] for item in (*empty, *cache_only, *evidence_only, *both)}) == 4
    for item in (*empty, *cache_only, *evidence_only, *both):
        assert "invisible" not in item["message"]
        assert "rank poorly" not in item["message"]


def test_audit_legacy_filled_count_stays_on_the_score_cache():
    card = _card(scores={"cached_score": 10}, evidence=[_evidence(), _evidence("other_score", 20)])
    assert card.benchmarks.filled_count() == 1
    assert _benchmark_findings(card) == []
    overlapping = _card(scores={"example_score": 10}, evidence=[_evidence(), _evidence("other_score", 20)])
    assert overlapping.benchmarks.filled_count() == 1
    assert _benchmark_findings(overlapping)[0]["message"] == _coverage_message(1, 2)


def test_audit_does_not_treat_evidence_arena_as_absent():
    card = _card(scores={"cached_score": 10}, evidence=[_evidence("arena_elo_overall", 1200)])
    findings = audit_card(card, Path("example.md"))
    assert not any(item["field"] == "arena_elo_overall" for item in findings)


def test_audit_still_notes_arena_absent_from_cache_and_evidence():
    card = _card(scores={"cached_score": 10})
    findings = [item for item in audit_card(card, Path("example.md")) if item["field"] == "arena_elo_overall"]
    assert findings == [{
        "model_id": "example/model",
        "provider": "example",
        "severity": "info",
        "category": "missing",
        "field": "arena_elo_overall",
        "message": (
            "Legacy cached scores and authored evidence records do not include arena_elo_overall. "
            "Query qualification is not decided by this audit."
        ),
    }]


def test_audit_notes_arena_absent_from_an_evidence_only_card():
    card = _card(evidence=[_evidence()])
    assert card.benchmarks.scores == {}
    assert card.benchmarks.filled_count() == 0
    findings = [item for item in audit_card(card, Path("example.md")) if item["field"] == "arena_elo_overall"]
    assert findings == [{
        "model_id": "example/model",
        "provider": "example",
        "severity": "info",
        "category": "missing",
        "field": "arena_elo_overall",
        "message": (
            "Legacy cached scores and authored evidence records do not include arena_elo_overall. "
            "Query qualification is not decided by this audit."
        ),
    }]


def test_audit_does_not_note_arena_when_the_legacy_cache_holds_it():
    card = _card(scores={"cached_score": 10, "arena_elo_overall": 1200})
    assert card.benchmarks.evidence == []
    findings = audit_card(card, Path("example.md"))
    assert not any(item["field"] == "arena_elo_overall" for item in findings)


def test_audit_skips_benchmark_and_arena_notes_for_image_generation():
    empty = _card(model_type="image-generation")
    assert empty.benchmarks.scores == {}
    assert empty.benchmarks.evidence == []
    empty_findings = audit_card(empty, Path("example.md"))
    assert not any(item["field"] == "benchmarks" for item in empty_findings)
    assert not any(item["field"] == "arena_elo_overall" for item in empty_findings)
    scored = _card(scores={"cached_score": 10}, model_type="image-generation")
    assert scored.benchmarks.evidence == []
    scored_findings = audit_card(scored, Path("example.md"))
    assert not any(item["field"] == "benchmarks" for item in scored_findings)
    assert not any(item["field"] == "arena_elo_overall" for item in scored_findings)


def _write_card(directory, relative, text):
    path = directory / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


_VALID_CARD = (
    "model_id: acme/ok\n"
    "display_name: Ok\n"
    "provider: acme\n"
    "model_type: llm-chat\n"
)
_OTHER_CARD = (
    "model_id: other/ok\n"
    "display_name: Ok\n"
    "provider: other\n"
    "model_type: llm-chat\n"
)
_BROKEN_CARD = (
    "model_id: acme/broken\n"
    "display_name: Broken\n"
    "provider: acme\n"
    "model_type: not-a-type\n"
)
_VALID_FINDINGS = [
    ("total_parameters", "missing"),
    ("context_window", "missing"),
    ("benchmarks", "missing"),
    ("cost_input", "missing"),
    ("release_date", "missing"),
]


def test_audit_ignores_noncontent_documents():
    with TemporaryDirectory() as directory:
        root = Path(directory)
        for name in sorted(NOT_CONTENT):
            (root / name).write_text("Catalogue licence notice.\n")
            _write_card(root, f"acme/{name}", "Catalogue licence notice.\n")
        assert run_audit(root) == []
        _write_card(root, "acme/broken.md", _BROKEN_CARD)
        findings = run_audit(root)
    assert [(item["field"], item["category"]) for item in findings] == [("yaml", "parse")]
    assert findings[0]["model_id"] == "acme/broken.md"


def test_audit_reads_a_card_whose_file_name_is_all_capitals():
    capitals = _VALID_CARD.replace("model_id: acme/ok", "model_id: acme/GPT")
    with TemporaryDirectory() as directory:
        root = Path(directory)
        _write_card(root, "acme/ok.md", _VALID_CARD)
        _write_card(root, "acme/GPT.md", capitals)
        findings = run_audit(root)
    lower = [(item["field"], item["category"]) for item in findings if item["model_id"] == "acme/ok"]
    upper = [(item["field"], item["category"]) for item in findings if item["model_id"] == "acme/GPT"]
    assert lower == _VALID_FINDINGS
    assert upper == _VALID_FINDINGS


def test_audit_skips_a_noncontent_name_whose_body_parses_as_a_card():
    with TemporaryDirectory() as directory:
        root = Path(directory)
        for name in sorted(NOT_CONTENT):
            (root / name).write_text(_VALID_CARD)
        assert run_audit(root) == []


def test_audit_provider_filter_keeps_valid_card_findings():
    with TemporaryDirectory() as directory:
        root = Path(directory)
        (root / "LICENSE.md").write_text("Catalogue licence notice.\n")
        _write_card(root, "acme/ok.md", _VALID_CARD)
        _write_card(root, "acme/broken.md", _BROKEN_CARD)
        _write_card(root, "other/ok.md", _OTHER_CARD)
        filtered = run_audit(root, "acme")
        ok = [item for item in filtered if item["model_id"] == "acme/ok"]
        assert [(item["field"], item["category"]) for item in ok] == _VALID_FINDINGS
        assert [item["model_id"] for item in filtered if item["category"] == "parse"] == ["acme/broken.md"]
        assert not any(item["model_id"] == "other/ok" for item in filtered)
        assert not any(item["model_id"] == "LICENSE.md" for item in filtered)


def test_three_authored_evidence_records_are_not_a_scoreless_finding():
    evidence = [_evidence(benchmark_id=f"score_{index}", score=50 + index) for index in range(3)]
    card = _card(evidence=evidence)
    assert card.benchmarks.filled_count() == 0
    assert _benchmark_findings(card) == []
    candidate = build_candidates([card], CollectingSink())[0]
    assert candidate.benchmark_scores == {f"score_{index}": float(50 + index) for index in range(3)}
