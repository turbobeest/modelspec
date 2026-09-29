"""A release signal becomes a reviewable card change (MODEL-113)."""

from __future__ import annotations

import hashlib
import hmac
import importlib.util
import json
import sys
from datetime import UTC, date, datetime
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator, FormatChecker

from decision.excluded import REMOVED_HOSTS
from release_signals.contract import ReleaseSignal, SignalError, sign
from release_signals.pipeline import (
    ChangePolicy,
    FetchResult,
    FirecrawlBudget,
    draft_signal,
    require_allowed_source,
    resolve_signal,
    update_existing_card,
)
from scripts import process_release_signals as processor

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = Path(__file__).parent / "fixtures" / "release_signals"


def signal(**changes: object) -> dict[str, object]:
    row: dict[str, object] = {
        "model_name": "Orbit 2",
        "provider": "Acme",
        "first_seen_url": "https://x.com/acme/status/123456789",
        "timestamp": "2026-09-26T13:14:15Z",
        "confidence": 0.97,
        "signal_id": "grok-20260926-123456789",
    }
    row.update(changes)
    return row


@pytest.mark.parametrize(
    "valid",
    [
        signal(),
        signal(timestamp="2026-09-26T13:14:15.123+05:30"),
        signal(timestamp="2026-09-26t13:14:15z"),
    ],
)
def test_v1_schema_accepts_the_documented_contract(valid: dict[str, object]) -> None:
    schema = json.loads(
        (ROOT / "schemas" / "release-signal-v1.schema.json").read_text(encoding="utf-8")
    )
    validator = Draft202012Validator(schema, format_checker=FormatChecker())

    validator.validate(valid)

    assert schema["$id"].endswith("release-signal-v1.schema.json")
    assert schema["required"] == [
        "model_name",
        "provider",
        "first_seen_url",
        "timestamp",
        "confidence",
        "signal_id",
    ]


@pytest.mark.parametrize(
    "invalid",
    [
        signal(confidence=1.01),
        signal(timestamp="2026-09-26"),
        signal(timestamp="2026-09-26 13:14:15Z"),
        signal(timestamp=" 2026-09-26T13:14:15Z"),
        signal(first_seen_url="https://example.com/announcement"),
        signal(extra="not in v1"),
    ],
)
def test_v1_schema_rejects_instances_outside_the_contract(
    invalid: dict[str, object],
) -> None:
    schema = json.loads(
        (ROOT / "schemas" / "release-signal-v1.schema.json").read_text(encoding="utf-8")
    )
    validator = Draft202012Validator(schema, format_checker=FormatChecker())

    assert not validator.is_valid(invalid)


def test_parser_accepts_rfc3339_and_rejects_instances_outside_the_contract() -> None:
    parsed = ReleaseSignal.parse(signal())
    offset = ReleaseSignal.parse(signal(timestamp="2026-09-26T13:14:15.123+05:30"))
    lowercase = ReleaseSignal.parse(signal(timestamp="2026-09-26t13:14:15z"))

    assert parsed.model_name == "Orbit 2"
    assert offset.instant == datetime(2026, 9, 26, 7, 44, 15, 123000, tzinfo=UTC)
    assert lowercase.instant == datetime(2026, 9, 26, 13, 14, 15, tzinfo=UTC)
    for bad in (
        signal(confidence=1.01),
        signal(timestamp="2026-09-26"),
        signal(timestamp="2026-09-26 13:14:15Z"),
        signal(timestamp=" 2026-09-26T13:14:15Z"),
        signal(first_seen_url="https://example.com/announcement"),
        signal(extra="not in v1"),
    ):
        with pytest.raises(SignalError):
            ReleaseSignal.parse(bad)


@pytest.mark.parametrize(
    ("payload", "accepted"),
    [
        (signal(first_seen_url="https://x.com/acme/status/123"), True),
        (signal(first_seen_url="https://x.com"), False),
        (signal(first_seen_url="https://x.com:443/acme/status/123"), False),
        (signal(model_name="   "), False),
        (signal(provider="   "), False),
        (signal(model_name="m" * 300), True),
        (signal(model_name="m" * 301), False),
        (signal(provider="p" * 300), True),
        (signal(provider="p" * 301), False),
        (signal(first_seen_url="https://x.com/" + "a" * 286), True),
        (signal(first_seen_url="https://x.com/" + "a" * 287), False),
        (signal(timestamp="2026-09-26T13:14:15." + "1" * 279 + "Z"), True),
        (signal(timestamp="2026-09-26T13:14:15." + "1" * 280 + "Z"), False),
        (signal(signal_id="s" * 128), True),
        (signal(signal_id="s" * 129), False),
    ],
)
def test_schema_and_parser_accept_the_same_field_boundaries(
    payload: dict[str, object], accepted: bool,
) -> None:
    schema = json.loads(
        (ROOT / "schemas" / "release-signal-v1.schema.json").read_text(encoding="utf-8")
    )
    schema_accepts = Draft202012Validator(
        schema, format_checker=FormatChecker()
    ).is_valid(payload)
    try:
        ReleaseSignal.parse(payload)
    except SignalError:
        parser_accepts = False
    else:
        parser_accepts = True

    assert schema_accepts is accepted
    assert parser_accepts is accepted


def test_hmac_signature_covers_the_exact_request_body() -> None:
    raw = json.dumps(signal(), separators=(",", ":")).encode()
    signature = sign(b"shared-test-secret", raw)

    assert signature == "sha256=" + hmac.new(
        b"shared-test-secret", raw, hashlib.sha256
    ).hexdigest()
    assert ReleaseSignal.from_signed_body(raw, signature, b"shared-test-secret").signal_id == (
        "grok-20260926-123456789"
    )
    with pytest.raises(SignalError, match="signature"):
        ReleaseSignal.from_signed_body(raw + b" ", signature, b"shared-test-secret")


def test_excluded_sources_and_firecrawl_credits_fail_before_use() -> None:
    for host in REMOVED_HOSTS:
        with pytest.raises(ValueError, match="excluded source"):
            require_allowed_source(f"https://{host}/model")

    budget = FirecrawlBudget(20)
    budget.charge(20)
    with pytest.raises(RuntimeError, match="cap exceeded"):
        budget.charge(1)


def _write_card(root: Path, provider: str, slug: str, *, display: str, version: str) -> Path:
    path = root / "models" / provider / f"{slug}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "---\n"
        f"model_id: {provider}/{slug}\n"
        f"display_name: {display}\n"
        f"provider: {provider}\n"
        f"provider_display: {provider.title()}\n"
        f"version: {version}\n"
        "---\n",
        encoding="utf-8",
    )
    return path


def test_resolve_distinguishes_existing_new_and_uncertain_without_fuzzy_matching(
    tmp_path: Path,
) -> None:
    _write_card(tmp_path, "acme", "orbit-1", display="Orbit 1", version="orbit-1")
    _write_card(tmp_path, "acme", "shared-a", display="Shared", version="shared")
    _write_card(tmp_path, "acme", "shared-b", display="Shared", version="shared")

    existing = resolve_signal(ReleaseSignal.parse(signal(model_name="Orbit 1")), tmp_path)
    new = resolve_signal(ReleaseSignal.parse(signal()), tmp_path)
    uncertain = resolve_signal(ReleaseSignal.parse(signal(model_name="Shared")), tmp_path)

    assert (existing.status, existing.model_id) == ("existing", "acme/orbit-1")
    assert (new.status, new.model_id) == ("new", "acme/orbit-2")
    assert uncertain.status == "uncertain"
    assert uncertain.candidates == ("acme/shared-a", "acme/shared-b")


def test_production_shaped_models_dev_drafts_only_primary_source_facts(
    tmp_path: Path,
) -> None:
    _write_card(tmp_path, "acme", "orbit-1", display="Orbit 1", version="orbit-1")
    primary_url = "https://acme.example/models"
    models_dev_url = "https://models.dev/api.json"
    models_dev = (FIXTURES / "models-dev-production.json").read_bytes()
    replies = {
        models_dev_url: FetchResult(
            url=models_dev_url,
            body=models_dev,
            content_type="application/json",
        ),
        primary_url: FetchResult(
            url=primary_url,
            body=(FIXTURES / "acme-orbit.html").read_bytes(),
            content_type="text/html",
        ),
    }

    result = draft_signal(
        ReleaseSignal.parse(signal()),
        root=tmp_path,
        fetch=lambda url: replies[url],
        read_date=date(2026, 9, 26),
        models_dev_url=models_dev_url,
    )

    assert result.resolution.status == "new"
    assert result.card_path == tmp_path / "models" / "acme" / "orbit-2.md"
    front = yaml.safe_load(result.card_path.read_text(encoding="utf-8").split("---", 2)[1])
    assert front["model_id"] == "acme/orbit-2"
    assert front["display_name"] == "Orbit 2"
    assert str(front["release_date"]) == "2026-09-26"
    assert front["benchmarks"]["scores"] == {}
    assert front["benchmarks"]["evidence"] == []
    assert front["cost"] == {}
    assert front["sources"]["provider_docs_url"] == primary_url
    assert front["sources"]["models_dev_url"] == "https://models.dev/acme"
    assert front["sources"]["last_scraped_models_dev"] == "2026-09-26"
    assert front["sources"]["last_scraped_pricing"] == ""
    assert "x.com" not in result.card_path.read_text(encoding="utf-8")
    assert result.evidence_urls == (primary_url, models_dev_url)
    assert result.firecrawl_credits == 0


@pytest.mark.parametrize(
    "body",
    [
        (FIXTURES / "evil-labs-orbit-visible.html").read_bytes(),
        b"<html><body>Acme Orbit 2 by Evil Labs.</body></html>",
    ],
)
def test_visible_primary_source_with_another_lab_returns_uncertain_without_drafting(
    tmp_path: Path, body: bytes,
) -> None:
    _write_card(tmp_path, "acme", "orbit-1", display="Orbit 1", version="orbit-1")
    primary_url = "https://acme.example/models"
    models_dev_url = "https://models.dev/api.json"
    replies = {
        models_dev_url: FetchResult(
            url=models_dev_url,
            body=(FIXTURES / "models-dev-production.json").read_bytes(),
            content_type="application/json",
        ),
        primary_url: FetchResult(
            url=primary_url,
            body=body,
            content_type="text/html",
        ),
    }

    result = draft_signal(
        ReleaseSignal.parse(signal()),
        root=tmp_path,
        fetch=lambda url: replies[url],
        read_date=date(2026, 9, 26),
        models_dev_url=models_dev_url,
    )

    assert result.resolution.status == "uncertain"
    assert result.resolution.reason == "the primary source does not identify the stated lab"
    assert result.card_path is None
    assert not (tmp_path / "models" / "acme" / "orbit-2.md").exists()


@pytest.mark.parametrize(
    "body",
    [
        b"<html><body>Evil Labs compares its model with Acme Orbit 2.</body></html>",
        b"<html><body>Evil Labs launches Acme Orbit 2.</body></html>",
    ],
)
def test_ambiguous_lab_and_model_relationship_is_flagged_for_identity_review(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, body: bytes,
) -> None:
    _write_card(tmp_path, "acme", "orbit-1", display="Orbit 1", version="orbit-1")
    pending = tmp_path / "pending.json"
    result_path = tmp_path / "result.json"
    pending.write_text(json.dumps({"signals": [signal()]}), encoding="utf-8")
    primary_url = "https://acme.example/models"
    models_dev_url = "https://models.dev/api.json"
    hf_search = "https://huggingface.co/api/models?search=Orbit+2&limit=20"
    replies = {
        models_dev_url: FetchResult(
            url=models_dev_url,
            body=(FIXTURES / "models-dev-production.json").read_bytes(),
            content_type="application/json",
        ),
        primary_url: FetchResult(
            url=primary_url,
            body=body,
            content_type="text/html",
        ),
        hf_search: FetchResult(url=hf_search, body=b"[]", content_type="application/json"),
    }
    monkeypatch.setattr(processor, "_fetch", lambda url: replies[url])

    result = processor.process(pending, result_path, root=tmp_path)

    assert result["status"] == "uncertain"
    assert result["reason"] == "the primary source does not identify the stated lab"
    assert json.loads(result_path.read_text(encoding="utf-8")) == result
    assert not (tmp_path / "models" / "acme" / "orbit-2.md").exists()
    workflow = (ROOT / ".github" / "workflows" / "release-signals.yml").read_text(
        encoding="utf-8"
    )
    assert "if: steps.classify.outputs.resolution == 'uncertain'" in workflow
    assert "release signal needs identity review" in workflow


def test_models_dev_prices_do_not_change_existing_card_prices(
    tmp_path: Path,
) -> None:
    card = _write_card(tmp_path, "acme", "orbit-1", display="Orbit 1", version="orbit-1")
    original = card.read_text(encoding="utf-8")
    front = yaml.safe_load(original.split("---", 2)[1])
    front.update({
        "cost": {"input": 1.25, "output": 5.0},
        "sources": {
            "models_dev_url": "https://models.dev/acme",
            "provider_docs_url": "https://acme.example/models",
            "last_scraped_models_dev": "2026-09-25",
            "last_scraped_pricing": "2026-09-25",
        },
        "card_updated": "2026-09-25",
    })
    card.write_text(
        "---\n" + yaml.dump(front, sort_keys=False) + "---" + original.split("---", 2)[2],
        encoding="utf-8",
    )
    before = card.read_bytes()
    from release_signals.pipeline import GatherResult, Resolution

    update_existing_card(
        GatherResult(
            resolution=Resolution("existing", "acme/orbit-1"),
            provider_id="acme",
            primary_url="https://acme.example/models",
            supporting_urls=("https://acme.example/models",),
        ),
        root=tmp_path,
        read_date=date(2026, 9, 26),
    )

    assert card.read_bytes() == before


def test_new_signal_processes_production_payload_into_board_evidence(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    root = tmp_path / "repo"
    cache = tmp_path / "copies"
    existing = _write_card(root, "acme", "orbit-1", display="Orbit 1", version="orbit-1")
    existing_text = existing.read_text(encoding="utf-8")
    existing_front = yaml.safe_load(existing_text.split("---", 2)[1])
    existing_front["benchmarks"] = {"evidence": [{
        "benchmark_id": "fixture_benchmark",
        "model_id_as_evaluated": "Orbit 1",
        "score": 72.0,
        "unit": "percent",
        "source_url": "https://example.test/leaderboard.json",
        "source_kind": "independent_evaluator",
        "evidence_date": "2026-09-25",
        "date_type": "evaluated",
        "verified_at": "2026-09-25",
    }]}
    existing.write_text(
        "---\n" + yaml.dump(existing_front, sort_keys=False)
        + "---" + existing_text.split("---", 2)[2],
        encoding="utf-8",
    )
    (root / "registry").mkdir(parents=True)
    (root / "registry" / "sources.yaml").write_text(
        """schema_version: 1
sources:
- id: fixture-source
  url: https://example.test/leaderboard.json
  fetch: http
  normaliser: text-default
  cited_regions:
  - id: rows
    locator: {kind: page, value: ''}
""",
        encoding="utf-8",
    )
    (root / "verification").mkdir()
    pending = tmp_path / "pending.json"
    result_path = tmp_path / "result.json"
    pending.write_text(json.dumps({"signals": [signal()]}), encoding="utf-8")
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
    store = processor.refresh_leaderboards.CopyStore(cache)
    projection = processor.refresh_leaderboards.readers.document(
        [{"model": "Orbit 2", "score": "81.5%"}],
        url="https://example.test/leaderboard.json",
        page_ref="sha256:" + "b" * 64,
        read_date="2026-09-26",
        note="fixture",
    )
    board = processor.refresh_leaderboards._reading_from_projection(
        key="fixture", source_id="fixture-source", benchmarks=("fixture_benchmark",),
        source_url="https://example.test/leaderboard.json", projected=projection,
        observed_at="2026-09-26", value_field="score", store=store,
    )
    monkeypatch.setattr(processor, "_fetch", lambda url: replies[url])
    monkeypatch.setattr(
        processor.refresh_leaderboards, "collect_readings", lambda *_: ([board], [])
    )
    monkeypatch.setenv("MODELSPEC_SOURCE_CACHE", str(cache))

    result = processor.process(pending, result_path, root=root)

    assert result["evidence_added"] == 1
    assert result["quarantined"] == 0
    card = root / "models" / "acme" / "orbit-2.md"
    front = yaml.safe_load(card.read_text(encoding="utf-8").split("---", 2)[1])
    assert front["cost"] == {}
    assert [(row["benchmark_id"], row["score"]) for row in front["benchmarks"]["evidence"]] == [
        ("fixture_benchmark", 81.5)
    ]


def test_models_dev_cannot_make_x_a_card_source(tmp_path: Path) -> None:
    _write_card(tmp_path, "acme", "orbit-1", display="Orbit 1", version="orbit-1")
    models_dev_url = "https://models.dev/api.json"
    x_url = "https://x.com/acme/status/123456789"
    payload = {
        "acme": {
            "name": "Acme",
            "models": {
                "orbit-2": {"id": "orbit-2", "name": "Orbit 2", "release_url": x_url}
            },
        }
    }
    requested: list[str] = []

    def fetch(url: str) -> FetchResult:
        requested.append(url)
        return FetchResult(
            url=url,
            body=json.dumps(payload).encode(),
            content_type="application/json",
        )

    with pytest.raises(ValueError, match="signal-only source"):
        draft_signal(
            ReleaseSignal.parse(signal()), root=tmp_path, fetch=fetch,
            read_date=date(2026, 9, 26), models_dev_url=models_dev_url,
        )

    assert requested == [models_dev_url]
    assert not (tmp_path / "models" / "acme" / "orbit-2.md").exists()


def test_allowed_source_redirecting_to_x_is_rejected(tmp_path: Path) -> None:
    _write_card(tmp_path, "acme", "orbit-1", display="Orbit 1", version="orbit-1")
    models_dev_url = "https://models.dev/api.json"
    primary_url = "https://acme.example/models/orbit-2"
    payload = {
        "acme": {
            "name": "Acme",
            "models": {
                "orbit-2": {
                    "id": "orbit-2", "name": "Orbit 2", "release_url": primary_url,
                }
            },
        }
    }
    replies = {
        models_dev_url: FetchResult(
            url=models_dev_url, body=json.dumps(payload).encode(),
            content_type="application/json",
        ),
        primary_url: FetchResult(
            url="https://twitter.com/acme/status/123456789",
            body=(FIXTURES / "acme-orbit.html").read_bytes(), content_type="text/html",
        ),
    }

    with pytest.raises(ValueError, match="signal-only source"):
        draft_signal(
            ReleaseSignal.parse(signal()), root=tmp_path, fetch=lambda url: replies[url],
            read_date=date(2026, 9, 26), models_dev_url=models_dev_url,
        )

    assert not (tmp_path / "models" / "acme" / "orbit-2.md").exists()


def test_pending_work_includes_every_signal_and_due_recheck() -> None:
    payload = {
        "signals": [signal(signal_id="new-a"), signal(signal_id="new-b")],
        "rechecks": [
            {
                "day": 1,
                "due": "2026-09-27",
                "pr_url": "https://github.com/example/repo/pull/1",
                "signal": signal(signal_id="old-a"),
            },
            {
                "day": 7,
                "due": "2026-10-03",
                "pr_url": "https://github.com/example/repo/pull/2",
                "signal": signal(signal_id="old-b"),
            },
        ],
    }

    assert processor.work_items(payload) == [
        {"signal_id": "new-a", "recheck_day": 0, "pr_url": None},
        {"signal_id": "new-b", "recheck_day": 0, "pr_url": None},
        {
            "signal_id": "old-a",
            "recheck_day": 1,
            "pr_url": "https://github.com/example/repo/pull/1",
        },
        {
            "signal_id": "old-b",
            "recheck_day": 7,
            "pr_url": "https://github.com/example/repo/pull/2",
        },
    ]


def test_open_new_card_pr_day_one_recheck_updates_that_card(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    _write_card(tmp_path, "acme", "orbit-1", display="Orbit 1", version="orbit-1")
    _write_card(tmp_path, "acme", "orbit-2", display="Orbit 2", version="orbit-2")
    pending = tmp_path / "pending.json"
    result_path = tmp_path / "result.json"
    pr_url = "https://github.com/example/repo/pull/294"
    pending.write_text(json.dumps({
        "rechecks": [{
            "day": 1,
            "due": "2026-09-27",
            "pr_url": pr_url,
            "signal": signal(),
        }],
    }))
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
        processor.refresh_leaderboards,
        "run",
        lambda **_: processor.refresh_leaderboards.RefreshReport(),
    )

    result = processor.process(
        pending,
        result_path,
        root=tmp_path,
        signal_id="grok-20260926-123456789",
        recheck_day=1,
    )

    assert result["status"] == "existing"
    assert result["model_id"] == "acme/orbit-2"
    assert result["pr_url"] == pr_url
    assert sorted(path.name for path in (tmp_path / "models" / "acme").glob("*.md")) == [
        "orbit-1.md",
        "orbit-2.md",
    ]


def test_closed_unmerged_new_card_pr_stops_before_redrafting(tmp_path: Path) -> None:
    _write_card(tmp_path, "acme", "orbit-1", display="Orbit 1", version="orbit-1")
    pending = tmp_path / "pending.json"
    result_path = tmp_path / "result.json"
    pr_url = "https://github.com/example/repo/pull/294"
    pending.write_text(json.dumps({
        "rechecks": [{
            "day": 1,
            "due": "2026-09-27",
            "pr_url": pr_url,
            "signal": signal(),
        }],
    }))

    result = processor.process(
        pending,
        result_path,
        root=tmp_path,
        signal_id="grok-20260926-123456789",
        recheck_day=1,
        closed_unmerged_pr=pr_url,
    )

    assert result == {
        "status": "closed_unmerged",
        "signal_id": "grok-20260926-123456789",
        "model_id": None,
        "candidates": [],
        "recheck_day": 1,
        "recheck_due": "2026-09-27",
        "pr_url": pr_url,
        "reason": "the original new-model PR was closed without merge",
    }
    assert not (tmp_path / "models" / "acme" / "orbit-2.md").exists()


def test_existing_signal_gathers_sources_and_refreshes_only_its_model(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    card = _write_card(
        tmp_path, "acme", "orbit-1", display="Orbit 1", version="orbit-1"
    )
    text = card.read_text(encoding="utf-8")
    front = yaml.safe_load(text.split("---", 2)[1])
    front["cost"] = {"input": 0.75, "output": 3.0}
    card.write_text(
        "---\n" + yaml.dump(front, sort_keys=False) + "---" + text.split("---", 2)[2],
        encoding="utf-8",
    )
    pending = tmp_path / "pending.json"
    result_path = tmp_path / "result.json"
    pending.write_text(json.dumps({"signals": [signal(model_name="Orbit 1")]}))
    models_dev_url = "https://models.dev/api.json"
    primary_url = "https://acme.example/models/orbit-1"
    hf_search = "https://huggingface.co/api/models?search=Orbit+1&limit=20"
    payload = {
        "acme": {
            "name": "Acme",
            "models": {
                "orbit-1": {
                    "id": "orbit-1", "name": "Orbit 1", "release_url": primary_url,
                    "cost": {"input": 1.25, "output": 5.0},
                }
            },
        }
    }
    replies = {
        models_dev_url: FetchResult(
            url=models_dev_url, body=json.dumps(payload).encode(),
            content_type="application/json",
        ),
        primary_url: FetchResult(
            url=primary_url, body=b"<html><body>Acme releases Orbit 1.</body></html>",
            content_type="text/html",
        ),
        hf_search: FetchResult(
            url=hf_search, body=b"[]", content_type="application/json",
        ),
    }
    refreshed: dict[str, object] = {}

    def run_refresh(**kwargs: object):
        refreshed.update(kwargs)
        return processor.refresh_leaderboards.RefreshReport()

    monkeypatch.setattr(processor, "_fetch", lambda url: replies[url])
    monkeypatch.setattr(processor.refresh_leaderboards, "run", run_refresh)

    result = processor.process(pending, result_path, root=tmp_path)

    assert result["status"] == "existing"
    assert result["sources"] == [primary_url, models_dev_url]
    assert refreshed["model_ids"] == ("acme/orbit-1",)
    updated = yaml.safe_load(
        (tmp_path / "models" / "acme" / "orbit-1.md").read_text().split("---", 2)[1]
    )
    assert updated["cost"] == {"input": 0.75, "output": 3.0}
    assert "last_scraped_pricing" not in updated["sources"]
    assert updated["sources"]["provider_docs_url"] == primary_url


def test_new_cards_and_identity_or_licence_changes_require_human_merge(tmp_path: Path) -> None:
    before = tmp_path / "before"
    after = tmp_path / "after"
    _write_card(after, "acme", "orbit-2", display="Orbit 2", version="orbit-2")

    created = ChangePolicy.classify(before, after)

    assert created.merge == "human"
    assert created.labels == ("new-model",)
    assert not created.score_only

    before_card = _write_card(
        before, "acme", "orbit-1", display="Orbit 1", version="orbit-1"
    )
    after_card = _write_card(
        after, "acme", "orbit-1", display="Orbit One", version="orbit-1"
    )
    changed = ChangePolicy.classify(before, after)
    assert changed.merge == "human"
    assert changed.labels == ("new-model",)
    assert any(str(before_card.relative_to(before)) in reason for reason in changed.reasons)
    assert after_card.exists()

    unchanged = ChangePolicy.classify(after, after)
    assert not unchanged.changed
    assert not unchanged.score_only


def test_score_only_evidence_refresh_is_auto_mergeable(tmp_path: Path) -> None:
    before = tmp_path / "before"
    after = tmp_path / "after"
    card_before = _write_card(
        before, "acme", "orbit-1", display="Orbit 1", version="orbit-1"
    )
    card_after = _write_card(
        after, "acme", "orbit-1", display="Orbit 1", version="orbit-1"
    )
    evidence = """benchmarks:
  evidence:
  - benchmark_id: fixture_benchmark
    model_id_as_evaluated: Orbit 1
    score: 72.0
    unit: percent
    source_url: https://example.test/leaderboard.json
    source_kind: independent_evaluator
    evidence_date: '2026-09-25'
    date_type: evaluated
    verified_at: '2026-09-25'
"""
    for path, observed in ((card_before, "2026-09-25"), (card_after, "2026-09-26")):
        text = path.read_text(encoding="utf-8")
        front = yaml.safe_load(text.split("---", 2)[1])
        front.update(yaml.safe_load(evidence))
        front["benchmarks"]["evidence"][0]["observed_at"] = observed
        path.write_text(
            "---\n" + yaml.dump(front, sort_keys=False) + "---" + text.split("---", 2)[2],
            encoding="utf-8",
        )

    decision = ChangePolicy.classify(before, after)

    assert decision.changed
    assert decision.score_only
    assert decision.merge == "auto"


def test_worker_intake_authenticates_deduplicates_and_lists_pending() -> None:
    spec = importlib.util.spec_from_file_location(
        "modelspec_signals_service", ROOT / "api" / "worker" / "src" / "signals_service.py"
    )
    service = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = service
    spec.loader.exec_module(service)

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

    async def scenario() -> None:
        kv = KV()
        raw = json.dumps(signal(), separators=(",", ":")).encode()
        signature = sign(b"write-secret", raw)
        created = await service.intake(
            raw=raw,
            signature=signature,
            secret=b"write-secret",
            enabled=True,
            kv=kv,
            now=datetime(2026, 9, 26, 13, 15, tzinfo=UTC),
        )
        duplicate = await service.intake(
            raw=raw,
            signature=signature,
            secret=b"write-secret",
            enabled=True,
            kv=kv,
            now=datetime(2026, 9, 26, 13, 16, tzinfo=UTC),
        )
        refused = await service.pending(
            authorization="Bearer wrong", read_key="read-secret", kv=kv,
            today=date(2026, 9, 26),
        )
        pending = await service.pending(
            authorization="Bearer read-secret", read_key="read-secret", kv=kv,
            today=date(2026, 9, 26),
        )
        acknowledged = await service.acknowledge(
            authorization="Bearer read-secret",
            read_key="read-secret",
            kv=kv,
            payload={
                "signal_id": "grok-20260926-123456789",
                "result": "new",
                "pr_url": "https://github.com/example/repo/pull/1",
            },
            today=date(2026, 9, 26),
        )
        due = await service.pending(
            authorization="Bearer read-secret", read_key="read-secret", kv=kv,
            today=date(2026, 9, 27),
        )

        assert (created.status, created.body["status"]) == (202, "accepted")
        assert (duplicate.status, duplicate.body["status"]) == (200, "duplicate")
        assert refused.status == 401
        assert pending.body["signals"] == [signal()]
        assert acknowledged.body["recheck_days"] == [1, 7, 30]
        assert due.body["signals"] == []
        assert [(row["day"], row["signal_id"]) for row in due.body["rechecks"]] == [
            (1, "grok-20260926-123456789")
        ]
        rechecked = await service.acknowledge(
            authorization="Bearer read-secret",
            read_key="read-secret",
            kv=kv,
            payload={
                "signal_id": "grok-20260926-123456789",
                "result": "existing",
                "pr_url": "https://github.com/example/repo/pull/2",
                "recheck_day": 1,
                "recheck_due": "2026-09-27",
            },
            today=date(2026, 9, 27),
        )
        after_recheck = await service.pending(
            authorization="Bearer read-secret", read_key="read-secret", kv=kv,
            today=date(2026, 9, 27),
        )
        assert rechecked.body["recheck_days"] == []
        assert after_recheck.body["rechecks"] == []

    import asyncio

    asyncio.run(scenario())


@pytest.mark.parametrize(
    "payload",
    [
        {"signal_id": "grok-20260926-123456789"},
        {
            "signal_id": "grok-20260926-123456789",
            "result": "existing",
            "recheck_day": 99,
        },
        {
            "signal_id": "grok-20260926-123456789",
            "result": "existing",
            "unexpected": True,
        },
        {"signal_id": "contains spaces", "result": "existing"},
        {"signal_id": "grok-20260926-123456789", "result": 1},
        {
            "signal_id": "grok-20260926-123456789",
            "result": "existing",
            "pr_url": "/pull/1",
        },
        {
            "signal_id": "grok-20260926-123456789",
            "result": "existing",
            "recheck_due": "2026-02-30",
        },
        {
            "signal_id": "grok-20260926-123456789",
            "result": "existing",
            "recheck_day": [],
        },
        {
            "signal_id": "grok-20260926-123456789",
            "result": "existing",
            "recheck_due": None,
        },
        {
            "signal_id": "grok-20260926-123456789",
            "result": "existing",
            "recheck_day": None,
        },
    ],
)
def test_worker_acknowledgement_rejects_payloads_outside_the_contract_before_kv_access(
    payload: dict[str, object],
) -> None:
    spec = importlib.util.spec_from_file_location(
        "modelspec_ack_validation_signals_service",
        ROOT / "api" / "worker" / "src" / "signals_service.py",
    )
    service = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = service
    spec.loader.exec_module(service)

    class InaccessibleKV:
        async def get(self, key: str) -> None:
            raise AssertionError(f"read KV before validating acknowledgement: {key}")

    async def scenario() -> None:
        outcome = await service.acknowledge(
            authorization="Bearer read-secret",
            read_key="read-secret",
            kv=InaccessibleKV(),
            payload=payload,
            today=date(2026, 9, 26),
        )

        assert outcome.status == 400
        assert outcome.body["error"]["code"] == "invalid_request"

    import asyncio

    asyncio.run(scenario())


def test_worker_pending_follows_every_kv_page_after_an_empty_page() -> None:
    spec = importlib.util.spec_from_file_location(
        "modelspec_paginated_signals_service",
        ROOT / "api" / "worker" / "src" / "signals_service.py",
    )
    service = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = service
    spec.loader.exec_module(service)

    pending_key = service.PENDING_PREFIX + "grok-20260926-123456789"
    recheck_key = service.RECHECK_PREFIX + "2026-09-27/grok-20260926-123456789"

    class KV:
        def __init__(self) -> None:
            self.list_calls: list[dict[str, str]] = []
            self.rows = {
                pending_key: json.dumps(signal()),
                recheck_key: json.dumps({
                    "signal_id": "grok-20260926-123456789",
                    "due": "2026-09-27",
                    "day": 1,
                    "pr_url": "https://github.com/example/repo/pull/1",
                    "signal": signal(),
                }),
            }

        async def get(self, key: str) -> str | None:
            return self.rows.get(key)

        async def list(self, options: dict[str, str]) -> dict[str, object]:
            self.list_calls.append(dict(options))
            prefix = options["prefix"]
            cursor = options.get("cursor")
            if prefix == service.PENDING_PREFIX and cursor is None:
                return {"keys": [], "list_complete": False, "cursor": "pending-2"}
            if prefix == service.PENDING_PREFIX and cursor == "pending-2":
                return {"keys": [{"name": pending_key}], "list_complete": True}
            if prefix == service.RECHECK_PREFIX and cursor is None:
                return {
                    "keys": [],
                    "list_complete": False,
                    "cursor": "recheck-2",
                }
            if prefix == service.RECHECK_PREFIX and cursor == "recheck-2":
                return {"keys": [{"name": recheck_key}], "list_complete": True}
            raise AssertionError(f"unexpected list options: {options}")

    async def scenario() -> None:
        kv = KV()
        result = await service.pending(
            authorization="Bearer read-secret",
            read_key="read-secret",
            kv=kv,
            today=date(2026, 9, 27),
        )

        assert result.body["signals"] == [signal()]
        assert [(row["day"], row["signal_id"]) for row in result.body["rechecks"]] == [
            (1, "grok-20260926-123456789")
        ]
        assert kv.list_calls == [
            {"prefix": service.PENDING_PREFIX},
            {"prefix": service.PENDING_PREFIX, "cursor": "pending-2"},
            {"prefix": service.RECHECK_PREFIX},
            {"prefix": service.RECHECK_PREFIX, "cursor": "recheck-2"},
        ]

    import asyncio

    asyncio.run(scenario())


def test_hourly_workflow_keeps_github_credentials_out_of_the_signal_sender() -> None:
    workflow = (ROOT / ".github" / "workflows" / "release-signals.yml").read_text(
        encoding="utf-8"
    )

    assert "cron: '17 * * * *'" in workflow
    assert "MODELSPEC_SIGNALS_READ_KEY" in workflow
    assert "RESEARCH_PR_TOKEN" in workflow
    assert "modelspec verify --json" in workflow
    assert "scripts/accuracy.py --profile pr" in workflow
    assert "scripts/recall_run.py" in workflow
    assert "new-model" in workflow
    assert "--draft" in workflow
    assert "gh pr merge --auto --squash" in workflow
    assert "steps.classify.outputs.failures == '0'" in workflow
    assert "steps.classify.outputs.quarantined == '0'" in workflow
    assert "1, 7, and 30 day re-checks" in workflow
    assert "strategy:" in workflow
    assert "max-parallel: 4" in workflow
    assert "matrix: ${{ fromJSON(needs.pending.outputs.matrix) }}" in workflow
    assert "pr_url: (.pr_url // null)" in workflow
    assert 'gh pr view "$PR_URL" --json state,headRefName,headRepositoryOwner' in workflow
    assert "ref: ${{ steps.recheck.outputs.ref }}" in workflow
    assert "--signal-id \"${{ matrix.work.signal_id }}\"" in workflow
    assert "--recheck-day \"${{ matrix.work.recheck_day }}\"" in workflow
    assert '--closed-unmerged-pr "$PR_URL"' in workflow
    assert 'git push --set-upstream origin "HEAD:$branch"' in workflow
    assert 'gh pr comment "$EXISTING_PR_URL"' in workflow
    assert "steps.recheck.outputs.mode != 'open'" in workflow
    assert "Flag a new-model PR closed without merge" in workflow


def test_worker_endpoint_ships_off_and_vendors_the_shared_contract() -> None:
    wrangler = (ROOT / "api" / "worker" / "wrangler.jsonc").read_text(encoding="utf-8")
    vendor = (ROOT / "api" / "worker" / "vendor.py").read_text(encoding="utf-8")
    entry = (ROOT / "api" / "worker" / "src" / "entry.py").read_text(encoding="utf-8")

    assert '"SIGNALS_ENABLED": "false"' in wrangler
    assert 'Path("release_signals/contract.py")' in vendor
    assert '"POST /v1/signals"' in entry
    assert '"GET /v1/signals/pending"' in entry
