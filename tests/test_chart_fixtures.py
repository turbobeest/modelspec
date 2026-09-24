"""Release-chart fixtures must be readable, and a mismatched bar fails CI.

The check compares a chart we transcribed with the evidence rows on the cards.
It does not change the export. A ``known_mismatch`` mark keeps a known bad bar
from failing the run, and a mark that now matches is stale.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from pipeline.load import Model
from scripts.chart_check import (
    apply_second_reading,
    classify_fixtures,
    fixture_errors,
    load_fixture,
    load_fixtures,
    load_manifest,
    load_models,
    mismatch_errors,
    parse_score,
    reconcile_readings,
    tolerance_for,
)

ROOT = Path(__file__).resolve().parents[1]
CHARTS = ROOT / "benchmarks" / "_charts"
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg", ".avif"}


def _model(model_id: str, evidence: list[dict], scores: dict | None = None) -> Model:
    return Model(
        model_id,
        Path(model_id),
        {"model_id": model_id, "benchmarks": {"evidence": evidence, "scores": scores or {}}},
        "",
    )


def _bar(**overrides) -> dict:
    bar = {
        "model_as_labelled": "GPT-6 Astra",
        "model_id": "openai/gpt-6-astra",
        "benchmark_id": "gpqa_diamond",
        "score": 96.0,
        "score_text": "96.0",
        "unit": "percent",
        "printed": True,
        "configuration": "max effort",
        "role": "subject",
    }
    bar.update(overrides)
    return bar


def _page(bars: list[dict], **chart_over) -> dict:
    chart = {
        "title": "Example",
        "competitor_numbers": "vendor_run",
        "readings": [{"reader": "test", "date": "2026-09-24"}],
        "bars": bars,
        "kind": "html_table",
    }
    chart.update(chart_over)
    return {
        "page_url": "https://openai.com/index/gpt-6-astra/",
        "publisher": "OpenAI",
        "charts": [chart],
        "_slug": "example",
    }


def _row(score: float, source: str = "https://openai.com/index/gpt-6-astra", **extra) -> dict:
    row = {
        "benchmark_id": "gpqa_diamond",
        "score": score,
        "unit": "percent",
        "source_url": source,
        "configuration": "max effort",
    }
    row.update(extra)
    return row


def test_tolerance_is_half_the_printed_step():
    assert tolerance_for("78.2") == 0.05
    assert tolerance_for("78") == 0.5
    assert tolerance_for("78.20") == 0.005


def test_subject_bar_matches_same_source_within_precision():
    report = classify_fixtures(
        [_page([_bar()])],
        [_model("openai/gpt-6-astra", [_row(96.04)])],
    )
    assert report["charts_detail"][0]["bars"][0]["status"] == "matched"
    assert report["charts_detail"][0]["flags"] == ["single_read"]


def test_subject_bar_mismatches_outside_precision():
    report = classify_fixtures(
        [_page([_bar()])],
        [_model("openai/gpt-6-astra", [_row(90.0)])],
    )
    bar = report["charts_detail"][0]["bars"][0]
    assert bar["status"] == "mismatched"
    assert bar["held"]["score"] == 90.0


def test_trailing_slash_is_the_same_source():
    report = classify_fixtures(
        [_page([_bar()])],
        [_model("openai/gpt-6-astra", [_row(96.0, source="https://openai.com/index/gpt-6-astra/")])],
    )
    assert report["charts_detail"][0]["bars"][0]["status"] == "matched"


def test_subject_bar_not_held_names_another_source():
    report = classify_fixtures(
        [_page([_bar()])],
        [_model("openai/gpt-6-astra", [_row(91.0, source="https://example.com/other")])],
    )
    bar = report["charts_detail"][0]["bars"][0]
    assert bar["status"] == "not_held"
    assert bar["context"]["score"] == 91.0


def test_official_reports_against_an_independent_row_is_not_held():
    page = _page(
        [
            _bar(
                role="competitor",
                model_id="google/gemini-3-1-pro-preview",
                model_as_labelled="Gemini 3.1 Pro",
                score=94.3,
                score_text="94.3",
            )
        ],
        competitor_numbers="official_reports",
    )
    model = _model(
        "google/gemini-3-1-pro-preview",
        [
            _row(
                94.14,
                source="https://artificialanalysis.ai/leaderboards/models",
                source_kind="independent_evaluator",
                configuration="Artificial Analysis leaderboard",
            ),
            _row(
                91.0,
                source="https://example.com/author",
                source_kind="benchmark_author",
                configuration="author run",
            ),
        ],
    )
    bar = classify_fixtures([page], [model])["charts_detail"][0]["bars"][0]
    assert bar["status"] == "not_held"
    assert bar["context"] == [
        {
            "score": 94.14,
            "unit": "percent",
            "source_url": "https://artificialanalysis.ai/leaderboards/models",
            "configuration": "Artificial Analysis leaderboard",
            "source_kind": "independent_evaluator",
        },
        {
            "score": 91.0,
            "unit": "percent",
            "source_url": "https://example.com/author",
            "configuration": "author run",
            "source_kind": "benchmark_author",
        },
    ]


def test_official_reports_matches_a_provider_self_report():
    page = _page(
        [
            _bar(
                role="competitor",
                model_id="openai/gpt-6-astra",
                model_as_labelled="GPT-6 Astra",
                score=57.9,
                score_text="57.9",
            )
        ],
        competitor_numbers="official_reports",
    )
    model = _model(
        "openai/gpt-6-astra",
        [
            _row(
                57.9,
                source="https://artificialanalysis.ai/leaderboards/models",
                source_kind="independent_evaluator",
            ),
            _row(
                57.9,
                source="https://vendor.example/report",
                source_kind="provider_self_report",
                configuration="provider table",
            ),
        ],
    )
    bar = classify_fixtures([page], [model])["charts_detail"][0]["bars"][0]
    assert bar["status"] == "matched"
    assert bar["same_source"] is False
    assert bar["held"]["score"] == 57.9
    assert bar["held"]["source_url"] == "https://vendor.example/report"
    assert bar["held"]["configuration"] == "provider table"


def test_official_reports_mismatches_a_different_self_report():
    page = _page(
        [
            _bar(
                role="competitor",
                model_id="openai/gpt-6-astra",
                model_as_labelled="GPT-6 Astra",
            )
        ],
        competitor_numbers="official_reports",
    )
    model = _model(
        "openai/gpt-6-astra",
        [
            _row(
                96.0,
                source="https://artificialanalysis.ai/leaderboards/models",
                source_kind="independent_evaluator",
            ),
            _row(
                90.0,
                source="https://vendor.example/report",
                source_kind="provider_self_report",
            ),
        ],
    )
    bar = classify_fixtures([page], [model])["charts_detail"][0]["bars"][0]
    assert bar["status"] == "mismatched"
    assert bar["held"]["score"] == 90.0
    assert bar["held"]["source_url"] == "https://vendor.example/report"


def test_vendor_run_is_a_gap_even_when_the_numbers_agree():
    page = _page(
        [
            _bar(
                role="competitor",
                model_id="google/gemini-3-8-flash",
                model_as_labelled="Gemini 3.8 Flash",
            )
        ],
        competitor_numbers="vendor_run",
    )
    model = _model(
        "google/gemini-3-8-flash",
        [_row(96.0, source="https://example.com/card", configuration="card run")],
    )
    bar = classify_fixtures([page], [model])["charts_detail"][0]["bars"][0]
    assert bar["status"] == "competitor_gap"
    assert bar["gap"] == 0
    assert bar["held"]["configuration"] == "card run"


def test_unstated_competitor_stays_unresolved():
    page = _page(
        [_bar(role="competitor", model_id="google/gemini-3-8-flash")],
        competitor_numbers="unstated",
    )
    model = _model("google/gemini-3-8-flash", [_row(96.0, source="https://example.com/card")])
    report = classify_fixtures([page], [model])
    assert report["charts_detail"][0]["bars"][0]["status"] == "competitor_unresolved"


def test_missing_card_is_not_held():
    page = _page([_bar(model_id=None, role="competitor")])
    assert classify_fixtures([page], [])["charts_detail"][0]["bars"][0]["status"] == "not_held"


def test_unprinted_bar_is_never_matched():
    page = _page([_bar(printed=False)])
    model = _model("openai/gpt-6-astra", [_row(96.0)])
    bar = classify_fixtures([page], [model])["charts_detail"][0]["bars"][0]
    assert bar["status"] == "low_confidence"
    assert bar["tolerance"] == 0.05


def test_two_readings_that_disagree_are_disputed():
    page = _page(
        [_bar()],
        readings=[
            {
                "reader": "a",
                "date": "2026-09-24",
                "bars": [
                    {
                        "model_as_labelled": "GPT-6 Astra",
                        "benchmark_id": "gpqa_diamond",
                        "score": 96.0,
                    }
                ],
            },
            {
                "reader": "b",
                "date": "2026-09-24",
                "bars": [
                    {
                        "model_as_labelled": "GPT-6 Astra",
                        "benchmark_id": "gpqa_diamond",
                        "score": 91.0,
                    }
                ],
            },
        ],
    )
    model = _model("openai/gpt-6-astra", [_row(96.0)])
    assert classify_fixtures([page], [model])["charts_detail"][0]["bars"][0]["status"] == "disputed"


def test_known_mismatch_must_still_be_a_mismatch():
    bad = _page([_bar(known_mismatch={"ticket": "TBD", "note": "off"})])
    good = _page([_bar()])
    model = _model("openai/gpt-6-astra", [_row(96.0)])
    stale = mismatch_errors(classify_fixtures([bad], [model]))
    assert stale and "stale" in stale[0]
    fresh = mismatch_errors(classify_fixtures([good], [model]))
    assert fresh == []
    off = classify_fixtures([bad], [_model("openai/gpt-6-astra", [_row(10.0)])])
    assert mismatch_errors(off) == []
    unmarked = _page([_bar()])
    missed = classify_fixtures([unmarked], [_model("openai/gpt-6-astra", [_row(10.0)])])
    assert mismatch_errors(missed)


def test_shipped_fixtures_and_no_chart_images():
    images = [path for path in CHARTS.rglob("*") if path.suffix.lower() in IMAGE_SUFFIXES]
    assert images == []
    fixtures = load_fixtures(CHARTS)
    assert fixtures, "benchmarks/_charts has no fixtures"
    models = load_models(ROOT)
    problems = fixture_errors(fixtures, models)
    assert problems == []
    report = classify_fixtures(fixtures, models)
    assert mismatch_errors(report) == []


def test_same_source_wins_for_a_competitor():
    page = _page(
        [_bar(role="competitor", model_id="google/gemini-3-8-flash", model_as_labelled="Gemini 3.8 Flash")],
        competitor_numbers="vendor_run",
    )
    model = _model("google/gemini-3-8-flash", [_row(96.0)])
    bar = classify_fixtures([page], [model])["charts_detail"][0]["bars"][0]
    assert bar["status"] == "matched"
    assert bar["same_source"] is True


def test_evaluated_bar_without_same_source_is_a_gap():
    page = _page(
        [
            _bar(
                role="evaluated",
                model_id="anthropic/claude-fable-5-1",
                model_as_labelled="Claude Fable 5.1",
                score=52.0,
                score_text="52.0",
            )
        ],
        competitor_numbers="vendor_run",
    )
    model = _model(
        "anthropic/claude-fable-5-1",
        [
            _row(55.8, source="https://www.anthropic.com/claude-fable-5-1-system-card"),
            _row(57.88, source="https://www.tbench.ai/leaderboard"),
        ],
    )
    bar = classify_fixtures([page], [model])["charts_detail"][0]["bars"][0]
    assert bar["status"] == "competitor_gap"
    assert round(bar["gap"], 2) == -3.8
    assert {row["source_url"] for row in bar["held_rows"]} == {
        "https://www.anthropic.com/claude-fable-5-1-system-card",
        "https://www.tbench.ai/leaderboard",
    }


def test_sibling_configurations_match_one_row():
    page = _page(
        [
            _bar(score=88.0, score_text="88.0", configuration="Claude Code"),
            _bar(score=90.6, score_text="90.6", configuration="DSH Minimal"),
        ]
    )
    model = _model("openai/gpt-6-astra", [_row(90.6, configuration="DSH Minimal")])
    bars = classify_fixtures([page], [model])["charts_detail"][0]["bars"]
    by_config = {bar["configuration"]: bar["status"] for bar in bars}
    assert by_config == {"DSH Minimal": "matched", "Claude Code": "other_configuration"}
    marked = _page(
        [
            _bar(score=88.0, score_text="88.0", configuration="Claude Code", known_mismatch={"ticket": "TBD", "note": "off"}),
            _bar(score=90.6, score_text="90.6", configuration="DSH Minimal"),
        ]
    )
    stale = mismatch_errors(classify_fixtures([marked], [model]))
    assert stale and "stale" in stale[0]


def test_sibling_configurations_that_miss_the_row_are_mismatches():
    page = _page(
        [
            _bar(score=88.0, score_text="88.0", configuration="Claude Code"),
            _bar(score=84.1, score_text="84.1", configuration="Codex"),
        ]
    )
    model = _model("openai/gpt-6-astra", [_row(90.6)])
    bars = classify_fixtures([page], [model])["charts_detail"][0]["bars"]
    assert {bar["status"] for bar in bars} == {"mismatched"}


def test_different_unit_is_not_a_gap():
    page = _page(
        [_bar(role="evaluated", score=1565, score_text="1565", unit="elo")],
        competitor_numbers="vendor_run",
    )
    model = _model(
        "openai/gpt-6-astra",
        [_row(53, unit="normalized Elo percent")],
    )
    bar = classify_fixtures([page], [model])["charts_detail"][0]["bars"][0]
    assert bar["status"] == "unit_differs"
    assert bar["chart_score"] == 1565
    assert bar["held"]["score"] == 53
    assert bar["held"]["unit"] == "normalized Elo percent"


def test_other_metric_is_not_compared():
    page = _page([_bar(score=41.6, score_text="41.6", metric="tasks_completed")])
    model = _model("openai/gpt-6-astra", [_row(68.5)])
    bar = classify_fixtures([page], [model])["charts_detail"][0]["bars"][0]
    assert bar["status"] == "other_metric"


def test_missing_benchmark_page_is_catalogue_coverage():
    page = _page(
        [
            _bar(
                benchmark_id=None,
                benchmark_as_labelled="DeepSWE v1.1",
                score=74.2,
                score_text="74.2",
            )
        ]
    )
    report = classify_fixtures([page], [])
    bar = report["charts_detail"][0]["bars"][0]
    assert bar["status"] == "no_benchmark_page"
    assert report["uncatalogued"] == [{"benchmark_as_labelled": "DeepSWE v1.1", "bars": 1}]


def test_reconcile_pairs_a_second_reading(tmp_path: Path):
    fixture_path = tmp_path / "example.yaml"
    fixture_path.write_text(
        """page_url: "https://example.com/post"
publisher: "Example"
read_on: "2026-09-24"
charts:
  - title: "Terminal-Bench"
    kind: image
    image_url: "https://example.com/a.png"
    image_sha256: "abc123"
    footnotes: "One setting."
    competitor_numbers: vendor_run
    readings:
      - reader: grok
        date: "2026-09-24"
    bars:
      - model_as_labelled: "GPT-6 Astra"
        model_id: "openai/gpt-6-astra"
        benchmark_id: terminal_bench_v4_0
        benchmark_as_labelled: "Terminal-Bench 4.0"
        score: 52.0
        unit: "percent"
        printed: true
        configuration: "max"
        role: subject
      - model_as_labelled: "Claude Fable 5.1"
        model_id: "anthropic/claude-fable-5-1"
        benchmark_id: terminal_bench_v4_0
        benchmark_as_labelled: "Terminal-Bench 4.0"
        score: 48
        unit: "percent"
        printed: false
        configuration: "max"
        role: competitor
      - model_as_labelled: "Only A"
        model_id: null
        benchmark_id: null
        benchmark_as_labelled: "DeepSWE"
        score: 10
        unit: "percent"
        printed: true
        configuration: ""
        role: competitor
""",
        encoding="utf-8",
    )
    fixture = load_fixture(fixture_path)
    manifest = {"aa-1.png": "abc123"}
    readings = [
        {
            "source": "aa-1.png",
            "reader": "reader-b",
            "read_on": "2026-09-25",
            "charts": [
                {
                    "title": "Terminal-Bench",
                    "items": [
                        {
                            "model_as_labelled": "GPT-6 Astra",
                            "benchmark_as_labelled": "Terminal-Bench 4.0",
                            "score": 52.04,
                            "score_text": "52.0",
                            "unit": "percent",
                            "metric_or_setting": "max",
                            "printed": True,
                        },
                        {
                            "model_as_labelled": "Claude Fable 5.1",
                            "benchmark_as_labelled": "Terminal-Bench 4.0",
                            "score": 49,
                            "score_text": "49",
                            "unit": "percent",
                            "metric_or_setting": "max",
                            "printed": False,
                            "uncertainty": 2,
                        },
                        {
                            "model_as_labelled": "Only B",
                            "benchmark_as_labelled": "DeepSWE",
                            "score": 3,
                            "score_text": "3",
                            "unit": "percent",
                            "metric_or_setting": "",
                            "printed": True,
                        },
                    ],
                }
            ],
        },
        {
            "source": "missing.png",
            "reader": "reader-b",
            "read_on": "2026-09-25",
            "charts": [],
        },
    ]
    report = reconcile_readings([fixture], readings, manifest)
    classes = sorted(row["class"] for row in report["pairs"])
    assert classes == ["agree", "agree", "only_a", "only_b", "unpaired_source"]
    disagree = next(
        row
        for row in reconcile_readings(
            [fixture],
            [
                {
                    "source": "aa-1.png",
                    "reader": "reader-b",
                    "read_on": "2026-09-25",
                    "charts": [
                        {
                            "title": "ignored",
                            "items": [
                                {
                                    "model_as_labelled": "GPT-6 Astra",
                                    "benchmark_as_labelled": "Terminal-Bench 4.0",
                                    "score": 40,
                                    "score_text": "40",
                                    "unit": "percent",
                                    "metric_or_setting": "max",
                                    "printed": True,
                                }
                            ],
                        }
                    ],
                }
            ],
            manifest,
        )["pairs"]
        if row["class"] == "disagree"
    )
    apply_second_reading(
        fixture_path,
        disagree["chart_index"],
        disagree["reader"],
        disagree["read_on"],
        [
            {
                "bar_index": disagree["bar_index"],
                "a_reader": "grok",
                "a_value": disagree["a"]["score_text"],
                "b_reader": "reader-b",
                "b_value": disagree["b"]["score_text"],
            }
        ],
    )
    reread = load_fixture(fixture_path)
    assert reread["charts"][0]["readings"][1]["reader"] == "reader-b"
    assert reread["charts"][0]["bars"][0]["disputed"][1]["value"] == 40
    status = classify_fixtures([reread], [_model("openai/gpt-6-astra", [_row(52.0)])])
    assert status["charts_detail"][0]["bars"][0]["status"] == "disputed"


def test_parse_score_accepts_the_forms_a_second_reader_writes():
    suffix = parse_score("33k")
    assert suffix.kind == "number" and suffix.value == 33000 and suffix.text == "33k"
    millions = parse_score("1.2M")
    assert millions.value == 1_200_000 and millions.text == "1.2M"
    money = parse_score("$1.66")
    assert money.value == 1.66 and money.text == "$1.66"
    percent = parse_score("33.2%")
    assert percent.value == 33.2 and percent.text == "33.2%"
    noted = parse_score("36.8†")
    assert noted.value == 36.8 and noted.text == "36.8†"
    for blank in ("—", "-", "", None):
        parsed = parse_score(blank)
        assert parsed.kind == "blank" and parsed.value is None
    odd = parse_score("+4 pts vs GPT-5.6 Sol")
    assert odd.kind == "unparsed" and odd.value is None and odd.text == "+4 pts vs GPT-5.6 Sol"


def test_unparsed_score_is_reported_and_does_not_crash():
    report = reconcile_readings(
        [],
        [
            {
                "source": "https://example.com/missing",
                "reader": "reader-b",
                "read_on": "2026-09-24",
                "charts": [
                    {
                        "title": "Odd",
                        "items": [
                            {
                                "model_as_labelled": "GPT-6 Astra",
                                "benchmark_as_labelled": "GPQA",
                                "score": "not a score",
                                "metric_or_setting": "",
                                "printed": True,
                            }
                        ],
                    }
                ],
            }
        ],
        {},
    )
    assert report["by_class"]["unpaired_source"] == 1
    paired = reconcile_readings(
        [
            {
                "page_url": "https://example.com/post",
                "charts": [
                    {
                        "title": "One",
                        "bars": [
                            {
                                "model_as_labelled": "GPT-6 Astra",
                                "benchmark_as_labelled": "GPQA",
                                "score": 1,
                                "score_text": "1",
                                "printed": True,
                                "configuration": "",
                            }
                        ],
                    }
                ],
                "_path": "example.yaml",
                "_slug": "example",
            }
        ],
        [
            {
                "source": "https://example.com/post",
                "reader": "reader-b",
                "read_on": "2026-09-24",
                "charts": [
                    {
                        "title": "One",
                        "items": [
                            {
                                "model_as_labelled": "GPT-6 Astra",
                                "benchmark_as_labelled": "GPQA",
                                "score": "not a score",
                                "metric_or_setting": "",
                                "printed": True,
                            }
                        ],
                    }
                ],
            }
        ],
        {},
    )
    assert [row["class"] for row in paired["pairs"]] == ["unparsed"]


def _one_bar_fixture(model: str, benchmark: str, **extra) -> dict:
    bar = {
        "model_as_labelled": model,
        "benchmark_as_labelled": benchmark,
        "score": extra.pop("score", 1),
        "score_text": extra.pop("score_text", "1"),
        "printed": True,
        "configuration": extra.pop("configuration", ""),
    }
    bar.update(extra)
    return {
        "page_url": "https://example.com/post",
        "charts": [{"title": "Bars", "bars": [bar]}],
        "_path": "example.yaml",
        "_slug": "example",
    }


def _one_reading(model: str, benchmark: str, **extra) -> dict:
    item = {
        "model_as_labelled": model,
        "benchmark_as_labelled": benchmark,
        "score": extra.pop("score", 1),
        "metric_or_setting": extra.pop("metric_or_setting", ""),
        "printed": True,
    }
    item.update(extra)
    return {
        "source": "https://example.com/post",
        "reader": "reader-b",
        "read_on": "2026-09-24",
        "charts": [{"title": "Bars", "items": [item]}],
    }


def _classes(fixture: dict, reading: dict) -> list[str]:
    return [row["class"] for row in reconcile_readings([fixture], [reading], {})["pairs"]]


def test_ifbench_prompt_and_ruler_context_stay_on_the_benchmark():
    assert _classes(
        _one_bar_fixture("8B Dense", "ifbench", score=77.17, score_text="77.17", configuration="Prompt."),
        _one_reading("Granite 4.2 8B Dense", "IFBench (prompt)", score=77.17),
    ) == ["agree"]
    assert sorted(
        _classes(
            _one_bar_fixture("8B Dense", "ifbench", configuration="Loose."),
            _one_reading("8B Dense", "IFBench (prompt)"),
        )
    ) == ["only_a", "only_b"]
    assert _classes(
        _one_bar_fixture("8B Dense", "ruler", score=71.41, score_text="71.41", configuration="128K context."),
        _one_reading("Granite 4.2 8B Dense", "RULER 128K", score=71.41),
    ) == ["agree"]
    assert sorted(
        _classes(
            _one_bar_fixture("8B Dense", "ruler", configuration="128K context."),
            _one_reading("8B Dense", "RULER 64K"),
        )
    ) == ["only_a", "only_b"]


def test_an_unstated_mode_does_not_become_the_mode():
    fixture = _one_bar_fixture("8B Dense", "GPQA", score=54.8, score_text="54.80")
    fixture["charts"][0]["bars"].append(
        {
            "model_as_labelled": "8B Dense",
            "benchmark_as_labelled": "GPQA",
            "score": 60,
            "score_text": "60",
            "printed": True,
            "configuration": "thinking",
        }
    )
    reading = _one_reading(
        "8B Dense",
        "GPQA",
        score=60,
        metric_or_setting="thinking",
    )
    reading["charts"][0]["items"].append(
        {
            "model_as_labelled": "8B Dense",
            "benchmark_as_labelled": "GPQA",
            "score": 54.8,
            "metric_or_setting": "section: Reasoning; thinking mode not stated",
            "printed": True,
        }
    )
    assert sorted(_classes(fixture, reading)) == ["agree", "agree"]


def test_prose_uncertainty_is_not_a_tolerance():
    fixture = _one_bar_fixture("Inkling", "MCP Atlas", score=76, score_text="76", printed=False)
    note = _one_reading(
        "Inkling",
        "MCP Atlas",
        score=76.4,
        score_text="76.4",
        printed=False,
        uncertainty="none; exact embedded value",
    )
    assert _classes(fixture, note) == ["disagree"]
    bound = _one_reading(
        "Inkling",
        "MCP Atlas",
        score=76.4,
        score_text="76.4",
        printed=False,
        uncertainty="±0.5; overlaps the next vertex",
    )
    assert _classes(fixture, bound) == ["agree"]


def test_label_normalisation_pairs_the_same_bar():
    fixture = {
        "page_url": "https://example.com/post",
        "charts": [
            {
                "title": "Bars",
                "bars": [
                    {
                        "model_as_labelled": "GPT-6 Astra (max)",
                        "benchmark_as_labelled": "Terminal-Bench 2.1",
                        "score": 90.6,
                        "score_text": "90.6",
                        "printed": True,
                        "configuration": "max",
                    },
                    {
                        "model_as_labelled": "GPT-6 Astra",
                        "benchmark_as_labelled": "HLE (with tools)",
                        "score": 57.2,
                        "score_text": "57.2",
                        "printed": True,
                        "configuration": "",
                    },
                ],
            }
        ],
        "_path": "example.yaml",
        "_slug": "example",
    }
    reading = {
        "source": "https://example.com/post",
        "reader": "reader-b",
        "read_on": "2026-09-24",
        "charts": [
            {
                "title": "Bars",
                "items": [
                    {
                        "model_as_labelled": "GPT-6 Astra max",
                        "benchmark_as_labelled": "Terminal-bench 2.1",
                        "score": 90.6,
                        "metric_or_setting": "max",
                        "printed": True,
                    },
                    {
                        "model_as_labelled": "GPT-6 Astra",
                        "benchmark_as_labelled": "Humanity's Last Exam, tools",
                        "score": 57.2,
                        "metric_or_setting": "",
                        "printed": True,
                    },
                ],
            }
        ],
    }
    classes = [row["class"] for row in reconcile_readings([fixture], [reading], {})["pairs"]]
    assert classes == ["agree", "agree"]


def test_effort_suffix_pairs_and_max_stays_apart_from_high():
    paired = _classes(
        _one_bar_fixture("GPT-6 Astra (max)", "Terminal-Bench 2.1", score=90.6, score_text="90.6"),
        _one_reading("GPT-6 Astra", "Terminal-Bench 2.1", score=90.6, metric_or_setting="max effort"),
    )
    assert paired == ["agree"]
    also = _classes(
        _one_bar_fixture("Grok 4.7", "DeepSWE v1.1", configuration="xhigh"),
        _one_reading("Grok 4.7 xHigh", "DeepSWE v1.1"),
    )
    assert also == ["agree"]
    fixture = {
        "page_url": "https://example.com/post",
        "charts": [
            {
                "title": "Bars",
                "bars": [
                    {
                        "model_as_labelled": "Opus 5 (max)",
                        "benchmark_as_labelled": "Terminal-Bench 2.1",
                        "score": 90,
                        "score_text": "90",
                        "printed": True,
                        "configuration": "max",
                    },
                    {
                        "model_as_labelled": "Opus 5 (high)",
                        "benchmark_as_labelled": "Terminal-Bench 2.1",
                        "score": 80,
                        "score_text": "80",
                        "printed": True,
                        "configuration": "high",
                    },
                ],
            }
        ],
        "_path": "example.yaml",
        "_slug": "example",
    }
    reading = {
        "source": "https://example.com/post",
        "reader": "reader-b",
        "read_on": "2026-09-24",
        "charts": [
            {
                "title": "Bars",
                "items": [
                    {
                        "model_as_labelled": "Opus 5",
                        "benchmark_as_labelled": "Terminal-Bench 2.1",
                        "score": 80,
                        "metric_or_setting": "high",
                        "printed": True,
                    },
                    {
                        "model_as_labelled": "Opus 5 max effort",
                        "benchmark_as_labelled": "Terminal-Bench 2.1",
                        "score": 90,
                        "metric_or_setting": "Max",
                        "printed": True,
                    },
                ],
            }
        ],
    }
    classes = sorted(_classes(fixture, reading))
    assert classes == ["agree", "agree"]
    apart = _classes(
        _one_bar_fixture("Opus 5 (max)", "Terminal-Bench 2.1", score=90, score_text="90"),
        _one_reading("Opus 5", "Terminal-Bench 2.1", score=80, metric_or_setting="high"),
    )
    assert sorted(apart) == ["only_a", "only_b"]


def test_claude_product_name_pairs_without_collapsing_the_version():
    assert _classes(
        _one_bar_fixture("Claude Opus 5.5", "SWE-bench Pro"),
        _one_reading("Opus 5.5", "SWE-bench Pro"),
    ) == ["agree"]
    assert _classes(
        _one_bar_fixture("Claude Sonnet 4.6", "SWE-bench Pro"),
        _one_reading("Sonnet 4.6", "SWE-bench Pro"),
    ) == ["agree"]
    assert sorted(
        _classes(
            _one_bar_fixture("Opus 5", "SWE-bench Pro"),
            _one_reading("Opus 5.5", "SWE-bench Pro"),
        )
    ) == ["only_a", "only_b"]
    assert _classes(
        _one_bar_fixture("Gemini 3.5 Flash", "SWE-bench Pro"),
        _one_reading("3.5 Flash", "SWE-bench Pro"),
    ) == ["agree"]


def test_percent_bold_and_underline_marks_pair():
    assert _classes(
        _one_bar_fixture("**Opus 5.5**", "SWE-bench Pro (%)"),
        _one_reading("__Opus 5.5__", "SWE-bench Pro"),
    ) == ["agree"]
    assert _classes(
        _one_bar_fixture("Opus 5.5", "Terminal-Bench 4.0"),
        _one_reading("Opus 5.5", "Terminal-Bench 4.0¹"),
    ) == ["agree"]


def test_section_header_and_main_set_pair():
    assert _classes(
        _one_bar_fixture("Opus 5", "SWE-bench Pro"),
        _one_reading("Opus 5", "Agentic coding / SWE-bench Pro"),
    ) == ["agree"]
    assert _classes(
        _one_bar_fixture("Opus 5", "FrontierCode v1.1 (Main)"),
        _one_reading("Opus 5", "FrontierCode v1.1, main set"),
    ) == ["agree"]
    assert sorted(
        _classes(
            _one_bar_fixture("Opus 5", "FrontierCode v1.1 (Main)"),
            _one_reading("Opus 5", "FrontierCode v1.1 (Extended)"),
        )
    ) == ["only_a", "only_b"]


def test_version_labels_stay_part_of_the_benchmark():
    assert _classes(
        _one_bar_fixture("Opus 5", "gdpval_aa", configuration="GDPval-AA v2, Elo."),
        _one_reading("Opus 5", "GDPval-AA v2"),
    ) == ["agree"]
    assert _classes(
        _one_bar_fixture("Opus 5", "GDPval-AA v2"),
        _one_reading("Opus 5", "GDPval-AA v2.1"),
    ) == ["only_a", "only_b"]
    assert _classes(
        _one_bar_fixture("Opus 5", "AA-Briefcase"),
        _one_reading("Opus 5", "AA-Briefcase v1.1"),
    ) == ["only_a", "only_b"]
    assert _classes(
        _one_bar_fixture("Opus 5", "aa_briefcase", configuration="AA Briefcase v1.1 Elo."),
        _one_reading("Opus 5", "AA-Briefcase v1.1"),
    ) == ["agree"]


def test_harvey_and_biomystery_wording_pairs():
    assert _classes(
        _one_bar_fixture("Claude Sonnet 5", "Harvey Legal Agent Benchmark held-out"),
        _one_reading("Sonnet 5", "Legal Agent Benchmark (Harvey's Held-Out Set)"),
    ) == ["agree"]
    assert _classes(
        _one_bar_fixture("Opus 5", "BioMysteryBench", configuration="hard"),
        _one_reading("Opus 5", "Biology / BioMysteryBench (hard)"),
    ) == ["agree"]
    assert _classes(
        _one_bar_fixture("Opus 5", "BioMysteryBench", configuration="human solved"),
        _one_reading("Opus 5", "BioMysteryBench (human solved)"),
    ) == ["agree"]
    assert sorted(
        _classes(
            _one_bar_fixture("Opus 5", "BioMysteryBench", configuration="hard"),
            _one_reading("Opus 5", "BioMysteryBench (human solved)"),
        )
    ) == ["only_a", "only_b"]


def test_working_exploit_and_register_control_stay_apart():
    fixture = {
        "page_url": "https://example.com/post",
        "charts": [
            {
                "title": "Firefox",
                "bars": [
                    {
                        "model_as_labelled": "Sonnet 5",
                        "benchmark_as_labelled": "Firefox 147 exploit development",
                        "score": 0.0,
                        "score_text": "0.0",
                        "printed": True,
                        "configuration": "Working exploit, pass@1.",
                    },
                    {
                        "model_as_labelled": "Sonnet 5",
                        "benchmark_as_labelled": "Firefox 147 exploit development",
                        "score": 13.2,
                        "score_text": "13.2",
                        "printed": True,
                        "configuration": "Register control only, pass@1.",
                        "metric": "register_control",
                    },
                ],
            }
        ],
        "_path": "example.yaml",
        "_slug": "example",
    }
    reading = {
        "source": "https://example.com/post",
        "reader": "reader-b",
        "read_on": "2026-09-24",
        "charts": [
            {
                "title": "Firefox",
                "items": [
                    {
                        "model_as_labelled": "Sonnet 5",
                        "benchmark_as_labelled": "Firefox 147 exploit development",
                        "score": 0.0,
                        "metric_or_setting": "darker bar; legend 'Working exploit (1.0)'",
                        "printed": True,
                    },
                    {
                        "model_as_labelled": "Sonnet 5",
                        "benchmark_as_labelled": "Firefox 147 exploit development",
                        "score": 13.2,
                        "metric_or_setting": "lighter bar; legend 'Register control only (0.5)'. It may be a partial-credit score",
                        "printed": True,
                    },
                ],
            }
        ],
    }
    assert sorted(_classes(fixture, reading)) == ["agree", "agree"]


def test_raw_healthbench_does_not_take_the_summary_number():
    assert sorted(
        _classes(
            _one_bar_fixture(
                "Claude Opus 5.5",
                "healthbench",
                score=77.1,
                score_text="77.1",
                configuration="HealthBench Professional, raw score.",
            ),
            _one_reading(
                "Claude Opus 5.5",
                "HealthBench Professional",
                score=65.6,
                metric_or_setting="standard config",
            ),
        )
    ) == ["only_a", "only_b"]


def test_partial_and_strict_stay_apart():
    assert _classes(
        _one_bar_fixture("Opus 5", "osworld", configuration="OSWorld 2.0 partial."),
        _one_reading("Opus 5", "OSWorld 2.0 (partial/strict) - partial"),
    ) == ["agree"]
    assert _classes(
        _one_bar_fixture("Opus 5", "osworld", configuration="OSWorld 2.0 partial."),
        _one_reading("Opus 5", "OSWorld 2.0 (partial/strict) - strict"),
    ) == ["only_a", "only_b"]


def test_pdf_source_pairs_by_document_hash():
    digest = "a" * 64
    fixture = _one_bar_fixture("Opus 5", "SWE-bench Pro", score=79.2, score_text="79.2")
    fixture["document_sha256"] = digest
    fixture["charts"][0]["kind"] = "html_table"
    reading = _one_reading("Claude Opus 5", "SWE-bench Pro", score=79.2)
    reading["source"] = "anthropic-opus-5-system-card.pdf"
    report = reconcile_readings([fixture], [reading], {"anthropic-opus-5-system-card.pdf": digest})
    assert [row["class"] for row in report["pairs"]] == ["agree"]
    missing = reconcile_readings(
        [fixture],
        [{**reading, "source": "other.pdf"}],
        {"other.pdf": "b" * 64},
    )
    assert missing["by_class"]["unpaired_source"] == 1


def test_phase2a_system_card_pdfs_use_the_manifest_digest():
    fixtures = {item["_slug"]: item for item in load_fixtures()}
    expected = {
        "anthropic-opus-5-5-system-card.pdf": "anthropic-claude-opus-5-5-system-card",
        "anthropic-fable-5-1-system-card.pdf": "anthropic-claude-fable-5-1-system-card",
        "anthropic-opus-5-system-card.pdf": "anthropic-claude-opus-5-system-card",
        "anthropic-sonnet-5-system-card.pdf": "anthropic-claude-sonnet-5-system-card",
        "anthropic-opus-4-8-system-card.pdf": "anthropic-claude-opus-4-8-system-card",
    }
    for slug in expected.values():
        assert re.fullmatch(r"[0-9a-f]{64}", fixtures[slug]["document_sha256"])
    # The chart cache holds the PDFs and lives outside the repository, so CI
    # can only check the digests' shape.
    manifest_path = Path("/Users/terbeest/dev/worktrees/.chart-cache/manifest-phase2a.tsv")
    if not manifest_path.is_file():
        pytest.skip("the chart cache is not on this machine")
    manifest = load_manifest(manifest_path)
    for name, slug in expected.items():
        assert fixtures[slug]["document_sha256"] == manifest[name]


def _resolved(score: float, readings: list[tuple[str, object]], score_text: str | None = None) -> dict:
    text = score_text if score_text is not None else str(score)
    return _bar(
        score=score,
        score_text=text,
        resolution={
            "rule": "two_of_three",
            "readings": [{"reader": reader, "value": value} for reader, value in readings],
        },
    )


def test_resolved_bar_needs_two_readings_within_printed_precision():
    # 85.64 is inside the printed step of 85.6. 85.7 is the next printed tenth.
    close = _resolved(85.6, [("grok-build-4.7", 85.6), ("claude-opus", 85.64), ("claude-sonnet", 10.0)], "85.6")
    page = _page([close])
    page["read_on"] = "2026-09-24"
    assert fixture_errors([page], []) == []
    apart = _resolved(85.6, [("grok-build-4.7", 85.6), ("claude-opus", 83.4), ("claude-sonnet", 80.0)], "85.6")
    page = _page([apart])
    page["read_on"] = "2026-09-24"
    errors = fixture_errors([page], [])
    assert errors and all("agree" in line for line in errors)
    report = classify_fixtures([page], [_model("openai/gpt-6-astra", [_row(85.6)])])
    assert report["charts_detail"][0]["bars"][0]["status"] == "disputed"


def test_third_reading_that_agrees_with_neither_stays_disputed():
    bar = _resolved(96.0, [("a", 96.0), ("b", 91.0), ("c", 80.0)], "96.0")
    page = _page([bar])
    page["read_on"] = "2026-09-24"
    model = _model("openai/gpt-6-astra", [_row(96.0)])
    assert classify_fixtures([page], [model])["charts_detail"][0]["bars"][0]["status"] == "disputed"


def test_resolved_score_must_be_the_agreed_value():
    # Two readers agree on 85.6. The score 83.4 matches the card and still fails.
    wrong = _resolved(83.4, [("grok-build-4.7", 85.6), ("claude-opus", 83.4), ("claude-sonnet", 85.6)], "83.4")
    page = _page([wrong])
    page["read_on"] = "2026-09-24"
    model = _model("openai/gpt-6-astra", [_row(83.4)])
    errors = fixture_errors([page], [])
    assert len(errors) == 1 and "agreed" in errors[0]
    assert classify_fixtures([page], [model])["charts_detail"][0]["bars"][0]["status"] == "matched"
    settled = _resolved(85.6, [("grok-build-4.7", 85.6), ("claude-opus", 83.4), ("claude-sonnet", 85.6)], "85.6")
    page = _page([settled])
    page["read_on"] = "2026-09-24"
    assert fixture_errors([page], []) == []
    bar = classify_fixtures([page], [_model("openai/gpt-6-astra", [_row(85.6)])])["charts_detail"][0]["bars"][0]
    assert bar["status"] == "matched"


def test_disputed_bar_is_not_a_match():
    page = _page(
        [_bar(disputed=[{"reader": "a", "value": 96.0}, {"reader": "b", "value": 91.0}])],
    )
    model = _model("openai/gpt-6-astra", [_row(96.0)])
    bar = classify_fixtures([page], [model])["charts_detail"][0]["bars"][0]
    assert bar["status"] == "disputed"
    marked = _page(
        [
            _bar(
                known_mismatch={"ticket": "TBD", "note": "off"},
                disputed=[{"reader": "a", "value": "33k"}, {"reader": "b", "value": 33001}],
            )
        ]
    )
    report = classify_fixtures([marked], [model])
    assert report["charts_detail"][0]["bars"][0]["status"] == "disputed"
    assert mismatch_errors(report) == []


def test_table_cells_pair_across_chart_titles_on_the_same_page():
    fixture = _one_bar_fixture(
        "GPT-6 Astra",
        "Terminal-Bench 4.0",
        score=57.9,
        score_text="57.9",
        configuration="Maximum at any effort.",
    )
    fixture["charts"][0]["title"] = "Coding"
    reading = _one_reading(
        "GPT-6 Astra",
        "Terminal-Bench 4.0",
        score=57.9,
        metric_or_setting="table value = maximum at any effort (table note)",
    )
    reading["charts"][0]["title"] = "Results table: Coding"
    assert _classes(fixture, reading) == ["agree"]
    other = _one_bar_fixture("GPT-6 Astra", "Terminal-Bench 4.0", score=57.9, score_text="57.9")
    other["page_url"] = "https://example.com/other"
    apart = reconcile_readings([other], [reading], {})
    assert apart["by_class"]["unpaired_source"] == 1
    assert apart["by_class"].get("agree", 0) == 0


def test_effort_phrases_normalise_and_a_table_cell_stays_off_a_tooltip_effort():
    assert _classes(
        _one_bar_fixture("GPT-6 Astra", "Terminal-Bench 4.0", score=57.9, score_text="57.9", configuration="max effort"),
        _one_reading("GPT-6 Astra", "Terminal-Bench 4.0", score=57.9, metric_or_setting="reasoning effort: Max"),
    ) == ["agree"]
    assert _classes(
        _one_bar_fixture("GPT-6 Sol", "AutomationBench", score=33.2, score_text="33.2", configuration="xhigh effort"),
        _one_reading(
            "GPT-6 Sol",
            "AutomationBench",
            score=33.2,
            metric_or_setting="effort: xhigh (in row label); cost per task: $0.27",
        ),
    ) == ["agree"]
    assert _classes(
        _one_bar_fixture("GPT-6 Astra", "DeepSWE", score=1, score_text="1", configuration="max effort"),
        _one_reading("GPT-6 Astra", "DeepSWE", score=1, metric_or_setting="effort: maximum (caption)"),
    ) == ["agree"]
    fixture = _one_bar_fixture(
        "Claude Opus 5",
        "FrontierCode 1.1 Extended",
        score=63.6,
        score_text="63.6",
        configuration="Maximum at any effort.",
    )
    reading = _one_reading("Claude Opus 5", "FrontierCode 1.1 Extended", score=63.6, metric_or_setting="reasoning effort: Medium")
    reading["charts"][0]["items"].append(
        {
            "model_as_labelled": "Claude Opus 5",
            "benchmark_as_labelled": "FrontierCode 1.1 Extended",
            "score": 70,
            "metric_or_setting": "reasoning effort: Max",
            "printed": True,
        }
    )
    assert sorted(_classes(fixture, reading)) == ["only_a", "only_b", "only_b"]


def test_harness_phrases_normalise_and_different_harnesses_stay_apart():
    assert _classes(
        _one_bar_fixture(
            "GPT-6 Astra",
            "FrontierCode 1.1 Extended",
            score=64.5,
            score_text="64.5",
            configuration="Codex-like developer message",
        ),
        _one_reading(
            "GPT-6 Astra",
            "FrontierCode 1.1 Extended (score)",
            score=64.5,
            metric_or_setting="table value = maximum at any effort (table note); footnote 8: Astra run with a Codex-like developer message",
        ),
    ) == ["agree"]
    assert _classes(
        _one_bar_fixture("GPT-6 Astra", "ARC-AGI-3", score=99.9, score_text="99.9", configuration="responses API harness"),
        _one_reading(
            "GPT-6 Astra",
            "ARC-AGI-3",
            score=99.9,
            metric_or_setting="footnote 1: Astra run with OpenAI's responses API harness (two settings changed)",
        ),
    ) == ["agree"]
    assert _classes(
        _one_bar_fixture("GPT-6 Astra", "ExploitGym", score=42.4, score_text="42.4", configuration="no 6-hour cap"),
        _one_reading(
            "GPT-6 Astra",
            "ExploitGym",
            score=42.4,
            metric_or_setting="footnote 13: run without the 6-hour time limit",
        ),
    ) == ["agree"]
    assert sorted(
        _classes(
            _one_bar_fixture("Opus 5", "Terminal-Bench 2.1", configuration="Codex-like developer message"),
            _one_reading("Opus 5", "Terminal-Bench 2.1", metric_or_setting="claude code"),
        )
    ) == ["only_a", "only_b"]


def test_version_labels_have_to_agree():
    assert _classes(
        _one_bar_fixture("Opus 5", "Artificial Analysis Intelligence Index v4.1.1", score=63.1, score_text="63.1"),
        _one_reading("Opus 5", "Artificial Analysis Intelligence Index v4.1.1", score=63.1),
    ) == ["agree"]
    assert sorted(
        _classes(
            _one_bar_fixture("Opus 5", "Artificial Analysis Intelligence Index v4.1.1"),
            _one_reading("Opus 5", "Artificial Analysis Intelligence Index v4.2"),
        )
    ) == ["only_a", "only_b"]
    assert _classes(
        _one_bar_fixture("Opus 5", "FrontierCode 1.1 Extended"),
        _one_reading("Opus 5", "FrontierCode 1.1 Extended (score)"),
    ) == ["agree"]
    assert sorted(
        _classes(
            _one_bar_fixture("Opus 5", "FrontierCode 1.1 Extended"),
            _one_reading("Opus 5", "FrontierCode 1.1 Main"),
        )
    ) == ["only_a", "only_b"]
    assert _classes(
        _one_bar_fixture("Opus 5", "ExploitBench June-August 2026"),
        _one_reading("Opus 5", "ExploitBench (June-Aug 2026)"),
    ) == ["agree"]
    assert sorted(
        _classes(
            _one_bar_fixture("Opus 5", "ExploitBench June-August 2026"),
            _one_reading("Opus 5", "ExploitBench June-August 2025"),
        )
    ) == ["only_a", "only_b"]
    captioned = _one_reading("GPT-6 Sol", "DeepSWE", score=68.8, metric_or_setting="reasoning effort: max")
    captioned["charts"][0]["footnotes"] = "Caption identifies DeepSWE 1.1."
    assert _classes(
        _one_bar_fixture("GPT-6 Sol", "DeepSWE v1.1", score=68.8, score_text="68.8", configuration="Max effort."),
        captioned,
    ) == ["agree"]
    both = _one_reading("GPT-6 Sol", "DeepSWE", metric_or_setting="max")
    both["charts"][0]["footnotes"] = "DeepSWE 1.1 and DeepSWE 1.2 are both named."
    assert sorted(
        _classes(_one_bar_fixture("GPT-6 Sol", "DeepSWE v1.1", configuration="max"), both)
    ) == ["only_a", "only_b"]


def test_openscore_dash_stays_on_the_benchmark_and_internal_names_pair():
    assert _classes(
        _one_bar_fixture("GPT-6 Astra", "OpenScore String Quartets (1 - OMR-NED)", score=0.84, score_text="0.84"),
        _one_reading("GPT-6 Astra", "OpenScore String Quartets (1 - OMR-NED)", score=0.84),
    ) == ["agree"]
    assert _classes(
        _one_bar_fixture("GPT-6 Astra", "Computer-use safety", score=2.4, score_text="2.4"),
        _one_reading("GPT-6 Astra", "Internal computer use safety benchmark (lower is better)", score=2.4),
    ) == ["agree"]
    assert sorted(
        _classes(
            _one_bar_fixture("GPT-6 Astra", "Computer-use safety"),
            _one_reading("GPT-6 Astra", "Internal computer use safety benchmark, w/ AutoReview (lower is better)"),
        )
    ) == ["only_a", "only_b"]


def test_openai_fixture_settings_name_the_harness_and_the_version():
    astra = (CHARTS / "openai-gpt-6-astra.yaml").read_text(encoding="utf-8")
    sol = (CHARTS / "openai-gpt-6-sol-and-luna.yaml").read_text(encoding="utf-8")
    for gone in (
        "Codex-like developer message for Astra",
        "Responses API harness for Astra",
        "Tier 4, v2",
        "No 6-hour cap for Astra and Sol",
        "max effort, Opus 5 fallback",
    ):
        assert gone not in astra
        assert gone not in sol
    assert 'benchmark_as_labelled: "FrontierCode 1.1 Extended"' in astra
    assert 'benchmark_as_labelled: "Artificial Analysis Intelligence Index v4.1.1"' in astra
    assert 'configuration: "Codex-like developer message"' in astra
    assert 'configuration: "responses API harness"' in astra
    assert 'configuration: "no 6-hour cap"' in astra


def test_hyphenated_model_version_pairs_and_the_next_version_stays_apart():
    assert _classes(
        _one_bar_fixture("Claude Opus 4.8", "SWE-bench Pro"),
        _one_reading("Claude-opus-4-8", "SWE-bench Pro"),
    ) == ["agree"]
    assert sorted(
        _classes(
            _one_bar_fixture("Claude Opus 4.8", "SWE-bench Pro"),
            _one_reading("Claude-opus-4-7", "SWE-bench Pro"),
        )
    ) == ["only_a", "only_b"]


def test_printed_benchmark_names_pair_with_the_catalogue_id():
    assert _classes(
        _one_bar_fixture(
            "Kimi K3 (max)",
            "hle",
            score=43.5,
            score_text="43.5",
            configuration="Model card. HLE-Full Full set, without tools.",
        ),
        _one_reading(
            "Kimi K3 (max)",
            "HLE-Full",
            score=43.5,
            metric_or_setting="first value = without tools",
        ),
    ) == ["agree"]
    assert sorted(
        _classes(
            _one_bar_fixture(
                "Kimi K3 (max)",
                "hle",
                configuration="HLE text-only, without tools.",
            ),
            _one_reading("Kimi K3 (max)", "HLE-Full", metric_or_setting="without tools"),
        )
    ) == ["only_a", "only_b"]
    assert _classes(
        _one_bar_fixture(
            "Kimi K3",
            "charxiv_reasoning",
            configuration="CharXiv (RQ) Without tools.",
        ),
        _one_reading("Kimi K3", "CharXiv (RQ)", metric_or_setting="without tools"),
    ) == ["agree"]
    assert _classes(
        _one_bar_fixture("Kimi K3", "gdpval_aa", configuration="GDPval-AA v2 (Elo)"),
        _one_reading("Kimi K3", "GDPval-AA v2 (Elo)"),
    ) == ["agree"]
    assert _classes(
        _one_bar_fixture("Kimi K3", "aa_briefcase", configuration="AA-Briefcase (Elo)"),
        _one_reading("Kimi K3", "AA-Briefcase (Elo)"),
    ) == ["agree"]
    assert _classes(
        _one_bar_fixture("Kimi K3", "deepsearchqa", configuration="DeepSearchQA (F1)"),
        _one_reading("Kimi K3", "DeepSearchQA (F1)"),
    ) == ["agree"]
    assert sorted(
        _classes(
            _one_bar_fixture("Kimi K3", "deepsearchqa", configuration="DeepSearchQA (F1)"),
            _one_reading("Kimi K3", "DeepSearchQA (EM)"),
        )
    ) == ["only_a", "only_b"]


def test_pass_at_5_and_python_tools_pair_and_pass_at_1_stays_apart():
    assert _classes(
        _one_bar_fixture(
            "Kimi K3",
            "zerobench",
            configuration="ZeroBench (pass@5) Pass@5, without tools.",
        ),
        _one_reading("Kimi K3", "ZeroBench (pass@5)", metric_or_setting="without tools"),
    ) == ["agree"]
    assert sorted(
        _classes(
            _one_bar_fixture("Kimi K3", "zerobench", configuration="ZeroBench (pass@5), without tools."),
            _one_reading("Kimi K3", "ZeroBench", metric_or_setting="pass@1, without tools"),
        )
    ) == ["only_a", "only_b"]
    assert _classes(
        _one_bar_fixture("Kimi K3", "MMMU-Pro", configuration="With Python tools."),
        _one_reading(
            "Kimi K3",
            "MMMU-Pro",
            metric_or_setting="second value = with tool augmentation (Python)",
        ),
    ) == ["agree"]
    assert sorted(
        _classes(
            _one_bar_fixture("Kimi K3", "MMMU-Pro", configuration="With Python tools."),
            _one_reading("Kimi K3", "MMMU-Pro", metric_or_setting="without tools"),
        )
    ) == ["only_a", "only_b"]


def test_tau3_banking_spellings_pair_and_plain_banking_stays_apart():
    assert _classes(
        _one_bar_fixture("Kimi K3", "τ³-Banking"),
        _one_reading("Kimi K3", r"τ3\tau^{3}-Banking"),
    ) == ["agree"]
    assert sorted(
        _classes(
            _one_bar_fixture("Kimi K3", "τ³-Banking"),
            _one_reading("Kimi K3", "Banking"),
        )
    ) == ["only_a", "only_b"]


def test_three_part_version_stays_intact_and_pairs_from_the_caption():
    fixture = _one_bar_fixture(
        "GLM-5.3 Flash",
        "AutomationBench",
        configuration="Card chart. AutomationBench (v1.0.6)",
    )
    reading = _one_reading("GLM-5.3-Flash", "AutomationBench")
    reading["charts"][0]["footnotes"] = "Subtitle: AutomationBench v1.0.6"
    assert _classes(fixture, reading) == ["agree"]
    assert sorted(
        _classes(
            fixture,
            _one_reading("GLM-5.3-Flash", "AutomationBench v1.6"),
        )
    ) == ["only_a", "only_b"]
    assert _classes(
        _one_bar_fixture("Opus 5", "Terminal-Bench 2.0"),
        _one_reading("Opus 5", "Terminal-Bench 2"),
    ) == ["agree"]


def test_logo_tooltip_name_pairs_and_a_different_tooltip_name_stays_apart():
    assert _classes(
        _one_bar_fixture("DeepSeek V4 Flash", "SWE-Bench Pro", score=55.6, score_text="55.6"),
        _one_reading(
            "(unlabelled: DeepSeek whale logo)",
            "SWE-Bench Pro",
            score=55.6,
            metric_or_setting="the blog's hover tooltip names it 'DeepSeek V4 Flash'",
        ),
    ) == ["agree"]
    assert sorted(
        _classes(
            _one_bar_fixture("DeepSeek V4 Flash", "SWE-Bench Pro"),
            _one_reading(
                "(unlabelled: DeepSeek whale logo)",
                "SWE-Bench Pro",
                metric_or_setting="names it 'DeepSeek V4 Pro'",
            ),
        )
    ) == ["only_a", "only_b"]


def test_a_cell_with_a_parenthetical_second_number_uses_the_first():
    assert _classes(
        _one_bar_fixture("Step 3.7 Flash", "GDPval-Stirrup", score=1415.8, score_text="1415.8"),
        _one_reading("Step 3.7 Flash", "GDPval-Stirrup", score="1415.8 (ii 45.8%)"),
    ) == ["agree"]


def test_cache_stem_pairs_with_the_filename_extension():
    digest = "c" * 64
    other = "d" * 64
    fixture = _one_bar_fixture("Opus 5", "SWE-bench Pro", score=79.2, score_text="79.2")
    fixture["document_sha256"] = digest
    fixture["charts"][0]["kind"] = "html_table"
    reading = _one_reading("Opus 5", "SWE-bench Pro", score=79.2)
    reading["source"] = "gemma-4-technical-report.pdf"
    paired = reconcile_readings([fixture], [reading], {"gemma-4-technical-report": digest})
    assert [row["class"] for row in paired["pairs"]] == ["agree"]
    image = _one_bar_fixture("Gemini 3.5 Flash", "SWE-bench Pro", score=70.3, score_text="70.3")
    image["charts"][0]["kind"] = "image"
    image["charts"][0]["image_sha256"] = digest
    image_reading = _one_reading("Gemini 3.5 Flash", "SWE-bench Pro", score=70.3)
    image_reading["source"] = "gemini-35-flash-benchmarks.gif"
    image_report = reconcile_readings(
        [image],
        [image_reading],
        {"gemini-35-flash-benchmarks": digest},
    )
    assert [row["class"] for row in image_report["pairs"]] == ["agree"]
    ambiguous = reconcile_readings(
        [fixture],
        [reading],
        {"gemma-4-technical-report": digest, "gemma-4-technical-report.pdf": other},
    )
    assert ambiguous["by_class"]["unpaired_source"] == 1


def test_not_fetched_reading_is_an_unpaired_source():
    fixture = _one_bar_fixture("LongCat", "SWE-bench Pro")
    fixture["page_url"] = "https://longcat.chat/blog/longcat-2.0"
    reading = _one_reading("LongCat", "SWE-bench Pro")
    reading["source"] = fixture["page_url"]
    reading["status"] = "not_fetched"
    reading["charts"] = []
    report = reconcile_readings([fixture], [reading], {})
    assert report["pairs"][0]["class"] == "unpaired_source"
    assert report["pairs"][0]["reason"] == "source was not fetched"


def test_slice_and_version_wording_stays_on_the_benchmark():
    assert _classes(
        _one_bar_fixture("Gemma 4 31B", "tau2", configuration="Airline. Thinking."),
        _one_reading("Gemma 4 31B", "Tau2 – airline", metric_or_setting="thinking mode"),
    ) == ["agree"]
    assert sorted(
        _classes(
            _one_bar_fixture("Gemma 4 31B", "tau2", configuration="Airline. Thinking."),
            _one_reading("Gemma 4 31B", "Tau2 – retail", metric_or_setting="thinking mode"),
        )
    ) == ["only_a", "only_b"]
    assert _classes(
        _one_bar_fixture("Gemma 4 E2B", "CoVoST", configuration="ja→en. CorpusBLEU."),
        _one_reading("Gemma 4 E2B", "CoVoST ja → en"),
    ) == ["agree"]
    assert _classes(
        _one_bar_fixture("Gemma 4 E2B", "FLEURS", configuration="FLEURS ASR, en, word error rate."),
        _one_reading("Gemma 4 E2B", "FLEURS ASR en"),
    ) == ["agree"]
    assert _classes(
        _one_bar_fixture("Gemma 4 31B", "live_code_bench", configuration="v6. Thinking."),
        _one_reading("Gemma 4 31B", "LiveCodeBench v6", metric_or_setting="thinking mode"),
    ) == ["agree"]
    assert sorted(
        _classes(
            _one_bar_fixture("Gemma 4 31B", "live_code_bench", configuration="v6. Thinking."),
            _one_reading("Gemma 4 31B", "LiveCodeBench v5"),
        )
    ) == ["only_a", "only_b"]
    assert _classes(
        _one_bar_fixture("Gemma 4 31B", "bbeh", configuration="Micro average."),
        _one_reading("Gemma 4 31B", "Big Bench Extra Hard"),
    ) == ["agree"]
    assert _classes(
        _one_bar_fixture("Gemma 4 31B", "hle_tools", configuration="With search. Thinking."),
        _one_reading("Gemma 4 31B", "HLE with search"),
    ) == ["agree"]
    assert _classes(
        _one_bar_fixture("Claude Fable 5", "arena_elo", configuration="Arena Text, 19 June 2026."),
        _one_reading("Claude Fable 5", "Arena Text"),
    ) == ["agree"]
    assert _classes(
        _one_bar_fixture("Gemma 4 31B", "deepmind_mrcr_v2", configuration="8-needle. Thinking."),
        _one_reading("Gemma 4 31B", "MRCR v2"),
    ) == ["agree"]
    assert _classes(
        _one_bar_fixture("Gemma 4 31B", "medxpertqa", configuration="Multimodal. Thinking."),
        _one_reading("Gemma 4 31B", "MedXPertQA MM"),
    ) == ["agree"]


def test_dotted_version_does_not_absorb_a_parameter_count():
    assert _classes(
        _one_bar_fixture("Qwen3.5-9B", "AA-LCR", score=61.7, score_text="61.7"),
        _one_reading("Qwen 3.5 9B", "AA-LCR", score=61.7),
    ) == ["agree"]
    assert sorted(
        _classes(
            _one_bar_fixture("Qwen3.5-9B", "AA-LCR"),
            _one_reading("Qwen3.5-4B", "AA-LCR"),
        )
    ) == ["only_a", "only_b"]
    assert _classes(
        _one_bar_fixture("8B Dense", "bfcl", score=52.39, score_text="52.39", configuration="v4"),
        _one_reading("Granite-4.2 8B Dense", "BFCL (v4)", score=52.39),
    ) == ["agree"]
    assert sorted(
        _classes(
            _one_bar_fixture("8B Dense", "bfcl", configuration="v4"),
            _one_reading("Granite-4.2 30B Dense", "BFCL (v4)"),
        )
    ) == ["only_a", "only_b"]
    assert _classes(
        _one_bar_fixture("30B Dense", "AIME25", score=89.2, score_text="89.2"),
        _one_reading("Granite 4.2 30B", "AIME25", score=89.2),
    ) == ["agree"]
    assert _classes(
        _one_bar_fixture("3B Dense", "τ³-bench (AVG)", score=45.78, score_text="45.78"),
        _one_reading("Granite 4.2 3B Dense", "τ³-bench", score=45.78),
    ) == ["agree"]
    both_spellings = _one_reading("Granite 4.2 8B", "AIME25", score=86.67)
    both_spellings["charts"][0]["items"].append(
        {
            "model_as_labelled": "Granite 4.2 8B Dense",
            "benchmark_as_labelled": "GPQA",
            "score": 54.8,
            "metric_or_setting": "",
            "printed": True,
        }
    )
    fixture = _one_bar_fixture("8B Dense", "AIME25", score=86.67, score_text="86.67")
    fixture["charts"][0]["bars"].append(
        {
            "model_as_labelled": "8B Dense",
            "benchmark_as_labelled": "GPQA",
            "score": 54.8,
            "score_text": "54.80",
            "printed": True,
            "configuration": "",
        }
    )
    assert sorted(_classes(fixture, both_spellings)) == ["agree", "agree"]


def test_size_quant_and_closed_marks_pair_and_two_quants_stay_apart():
    assert _classes(
        _one_bar_fixture("Devstral Small 2", "SWE-bench Verified", score=68.2, score_text="68.2"),
        _one_reading("Devstral Small 2 (24B Dense)", "SWE-bench Verified", score=68.2),
    ) == ["agree"]
    assert _classes(
        _one_bar_fixture("Gemma 4 26B A4B", "IFBench", score=77.2, score_text="77.2"),
        _one_reading("Gemma-4-26B-A4B-it", "IFBench (Inst. Follow.)", score=77.2),
    ) == ["agree"]
    assert _classes(
        _one_bar_fixture("Nemotron 3 Ultra BF16", "PinchBench", score=81.2, score_text="81.2"),
        _one_reading("Nemotron 3 Ultra 550B-A55B BF16", "PinchBench", score=81.2),
    ) == ["agree"]
    assert sorted(
        _classes(
            _one_bar_fixture("Nemotron 3 Ultra BF16", "PinchBench"),
            _one_reading("Nemotron 3 Ultra NVFP4", "PinchBench"),
        )
    ) == ["only_a", "only_b"]
    assert _classes(
        _one_bar_fixture("Claude Haiku 4.5", "CLIcK", score=53.5, score_text="53.5"),
        _one_reading("Claude Haiku 4.5 (closed)", "CLIcK", score=53.5),
    ) == ["agree"]
    assert _classes(
        _one_bar_fixture("DeepSeek V4 Pro", "Terminal-Bench 2.1", score=64.0, score_text="64.0"),
        _one_reading("DeepSeek-V4-Pro-0813", "Terminal-Bench 2.1", score=64.0),
    ) == ["agree"]
    assert sorted(
        _classes(
            _one_bar_fixture("Gemma 4 26B A4B", "swe_bench_verified", score=57.4, score_text="57.4"),
            _one_reading("Gemma-4-26B-A4B-it", "SWE-Bench (Coding)", score=57.4, metric_or_setting="variant not stated"),
        )
    ) == ["only_a", "only_b"]
    assert sorted(
        _classes(
            _one_bar_fixture("Gemma 4 26B A4B", "terminal_bench_v2_1", score=37.2, score_text="37.2"),
            _one_reading(
                "Gemma-4-26B-A4B-it",
                "Terminal-Bench (Terminal)",
                score=37.2,
                metric_or_setting="version not stated",
            ),
        )
    ) == ["only_a", "only_b"]


def test_score_scale_inside_parentheses_is_not_a_section():
    assert _classes(
        _one_bar_fixture("GLM-5.1", "IOI 2025", score=76.1, score_text="76.1"),
        _one_reading("GLM-5.1 754B-A40B", "IOI 2025 (Score / 600)", score=76.1),
    ) == ["agree"]
    assert _classes(
        _one_bar_fixture("Opus 5", "SWE-bench Pro"),
        _one_reading("Opus 5", "Agentic coding / SWE-bench Pro"),
    ) == ["agree"]


def test_niah_cells_pair_on_depth_and_the_quant_stays_out_of_the_model():
    fixture = {
        "page_url": "https://example.com/post",
        "charts": [
            {
                "title": "NIAH",
                "bars": [
                    {
                        "model_as_labelled": "A.X K2",
                        "benchmark_as_labelled": "niah",
                        "score": 100,
                        "score_text": "100",
                        "printed": True,
                        "configuration": "NVFP4 experts-only W4A4. YaRN factor 2. Depth 0%. Context 1000 tokens.",
                    },
                    {
                        "model_as_labelled": "A.X K2",
                        "benchmark_as_labelled": "niah",
                        "score": 90,
                        "score_text": "90",
                        "printed": True,
                        "configuration": "NVFP4 experts-only W4A4. YaRN factor 2. Depth 10%. Context 1000 tokens.",
                    },
                ],
            }
        ],
        "_path": "example.yaml",
        "_slug": "example",
    }
    reading = {
        "source": "https://example.com/post",
        "reader": "reader-b",
        "read_on": "2026-09-24",
        "charts": [
            {
                "title": "NIAH",
                "items": [
                    {
                        "model_as_labelled": "A.X K2 NVFP4 (experts-only W4A4)",
                        "benchmark_as_labelled": "Needle-In-A-Haystack",
                        "score": 90,
                        "metric_or_setting": "context length 1000 tokens; needle depth 10.0%; YARN factor=2; NVFP4 experts-only W4A4 quantised checkpoint",
                        "printed": True,
                    },
                    {
                        "model_as_labelled": "A.X K2 NVFP4 (experts-only W4A4)",
                        "benchmark_as_labelled": "Needle-In-A-Haystack",
                        "score": 100,
                        "metric_or_setting": "context length 1000 tokens; needle depth 0.0%; YARN factor=2; NVFP4 experts-only W4A4 quantised checkpoint",
                        "printed": True,
                    },
                ],
            }
        ],
    }
    assert sorted(_classes(fixture, reading)) == ["agree", "agree"]


def test_index_version_is_not_the_component_list_and_claude_order_pairs():
    metric = (
        "Intelligence Index v4.1.1 (9 evaluations: GDPval-AA v2, Terminal-Bench v2.1, "
        "Humanity's Last Exam); effort/setting in label: max with fallback"
    )
    assert _classes(
        _one_bar_fixture(
            "Claude Fable 5.1",
            "Artificial Analysis Intelligence Index v4.1.1",
            score=66,
            score_text="66",
            configuration="max with fallback",
        ),
        _one_reading(
            "Claude Fable 5.1 (max with fallback)",
            "Artificial Analysis Intelligence Index",
            score=66,
            metric_or_setting=metric,
        ),
    ) == ["agree"]
    assert sorted(
        _classes(
            _one_bar_fixture("Claude Haiku 4.5", "Artificial Analysis Intelligence Index v4.1.1"),
            _one_reading("Claude 4.6 Haiku", "Artificial Analysis Intelligence Index v4.1.1"),
        )
    ) == ["only_a", "only_b"]
    assert _classes(
        _one_bar_fixture("Claude Haiku 4.5", "Artificial Analysis Intelligence Index v4.1.1", score=30, score_text="30"),
        _one_reading("Claude 4.5 Haiku", "Artificial Analysis Intelligence Index v4.1.1", score=30),
    ) == ["agree"]
    assert sorted(
        _classes(
            _one_bar_fixture("Command A+", "Artificial Analysis Intelligence Index v4.1.1"),
            _one_reading("Command A+", "Artificial Analysis Intelligence Index v4.1"),
        )
    ) == ["only_a", "only_b"]
