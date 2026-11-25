"""An effort word that is part of a card's own name is not an effort (MODEL-568).

"Mistral Medium" is a model, not Mistral at medium effort. The verifier read the
last word as an effort label and refused every Arena row for such a card. A
word belongs to the name when the subject spells one of the card's registered
names (or the first words of one) and the subject without the word is none of
them. Real effort labels, "(xHigh)", " high", "_max", parse as before. Names
and numbers are invented, except the published "Mistral Medium" spelling.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from decision import verify
from decision.model import DETERMINISTIC, SourceRef, TargetRef, VerificationActor
from scripts import refresh_leaderboards as refresh
from tests.test_leaderboard_refresh import (
    _ARENA_DATASET,
    _ARENA_NEW,
    _arena_registry,
    _evidence_row,
    _verification_log,
)

_COLLECTOR = VerificationActor(agent="fixture-collector", model_family="fixture",
                               method="fixture@1")


def _claim(names: tuple[str, ...], effort: str | None = None, value: float = 1200.0):
    return verify.Claim(
        target=TargetRef(kind="evidence", id="lab/fixture#arena_elo_overall#x"),
        subject="lab/fixture",
        names=names,
        field="arena_elo_overall",
        label="rating",
        value=value,
        unit="Arena score (Elo scale)",
        conditions={"effort": effort, "harness": None, "date": None},
        collector=_COLLECTOR,
        sources=(SourceRef(source_id="fixture", snapshot_ref="sha256:" + "a" * 64,
                           cited_regions=["rows"]),),
    )


def _region(*rows: tuple[str, float]) -> str:
    return json.dumps({"rows": [{"model_name": name, "rating": rating} for name, rating in rows]})


def _compare(claim, region: str):
    readings = verify.StructuredDataExtractor().extract(claim, region)
    return verify.compare(claim, readings)


# --- the word test -------------------------------------------------------------------------------

_MEDIUM_NAMES = ("Mistral Medium", "Mistral Medium (latest)", "mistral-medium-latest")


def test_mistral_medium_names_no_effort() -> None:
    assert verify.effort_word_is_name("Mistral Medium", _MEDIUM_NAMES)
    assert verify.structured_name_effort("Mistral Medium", _MEDIUM_NAMES) is None
    # The first words of a registered name are enough: "(latest)" is that card's.
    assert verify.structured_name_effort("Mistral Medium", ("Mistral Medium (latest)",)) is None


def test_without_names_the_old_reading_stands() -> None:
    """No registered names, no decision: callers that pass none read as before."""
    assert verify.structured_name_effort("Mistral Medium") == "Medium"
    assert verify.effort_word_is_name("Mistral Medium", ()) is False


@pytest.mark.parametrize("name", [
    "Example Large", "Example Small", "Example Mini", "Example Pro",
    "Example Large 2", "Example Pro Preview",
])
def test_size_and_tier_words_are_never_efforts(name: str) -> None:
    assert verify.structured_name_effort(name, (name,)) is None
    assert verify.structured_name_effort(name) is None


@pytest.mark.parametrize("name", ["Example Max", "Example High", "Example 3 Max", "Example Pro Max"])
def test_max_and_high_in_the_card_name_are_the_name(name: str) -> None:
    slug = name.lower().replace(" ", "-")
    assert verify.structured_name_effort(name, (name, slug)) is None
    assert verify.structured_name_effort(name, (slug,)) is None


@pytest.mark.parametrize(("subject", "names", "effort"), [
    ("Example Model (xHigh)", ("Example Model",), "xHigh"),
    # A parenthesis is a qualifier even when the label itself is registered.
    ("Example Model (xHigh)", ("Example Model (xHigh)", "Example Model"), "xHigh"),
    ("Example Max (High)", ("Example Max",), "High"),
    ("Example Model high", ("Example Model high", "Example Model", "example-model"), "high"),
    ("Example Model - Max", ("Example Model - Max", "Example Model"), "Max"),
    ("example-model_max", ("example-model_max", "example-model"), "max"),
    ("example-model-2026-01-01_high", ("example-model-2026-01-01_high",), "high"),
    ("Other Model low", ("Example Model",), "low"),
])
def test_real_effort_labels_still_parse(subject: str, names: tuple[str, ...], effort: str) -> None:
    assert verify.structured_name_effort(subject, names) == effort
    assert verify.structured_name_effort(subject) == effort


def test_a_hyphen_is_still_not_a_separator() -> None:
    assert verify.structured_name_effort("example-model-max", ("example-model",)) is None


def test_the_writer_reads_parenthesised_efforts_as_before() -> None:
    assert refresh._name_effort("Example Model (xHigh)") == "xhigh"
    assert refresh._name_effort("Example Model (max effort)") == "max"
    assert refresh._name_effort("Mistral Medium") is None


# --- the verifier --------------------------------------------------------------------------------


def test_the_verifier_owns_a_mistral_medium_row_without_an_effort() -> None:
    claim = _claim(_MEDIUM_NAMES)
    region = _region(("Mistral Medium", 1200.0), ("Mistral Large", 1250.0))
    assert _compare(claim, region) == []


def test_the_verifier_still_checks_the_score_of_a_name_word_row() -> None:
    claim = _claim(_MEDIUM_NAMES, value=1300.0)
    diffs = _compare(claim, _region(("Mistral Medium", 1200.0)))
    assert diffs
    assert all(d.field in ("value", "unit") for d in diffs), diffs


def test_the_verifier_still_reads_a_spaced_effort_on_the_cards_name() -> None:
    """ "Example Model high" for the card "Example Model": high is an effort."""
    names = ("Example Model high", "Example Model", "example-model")
    region = _region(("Example Model high", 1200.0))
    assert _compare(_claim(names, effort="high"), region) == []
    diffs = _compare(_claim(names), region)
    assert [(d.field, d.found) for d in diffs] == [("effort", "high")]


def test_the_verifier_still_reads_a_parenthesised_effort() -> None:
    names = ("Example Model (xHigh)", "Example Model")
    region = _region(("Example Model (xHigh)", 1200.0))
    assert _compare(_claim(names, effort="xhigh"), region) == []
    assert [d.field for d in _compare(_claim(names), region)] == ["effort"]


# --- the weekly refresh --------------------------------------------------------------------------

_MODEL = "lab/example-medium"


def _run(monkeypatch, tmp_path: Path, *, display: str, evaluated: str, version: str,
         effort: str | None = None):
    """One invented Arena card through ``refresh.run``. No network."""
    root = tmp_path / "repo"
    cache = tmp_path / "copies"
    source_id = "fixture-arena"
    card = root / "models" / "lab" / "model.md"
    card.parent.mkdir(parents=True)
    card.write_text(
        f"""---
model_id: {_MODEL}
display_name: {json.dumps(display)}
version: {version}
benchmarks:
  evidence:
  - benchmark_id: arena_elo_overall
    model_id_as_evaluated: {json.dumps(evaluated)}
    score: 1000.0
    unit: Arena score (Elo scale)
    interval: [990.0, 1010.0]
    n: 500
    effort: {"null" if effort is None else effort}
    source_url: {_ARENA_DATASET}
    source_kind: independent_evaluator
    evidence_date: '2026-10-01'
    date_type: published
    observed_at: '2026-10-01'
    verified_at: '2026-10-01'
    benchmark_version: text / overall, latest split, rating 1000
    configuration: >-
      Pinned LMArena dataset; publication date 2026-10-01; rating 1000.00
      [990.00, 1010.00], 500 votes, rank 40. Observed 2026-10-01.
    id: {_MODEL}#arena_elo_overall#old
    sources:
    - source_id: {source_id}
      snapshot_ref: sha256:{'a' * 64}
      cited_regions: [rows]
---
""",
        encoding="utf-8",
    )
    _arena_registry(root, source_id)
    (root / "verification").mkdir()
    url = f"{_ARENA_DATASET}/resolve/{_ARENA_NEW}/text/latest-00000-of-00001.parquet"
    rows = [{
        "model_name": evaluated, "rating": 1210.0, "rating_lower": 1204.0,
        "rating_upper": 1216.0, "vote_count": 4000,
        "leaderboard_publish_date": "2026-11-11", "rank": 30,
    }]
    projection = refresh.readers.document(
        rows, url=url, page_ref="sha256:" + "b" * 64, read_date="2026-11-11", note="fixture",
    )
    board = refresh._reading_from_projection(
        key="arena:text", source_id=source_id, benchmarks=("arena_elo_overall",),
        source_url=url, projected=projection, observed_at="2026-11-11",
        value_field="rating", store=refresh.CopyStore(cache), card_urls=(_ARENA_DATASET,),
    )
    monkeypatch.delenv(refresh.ARENA_REVISION_ENV, raising=False)
    monkeypatch.setattr(refresh.readers, "resolve_arena_revision",
                        lambda _fetch: refresh.readers.ArenaRevision(sha=_ARENA_NEW))
    monkeypatch.setattr(refresh, "collect_readings", lambda *_args, **_kwargs: ([board], []))
    before = tmp_path / "before"
    shutil.copytree(root, before)
    report = refresh.run(observed_at="2026-11-11", dry_run=False, root=root,
                         source_cache=cache, model_ids=(_MODEL,), arena_latest=True)
    return report, card, root, before


@pytest.mark.usefixtures("terms_register_present")
def test_the_refresh_does_not_adopt_a_name_word_as_effort(monkeypatch, tmp_path: Path) -> None:
    """Before MODEL-568 the refresh wrote effort medium onto an "Example Medium" row."""
    report, card, root, before = _run(
        monkeypatch, tmp_path, display="Example Medium (latest)",
        evaluated="Example Medium", version="example-medium-latest",
    )
    assert report.failures == [], report.failures
    row = _evidence_row(card)
    assert row["score"] == 1210.0
    assert row["effort"] is None
    assert _verification_log(root)["outcome"] == "verified"
    assert refresh.check_score_only(before, root).ok


@pytest.mark.usefixtures("terms_register_present")
def test_the_refresh_still_adopts_a_spaced_effort(monkeypatch, tmp_path: Path) -> None:
    """ "Example Model high" for the card "Example Model" is still read at high."""
    report, card, root, _before = _run(
        monkeypatch, tmp_path, display="Example Model",
        evaluated="Example Model high", version="example-model",
    )
    assert report.failures == [], report.failures
    row = _evidence_row(card)
    assert row["score"] == 1210.0
    assert row["effort"] == "high"
    assert _verification_log(root)["outcome"] == "verified"
