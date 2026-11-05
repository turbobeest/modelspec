"""Private measurement crosses into a public report only as validated counts."""

import io
import json
import zipfile
from datetime import UTC, datetime

import httpx
import pytest

from decision.snapshot import SnapshotInputs, audit_build, default_registry
from scripts.slo import __main__ as cli
from scripts.slo import report as slo

NOW = datetime(2026, 11, 5, 9, 37, tzinfo=UTC)


def counts():
    return {
        "as_of": "2026-11-05",
        "release_coverage": {"counts_only": True, "stages": {
            stage: {"measured": 2, "completed": 1, "pending": 1,
                    "unknown": 0, "late": 1, "errors": 0}
            for stage in slo.RELEASE_STAGES
        }},
    }


def archive(data, name="coverage.json"):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zipped:
        zipped.writestr(name, json.dumps(data))
    return buffer.getvalue()


def transport(payload, *, event="schedule", branch="main", expired=False, missing=False):
    requests = []

    def respond(request):
        requests.append(request)
        path = request.url.path
        if path.endswith("release-coverage.yml/runs"):
            return httpx.Response(200, json={"workflow_runs": [{
                "id": 7, "event": event, "head_branch": branch,
                "head_repository": {"full_name": "turbobeest/modelspec-data"},
            }]})
        if path.endswith("runs/7/artifacts"):
            return httpx.Response(200, json={"total_count": 0 if missing else 1,
                "artifacts": [] if missing else [{"id": 11, "name": "release-coverage-counts",
                                                  "expired": expired,
                                                  "size_in_bytes": len(payload)}]})
        if path.endswith("artifacts/11/zip"):
            return httpx.Response(302, headers={"location": "https://storage.example.test/blob"})
        if request.url.host == "storage.example.test":
            return httpx.Response(200, content=payload)
        pytest.fail("unexpected HTTP request")

    return httpx.MockTransport(respond), requests


def test_private_step_produces_counts_file_that_the_public_report_renders(tmp_path, monkeypatch,
                                                                       capsys):
    from scripts.slo import releases

    history = slo.ReleaseHistory(releases=(
        slo.Release("secret/model", datetime(2026, 11, 1, tzinfo=UTC), premier_eligible=True),
    ), snapshot_history=True)
    monkeypatch.setattr(releases, "read_release_history", lambda *a, **kw: history)
    monkeypatch.setenv("GITHUB_REPOSITORY", "turbobeest/modelspec-data")
    count_path = tmp_path / "counts" / "coverage.json"
    detail = tmp_path / "detail"
    assert cli.main(["releases", "--data-dir", str(tmp_path), "--private-detail", "--out",
                     str(detail), "--counts-out", str(count_path), "--now", NOW.isoformat()]) == 0
    assert "secret/model" in (detail / "coverage.json").read_text()
    assert "secret/model" not in count_path.read_text()
    capsys.readouterr()

    audit = audit_build(SnapshotInputs(models=[]), registry=default_registry(),
                        premier=[], as_of=NOW.date(), guard=None)
    inputs = slo.Inputs(audit, {"models": []}, {}, (None, "offline"), {}, tmp_path)
    monkeypatch.setattr(cli, "read_repo", lambda *a, **kw: inputs)
    monkeypatch.setenv("GITHUB_REPOSITORY", "turbobeest/modelspec")
    out = tmp_path / "public"
    assert cli.main(["report", "--release-report", str(count_path), "--out", str(out),
                     "--now", NOW.isoformat()]) == 0
    data = json.loads((out / "coverage.json").read_text())
    release_results = [r for r in data["targets"] if r["id"] in slo.RELEASE_STAGES]
    assert len(release_results) == 4
    assert all(r["status"] == "breach" and r["measured"] == 1 for r in release_results)
    public_text = capsys.readouterr().out + "".join(
        (out / name).read_text() for name in ("coverage.json", "summary.md", "index.html"))
    assert "secret/model" not in public_text
    assert "p90_days" not in public_text and "Release coverage, counts only" in public_text


def test_download_checks_workflow_origin_and_drops_all_private_detail():
    from scripts.slo.release_counts import fetch_counts

    data = counts()
    data["targets"] = [{"errors": ["private stderr"], "subject": "secret/model"}]
    data["release_coverage"]["releases"] = [{"model_id": "secret/model"}]
    mocked, requests = transport(archive(data))
    with httpx.Client(transport=mocked) as client:
        result = fetch_counts("private-token", now=NOW, client=client)
    assert result == counts()
    assert len(requests) == 4
    assert all(r.headers["authorization"] == "Bearer private-token" for r in requests[:3])
    assert "authorization" not in requests[-1].headers


@pytest.mark.parametrize("change", [
    "stale", "future", "private", "negative", "huge", "bool", "inconsistent", "wrong-file",
    "oversized", "branch", "pull-request", "expired", "missing", "malformed",
])
def test_unusable_artifact_becomes_fixed_error_counts_without_private_text(change):
    from scripts.slo.release_counts import fetch_counts

    data = counts()
    opts = {}
    name = "coverage.json"
    if change in {"stale", "future"}:
        data["as_of"] = "2026-11-04" if change == "stale" else "2026-11-06"
    if change == "private":
        data["release_coverage"]["counts_only"] = False
    value = data["release_coverage"]["stages"]["release-card-lag"]
    if change in {"negative", "huge", "bool"}:
        value["errors"] = {"negative": -1, "huge": 10**100, "bool": True}[change]
    if change == "inconsistent":
        value["completed"] = 10
    if change == "wrong-file":
        name = "../secret.json"
    if change == "oversized":
        data["secret"] = "private" * 10000
    if change == "branch":
        opts["branch"] = "feature"
    if change == "pull-request":
        opts["event"] = "pull_request"
    if change in {"expired", "missing"}:
        opts[change] = True
    payload = b"private malformed archive" if change == "malformed" else archive(data, name)
    mocked, _ = transport(payload, **opts)
    with httpx.Client(transport=mocked) as client:
        result = fetch_counts("private-token", now=NOW, client=client)
    assert result["as_of"] == "2026-11-05"
    for summary in result["release_coverage"]["stages"].values():
        assert summary == {"measured": 0, "completed": 0, "pending": 0,
                           "unknown": 0, "late": 0, "errors": 1}
    assert "private" not in json.dumps(result)


def test_missing_token_and_environment_handoff_are_silent_and_fail_closed(tmp_path, monkeypatch,
                                                                       capsys):
    monkeypatch.delenv("MODELSPEC_DATA_TOKEN", raising=False)
    output = tmp_path / "job-output"
    monkeypatch.setenv("GITHUB_OUTPUT", str(output))
    assert cli.main(["release-counts", "--github-output", "--now", NOW.isoformat()]) == 0
    key, payload = output.read_text().strip().split("=", 1)
    assert key == "counts" and len(payload) < 2048
    monkeypatch.setenv("PRIVATE_RELEASE_COUNTS", payload)
    count_file = tmp_path / "count-file.json"
    assert cli.main(["release-counts", "--from-env", "--out", str(count_file),
                     "--now", NOW.isoformat()]) == 0
    assert json.loads(count_file.read_text()) == json.loads(payload)
    assert all(s["errors"] == 1 for s in json.loads(payload)["release_coverage"]["stages"].values())
    captured = capsys.readouterr()
    assert captured.out == captured.err == ""
