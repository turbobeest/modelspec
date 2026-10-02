"""The answer-engine visibility harness (MODEL-256). No network: engines are faked."""

from __future__ import annotations

import json
from datetime import UTC, date, datetime
from pathlib import Path

import pytest

from scripts.aeo import engines, visibility
from scripts.aeo.engines import Answer, Citation, EngineUnavailable
from scripts.aeo.visibility import Config, EngineConfig, detect

# ── adapters: shapes as the APIs returned them on 2026-10-01 ─────────────────


def test_openai_parse_reads_text_citations_and_fanout() -> None:
    body = {"model": "gpt-6-sol-2026", "usage": {"input_tokens": 1000, "output_tokens": 200},
            "output": [
                {"type": "web_search_call", "action": {"type": "search", "queries": ["a", "b"], "query": "a"}},
                {"type": "message", "content": [{"type": "output_text", "text": "Use modelspec.dev.",
                                                  "annotations": [{"type": "url_citation", "url": "https://www.modelspec.dev/method/",
                                                                   "title": "How ModelSpec decides"}]}]}]}
    a = engines.openai_parse(body)
    assert (a.text, a.model_version, a.fanout_queries, a.searches) == ("Use modelspec.dev.", "gpt-6-sol-2026", ["a", "b"], 1)
    assert a.citations == [Citation("https://www.modelspec.dev/method/", "modelspec.dev", "How ModelSpec decides")]
    assert (a.input_tokens, a.output_tokens, a.searched) == (1000, 200, True)


def test_anthropic_parse_counts_searches_and_reads_cited_results() -> None:
    body = {"model": "claude-sonnet-5-5", "usage": {"input_tokens": 50, "output_tokens": 9,
                                                     "server_tool_use": {"web_search_requests": 2}},
            "content": [{"type": "thinking", "thinking": "..."},
                        {"type": "server_tool_use", "name": "web_search", "input": {"query": "choose llm"}},
                        {"type": "web_search_tool_result", "content": [
                            {"type": "web_search_result", "url": "https://example.com/a", "title": "A"}]},
                        {"type": "text", "text": "Answer.", "citations": [
                            {"type": "web_search_result_location", "url": "https://example.com/a", "title": "A"}]}]}
    a = engines.anthropic_parse(body)
    assert (a.text, a.fanout_queries, a.searches, a.searched) == ("Answer.", ["choose llm"], 2, True)
    assert [c.domain for c in a.citations] == ["example.com"]


def test_anthropic_parse_records_an_answer_that_did_not_search() -> None:
    a = engines.anthropic_parse({"model": "m", "usage": {"input_tokens": 1, "output_tokens": 1},
                                 "content": [{"type": "text", "text": "From memory."}]})
    assert (a.searched, a.searches, a.citations) == (False, 0, [])


def test_perplexity_parse_prefers_reported_cost_and_search_results() -> None:
    body = {"model": "sonar", "choices": [{"message": {"content": "Text"}}],
            "citations": ["https://x.org/1"],
            "search_results": [{"url": "https://learn.microsoft.com/a", "title": "MS"}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 686, "cost": {"total_cost": 0.0057}}}
    a = engines.perplexity_parse(body)
    assert [c.domain for c in a.citations] == ["learn.microsoft.com"]
    assert a.reported_cost_usd == 0.0057


def test_gemini_parse_takes_the_domain_from_the_title_behind_the_redirect() -> None:
    body = {"modelVersion": "gemini-flash-latest", "usageMetadata": {"promptTokenCount": 5, "candidatesTokenCount": 7},
            "candidates": [{"content": {"parts": [{"text": "Hi"}]}, "groundingMetadata": {
                "webSearchQueries": ["q1"],
                "groundingChunks": [{"web": {"uri": "https://vertexaisearch.cloud.google.com/grounding-api-redirect/x",
                                             "title": "modelspec.dev"}}]}}]}
    a = engines.gemini_parse(body)
    assert [c.domain for c in a.citations] == ["modelspec.dev"]
    assert (a.fanout_queries, a.searched) == (["q1"], True)


def test_xai_parse_reads_the_openai_shape_and_its_own_reported_cost() -> None:
    body = {"model": "grok-4.20-0309-non-reasoning",
            "usage": {"input_tokens": 58191, "output_tokens": 1657, "cost_in_usd_ticks": 790876500},
            "output": [{"type": "web_search_call", "action": {"type": "search", "query": "choose ai model"}},
                       {"type": "web_search_call", "action": {"type": "open_page", "url": "https://benchlm.ai/x"}},
                       {"type": "message", "content": [{"type": "output_text", "text": "Pick by task.", "annotations": [
                           {"type": "url_citation", "url": "https://benchlm.ai/tools/llm-selector"}]}]}]}
    a = engines.xai_parse(body)
    assert (a.text, a.fanout_queries, a.searches) == ("Pick by task.", ["choose ai model"], 2)
    assert [c.domain for c in a.citations] == ["benchlm.ai"]
    assert a.reported_cost_usd == pytest.approx(0.0790876)
    assert engines.xai_request("m", "q", 100)["max_turns"] == engines.XAI_MAX_TURNS == 1


def test_a_quota_refusal_is_unavailable_not_retried() -> None:
    import httpx

    response = httpx.Response(429, text='{"error":{"status":"RESOURCE_EXHAUSTED"}}',
                              request=httpx.Request("POST", "https://x"))
    with pytest.raises(EngineUnavailable, match="gemini: HTTP 429"):
        engines._raise_for(response, "gemini")


# ── detection ────────────────────────────────────────────────────────────────


@pytest.mark.parametrize(("text", "domains", "expected"), [
    ("Try modelspec.dev to choose a model.", [], dict(mentioned=True, recommended=True, cited=False)),
    ("ModelSpec ranks models from benchmarks.", [], dict(mentioned=True, recommended=False, cited=False)),
    ("OpenAI's Model Spec defines model behaviour.", [], dict(mentioned=False, confused_with=("openai-model-spec",))),
    ("modelspec is a NeuroML package for model specification.", [],
     dict(mentioned=False, confused_with=("pypi-modelspec",))),
    ("Compare benchmarks.", ["a.com", "b.com", "modelspec.dev"], dict(mentioned=True, cited=True, cited_top3=True)),
    ("Compare benchmarks.", ["a.com", "b.com", "c.com", "modelspec.dev"], dict(cited=True, cited_top3=False)),
])
def test_detection(text: str, domains: list[str], expected: dict[str, object]) -> None:
    d = detect(text, domains)
    for field, value in expected.items():
        assert getattr(d, field) == value, field
    assert d.accurate is None


# ── money and the run ────────────────────────────────────────────────────────

ENGINE = EngineConfig(name="openai", model="m", key="op://vault/item/field", price_in=2.0, price_out=10.0,
                      search_fee=0.01, est_call_usd=0.05)
PROMPTS = [{"id": f"p{i}", "text": f"prompt {i}", "cluster": "category", "success": "mentioned"} for i in range(3)]
AT = datetime(2026, 10, 2, 6, 0, tzinfo=UTC)


def _answer(text: str = "Use modelspec.dev for model selection.") -> Answer:
    return Answer(text=text, model_version="m-1", citations=[Citation("https://modelspec.dev/", "modelspec.dev")],
                  input_tokens=10_000, output_tokens=1_000, searches=1, searched=True, raw={"ok": True})


def test_call_cost_prices_tokens_and_searches_unless_the_engine_reports_one() -> None:
    assert visibility.call_cost(ENGINE, _answer()) == pytest.approx(0.02 + 0.01 + 0.01)
    reported = _answer()
    reported.reported_cost_usd = 0.0057
    assert visibility.call_cost(ENGINE, reported) == 0.0057


def test_config_refuses_a_literal_key(tmp_path: Path) -> None:
    path = tmp_path / "engines.yaml"
    path.write_text("monthly_cap_usd: 15\nengines:\n  openai: {model: m, key: sk-live, price_in: 1, "
                    "price_out: 1, search_fee: 0, est_call_usd: 0.01}\n")
    with pytest.raises(ValueError, match="op:// references"):
        visibility.load_config(path)


def _run(tmp_path: Path, *, cap: float, call, key=lambda ref: "secret") -> Path:
    config = Config(monthly_cap_usd=cap, max_output_tokens=500, engines=(ENGINE,))
    return visibility.run(PROMPTS, config, runs_root=tmp_path, today=date(2026, 10, 2),
                          calls={"openai": call}, key=key, now=lambda: AT)


def test_a_run_stores_every_answer_and_the_month_spend(tmp_path: Path) -> None:
    seen: list[str] = []

    def call(model: str, key: str, prompt: str, max_tokens: int) -> Answer:
        seen.append(prompt)
        assert (model, key, max_tokens) == ("m", "secret", 500)
        return _answer()

    out = _run(tmp_path, cap=15, call=call)
    rows = [json.loads(line) for line in (out / "runs.jsonl").read_text().splitlines()]
    assert seen == ["prompt 0", "prompt 1", "prompt 2"]
    assert [r["prompt_id"] for r in rows] == ["p0", "p1", "p2"]
    assert all(r["surface"] == "api" and r["success"] and r["detection"]["cited"] for r in rows)
    assert json.loads((out / "raw" / "openai" / "p0.json").read_text()) == {"ok": True}
    assert "secret" not in (out / "runs.jsonl").read_text()
    assert visibility.month_spend(tmp_path, "2026-10") == pytest.approx(3 * 0.04)
    assert visibility.month_spend(tmp_path, "2026-11") == 0


def test_an_engine_whose_estimate_would_cross_the_cap_does_not_start(tmp_path: Path) -> None:
    out = _run(tmp_path, cap=0.10, call=lambda *a: pytest.fail("called over budget"))
    log = json.loads((out / "engines.json").read_text())
    assert log["engines"][0]["status"] == "skipped"
    assert log["engines"][0]["reason"] == "budget: $0.00 spent + $0.15 estimate > $0.10 cap"


def test_the_run_stops_once_the_cap_is_reached(tmp_path: Path) -> None:
    expensive = _answer()
    expensive.reported_cost_usd = 0.20
    out = _run(tmp_path, cap=0.25, call=lambda *a: expensive)
    log = json.loads((out / "engines.json").read_text())["engines"][0]
    assert (log["status"], log["runs"]) == ("stopped", 2)


def test_an_unavailable_engine_is_recorded_with_its_reason(tmp_path: Path) -> None:
    def refuse(*args):
        raise EngineUnavailable("gemini: HTTP 429: quota")

    out = _run(tmp_path, cap=15, call=refuse)
    log = json.loads((out / "engines.json").read_text())["engines"][0]
    assert (log["status"], log["reason"]) == ("unavailable", "gemini: HTTP 429: quota")


def test_the_report_labels_the_surface_and_shows_deltas_against_a_baseline(tmp_path: Path) -> None:
    base_dir = _run(tmp_path / "base", cap=15, call=lambda *a: _answer("Nothing relevant here."))
    visibility.write_report(base_dir)
    out = _run(tmp_path / "now", cap=15, call=lambda *a: _answer())
    text = visibility.write_report(out, base_dir)
    assert "**Surface: API**" in text
    assert "| category/openai | 3 | 100% (+0 pts) |" in text  # cited in both runs: mentioned either way
    summary = json.loads((out / "summary.json").read_text())
    assert summary["cells"]["category/openai"]["mentioned"] == 1.0
    assert summary["top_cited_domains"]["category"] == [["modelspec.dev", 3]]
