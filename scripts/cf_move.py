#!/usr/bin/env python3
"""Move Workers KV namespaces and audit a zone between two Cloudflare accounts (MODEL-441).

KV: copy once with an empty base and keep the source snapshot (`--save-src`) as the
base. After the zone moves, merge again with that base. The merge applies only the
keys the old Worker changed after the base. Any key both sides changed is reported
as a conflict and never overwritten.

Zone: dump a zone's configuration read-only from each account, then diff the two
dumps to find what the DNS export does not carry.

    CF_API_TOKEN=... python scripts/cf_move.py kv-snapshot --account A --namespace N --out F
    CF_SRC_API_TOKEN=... CF_DST_API_TOKEN=... python scripts/cf_move.py kv-merge \\
        --base empty --save-src base.json --src-account A --src-namespace N \\
        --dst-account B --dst-namespace M [--apply]
    CF_API_TOKEN=... python scripts/cf_move.py zone-dump --account A --zone modelspec.dev --out F
    python scripts/cf_move.py zone-diff old.json new.json
    CF_API_TOKEN=... python scripts/cf_move.py attach-routes --account B --zone modelspec.dev \
        --route 'api.modelspec.dev/*=modelspec-rank' --wait-active

Routes: Workers routes need an active zone, so the new account's Workers deploy
without them and `attach-routes --wait-active` adds them the moment the moved
zone turns Active.

Snapshots and dumps hold stored values: they are written mode 0600 and never
inside this repository's working tree.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
API = "https://api.cloudflare.com/client/v4"
# Cloudflare refuses an expiration less than 60 seconds ahead.
MIN_EXPIRY_AHEAD = 60
# Bulk write and bulk delete take at most 10,000 keys and 100 MB per request.
BULK_MAX_ITEMS = 10_000
BULK_MAX_BYTES = 90_000_000
DEFAULT_SKIP_PREFIXES = ("count:",)
EMPTY_BASE = ("-", "empty")

Request = Callable[[str, str, dict[str, str], bytes | None], tuple[int, bytes]]


class CFError(Exception):
    """A Cloudflare call failed. The message names the path and status, never secrets."""

    def __init__(self, message: str, status: int | None = None):
        super().__init__(message)
        self.status = status


class UsageError(Exception):
    pass


@dataclass(frozen=True)
class Entry:
    """One stored KV pair. Two entries are equal when value and metadata match."""

    value_b64: str
    metadata: dict | None = None
    expiration: int | None = field(default=None, compare=False)


@dataclass(frozen=True)
class Plan:
    puts: dict[str, Entry]
    deletes: list[str]
    conflicts: list[str]
    skipped: list[str]


def plan_merge(
    base: dict[str, Entry],
    src: dict[str, Entry],
    dst: dict[str, Entry],
    *,
    skip_prefixes: tuple[str, ...],
    now: int,
) -> Plan:
    """Three-way merge of src into dst since base; a missing key is None on any side."""
    puts: dict[str, Entry] = {}
    deletes: list[str] = []
    conflicts: list[str] = []
    skipped: list[str] = []
    for key in sorted(base.keys() | src.keys()):
        if key.startswith(skip_prefixes):
            skipped.append(key)
            continue
        b, s, d = base.get(key), src.get(key), dst.get(key)
        if s == b:
            continue
        if d == b:
            if s is None:
                deletes.append(key)
            elif s.expiration is not None and s.expiration < now + MIN_EXPIRY_AHEAD:
                skipped.append(key)
            else:
                puts[key] = s
        elif d != s:
            conflicts.append(key)
    return Plan(puts, deletes, conflicts, skipped)


def key_prefix(key: str) -> str:
    head, sep, _ = key.partition(":")
    return f"{head}:" if sep else "(no prefix)"


def summarize(plan: Plan) -> list[str]:
    """Counts per prefix plus conflict and skipped key names. Never values."""
    lines = [
        f"{len(plan.puts)} put, {len(plan.deletes)} delete, "
        f"{len(plan.conflicts)} conflict, {len(plan.skipped)} skipped"
    ]
    for action, keys in (("put", plan.puts), ("delete", plan.deletes)):
        counts = Counter(key_prefix(k) for k in keys)
        lines += [f"  {action} {prefix} {n}" for prefix, n in sorted(counts.items())]
    lines += [f"conflict {k}" for k in plan.conflicts]
    lines += [f"skipped {k}" for k in plan.skipped]
    return lines


def urllib_request(
    method: str, url: str, headers: dict[str, str], body: bytes | None
) -> tuple[int, bytes]:
    req = urllib.request.Request(url, data=body, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read()


class Api:
    """Bearer-token calls to the v4 API. The token stays in the Authorization header."""

    def __init__(self, token: str, request: Request):
        self._token = token
        self._request = request

    def _call(self, method: str, path: str, body: bytes | None) -> bytes:
        headers = {"Authorization": f"Bearer {self._token}"}
        if body is not None:
            headers["Content-Type"] = "application/json"
        status, raw = self._request(method, API + path, headers, body)
        if not 200 <= status < 300:
            raise CFError(f"{method} {path.split('?')[0]}: HTTP {status}{_codes(raw)}", status)
        return raw

    def raw(self, method: str, path: str) -> bytes:
        return self._call(method, path, None)

    def json(self, method: str, path: str, payload: object = None) -> dict:
        body = None if payload is None else json.dumps(payload).encode()
        raw = self._call(method, path, body)
        envelope = json.loads(raw)
        if not envelope.get("success", False):
            raise CFError(f"{method} {path.split('?')[0]}: success false{_codes(raw)}")
        return envelope

    def result(self, path: str):
        return self.json("GET", path)["result"]

    def paged(self, path: str, per_page: int = 50) -> list:
        items: list = []
        page = 1
        while True:
            query = urllib.parse.urlencode({"page": page, "per_page": per_page})
            envelope = self.json("GET", f"{path}?{query}")
            items.extend(envelope.get("result") or [])
            total_pages = (envelope.get("result_info") or {}).get("total_pages") or 1
            if page >= total_pages:
                return items
            page += 1


def _codes(raw: bytes) -> str:
    try:
        errors = json.loads(raw).get("errors") or []
    except (ValueError, AttributeError):
        return ""
    parts = [
        f"{e.get('code')} {e.get('message', '')}".strip()
        for e in errors
        if isinstance(e, dict)
    ]
    return f" ({'; '.join(parts)})" if parts else ""


def _chunks(items: list, max_items: int, max_bytes: int) -> Iterator[list]:
    chunk: list = []
    size = 0
    for item in items:
        item_size = len(json.dumps(item))
        if chunk and (len(chunk) >= max_items or size + item_size > max_bytes):
            yield chunk
            chunk, size = [], 0
        chunk.append(item)
        size += item_size
    if chunk:
        yield chunk


class KVClient:
    """One Workers KV namespace over the REST API."""

    def __init__(
        self, account_id: str, namespace_id: str, token: str, request: Request = urllib_request
    ):
        self._api = Api(token, request)
        self._base = f"/accounts/{account_id}/storage/kv/namespaces/{namespace_id}"

    def snapshot(self, skip_prefixes: tuple[str, ...] = ()) -> dict[str, Entry]:
        # https://developers.cloudflare.com/api/resources/kv/subresources/namespaces/subresources/keys/methods/list/
        listed: list[dict] = []
        cursor = ""
        while True:
            query = {"limit": 1000, **({"cursor": cursor} if cursor else {})}
            envelope = self._api.json("GET", f"{self._base}/keys?{urllib.parse.urlencode(query)}")
            listed.extend(envelope.get("result") or [])
            cursor = (envelope.get("result_info") or {}).get("cursor") or ""
            if not cursor:
                break
        entries: dict[str, Entry] = {}
        for item in listed:
            name = item["name"]
            if name.startswith(skip_prefixes):  # the merge skips them; do not pay a read each
                continue
            try:
                raw = self._api.raw(
                    "GET", f"{self._base}/values/{urllib.parse.quote(name, safe='')}"
                )
            except CFError as exc:
                if exc.status == 404:  # expired or deleted between the listing and the read
                    continue
                raise
            entries[name] = Entry(
                base64.b64encode(raw).decode(), item.get("metadata"), item.get("expiration")
            )
        return entries

    def apply(self, plan: Plan) -> list[str]:
        """Write the plan's puts and deletes. Returns the keys Cloudflare reports unwritten."""
        failed: list[str] = []
        items = [_bulk_item(key, entry) for key, entry in sorted(plan.puts.items())]
        # https://developers.cloudflare.com/api/resources/kv/subresources/namespaces/methods/bulk_update/
        for chunk in _chunks(items, BULK_MAX_ITEMS, BULK_MAX_BYTES):
            failed += self._unsuccessful(self._api.json("PUT", f"{self._base}/bulk", chunk))
        # https://developers.cloudflare.com/api/resources/kv/subresources/namespaces/methods/bulk_delete/
        for chunk in _chunks(plan.deletes, BULK_MAX_ITEMS, BULK_MAX_BYTES):
            failed += self._unsuccessful(self._api.json("POST", f"{self._base}/bulk/delete", chunk))
        return failed

    @staticmethod
    def _unsuccessful(envelope: dict) -> list[str]:
        return list((envelope.get("result") or {}).get("unsuccessful_keys") or [])


def _bulk_item(key: str, entry: Entry) -> dict:
    item: dict = {"key": key, "value": entry.value_b64, "base64": True}
    if entry.expiration is not None:
        item["expiration"] = entry.expiration
    if entry.metadata is not None:
        item["metadata"] = entry.metadata
    return item


def snapshot_to_json(entries: dict[str, Entry], account_id: str, namespace_id: str) -> dict:
    return {
        "account": account_id,
        "namespace": namespace_id,
        "entries": {
            k: {"value_b64": e.value_b64, "metadata": e.metadata, "expiration": e.expiration}
            for k, e in sorted(entries.items())
        },
    }


def snapshot_from_json(data: dict) -> dict[str, Entry]:
    return {
        k: Entry(v["value_b64"], v.get("metadata"), v.get("expiration"))
        for k, v in data["entries"].items()
    }


# Zone side. Each section is read independently so one the token cannot read
# does not sink the whole dump.

ZoneReader = Callable[[Api, str], object]


def _one(suffix: str) -> ZoneReader:
    return lambda api, zone: api.result(zone + suffix)


def _paged(suffix: str) -> ZoneReader:
    return lambda api, zone: api.paged(zone + suffix)


def _text(suffix: str) -> ZoneReader:
    return lambda api, zone: api.raw("GET", zone + suffix).decode()


def _rulesets(api: Api, zone: str) -> list:
    full = []
    for summary in api.result(f"{zone}/rulesets") or []:
        try:
            full.append(api.result(f"{zone}/rulesets/{summary['id']}"))
        except CFError as exc:
            if not _is_unreadable(exc):
                raise
            full.append({"name": summary.get("name"), "phase": summary.get("phase"),
                         "unreadable": exc.status})
    return full


ZONE_SECTIONS: tuple[tuple[str, ZoneReader], ...] = (
    ("dns_records", _paged("/dns_records")),
    ("dns_export", _text("/dns_records/export")),
    ("settings", _one("/settings")),
    ("rulesets", _rulesets),
    ("page_rules", _one("/pagerules")),
    ("workers_routes", _one("/workers/routes")),
    ("email_routing", _one("/email/routing")),
    ("email_routing_rules", _paged("/email/routing/rules")),
    ("email_routing_catch_all", _one("/email/routing/rules/catch_all")),
    ("certificate_packs", _paged("/ssl/certificate_packs")),
    ("dnssec", _one("/dnssec")),
)


def parse_route(spec: str) -> tuple[str, str]:
    pattern, sep, script = spec.rpartition("=")
    if not sep or not pattern or not script:
        raise UsageError(f"route must be PATTERN=SCRIPT, got {spec!r}")
    return pattern, script


def attach_routes(
    account_id: str,
    zone_name: str,
    routes: list[tuple[str, str]],
    token: str,
    request: Request = urllib_request,
    *,
    wait_active: bool = False,
    probe: bool = False,
    poll_seconds: float = 1.0,
    timeout_seconds: float = 0,
    sleep: Callable[[float], None] = time.sleep,
    clock: Callable[[], float] = time.monotonic,
) -> list[str]:
    """Make each pattern route to its script on the zone. Idempotent: existing
    matching routes are left alone, a pattern bound to another script is moved."""
    api = Api(token, request)
    query = urllib.parse.urlencode({"name": zone_name, "account.id": account_id})
    zones = api.result(f"/zones?{query}") or []
    if len(zones) != 1:
        raise CFError(f"zone {zone_name}: {len(zones)} matches in account {account_id}")
    zone_path = f"/zones/{zones[0]['id']}"
    status = zones[0].get("status")
    deadline = clock() + timeout_seconds if timeout_seconds else None
    while wait_active and not probe and status != "active":
        if deadline is not None and clock() >= deadline:
            raise CFError(f"zone {zone_name} is still {status}")
        sleep(poll_seconds)
        status = api.result(zone_path).get("status")
    if probe:
        # Proves the token can write routes on this zone before anything
        # depends on it: a throwaway route with no Worker, deleted at once.
        made = api.json("POST", f"{zone_path}/workers/routes",
                        {"pattern": f"{zone_name}/__cf-move-probe-{int(clock() * 1000)}*"})
        api.json("DELETE", f"{zone_path}/workers/routes/{made['result']['id']}")
        return [f"probe ok: this token can write routes on {zone_name} ({status})"]
    if status != "active":
        raise CFError(f"zone {zone_name} is {status}; routes need an active zone")
    # https://developers.cloudflare.com/api/resources/workers/subresources/routes/methods/create/
    existing = {r["pattern"]: r for r in api.result(f"{zone_path}/workers/routes") or []}
    done: list[str] = []
    for pattern, script in routes:
        current = existing.get(pattern)
        if current is None:
            api.json("POST", f"{zone_path}/workers/routes", {"pattern": pattern, "script": script})
            done.append(f"added {pattern} -> {script}")
        elif current.get("script") != script:
            api.json("PUT", f"{zone_path}/workers/routes/{current['id']}",
                     {"pattern": pattern, "script": script})
            done.append(f"moved {pattern} -> {script}")
        else:
            done.append(f"kept {pattern} -> {script}")
    return done


def _is_unreadable(exc: CFError) -> bool:
    # A 4xx on one section (no permission, feature off for the zone) is recorded;
    # rate limits and server errors still fail the dump.
    return exc.status is not None and 400 <= exc.status < 500 and exc.status != 429


def zone_dump(
    account_id: str, zone_name: str, token: str, request: Request = urllib_request
) -> dict:
    api = Api(token, request)
    query = urllib.parse.urlencode({"name": zone_name, "account.id": account_id})
    zones = api.result(f"/zones?{query}") or []
    if len(zones) != 1:
        raise CFError(f"zone {zone_name}: {len(zones)} matches in account {account_id}")
    dump: dict = {"zone": zones[0]}
    zone_path = f"/zones/{zones[0]['id']}"
    for name, read in ZONE_SECTIONS:
        try:
            dump[name] = read(api, zone_path)
        except CFError as exc:
            if not _is_unreadable(exc):
                raise
            dump[name] = {"unreadable": exc.status}
    return dump


VOLATILE_FIELDS = (
    "id", "zone_id", "zone_name", "created_on", "modified_on", "last_modified", "last_updated",
    "activated_on", "comment_modified_on", "tags_modified_on", "uploaded_on", "expires_on",
    "time_remaining", "version", "account", "owner", "tag", "ref", "permissions",
    "primary_certificate", "validation_records",
)
# Lists under these keys run in order (ruleset rules), so their order is kept.
ORDERED_LISTS = ("rules",)
# Inside these, an `id` or `version` is what runs (the managed ruleset a rule
# executes, and its version), not an identity, so nothing below them is dropped.
SEMANTIC_SUBTREES = ("action_parameters",)


def _canon(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _strip(value: object, ordered: bool = False, keep: bool = False) -> object:
    if isinstance(value, dict):
        return {
            k: _strip(v, k in ORDERED_LISTS, keep or k in SEMANTIC_SUBTREES)
            for k, v in sorted(value.items())
            if keep or k not in VOLATILE_FIELDS
        }
    if isinstance(value, list):
        items = [_strip(v, keep=keep) for v in value]
        return items if ordered else sorted(items, key=_canon)
    return value


def normalize(dump: dict) -> dict:
    """Drop identity and timestamp fields and order lists so two accounts compare."""
    shaped = dict(dump)
    if isinstance(shaped.get("settings"), list):
        # A setting's `id` is its name, not an identity field.
        shaped["settings"] = {s["id"]: s.get("value") for s in shaped["settings"]}
    if isinstance(shaped.get("dns_export"), str):
        # Comment lines carry the export time; the SOA carries the serial and account NS.
        shaped["dns_export"] = sorted(
            line for line in shaped["dns_export"].splitlines()
            if line.strip() and not line.lstrip().startswith(";") and "SOA" not in line.split()
        )
    return _strip(shaped)


ABSENT = "<absent>"


def _show(value: object) -> str:
    return ABSENT if value is ABSENT else _canon(value)


def _diff(a: object, b: object, path: str, out: list[str]) -> None:
    if a == b:
        return
    if isinstance(a, dict) and isinstance(b, dict):
        for key in sorted(a.keys() | b.keys()):
            _diff(a.get(key, ABSENT), b.get(key, ABSENT), f"{path}.{key}" if path else key, out)
        return
    if isinstance(a, list) and isinstance(b, list):
        a_set = {_canon(x): x for x in a}
        b_set = {_canon(x): x for x in b}
        if a_set.keys() == b_set.keys():
            out.append(f"{path}: same items, order differs")
            return
        out += [f"{path}[]: a={k} b={ABSENT}" for k in sorted(a_set.keys() - b_set.keys())]
        out += [f"{path}[]: a={ABSENT} b={k}" for k in sorted(b_set.keys() - a_set.keys())]
        return
    out.append(f"{path}: a={_show(a)} b={_show(b)}")


def zone_diff(a: dict, b: dict) -> list[str]:
    out: list[str] = []
    _diff(normalize(a), normalize(b), "", out)
    return out


def check_out_path(path: Path) -> Path:
    resolved = path.expanduser().resolve()
    if resolved == REPO_ROOT or REPO_ROOT in resolved.parents:
        raise UsageError(f"refusing to write stored values inside the repository: {resolved}")
    return resolved


def write_private(path: Path, data: object) -> None:
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    os.fchmod(fd, 0o600)
    with os.fdopen(fd, "w") as fh:
        json.dump(data, fh, indent=1, sort_keys=True)
        fh.write("\n")


def _token(name: str) -> str:
    value = os.environ.get(name, "")
    if not value:
        raise UsageError(f"set {name}")
    return value


def _cmd_kv_snapshot(args: argparse.Namespace) -> int:
    out = check_out_path(args.out)
    client = KVClient(args.account, args.namespace, _token("CF_API_TOKEN"), urllib_request)
    entries = client.snapshot()
    write_private(out, snapshot_to_json(entries, args.account, args.namespace))
    print(f"wrote {len(entries)} entries to {out}")
    return 0


def destination_frozen(origin: str, secret: str, request: Request = urllib_request) -> str:
    """The destination Worker's ledger role, which must not be `live` while
    the merge writes (MODEL-441). A frozen ledger makes the Worker refuse every
    write to key records, so the destination snapshot cannot go stale between
    the read and the write. Raises UsageError otherwise."""
    status, raw = request("GET", origin.rstrip("/") + "/internal/ledger/status",
                          {"Authorization": f"Bearer {secret}"}, None)
    role = ""
    if status == 200:
        try:
            role = str(json.loads(raw).get("role") or "")
        except ValueError:
            role = ""
    if role not in ("standby", "sealed"):
        raise UsageError(
            f"the destination ledger at {origin} is not frozen (HTTP {status}, role {role or '?'}): "
            "its Worker may write key records, so a merge could overwrite them")
    return role


def _cmd_kv_merge(args: argparse.Namespace) -> int:
    save_src = check_out_path(args.save_src) if args.save_src else None
    src_token, dst_token = _token("CF_SRC_API_TOKEN"), _token("CF_DST_API_TOKEN")
    if args.apply:
        if not args.dst_worker:
            raise UsageError("--apply needs --dst-worker, the destination Worker's origin")
        destination_frozen(args.dst_worker, _token("LEDGER_ADMIN_SECRET"), urllib_request)
    if args.base in EMPTY_BASE:
        base: dict[str, Entry] = {}
    else:
        base = snapshot_from_json(json.loads(Path(args.base).read_text()))
    skip = tuple(args.skip_prefix or DEFAULT_SKIP_PREFIXES)
    src = KVClient(args.src_account, args.src_namespace, src_token, urllib_request).snapshot(skip)
    if save_src:
        write_private(save_src, snapshot_to_json(src, args.src_account, args.src_namespace))
        print(f"wrote source snapshot ({len(src)} entries) to {save_src}")
    dst_client = KVClient(args.dst_account, args.dst_namespace, dst_token, urllib_request)
    plan = plan_merge(
        base,
        src,
        dst_client.snapshot(skip),
        skip_prefixes=skip,
        now=args.now if args.now is not None else int(time.time()),
    )
    print(("apply: " if args.apply else "dry run: ") + "\n".join(summarize(plan)))
    if args.apply:
        failed = dst_client.apply(plan)
        destination_frozen(args.dst_worker, _token("LEDGER_ADMIN_SECRET"), urllib_request)
        if failed:
            print("\n".join(f"unwritten {k}" for k in failed), file=sys.stderr)
            return 2
    return 1 if plan.conflicts else 0


def _cmd_zone_dump(args: argparse.Namespace) -> int:
    out = check_out_path(args.out)
    dump = zone_dump(args.account, args.zone, _token("CF_API_TOKEN"), urllib_request)
    write_private(out, dump)
    unreadable = [k for k, v in dump.items() if isinstance(v, dict) and "unreadable" in v]
    print(f"wrote {args.zone} to {out}")
    for section in unreadable:
        print(f"unreadable {section}: HTTP {dump[section]['unreadable']}", file=sys.stderr)
    return 0


def _cmd_zone_diff(args: argparse.Namespace) -> int:
    lines = zone_diff(json.loads(Path(args.a).read_text()), json.loads(Path(args.b).read_text()))
    print("\n".join(lines) if lines else "no differences")
    return 1 if lines else 0


def _cmd_attach_routes(args: argparse.Namespace) -> int:
    routes = [parse_route(spec) for spec in args.route or []]
    if not routes and not args.probe:
        raise UsageError("give at least one --route, or --probe")
    for line in attach_routes(
        args.account, args.zone, routes, _token("CF_API_TOKEN"), urllib_request,
        wait_active=args.wait_active, probe=args.probe, poll_seconds=args.poll,
        timeout_seconds=args.timeout,
    ):
        print(line)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)

    snap = sub.add_parser("kv-snapshot", help="save every key, value and metadata (CF_API_TOKEN)")
    snap.add_argument("--account", required=True)
    snap.add_argument("--namespace", required=True)
    snap.add_argument("--out", type=Path, required=True)
    snap.set_defaults(run=_cmd_kv_snapshot)

    merge = sub.add_parser(
        "kv-merge", help="merge source changes since base into destination (CF_SRC/DST_API_TOKEN)"
    )
    merge.add_argument("--base", required=True, help="base snapshot file, or '-'/'empty'")
    merge.add_argument("--src-account", required=True)
    merge.add_argument("--src-namespace", required=True)
    merge.add_argument("--dst-account", required=True)
    merge.add_argument("--dst-namespace", required=True)
    merge.add_argument(
        "--skip-prefix", action="append", help="key prefix to leave alone (default: count:)"
    )
    merge.add_argument("--apply", action="store_true", help="write; default is a dry run")
    merge.add_argument(
        "--dst-worker",
        help="destination Worker origin; with --apply its ledger must be frozen (LEDGER_ADMIN_SECRET)")
    merge.add_argument("--now", type=int, help="epoch seconds; default: now")
    merge.add_argument(
        "--save-src", type=Path, help="write the source snapshot this merge used (the next base)"
    )
    merge.set_defaults(run=_cmd_kv_merge)

    dump = sub.add_parser("zone-dump", help="read-only dump of a zone's config (CF_API_TOKEN)")
    dump.add_argument("--account", required=True)
    dump.add_argument("--zone", required=True)
    dump.add_argument("--out", type=Path, required=True)
    dump.set_defaults(run=_cmd_zone_dump)

    diff = sub.add_parser("zone-diff", help="compare two zone dumps")
    diff.add_argument("a")
    diff.add_argument("b")
    diff.set_defaults(run=_cmd_zone_diff)

    attach = sub.add_parser(
        "attach-routes", help="route patterns to Workers once the zone is active (CF_API_TOKEN)"
    )
    attach.add_argument("--account", required=True)
    attach.add_argument("--zone", required=True)
    attach.add_argument("--route", action="append", help="PATTERN=SCRIPT")
    attach.add_argument("--probe", action="store_true",
                        help="only prove this token can write routes on the zone")
    attach.add_argument("--wait-active", action="store_true", help="poll until the zone is active")
    attach.add_argument("--poll", type=float, default=1.0, help="seconds between polls")
    attach.add_argument("--timeout", type=float, default=0, help="seconds; 0 waits forever")
    attach.set_defaults(run=_cmd_attach_routes)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.run(args)
    except (UsageError, CFError, OSError, ValueError, KeyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
