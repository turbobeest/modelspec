"""Open LLM Leaderboard v2 scores live under their own keys (MODEL-116).

OLL v2 reports "MATH Lvl 5" (the 1,324 level-5 problems of the MATH test
split) and "GPQA" (lm-eval's `leaderboard_gpqa`: Main, Extended and Diamond
pooled). Neither is MATH-500 or GPQA Diamond, so the enrichment scripts must
never write `math_500` or `gpqa_diamond`, and no card may keep one there.
"""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

import yaml

from schema.card import ModelCard, Identity
from scripts import enrich_open_llm, enrich_v2_benchmarks

ROOT = Path(__file__).resolve().parents[1]
MISLABELLED = {"math_500", "gpqa_diamond"}
OLL_KEYS = {"math_lvl5", "gpqa_pooled"}


def _card() -> ModelCard:
    return ModelCard(identity=Identity(model_id="example/tiny-7b", display_name="Tiny 7B", provider="example"))


def _front_matter(path: Path) -> dict:
    match = re.match(r"^---\n(.*?)\n---", path.read_text(encoding="utf-8"), re.S)
    return yaml.safe_load(match.group(1)) if match else {}


@lru_cache(maxsize=1)
def _cards() -> tuple[tuple[Path, dict], ...]:
    return tuple((p, _front_matter(p)) for p in sorted((ROOT / "models").rglob("*.md")) if p.name != "LICENSE.md")


def test_v2_enrichment_writes_the_oll_keys() -> None:
    card = _card()
    row = {"ifeval": 50.0, "bbh": 40.0, "math_lvl5": 12.3, "gpqa_pooled": 30.1, "musr": 41.0, "mmlu_pro": 25.0}
    matcher = enrich_v2_benchmarks.V2Matcher({"example/tiny-7b": row})

    modified, filled = enrich_v2_benchmarks.enrich_card(card, matcher)

    assert modified
    assert card.benchmarks.scores["math_lvl5"] == 12.3
    assert card.benchmarks.scores["gpqa_pooled"] == 30.1
    assert not MISLABELLED & set(card.benchmarks.scores)
    assert not MISLABELLED & set(filled)


def test_v2_enrichment_renames_legacy_extraction_keys() -> None:
    """The extracted JSON written before MODEL-116 used the wrong keys."""
    legacy = {"example/tiny-7b": {"math_500": 12.3, "gpqa_diamond": 30.1, "bbh": 40.0}}

    canonical = enrich_v2_benchmarks.canonical_scores(legacy)

    assert canonical == {"example/tiny-7b": {"math_lvl5": 12.3, "gpqa_pooled": 30.1, "bbh": 40.0}}


def test_v2_enrichment_key_list_names_the_oll_keys() -> None:
    assert OLL_KEYS <= set(enrich_v2_benchmarks.V2_BENCHMARKS)
    assert not MISLABELLED & set(enrich_v2_benchmarks.V2_BENCHMARKS)
    assert enrich_v2_benchmarks.OLL_V2_COLUMNS["MATH Lvl 5"] == "math_lvl5"
    assert enrich_v2_benchmarks.OLL_V2_COLUMNS["GPQA"] == "gpqa_pooled"


def test_open_llm_enrichment_maps_dataset_columns_to_the_oll_keys() -> None:
    rows = {"rows": [{"row": {"fullname": "example/tiny-7b", "MATH Lvl 5": 12.3, "GPQA": 30.1, "BBH": 40.0}}]}

    parsed = enrich_open_llm._parse_dataset_response(rows)

    (scores,) = parsed.values()
    assert scores == {"math_lvl5": 12.3, "gpqa_pooled": 30.1, "bbh": 40.0}


def test_open_llm_enrichment_maps_gradio_columns_to_the_oll_keys() -> None:
    # [name, average, mmlu_pro, gpqa, bbh, ifeval, math, musr]
    data = {"data": [["example/tiny-7b", 30.0, 25.0, 30.1, 40.0, 50.0, 12.3, 41.0]]}

    (scores,) = enrich_open_llm._parse_gradio_response(data).values()

    assert scores["math_lvl5"] == 12.3
    assert scores["gpqa_pooled"] == 30.1
    assert not MISLABELLED & set(scores)


def test_open_llm_enrichment_never_writes_the_mislabelled_keys() -> None:
    assert not MISLABELLED & set(enrich_open_llm.OPEN_LLM_V2_BENCHMARKS)
    assert OLL_KEYS <= set(enrich_open_llm.OPEN_LLM_V2_BENCHMARKS)


def test_open_llm_enrichment_has_no_curated_scores() -> None:
    """The hand-typed table did not match the dataset it named (MODEL-116)."""
    assert not hasattr(enrich_open_llm, "OPEN_LLM_V2")


def test_oll_keys_have_benchmark_pages() -> None:
    math = _front_matter(ROOT / "benchmarks" / "math_lvl5.md")
    gpqa = _front_matter(ROOT / "benchmarks" / "gpqa_pooled.md")

    assert math["id"] == "math_lvl5"
    assert math["dataset"]["size"] == 1324
    assert math["lineage"]["family"] == "math"
    assert gpqa["id"] == "gpqa_pooled"
    assert gpqa["lineage"]["family"] == "gpqa"
    assert gpqa["harness"]["lm_eval"] == "leaderboard_gpqa"


def test_cards_with_oll_keys_cite_the_leaderboard() -> None:
    offenders = [
        str(p.relative_to(ROOT))
        for p, fm in _cards()
        if OLL_KEYS & set(((fm.get("benchmarks") or {}).get("scores") or {}))
        and "open-llm-leaderboard-v2" not in ((fm.get("benchmarks") or {}).get("benchmark_source") or "")
    ]
    assert offenders == []


def test_no_card_keeps_an_oll_value_under_the_mislabelled_keys() -> None:
    """Every card that took these keys from OLL v2 had its flat scores
    written by the scrape (MODEL-116 PR body lists them). The notes that
    flagged the overlap during MODEL-125 are rewritten once it is fixed."""
    offenders = []
    for p, fm in _cards():
        notes = (fm.get("benchmarks") or {}).get("benchmark_notes") or ""
        if re.search(r"(math_500|gpqa_diamond) holds the Open LLM Leaderboard", notes):
            offenders.append(str(p.relative_to(ROOT)))
    assert offenders == []


def test_leaderboard_only_cards_carry_no_mislabelled_flat_score() -> None:
    """A card whose flat scores come only from the Open LLM Leaderboard has no
    source for MATH-500 or GPQA Diamond."""
    offenders = []
    for p, fm in _cards():
        b = fm.get("benchmarks") or {}
        sources = {s.strip() for s in (b.get("benchmark_source") or "").split(",") if s.strip()}
        if sources and sources <= {"open-llm-leaderboard-v1", "open-llm-leaderboard-v2"}:
            if MISLABELLED & set(b.get("scores") or {}):
                offenders.append(str(p.relative_to(ROOT)))
    assert offenders == []


#: Exact zeros checked at source. Each is a real score from a run that
#: produced non-zero results on its other tasks, so it stays.
CONFIRMED_ZEROS = {
    ("models/google/mt5-small.md", "math_lvl5"),
    ("models/microsoft/dialogpt-medium.md", "math_lvl5"),
}


def test_every_exact_zero_score_is_confirmed_at_source() -> None:
    zeros = {
        (str(p.relative_to(ROOT)), key)
        for p, fm in _cards()
        for key, value in (((fm.get("benchmarks") or {}).get("scores")) or {}).items()
        if value == 0
    }
    assert zeros == CONFIRMED_ZEROS
