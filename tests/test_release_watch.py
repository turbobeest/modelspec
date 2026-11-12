"""The primary-source release watcher (MODEL-216)."""

from __future__ import annotations

import asyncio
import importlib.util
import json
import re
import sys
from datetime import UTC, date, datetime
from pathlib import Path

import httpx
import pytest
import yaml
from jsonschema import Draft202012Validator, FormatChecker

from decision.excluded import REMOVED_HOSTS
from release_signals import watch
from release_signals.contract import ReleaseSignal, SignalError
from release_signals.scope import IN_SCOPE_PIPELINE_TAGS, OUT_OF_SCOPE_PIPELINE_TAGS
from release_signals.watch import (
    Registry,
    Response,
    Seen,
    Source,
    SourceRun,
    _normalise,
    discoveries,
    extract,
    load_baseline,
    load_catalogue,
    load_registry,
    run_all,
    signal_id,
)
from scripts import process_release_signals as processor
from scripts import release_watch
from scripts.release_watch_filter import filter_releases

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "release_watch"
NOW = datetime(2026, 9, 29, 20, 0, tzinfo=UTC)
PAGE = "https://docs.acme.example/models"
HF = "https://huggingface.co/api/models?author=acme-lab&sort=createdAt&direction=-1&limit=100"
OPENROUTER = "https://openrouter.ai/api/v1/models"
FILES = {PAGE: "acme-models.html", HF: "hf-acme.json", OPENROUTER: "openrouter.json"}
DISCOVERY_SCHEMA = json.loads(
    (ROOT / "schemas" / "release-discovery-v1.schema.json").read_text(encoding="utf-8")
)
SIGNAL_SCHEMA = json.loads(
    (ROOT / "schemas" / "release-signal-v1.schema.json").read_text(encoding="utf-8")
)


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


def _service():
    spec = importlib.util.spec_from_file_location(
        "release_watch_signals_service", ROOT / "api" / "worker" / "src" / "signals_service.py"
    )
    service = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = service
    spec.loader.exec_module(service)
    return service


def _catalogue(root: Path) -> Path:
    card = root / "models" / "acme" / "acme-one-1.md"
    card.parent.mkdir(parents=True)
    card.write_text(
        "---\nmodel_id: acme/acme-one-1\ndisplay_name: Acme One 1\nprovider: acme\n"
        "provider_display: Acme\nversion: acme-one-1\n---\n",
        encoding="utf-8",
    )
    return root


def _registry(root: Path) -> Path:
    path = root / "release-watch.yaml"
    real = yaml.safe_load((ROOT / "registry" / "release-watch.yaml").read_text(encoding="utf-8"))
    path.write_text(yaml.safe_dump({
        "user_agent": real["user_agent"],
        "recent_days": real["recent_days"],
        "variant_exclude": real["variant_exclude"],
        "page_exclude": real["page_exclude"],
        "sources": [
            {"id": "acme-models", "kind": "page", "url": PAGE, "provider": "acme",
             "pattern": "acme-[a-z0-9][a-z0-9.-]*[a-z0-9]", "confidence": 0.9},
            {"id": "hf-acme", "kind": "huggingface", "org": "acme-lab",
             "provider": "Acme", "confidence": 0.7},
            {"id": "openrouter", "kind": "openrouter", "url": OPENROUTER,
             "providers": {"acme": "acme"}, "confidence": 0.8},
        ],
    }), encoding="utf-8")
    return path


def replay(state: str, *, down: frozenset[str] = frozenset(), robots: int = 404):
    """Serve the fixture set `state`; URLs in `down` fail as a dead host would."""

    def fetch(url: str) -> Response:
        if any(url.startswith(prefix) for prefix in down):
            raise httpx.ConnectError(f"cannot reach {url}")
        if url.endswith("/robots.txt"):
            return Response(robots, b"")
        return Response(200, (FIXTURES / state / FILES[url]).read_bytes())

    return fetch


@pytest.fixture
def world(tmp_path: Path):
    root = _catalogue(tmp_path)
    registry = load_registry(_registry(root))
    fetch = replay("before")
    baseline = {
        source.id: frozenset(extract(source, fetch(source.url).body, registry))
        for source in registry.sources
    }
    return registry, baseline, load_catalogue(root)


@pytest.mark.parametrize("repos", [["other-lab/orbit-3"], ["acme-lab/orbit-3", "other-lab/orbit-4"]])
def test_huggingface_foreign_owner_cannot_be_credited_to_requested_lab(world, repos) -> None:
    registry, baseline, _ = world
    normal_fetch = replay("before")

    def fetch(url: str) -> Response:
        if url == HF:
            return Response(200, json.dumps([
                {"id": repo, "createdAt": "2026-09-29T00:00:00Z"} for repo in repos
            ]).encode())
        return normal_fetch(url)

    runs = run_all(registry, baseline, fetch=fetch, now=NOW)

    assert filter_releases(runs, NOW)["signals"] == []
    assert [run.status for run in runs] == ["ok", "parse_failed", "ok"]
    assert "owner" in runs[1].detail


@pytest.mark.parametrize("owner", ["acme-lab", "ACME-LAB"])
def test_huggingface_configured_author_maps_to_provider(world, owner: str) -> None:
    registry, baseline, _ = world
    normal_fetch = replay("before")

    def fetch(url: str) -> Response:
        if url == HF:
            return Response(200, json.dumps([
                {"id": f"{owner}/Orbit-3", "createdAt": "2026-09-29T00:00:00Z"},
            ]).encode())
        return normal_fetch(url)

    runs = run_all(registry, baseline, fetch=fetch, now=NOW)
    signals = filter_releases(runs, NOW)["signals"]

    assert [run.status for run in runs] == ["ok", "ok", "ok"]
    assert len(signals) == 1
    assert signals[0].provider == "acme"
    assert signals[0].model_name == "Orbit-3"
    assert signals[0].first_seen_url == f"https://huggingface.co/{owner}/Orbit-3"


@pytest.mark.parametrize(
    ("body", "expected_status", "expected_names"),
    [
        (b"gpt-7-alpha\xff-pro", "parse_failed", ["orbit-3"]),
        ("New model: gpt-7-alpha-pro. Café".encode(), "ok", ["gpt-7-alpha-pro", "orbit-3"]),
    ],
)
def test_invalid_utf8_cannot_create_truncated_model_identity(
    body: bytes, expected_status: str, expected_names: list[str],
) -> None:
    source = next(source for source in load_registry().sources if source.id == "openai-models")
    healthy = Source("healthy", "page", PAGE, 0.9, provider="acme", pattern=r"orbit-[a-z0-9-]+")
    registry = Registry("fixture", 30, r"gguf", r"sdk", (source, healthy))

    def fetch(url: str) -> Response:
        if url.endswith("/robots.txt"):
            return Response(404, b"")
        return Response(200, body if url == source.url else b"orbit-3")

    runs = run_all(registry, {source.id: frozenset(), healthy.id: frozenset()}, fetch=fetch, now=NOW)

    assert [run.status for run in runs] == [expected_status, "ok"]
    assert [signal.model_name for signal in discoveries(runs, NOW)] == expected_names
    if expected_status == "parse_failed":
        assert "UnicodeDecodeError" in runs[0].detail


def _watch_created_timestamp(created: object) -> list[SourceRun]:
    router = Source("router", "openrouter", OPENROUTER, 0.8, providers={"acme": "acme"})
    healthy = Source("healthy", "page", PAGE, 0.9, provider="acme", pattern=r"orbit-[a-z0-9-]+")
    registry = Registry("fixture", 30, r"gguf", r"sdk", (router, healthy))

    def fetch(url: str) -> Response:
        if url.endswith("/robots.txt"):
            return Response(404, b"")
        if url == OPENROUTER:
            return Response(200, json.dumps({
                "data": [{"id": "acme/orbit-3", "created": created}],
            }).encode())
        assert url == PAGE
        return Response(200, b"orbit-4")

    return run_all(
        registry, {router.id: frozenset(), healthy.id: frozenset()}, fetch=fetch, now=NOW,
    )


@pytest.mark.parametrize(
    "created",
    [1e100, -1e100, float("nan"), float("inf"), float("-inf"), 10**100,
     True, "not-a-timestamp", {}, []],
    ids=["overflow", "negative-overflow", "nan", "infinity", "negative-infinity",
         "large-integer", "boolean", "string", "object", "array"],
)
def test_out_of_range_created_is_one_source_outage(created: object) -> None:
    runs = _watch_created_timestamp(created)

    assert [run.status for run in runs] == ["parse_failed", "ok"]
    assert runs[0].detail
    assert [signal.model_name for signal in discoveries(runs, NOW)] == ["orbit-4"]


@pytest.mark.parametrize("error", [OverflowError, OSError, ValueError])
def test_timestamp_platform_failure_is_one_source_outage(monkeypatch, error) -> None:
    class PlatformDatetime(datetime):
        @classmethod
        def fromtimestamp(cls, value, tz=None):
            raise error("fixture platform conversion failure")

    monkeypatch.setattr(watch, "datetime", PlatformDatetime)

    runs = _watch_created_timestamp(1790712000)

    assert [run.status for run in runs] == ["parse_failed", "ok"]
    assert runs[0].detail
    assert [signal.model_name for signal in discoveries(runs, NOW)] == ["orbit-4"]


@pytest.mark.parametrize(
    ("created", "expected_created", "expected_names"),
    [
        (1790712000, datetime(2026, 9, 29, 20, tzinfo=UTC), ["orbit-3", "orbit-4"]),
        (1790712000.5, datetime(2026, 9, 29, 20, 0, 0, 500000, tzinfo=UTC), ["orbit-3", "orbit-4"]),
        (0, None, ["orbit-4"]),
        (None, None, ["orbit-3", "orbit-4"]),
    ],
)
def test_valid_created_timestamp_preserves_recency(created, expected_created, expected_names) -> None:
    runs = _watch_created_timestamp(created)

    assert [run.status for run in runs] == ["ok", "ok"]
    assert runs[0].listed == 1
    assert [signal.model_name for signal in discoveries(runs, NOW)] == expected_names
    if created != 0:
        assert len(runs[0].new) == 1
        assert runs[0].new[0].created == expected_created


def test_a_release_on_the_replayed_sources_becomes_one_discovery_per_model(world) -> None:
    registry, baseline, catalogue = world

    quiet = run_all(registry, baseline, fetch=replay("before"), now=NOW,
                    catalogued=catalogue.catalogued)
    runs = run_all(registry, baseline, fetch=replay("after"), now=NOW,
                   catalogued=catalogue.catalogued)
    signals = discoveries(runs, NOW)

    assert discoveries(quiet, NOW) == []
    assert [run.status for run in runs] == ["ok", "ok", "ok"]
    # The page, Hugging Face and OpenRouter all list Acme Two 2: one signal, from
    # the lab's own page. The GGUF repackaging, the `:free` and `~latest`
    # aliases, a two-year-old repo that slid into the feed window, an unmapped
    # lab, and Acme One 1 (already a card) file nothing.
    assert [signal.to_dict() for signal in signals] == [
        {
            "model_name": "acme-two-2",
            "provider": "acme",
            "first_seen_url": PAGE,
            "timestamp": "2026-09-29T20:00:00Z",
            "confidence": 0.9,
            "signal_id": "watch:acme:acme-two-2",
        },
        {
            "model_name": "Acme-Vision-3",
            "provider": "Acme",
            "first_seen_url": "https://huggingface.co/acme-lab/Acme-Vision-3",
            "timestamp": "2026-09-29T20:00:00Z",
            "confidence": 0.7,
            "signal_id": "watch:acme:acme-vision-3",
        },
    ]
    validator = Draft202012Validator(DISCOVERY_SCHEMA, format_checker=FormatChecker())
    for signal in signals:
        assert list(validator.iter_errors(signal.to_dict())) == []


def test_a_replayed_discovery_runs_through_the_unchanged_signal_queue(world) -> None:
    registry, baseline, catalogue = world
    service = _service()
    runs = run_all(registry, baseline, fetch=replay("after"), now=NOW,
                   catalogued=catalogue.catalogued)
    first = discoveries(runs, NOW)[0]
    raw = json.dumps(first.to_dict()).encode()

    async def scenario():
        kv = KV()
        filed = await service.discovered(
            raw=raw, authorization="Bearer read", read_key="read", kv=kv, now=NOW)
        pending = await service.pending(
            authorization="Bearer read", read_key="read", kv=kv, today=NOW.date())
        items = processor.work_items(pending.body)
        acknowledged = await service.acknowledge(
            authorization="Bearer read", read_key="read", kv=kv,
            payload={"signal_id": first.signal_id, "result": "uncertain", "pr_url": None},
            today=NOW.date())
        # The next watcher run posts the same discovery again, and so does every
        # run after it until the model is catalogued. Each is a no-op.
        again = await service.discovered(
            raw=raw, authorization="Bearer read", read_key="read", kv=kv, now=NOW)
        due = await service.pending(
            authorization="Bearer read", read_key="read", kv=kv, today=date(2026, 9, 30))
        return filed, pending, items, acknowledged, again, due

    filed, pending, items, acknowledged, again, due = asyncio.run(scenario())

    assert (filed.status, filed.body["status"]) == (202, "accepted")
    assert pending.body["schema_version"] == "2"
    assert pending.body["signals"] == [first.to_dict()]
    assert items == [{"signal_id": "watch:acme:acme-two-2", "recheck_day": 0, "pr_url": None}]
    assert acknowledged.body["recheck_days"] == [1, 7, 30]
    assert (again.status, again.body["status"]) == (200, "duplicate")
    assert due.body["signals"] == []
    assert [(row["day"], row["signal_id"]) for row in due.body["rechecks"]] == [
        (1, "watch:acme:acme-two-2")
    ]
    assert processor.work_items(due.body)[0]["recheck_day"] == 1


def test_the_processing_script_takes_a_discovery_as_it_takes_a_grok_signal(
    world, tmp_path: Path,
) -> None:
    registry, baseline, catalogue = world
    runs = run_all(registry, baseline, fetch=replay("after"), now=NOW,
                   catalogued=catalogue.catalogued)
    first = discoveries(runs, NOW)[0]
    pending = tmp_path / "pending.json"
    pending.write_text(json.dumps({"signals": [first.to_dict()], "rechecks": []}))
    empty = tmp_path / "empty-catalogue"
    (empty / "models").mkdir(parents=True)

    result = processor.process(
        pending, tmp_path / "result.json", root=empty, signal_id=first.signal_id,
    )

    # No catalogue lab is named `acme` here, so identity review gets it, the
    # same outcome a Grok Bot signal for an unknown lab gets.
    assert (result["status"], result["signal_id"]) == ("uncertain", "watch:acme:acme-two-2")


def test_the_schedule_keeps_a_listed_model_inside_24_hours() -> None:
    workflow = yaml.safe_load(
        (ROOT / ".github" / "workflows" / "release-watch.yml").read_text(encoding="utf-8")
    )
    (schedule,) = workflow[True]["schedule"]
    minute, hours, *rest = schedule["cron"].split()
    assert rest == ["*", "*", "*"] and minute.isdigit()
    step = int(re.fullmatch(r"\*/(\d+)", hours).group(1))
    # A model filed on the next run reaches the queue within one interval, and
    # the hourly release-signals run picks it up within the hour after that.
    assert step + 1 <= 24


def test_a_source_outage_is_reported_and_the_rest_still_file(world) -> None:
    registry, baseline, catalogue = world
    runs = run_all(registry, baseline, fetch=replay("after", down=frozenset({PAGE})),
                   now=NOW, catalogued=catalogue.catalogued)
    signals = discoveries(runs, NOW)
    result = release_watch.report(runs, signals, None, NOW)

    assert [(run.source.id, run.status) for run in runs] == [
        ("acme-models", "unreachable"), ("hf-acme", "ok"), ("openrouter", "ok"),
    ]
    # With the page down, Hugging Face files Acme Two 2 instead.
    assert [signal.first_seen_url for signal in signals] == [
        "https://huggingface.co/acme-lab/Acme-Two-2",
        "https://huggingface.co/acme-lab/Acme-Vision-3",
    ]
    assert release_watch.failures(result) == [
        f"- `acme-models` unreachable: ConnectError: cannot reach {PAGE} ({PAGE})"
    ]
    assert "### Outages" in release_watch.summary(result)


def test_a_page_that_stops_yielding_ids_is_an_outage_not_a_quiet_day(world) -> None:
    registry, baseline, catalogue = world

    def blank(url: str) -> Response:
        if url == PAGE:
            return Response(200, b"<html><body>Loading...</body></html>")
        return replay("after")(url)

    runs = run_all(registry, baseline, fetch=blank, now=NOW, catalogued=catalogue.catalogued)
    assert (runs[0].status, runs[0].detail) == (
        "parse_failed", "0 model IDs, below the floor of 1",
    )


@pytest.mark.parametrize(("robots", "status"), [
    (503, "robots_disallowed"), (403, "ok"), (401, "ok"), (404, "ok"),
])
def test_robots_rules_are_read_before_every_source(world, robots: int, status: str) -> None:
    registry, baseline, catalogue = world
    runs = run_all(registry, baseline, fetch=replay("after", robots=robots), now=NOW,
                   catalogued=catalogue.catalogued)
    assert {run.status for run in runs} == {status}


def test_robots_disallow_rule_stops_the_fetch(world) -> None:
    registry, baseline, catalogue = world
    fetched: list[str] = []

    def fetch(url: str) -> Response:
        fetched.append(url)
        if url.endswith("/robots.txt"):
            return Response(200, b"User-agent: *\nDisallow: /models\n")
        return replay("after")(url)

    runs = run_all(registry, baseline, fetch=fetch, now=NOW, catalogued=catalogue.catalogued)
    assert runs[0].status == "robots_disallowed"
    assert PAGE not in fetched


def test_a_burst_of_new_ids_is_held_for_a_person(world) -> None:
    registry, baseline, catalogue = world
    many = "".join(f"<td>acme-new-{n}</td>" for n in range(11)).encode()

    def burst(url: str) -> Response:
        return Response(200, many) if url == PAGE else replay("after")(url)

    runs = run_all(registry, baseline, fetch=burst, now=NOW, catalogued=catalogue.catalogued)
    assert runs[0].status == "burst"
    assert all(signal.first_seen_url != PAGE for signal in discoveries(runs, NOW))


def test_a_refused_post_is_an_alert() -> None:
    signal = ReleaseSignal.parse({
        "model_name": "acme-two-2", "provider": "acme", "first_seen_url": PAGE,
        "timestamp": "2026-09-29T20:00:00Z", "confidence": 0.9,
        "signal_id": "watch:acme:acme-two-2",
    }, discovered=True)
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(404, json={"error": {"code": "not_found"}})

    posted = release_watch.post_discoveries(
        [signal], origin="https://api.example", read_key="read",
        client=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    result = {"sources": [], "posted": posted}

    assert seen[0].url == "https://api.example/v1/signals/discovered"
    assert seen[0].headers["authorization"] == "Bearer read"
    assert posted[0]["ok"] is False
    assert release_watch.failures(result)[0].startswith(
        "- filing refused `watch:acme:acme-two-2`: HTTP 404"
    )


def test_with_the_queue_off_each_discovery_is_one_issue_ever() -> None:
    discoveries_ = [
        ReleaseSignal.parse(_discovery(), discovered=True),
        ReleaseSignal.parse(_discovery(
            model_name="Acme-Vision-3", signal_id="watch:acme:acme-vision-3",
            first_seen_url="https://huggingface.co/acme-lab/Acme-Vision-3",
        ), discovered=True),
    ]
    created: list[dict] = []

    def handler(request: httpx.Request) -> httpx.Response:
        if request.method == "GET":
            assert request.url.params["state"] == "all"
            assert request.url.params["labels"] == "release-discovery"
            # Closed long ago, still never filed again.
            return httpx.Response(200, json=[{
                "title": "release discovery: acme-two-2 (acme) `watch:acme:acme-two-2`",
                "state": "closed",
            }])
        created.append(json.loads(request.content))
        return httpx.Response(201, json={"number": 7})

    outcomes = release_watch.file_issues(
        discoveries_, repository="owner/repo", token="t",
        client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    assert [(row["signal_id"], row["ok"], row["filed"]) for row in outcomes] == [
        ("watch:acme:acme-two-2", True, False),
        ("watch:acme:acme-vision-3", True, True),
    ]
    assert created[0]["labels"] == ["release-discovery", "new-model"]
    assert created[0]["title"].endswith("`watch:acme:acme-vision-3`")
    assert "trigger, not evidence" in created[0]["body"]


def test_a_failed_issue_listing_is_an_alert_not_a_flood() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET", "nothing may be created without the dedup set"
        return httpx.Response(502)

    outcomes = release_watch.file_issues(
        [ReleaseSignal.parse(_discovery(), discovered=True)], repository="owner/repo",
        token="t", client=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    assert release_watch.failures({"sources": [], "posted": outcomes})[0].startswith(
        "- filing refused `watch:acme:acme-two-2`: HTTP 0 listing release-discovery issues"
    )


def test_one_model_on_several_sources_shares_one_signal_id() -> None:
    assert signal_id("anthropic", "claude-opus-5.5") == signal_id("anthropic", "claude-opus-5-5")
    assert signal_id("Alibaba / Qwen Team", "Qwen3.5-72B") == "watch:alibaba-qwen-team:qwen3-5-72b"
    long = signal_id("acme", "x" * 200)
    assert len(long) == 128 and long.startswith("watch:acme:")


def test_page_extraction_unwraps_serialised_ids_and_keeps_prose() -> None:
    """A flight key `.$<id>.<digits>:` keeps the id. Other `$` matches are dropped."""
    registry = load_registry()
    anthropic = next(item for item in registry.sources if item.id == "anthropic-models")
    openai = next(item for item in registry.sources if item.id == "openai-models")
    deepseek = next(item for item in registry.sources if item.id == "deepseek-models")
    page = (
        '["$","section",".$claude-opus-4-20250514.1:$section"]\n'
        "Listed: claude-opus-4-20250514, claude-opus-5.5, claude-opus-5.1, "
        "claude-sonnet-4-5.1, and claude-sonnet-5.5.\n"
    )
    found = extract(anthropic, page.encode(), registry)
    assert set(found) == {
        "claude-opus-4-20250514",
        "claude-opus-5.5",
        "claude-opus-5.1",
        "claude-sonnet-4-5.1",
        "claude-sonnet-5.5",
    }
    assert signal_id(anthropic.provider, "claude-opus-5.5") == signal_id(
        anthropic.provider, "claude-opus-5-5",
    )

    # The key is the only copy. A dotted id keeps its own dots and loses the index.
    assert set(extract(anthropic, b".$claude-opus-5.5.1:", registry)) == {"claude-opus-5.5"}
    assert set(extract(anthropic, b".$claude-opus-4-20250514.1:$x", registry)) == {
        "claude-opus-4-20250514",
    }

    # A `$` prefix that is not `.$<id>.<digits>:` cannot be split from a version.
    assert extract(anthropic, b'".0:$claude-opus-4-8.1"', registry) == {}

    # `.$` without that index is still serialisation. A bare id stays.
    prefix_only = ".$claude-opus-5.5 is serialised. claude-haiku-4-5 is listed."
    assert set(extract(anthropic, prefix_only.encode(), registry)) == {"claude-haiku-4-5"}

    # Text with no preceding `$` is kept, including a price glued on with `:$`.
    assert set(extract(anthropic, b"notes claude-opus-4-20250514.1:$section", registry)) == {
        "claude-opus-4-20250514.1",
    }
    assert set(extract(openai, b"gpt-6.1:$2.50", registry)) == {"gpt-6.1"}
    assert set(extract(openai, b"gpt-7.1 is listed", registry)) == {"gpt-7.1"}
    assert set(extract(deepseek, b"deepseek-v5.2:$1", registry)) == {"deepseek-v5.2"}


# ── the two contracts stay apart ─────────────────────────────────────────────

def _discovery(**changes: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "model_name": "acme-two-2", "provider": "acme", "first_seen_url": PAGE,
        "timestamp": "2026-09-29T20:00:00Z", "confidence": 0.9,
        "signal_id": "watch:acme:acme-two-2",
    }
    payload.update(changes)
    return payload


@pytest.mark.parametrize("changes", [
    {"first_seen_url": "https://x.com/acme/status/1"},
    {"first_seen_url": "https://t.co/abc"},
    {"first_seen_url": f"https://{REMOVED_HOSTS[0]}/models/acme-two-2"},
    {"first_seen_url": "http://docs.acme.example/models"},
    {"signal_id": "grok-20260929-1"},
])
def test_a_discovery_outside_its_contract_is_refused_by_parser_and_schema(
    changes: dict[str, object],
) -> None:
    validator = Draft202012Validator(DISCOVERY_SCHEMA, format_checker=FormatChecker())
    with pytest.raises(SignalError):
        ReleaseSignal.parse(_discovery(**changes), discovered=True)
    if REMOVED_HOSTS[0] not in str(changes):
        assert list(validator.iter_errors(_discovery(**changes)))


def test_grok_bot_cannot_use_the_watcher_prefix() -> None:
    grok = {
        "model_name": "Grok 5 Mini", "provider": "xAI",
        "first_seen_url": "https://x.com/xai/status/1", "timestamp": "2026-09-26T13:14:15Z",
        "confidence": 0.97, "signal_id": "watch:xai:grok-5-mini",
    }
    validator = Draft202012Validator(SIGNAL_SCHEMA, format_checker=FormatChecker())
    with pytest.raises(SignalError, match="reserved"):
        ReleaseSignal.parse(grok)
    assert list(validator.iter_errors(grok))
    # A queued row is parsed under the contract its ID names.
    assert ReleaseSignal.from_queue(_discovery()).first_seen_url == PAGE
    assert ReleaseSignal.from_queue({**grok, "signal_id": "grok-1"}).signal_id == "grok-1"


def test_the_discovered_endpoint_needs_the_read_key_and_a_fresh_discovery() -> None:
    service = _service()

    async def post(payload: dict, authorization: str = "Bearer read"):
        return await service.discovered(
            raw=json.dumps(payload).encode(), authorization=authorization,
            read_key="read", kv=KV(), now=NOW,
        )

    wrong_key = asyncio.run(post(_discovery(), "Bearer nope"))
    x_url = asyncio.run(post(_discovery(first_seen_url="https://x.com/a/status/1")))
    stale = asyncio.run(post(_discovery(timestamp="2026-09-27T20:00:00Z")))

    assert wrong_key.status == 401
    assert (x_url.status, x_url.body["error"]["code"]) == (400, "invalid_signal")
    assert (stale.status, stale.body["error"]["code"]) == (400, "stale_signal")


# ── the committed registry ───────────────────────────────────────────────────

def test_the_registry_has_a_baseline_and_a_catalogue_lab_for_every_source() -> None:
    registry = load_registry()
    baseline = load_baseline()
    catalogue = load_catalogue()

    assert {source.id for source in registry.sources} == set(baseline)
    for source in registry.sources:
        assert baseline[source.id], source.id
        for provider in {source.provider} if source.provider else set(source.providers.values()):
            assert catalogue.lab(provider), f"{source.id}: {provider!r} is not one catalogue lab"
    kinds = {source.kind for source in registry.sources}
    assert kinds == {"page", "huggingface", "openrouter"}

    # Every carded lab is watched from at least one primary source (MODEL-215's
    # coverage audit). A new lab directory without a source fails here.
    # `cerebras` holds other labs' models as Cerebras serves them.
    watched = {
        lab
        for source in registry.sources
        for provider in ({source.provider} if source.provider else set(source.providers.values()))
        for lab in catalogue.labs[_normalise(provider)]
    }
    carded = {path.name for path in (ROOT / "models").iterdir() if path.is_dir()}
    assert carded - watched == {"cerebras"}


def test_the_workflow_alerts_on_outage_and_holds_no_pr_credential() -> None:
    text = (ROOT / ".github" / "workflows" / "release-watch.yml").read_text(encoding="utf-8")
    workflow = yaml.safe_load(text)
    job = workflow["jobs"]["watch"]

    # It runs whether or not the queue is on; the switch picks the sink.
    assert "if" not in job
    assert 'sink=--post' in text and 'sink=--issues' in text
    assert 'python scripts/release_watch.py "$sink"' in text
    assert job["timeout-minutes"] <= 10
    # Source watching holds only the signal read key; dispatch is a separate job.
    assert set(re.findall(r"secrets\.(\w+)", json.dumps(job))) == {"MODELSPEC_SIGNALS_READ_KEY"}
    dispatch = workflow["jobs"]["dispatch"]
    assert set(re.findall(r"secrets\.(\w+)", json.dumps(dispatch))) == {"MODELSPEC_DATA_DISPATCH_TOKEN"}
    assert "--repo turbobeest/modelspec-data" in json.dumps(dispatch)
    assert not any("gh issue create --label release-watch" in step.get("run", "") for step in job["steps"])
    assert 'select(.filed == true)' in text
    assert "DATA_SPLIT_ENABLED" in dispatch["if"]


def test_public_source_detection_retains_observations_before_catalogue_filtering(world):
    registry, baseline, _ = world
    runs = run_all(registry, baseline, fetch=replay("after"), now=NOW)
    assert discoveries(runs, NOW)
    source = registry.sources[0]
    from dataclasses import replace
    limited = replace(registry, sources=(replace(source, max_new=0),))
    runs = run_all(limited, baseline, fetch=replay("after"), now=NOW)
    assert runs[0].status == "ok"
    # Card filtering happens after detection, so rejected observations stay in
    # reports and the source's max_new does not turn duplicates into an outage.
    from scripts.release_watch_filter import filter_releases
    detected = run_all(registry, {source.id: frozenset() for source in registry.sources},
                       fetch=replay("after"), now=NOW)
    filtered = filter_releases(detected, NOW, catalogue=world[2])
    assert any(row["model_name"] == "acme-one-1" for row in filtered["observations"])
    assert any(row["model_name"] == "acme-one-1" and "already carded" in row["reason"]
               for row in filtered["rejected"])


# ── MODEL-421: an outage fails the run ─────────────────────────────────────


def _outage_fetch(url: str) -> Response:
    """The lab page is down, OpenRouter answers 503, Hugging Face is fine."""
    if url.endswith("/robots.txt"):
        return Response(404, b"")
    if url == PAGE:
        raise httpx.ConnectError(f"cannot reach {url}")
    if url == OPENROUTER:
        return Response(503, b"")
    return Response(200, (FIXTURES / "after" / FILES[url]).read_bytes())


def _watch_files(tmp_path: Path, world) -> tuple[Path, Path]:
    from release_signals.watch import write_baseline

    _registry_, baseline, _catalogue_ = world
    path = tmp_path / "baseline.json"
    write_baseline(path, baseline, NOW)
    return tmp_path / "release-watch.yaml", path


def test_a_source_outage_makes_the_watcher_exit_non_zero(world, tmp_path, monkeypatch) -> None:
    registry_path, baseline_path = _watch_files(tmp_path, world)
    monkeypatch.setattr(release_watch, "http_fetch", lambda user_agent: _outage_fetch)
    report_path = tmp_path / "watch.json"

    status = release_watch.main(["--registry", str(registry_path), "--baseline",
                                 str(baseline_path), "--report", str(report_path)])

    assert status == 1
    sources = {row["id"]: (row["status"], row["detail"])
               for row in json.loads(report_path.read_text())["sources"]}
    assert sources == {
        "acme-models": ("unreachable", f"ConnectError: cannot reach {PAGE}"),
        "hf-acme": ("ok", ""),
        "openrouter": ("unreachable", "HTTP 503"),
    }


def test_every_source_answering_exits_zero(world, tmp_path, monkeypatch) -> None:
    registry_path, baseline_path = _watch_files(tmp_path, world)
    monkeypatch.setattr(release_watch, "http_fetch", lambda user_agent: replay("after"))
    assert release_watch.main(["--registry", str(registry_path),
                               "--baseline", str(baseline_path)]) == 0


def test_run_report_counts_filed_ids_whose_created_is_missing() -> None:
    router = Source("router", "openrouter", OPENROUTER, 0.8, providers={"acme": "acme"})
    page = Source("page", "page", PAGE, 0.9, provider="acme", pattern=r"orbit-[a-z0-9-]+")
    registry = Registry("fixture", 30, r"gguf", r"sdk", (router, page))
    recent = 1790712000

    def fetch(url: str) -> Response:
        if url.endswith("/robots.txt"):
            return Response(404, b"")
        if url == OPENROUTER:
            return Response(200, json.dumps({"data": [
                {"id": "acme/orbit-old", "created": 0},
                {"id": "acme/orbit-new", "created": recent},
                {"id": "acme/orbit-blank"},
            ]}).encode())
        return Response(200, b"orbit-4")

    runs = run_all(
        registry, {router.id: frozenset(), page.id: frozenset()}, fetch=fetch, now=NOW,
    )
    filed = [signal.model_name for signal in discoveries(runs, NOW)]
    assert "orbit-old" not in filed
    assert "orbit-blank" in filed
    assert "orbit-4" in filed
    result = release_watch.report(runs, discoveries(runs, NOW), None, NOW)
    assert [row["missing_created"] for row in result["sources"]] == [1, 1]
    text = release_watch.summary(result)
    assert "`router` 1" in text
    assert "`page` 1" not in text

    hub = Source(
        "hub", "huggingface", "https://huggingface.co/api/models?author=acme",
        0.7, provider="acme",
    )
    hub_run = SourceRun(hub, "ok", "", 1, (
        Seen("acme/orbit-hub", "orbit-hub", "acme", hub.url),
    ))
    mixed = release_watch.report(
        [runs[0], hub_run, runs[1]], discoveries(runs, NOW), None, NOW,
    )
    assert [row["missing_created"] for row in mixed["sources"]] == [1, 1, 1]
    mixed_text = release_watch.summary(mixed)
    assert "`router` 1" in mixed_text and "`hub` 1" in mixed_text
    assert "`page` 1" not in mixed_text
    page_only = release_watch.report([runs[1]], discoveries(runs, NOW), None, NOW)
    assert page_only["sources"][0]["missing_created"] == 1
    assert "Filed with no created time" not in release_watch.summary(page_only)

    # A carded id is rejected rather than filed, so its missing created time is not counted.
    from release_signals.watch import Catalogue
    carded = Catalogue(labs={}, aliases={"acme": frozenset({"orbit-4"})})
    filtered = filter_releases(runs, NOW, catalogue=carded)
    filed_report = release_watch.report(
        runs, filtered["signals"], None, NOW, filtered=filtered,
    )
    assert [row["missing_created"] for row in filed_report["sources"]] == [1, 0]

    burst = SourceRun(router, "burst", "2 new IDs at once, above 1", 2, runs[0].new)
    held = release_watch.report([burst], [], None, NOW)
    assert held["sources"][0]["missing_created"] == 0
    assert "Filed with no created time" not in release_watch.summary(held)


SHIM = '''
import sys
import httpx
from release_signals.watch import Response
from scripts import release_watch

PAGE, OPENROUTER = {page!r}, {openrouter!r}
OK = {ok!r}

def fetch(url):
    if url.endswith("/robots.txt"):
        return Response(404, b"")
    if url == PAGE and not OK:
        raise httpx.ConnectError("cannot reach " + url)
    if url == OPENROUTER and not OK:
        return Response(503, b"")
    return Response(200, open({fixtures!r} + "/" + {files!r}[url], "rb").read())

release_watch.http_fetch = lambda user_agent: fetch
# The workflow passes the sink; this simulation files nowhere.
args = [a for a in sys.argv[2:] if a not in ("--post", "--issues")]
sys.exit(release_watch.main(args + ["--registry", {registry!r}, "--baseline", {baseline!r}]))
'''


def _run_watch_step(tmp_path: Path, world, *, ok: bool):
    """Run the workflow's real watch step, with `python` running the real
    watcher against a simulated fetch."""
    import os
    import shutil
    import subprocess

    if not shutil.which("jq") or not shutil.which("bash"):
        pytest.skip("the watch step needs bash and jq")
    registry_path, baseline_path = _watch_files(tmp_path, world)
    workflow = yaml.safe_load(
        (ROOT / ".github" / "workflows" / "release-watch.yml").read_text(encoding="utf-8"))
    step = next(s for s in workflow["jobs"]["watch"]["steps"] if s.get("id") == "watch")
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    shim = tmp_path / "shim.py"
    shim.write_text(SHIM.format(
        page=PAGE, openrouter=OPENROUTER, ok=ok, fixtures=str(FIXTURES / "after"),
        files=FILES, registry=str(registry_path), baseline=str(baseline_path)))
    python = bin_dir / "python"
    python.write_text(f'#!/bin/sh\nexec "{sys.executable}" "{shim}" "$@"\n')
    python.chmod(0o755)
    runner_temp = tmp_path / "runner"
    runner_temp.mkdir()
    outputs, step_summary = tmp_path / "outputs", tmp_path / "summary"
    env = {
        **os.environ,
        "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}",
        "PYTHONPATH": str(ROOT),
        "SIGNALS_ENABLED": "true",
        "RUNNER_TEMP": str(runner_temp),
        "GITHUB_OUTPUT": str(outputs),
        "GITHUB_STEP_SUMMARY": str(step_summary),
    }
    # GitHub's default shell for `run:` steps.
    done = subprocess.run(["bash", "--noprofile", "--norc", "-eo", "pipefail", "-c",
                           step["run"]], cwd=ROOT, env=env, capture_output=True, text=True,
                          timeout=120)
    return done, outputs.read_text(), step_summary.read_text()


def test_a_simulated_outage_fails_the_workflow_run(world, tmp_path) -> None:
    done, outputs, step_summary = _run_watch_step(tmp_path, world, ok=False)
    assert done.returncode == 1, done.stderr
    assert "::error::release_watch.py exited 1" in done.stdout
    # The outputs are written before the step fails, so dispatch still sees them.
    assert "status=1" in outputs and "discoveries=0" in outputs
    assert "### Outages" in step_summary
    assert f"`acme-models` unreachable: ConnectError: cannot reach {PAGE}" in step_summary
    assert "`openrouter` unreachable: HTTP 503" in step_summary


def test_a_run_where_every_source_answers_stays_green(world, tmp_path) -> None:
    done, outputs, step_summary = _run_watch_step(tmp_path, world, ok=True)
    assert done.returncode == 0, done.stderr
    assert "status=0" in outputs and "### Outages" not in step_summary


def test_dispatch_still_runs_for_discoveries_when_the_watch_job_fails() -> None:
    workflow = yaml.safe_load(
        (ROOT / ".github" / "workflows" / "release-watch.yml").read_text(encoding="utf-8"))
    condition = workflow["jobs"]["dispatch"]["if"]
    assert condition.startswith("${{ !cancelled() &&")
    assert "needs.watch.outputs.discoveries != ''" in condition


def _hf_registry() -> tuple[Source, Registry]:
    source = Source("hf-acme", "huggingface", HF, 0.7, provider="Acme")
    return source, Registry("fixture", 30, r"gguf", "", (source,))


def test_huggingface_listing_metadata_reaches_the_observation_not_the_filed_signal() -> None:
    source, registry = _hf_registry()
    body = json.dumps([
        {
            "id": "acme-lab/Orbit-9",
            "createdAt": "2026-09-29T00:00:00Z",
            "pipeline_tag": "text-generation",
            "library_name": "transformers",
            "tags": [
                "transformers",
                "text-generation",
                "conversational",
                "base_model:finetune:acme-lab/Orbit-1",
                "license:mit",
                "en",
                "arxiv:1234.5678",
            ],
            "cardData": {"base_model": "acme-lab/Orbit-1"},
        },
        {
            "id": "acme-lab/Orbit-8",
            "createdAt": "2026-09-29T00:00:00Z",
            "pipeline_tag": "text-generation",
            "tags": ["text-generation", "base_model:quantized:other-lab/Base-2"],
        },
    ]).encode()
    listed = extract(source, body, registry)
    orbit9 = listed["acme-lab/Orbit-9"]
    orbit8 = listed["acme-lab/Orbit-8"]
    assert orbit9.pipeline_tag == "text-generation"
    assert orbit9.base_model == "acme-lab/Orbit-1"
    assert orbit9.tags == (
        "transformers",
        "text-generation",
        "conversational",
        "base_model:finetune:acme-lab/Orbit-1",
    )
    assert orbit8.base_model == "other-lab/Base-2"
    assert orbit8.tags == (
        "text-generation",
        "base_model:quantized:other-lab/Base-2",
    )

    result = filter_releases([
        SourceRun(source, "ok", listed=2, new=(orbit9, orbit8)),
    ], NOW)
    by_name = {row["model_name"]: row for row in result["observations"]}
    assert by_name["Orbit-9"]["pipeline_tag"] == "text-generation"
    assert by_name["Orbit-9"]["base_model"] == "acme-lab/Orbit-1"
    assert by_name["Orbit-9"]["tags"] == [
        "transformers", "text-generation", "conversational",
        "base_model:finetune:acme-lab/Orbit-1",
    ]
    assert by_name["Orbit-8"]["base_model"] == "other-lab/Base-2"
    assert "license:mit" not in json.dumps(result["observations"])
    for signal in result["signals"]:
        assert set(signal.to_dict()) == {
            "model_name", "provider", "first_seen_url", "timestamp",
            "confidence", "signal_id",
        }
        with pytest.raises(SignalError, match="unknown"):
            ReleaseSignal.parse(
                {**signal.to_dict(), "pipeline_tag": "text-generation"},
                discovered=True,
            )


def test_replay_restores_huggingface_metadata(tmp_path: Path) -> None:
    from scripts.release_watch_filter import replay_reports

    source, registry = _hf_registry()
    report = tmp_path / "watch.json"
    report.write_text(json.dumps({
        "observed_at": "2026-09-29T20:00:00Z",
        "observations": [{
            "source_id": source.id,
            "source_key": "acme-lab/Orbit-9",
            "model_name": "Orbit-9",
            "provider": "Acme",
            "url": "https://huggingface.co/acme-lab/Orbit-9",
            "created": "2026-09-29T00:00:00+00:00",
            "confidence": 0.7,
            "pipeline_tag": "text-generation",
            "tags": ["transformers", "base_model:finetune:acme-lab/Orbit-1"],
            "base_model": "acme-lab/Orbit-1",
        }],
    }), encoding="utf-8")
    runs, _stamp = replay_reports([report], registry)
    seen = runs[0].new[0]
    assert seen.pipeline_tag == "text-generation"
    assert seen.tags == ("transformers", "base_model:finetune:acme-lab/Orbit-1")
    assert seen.base_model == "acme-lab/Orbit-1"


def _api_row(repo: str, **fields: object) -> dict:
    row = {"id": repo, "createdAt": "2026-09-29T00:00:00Z", "private": False}
    row.update(fields)
    return row


def test_fixture_api_rows_cover_tag_classes_fallback_unknown_and_derivatives() -> None:
    source, registry = _hf_registry()
    rows = []
    expect: dict[str, str | None] = {}
    for index, tag in enumerate(sorted(IN_SCOPE_PIPELINE_TAGS)):
        repo = f"acme-lab/in-{index}"
        rows.append(_api_row(
            repo, pipeline_tag=tag, library_name="transformers",
            tags=[tag, "license:mit", "en"],
        ))
        expect[repo] = None
    for index, tag in enumerate(sorted(OUT_OF_SCOPE_PIPELINE_TAGS)):
        repo = f"acme-lab/out-{index}"
        rows.append(_api_row(repo, pipeline_tag=tag, tags=[tag, "arxiv:1.2"]))
        expect[repo] = tag
    rows.append(_api_row(
        "acme-lab/audio-extra", pipeline_tag="audio-text-to-text",
        tags=["audio-text-to-text"],
    ))
    expect["acme-lab/audio-extra"] = "audio-text-to-text"
    rows.append(_api_row(
        "acme-lab/acme-robotics-arm", pipeline_tag="graph-ml",
        tags=["graph-ml", "robotics"],
    ))
    expect["acme-lab/acme-robotics-arm"] = None
    rows.append(_api_row("acme-lab/acme-embodied-walker", tags=["en", "lora"]))
    expect["acme-lab/acme-embodied-walker"] = "robotics or embodied checkpoint"
    rows.append(_api_row("acme-lab/orbit-plain"))
    expect["acme-lab/orbit-plain"] = None
    rows.append(_api_row(
        "acme-lab/orbit-rl", tags=["table-tennis", "reinforcement-learning"],
    ))
    expect["acme-lab/orbit-rl"] = "reinforcement-learning"
    rows.append(_api_row(
        "acme-lab/tuned-tag", pipeline_tag="text-generation",
        tags=["text-generation", "base_model:finetune:other-lab/Orbit-1"],
    ))
    expect["acme-lab/tuned-tag"] = None
    rows.append(_api_row(
        "acme-lab/tuned-card", pipeline_tag="text-generation",
        tags=["text-generation"],
        cardData={"base_model": "other-lab/Orbit-2"},
    ))
    expect["acme-lab/tuned-card"] = None
    rows.append(_api_row(
        "acme-lab/orbit-1-sparse", pipeline_tag="text-generation",
        tags=["text-generation", "base_model:finetune:other-lab/Orbit-1"],
    ))
    expect["acme-lab/orbit-1-sparse"] = "derivative of other-lab/Orbit-1"
    rows.append(_api_row(
        "acme-lab/siglip-vl", pipeline_tag="image-text-to-text",
        tags=[
            "image-text-to-text",
            "base_model:finetune:acme-lab/flagship",
            "base_model:other-lab/siglip",
        ],
        cardData={"base_model": ["acme-lab/flagship", "other-lab/siglip"]},
    ))
    expect["acme-lab/siglip-vl"] = None
    rows.append(_api_row(
        "acme-lab/own-tune", pipeline_tag="text-generation",
        tags=["text-generation", "base_model:acme-lab/Orbit-1"],
        cardData={"base_model": "acme-lab/Orbit-1"},
    ))
    expect["acme-lab/own-tune"] = None
    rows.append(_api_row(
        "acme-lab/fresh", pipeline_tag="text-generation", tags=["text-generation"],
    ))
    expect["acme-lab/fresh"] = None

    listed = extract(source, json.dumps(rows).encode(), registry)
    result = filter_releases([
        SourceRun(source, "ok", listed=len(listed), new=tuple(listed.values())),
    ], NOW)
    filed = {signal.model_name for signal in result["signals"]}
    reasons = {row["source_key"]: row["reason"] for row in result["rejected"]}
    for repo, reason in expect.items():
        name = repo.split("/", 1)[1]
        if reason is None:
            assert name in filed, repo
            assert repo not in reasons
        else:
            assert reasons[repo] == reason, repo
            assert name not in filed
    for signal in result["signals"]:
        assert "pipeline_tag" not in signal.to_dict()
    by_key = {row["source_key"]: row for row in result["observations"]}
    assert by_key["acme-lab/in-0"]["tags"][0] == "transformers"
    assert "license:mit" not in by_key["acme-lab/in-0"]["tags"]
    assert by_key["acme-lab/tuned-tag"]["base_model"] == "other-lab/Orbit-1"
    assert by_key["acme-lab/tuned-card"]["base_model"] == "other-lab/Orbit-2"
    assert by_key["acme-lab/orbit-1-sparse"]["base_model"] == "other-lab/Orbit-1"
    assert by_key["acme-lab/siglip-vl"]["base_model"] == "other-lab/siglip"
    assert by_key["acme-lab/siglip-vl"]["base_models"] == [
        "acme-lab/flagship", "other-lab/siglip",
    ]
    assert by_key["acme-lab/own-tune"]["base_model"] == "acme-lab/Orbit-1"
    assert "base_model" not in by_key["acme-lab/fresh"]
    assert "pipeline_tag" not in by_key["acme-lab/orbit-plain"]
    assert by_key["acme-lab/acme-robotics-arm"]["pipeline_tag"] == "graph-ml"
