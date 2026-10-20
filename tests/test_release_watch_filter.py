"""Release-watch filtering at the CLI, report and issue-sink boundaries."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import UTC, datetime, timedelta
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
               "LFM-docs-2", "LFM-client-2", "LFM2.5-8B", "sdk", "liquid-docs"],
        "openrouter": ["lfm-2.5-24b-a2b"],
    })
    assert {row["signal_id"] for row in result["discoveries"]} == {
        "watch:liquid:lfm-2-5-24b-a2b", "watch:liquid:lfm-2-5-24b-a2b-base",
        "watch:liquid:lfm-2-6-24b-a2b", "watch:liquid:lfm-2-5-8b",
        "watch:liquid:lfm-sdk-2-0", "watch:liquid:lfm-blog-2",
        "watch:liquid:lfm-docs-2", "watch:liquid:lfm-client-2",
    }
    assert {row["model_name"] for row in result["rejected"]} == {
        "sdk", "liquid-docs",
    }
    assert all(row["reason"] for row in result["rejected"])


@pytest.mark.parametrize("name", [
    "ERNIE-5-Docs", "Pixtral-Docs", "ocr-doc", "client-embed-1", "guide-7b",
    "Example-LM", "agent-sdk-model-7b",
])
def test_huggingface_model_names_with_artifact_tokens_stay_discoveries(
    tmp_path, monkeypatch, name,
):
    result = run_watch(tmp_path, monkeypatch, {
        "page": "<td>lfm-2</td>", "hf": [name], "openrouter": ["lfm-2"],
    })
    assert name in {row["model_name"] for row in result["discoveries"]}
    assert name in release_watch.summary(result)
    assert not result["rejected"]


def test_summary_lists_every_rejected_item_with_reason_and_source(tmp_path, monkeypatch):
    result = run_watch(tmp_path, monkeypatch, {
        "page": "<td>lfm-2</td>",
        "hf": ["docs", "liquid-sdk", "guide-liquid"],
        "openrouter": ["client"],
    })
    assert len(result["rejected"]) == 4
    text = release_watch.summary(result)
    assert "### Rejected (not filed)" in text
    for row in result["rejected"]:
        assert row["model_name"] in text
        assert row["reason"] in text
        assert row["source_id"] in text
        assert row["url"] in text


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


def recall_fixture(tmp_path):
    catalogue = tmp_path / "catalogue"
    catalogue.mkdir()

    def git(*args, stamp=None):
        env = {**os.environ, "GIT_CONFIG_NOSYSTEM": "1",
               "GIT_CONFIG_GLOBAL": os.devnull}
        if stamp:
            env.update(GIT_AUTHOR_DATE=stamp, GIT_COMMITTER_DATE=stamp)
        return subprocess.run(
            ["git", "-C", str(catalogue), *args], check=True, capture_output=True,
            text=True, env=env,
        ).stdout.strip()

    git("init", "-b", "main")
    git("config", "user.name", "Recall fixture")
    git("config", "user.email", "fixture@example.invalid")
    git("config", "commit.gpgsign", "false")

    def card(name, stamp, version=None):
        path = catalogue / "models" / "liquid" / f"{name}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            f"---\nmodel_id: liquid/{name}\nprovider: liquid\n"
            f"display_name: {name}\nversion: {version or name}\n"
            "release_date: 2020-01-01\n---\nPRIVATE BODY MUST NOT LEAK\n",
        )
        git("add", ".")
        git("commit", "-m", name, stamp=stamp)

    card("old", "2026-10-20T23:59:59Z")
    card("Pixtral-Docs", "2026-10-21T00:00:00Z")
    card("docs", "2026-11-01T00:00:00Z")
    card("missing-2", "2026-11-02T00:00:00Z")
    git("switch", "-c", "card-branch")
    card("alias-card", "2026-10-20T00:00:00Z", "LFM2.5-24B-A2B")
    git("switch", "main")
    git("merge", "--no-ff", "-m", "Add reviewed card", "card-branch",
        stamp="2026-11-19T23:59:59Z")
    card("outside", "2026-11-20T00:00:00Z")
    # The comparison must read the added revision, not this later edit.
    card("Pixtral-Docs", "2026-11-21T00:00:00Z", "renamed-99")
    reports = []
    for day in range(-1, 31):
        stamp = datetime(2026, 10, 21, tzinfo=UTC) + timedelta(days=day)
        names = ["missing-2"] if day in (-1, 30) else []
        if day == 0:
            names = ["Pixtral-Docs", "docs", "LFM2.5-24B-A2B-BF16"]
        observations = [{
            "source_id": "hf-liquidai", "source_key": f"LiquidAI/{name}",
            "model_name": name, "provider": "liquid",
            "url": f"https://huggingface.co/LiquidAI/{name}", "created": None,
            "confidence": 0.7,
        } for name in names]
        path = tmp_path / f"watch-{day}.json"
        path.write_text(json.dumps({
            "observed_at": stamp.isoformat(),
            "sources": [{"id": "hf-liquidai", "status": "ok", "detail": "",
                         "url": "https://huggingface.co/api/models"}],
            "observations": observations,
        }))
        reports.append(path)
    return catalogue, reports, git("rev-parse", "HEAD")


def test_recall_compares_30_days_of_retained_inputs_with_card_additions(
    tmp_path, monkeypatch,
):
    catalogue, reports, revision = recall_fixture(tmp_path)

    def forbidden(*args, **kwargs):
        pytest.fail("recall attempted network access")

    monkeypatch.setattr(release_watch, "http_fetch", forbidden)
    monkeypatch.setattr(httpx.Client, "request", forbidden)
    output = tmp_path / "recall.json"
    summary = tmp_path / "recall.md"
    args = [arg for path in [*reports, reports[1]] for arg in ("--replay", str(path))]
    assert release_watch.main([
        *args, "--recall-end", "2026-11-20", "--catalogue-root", str(catalogue),
        "--report", str(output), "--summary", str(summary),
    ]) == 1  # Two card additions have no accepted discovery.
    result = json.loads(output.read_text())["recall"]
    assert result["window_start"] == "2026-10-21"
    assert result["window_end_exclusive"] == "2026-11-20"
    assert result["catalogue_revision"] == revision
    assert result["cards_added"] == 4
    assert result["matched_cards"] == 2
    assert result["recall"] == 0.5
    assert result["missing_artifact_days"] == []
    rows = {row["path"]: row for row in result["cards"]}
    assert rows["models/liquid/Pixtral-Docs.md"]["matched_signal_ids"] == [
        "watch:liquid:pixtral-docs",
    ]
    assert rows["models/liquid/alias-card.md"]["matched_signal_ids"] == [
        "watch:liquid:lfm-2-5-24b-a2b",
    ]
    assert datetime.fromisoformat(rows["models/liquid/alias-card.md"]["added_at"]) == datetime(
        2026, 11, 19, 23, 59, 59, tzinfo=UTC,
    )
    assert rows["models/liquid/docs.md"]["rejected"][0]["source_id"] == "hf-liquidai"
    assert rows["models/liquid/missing-2.md"]["matched_signal_ids"] == []
    assert rows["models/liquid/missing-2.md"]["rejected"] == []
    assert "missing-2.md" in summary.read_text()
    assert "PRIVATE BODY" not in output.read_text() + summary.read_text()


def test_recall_reports_artifact_gaps_and_outages_instead_of_claiming_full_coverage(tmp_path):
    catalogue, reports, _ = recall_fixture(tmp_path)
    failed = json.loads(reports[2].read_text())
    failed["sources"][0].update(status="unreachable", detail="fixture outage")
    reports[2].write_text(json.dumps(failed))
    output = tmp_path / "recall.json"
    assert release_watch.main([
        "--replay", str(reports[2]), "--recall-end", "2026-11-20",
        "--catalogue-root", str(catalogue), "--report", str(output),
    ]) == 1
    result = json.loads(output.read_text())["recall"]
    assert len(result["missing_artifact_days"]) == 29
    assert "2026-10-21" in result["missing_artifact_days"]
    assert "2026-10-22" not in result["missing_artifact_days"]
    assert result["source_failures"][0]["detail"] == "fixture outage"
    assert result["matched_cards"] == 0


def test_recall_cli_has_no_recall_denominator_when_no_cards_were_added(tmp_path):
    catalogue, reports, _ = recall_fixture(tmp_path)
    args = []
    for day, path in enumerate(reports[:30]):
        stamp = datetime(2026, 11, 22, tzinfo=UTC) + timedelta(days=day)
        report = json.loads(path.read_text())
        report.update(observed_at=stamp.isoformat(), observations=[])
        path.write_text(json.dumps(report))
        args.extend(["--replay", str(path)])
    output = tmp_path / "recall.json"
    done = subprocess.run([
        sys.executable, str(Path(release_watch.__file__).resolve()), *args,
        "--recall-end", "2026-12-22", "--catalogue-root", str(catalogue),
        "--report", str(output),
    ], capture_output=True, text=True, timeout=30)
    assert done.returncode == 0, done.stderr
    result = json.loads(output.read_text())["recall"]
    assert result["cards_added"] == result["matched_cards"] == 0
    assert result["recall"] is None
    assert result["missing_artifact_days"] == []


def test_recall_refuses_shallow_catalogue_and_writing_into_catalogue(tmp_path):
    catalogue, reports, _ = recall_fixture(tmp_path)
    shallow = tmp_path / "shallow"
    subprocess.run([
        "git", "clone", "--depth=1", catalogue.as_uri(), str(shallow),
    ], check=True, capture_output=True, text=True)
    args = ["--replay", str(reports[1]), "--recall-end", "2026-11-20"]
    with pytest.raises(SystemExit) as error:
        release_watch.main([*args, "--catalogue-root", str(shallow)])
    assert error.value.code == 2
    card = catalogue / "models/liquid/Pixtral-Docs.md"
    original = card.read_bytes()
    with pytest.raises(SystemExit) as error:
        release_watch.main([*args, "--catalogue-root", str(catalogue),
                            "--report", str(card)])
    assert error.value.code == 2
    assert card.read_bytes() == original
