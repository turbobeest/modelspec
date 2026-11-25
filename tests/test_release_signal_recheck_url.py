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


def _step(name: str) -> dict:
    workflow = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    return next(
        step for step in workflow["jobs"]["process"]["steps"] if step.get("name") == name
    )


def _gh_stub(tmp_path: Path) -> Path:
    stub = tmp_path / "bin"
    stub.mkdir(exist_ok=True)
    (stub / "gh").write_text(
        "#!/bin/bash\n"
        "printf '%s\\n' \"$*\" >> \"$RUNNER_TEMP/gh-calls\"\n"
        "case \"$1 $2\" in\n"
        "  'pr view') printf '%s' '{\"state\":\"OPEN\",\"headRefName\":"
        "\"data/release-signal-grok-20260926-123456789-1\","
        "\"headRepositoryOwner\":{\"login\":\"turbobeest\"}}' ;;\n"
        "  'pr create') echo 'https://github.com/turbobeest/modelspec-data/pull/9999' ;;\n"
        "esac\n",
        encoding="utf-8",
    )
    (stub / "gh").chmod(0o755)
    return stub


def _run(step: dict, tmp_path: Path, env: dict[str, str]) -> dict[str, str]:
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
                (str(_gh_stub(tmp_path)), str(Path(sys.executable).parent), os.environ["PATH"])
            ),
        } | env,
    )
    assert done.returncode == 0, done.stderr
    return dict(
        line.split("=", 1) for line in output.read_text(encoding="utf-8").splitlines() if line
    )


@pytest.mark.parametrize("first_url", [ISSUE_URL, None])
def test_no_second_draft_opens_once_the_signal_has_an_open_card_pull_request(
    service, tmp_path: Path, first_url,
) -> None:
    async def rows() -> dict[int, object]:
        kv = _queued(service)
        await _ack(service, kv, date(2026, 9, 26), result="uncertain", pr_url=first_url)
        await _ack(
            service, kv, date(2026, 9, 27), result="new", pr_url=PR_URL,
            recheck_day=1, recheck_due="2026-09-27",
        )
        return await _due(service, kv, date(2026, 10, 3))

    day_seven_url = asyncio.run(rows())[7]
    assert day_seven_url == PR_URL

    base = _run(_step("Select the re-check base"), tmp_path, {
        "PR_URL": str(day_seven_url),
        "DEFAULT_BRANCH": "main",
        "REPOSITORY_OWNER": "turbobeest",
    })
    assert base == {
        "mode": "open",
        "ref": "data/release-signal-grok-20260926-123456789-1",
        "branch": "data/release-signal-grok-20260926-123456789-1",
    }

    (tmp_path / "result.json").write_text(json.dumps({
        "status": "existing", "signal_id": SIGNAL_ID, "model_id": "acme/orbit-2",
    }), encoding="utf-8")
    opened = _run(_step("Open or update the pull request"), tmp_path, {
        "PR_MODE": base["mode"],
        "EXISTING_PR_URL": str(day_seven_url),
        "HUMAN": "true",
        "REGRESSED": "false",
        "REGRESSION_IDS": "",
        "BRANCH": base["branch"],
    })
    calls = (tmp_path / "gh-calls").read_text(encoding="utf-8")
    assert opened == {"url": PR_URL}
    assert "pr create" not in calls
    assert f"pr comment {PR_URL}" in calls
