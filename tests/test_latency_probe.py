"""Transport measurements use the wire body and never publish request data."""

import gzip
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from qa import latency_probe as probe


def test_measure_separates_network_phases_and_decoded_bytes(monkeypatch):
    private = "private-test-credential"
    monkeypatch.setenv("MODELSPEC_API_KEY", private)
    raw = b'{"result":"' + b"a" * 1000 + b'"}'
    compressed = gzip.compress(raw)

    def curl(command, **kwargs):
        assert private not in " ".join(command)
        assert "secret-request" not in " ".join(command)
        assert private in kwargs["input"]
        Path(command[command.index("--dump-header") + 1]).write_text(
            "HTTP/1.1 200 Connection established\n\n"
            "HTTP/2 200\nContent-Encoding: gzip\ncf-ray: example-BOS\n"
            'Server-Timing: snapshot;dur=12.3, isolate;desc="cold"\n\n')
        Path(command[command.index("--output") + 1]).write_bytes(compressed)
        return SimpleNamespace(returncode=0, stdout=json.dumps({
            "http_code": 200, "time_namelookup": .01, "time_connect": .03,
            "time_appconnect": .06, "time_starttransfer": .16, "time_total": .18,
        }))

    monkeypatch.setattr(probe.subprocess, "run", curl)
    row = probe.measure("https://api.example.test", {
        "name": "example", "path": "/v1/decide", "method": "POST",
        "body": {"task": "secret-request"}}, encoding="gzip")
    assert row["dns_ms"] == 10
    assert row["connect_ms"] == 20
    assert row["tls_ms"] == 30
    assert row["ttfb_ms"] == 160
    assert row["post_tls_ttfb_ms"] == 100
    assert row["download_ms"] == 20
    assert row["compressed_bytes"] == len(compressed)
    assert row["raw_bytes"] == len(raw)
    assert row["colo"] == "BOS"
    assert row["server_durations_ms"] == {"snapshot": 12.3}
    assert row["isolate_state"] == "cold"
    assert private not in json.dumps(row)
    assert "secret-request" not in json.dumps(row)


def test_keyless_calls_and_http_refusals_remain_visible(monkeypatch):
    monkeypatch.delenv("MODELSPEC_API_KEY", raising=False)

    def curl(command, **kwargs):
        assert "Authorization" not in kwargs["input"]
        Path(command[command.index("--output") + 1]).write_bytes(b"refused")
        return SimpleNamespace(returncode=0, stdout='{"http_code":401,"time_total":0.1}')

    monkeypatch.setattr(probe.subprocess, "run", curl)
    row = probe.measure("https://api.example.test", {"path": "/v1/rank"}, encoding="identity")
    assert probe.summarise([row])["statuses"] == {"401": 1}
    assert row["raw_bytes"] == row["compressed_bytes"] == 7


@pytest.mark.parametrize("path", ["//evil.example/a", "/v1/rank?secret=x", "/v1/rank#secret"])
def test_manifests_cannot_change_origin_or_publish_queries(path):
    with pytest.raises(ValueError):
        probe.validate_shapes([{"name": "shape-01", "path": path}])


def test_percentiles_retain_first_call_and_report_warm_separately():
    base = {"curl_exit": 0, "status": 200, "colo": "BOS", "content_encoding": "br"}
    keys = ("dns_ms", "connect_ms", "tls_ms", "ttfb_ms", "total_ms", "post_tls_ttfb_ms",
            "download_ms", "compressed_bytes", "raw_bytes")
    rows = [{**base, **dict.fromkeys(keys, n)} for n in (1000, 10, 20, 30)]
    for row, state in zip(rows, ("cold", "warm", "cold", "warm")):
        row["isolate_state"] = state
    summary = probe.summarise(rows)
    assert summary["first_total_ms"] == 1000
    assert summary["total_ms"] == {"p50": 25, "p95": 1000}
    assert summary["warm_total_ms"] == {"p50": 20, "p95": 30}
    assert summary["isolate_states"] == {
        "cold": {"calls": 2, "ttfb_ms": {"p50": 510, "p95": 1000}},
        "warm": {"calls": 2, "ttfb_ms": {"p50": 20, "p95": 30}},
    }
