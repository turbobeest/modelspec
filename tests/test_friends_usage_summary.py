"""Friends reports use existing daily counters and disclose expired coverage."""

from __future__ import annotations

import asyncio
import importlib
import json
import subprocess
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKER_SRC = REPO_ROOT / "api" / "worker" / "src"
if str(WORKER_SRC) not in sys.path:
    sys.path.insert(0, str(WORKER_SRC))

import access_config  # noqa: E402
import access_keys  # noqa: E402
import access_limits  # noqa: E402
from access_kv import MemoryKV  # noqa: E402

FINGERPRINT = "a" * 64
OTHER_FINGERPRINT = "b" * 64


def report_module():
    return importlib.import_module("scripts.friends_usage_summary")


def key_record(fingerprint: str, *, tier: str = "friends", active: bool = True) -> str:
    return json.dumps(
        access_keys.KeyRecord(
            key_id=fingerprint[:12],
            tier=tier,
            owner="private-owner-marker",
            created_at="2026-09-01T00:00:00Z",
            active=active,
            label="private-label-marker",
        ).to_json()
    )


def snapshot(day: int, count: int, *, active: bool = True) -> dict:
    captured = datetime(2026, 9, day, 12, tzinfo=UTC) + timedelta(days=1)
    return {
        "schema_version": 1,
        "month": "2026-09",
        "captured_at": captured.isoformat().replace("+00:00", "Z"),
        "complete_days": [f"2026-09-{day:02}"],
        "keys": [
            {
                "fingerprint": FINGERPRINT,
                "key_id": FINGERPRINT[:12],
                "active": active,
                "days": {f"2026-09-{day:02}": count},
            }
        ],
    }


def test_monthly_summary_counts_daily_buckets_once_and_includes_revoked_keys() -> None:
    report = report_module()
    store = MemoryKV(
        {
            f"key:{FINGERPRINT}": key_record(FINGERPRINT),
            f"key:{OTHER_FINGERPRINT}": key_record(OTHER_FINGERPRINT, active=False),
            f"key:{'c' * 64}": key_record("c" * 64, tier="paid"),
            f"count:{FINGERPRINT[:12]}:daily:2026-09-01": "2",
            f"count:{FINGERPRINT[:12]}:daily:2026-09-30": "3",
            f"count:{FINGERPRINT[:12]}:daily:2026-08-31": "90",
            f"count:{FINGERPRINT[:12]}:burst:2026-09-30T12:00": "3",
            f"count:{OTHER_FINGERPRINT[:12]}:daily:2026-09-15": "4",
            f"count:{'c' * 12}:daily:2026-09-15": "100",
        }
    )
    before = dict(store.data)

    captured = asyncio.run(
        report.capture(store, "2026-09", now=datetime(2026, 10, 1, 12, tzinfo=UTC))
    )
    result = report.summarize([captured], "2026-09")

    assert result["keys"] == [
        {"key_id": "aaaaaaaaaaaa", "active": True, "requests": 5},
        {"key_id": "bbbbbbbbbbbb", "active": False, "requests": 4},
    ]
    assert result["total_requests"] == 9
    assert result["partial"] is True
    assert result["covered_days"] == ["2026-09-30"]
    assert result["missing_days"] == [f"2026-09-{day:02}" for day in range(1, 30)]
    assert store.data == before
    assert all(verb == "get" for verb, _ in store.calls)
    serialized = json.dumps(captured) + json.dumps(result)
    assert "private-owner-marker" not in serialized
    assert "private-label-marker" not in serialized


def test_daily_snapshots_reconstruct_a_month_without_double_counting() -> None:
    report = report_module()
    captures = [snapshot(day, day) for day in range(1, 31)]
    captures.extend([snapshot(1, 0), snapshot(30, 35, active=False)])

    result = report.summarize(captures, "2026-09")

    assert result == {
        "month": "2026-09",
        "partial": False,
        "covered_days": [f"2026-09-{day:02}" for day in range(1, 31)],
        "missing_days": [],
        "total_requests": 470,
        "keys": [{"key_id": "aaaaaaaaaaaa", "active": False, "requests": 470}],
    }


def test_report_reads_the_actual_access_meter_counter_names() -> None:
    report = report_module()
    store = MemoryKV({f"key:{FINGERPRINT}": key_record(FINGERPRINT)})
    tier = access_config.TierLimits("friends", None, 60, True, True, "fixture")
    used_at = datetime(2026, 9, 30, 12, tzinfo=UTC)
    asyncio.run(access_limits.consume(store, FINGERPRINT[:12], tier, used_at))

    captured = asyncio.run(
        report.capture(store, "2026-09", now=datetime(2026, 10, 1, 12, tzinfo=UTC))
    )
    result = report.summarize([captured], "2026-09")

    assert result["keys"] == [{"key_id": "aaaaaaaaaaaa", "active": True, "requests": 1}]
    assert result["total_requests"] == 1


def test_capture_follows_store_pagination_and_reports_zero_usage() -> None:
    report = report_module()

    class PagedStore(MemoryKV):
        async def list(self, options=None):
            if options["prefix"] == "key:":
                if not options.get("cursor"):
                    return {
                        "keys": [{"name": f"key:{FINGERPRINT}"}],
                        "list_complete": False,
                        "cursor": "next",
                    }
                assert options["cursor"] == "next"
                return {"keys": [{"name": f"key:{OTHER_FINGERPRINT}"}], "list_complete": True}
            return {"keys": [], "list_complete": True}

    store = PagedStore(
        {
            f"key:{FINGERPRINT}": key_record(FINGERPRINT),
            f"key:{OTHER_FINGERPRINT}": key_record(OTHER_FINGERPRINT),
        }
    )
    captured = asyncio.run(
        report.capture(store, "2026-09", now=datetime(2026, 9, 10, 12, tzinfo=UTC))
    )
    result = report.summarize([captured], "2026-09")

    assert result["keys"] == [
        {"key_id": "aaaaaaaaaaaa", "active": True, "requests": 0},
        {"key_id": "bbbbbbbbbbbb", "active": True, "requests": 0},
    ]
    assert result["covered_days"] == ["2026-09-09"]


@pytest.mark.parametrize("month", ["2026-9", "2026-13", "2026-00", "not-a-month"])
def test_invalid_month_is_refused_before_reading_store(month: str) -> None:
    report = report_module()
    store = MemoryKV()
    with pytest.raises(ValueError, match="YYYY-MM"):
        asyncio.run(report.capture(store, month, now=datetime(2026, 10, 1, tzinfo=UTC)))
    assert store.calls == []


def test_cli_merges_snapshot_inputs_without_remote_reads(tmp_path, capsys) -> None:
    report = report_module()
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    first.write_text(json.dumps(snapshot(1, 2)), encoding="utf-8")
    second.write_text(json.dumps(snapshot(1, 4)), encoding="utf-8")

    def refuse_remote(command):
        pytest.fail(f"offline report tried to run {command}")

    status = report.main(
        ["--month", "2026-09", "--input", str(first), "--input", str(second)], run=refuse_remote
    )

    output = capsys.readouterr()
    assert status == 0
    assert output.err == ""
    assert json.loads(output.out)["total_requests"] == 4


def test_remote_snapshot_uses_only_read_commands_and_configured_environment(
    tmp_path, capsys
) -> None:
    report = report_module()
    config = tmp_path / "wrangler.jsonc"
    config.write_text('{"kv_namespaces":[{"binding":"ACCESS","id":"fake"}]}', encoding="utf-8")
    calls = []

    def run(command):
        calls.append(command)
        if command[4] == "list":
            prefix = command[command.index("--prefix") + 1]
            return json.dumps([{"name": f"key:{FINGERPRINT}"}] if prefix == "key:" else [])
        assert command[4] == "get"
        assert "--text" in command
        return key_record(FINGERPRINT)

    status = report.main(
        ["--month", "2026-09", "--snapshot", "--config", str(config), "--env", "staging"], run=run
    )

    output = capsys.readouterr()
    assert status == 0
    assert output.err == ""
    assert json.loads(output.out)["keys"][0]["key_id"] == FINGERPRINT[:12]
    assert {command[4] for command in calls} == {"list", "get"}
    for command in calls:
        assert command[command.index("--binding") + 1] == "ACCESS"
        assert "--remote" in command
        assert command[command.index("--config") + 1] == str(config)
        assert command[command.index("--env") + 1] == "staging"


def test_wrangler_failure_does_not_print_stored_record_or_secrets(monkeypatch, capsys) -> None:
    report = report_module()

    def fail(command, **kwargs):
        assert kwargs["stdin"] is subprocess.DEVNULL
        assert kwargs["env"]["CI"] == "1"
        assert kwargs["env"]["WRANGLER_SEND_METRICS"] == "false"
        return subprocess.CompletedProcess(
            command, 1, key_record(FINGERPRINT), "live_PRIVATE_SECRET_MARKER"
        )

    monkeypatch.setattr(report.subprocess, "run", fail)
    status = report.main(["--month", "2026-09"])

    output = capsys.readouterr()
    assert status == 1
    assert output.out == ""
    assert "Wrangler exited 1" in output.err
    assert "PRIVATE_SECRET_MARKER" not in output.err
    assert "private-owner-marker" not in output.err


def test_corrupt_or_wrong_month_snapshot_fails_instead_of_reporting_a_total() -> None:
    report = report_module()
    wrong_month = snapshot(1, 2)
    wrong_month["month"] = "2026-08"
    corrupt = snapshot(1, -2)
    for invalid in [wrong_month, corrupt]:
        with pytest.raises(ValueError):
            report.summarize([invalid], "2026-09")


@pytest.mark.parametrize(
    "when, covered",
    [
        (datetime(2026, 10, 1, 0, 0, 59, tzinfo=UTC), []),
        (datetime(2026, 10, 1, 0, 1, tzinfo=UTC), ["2026-09-30"]),
        (datetime(2026, 10, 2, 12, tzinfo=UTC), []),
    ],
)
def test_capture_only_certifies_the_unexpired_previous_day(when, covered) -> None:
    report = report_module()
    result = asyncio.run(report.capture(MemoryKV(), "2026-09", now=when))
    assert result["complete_days"] == covered


def test_saved_coverage_cannot_certify_days_that_had_already_expired() -> None:
    report = report_module()
    invalid = snapshot(30, 2)
    invalid["complete_days"] = ["2026-09-01"]
    with pytest.raises(ValueError, match="coverage"):
        report.summarize([invalid], "2026-09")


def test_daily_counter_listing_follows_all_pages() -> None:
    report = report_module()
    prefix = f"count:{FINGERPRINT[:12]}:daily:"

    class PagedCounterStore(MemoryKV):
        async def list(self, options=None):
            if options["prefix"] == prefix + "2026-09-":
                if not options.get("cursor"):
                    return {
                        "keys": [{"name": prefix + "2026-09-29"}],
                        "list_complete": False,
                        "cursor": "next",
                    }
                return {"keys": [{"name": prefix + "2026-09-30"}], "list_complete": True}
            return await super().list(options)

    store = PagedCounterStore(
        {
            f"key:{FINGERPRINT}": key_record(FINGERPRINT),
            prefix + "2026-09-29": "3",
            prefix + "2026-09-30": "4",
        }
    )
    captured = asyncio.run(
        report.capture(store, "2026-09", now=datetime(2026, 10, 1, 12, tzinfo=UTC))
    )
    assert report.summarize([captured], "2026-09")["total_requests"] == 7
