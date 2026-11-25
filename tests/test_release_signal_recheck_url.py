"""A re-check follows the pull request a later run reported (MODEL-475).

The first acknowledgement of a signal can carry no pull request: an identity
review issue, or nothing at all. When a later re-check opens a card pull
request, the remaining re-checks must point at that pull request, so the
workflow updates it instead of drafting the same model a second time.
"""

from __future__ import annotations

import asyncio
import importlib.util
import json
import os
import subprocess
import sys
from datetime import date
from pathlib import Path

import pytest
import yaml

from release_signals.pipeline import FetchResult, clear_catalogue_cache
from scripts import process_release_signals as processor
from tests.test_release_signals import FIXTURES, _write_card

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "private-writers" / "release-signals.yml"
SIGNAL_ID = "grok-20260926-123456789"
KEY = "Bearer read-secret"
ISSUE_URL = "https://github.com/turbobeest/modelspec-data/issues/9001"
PR_URL = "https://github.com/turbobeest/modelspec-data/pull/9002"
LATER_PR_URL = "https://github.com/turbobeest/modelspec-data/pull/9003"


def _signal() -> dict[str, object]:
    return {
        "model_name": "Orbit 2",
        "provider": "Acme",
        "first_seen_url": "https://x.com/acme/status/123456789",
        "timestamp": "2026-09-26T13:14:15Z",
        "confidence": 0.97,
        "signal_id": SIGNAL_ID,
    }


@pytest.fixture
def service():
    spec = importlib.util.spec_from_file_location(
        "modelspec_recheck_url_signals_service",
        ROOT / "api" / "worker" / "src" / "signals_service.py",
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class KV:
    def __init__(self) -> None:
        self.rows: dict[str, str] = {}

    async def get(self, key: str) -> str | None:
        return self.rows.get(key)

    async def put(self, key: str, value: str) -> None:
        self.rows[key] = value

    async def delete(self, key: str) -> None:
        self.rows.pop(key, None)

    async def list(self, options: dict | None = None):
        prefix = (options or {}).get("prefix", "")
        return {"keys": [{"name": key} for key in sorted(self.rows) if key.startswith(prefix)]}


def _queued(service) -> KV:
    kv = KV()
    kv.rows[service.PENDING_PREFIX + SIGNAL_ID] = json.dumps(
        _signal(), separators=(",", ":"), sort_keys=True,
    )
    return kv


async def _ack(service, kv: KV, today: date, **payload: object):
    return await service.acknowledge(
        authorization=KEY, read_key="read-secret", kv=kv,
        payload={"signal_id": SIGNAL_ID, **payload}, today=today,
    )


async def _due(service, kv: KV, today: date) -> dict[int, object]:
    listed = await service.pending(
        authorization=KEY, read_key="read-secret", kv=kv, today=today,
    )
    return {row["day"]: row["pr_url"] for row in listed.body["rechecks"]}


@pytest.mark.parametrize("first_url", [ISSUE_URL, None])
def test_a_recheck_that_reports_a_pull_request_relinks_the_later_rechecks(
    service, first_url,
) -> None:
    async def scenario() -> None:
        kv = _queued(service)
        first = await _ack(
            service, kv, date(2026, 9, 26), result="uncertain", pr_url=first_url,
        )
        assert first.body["recheck_days"] == [1, 7, 30]
        assert await _due(service, kv, date(2026, 10, 26)) == {
            1: first_url, 7: first_url, 30: first_url,
        }

        day_one = await _ack(
            service, kv, date(2026, 9, 27), result="new", pr_url=PR_URL,
            recheck_day=1, recheck_due="2026-09-27",
        )

        # The response keeps its shape: a re-check schedules nothing new.
        assert day_one.status == 200
        assert day_one.body == {
            "schema_version": "1",
            "endpoint": "signals.ack",
            "status": "acknowledged",
            "signal_id": SIGNAL_ID,
            "recheck_days": [],
        }
        assert await _due(service, kv, date(2026, 10, 26)) == {7: PR_URL, 30: PR_URL}
        rows = [
            json.loads(value) for key, value in kv.rows.items()
            if key.startswith(service.RECHECK_PREFIX)
        ]
        # Only the URL moves; every row keeps the fields it was stored with.
        assert sorted(rows[0]) == ["day", "due", "pr_url", "signal", "signal_id"]
        assert [(row["day"], row["due"]) for row in sorted(rows, key=lambda r: r["day"])] == [
            (7, "2026-10-03"), (30, "2026-10-26"),
        ]

    asyncio.run(scenario())


@pytest.mark.parametrize("reported", [None, ISSUE_URL])
def test_a_recheck_that_reports_no_pull_request_keeps_the_stored_one(
    service, reported,
) -> None:
    async def scenario() -> None:
        kv = _queued(service)
        await _ack(service, kv, date(2026, 9, 26), result="new", pr_url=PR_URL)
        await _ack(
            service, kv, date(2026, 9, 27), result="existing", pr_url=reported,
            recheck_day=1, recheck_due="2026-09-27",
        )
        assert await _due(service, kv, date(2026, 10, 26)) == {7: PR_URL, 30: PR_URL}

    asyncio.run(scenario())


def test_a_later_pull_request_replaces_an_earlier_one_and_spares_other_signals(
    service,
) -> None:
    async def scenario() -> None:
        kv = _queued(service)
        other = dict(_signal(), signal_id="grok-20260926-987654321")
        kv.rows[service.PENDING_PREFIX + other["signal_id"]] = json.dumps(
            other, separators=(",", ":"), sort_keys=True,
        )
        await _ack(service, kv, date(2026, 9, 26), result="new", pr_url=PR_URL)
        await service.acknowledge(
            authorization=KEY, read_key="read-secret", kv=kv,
            payload={"signal_id": other["signal_id"], "result": "uncertain", "pr_url": ISSUE_URL},
            today=date(2026, 9, 26),
        )
        # Day 7 runs first, as it can after a failed day-1 job; day 1 must follow it.
        await _ack(
            service, kv, date(2026, 10, 3), result="new", pr_url=LATER_PR_URL,
            recheck_day=7, recheck_due="2026-10-03",
        )
        listed = await service.pending(
            authorization=KEY, read_key="read-secret", kv=kv, today=date(2026, 10, 26),
        )
        by_signal: dict[str, dict[int, object]] = {}
        for row in listed.body["rechecks"]:
            by_signal.setdefault(row["signal_id"], {})[row["day"]] = row["pr_url"]
        assert by_signal == {
            SIGNAL_ID: {1: LATER_PR_URL, 30: LATER_PR_URL},
            other["signal_id"]: {1: ISSUE_URL, 7: ISSUE_URL, 30: ISSUE_URL},
        }

    asyncio.run(scenario())


class YieldingKV(KV):
    """Gives the event loop away around every operation, as a remote store does."""

    def __init__(self, fail_at: int | None = None) -> None:
        super().__init__()
        self.writes = 0
        self.fail_at = fail_at

    async def _write(self) -> None:
        self.writes += 1
        if self.fail_at is not None and self.writes == self.fail_at:
            raise RuntimeError("injected KV write failure")
        await asyncio.sleep(0)

    async def get(self, key: str) -> str | None:
        await asyncio.sleep(0)
        value = self.rows.get(key)
        await asyncio.sleep(0)
        return value

    async def put(self, key: str, value: str) -> None:
        await self._write()
        self.rows[key] = value
        await asyncio.sleep(0)

    async def delete(self, key: str) -> None:
        await self._write()
        self.rows.pop(key, None)
        await asyncio.sleep(0)


async def _seeded(service, kv: KV, first_url: object = ISSUE_URL) -> KV:
    kv.rows[service.PENDING_PREFIX + SIGNAL_ID] = json.dumps(
        _signal(), separators=(",", ":"), sort_keys=True,
    )
    await _ack(service, kv, date(2026, 9, 26), result="uncertain", pr_url=first_url)
    return kv


def _day(day: int, due: str, url: str = PR_URL) -> dict[str, object]:
    return {"result": "new", "pr_url": url, "recheck_day": day, "recheck_due": due}


def test_a_retried_acknowledgement_of_a_completed_recheck_is_a_no_op_success(service) -> None:
    async def scenario() -> None:
        kv = await _seeded(service, KV())
        first = await _ack(service, kv, date(2026, 9, 27), **_day(1, "2026-09-27"))
        after = dict(kv.rows)
        retried = await _ack(service, kv, date(2026, 9, 27), **_day(1, "2026-09-27"))
        assert retried.status == 200
        assert retried.body == first.body
        assert kv.rows == after
        # A re-check that never existed is still not found.
        missing = await _ack(service, kv, date(2026, 9, 28), **_day(1, "2026-09-28"))
        assert missing.status == 404

    asyncio.run(scenario())


def test_a_failed_write_leaves_the_recheck_due_and_its_retry_converges(service) -> None:
    async def writes() -> int:
        kv = await _seeded(service, YieldingKV())
        kv.writes = 0
        await _ack(service, kv, date(2026, 9, 27), **_day(1, "2026-09-27"))
        return kv.writes

    total = asyncio.run(writes())
    assert total >= 5  # audit, three row relinks or fewer, marker, delete

    async def scenario(fail_at: int) -> None:
        kv = await _seeded(service, YieldingKV())
        kv.writes, kv.fail_at = 0, fail_at
        with pytest.raises(RuntimeError):
            await _ack(service, kv, date(2026, 9, 27), **_day(1, "2026-09-27"))
        kv.fail_at = None
        # The acknowledged row is still due until its own delete succeeds. If it
        # moved, it moved onto the pull request, so its retry updates that one.
        due = await _due(service, kv, date(2026, 9, 27))
        if fail_at < total:
            assert due.get(1) in (ISSUE_URL, PR_URL)
        retried = await _ack(service, kv, date(2026, 9, 27), **_day(1, "2026-09-27"))
        assert retried.status == 200
        assert await _due(service, kv, date(2026, 10, 26)) == {7: PR_URL, 30: PR_URL}

    for fail_at in range(1, total + 1):
        asyncio.run(scenario(fail_at))


@pytest.mark.parametrize("stagger", range(0, 120, 2))
def test_parallel_acknowledgements_never_resurrect_a_completed_recheck(
    service, stagger,
) -> None:
    async def later(coroutine, ticks: int):
        for _ in range(ticks):
            await asyncio.sleep(0)
        return await coroutine

    async def scenario() -> None:
        kv = await _seeded(service, YieldingKV())
        outcomes = await asyncio.gather(
            _ack(service, kv, date(2026, 10, 3), **_day(1, "2026-09-27")),
            # Day 7 reports no pull request, so it moves nothing while day 1 relinks it.
            later(_ack(
                service, kv, date(2026, 10, 3), **_day(7, "2026-10-03", ISSUE_URL),
            ), stagger),
            later(_ack(service, kv, date(2026, 10, 3), **_day(1, "2026-09-27")), stagger // 2),
        )
        assert [outcome.status for outcome in outcomes] == [200, 200, 200]
        assert await _due(service, kv, date(2026, 10, 26)) == {30: PR_URL}
        row = json.loads(kv.rows[f"{service.RECHECK_PREFIX}2026-10-26/{SIGNAL_ID}"])
        assert (row["day"], row["due"], row["pr_url"]) == (30, "2026-10-26", PR_URL)

    asyncio.run(scenario())


def test_a_retried_partial_first_acknowledgement_is_relinked_on_both_schedules(
    service,
) -> None:
    async def scenario() -> None:
        kv = YieldingKV()
        kv.rows[service.PENDING_PREFIX + SIGNAL_ID] = json.dumps(
            _signal(), separators=(",", ":"), sort_keys=True,
        )
        # The first acknowledgement dies before it deletes the pending row ...
        kv.fail_at = 6  # seen, audit, three rows, then the pending delete
        with pytest.raises(RuntimeError):
            await _ack(service, kv, date(2026, 9, 26), result="uncertain", pr_url=ISSUE_URL)
        kv.fail_at = None
        assert service.PENDING_PREFIX + SIGNAL_ID in kv.rows
        # ... so the next day's run acknowledges it again, on a second schedule.
        await _ack(service, kv, date(2026, 9, 27), result="uncertain", pr_url=ISSUE_URL)
        dues = sorted(
            key.removeprefix(service.RECHECK_PREFIX) for key in kv.rows
            if key.startswith(service.RECHECK_PREFIX)
        )
        assert [due.split("/")[0] for due in dues] == [
            "2026-09-27", "2026-09-28", "2026-10-03", "2026-10-04", "2026-10-26", "2026-10-27",
        ]
        await _ack(service, kv, date(2026, 9, 27), **_day(1, "2026-09-27"))
        listed = await service.pending(
            authorization=KEY, read_key="read-secret", kv=kv, today=date(2026, 10, 27),
        )
        assert sorted((row["due"], row["pr_url"]) for row in listed.body["rechecks"]) == [
            ("2026-09-28", PR_URL), ("2026-10-03", PR_URL), ("2026-10-04", PR_URL),
            ("2026-10-26", PR_URL), ("2026-10-27", PR_URL),
        ]

    asyncio.run(scenario())


def _step(name: str) -> dict:
    workflow = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    return next(
        step for step in workflow["jobs"]["process"]["steps"] if step.get("name") == name
    )


BRANCH = "data/release-signal-grok-20260926-123456789-1"


def _gh_stub(tmp_path: Path, state: str) -> Path:
    stub = tmp_path / "bin"
    stub.mkdir(exist_ok=True)
    (stub / "gh").write_text(
        "#!/bin/bash\n"
        "printf '%s\\n' \"$*\" >> \"$RUNNER_TEMP/gh-calls\"\n"
        "case \"$1 $2\" in\n"
        f"  'pr view') printf '%s' '{{\"state\":\"{state}\",\"headRefName\":\"{BRANCH}\","
        "\"headRepositoryOwner\":{\"login\":\"turbobeest\"}}' ;;\n"
        "  'pr create') echo 'https://github.com/turbobeest/modelspec-data/pull/9999' ;;\n"
        "esac\n",
        encoding="utf-8",
    )
    (stub / "gh").chmod(0o755)
    return stub


def _run(step: dict, tmp_path: Path, state: str, env: dict[str, str]) -> dict[str, str]:
    output = tmp_path / "github-output"
    output.write_text("", encoding="utf-8")
    done = subprocess.run(
        ["bash", "-e", "-c", step["run"]],
        cwd=tmp_path, capture_output=True, text=True,
        env=os.environ | {
            "RUNNER_TEMP": str(tmp_path),
            "GITHUB_OUTPUT": str(output),
            "GH_TOKEN": "offline-fixture",
            "PATH": os.pathsep.join(
                (str(_gh_stub(tmp_path, state)), str(Path(sys.executable).parent),
                 os.environ["PATH"])
            ),
        } | env,
    )
    assert done.returncode == 0, done.stderr
    return dict(
        line.split("=", 1) for line in output.read_text(encoding="utf-8").splitlines() if line
    )


def _git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-C", str(repo), "-c", "user.name=fixture", "-c", "user.email=fixture@invalid",
         "-c", "commit.gpgsign=false", *args],
        check=True, capture_output=True,
    )


def _data_repo(tmp_path: Path, *, merged: bool) -> Path:
    """A data checkout whose day-1 re-check drafted Orbit 2 on its own branch."""
    repo = tmp_path / "data"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _write_card(repo, "acme", "orbit-1", display="Orbit 1", version="orbit-1")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "base")
    _git(repo, "checkout", "-q", "-b", BRANCH)
    _write_card(repo, "acme", "orbit-2", display="Orbit 2", version="orbit-2")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "draft Orbit 2")
    _git(repo, "checkout", "-q", "main")
    if merged:
        _git(repo, "merge", "-q", "--no-ff", "-m", "merge the card PR", BRANCH)
    return repo


def _offline_sources(monkeypatch: pytest.MonkeyPatch) -> None:
    models_dev_url = "https://models.dev/api.json"
    provider_url = "https://acme.example/models"
    hf_search = "https://huggingface.co/api/models?search=Orbit+2&limit=20"
    replies = {
        models_dev_url: FetchResult(
            url=models_dev_url,
            body=(FIXTURES / "models-dev-production.json").read_bytes(),
            content_type="application/json",
        ),
        provider_url: FetchResult(
            url=provider_url,
            body=(FIXTURES / "acme-orbit.html").read_bytes(),
            content_type="text/html",
        ),
        hf_search: FetchResult(url=hf_search, body=b"[]", content_type="application/json"),
    }
    monkeypatch.setattr(processor, "_fetch", lambda url: replies[url])
    monkeypatch.setattr(
        processor.refresh_leaderboards, "run",
        lambda **_: processor.refresh_leaderboards.RefreshReport(),
    )


@pytest.mark.parametrize("first_url", [ISSUE_URL, None])
@pytest.mark.parametrize("state", ["OPEN", "MERGED"])
def test_no_second_draft_opens_for_a_signal_with_an_open_or_merged_card_pull_request(
    service, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, first_url, state,
) -> None:
    clear_catalogue_cache()

    async def day_seven() -> dict:
        kv = await _seeded(service, KV(), first_url)
        await _ack(service, kv, date(2026, 9, 27), **_day(1, "2026-09-27"))
        listed = await service.pending(
            authorization=KEY, read_key="read-secret", kv=kv, today=date(2026, 10, 3),
        )
        return listed.body

    pending = asyncio.run(day_seven())
    assert [(row["day"], row["pr_url"]) for row in pending["rechecks"]] == [(7, PR_URL)]

    base = _run(_step("Select the re-check base"), tmp_path, state, {
        "PR_URL": PR_URL, "DEFAULT_BRANCH": "main", "REPOSITORY_OWNER": "turbobeest",
    })
    if state == "OPEN":
        assert base == {"mode": "open", "ref": BRANCH, "branch": BRANCH}
    else:
        assert base == {"mode": "merged", "ref": "main", "branch": ""}

    # Check out what the workflow checks out, then process the Worker's day-7 row.
    repo = _data_repo(tmp_path, merged=state == "MERGED")
    _git(repo, "checkout", "-q", base["ref"])
    _offline_sources(monkeypatch)
    (tmp_path / "pending.json").write_text(json.dumps(pending), encoding="utf-8")
    result = processor.process(
        tmp_path / "pending.json", tmp_path / "result.json",
        root=repo, signal_id=SIGNAL_ID, recheck_day=7,
    )
    assert (result["status"], result["model_id"], result["pr_url"]) == (
        "existing", "acme/orbit-2", PR_URL,
    )
    assert sorted(path.name for path in (repo / "models" / "acme").glob("*.md")) == [
        "orbit-1.md", "orbit-2.md",
    ]

    if state == "OPEN":
        opened = _run(_step("Open or update the pull request"), tmp_path, state, {
            "PR_MODE": base["mode"], "EXISTING_PR_URL": PR_URL, "HUMAN": "true",
            "REGRESSED": "false", "REGRESSION_IDS": "", "BRANCH": base["branch"],
        })
        calls = (tmp_path / "gh-calls").read_text(encoding="utf-8")
        assert opened == {"url": PR_URL}
        assert "pr create" not in calls
        assert f"pr comment {PR_URL}" in calls
