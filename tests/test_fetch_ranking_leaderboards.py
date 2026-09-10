"""Live-leaderboard harvest: ranked keys only, conservative maps, observation dates."""

from __future__ import annotations

import json

from scripts.benchmarks.fetch import CachedPage
from scripts.fetch_ranking_leaderboards import (
    AA_URL,
    ARENA_URL,
    CardRef,
    extract_aa,
    extract_arena,
    parse_aa_models,
    parse_arena_snapshots,
    parse_stated_date,
    propose_explicit_maps,
    ranked_benchmarks,
)


def _page(url: str, html: str, fetched_at: str = "2026-09-10") -> CachedPage:
    from pathlib import Path

    return CachedPage(
        url=url,
        path=Path("unused.html"),
        text=html,
        fetched_at=fetched_at,
        from_cache=True,
        meta={"fetched_at": fetched_at},
    )


def _next_f(obj: dict) -> str:
    inner = "3a:" + json.dumps(["$", "$L1", None, obj], separators=(",", ":"))
    payload = json.dumps([1, inner], separators=(",", ":"))
    return f"<script>self.__next_f.push({payload})</script>"


def test_next_f_decoder_does_not_skip_later_payloads() -> None:
    from scripts.fetch_ranking_leaderboards import iter_next_f_strings

    first = json.dumps([1, '1:"tiny"'], separators=(",", ":"))
    second = json.dumps(
        [1, "3a:" + json.dumps(["$", "$L1", None, {"models": [{"shortName": "Z", "gpqa": 0.5}]}], separators=(",", ":"))],
        separators=(",", ":"),
    )
    html = f"<script>self.__next_f.push({first})</script><script>self.__next_f.push({second})</script>"
    bodies = iter_next_f_strings(html)
    assert any("models" in body for body in bodies)


def test_aa_extracts_ranked_components_not_the_index() -> None:
    html = _next_f(
        {
            "models": [
                {
                    "shortName": "GPT-6 Astra (max)",
                    "slug": "gpt-6-astra",
                    "intelligenceIndex": 52.8,
                    "gpqa": 0.9606,
                    "scicode": 0.5648,
                    "lcr": 0.8067,
                    "gdpvalNormalized": 0.5401,
                    "critpt": 0.3171,
                    "mmmuPro": 0.86,
                    "terminalbenchV40": 0.59,
                }
            ]
        }
    )
    models = parse_aa_models(html)
    assert len(models) == 1
    scores, refusals = extract_aa(_page(AA_URL, html, "2026-09-08"), ranked_benchmarks())
    by_bench = {s.benchmark_id: s for s in scores}
    assert by_bench["gpqa_diamond"].score == 96.06
    assert by_bench["scicode"].unit == "percent"
    assert by_bench["aa_lcr"].score == 80.67
    assert by_bench["gdpval_aa"].score == 54.01
    assert by_bench["critpt"].evidence_date == "2026-09-08"
    assert by_bench["critpt"].date_type == "evaluated"
    assert by_bench["critpt"].date_source == "observation_fetch_date"
    ids = {s.benchmark_id for s in scores}
    assert "mmmu" not in ids
    assert "terminal_bench" not in ids
    causes = {r.extra: r.cause for r in refusals}
    assert causes["intelligenceIndex"] == "aa_field_not_ranked"
    assert causes["mmmuPro"] == "aa_field_not_ranked"
    assert causes["terminalbenchV40"] == "aa_field_not_ranked"


def test_arena_maps_style_control_overall_only() -> None:
    html = _next_f(
        {
            "leaderboard": {
                "id": "leaderboard-sets/public/leaderboards/text-overall-style_control/leaderboard-snapshots/latest",
                "entries": [
                    {
                        "modelDisplayName": "claude-fable-5",
                        "rating": 1507.164,
                        "votes": 27189,
                    }
                ],
            }
        }
    ).replace(
        '"id":"leaderboard-sets/public/leaderboards/text-overall-style_control/leaderboard-snapshots/latest"',
        '"id":"leaderboard-sets/public/leaderboards/text-overall-style_control/leaderboard-snapshots/latest","entries":',
    )
    # The replace above would break JSON. Build the real HTML the parser looks for.
    html = (
        "<script>self.__next_f.push("
        + json.dumps(
            [
                1,
                '15:["$","main",null,{"leaderboard":{"id":'
                '"leaderboard-sets/public/leaderboards/text-overall-style_control/'
                'leaderboard-snapshots/latest","entries":'
                + json.dumps(
                    [
                        {
                            "modelDisplayName": "claude-fable-5",
                            "rating": 1507.164,
                            "votes": 27189,
                        }
                    ],
                    separators=(",", ":"),
                )
                + ',"other":"leaderboard-sets/public/leaderboards/webdev-overall-raw/'
                'leaderboard-snapshots/latest","entries":'
                + json.dumps(
                    [
                        {
                            "modelDisplayName": "gpt-6-astra-max",
                            "rating": 1796.19,
                            "votes": 1810,
                        }
                    ],
                    separators=(",", ":"),
                )
                + "}}]",
            ],
            separators=(",", ":"),
        )
        + ")</script>"
    )
    snaps = parse_arena_snapshots(html)
    assert "text-overall-style_control" in snaps
    assert "webdev-overall-raw" in snaps
    scores, refusals = extract_arena(_page(ARENA_URL, html), ranked_benchmarks())
    assert len(scores) == 1
    assert scores[0].benchmark_id == "arena_elo_style_control"
    assert scores[0].score == 1507.16
    assert scores[0].unit == "elo"
    assert any(r.extra == "webdev-overall-raw" for r in refusals)
    assert all(s.benchmark_id != "arena_elo_coding" for s in scores)
    assert all(s.benchmark_id != "arena_elo_overall" for s in scores)


def test_stated_date_is_preferred_over_observation() -> None:
    html = "Last updated 2026-09-01\n" + _next_f(
        {
            "models": [
                {
                    "shortName": "Gemma 4 31B IT",
                    "gpqa": 0.843,
                    "scicode": None,
                    "lcr": None,
                    "gdpvalNormalized": None,
                    "critpt": None,
                }
            ]
        }
    )
    assert parse_stated_date(html) == "2026-09-01"
    scores, _ = extract_aa(_page(AA_URL, html, "2026-09-10"), ranked_benchmarks())
    assert scores[0].evidence_date == "2026-09-01"
    assert scores[0].date_source == "stated_on_page"


def test_propose_maps_exact_display_and_canonical_max_only() -> None:
    cards = [
        CardRef("openai/gpt-6-astra", "GPT-6 Astra", "gpt-6-astra", "gpt-6-astra"),
        CardRef("anthropic/claude-opus-5", "Claude Opus 5", "claude-opus-5", "claude-opus-5"),
        CardRef("moonshot/kimi-k3", "Kimi K3", "kimi-k3", "kimi-k3"),
        CardRef("cohere/command-a-03-2025", "Command A", "command-a-03-2025", "command-a"),
        CardRef(
            "cohere/command-a-plus-05-2026",
            "Command A Plus",
            "command-a-plus-05-2026",
            "command-a-plus",
        ),
        CardRef("meta/llama-3-1-405b", "Llama 3.1 405B", "llama-3-1-405b", "llama-3-1-405b"),
        CardRef(
            "meta/llama-3-1-405b-instruct",
            "Llama 3.1 405B Instruct",
            "llama-3-1-405b-instruct",
            "llama-3-1-405b-instruct",
        ),
        CardRef(
            "nous-research/meta-llama-3-8b",
            "Meta Llama 3 8B",
            "meta-llama-3-8b",
            "meta-llama-3-8b",
        ),
        CardRef(
            "meta/meta-llama-3-8b",
            "Meta Llama 3 8B",
            "meta-llama-3-8b",
            "meta-llama-3-8b",
        ),
    ]
    names = [
        "GPT-6 Astra (max)",
        "Claude Opus 5 (high)",
        "Claude Opus 5",
        "kimi-k3-max",
        "claude-opus-5-high",
        "Meta Llama 3 8B",
        "definitely-unknown-model",
        "Command A+",
        "Llama 3.1 405B",
        "Llama 3.1 405B Instruct",
    ]
    mapping, refusals = propose_explicit_maps(names, cards)
    assert mapping["GPT-6 Astra (max)"] == "openai/gpt-6-astra"
    assert mapping["Claude Opus 5"] == "anthropic/claude-opus-5"
    assert mapping["kimi-k3-max"] == "moonshot/kimi-k3"
    assert mapping["Command A+"] == "cohere/command-a-plus-05-2026"
    assert mapping["Llama 3.1 405B Instruct"] == "meta/llama-3-1-405b-instruct"
    assert "Llama 3.1 405B" not in mapping
    assert "Claude Opus 5 (high)" not in mapping
    assert "claude-opus-5-high" not in mapping
    assert "Meta Llama 3 8B" not in mapping
    causes = {r.name: r.cause for r in refusals}
    assert causes["Claude Opus 5 (high)"] == "effort_variant"
    assert causes["claude-opus-5-high"] == "effort_variant"
    assert causes["Meta Llama 3 8B"] == "ambiguous_name"
    assert causes["definitely-unknown-model"] == "unmapped_name"
    assert causes["Llama 3.1 405B"] == "ambiguous_name"


def test_cache_observation_date_is_not_today_when_meta_says_otherwise() -> None:
    html = _next_f(
        {
            "models": [
                {
                    "shortName": "X",
                    "gpqa": 0.5,
                    "scicode": None,
                    "lcr": None,
                    "gdpvalNormalized": None,
                    "critpt": None,
                }
            ]
        }
    )
    scores, _ = extract_aa(_page(AA_URL, html, "2026-08-01"), ranked_benchmarks())
    assert scores[0].evidence_date == "2026-08-01"
