"""New release cards carry verified prices or explicit price gaps."""

from datetime import date
import json
from pathlib import Path

import yaml

from release_signals.contract import ReleaseSignal
from release_signals.pipeline import FetchResult, draft_signal


MODEL_URL = "https://ai.google.dev/gemini-api/docs/models/fixture-model"
PRICE_URL = "https://ai.google.dev/gemini-api/docs/pricing"


def release_catalogue(root: Path, *, prices: bool):
    existing = root / "models/google/previous-model.md"
    existing.parent.mkdir(parents=True)
    existing.write_text("---\n" + yaml.safe_dump({
        "model_id": "google/previous-model",
        "display_name": "Previous Model",
        "provider": "google",
        "provider_display": "Google",
    }) + "---\n")
    (root / "registry").mkdir()
    (root / "registry/source-terms.json").write_text(json.dumps({
        "ai.google.dev": "permits",
    }))
    signal = ReleaseSignal.parse({
        "model_name": "Fixture Model", "provider": "Google",
        "first_seen_url": "https://x.com/google/status/123456789",
        "timestamp": "2026-10-20T12:00:00Z", "confidence": 0.99,
        "signal_id": "price-fixture-123456789",
    })
    replies = {
        "https://models.dev/api.json": json.dumps({"google": {
            "name": "Google", "models": {"fixture-model": {
                "id": "fixture-model", "name": "Fixture Model",
                "release_url": MODEL_URL,
                "cost": {"input": 999, "output": 999},
            }},
        }}).encode(),
        MODEL_URL: b"<h1>Google announces Fixture Model</h1>",
        PRICE_URL: (
            b"<table><tr><th>Model</th><th>Input price per 1M tokens</th>"
            b"<th>Output price per 1M tokens</th></tr>"
            b"<tr><td>Fixture Model</td><td>$2</td><td>$8</td></tr></table>"
            if prices else b"<h1>Pricing has not been published</h1>"
        ),
    }

    def fetch(url):
        return FetchResult(url=url, body=replies[url], content_type="text/html")

    return signal, fetch


def test_new_release_card_carries_verified_offering_without_full_admission(tmp_path, monkeypatch):
    signal, fetch = release_catalogue(tmp_path, prices=True)
    monkeypatch.setenv("MODELSPEC_SOURCE_CACHE", str(tmp_path / "source-copies"))

    result = draft_signal(signal, root=tmp_path, fetch=fetch, read_date=date(2026, 10, 20))

    offering = tmp_path / "offerings/google-gemini-api/google/fixture-model.yaml"
    assert offering.is_file()
    [row] = yaml.safe_load(offering.read_text())
    assert {fact["facet"]: fact["value"] for fact in row["facts"]} == {
        "offering.price.input": 2, "offering.price.output": 8,
    }
    assert result.offering_path == offering
    assert not {"offering.price.input", "offering.price.output"} & {
        gap["facet"] for gap in result.price_gaps
    }
    assert result.firecrawl_credits == 0
    assert (tmp_path / "verification/log.jsonl").is_file()
    assert (tmp_path / "registry/sources.yaml").is_file()
    assert not (tmp_path / "premier").exists()
    front = yaml.safe_load(result.card_path.read_text().split("---", 2)[1])
    assert front["cost"] == {}


def test_new_release_without_verifiable_prices_records_reasons(tmp_path, monkeypatch):
    signal, fetch = release_catalogue(tmp_path, prices=False)
    monkeypatch.setenv("MODELSPEC_SOURCE_CACHE", str(tmp_path / "source-copies"))

    result = draft_signal(signal, root=tmp_path, fetch=fetch, read_date=date(2026, 10, 20))

    assert result.card_path.is_file()
    assert result.price_gaps
    assert all(gap["reason"] for gap in result.price_gaps)
    assert result.firecrawl_credits == 0
    offerings = list((tmp_path / "offerings").rglob("*.yaml"))
    assert all(not row["facts"] for path in offerings for row in yaml.safe_load(path.read_text()))


def test_release_workflow_stages_offering_sources_and_receipts(tmp_path):
    import os
    import shlex
    import subprocess

    workflow_path = Path(os.environ.get(
        "MODEL449_RELEASE_WORKFLOW",
        str(Path(__file__).resolve().parents[1] / ".github/private-writers/release-signals.yml"),
    ))
    workflow = yaml.safe_load(workflow_path.read_text())
    steps = workflow["jobs"]["process"]["steps"]
    commit = next(step for step in steps if step.get("name") == "Commit and push the isolated signal branch")
    command = next(line.strip() for line in commit["run"].splitlines() if line.strip().startswith("git add "))
    files = (
        "models/google/fixture-model.md",
        "offerings/google-gemini-api/google/fixture-model.yaml",
        "registry/sources.yaml", "verification/log.jsonl",
    )
    for relative in files:
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("fixture\n")
    subprocess.run(["git", "init", "--quiet", str(tmp_path)], check=True)
    subprocess.run(shlex.split(command), cwd=tmp_path, check=True)
    staged = subprocess.run(
        ["git", "diff", "--cached", "--name-only"], cwd=tmp_path,
        check=True, capture_output=True, text=True,
    ).stdout.splitlines()
    assert set(staged) == set(files)


def test_release_workflow_retains_price_sources_and_installs_local_chromium():
    import os

    workflow_path = Path(os.environ.get(
        "MODEL449_RELEASE_WORKFLOW",
        str(Path(__file__).resolve().parents[1] / ".github/private-writers/release-signals.yml"),
    ))
    workflow = yaml.safe_load(workflow_path.read_text())
    steps = workflow["jobs"]["process"]["steps"]
    copies = [step for step in steps if step.get("uses") == "actions/upload-artifact@v4"
              and step.get("with", {}).get("path") == "${{ runner.temp }}/source-copies"]
    assert len(copies) == 1
    assert copies[0]["with"]["retention-days"] == 35
    assert copies[0]["if"] == "always()"
    verify = next(step for step in steps
                  if step.get("name") == "Validate cards and run two-key verification")
    assert verify["env"]["MODELSPEC_SOURCE_CACHE"] == "${{ runner.temp }}/source-copies"
    assert any("playwright install --with-deps --only-shell chromium" in step.get("run", "")
               for step in steps)
    assert any("--require-hashes --no-deps" in step.get("run", "")
               and "price-reread-render.requirements.txt" in step.get("run", "")
               for step in steps)


def test_signal_process_persists_offering_and_price_report_with_production_fetcher(
    tmp_path, monkeypatch,
):
    import httpx

    from scripts import process_release_signals as processor

    signal, fetch = release_catalogue(tmp_path, prices=True)
    pending = tmp_path / "pending.json"
    result_path = tmp_path / "result.json"
    pending.write_text(json.dumps({"signals": [{
        "model_name": signal.model_name, "provider": signal.provider,
        "first_seen_url": signal.first_seen_url, "timestamp": "2026-10-20T12:00:00Z",
        "confidence": 0.99, "signal_id": signal.signal_id,
    }]}))
    requests = []

    def request(request):
        url = str(request.url)
        requests.append(url)
        response = fetch(url)
        return httpx.Response(200, content=response.body,
                              headers={"content-type": response.content_type})

    client_type = httpx.Client
    monkeypatch.setattr(processor.httpx, "Client", lambda: client_type(
        transport=httpx.MockTransport(request)))
    monkeypatch.setattr(processor, "_fetch", fetch)
    monkeypatch.setattr(processor.refresh_leaderboards, "run", lambda **_: (
        processor.refresh_leaderboards.RefreshReport()))
    monkeypatch.setenv("MODELSPEC_SOURCE_CACHE", str(tmp_path / "source-copies"))

    result = processor.process(pending, result_path, root=tmp_path)

    assert result["status"] == "new"
    assert result["offering"] == "offerings/google-gemini-api/google/fixture-model.yaml"
    assert (tmp_path / result["offering"]).is_file()
    assert result["price_gaps"]
    assert all(gap["reason"] for gap in result["price_gaps"])
    assert not {"offering.price.input", "offering.price.output"} & {
        gap["facet"] for gap in result["price_gaps"]
    }
    assert result["price_sources"]
    assert all("url" in source and "outcome" in source for source in result["price_sources"])
    assert result["firecrawl_credits"] == 0
    assert json.loads(result_path.read_text()) == result
    assert set(requests) == {MODEL_URL, PRICE_URL}
    assert "<table>" not in result_path.read_text()
