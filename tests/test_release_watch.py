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
from release_signals.contract import ReleaseSignal, SignalError
from release_signals.watch import (
    Response,
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
    # The read key it already holds is the only secret: no PR token, no
    # Firecrawl key, nothing Jamie has to create for it.
    assert set(re.findall(r"secrets\.(\w+)", text)) == {"MODELSPEC_SIGNALS_READ_KEY"}
    alert = next(step for step in job["steps"] if step.get("name") == "Raise the outage alert")
    # A crash before the report, or any failed step, still alerts.
    assert alert["if"] == "${{ !cancelled() && (failure() || steps.watch.outputs.status != '0') }}"
    assert "before writing a report" in text
    assert "gh issue create --label release-watch" in alert["run"]
    assert alert["run"].rstrip().endswith("exit 1")
