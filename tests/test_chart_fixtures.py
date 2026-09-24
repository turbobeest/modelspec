"""Release-chart fixtures must be readable, and a mismatched bar fails CI.

The check compares a chart we transcribed with the evidence rows on the cards.
It does not change the export. A ``known_mismatch`` mark keeps a known bad bar
from failing the run, and a mark that now matches is stale.
"""

from __future__ import annotations

from pathlib import Path

from pipeline.load import Model
from scripts.chart_check import (
    apply_second_reading,
    classify_fixtures,
    fixture_errors,
    load_fixture,
    load_fixtures,
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
