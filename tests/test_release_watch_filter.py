"""Release-watch filtering at the CLI, report and issue-sink boundaries."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import httpx
import pytest
import yaml

from release_signals.contract import ReleaseSignal
from release_signals.watch import Response
from scripts import release_watch

NOW = datetime(2026, 10, 20, tzinfo=UTC)


def run_watch(tmp_path, monkeypatch, entries):
    sources = [
        {"id": "liquid-page", "kind": "page", "provider": "liquid",
         "url": "https://liquid.example/models", "pattern": "lfm-[a-z0-9.-]+",
         "confidence": 0.9},
        {"id": "hf-liquidai", "kind": "huggingface", "org": "LiquidAI",
         "provider": "liquid", "confidence": 0.7},
        {"id": "openrouter", "kind": "openrouter", "url": "https://openrouter.ai/api/v1/models",
         "providers": {"liquid": "liquid"}, "confidence": 0.8},
    ]
    registry = tmp_path / "registry.yaml"
    registry.write_text(yaml.safe_dump({
        "user_agent": "test", "recent_days": 30, "variant_exclude": "(gguf)",
        "page_exclude": "(docs)", "sources": sources,
    }))
    baseline = tmp_path / "baseline.json"
    baseline.write_text(json.dumps({"sources": {s["id"]: [] for s in sources}}))

    def fetch(url):
        if url.endswith("/robots.txt"):
            return Response(404, b"")
        if url.startswith("https://liquid.example/"):
            return Response(200, entries["page"].encode())
        if url.startswith("https://huggingface.co/"):
            return Response(200, json.dumps([
                {"id": f"LiquidAI/{name}", "createdAt": "2026-10-20T00:00:00Z"}
                for name in entries["hf"]
            ]).encode())
        return Response(200, json.dumps({"data": [
            {"id": f"liquid/{name}", "created": int(NOW.timestamp())}
            for name in entries["openrouter"]
        ]}).encode())

    monkeypatch.setattr(release_watch, "http_fetch", lambda user_agent: fetch)
    report = tmp_path / "watch.json"
    assert release_watch.main([
        "--registry", str(registry), "--baseline", str(baseline), "--report", str(report),
    ]) == 0
    return json.loads(report.read_text())


def test_cli_groups_sources_and_packaging_with_evidence_and_a_draft(tmp_path, monkeypatch):
    result = run_watch(tmp_path, monkeypatch, {
        "page": "<td>lfm-2.5-24b-a2b</td>",
        "hf": ["LFM2.5-24B-A2B", "LFM2.5-24B-A2B-BF16"],
        "openrouter": ["lfm-2.5-24b-a2b"],
    })
    assert [row["signal_id"] for row in result["discoveries"]] == [
        "watch:liquid:lfm-2-5-24b-a2b",
    ]
    group, = result["groups"]
    assert {e["source_id"] for e in group["evidence"]} == {
        "liquid-page", "hf-liquidai", "openrouter",
    }
    assert len(group["evidence"]) == 4
    assert group["draft_card"]["status"] == "draft"
    assert group["draft_card"]["release_date"] is None
    assert group["draft_card"]["model_name"] == "lfm-2.5-24b-a2b"
    assert len(group["draft_card"]["source_urls"]) == 4


def test_cli_drops_non_model_items_but_keeps_distinct_releases(tmp_path, monkeypatch):
    result = run_watch(tmp_path, monkeypatch, {
        "page": "<td>lfm-2.5-24b-a2b</td><td>lfm-sdk-2.0</td>",
        "hf": ["LFM2.5-24B-A2B-Base", "LFM2.6-24B-A2B", "LFM-blog-2",
               "LFM-docs-2", "LFM-client-2", "LFM2.5-8B"],
        "openrouter": ["lfm-2.5-24b-a2b"],
    })
    assert {row["signal_id"] for row in result["discoveries"]} == {
        "watch:liquid:lfm-2-5-24b-a2b", "watch:liquid:lfm-2-5-24b-a2b-base",
        "watch:liquid:lfm-2-6-24b-a2b", "watch:liquid:lfm-2-5-8b",
    }
    assert {row["model_name"] for row in result["rejected"]} == {
        "lfm-sdk-2.0", "LFM-blog-2", "LFM-docs-2", "LFM-client-2",
    }
    assert all(row["reason"] for row in result["rejected"])


def test_existing_legacy_alias_issue_prevents_a_second_issue():
    signal = ReleaseSignal.parse({
        "model_name": "lfm-2.5-24b-a2b", "provider": "liquid",
        "first_seen_url": "https://openrouter.ai/liquid/lfm-2.5-24b-a2b",
        "timestamp": "2026-10-20T00:00:00Z", "confidence": 0.8,
        "signal_id": "watch:liquid:lfm-2-5-24b-a2b",
    }, discovered=True)

    def handler(request):
        assert request.method == "GET", "the legacy alias already owns this release"
        return httpx.Response(200, json=[{
            "title": "release discovery `watch:liquid:lfm2-5-24b-a2b-bf16`",
            "state": "closed",
        }])

    outcomes = release_watch.file_issues(
        [signal], repository="owner/repo", token="test",
        client=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    assert [(row["ok"], row["filed"]) for row in outcomes] == [(True, False)]


@pytest.mark.parametrize(("provider", "names", "expected"), [
    ("anthropic", ["claude-sonnet-4-5", "claude-sonnet-4.5-20250929"],
     ("anthropic", "claude-sonnet-4-5")),
    ("Alibaba / Qwen Team", ["Qwen3.5-8B", "qwen3.5-8b-bf16"],
     ("alibaba-qwen-team", "qwen3-5-8b")),
    ("nvidia", ["NVIDIA-Nemotron-3.5-Super-VL-120B-A12B-BF16",
                "nemotron-3.5-super-vl"],
     ("nvidia", "nemotron-3-5-super-vl-120b-a12b")),
    ("ifm", ["LoopedLM-P1-dense-d112-336b", "LoopedLM-P1-dense-d112-500b"],
     ("ifm", "loopedlm-p1-dense-d112")),
    ("nvidia", ["NVIDIA-Nemotron-Labs-Dory1.0-4B-BF16",
                "NVIDIA-Nemotron-Labs-Dory1.0-4B-MXFP8"],
     ("nvidia", "nemotron-labs-dory1-0-4b")),
])
def test_release_aliases_share_an_identity(provider, names, expected):
    from scripts.release_watch_filter import canonical_release

    assert [canonical_release(provider, name) for name in names] == [expected] * len(names)


def test_mirrors_share_the_upstream_release_without_merging_other_labs():
    from scripts.release_watch_filter import canonical_release

    assert canonical_release("unsloth", "LFM2.5-24B-A2B") == (
        "liquid", "lfm-2-5-24b-a2b",
    )
    assert canonical_release("unsloth", "embeddinggemma-2") == ("google", "embeddinggemma-2")
    assert canonical_release("some-other-lab", "embeddinggemma-2") == (
        "some-other-lab", "embeddinggemma-2",
    )


def test_named_minor_versions_sizes_and_tuning_are_distinct():
    from scripts.release_watch_filter import canonical_release

    names = ["gemini-2.0", "gemini-2.5", "gemma-3-4b", "gemma-3-12b",
             "gemma-3-4b-base", "gemma-3-4b-instruct", "gemini-2.5-flash",
             "gemini-2.5-flash-lite", "gemini-2.5-pro"]
    assert len({canonical_release("google", name) for name in names}) == len(names)


def test_issue_contains_draft_even_when_called_without_a_report():
    signal = ReleaseSignal.parse({
        "model_name": "acme-two-2", "provider": "acme",
        "first_seen_url": "https://acme.example/models",
        "timestamp": "2026-10-20T00:00:00Z", "confidence": 0.9,
        "signal_id": "watch:acme:acme-two-2",
    }, discovered=True)
    bodies = []

    def handler(request):
        if request.method == "GET":
            return httpx.Response(200, json=[])
        bodies.append(json.loads(request.content)["body"])
        return httpx.Response(201, json={"number": 1})

    release_watch.file_issues(
        [signal], repository="owner/repo", token="test",
        client=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    body, = bodies
    assert "### Draft card" in body
    assert "release_date: null" in body
    assert "https://acme.example/models" in body


def test_workflow_keeps_normalized_reports_for_a_30_day_replay():
    workflow = yaml.safe_load(Path(".github/workflows/release-watch.yml").read_text())
    uploads = [
        step for step in workflow["jobs"]["watch"]["steps"]
        if step.get("uses", "").startswith("actions/upload-artifact@")
    ]
    assert len(uploads) == 1
    assert uploads[0]["if"] == "always()"
    assert uploads[0]["with"]["retention-days"] >= 30
    assert "watch.json" in uploads[0]["with"]["path"]


def test_separately_released_dated_models_are_not_aliases():
    from scripts.release_watch_filter import canonical_release

    assert canonical_release("anthropic", "claude-3-5-sonnet-20240620") != canonical_release(
        "anthropic", "claude-3-5-sonnet-20241022",
    )
    assert canonical_release("openai", "gpt-4o-2024-05-13") != canonical_release(
        "openai", "gpt-4o-2024-11-20",
    )


def test_experiment_recipes_and_unverified_exports_remain_distinct():
    from scripts.release_watch_filter import canonical_release, rejection_reason

    assert canonical_release("ifm", "LoopedLM-P1-dense-d112-336b") != canonical_release(
        "ifm", "LoopedLM-P1-moe-huginn-500b",
    )
    assert canonical_release("nvidia", "cosmos3-nano-libero10-sdg-export-D") != canonical_release(
        "nvidia", "cosmos3-nano-libero10-sdg-export-S_best",
    )
    assert rejection_reason("openbmb", "Trident-Train") is None


def test_offline_replay_reproduces_groups_without_fetch_or_post(tmp_path, monkeypatch):
    first = run_watch(tmp_path, monkeypatch, {
        "page": "<td>lfm-2.5-24b-a2b</td>",
        "hf": ["LFM2.5-24B-A2B", "LFM2.5-24B-A2B-BF16"],
        "openrouter": ["lfm-2.5-24b-a2b"],
    })

    def forbidden(*args, **kwargs):
        pytest.fail("replay attempted a network operation")

    monkeypatch.setattr(release_watch, "http_fetch", forbidden)
    monkeypatch.setattr(httpx.Client, "request", forbidden)
    output = tmp_path / "replay.json"
    assert release_watch.main([
        "--registry", str(tmp_path / "registry.yaml"),
        "--replay", str(tmp_path / "watch.json"),
        "--replay", str(tmp_path / "watch.json"), "--report", str(output),
    ]) == 0
    replayed = json.loads(output.read_text())
    assert replayed["groups"] == first["groups"]
    assert replayed["discoveries"] == first["discoveries"]
    assert replayed["posted"] is None
    for mode in ("--issues", "--post", "--rebaseline"):
        with pytest.raises(SystemExit) as error:
            release_watch.main(["--replay", str(output), mode])
        assert error.value.code == 2


def test_public_issue_replay_keeps_each_newly_carded_release_once(tmp_path, monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("historical replay attempted network access")

    monkeypatch.setattr(release_watch, "http_fetch", forbidden)
    output = tmp_path / "replay.json"
    assert release_watch.main([
        "--replay", "docs/evidence/g2-ios/MODEL-432-discovery-inputs.json",
        "--report", str(output),
    ]) == 0
    report = json.loads(output.read_text())
    ids = [row["signal_id"] for row in report["discoveries"]]
    assert len(ids) == len(set(ids))
    # Independently compared with additions in the private data history.
    # Earlier cards and backfilled old releases are not new watcher releases.
    for identifier in (
        "watch:google:gemini-4-argon", "watch:anthropic:claude-haiku-5-5",
        "watch:xai:grok-imagine-video-1-5-lite", "watch:mistral:mistral-large-4",
    ):
        assert ids.count(identifier) == 1
    retained = {
        row["source_key"] for group in report["groups"] for row in group["evidence"]
    }
    rejected = {row["source_key"] for row in report["rejected"]}
    original = json.loads(Path(
        "docs/evidence/g2-ios/MODEL-432-discovery-inputs.json",
    ).read_text())
    assert len(retained) == 176
    assert rejected == {"watch:ibm:ensemble-forecasting-with-ibm-granite-time-series"}
    assert retained | rejected == {row["source_key"] for row in original["observations"]}
