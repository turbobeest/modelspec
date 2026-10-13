"""MODEL-364: named model comparison through the keyed CLI boundary."""

from __future__ import annotations

import json
import re

import httpx
import pytest
from typer.testing import CliRunner

from cli.modelspec import cli, client

KEY = "live_model364_test_secret"
MODELS = ["lab/first", "other/second"]
COMPARISON = {
    "contract_version": "3.0",
    "endpoint": "compare-models",
    "snapshot": "snap_current",
    "models": [
        {
            "model": "lab/first",
            "lifecycle": "active",
            "facts": [
                {
                    "facet": "model.context_window",
                    "state": "known",
                    "value": 200000,
                    "unit": "tokens",
                    "record_id": "first#context",
                    "source_ids": ["docs"],
                },
                {
                    "facet": "model.parameters",
                    "state": "unknown",
                    "value": None,
                    "unit": "billion_parameters",
                },
            ],
            "offerings": [
                {
                    "offering": {
                        "model": "lab/first",
                        "provider": "provider",
                        "region": "global",
                        "tier": "standard",
                    },
                    "facts": [
                        {
                            "facet": "offering.price_input",
                            "state": "known",
                            "value": 1.25,
                            "unit": "usd_per_million_tokens",
                            "record_id": "first#price",
                            "source_ids": ["docs"],
                        }
                    ],
                }
            ],
            "evidence": [
                {
                    "benchmark": "coding",
                    "value": 0.8,
                    "unit": "fraction",
                    "record_id": "first#coding",
                    "source_ids": ["benchmarks"],
                    "version": "v1",
                    "effort": "high",
                    "harness": "agent",
                    "measured_by": "lab",
                    "date": "2026-10-01",
                }
            ],
        },
        {
            "model": "other/second",
            "lifecycle": "retired",
            "facts": [
                {
                    "facet": "model.context_window",
                    "state": "unknown",
                    "value": None,
                    "unit": "tokens",
                }
            ],
            "offerings": [],
            "evidence": [
                {
                    "benchmark": "coding",
                    "value": 0.6,
                    "unit": "fraction",
                    "version": "v2",
                    "effort": "low",
                    "harness": "other-agent",
                }
            ],
        },
    ],
    "sources": [
        {"id": "docs", "url": "https://example.test/docs"},
        {"id": "benchmarks", "url": "https://example.test/benchmarks"},
    ],
    "omitted": {"facts": 1, "offerings": 2, "evidence": 3},
}
API_TEXT = " \n" + json.dumps(COMPARISON, indent=2) + "\n"


@pytest.fixture(autouse=True)
def isolated(monkeypatch, tmp_path):
    monkeypatch.delenv("MODELSPEC_API_KEY", raising=False)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
    monkeypatch.chdir(tmp_path)

    def forbidden(request):
        raise AssertionError("Local refusal tried HTTP")

    monkeypatch.setattr(client, "_transport", httpx.MockTransport(forbidden))


def run(args, *, keyed=True):
    return CliRunner().invoke(cli.app, args, env={"MODELSPEC_API_KEY": KEY} if keyed else {})


@pytest.mark.parametrize(
    "models", [MODELS, ["bad"], ["bad", "bad"], ["a/a", "b/b", "c/c", "d/d", "e/e"]]
)
def test_keyless_named_compare_refuses_exactly_like_decide_before_validation(models):
    result = run(["compare", *models, "--json"], keyed=False)
    decide = run(["decide", "--spec", "missing", "--json"], keyed=False)
    assert result.exit_code == decide.exit_code == 5, result.output
    body, decide_body = json.loads(result.stdout), json.loads(decide.stdout)
    assert body["command"] == "modelspec compare"
    assert body == {**decide_body, "command": "modelspec compare"}


@pytest.mark.parametrize(
    "extra", [["--spec", "missing"], ["--template", "id"], ["--to", "snap_old"]]
)
def test_keyless_named_compare_refuses_before_snapshot_flag_validation(extra):
    result = run(["compare", *MODELS, *extra, "--json"], keyed=False)
    assert result.exit_code == 5, result.output
    assert json.loads(result.stdout)["error"]["code"] == "missing_api_key"


@pytest.mark.parametrize(
    "models", [MODELS, [*MODELS, "third/model"], [*MODELS, "third/model", "fourth/model"]]
)
@pytest.mark.parametrize("json_at_root", [False, True])
def test_named_compare_posts_only_requested_models_and_preserves_json_bytes(
    monkeypatch, models, json_at_root
):
    calls = []

    def handler(request):
        calls.append(request)
        assert request.method == "POST"
        assert request.url == "https://api.modelspec.dev/v1/compare-models"
        assert request.headers["authorization"] == "Bearer live_model364_test_secret"
        assert json.loads(request.content) == {"models": models}
        return httpx.Response(200, text=API_TEXT)

    monkeypatch.setattr(client, "_transport", httpx.MockTransport(handler))
    args = ["--json", "compare", *models] if json_at_root else ["compare", *models, "--json"]
    result = run(args)
    assert result.exit_code == 0, result.output
    assert result.stdout_bytes == API_TEXT.encode("utf-8")
    assert result.stderr == ""
    assert len(calls) == 1


@pytest.mark.parametrize(
    "models",
    [
        ["lab/first"],
        [*MODELS, "third/model", "fourth/model", "fifth/model"],
        ["lab/first", "lab/first"],
        ["bare", "other/second"],
        ["Lab/first", "other/second"],
        ["lab/first/variant", "other/second"],
        ["lab/first\n", "other/second"],
        ["lab/" + "a" * 125, "other/second"],
    ],
)
def test_named_compare_validates_count_distinctness_and_model_ids_before_http(models):
    result = run(["compare", *models, "--json"])
    assert result.exit_code == 1, result.output
    payload = json.loads(result.stdout)
    assert payload["error"]["code"] == "invalid_compare_models"
    assert "modelspec compare LAB/MODEL LAB/MODEL [LAB/MODEL LAB/MODEL]" in payload["next"][-1]


@pytest.mark.parametrize(
    "extra", [["--spec", "missing"], ["--template", "id"], ["--to", "snap_old"]]
)
def test_named_models_and_snapshot_arguments_are_mutually_exclusive(extra):
    result = run(["compare", *MODELS, *extra, "--json"])
    assert result.exit_code == 1, result.output
    assert json.loads(result.stdout)["error"]["code"] == "usage_error"


def test_human_named_comparison_shows_model_columns_facts_prices_evidence_and_sources(monkeypatch):
    monkeypatch.setattr(
        client,
        "_transport",
        httpx.MockTransport(lambda request: httpx.Response(200, json=COMPARISON)),
    )
    result = run(["compare", *MODELS])
    assert result.exit_code == 0, result.output
    assert result.stdout.splitlines() == [
        "Model comparison: snap_current",
        "| Fact or evidence | lab/first | other/second |",
        "| --- | --- | --- |",
        "| lifecycle | active | retired |",
        "| model.context_window | 200000 tokens [record: first#context] "
        "[sources: docs] | unknown |",
        "| model.parameters | unknown | not shown |",
        "| offering (provider=provider, region=global, tier=standard) | available | not shown |",
        "| offering.price_input (provider=provider, region=global, tier=standard) | "
        "1.25 usd_per_million_tokens [record: first#price] [sources: docs] | not shown |",
        "| coding (version=v1, effort=high, harness=agent, measured_by=lab, date=2026-10-01) | "
        "0.8 fraction [record: first#coding] [sources: benchmarks] | not shown |",
        "| coding (version=v2, effort=low, harness=other-agent) | not shown | 0.6 fraction |",
        "Omitted: facts=1, offerings=2, evidence=3",
        "Sources:",
        "  docs: https://example.test/docs",
        "  benchmarks: https://example.test/benchmarks",
    ]
    assert result.stderr == ""


def test_human_named_comparison_retains_conflicting_values_and_empty_sections(monkeypatch):
    comparison = json.loads(API_TEXT)
    comparison["models"][0]["facts"] = [
        {"facet": "model.context_window", "state": "known", "value": 100, "unit": "tokens"},
        {"facet": "model.context_window", "state": "unknown", "value": None, "unit": "tokens"},
        {"facet": "model.function_calling", "state": "known", "value": False, "unit": "bool"},
    ]
    comparison["models"][0]["offerings"] = []
    comparison["models"][0]["evidence"] = []
    comparison["sources"] = []
    comparison["omitted"] = {"facts": 0, "offerings": 0, "evidence": 0}
    monkeypatch.setattr(
        client,
        "_transport",
        httpx.MockTransport(lambda request: httpx.Response(200, json=comparison)),
    )
    result = run(["compare", *MODELS])
    assert result.exit_code == 0, result.output
    assert "| model.context_window | 100 tokens; unknown | unknown |" in result.stdout
    assert "| model.function_calling | false bool | not shown |" in result.stdout
    assert "Omitted: facts=0, offerings=0, evidence=0" in result.stdout


def test_missing_values_are_not_shown_instead_of_reported_unknown_when_response_is_bounded(
    monkeypatch,
):
    comparison = json.loads(API_TEXT)
    comparison["models"][0]["facts"] = [
        {"facet": "model.context_window", "state": "known", "value": 100, "unit": "tokens"},
        {"facet": "model.parameters", "state": "unknown", "value": None, "unit": "billions"},
    ]
    comparison["models"][1]["facts"] = []
    monkeypatch.setattr(
        client,
        "_transport",
        httpx.MockTransport(lambda request: httpx.Response(200, json=comparison)),
    )
    result = run(["compare", *MODELS])
    assert result.exit_code == 0, result.output
    assert "| model.context_window | 100 tokens | not shown |" in result.stdout
    assert "| model.parameters | unknown | not shown |" in result.stdout
    assert (
        "| offering (provider=provider, region=global, tier=standard) | available | not shown |"
        in result.stdout
    )
    assert (
        "| coding (version=v2, effort=low, harness=other-agent) | not shown | 0.6 fraction |"
        in result.stdout
    )
    assert "Omitted: facts=1, offerings=2, evidence=3" in result.stdout


def test_human_named_comparison_preserves_evidence_subcategory_interval_and_sample_count(
    monkeypatch,
):
    comparison = json.loads(API_TEXT)
    comparison["models"][0]["evidence"] = [
        {
            "benchmark": "coding",
            "version": "v1",
            "subcategory": "python",
            "value": 0.8,
            "unit": None,
            "interval": [0.7, 0.9],
            "n": 20,
        },
    ]
    comparison["models"][1]["evidence"] = [
        {
            "benchmark": "coding",
            "version": "v1",
            "subcategory": "rust",
            "value": 0.6,
            "unit": None,
            "interval": [0.55, 0.65],
            "n": 30,
        },
    ]
    monkeypatch.setattr(
        client,
        "_transport",
        httpx.MockTransport(lambda request: httpx.Response(200, json=comparison)),
    )
    result = run(["compare", *MODELS])
    assert result.exit_code == 0, result.output
    assert (
        "| coding (version=v1, subcategory=python) | "
        "0.8 [interval: [0.7, 0.9]] [n: 20] | not shown |" in result.stdout
    )
    assert (
        "| coding (version=v1, subcategory=rust) | not shown | "
        "0.6 [interval: [0.55, 0.65]] [n: 30] |" in result.stdout
    )


@pytest.mark.parametrize(
    "status,code,exit_code",
    [
        (401, "invalid_api_key", 5),
        (402, "payment_required", 6),
        (429, "rate_limited", 6),
        (503, "export_unavailable", 1),
    ],
)
def test_named_compare_uses_existing_hosted_error_recovery(monkeypatch, status, code, exit_code):
    monkeypatch.setattr(
        client,
        "_transport",
        httpx.MockTransport(
            lambda request: httpx.Response(
                status, json={"error": {"code": code, "message": "refused"}}
            )
        ),
    )
    result = run(["compare", *MODELS, "--json"])
    assert result.exit_code == exit_code, result.output
    payload = json.loads(result.stdout)
    assert payload["error"] == {"code": code, "message": "refused"}
    assert payload["next"]
    assert KEY not in result.output


@pytest.mark.parametrize("body", [{}, {"models": []}, {"models": None}])
def test_human_named_compare_malformed_response_has_actionable_recovery(monkeypatch, body):
    monkeypatch.setattr(
        client, "_transport", httpx.MockTransport(lambda request: httpx.Response(200, json=body))
    )
    result = run(["compare", *MODELS])
    assert result.exit_code == 1, result.output
    assert not isinstance(result.exception, KeyError | TypeError | AttributeError)
    assert "The hosted API did not return the expected JSON object." in result.stderr
    assert "Next steps:" in result.stderr


def test_compare_help_distinguishes_named_models_and_snapshot_forms():
    result = CliRunner().invoke(cli.app, ["compare", "--help"], env={"COLUMNS": "200"})
    assert result.exit_code == 0, result.output
    text = re.sub(r"\x1b\[[0-9;]*m", "", result.stdout)
    assert "POST /v1/compare-models" in text
    assert "2 to 4" in text
    assert "--spec" in text and "--template" in text and "--to" in text
