"""MODEL-441: the KV three-way merge, the thin Cloudflare client and the zone audit."""

from __future__ import annotations

import json
import stat

import pytest

from scripts import cf_move
from scripts.cf_move import Entry, KVClient, Plan, normalize, plan_merge, zone_diff

TOKEN = "tok-SECRET-123"
NOW = 1_800_000_000


def merge(base, src, dst, skip=("count:",)):
    return plan_merge(base, src, dst, skip_prefixes=skip, now=NOW)


A, B, C = Entry("YQ=="), Entry("Yg=="), Entry("Yw==")


def test_unchanged_source_does_nothing_even_when_destination_differs():
    assert merge({"k": A}, {"k": A}, {"k": B}) == Plan({}, [], [], [])


def test_source_change_applies_when_destination_still_matches_base():
    assert merge({"k": A, "gone": A}, {"k": B, "new": C}, {"k": A, "gone": A}) == Plan(
        {"k": B, "new": C}, ["gone"], [], []
    )


def test_destination_already_equal_to_source_is_left_alone():
    assert merge({"k": A}, {"k": B}, {"k": B}) == Plan({}, [], [], [])
    assert merge({"k": A}, {}, {}) == Plan({}, [], [], [])


def test_both_sides_changed_is_a_conflict_never_an_overwrite():
    assert merge({"k": A, "d": A}, {"k": B, "d": B}, {"k": C}) == Plan({}, [], ["d", "k"], [])


def test_metadata_difference_counts_as_a_change_but_expiration_alone_does_not():
    plan = merge({"k": Entry("YQ==", {"tier": "free"})}, {"k": Entry("YQ==", {"tier": "pro"})},
                 {"k": Entry("YQ==", {"tier": "free"})})
    assert plan.puts == {"k": Entry("YQ==", {"tier": "pro"})}
    later = Entry("YQ==", None, NOW + 9999)
    assert merge({"k": A}, {"k": later}, {"k": A}) == Plan({}, [], [], [])


def test_skip_prefixes_and_expiring_soon_puts_are_listed_as_skipped():
    soon = Entry("Yg==", None, NOW + 59)
    ok = Entry("Yg==", None, NOW + 60)
    plan = merge({}, {"count:k1:decide:1": A, "soon": soon, "ok": ok}, {})
    assert plan == Plan({"ok": ok}, [], [], ["count:k1:decide:1", "soon"])


def test_first_copy_with_empty_base_puts_missing_and_conflicts_on_differing():
    plan = merge({}, {"key:a": A, "key:b": B, "session:c": C}, {"key:b": C, "session:c": C})
    assert plan == Plan({"key:a": A}, [], ["key:b"], [])


def test_summary_counts_by_prefix_and_names_conflicts_but_never_values():
    plan = Plan({"key:a": Entry("c2VjcmV0"), "key:b": A, "plain": A}, ["sub:x"], ["key:c"],
                ["count:z"])
    assert cf_move.summarize(plan) == [
        "3 put, 1 delete, 1 conflict, 1 skipped",
        "  put (no prefix) 1",
        "  put key: 2",
        "  delete sub: 1",
        "conflict key:c",
        "skipped count:z",
    ]


class FakeCF:
    """Records calls and answers from a route table keyed by (method, path-with-query)."""

    def __init__(self, routes):
        self.routes = routes
        self.calls = []

    def __call__(self, method, url, headers, body):
        path = url.removeprefix(cf_move.API)
        self.calls.append((method, path, headers, None if body is None else json.loads(body)))
        status, payload = self.routes[(method, path)]
        if isinstance(payload, bytes):
            return status, payload
        return status, json.dumps(payload).encode()


def ok(result, **result_info):
    return 200, {"success": True, "errors": [], "result": result, "result_info": result_info}


NS = "/accounts/acc/storage/kv/namespaces/ns"


def test_snapshot_follows_the_cursor_and_reads_each_value_as_base64():
    fake = FakeCF({
        ("GET", f"{NS}/keys?limit=1000"): ok(
            [{"name": "key:a", "metadata": {"t": 1}}], cursor="c1", count=1
        ),
        ("GET", f"{NS}/keys?limit=1000&cursor=c1"): ok(
            [{"name": "sub/x y", "expiration": NOW + 600}, {"name": "gone"}], cursor="", count=2
        ),
        ("GET", f"{NS}/values/key%3Aa"): (200, b"hello"),
        ("GET", f"{NS}/values/sub%2Fx%20y"): (200, b"\x00\xff"),
        ("GET", f"{NS}/values/gone"): (404, {"success": False, "errors": []}),
    })
    snap = KVClient("acc", "ns", TOKEN, fake).snapshot()
    assert snap == {"key:a": Entry("aGVsbG8=", {"t": 1}), "sub/x y": Entry("AP8=")}
    assert snap["sub/x y"].expiration == NOW + 600
    assert fake.calls[0][2] == {"Authorization": f"Bearer {TOKEN}"}


def test_apply_chunks_puts_at_ten_thousand_and_bulk_deletes_by_name():
    puts = {f"k{i:05d}": A for i in range(10_001)}
    puts["k00000"] = Entry("Yg==", {"m": 1}, NOW + 3600)
    fake = FakeCF({
        ("PUT", f"{NS}/bulk"): ok({"successful_key_count": 1, "unsuccessful_keys": []}),
        ("POST", f"{NS}/bulk/delete"): ok({"successful_key_count": 2, "unsuccessful_keys": ["d1"]}),
    })
    failed = KVClient("acc", "ns", TOKEN, fake).apply(Plan(puts, ["d1", "d2"], [], []))
    assert [(m, p, len(b)) for m, p, _, b in fake.calls] == [
        ("PUT", f"{NS}/bulk", 10_000),
        ("PUT", f"{NS}/bulk", 1),
        ("POST", f"{NS}/bulk/delete", 2),
    ]
    assert fake.calls[0][3][:2] == [
        {"key": "k00000", "value": "Yg==", "base64": True, "expiration": NOW + 3600,
         "metadata": {"m": 1}},
        {"key": "k00001", "value": "YQ==", "base64": True},
    ]
    assert fake.calls[2][3] == ["d1", "d2"]
    assert failed == ["d1"]


def test_api_errors_name_path_and_status_but_never_the_token():
    fake = FakeCF({
        ("GET", f"{NS}/keys?limit=1000"): (
            403, {"success": False, "errors": [{"code": 10000, "message": "Authentication error"}]}
        ),
    })
    with pytest.raises(cf_move.CFError) as caught:
        KVClient("acc", "ns", TOKEN, fake).snapshot()
    assert str(caught.value) == f"GET {NS}/keys: HTTP 403 (10000 Authentication error)"
    assert TOKEN not in str(caught.value)


def test_success_false_on_a_2xx_still_raises():
    fake = FakeCF({("POST", f"{NS}/bulk/delete"): (200, {"success": False, "errors": []})})
    with pytest.raises(cf_move.CFError, match=r"^POST .*/bulk/delete: success false$"):
        KVClient("acc", "ns", TOKEN, fake).apply(Plan({}, ["x"], [], []))


Z = "/zones/z1"


def zone_routes(overrides=None):
    routes = {
        ("GET", "/zones?name=modelspec.dev&account.id=acc"): ok(
            [{"id": "z1", "name": "modelspec.dev"}]
        ),
        ("GET", f"{Z}/dns_records?page=1&per_page=50"): ok(
            [{"id": "r1", "type": "A", "name": "modelspec.dev", "content": "192.0.2.1"}],
            page=1, total_pages=2,
        ),
        ("GET", f"{Z}/dns_records?page=2&per_page=50"): ok(
            [{"id": "r2", "type": "MX", "name": "modelspec.dev", "content": "mx.example"}],
            page=2, total_pages=2,
        ),
        ("GET", f"{Z}/dns_records/export"): (200, b"modelspec.dev.\t1\tIN\tA\t192.0.2.1\n"),
        ("GET", f"{Z}/settings"): ok([{"id": "ssl", "value": "strict", "editable": True}]),
        ("GET", f"{Z}/rulesets"): ok(
            [{"id": "rs1", "name": "z", "phase": "http_request_firewall_custom"}]
        ),
        ("GET", f"{Z}/rulesets/rs1"): ok({"id": "rs1", "phase": "http_request_firewall_custom",
                                          "rules": [{"id": "x", "expression": "true"}]}),
        ("GET", f"{Z}/pagerules"): (403, {"success": False, "errors": [{"code": 10000}]}),
        ("GET", f"{Z}/workers/routes"): ok([{"id": "w", "pattern": "api.modelspec.dev/*"}]),
        ("GET", f"{Z}/email/routing"): ok({"enabled": True}),
        ("GET", f"{Z}/email/routing/rules?page=1&per_page=50"): ok([], total_pages=1),
        ("GET", f"{Z}/email/routing/rules/catch_all"): ok({"enabled": False}),
        ("GET", f"{Z}/ssl/certificate_packs?page=1&per_page=50"): ok([], total_pages=1),
        ("GET", f"{Z}/dnssec"): ok({"status": "active"}),
    }
    routes.update(overrides or {})
    return routes


def test_zone_dump_pages_dns_and_records_a_forbidden_section_instead_of_failing():
    dump = cf_move.zone_dump("acc", "modelspec.dev", TOKEN, FakeCF(zone_routes()))
    assert dump["page_rules"] == {"unreadable": 403}
    assert [r["id"] for r in dump["dns_records"]] == ["r1", "r2"]
    assert dump["dns_export"] == "modelspec.dev.\t1\tIN\tA\t192.0.2.1\n"
    assert dump["rulesets"] == [{"id": "rs1", "phase": "http_request_firewall_custom",
                                 "rules": [{"id": "x", "expression": "true"}]}]
    assert dump["dnssec"] == {"status": "active"}


def test_zone_dump_still_fails_on_a_server_error():
    fake = FakeCF(zone_routes({("GET", f"{Z}/dnssec"): (500, b"oops")}))
    with pytest.raises(cf_move.CFError, match=r"^GET /zones/z1/dnssec: HTTP 500$"):
        cf_move.zone_dump("acc", "modelspec.dev", TOKEN, fake)


OLD = {
    "zone": {"id": "z1", "name": "modelspec.dev", "account": {"id": "acc1"}, "plan": "free"},
    "dns_records": [
        {"id": "r2", "type": "TXT", "name": "x", "content": "v=spf1", "modified_on": "2026-01-01"},
        {"id": "r1", "type": "A", "name": "x", "content": "192.0.2.1", "zone_id": "z1"},
    ],
    "dns_export": ";; Exported: 2026-10-01\nx. 1 IN SOA ns1. a. 7 1 1 1 1\nx. 1 IN A 192.0.2.1\n",
    "settings": [
        {"id": "ssl", "value": "strict", "modified_on": "t"},
        {"id": "ipv6", "value": "on"},
    ],
    "rulesets": [{"id": "rs", "version": "3", "rules": [{"id": "a", "expression": "1"},
                                                       {"id": "b", "expression": "2"}]}],
    "page_rules": {"unreadable": 403},
}


def test_normalize_drops_identity_and_time_fields_and_orders_lists():
    assert normalize(OLD) == {
        "zone": {"name": "modelspec.dev", "plan": "free"},
        "dns_records": [
            {"content": "192.0.2.1", "name": "x", "type": "A"},
            {"content": "v=spf1", "name": "x", "type": "TXT"},
        ],
        "dns_export": ["x. 1 IN A 192.0.2.1"],
        "settings": {"ipv6": "on", "ssl": "strict"},
        "rulesets": [{"rules": [{"expression": "1"}, {"expression": "2"}]}],
        "page_rules": {"unreadable": 403},
    }


def test_zone_diff_ignores_account_identity_and_reports_real_differences():
    new = json.loads(json.dumps(OLD))
    new["zone"].update(id="z9", account={"id": "acc2"})
    new["dns_records"].reverse()
    new["dns_records"][0].update(id="r7", modified_on="2026-10-22")
    assert zone_diff(OLD, new) == []

    new["settings"][0]["value"] = "full"
    new["dns_records"].append({"id": "r9", "type": "CNAME", "name": "www", "content": "x"})
    new["rulesets"][0]["rules"].reverse()
    new["page_rules"] = []
    assert zone_diff(OLD, new) == [
        'dns_records[]: a=<absent> b={"content":"x","name":"www","type":"CNAME"}',
        'page_rules: a={"unreadable":403} b=[]',
        "rulesets[]: a="
        '{"rules":[{"expression":"1"},{"expression":"2"}]} b=<absent>',
        "rulesets[]: a=<absent> b="
        '{"rules":[{"expression":"2"},{"expression":"1"}]}',
        'settings.ssl: a="strict" b="full"',
    ]


def test_snapshot_round_trips_through_its_file_form():
    snap = {"key:a": Entry("YQ==", {"t": 1}, NOW)}
    data = cf_move.snapshot_to_json(snap, "acc", "ns")
    back = cf_move.snapshot_from_json(json.loads(json.dumps(data)))
    assert back == snap and back["key:a"].expiration == NOW


def test_outputs_are_private_and_never_written_inside_the_repository(tmp_path, monkeypatch):
    inside = cf_move.REPO_ROOT / "kv-snapshot-should-not-exist.json"
    monkeypatch.setenv("CF_API_TOKEN", TOKEN)
    monkeypatch.setattr(cf_move, "urllib_request", lambda *a: pytest.fail("network used"))
    argv = ["kv-snapshot", "--account", "acc", "--namespace", "ns", "--out", str(inside)]
    assert cf_move.main(argv) == 2
    assert not inside.exists()

    out = tmp_path / "snap.json"
    out.write_text("old")
    out.chmod(0o644)
    cf_move.write_private(cf_move.check_out_path(out), {"entries": {}})
    assert stat.S_IMODE(out.stat().st_mode) == 0o600
    assert json.loads(out.read_text()) == {"entries": {}}


def test_kv_merge_dry_run_prints_the_plan_and_exits_one_on_conflict(tmp_path, monkeypatch, capsys):
    src_ns = "/accounts/old/storage/kv/namespaces/n1"
    dst_ns = "/accounts/new/storage/kv/namespaces/n2"
    fake = FakeCF({
        ("GET", f"{src_ns}/keys?limit=1000"): ok([{"name": "key:a"}, {"name": "key:b"}], cursor=""),
        ("GET", f"{src_ns}/values/key%3Aa"): (200, b"a"),
        ("GET", f"{src_ns}/values/key%3Ab"): (200, b"b"),
        ("GET", f"{dst_ns}/keys?limit=1000"): ok([{"name": "key:b"}], cursor=""),
        ("GET", f"{dst_ns}/values/key%3Ab"): (200, b"other"),
    })
    monkeypatch.setattr(cf_move, "urllib_request", fake)
    monkeypatch.setenv("CF_SRC_API_TOKEN", "src-tok")
    monkeypatch.setenv("CF_DST_API_TOKEN", "dst-tok")
    saved = tmp_path / "base.json"
    code = cf_move.main([
        "kv-merge", "--base", "empty", "--save-src", str(saved), "--now", str(NOW),
        "--src-account", "old", "--src-namespace", "n1",
        "--dst-account", "new", "--dst-namespace", "n2",
    ])
    out = capsys.readouterr().out
    assert code == 1
    assert out.splitlines()[1:] == [
        "dry run: 1 put, 0 delete, 1 conflict, 0 skipped",
        "  put key: 1",
        "conflict key:b",
    ]
    assert "YQ==" not in out
    assert all(method == "GET" for method, *_ in fake.calls)
    assert cf_move.snapshot_from_json(json.loads(saved.read_text())) == {
        "key:a": Entry("YQ=="), "key:b": Entry("Yg==")
    }


class ZoneApi:
    """A zone that turns active after `pending_polls` status reads."""

    def __init__(self, pending_polls, routes):
        self.pending_polls = pending_polls
        self.routes = routes
        self.writes = []

    def __call__(self, method, url, headers, body):
        path = url.removeprefix(cf_move.API).split("?")[0]
        if path == "/zones":
            status = "pending" if self.pending_polls else "active"
            return 200, json.dumps({"success": True, "result": [{"id": "z1", "status": status}]}).encode()
        if path == "/zones/z1":
            self.pending_polls = max(0, self.pending_polls - 1)
            status = "pending" if self.pending_polls else "active"
            return 200, json.dumps({"success": True, "result": {"id": "z1", "status": status}}).encode()
        if path == "/zones/z1/workers/routes" and method == "GET":
            return 200, json.dumps({"success": True, "result": self.routes}).encode()
        self.writes.append((method, path, json.loads(body)))
        return 200, json.dumps({"success": True, "result": {}}).encode()


def test_attach_routes_waits_for_the_zone_then_adds_moves_and_keeps_routes():
    api = ZoneApi(3, [{"id": "r1", "pattern": "api.modelspec.dev/mcp*", "script": "old-mcp"},
                      {"id": "r2", "pattern": "api.modelspec.dev/*", "script": "modelspec-rank"}])
    slept = []

    done = cf_move.attach_routes(
        "acct", "modelspec.dev",
        [("api.modelspec.dev/*", "modelspec-rank"), ("api.modelspec.dev/mcp*", "modelspec-mcp"),
         ("api.modelspec.dev/.well-known/mcp/server-card.json", "modelspec-mcp")],
        TOKEN, api, wait_active=True, sleep=slept.append)

    assert len(slept) == 3
    assert done == ["kept api.modelspec.dev/* -> modelspec-rank",
                    "moved api.modelspec.dev/mcp* -> modelspec-mcp",
                    "added api.modelspec.dev/.well-known/mcp/server-card.json -> modelspec-mcp"]
    assert api.writes == [
        ("PUT", "/zones/z1/workers/routes/r1", {"pattern": "api.modelspec.dev/mcp*", "script": "modelspec-mcp"}),
        ("POST", "/zones/z1/workers/routes",
         {"pattern": "api.modelspec.dev/.well-known/mcp/server-card.json", "script": "modelspec-mcp"}),
    ]


def test_attach_routes_refuses_a_pending_zone_without_waiting_and_times_out_when_asked():
    with pytest.raises(cf_move.CFError, match="routes need an active zone"):
        cf_move.attach_routes("acct", "modelspec.dev", [("a/*", "w")], TOKEN, ZoneApi(1, []))
    ticks = iter([0.0, 0.0, 5.0])
    with pytest.raises(cf_move.CFError, match="still pending"):
        cf_move.attach_routes("acct", "modelspec.dev", [("a/*", "w")], TOKEN, ZoneApi(9, []),
                              wait_active=True, timeout_seconds=4, sleep=lambda _s: None,
                              clock=lambda: next(ticks))


def test_route_specs_split_on_the_last_equals_sign():
    assert cf_move.parse_route("api.modelspec.dev/*=modelspec-rank") == ("api.modelspec.dev/*", "modelspec-rank")
    with pytest.raises(cf_move.UsageError):
        cf_move.parse_route("api.modelspec.dev/*")
