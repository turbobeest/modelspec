"""A release signal becomes a reviewable card change (MODEL-113)."""

from __future__ import annotations

import asyncio
import hashlib
import hmac
import httpx
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
    DraftResult,
    FetchResult,
    FirecrawlBudget,
    IdentityUncertainError,
    ModelsDevNotListed,
    RequiredSourceError,
    _JSON_LD_MAX_DEPTH,
    _JsonLd,
    _models_dev_listing,
    _primary_identity,
    clear_catalogue_cache,
    draft_signal,
    require_allowed_source,
    resolve_signal,
    update_existing_card,
)
from scripts import process_release_signals as processor

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = Path(__file__).parent / "fixtures" / "release_signals"


@pytest.fixture(autouse=True)
def _clear_catalogue_index_before_each_test() -> None:
    clear_catalogue_cache()


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


def _draft_visible_signal(
    tmp_path: Path, body: bytes, *, model_name: str = "Orbit 2",
    huggingface: bytes | None = None,
) -> DraftResult:
    _write_card(tmp_path, "acme", "orbit-1", display="Orbit 1", version="orbit-1")
    primary_url = "https://acme.example/models"
    models_dev_url = "https://models.dev/api.json"
    catalogue = json.loads((FIXTURES / "models-dev-production.json").read_bytes())
    catalogue["acme"]["models"]["orbit-2"]["name"] = model_name
    replies = {
        models_dev_url: FetchResult(
            models_dev_url, json.dumps(catalogue).encode(), "application/json",
        ),
        primary_url: FetchResult(primary_url, body, "text/html"),
    }
    if huggingface is not None:
        search_url = "https://huggingface.co/api/models?search=Orbit+2&limit=20"
        repo_url = "https://huggingface.co/acme/orbit-2"
        replies[search_url] = FetchResult(search_url, huggingface, "application/json")
        replies[repo_url] = FetchResult(repo_url, b"Model card", "text/html")
    return draft_signal(
        ReleaseSignal.parse(signal(model_name=model_name)),
        root=tmp_path, fetch=lambda url: replies[url],
        read_date=date(2026, 9, 26),
        discover_huggingface=huggingface is not None,
    )


@pytest.mark.parametrize(
    "body",
    [
        b"<h1>Acme launches Orbit 20.</h1>",
        b"<h1>NotAcme launches Orbit 2.</h1>",
        b"<h1>Acme launches Orbit 2 Pro.</h1>",
        b"<h1>Acme launches Orbit 2.1.</h1>",
        b"<p>Orbit 20 by Acme.</p>",
        b"<p>Orbit 2 Pro by Acme.</p>",
        b"<p>Orbit 2 by Acme Labs.</p>",
        b"<p>Acme launches Orbit 2.</p><p>Other Lab launches Orbit 2.</p>",
        b"<p>Acme launches Orbit 2.</p><p>Orbit 2 by Other Lab.</p>",
    ],
)
def test_similar_name_is_not_identity(tmp_path: Path, body: bytes) -> None:
    result = _draft_visible_signal(tmp_path, body)

    assert result.resolution.status == "uncertain"
    assert result.card_path is None
    assert not (tmp_path / "models" / "acme" / "orbit-2.md").exists()


@pytest.mark.parametrize(
    "body",
    [
        b"<h1>Acme announces Orbit 2.</h1>",
        b"<h1>Acme introduces Orbit 2.</h1>",
        b"<h1>Acme launches Orbit 2.</h1>",
        b"<h1>Acme releases Orbit 2</h1>",
        b"<p>Orbit 2 by Acme.</p>",
        b"<h1>ACME launches <em>Orbit-2</em>.</h1>",
    ],
)
def test_exact_visible_identity_drafts(tmp_path: Path, body: bytes) -> None:
    result = _draft_visible_signal(tmp_path, body)

    assert result.resolution.status == "new"
    assert result.card_path == tmp_path / "models" / "acme" / "orbit-2.md"
    assert result.card_path.is_file()


def test_exact_visible_identity_preserves_model_version(tmp_path: Path) -> None:
    result = _draft_visible_signal(
        tmp_path, b"<h1>Acme launches Orbit 2.1.</h1>", model_name="Orbit 2.1",
    )

    assert result.resolution.status == "new"
    assert result.card_path is not None
    assert result.card_path.is_file()
    front = yaml.safe_load(result.card_path.read_text().split("---", 2)[1])
    assert front["display_name"] == "Orbit 2.1"


@pytest.mark.parametrize(
    "payload",
    [b"[null]", b"[1]", b'["orbit-2"]', b"null", b"{}",
     b'[{"id":"acme/orbit-2"},null]'],
)
def test_malformed_optional_hf_does_not_block_card(tmp_path: Path, payload: bytes) -> None:
    result = _draft_visible_signal(
        tmp_path, b"<h1>Acme launches Orbit 2.</h1>", huggingface=payload,
    )

    assert result.card_path is not None
    assert result.card_path.is_file()
    assert len(result.gather_failures) == 1
    assert result.gather_failures[0].startswith("Hugging Face search failed:")
    assert result.evidence_urls == ("https://acme.example/models", "https://models.dev/api.json")


@pytest.mark.parametrize(
    ("payload", "expected_supporting"),
    [
        (b"[]", ()),
        (b'[{"id":"acme/orbit-2"}]', ("https://huggingface.co/acme/orbit-2",)),
        (b'[{"id":"other-lab/orbit-2"}]', ()),
        (b'[{"id":"acme/orbit-20"}]', ()),
    ],
)
def test_valid_optional_hf_preserves_exact_identity_checks(
    tmp_path: Path, payload: bytes, expected_supporting: tuple[str, ...],
) -> None:
    result = _draft_visible_signal(
        tmp_path, b"<h1>Acme launches Orbit 2.</h1>", huggingface=payload,
    )

    assert result.card_path is not None
    assert result.card_path.is_file()
    assert result.gather_failures == ()
    assert result.evidence_urls == (
        "https://acme.example/models", "https://models.dev/api.json", *expected_supporting,
    )


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
    workflow = (ROOT / ".github" / "private-writers" / "release-signals.yml").read_text(
        encoding="utf-8"
    )
    assert "release signals needing identity review" in workflow
    assert workflow.count("gh issue create") == 1


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
        processor.refresh_leaderboards, "collect_readings", lambda *_args, **_kwargs: ([board], [])
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


@pytest.fixture
def signals_service():
    spec = importlib.util.spec_from_file_location(
        "modelspec_regression_signals_service",
        ROOT / "api" / "worker" / "src" / "signals_service.py",
    )
    service = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = service
    spec.loader.exec_module(service)
    return service


class SignalKV:
    def __init__(self) -> None:
        self.rows: dict[str, str] = {}
        self.calls: list[tuple[str, str]] = []

    async def get(self, key: str) -> str | None:
        self.calls.append(("get", key))
        return self.rows.get(key)

    async def put(self, key: str, value: str) -> None:
        self.calls.append(("put", key))
        self.rows[key] = value

    async def delete(self, key: str) -> None:
        self.calls.append(("delete", key))
        self.rows.pop(key, None)

    async def list(self, options: dict[str, str]) -> dict[str, object]:
        self.calls.append(("list", options["prefix"]))
        return {"keys": [{"name": key} for key in self.rows if key.startswith(options["prefix"])]}


@pytest.mark.parametrize("legacy_pending", [False, True])
@pytest.mark.parametrize("conflicting", [False, True])
def test_replay_after_ack_is_still_duplicate(signals_service, legacy_pending, conflicting) -> None:
    async def scenario() -> None:
        kv = SignalKV()
        raw = json.dumps(signal()).encode()
        if legacy_pending:
            kv.rows[signals_service.PENDING_PREFIX + str(signal()["signal_id"])] = json.dumps(
                signal(), separators=(",", ":"), sort_keys=True,
            )
        else:
            accepted = await signals_service.intake(
                raw=raw, signature=sign(b"write-secret", raw), secret=b"write-secret",
                enabled=True, kv=kv, now=datetime(2026, 9, 26, 13, 15, tzinfo=UTC),
            )
            assert (accepted.status, accepted.body["status"]) == (202, "accepted")
        acknowledged = await signals_service.acknowledge(
            authorization="Bearer read-secret", read_key="read-secret", kv=kv,
            payload={"signal_id": signal()["signal_id"], "result": "new"},
            today=date(2026, 9, 26),
        )
        assert acknowledged.status == 200
        rows_after_ack = dict(kv.rows)
        raw = json.dumps(signal(model_name="Orbit 3") if conflicting else signal(),
                         sort_keys=True, separators=(",", ":")).encode()
        replay = await signals_service.intake(
            raw=raw, signature=sign(b"write-secret", raw), secret=b"write-secret",
            enabled=True, kv=kv, now=datetime(2026, 9, 26, 13, 16, tzinfo=UTC),
        )
        if conflicting:
            assert replay.status == 409
            assert replay.body["error"]["code"] == "signal_id_conflict"
        else:
            assert (replay.status, replay.body["status"]) == (200, "duplicate")
        pending = await signals_service.pending(
            authorization="Bearer read-secret", read_key="read-secret", kv=kv,
            today=date(2026, 9, 26),
        )
        assert pending.body["signals"] == []
        assert kv.rows == rows_after_ack

    asyncio.run(scenario())


@pytest.mark.parametrize(
    ("raw", "signature", "status"),
    [
        pytest.param(json.dumps(signal()).encode(), "sha256=é", 401, id="signature"),
        pytest.param(json.dumps(signal(first_seen_url="https://[broken/")).encode(),
                     None, 400, id="url"),
        pytest.param(json.dumps(signal(confidence=10**400)).encode(),
                     None, 400, id="confidence"),
        pytest.param(json.dumps(signal(timestamp="0001-01-01T00:00:00+01:00")).encode(),
                     None, 400, id="timestamp"),
        pytest.param(b"[" * 1100 + b"]" * 1100, None, 400, id="json"),
    ],
)
def test_invalid_input_returns_client_error(signals_service, raw, signature, status) -> None:
    kv = SignalKV()
    result = asyncio.run(signals_service.intake(
        raw=raw, signature=signature if signature is not None else sign(b"write-secret", raw),
        secret=b"write-secret", enabled=True, kv=kv,
        now=datetime(2026, 9, 26, 13, 15, tzinfo=UTC),
    ))

    assert result.status == status
    assert result.body["error"]["code"] == "invalid_signal"
    assert kv.calls == []


@pytest.mark.parametrize("endpoint", ["pending", "discovered", "acknowledge"])
def test_non_ascii_read_key_returns_401(signals_service, endpoint) -> None:
    kv = SignalKV()
    kwargs = {"authorization": "Bearer é", "read_key": "read-secret", "kv": kv}
    if endpoint == "discovered":
        kwargs["raw"] = b"{}"
    else:
        kwargs["today"] = date(2026, 9, 26)
    if endpoint == "acknowledge":
        kwargs["payload"] = {"signal_id": signal()["signal_id"], "result": None}
    result = asyncio.run(getattr(signals_service, endpoint)(**kwargs))

    assert result.status == 401
    assert result.body["error"]["code"] == "unauthorised"
    assert kv.calls == []


@pytest.mark.parametrize(
    "changes",
    [
        pytest.param({"first_seen_url": "https://[broken/"}, id="url"),
        pytest.param({"confidence": 10**400}, id="confidence"),
        pytest.param({"timestamp": "0001-01-01T00:00:00+01:00"}, id="timestamp"),
    ],
)
def test_invalid_discovery_returns_400(signals_service, changes) -> None:
    payload = signal(signal_id="watch:acme:orbit-2", first_seen_url="https://acme.example/models")
    payload.update(changes)
    kv = SignalKV()
    result = asyncio.run(signals_service.discovered(
        raw=json.dumps(payload).encode(), authorization="Bearer read-secret",
        read_key="read-secret", kv=kv, now=datetime(2026, 9, 26, 13, 15, tzinfo=UTC),
    ))

    assert result.status == 400
    assert result.body["error"]["code"] == "invalid_signal"
    assert kv.calls == []


def test_nested_discovery_json_returns_client_error(signals_service) -> None:
    kv = SignalKV()
    result = asyncio.run(signals_service.discovered(
        raw=b"[" * 1100 + b"]" * 1100,
        authorization="Bearer read-secret",
        read_key="read-secret",
        kv=kv,
        now=datetime(2026, 9, 26, 13, 15, tzinfo=UTC),
    ))

    assert result.status == 400
    assert result.body["error"]["code"] == "invalid_signal"
    assert kv.calls == []


def test_nested_acknowledgement_json_returns_client_error(signals_service) -> None:
    import ast

    tree = ast.parse((ROOT / "api/worker/src/entry.py").read_text())
    function = next(
        node for node in ast.walk(tree)
        if isinstance(node, ast.AsyncFunctionDef) and node.name == "_signals"
    )
    kv = SignalKV()
    namespace = {
        "json": json,
        "datetime": datetime,
        "UTC": UTC,
        "signals_service": signals_service,
        "SIGNALS_ENABLED_VAR": "SIGNALS_ENABLED",
        "SIGNALS_READ_KEY_VAR": "SIGNALS_READ_KEY",
        "_access_store": lambda _env: kv,
        "_json_response": lambda status, body: (status, body),
    }
    compiled = compile(
        ast.Module(body=[function], type_ignores=[]), "entry.py::_signals", "exec",
    )
    exec(compiled, namespace)

    class Env:
        SIGNALS_ENABLED = "true"
        SIGNALS_READ_KEY = "read-secret"

    class Request:
        headers = {"authorization": "Bearer read-secret"}

        async def text(self) -> str:
            return "[" * 1100 + "]" * 1100

    class Worker:
        env = Env()

    status, body = asyncio.run(namespace["_signals"](
        Worker(), Request(), "/v1/signals/ack", "POST", "audit",
    ))

    assert status == 400
    assert body["error"]["code"] == "invalid_request"
    assert kv.calls == []


def _signals_route(signals_service, kv):
    import ast

    tree = ast.parse((ROOT / "api/worker/src/entry.py").read_text())
    function = next(
        node for node in ast.walk(tree)
        if isinstance(node, ast.AsyncFunctionDef) and node.name == "_signals"
    )
    namespace = {
        "json": json,
        "datetime": datetime,
        "UTC": UTC,
        "signals_service": signals_service,
        "SIGNALS_ENABLED_VAR": "SIGNALS_ENABLED",
        "SIGNALS_HMAC_SECRET_VAR": "SIGNALS_HMAC_SECRET",
        "SIGNALS_READ_KEY_VAR": "SIGNALS_READ_KEY",
        "_access_store": lambda _env: kv,
        "_json_response": lambda status, body: (status, body),
    }
    compiled = compile(
        ast.Module(body=[function], type_ignores=[]), "entry.py::_signals", "exec",
    )
    exec(compiled, namespace)
    return namespace["_signals"]


class _BodyRequest:
    def __init__(self, body: str, headers: dict[str, str] | None = None) -> None:
        self.headers = {} if headers is None else headers
        self.reads = 0
        self._body = body

    async def text(self) -> str:
        self.reads += 1
        return self._body


class _SignalsWorker:
    class Env:
        SIGNALS_ENABLED = "true"
        SIGNALS_HMAC_SECRET = "write-secret"
        SIGNALS_READ_KEY = "read-secret"

    env = Env()


_NESTED_SIGNAL_BODY = "[" * 1100 + "]" * 1100


def _call_signals(signals_service, path: str, headers: dict[str, str], body: str):
    kv = SignalKV()
    request = _BodyRequest(body, headers)
    status, payload = asyncio.run(_signals_route(signals_service, kv)(
        _SignalsWorker(), request, path, "POST", "audit",
    ))
    return status, payload, request.reads, kv


@pytest.mark.parametrize(
    ("path", "headers", "body", "code"),
    [
        ("/v1/signals", {}, _NESTED_SIGNAL_BODY, "invalid_signal"),
        ("/v1/signals", {}, "x" * 5000, "invalid_signal"),
        ("/v1/signals", {"x-modelspec-signature": "sha256=zz"}, _NESTED_SIGNAL_BODY,
         "invalid_signal"),
        ("/v1/signals", {"x-modelspec-signature": "sha256=é"}, "x" * 5000, "invalid_signal"),
        ("/v1/signals", {"x-modelspec-signature": "sha256=" + ("AB" * 32)},
         _NESTED_SIGNAL_BODY, "invalid_signal"),
        ("/v1/signals/discovered", {}, _NESTED_SIGNAL_BODY, "unauthorised"),
        ("/v1/signals/discovered", {"authorization": "Bearer é"}, "x" * 5000, "unauthorised"),
        ("/v1/signals/ack", {}, _NESTED_SIGNAL_BODY, "unauthorised"),
        ("/v1/signals/ack", {"authorization": "Bearer é"}, _NESTED_SIGNAL_BODY, "unauthorised"),
        ("/v1/signals/ack", {"authorization": "Bearer wrong"}, _NESTED_SIGNAL_BODY, "unauthorised"),
    ],
)
def test_unauthenticated_signal_routes_do_not_read_the_body(
    signals_service, path, headers, body, code,
) -> None:
    status, payload, reads, kv = _call_signals(signals_service, path, headers, body)

    assert status == 401
    assert payload["error"]["code"] == code
    assert reads == 0
    assert kv.calls == []


def test_nested_acknowledgement_without_a_bearer_returns_401(signals_service) -> None:
    status, payload, reads, kv = _call_signals(
        signals_service, "/v1/signals/ack", {}, _NESTED_SIGNAL_BODY,
    )

    assert status == 401
    assert payload["error"]["code"] == "unauthorised"
    assert reads == 0
    assert kv.calls == []


def test_valid_bearer_keeps_nested_acknowledgement_invalid(signals_service) -> None:
    status, payload, reads, kv = _call_signals(
        signals_service, "/v1/signals/ack",
        {"authorization": "Bearer read-secret"}, _NESTED_SIGNAL_BODY,
    )

    assert status == 400
    assert payload["error"]["code"] == "invalid_request"
    assert reads == 1
    assert kv.calls == []


def test_a_well_formed_signature_is_checked_against_the_body(signals_service) -> None:
    status, payload, reads, kv = _call_signals(
        signals_service, "/v1/signals",
        {"x-modelspec-signature": "sha256=" + ("ab" * 32)}, _NESTED_SIGNAL_BODY,
    )

    assert status == 401
    assert payload["error"]["code"] == "invalid_signal"
    assert reads == 1
    assert kv.calls == []


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


def _run_pending_matrix(
    tmp_path: Path, pending: dict, limit: str, run: str = "0",
) -> dict[str, str]:
    import os
    import subprocess

    workflow = yaml.safe_load(
        (ROOT / ".github" / "private-writers" / "release-signals.yml").read_text(encoding="utf-8")
    )
    step = next(item for item in workflow["jobs"]["pending"]["steps"] if item.get("id") == "matrix")
    (tmp_path / "pending.json").write_text(json.dumps(pending), encoding="utf-8")
    output = tmp_path / "github-output"
    result = subprocess.run(
        ["bash", "-e", "-c", step["run"]],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        env=os.environ | {
            "RUNNER_TEMP": str(tmp_path),
            "GITHUB_OUTPUT": str(output),
            "MAX_RELEASE_SIGNAL_WORK_ITEMS": limit,
            "GITHUB_RUN_NUMBER": run,
        },
    )
    assert result.returncode == 0, result.stderr
    parsed: dict[str, str] = {}
    for line in output.read_text(encoding="utf-8").splitlines():
        key, value = line.split("=", 1)
        parsed[key] = value
    return parsed


def test_each_run_keeps_at_most_ten_work_items_signals_before_rechecks(tmp_path: Path) -> None:
    workflow_text = (ROOT / ".github" / "private-writers" / "release-signals.yml").read_text(
        encoding="utf-8"
    )
    assert 'MAX_RELEASE_SIGNAL_WORK_ITEMS: "10"' in workflow_text
    workflow = yaml.safe_load(workflow_text)
    matrix = next(item for item in workflow["jobs"]["pending"]["steps"] if item.get("id") == "matrix")
    assert "[:10]" not in matrix["run"]
    assert '--argjson limit "$MAX_RELEASE_SIGNAL_WORK_ITEMS"' in matrix["run"]
    signals = [
        {"signal_id": f"s{index:02d}", "timestamp": f"2026-01-{index:02d}T00:00:00Z"}
        for index in (3, 1, 2, 12, 4, 5, 6, 7, 8, 9, 10, 11)
    ]
    rechecks = [
        {
            "day": 7, "due": "2026-02-02", "pr_url": "https://github.com/example/repo/pull/2",
            "signal": {"signal_id": "r-late", "timestamp": "2026-01-02T00:00:00Z"},
        },
        {
            "day": 1, "due": "2026-02-01", "pr_url": None,
            "signal": {"signal_id": "r-early", "timestamp": "2026-01-09T00:00:00Z"},
        },
        {
            "day": 30, "due": "2026-02-01",
            "signal": {"signal_id": "r-tie", "timestamp": "2026-01-01T00:00:00Z"},
        },
    ]
    capped = _run_pending_matrix(tmp_path, {"signals": signals, "rechecks": rechecks}, "2")
    assert capped["count"] == "2"
    capped_work = json.loads(capped["matrix"])["work"]
    assert [item["signal_id"] for item in capped_work] == ["s01", "r-tie"]
    assert [item["recheck_day"] for item in capped_work] == [0, 30]
    assert [item["pr_url"] for item in capped_work] == [None, None]

    selected = _run_pending_matrix(
        tmp_path, {"signals": signals[:2], "rechecks": rechecks}, "10",
    )
    # signals[:2] is the shuffled prefix (s03, s01), not the two oldest.
    work = json.loads(selected["matrix"])["work"]
    assert selected["count"] == "5"
    assert [item["signal_id"] for item in work] == ["s01", "s03", "r-tie", "r-early", "r-late"]
    assert [item["recheck_day"] for item in work] == [0, 0, 30, 1, 7]
    assert work[3]["pr_url"] is None
    assert work[4]["pr_url"] == "https://github.com/example/repo/pull/2"

    review = workflow["jobs"]["review"]
    assert review["name"] == "Open one identity-review issue"
    assert review["needs"] == ["pending", "process"]
    assert "needs.pending.outputs.count != '0'" in review["if"]
    review_runs = "\n".join(step.get("run") or "" for step in review["steps"])
    assert "python" not in review_runs
    assert "release signals needing identity review" in review_runs
    assert 'select(.status == "uncertain")' in review_runs
    assert workflow_text.count("gh issue create") == 1
    process_steps = workflow["jobs"]["process"]["steps"]
    uploaded = [
        step for step in process_steps
        if step.get("uses") == "actions/upload-artifact@v4"
        and step.get("with", {}).get("path") == "${{ runner.temp }}/result.json"
    ]
    assert len(uploaded) == 1
    assert uploaded[0]["if"] == "always()"
    assert uploaded[0]["with"]["if-no-files-found"] == "ignore"
    closed = next(step for step in process_steps if step.get("id") == "closed_pr")
    assert "gh issue create" not in (closed.get("run") or "")
    assert "Flag a new-model PR closed without merge" == closed["name"]
    ack = next(step for step in process_steps if "Acknowledge the signal" in step.get("name", ""))
    assert "steps.uncertain.outputs.url" not in ack["env"]["RESULT_URL"]


def test_pending_selection_rotates_instead_of_blocking_the_queue(tmp_path: Path) -> None:
    signals = [
        {"signal_id": f"s{index:02d}", "timestamp": f"2026-01-{index + 1:02d}T00:00:00Z"}
        for index in range(12)
    ]
    rechecks = [
        {
            "day": 1,
            "due": f"2026-03-{index + 1:02d}",
            "pr_url": None,
            "signal": {"signal_id": f"r{index}", "timestamp": "2026-01-01T00:00:00Z"},
        }
        for index in range(5)
    ]

    def selected_ids(name: str, run: str, pending: dict) -> list[str]:
        directory = tmp_path / name
        directory.mkdir()
        parsed = _run_pending_matrix(directory, pending, "10", run)
        assert parsed["count"] == str(len(json.loads(parsed["matrix"])["work"]))
        return [item["signal_id"] for item in json.loads(parsed["matrix"])["work"]]

    full = {"signals": signals, "rechecks": rechecks}
    assert selected_ids("run1", "1", full) == [
        "s01", "s02", "s03", "s04", "s05", "s06", "s07", "r1", "r2", "r3",
    ]
    assert selected_ids("run2", "2", full) == [
        "s02", "s03", "s04", "s05", "s06", "s07", "s08", "r2", "r3", "r4",
    ]
    assert selected_ids("run13", "13", full) == [
        "s01", "s02", "s03", "s04", "s05", "s06", "s07", "r3", "r4", "r0",
    ]
    assert selected_ids("few-signals", "1", {
        "signals": signals[:2], "rechecks": rechecks,
    }) == ["s00", "s01", "r0", "r1", "r2", "r3", "r4"]
    assert selected_ids("few-rechecks", "1", {
        "signals": signals, "rechecks": rechecks[:1],
    }) == ["s01", "s02", "s03", "s04", "s05", "s06", "s07", "s08", "s09", "r0"]
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    empty = _run_pending_matrix(empty_dir, {"signals": [], "rechecks": []}, "10", "1")
    assert empty["count"] == "0"
    assert json.loads(empty["matrix"])["work"] == []


def test_per_job_artifact_names_keep_signal_punctuation_out() -> None:
    from fnmatch import fnmatch

    workflow = yaml.safe_load(
        (ROOT / ".github" / "private-writers" / "release-signals.yml").read_text(encoding="utf-8")
    )
    signal_id = "watch:acme/orbit-6.1"
    job_index = "4"
    expected = {
        "${{ runner.temp }}/result.json": "release-signal-result-",
        "${{ runner.temp }}/source-copies": "release-signal-price-copies-",
        "${{ runner.temp }}/audit.json": "release-signal-audit-",
    }
    rendered_names: dict[str, str] = {}
    for step in workflow["jobs"]["process"]["steps"]:
        if step.get("uses") != "actions/upload-artifact@v4":
            continue
        path = step.get("with", {}).get("path")
        if path not in expected:
            continue
        assert step["with"].get("overwrite") is True
        template = step["with"]["name"]
        rendered = (
            template
            .replace("${{ matrix.work.signal_id }}", signal_id)
            .replace("${{ steps.classify.outputs.signal_id }}", signal_id)
            .replace("${{ matrix.work.recheck_day }}", "1")
            .replace("${{ strategy.job-index }}", job_index)
        )
        assert "${{" not in rendered
        assert ":" not in rendered
        assert "/" not in rendered
        assert signal_id not in rendered
        prefix = expected[path]
        assert rendered == f"{prefix}{job_index}"
        rendered_names[path] = rendered
    assert set(rendered_names) == set(expected)
    pattern = next(
        step["with"]["pattern"]
        for step in workflow["jobs"]["review"]["steps"]
        if step.get("uses") == "actions/download-artifact@v4"
    )
    assert pattern == "release-signal-result-*"
    assert fnmatch(rendered_names["${{ runner.temp }}/result.json"], pattern)


def _gh_invocations(run: str) -> list[str]:
    lines = run.splitlines()
    calls: list[str] = []
    index = 0
    while index < len(lines):
        stripped = lines[index].strip()
        if stripped.startswith("#") or not stripped.startswith("gh "):
            index += 1
            continue
        parts = [stripped]
        while parts[-1].endswith("\\"):
            index += 1
            parts.append(lines[index].strip())
        calls.append(" ".join(part.removesuffix("\\").strip() for part in parts))
        index += 1
    return calls


def test_review_job_gh_calls_name_the_repository() -> None:
    workflow = yaml.safe_load(
        (ROOT / ".github" / "private-writers" / "release-signals.yml").read_text(encoding="utf-8")
    )
    review = workflow["jobs"]["review"]
    job_env = dict(review.get("env") or {})
    calls: list[str] = []
    for step in review["steps"]:
        step_env = {**job_env, **dict(step.get("env") or {})}
        for call in _gh_invocations(step.get("run") or ""):
            calls.append(call)
            assert "GH_REPO" in step_env or "--repo" in call
    assert calls == [
        "gh label create new-model --color 0E8A16 "
        "--description 'Release identity needs human review' --force",
        "gh issue create --title \"release signals needing identity review ($today)\" "
        "--label new-model --body-file \"$RUNNER_TEMP/issue-body.md\"",
    ]
    assert review["env"]["GH_REPO"] == "${{ github.repository }}"


def test_the_roll_up_opens_one_issue_only_for_uncertain_results(tmp_path: Path) -> None:
    import os
    import subprocess

    workflow = yaml.safe_load(
        (ROOT / ".github" / "private-writers" / "release-signals.yml").read_text(encoding="utf-8")
    )
    step = next(
        item for item in workflow["jobs"]["review"]["steps"]
        if item.get("name") == "Open one issue for uncertain identities"
    )
    results = tmp_path / "signal-results"
    (results / "a").mkdir(parents=True)
    (results / "b").mkdir()
    (results / "a" / "result.json").write_text(json.dumps({
        "status": "uncertain", "signal_id": "s-a", "reason": "two cards",
    }), encoding="utf-8")
    (results / "b" / "result.json").write_text(json.dumps({
        "status": "ignored", "signal_id": "s-b", "reason": "test signal",
    }), encoding="utf-8")
    stub = tmp_path / "bin"
    stub.mkdir()
    (stub / "gh").write_text(
        "#!/bin/bash\nprintf '%s\\n' \"$*\" > \"$RUNNER_TEMP/gh-args\"\n",
        encoding="utf-8",
    )
    (stub / "gh").chmod(0o755)
    env = os.environ | {
        "RUNNER_TEMP": str(tmp_path),
        "GH_TOKEN": "offline-fixture",
        "PATH": f"{stub}{os.pathsep}{os.environ['PATH']}",
    }

    opened = subprocess.run(
        ["bash", "-e", "-c", step["run"]], cwd=tmp_path, capture_output=True, text=True, env=env,
    )
    assert opened.returncode == 0, opened.stderr
    assert "issue create" in (tmp_path / "gh-args").read_text(encoding="utf-8")
    assert "release signals needing identity review" in (tmp_path / "gh-args").read_text(encoding="utf-8")
    assert "- s-a: two cards" in (tmp_path / "issue-body.md").read_text(encoding="utf-8")
    assert "s-b" not in (tmp_path / "issue-body.md").read_text(encoding="utf-8")

    (results / "a" / "result.json").write_text(json.dumps({
        "status": "existing", "signal_id": "s-a", "reason": "",
    }), encoding="utf-8")
    (tmp_path / "gh-args").unlink()
    quiet = subprocess.run(
        ["bash", "-e", "-c", step["run"]], cwd=tmp_path, capture_output=True, text=True, env=env,
    )
    assert quiet.returncode == 0, quiet.stderr
    assert not (tmp_path / "gh-args").exists()


def _run_review_issue_step(tmp_path: Path) -> str:
    import os
    import subprocess

    workflow = yaml.safe_load(
        (ROOT / ".github" / "private-writers" / "release-signals.yml").read_text(encoding="utf-8")
    )
    step = next(
        item for item in workflow["jobs"]["review"]["steps"]
        if item.get("name") == "Open one issue for uncertain identities"
    )
    stub = tmp_path / "bin"
    stub.mkdir(exist_ok=True)
    (stub / "gh").write_text(
        "#!/bin/bash\nprintf '%s\\n' \"$*\" > \"$RUNNER_TEMP/gh-args\"\n",
        encoding="utf-8",
    )
    (stub / "gh").chmod(0o755)
    env = os.environ | {
        "RUNNER_TEMP": str(tmp_path),
        "GH_TOKEN": "offline-fixture",
        "PATH": f"{stub}{os.pathsep}{os.environ['PATH']}",
    }
    opened = subprocess.run(
        ["bash", "-e", "-c", step["run"]],
        cwd=tmp_path, capture_output=True, text=True, env=env,
    )
    assert opened.returncode == 0, opened.stderr
    return (tmp_path / "issue-body.md").read_text(encoding="utf-8")


def test_the_roll_up_lists_a_closed_unmerged_result_under_its_own_heading(
    tmp_path: Path,
) -> None:
    results = tmp_path / "signal-results"
    (results / "a").mkdir(parents=True)
    (results / "b").mkdir()
    (results / "c").mkdir()
    pr_url = "https://github.com/example/repo/pull/294"
    (results / "a" / "result.json").write_text(json.dumps({
        "status": "uncertain", "signal_id": "s-a", "reason": "two cards",
    }), encoding="utf-8")
    (results / "b" / "result.json").write_text(json.dumps({
        "status": "ignored", "signal_id": "s-b", "reason": "test signal",
    }), encoding="utf-8")
    (results / "c" / "result.json").write_text(json.dumps({
        "status": "closed_unmerged",
        "signal_id": "s-c",
        "reason": "the original new-model PR was closed without merge",
        "pr_url": pr_url,
    }), encoding="utf-8")

    body = _run_review_issue_step(tmp_path)
    assert "issue create" in (tmp_path / "gh-args").read_text(encoding="utf-8")
    assert "- s-a: two cards" in body
    assert "s-b" not in body
    assert "New-model pull requests closed without merge" in body
    closed_line = (
        "- s-c: the original new-model PR was closed without merge "
        f"({pr_url})"
    )
    assert closed_line in body

    (results / "a" / "result.json").write_text(json.dumps({
        "status": "existing", "signal_id": "s-a", "reason": "",
    }), encoding="utf-8")
    (tmp_path / "gh-args").unlink()
    (tmp_path / "issue-body.md").unlink()
    closed_only = _run_review_issue_step(tmp_path)
    assert "issue create" in (tmp_path / "gh-args").read_text(encoding="utf-8")
    assert "Signals whose identity could not be resolved." not in closed_only
    assert "New-model pull requests closed without merge" in closed_only
    assert "s-a" not in closed_only
    assert "s-b" not in closed_only

    (results / "c" / "result.json").write_text(json.dumps({
        "status": "uncertain", "signal_id": "s-a", "reason": "two cards",
    }), encoding="utf-8")
    (tmp_path / "gh-args").unlink()
    uncertain_only = _run_review_issue_step(tmp_path)
    assert "- s-a: two cards" in uncertain_only
    assert "New-model pull requests closed without merge" not in uncertain_only


def test_only_the_release_signals_verify_step_skips_absent_copies() -> None:
    roots = [ROOT / ".github" / "private-writers", ROOT / ".github" / "workflows"]
    hits = []
    for root in roots:
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            if "--skip-absent-copies" in text:
                hits.append(path.relative_to(ROOT).as_posix())
    assert hits == [".github/private-writers/release-signals.yml"]
    workflow = yaml.safe_load(
        (ROOT / ".github" / "private-writers" / "release-signals.yml").read_text(encoding="utf-8")
    )
    steps = workflow["jobs"]["process"]["steps"]
    verify_steps = [
        step for step in steps
        if step.get("name") == "Validate cards and run two-key verification"
    ]
    assert len(verify_steps) == 1
    assert "--skip-absent-copies" in verify_steps[0]["run"]
    others = "\n".join(
        step.get("run") or "" for step in steps if step is not verify_steps[0]
    )
    assert "--skip-absent-copies" not in others


def test_the_verify_step_writes_outcome_counts_to_the_step_summary() -> None:
    workflow = yaml.safe_load(
        (ROOT / ".github" / "private-writers" / "release-signals.yml").read_text(encoding="utf-8")
    )
    step = next(
        item for item in workflow["jobs"]["process"]["steps"]
        if item.get("name") == "Validate cards and run two-key verification"
    )
    run = step["run"]
    for label in (
        "verified:", "mismatch:", "unreachable:", "skipped:",
        "skipped for no copy:", "GITHUB_STEP_SUMMARY",
    ):
        assert label in run
    assert "results" not in run


def test_the_process_job_cannot_open_issues() -> None:
    workflow = yaml.safe_load(
        (ROOT / ".github" / "private-writers" / "release-signals.yml").read_text(encoding="utf-8")
    )
    assert workflow["jobs"]["process"]["timeout-minutes"] == 30
    assert "issues" not in workflow["jobs"]["process"]["permissions"]
    assert workflow["jobs"]["review"]["permissions"]["issues"] == "write"
    for step in workflow["jobs"]["process"]["steps"]:
        run = step.get("run") or ""
        assert "gh label" not in run
        assert "gh issue" not in run
    review_runs = "\n".join(
        step.get("run") or "" for step in workflow["jobs"]["review"]["steps"]
    )
    assert "gh label create new-model" in review_runs


def test_the_process_job_gates_on_approved_private_answers_before_push() -> None:
    workflow = yaml.safe_load(
        (ROOT / ".github" / "private-writers" / "release-signals.yml").read_text(encoding="utf-8")
    )
    steps = workflow["jobs"]["process"]["steps"]
    names = [step.get("name") for step in steps]
    recall_at = names.index("Run the MODEL-160 recall report")
    gate_at = names.index("Compare approved answers on private data")
    push_at = names.index("Commit and push the isolated signal branch")
    assert recall_at < gate_at < push_at
    step = steps[gate_at]
    assert step["if"] == "steps.classify.outputs.changed == 'true'"
    assert "continue-on-error" not in step
    run = step["run"]
    assert "python -I -m scripts.recall_run" not in run
    assert "scripts/recall_run.py" not in run
    assert "||" not in run
    assert "python -I -m scripts.accuracy --compare-approved-answers" in run
    assert "reports/recall/check.py" not in run
    assert '--report-dir "$RUNNER_TEMP/recall"' in run
    assert "--baseline reports/recall/baseline.json" in run
    assert '--summary "$GITHUB_STEP_SUMMARY"' in run
    assert '--approved-baseline "$RUNNER_TEMP/approved-private-recall.json"' in run


def test_the_approved_answer_outputs_wire_the_pull_request_step() -> None:
    gate = _process_step("Compare approved answers on private data")
    opened = _process_step("Open or update the pull request")
    writer = (ROOT / "scripts" / "accuracy.py").read_text(encoding="utf-8")
    step_id = gate["id"]

    assert step_id == "approved"
    assert '--step-output "$GITHUB_OUTPUT"' in gate["run"]
    assert 'handle.write(f"regressed=' in writer
    assert 'handle.write(f"regression_ids=' in writer
    assert opened["env"]["REGRESSED"] == f"${{{{ steps.{step_id}.outputs.regressed }}}}"
    assert opened["env"]["REGRESSION_IDS"] == (
        f"${{{{ steps.{step_id}.outputs.regression_ids }}}}"
    )


def _process_step(name: str) -> dict:
    workflow = yaml.safe_load(
        (ROOT / ".github" / "private-writers" / "release-signals.yml").read_text(encoding="utf-8")
    )
    return next(
        step for step in workflow["jobs"]["process"]["steps"] if step.get("name") == name
    )


def _engine_python(tmp_path: Path) -> Path:
    """A `python` on PATH that loads this worktree, as the runner's .pth file does."""
    bindir = tmp_path / "bin"
    bindir.mkdir()
    launcher = bindir / "launch.py"
    launcher.write_text(
        "import sys\n"
        f"sys.path.insert(0, {str(ROOT)!r})\n"
        "args = sys.argv[1:]\n"
        "if args and args[0] == '-I':\n"
        "    args = args[1:]\n"
        "if len(args) >= 2 and args[0] == '-m':\n"
        "    sys.argv = [args[1], *args[2:]]\n"
        "    module = __import__(args[1], fromlist=['main'])\n"
        "    raise SystemExit(module.main())\n"
        "if args and args[0] == '-c':\n"
        "    exec(compile(args[1], '<workflow>', 'exec'), {'__name__': '__main__'})\n"
        "    raise SystemExit(0)\n"
        "raise SystemExit('unexpected python arguments')\n",
        encoding="utf-8",
    )
    wrapper = bindir / "python"
    wrapper.write_text(f"#!/bin/sh\nexec {sys.executable} {launcher} \"$@\"\n", encoding="utf-8")
    wrapper.chmod(0o755)
    return bindir


def _approved_data_repo(tmp_path: Path) -> Path:
    import subprocess

    data = tmp_path / "data"
    recall = data / "reports" / "recall"
    recall.mkdir(parents=True)
    verdicts = {f"Q{number:02d}": "pass" for number in range(1, 21)}
    (recall / "baseline.json").write_text(
        json.dumps({"schema_version": 1, "verdicts": verdicts}), encoding="utf-8",
    )
    subprocess.run(["git", "init", "-q"], cwd=data, check=True)
    subprocess.run(["git", "config", "user.email", "signals@example.com"], cwd=data, check=True)
    subprocess.run(["git", "config", "user.name", "signals"], cwd=data, check=True)
    subprocess.run(["git", "add", "reports"], cwd=data, check=True)
    subprocess.run(
        ["git", "-c", "commit.gpgsign=false", "commit", "-q", "-m", "baseline"],
        cwd=data, check=True,
    )
    subprocess.run(["git", "update-ref", "refs/remotes/origin/main", "HEAD"], cwd=data, check=True)
    return data


def _run_approved_step(tmp_path: Path, *, report: dict | None) -> subprocess.CompletedProcess[str]:
    import os
    import subprocess

    data = _approved_data_repo(tmp_path)
    runner = tmp_path / "runner"
    runner.mkdir()
    if report is not None:
        recall = runner / "recall"
        recall.mkdir()
        (recall / "recall.json").write_text(json.dumps({"questions": [
            {"id": question_id, "verdict": verdict}
            for question_id, verdict in report.items()
        ]}), encoding="utf-8")
    step = _process_step("Compare approved answers on private data")
    env = os.environ | {
        "PATH": f"{_engine_python(tmp_path)}:{os.environ['PATH']}",
        "RUNNER_TEMP": str(runner),
        "GITHUB_OUTPUT": str(runner / "github-output"),
        "GITHUB_STEP_SUMMARY": str(runner / "summary"),
    }
    return subprocess.run(
        ["bash", "-e", "-c", step["run"]],
        cwd=data, capture_output=True, text=True, env=env, check=False,
    )


def test_a_regression_exits_zero_and_acknowledgement_still_runs(tmp_path: Path) -> None:
    report = {f"Q{number:02d}": "pass" for number in range(1, 21)}
    report["Q01"] = "partial"
    result = _run_approved_step(tmp_path, report=report)
    ack = _process_step("Acknowledge the signal and schedule its 1, 7, and 30 day re-checks")
    commit = _process_step("Commit and push the isolated signal branch")
    opened = _process_step("Open or update the pull request")

    assert result.returncode == 0, result.stderr
    recorded = (tmp_path / "runner" / "github-output").read_text(encoding="utf-8")
    assert "regressed=true\n" in recorded
    assert "regression_ids=Q01\n" in recorded
    assert ack["if"] == "steps.classify.outputs.resolution != 'empty'"
    assert "approved" not in ack["if"]
    assert commit["if"] == "steps.classify.outputs.changed == 'true'"
    assert opened["if"] == "steps.classify.outputs.changed == 'true'"


def test_an_unreadable_approved_answer_input_fails_the_job(tmp_path: Path) -> None:
    step = _process_step("Compare approved answers on private data")
    result = _run_approved_step(tmp_path, report=None)

    assert "continue-on-error" not in step
    assert result.returncode != 0


@pytest.mark.parametrize("human", ["true", "false"])
def test_a_regression_forces_a_draft_and_lists_the_question_ids(tmp_path: Path, human: str) -> None:
    import os
    import subprocess

    step = _process_step("Open or update the pull request")
    (tmp_path / "result.json").write_text(
        json.dumps({"model_id": "acme/orbit"}), encoding="utf-8",
    )
    env = os.environ | {
        "PATH": f"{Path(sys.executable).parent}:{os.environ['PATH']}",
        "RUNNER_TEMP": str(tmp_path),
        "GITHUB_OUTPUT": str(tmp_path / "github-output"),
        "BRANCH": "data/release-signal-fixture-initial",
        "PR_MODE": "initial",
        "HUMAN": human,
        "REGRESSED": "true",
        "REGRESSION_IDS": "Q01, Q05",
        "EXISTING_PR_URL": "",
    }
    stub = (
        'gh() { printf "%s\\n" "$*" >> "$RUNNER_TEMP/calls"; '
        'echo "https://github.com/turbobeest/modelspec-data/pull/9"; }\n'
    )
    result = subprocess.run(
        ["bash", "-e", "-c", stub + step["run"]],
        cwd=tmp_path, capture_output=True, text=True, env=env, check=False,
    )

    assert result.returncode == 0, result.stderr
    recorded = (tmp_path / "calls").read_text(encoding="utf-8")
    body = (tmp_path / "pr-body.md").read_text(encoding="utf-8")
    assert recorded.splitlines()[0].startswith("pr create --draft ")
    assert "ANSWERS REGRESS: " in recorded
    assert body.startswith("Regressed question ids: Q01, Q05\n")
    assert (
        'The data repository\'s "Approved answers on private data" check must pass before merge.\n'
        in body
    )
    if human == "true":
        assert "--label new-model" in recorded
        assert "data: add or identify acme/orbit (MODEL-113)" in recorded
    else:
        assert "--label" not in recorded
        assert "data: refresh acme/orbit release evidence (MODEL-113)" in recorded


_OPEN_PR_URL = "https://github.com/turbobeest/modelspec-data/pull/41"
_REGRESS_CHECK_LINE = (
    'The data repository\'s "Approved answers on private data" check must pass before merge.\n'
)


def _run_open_pr_step(
    tmp_path: Path,
    *,
    human: str,
    regressed: str,
    title: str,
    fail: str = "",
) -> subprocess.CompletedProcess[str]:
    import os
    import subprocess

    step = _process_step("Open or update the pull request")
    (tmp_path / "result.json").write_text(
        json.dumps({"model_id": "acme/orbit"}), encoding="utf-8",
    )
    env = os.environ | {
        "PATH": f"{Path(sys.executable).parent}:{os.environ['PATH']}",
        "RUNNER_TEMP": str(tmp_path),
        "GITHUB_OUTPUT": str(tmp_path / "github-output"),
        "BRANCH": "data/release-signal-fixture-recheck",
        "PR_MODE": "open",
        "HUMAN": human,
        "REGRESSED": regressed,
        "REGRESSION_IDS": "Q01, Q05",
        "EXISTING_PR_URL": _OPEN_PR_URL,
        "EXISTING_TITLE": title,
        "GH_FAIL": fail,
    }
    stub = """\
gh() {
  printf '%s\\n' "$*" >> "$RUNNER_TEMP/calls"
  if [ -n "${GH_FAIL:-}" ] && [ "$2" = "$GH_FAIL" ]; then
    echo "gh failed" >&2
    return 1
  fi
  if [ "$1 $2" = "pr view" ]; then
    printf '%s\\n' "{\\"title\\":\\"$EXISTING_TITLE\\"}"
    return 0
  fi
  printf '%s\\n' "https://github.com/turbobeest/modelspec-data/pull/9"
}
"""
    return subprocess.run(
        ["bash", "-e", "-c", stub + step["run"]],
        cwd=tmp_path, capture_output=True, text=True, env=env, check=False,
    )


def _open_pr_calls(tmp_path: Path) -> list[str]:
    return (tmp_path / "calls").read_text(encoding="utf-8").splitlines()


def test_an_open_score_only_regression_converts_the_pull_request_to_a_draft(
    tmp_path: Path,
) -> None:
    title = "data: refresh acme/orbit release evidence (MODEL-113)"
    result = _run_open_pr_step(
        tmp_path, human="false", regressed="true", title=title,
    )

    assert result.returncode == 0, result.stderr
    recorded = _open_pr_calls(tmp_path)
    assert recorded[0] == f"pr ready --undo {_OPEN_PR_URL}"
    assert recorded[1] == f"pr view {_OPEN_PR_URL} --json title"
    assert recorded[2] == f"pr edit {_OPEN_PR_URL} --title ANSWERS REGRESS: {title}"
    assert recorded[3].startswith(f"pr comment {_OPEN_PR_URL} --body-file ")
    assert len(recorded) == 4
    assert "pr create" not in "\n".join(recorded)
    body = (tmp_path / "pr-body.md").read_text(encoding="utf-8")
    assert body.startswith("Regressed question ids: Q01, Q05\n")
    assert _REGRESS_CHECK_LINE in body


def test_an_open_new_model_regression_converts_the_pull_request_to_a_draft(
    tmp_path: Path,
) -> None:
    title = "data: add or identify acme/orbit (MODEL-113)"
    result = _run_open_pr_step(
        tmp_path, human="true", regressed="true", title=title,
    )

    assert result.returncode == 0, result.stderr
    recorded = _open_pr_calls(tmp_path)
    assert recorded[0] == f"pr ready --undo {_OPEN_PR_URL}"
    assert recorded[1] == f"pr view {_OPEN_PR_URL} --json title"
    assert recorded[2] == f"pr edit {_OPEN_PR_URL} --title ANSWERS REGRESS: {title}"
    assert recorded[3].startswith(f"pr comment {_OPEN_PR_URL} --body-file ")
    assert len(recorded) == 4
    assert "pr create" not in "\n".join(recorded)
    assert "--label" not in "\n".join(recorded)
    body = (tmp_path / "pr-body.md").read_text(encoding="utf-8")
    assert body.startswith("Regressed question ids: Q01, Q05\n")
    assert _REGRESS_CHECK_LINE in body


def test_an_open_regression_keeps_a_title_that_already_has_the_prefix(
    tmp_path: Path,
) -> None:
    title = "ANSWERS REGRESS: data: add or identify acme/orbit (MODEL-113)"
    result = _run_open_pr_step(
        tmp_path, human="true", regressed="true", title=title,
    )

    assert result.returncode == 0, result.stderr
    recorded = _open_pr_calls(tmp_path)
    assert recorded[0] == f"pr ready --undo {_OPEN_PR_URL}"
    assert recorded[1] == f"pr view {_OPEN_PR_URL} --json title"
    assert recorded[2].startswith(f"pr comment {_OPEN_PR_URL} --body-file ")
    assert len(recorded) == 3
    assert "pr edit" not in "\n".join(recorded)


def test_an_open_pull_request_that_did_not_regress_is_only_commented(
    tmp_path: Path,
) -> None:
    title = "ANSWERS REGRESS: data: refresh acme/orbit release evidence (MODEL-113)"
    result = _run_open_pr_step(
        tmp_path, human="false", regressed="false", title=title,
    )

    assert result.returncode == 0, result.stderr
    recorded = _open_pr_calls(tmp_path)
    assert recorded == [
        f"pr comment {_OPEN_PR_URL} --body-file {tmp_path / 'result.json'}",
    ]
    assert not (tmp_path / "pr-body.md").exists()


@pytest.mark.parametrize("fail", ["ready", "view", "edit", "comment"])
def test_an_open_regression_names_the_pull_request_when_gh_fails(
    tmp_path: Path, fail: str,
) -> None:
    title = "data: refresh acme/orbit release evidence (MODEL-113)"
    result = _run_open_pr_step(
        tmp_path, human="false", regressed="true", title=title, fail=fail,
    )

    assert result.returncode != 0
    assert (
        "::error::The signal branch is already pushed. "
        f"Updating {_OPEN_PR_URL} failed."
    ) in result.stdout
    recorded = "\n".join(_open_pr_calls(tmp_path))
    if fail == "comment":
        assert "pr comment" in recorded
    else:
        assert "pr comment" not in recorded


def test_hourly_workflow_keeps_github_credentials_out_of_the_signal_sender() -> None:
    workflow = (ROOT / ".github" / "private-writers" / "release-signals.yml").read_text(
        encoding="utf-8"
    )

    gate = (ROOT / ".github/workflows/release-signals-gate.yml").read_text()
    assert "cron: '17 * * * *'" in gate
    assert "MODELSPEC_DATA_DISPATCH_TOKEN" in gate
    assert "schedule:" not in workflow
    assert "MODELSPEC_SIGNALS_READ_KEY" in workflow
    assert "secrets.GITHUB_TOKEN" in workflow
    assert "python -I -m cli.modelspec.legacy verify --skip-absent-copies --json" in workflow
    assert "python -I -m scripts.accuracy --profile data-pr" in workflow
    assert "python -I -m scripts.recall_run" in workflow
    assert "new-model" in workflow
    assert "--draft" in workflow
    assert "gh pr merge" not in workflow
    assert "1, 7, and 30 day re-checks" in workflow
    assert "strategy:" in workflow
    assert "max-parallel: 4" in workflow
    assert "matrix: ${{ fromJSON(needs.pending.outputs.matrix) }}" in workflow
    assert "pr_url: (.pr_url // null)" in workflow
    assert 'gh pr view "$PR_URL" --json state,headRefName,headRepositoryOwner' in workflow
    assert "ref: ${{ steps.recheck.outputs.ref }}" in workflow
    assert "SIGNAL_ID: ${{ matrix.work.signal_id }}" in workflow
    assert "RECHECK_DAY: ${{ matrix.work.recheck_day }}" in workflow
    assert '--signal-id "$SIGNAL_ID"' in workflow
    assert '--recheck-day "$RECHECK_DAY"' in workflow
    assert '--closed-unmerged-pr "$PR_URL"' in workflow
    assert 'git push --set-upstream origin "HEAD:$branch"' in workflow
    assert 'gh pr comment "$EXISTING_PR_URL"' in workflow
    assert "Flag a new-model PR closed without merge" in workflow


@pytest.mark.parametrize("signals,rechecks,count", [([], [], 0), ([{}], [], 1), ([], [{}], 1), ([{}, {}], [{}], 3)])
def test_pending_gate_counts_valid_queues_and_dispatches_once(tmp_path, signals, rechecks, count):
    import os
    import subprocess

    import yaml

    workflow = yaml.safe_load((ROOT / ".github/workflows/release-signals-gate.yml").read_text())
    pending, dispatch = workflow["jobs"]["pending"]["steps"]
    assert workflow["jobs"]["pending"]["if"] == "vars.SIGNALS_ENABLED == 'true'"
    assert dispatch["if"] == "steps.pending.outputs.count != '0'"
    source = pending["run"][pending["run"].index("count=$(jq "):]
    (tmp_path / "pending.json").write_text(json.dumps({
        "schema_version": "2", "service_commit": "fixture", "endpoint": "signals.pending",
        "signals": signals, "rechecks": rechecks,
    }))
    output = tmp_path / "output"
    result = subprocess.run(
        ["bash", "-e", "-c", source], cwd=tmp_path, capture_output=True, text=True,
        env=os.environ | {"RUNNER_TEMP": str(tmp_path), "GITHUB_OUTPUT": str(output)},
    )
    assert result.returncode == 0, result.stderr
    assert output.read_text() == f"count={count}\n"
    assert not result.stdout and not result.stderr
    stub = 'gh() { printf "%s\\n" "$*" >> calls; }\n'
    dispatch_result = subprocess.run(
        ["bash", "-e", "-c", stub + '. "$GITHUB_OUTPUT"\nif [ "$count" != 0 ]; then\n' + dispatch["run"] + "fi\n"],
        cwd=tmp_path, capture_output=True, text=True,
        env=os.environ | {"GITHUB_OUTPUT": str(output), "GH_TOKEN": "offline-fixture"},
    )
    assert dispatch_result.returncode == 0, dispatch_result.stderr
    calls = tmp_path / "calls"
    if count:
        assert calls.read_text().splitlines() == ["workflow run release-signals.yml --repo turbobeest/modelspec-data --ref main"]
    else:
        assert not calls.exists()


def test_worker_endpoint_is_on_and_vendors_the_shared_contract() -> None:
    wrangler = (ROOT / "api" / "worker" / "wrangler.jsonc").read_text(encoding="utf-8")
    vendor = (ROOT / "api" / "worker" / "vendor.py").read_text(encoding="utf-8")
    entry = (ROOT / "api" / "worker" / "src" / "entry.py").read_text(encoding="utf-8")

    assert '"SIGNALS_ENABLED": "true"' in wrangler
    assert 'Path("release_signals/contract.py")' in vendor
    assert '"POST /v1/signals"' in entry
    assert '"GET /v1/signals/pending"' in entry


_MODELS_DEV = "https://models.dev/api.json"
_PRIMARY = "https://acme.example/models"


@pytest.mark.parametrize(
    ("broken_url", "body"),
    [
        (_MODELS_DEV, b""),
        (_MODELS_DEV, b"{"),
        (_MODELS_DEV, b"<html>upstream error</html>"),
        (_MODELS_DEV, b"\xff"),
        (_MODELS_DEV, b'{"unrelated":1}'),
        (_MODELS_DEV, b'{"acme":{"name":"Acme","models":[]}}'),
        (
            _PRIMARY,
            b'<script type="application/ld+json">'
            b'{"name":"Orbit 2","publisher":{"name":"Acme"},'
            b'"datePublished":"not-a-date"}</script>',
        ),
        (
            _PRIMARY,
            b'<script type="application/ld+json">'
            b'{"name":"Orbit 2","publisher":{"name":"Acme"},'
            b'"datePublished":"2026-09-26T00:30:00+02:00"}</script>',
        ),
        pytest.param(
            _MODELS_DEV,
            b'{"acme":' + b"1" * 5000 + b"}",
            id="five-thousand-digit-integer",
        ),
        pytest.param(
            _MODELS_DEV,
            b"[" * 200000,
            id="two-hundred-thousand-nested-brackets",
        ),
        pytest.param(_MODELS_DEV, b"[]", id="top-level-array"),
        pytest.param(_MODELS_DEV, b"null", id="top-level-null"),
    ],
)
def test_bad_required_source_exits_with_controlled_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    broken_url: str,
    body: bytes,
) -> None:
    card = tmp_path / "models" / "acme" / "orbit-2.md"
    card.parent.mkdir(parents=True)
    original = (
        "---\n"
        "model_id: acme/orbit-2\n"
        "display_name: Orbit 2\n"
        "provider: acme\n"
        "provider_display: Acme\n"
        "version: orbit-2\n"
        "---\n"
    )
    card.write_text(original)
    queued = {
        "model_name": "Orbit 2",
        "provider": "Acme",
        "first_seen_url": "https://x.com/acme/status/1",
        "timestamp": "2026-09-26T12:00:00Z",
        "confidence": 0.9,
        "signal_id": "audit-1",
    }
    pending = tmp_path / "pending.json"
    result_path = tmp_path / "result.json"
    pending.write_text(json.dumps({"signals": [queued]}))
    replies = {
        _MODELS_DEV: json.dumps({
            "acme": {
                "name": "Acme",
                "models": {
                    "orbit-2": {
                        "id": "orbit-2",
                        "name": "Orbit 2",
                        "release_url": _PRIMARY,
                    },
                },
            },
        }).encode(),
        _PRIMARY: b"<h1>Acme launches Orbit 2.</h1>",
    }
    replies[broken_url] = body

    def fetch(url: str) -> FetchResult:
        assert url in replies, f"unexpected fetch: {url}"
        content_type = "application/json" if url == _MODELS_DEV else "text/html"
        return FetchResult(url, replies[url], content_type)

    monkeypatch.setattr(processor, "_fetch", fetch)
    monkeypatch.setattr(sys, "argv", [
        "process_release_signals",
        "--root", str(tmp_path),
        "--pending", str(pending),
        "--result", str(result_path),
    ])

    assert processor.main() == 2
    output = capsys.readouterr()
    rendered = output.out + output.err
    assert broken_url in rendered
    assert "Traceback" not in rendered
    assert card.read_text() == original
    assert json.loads(pending.read_text()) == {"signals": [queued]}
    assert not result_path.exists()


def test_long_date_published_diagnostic_is_bounded(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    card = tmp_path / "models" / "acme" / "orbit-2.md"
    card.parent.mkdir(parents=True)
    original = (
        "---\n"
        "model_id: acme/orbit-2\n"
        "display_name: Orbit 2\n"
        "provider: acme\n"
        "provider_display: Acme\n"
        "version: orbit-2\n"
        "---\n"
    )
    card.write_text(original)
    queued = {
        "model_name": "Orbit 2",
        "provider": "Acme",
        "first_seen_url": "https://x.com/acme/status/1",
        "timestamp": "2026-09-26T12:00:00Z",
        "confidence": 0.9,
        "signal_id": "audit-1",
    }
    pending = tmp_path / "pending.json"
    result_path = tmp_path / "result.json"
    pending.write_text(json.dumps({"signals": [queued]}))
    published = "x" * 100000
    primary = (
        '<script type="application/ld+json">'
        '{"name":"Orbit 2","publisher":{"name":"Acme"},'
        f'"datePublished":"{published}"}}</script>'
    ).encode()
    replies = {
        _MODELS_DEV: json.dumps({
            "acme": {
                "name": "Acme",
                "models": {
                    "orbit-2": {
                        "id": "orbit-2",
                        "name": "Orbit 2",
                        "release_url": _PRIMARY,
                    },
                },
            },
        }).encode(),
        _PRIMARY: primary,
    }

    def fetch(url: str) -> FetchResult:
        assert url in replies, f"unexpected fetch: {url}"
        content_type = "application/json" if url == _MODELS_DEV else "text/html"
        return FetchResult(url, replies[url], content_type)

    def refuse_refresh(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("leaderboard refresh must not run")

    monkeypatch.setattr(processor, "_fetch", fetch)
    monkeypatch.setattr(processor.refresh_leaderboards, "run", refuse_refresh)
    monkeypatch.setattr(sys, "argv", [
        "process_release_signals",
        "--root", str(tmp_path),
        "--pending", str(pending),
        "--result", str(result_path),
    ])

    assert processor.main() == 2
    output = capsys.readouterr()
    rendered = output.out + output.err
    assert _PRIMARY in rendered
    assert len(rendered) < 600
    assert "\n" not in rendered.strip()
    assert "Traceback" not in rendered
    assert card.read_text() == original
    assert json.loads(pending.read_text()) == {"signals": [queued]}
    assert not result_path.exists()


def test_prohibited_release_url_stays_a_value_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    assert not issubclass(RequiredSourceError, ValueError)
    card = tmp_path / "models" / "acme" / "orbit-2.md"
    card.parent.mkdir(parents=True)
    original = (
        "---\n"
        "model_id: acme/orbit-2\n"
        "display_name: Orbit 2\n"
        "provider: acme\n"
        "provider_display: Acme\n"
        "version: orbit-2\n"
        "---\n"
    )
    card.write_text(original)
    queued = {
        "model_name": "Orbit 2",
        "provider": "Acme",
        "first_seen_url": "https://x.com/acme/status/1",
        "timestamp": "2026-09-26T12:00:00Z",
        "confidence": 0.9,
        "signal_id": "audit-1",
    }
    pending = tmp_path / "pending.json"
    result_path = tmp_path / "result.json"
    pending_text = json.dumps({"signals": [queued]})
    pending.write_text(pending_text)
    prohibited = "https://" + "artificial" + "analysis.ai" + "/orbit-2"
    replies = {
        _MODELS_DEV: json.dumps({
            "acme": {
                "name": "Acme",
                "models": {
                    "orbit-2": {
                        "id": "orbit-2",
                        "name": "Orbit 2",
                        "release_url": prohibited,
                    },
                },
            },
        }).encode(),
    }

    def fetch(url: str) -> FetchResult:
        assert url in replies, f"unexpected fetch: {url}"
        return FetchResult(url, replies[url], "application/json")

    def refuse_refresh(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("leaderboard refresh must not run")

    monkeypatch.setattr(processor, "_fetch", fetch)
    monkeypatch.setattr(processor.refresh_leaderboards, "run", refuse_refresh)
    monkeypatch.setattr(sys, "argv", [
        "process_release_signals",
        "--root", str(tmp_path),
        "--pending", str(pending),
        "--result", str(result_path),
    ])

    with pytest.raises(ValueError, match="excluded source") as caught:
        processor.main()
    assert not isinstance(caught.value, RequiredSourceError)
    assert card.read_text() == original
    assert pending.read_text() == pending_text
    assert not result_path.exists()


def test_required_source_diagnostic_is_on_stderr(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    card = tmp_path / "models" / "acme" / "orbit-2.md"
    card.parent.mkdir(parents=True)
    card.write_text(
        "---\n"
        "model_id: acme/orbit-2\n"
        "display_name: Orbit 2\n"
        "provider: acme\n"
        "provider_display: Acme\n"
        "version: orbit-2\n"
        "---\n"
    )
    pending = tmp_path / "pending.json"
    pending.write_text(json.dumps({"signals": [{
        "model_name": "Orbit 2",
        "provider": "Acme",
        "first_seen_url": "https://x.com/acme/status/1",
        "timestamp": "2026-09-26T12:00:00Z",
        "confidence": 0.9,
        "signal_id": "audit-1",
    }]}))

    def fetch(url: str) -> FetchResult:
        assert url == _MODELS_DEV, f"unexpected fetch: {url}"
        return FetchResult(url, b"", "application/json")

    monkeypatch.setattr(processor, "_fetch", fetch)
    monkeypatch.setattr(sys, "argv", [
        "process_release_signals",
        "--root", str(tmp_path),
        "--pending", str(pending),
        "--result", str(tmp_path / "result.json"),
    ])

    assert processor.main() == 2
    output = capsys.readouterr()
    assert _MODELS_DEV in output.err
    assert "required source" in output.err
    assert "required source" not in output.out
    assert _MODELS_DEV not in output.out


@pytest.mark.parametrize(
    "filler",
    [
        pytest.param(None, id="null"),
        pytest.param(0, id="zero"),
        pytest.param("", id="empty-string"),
        pytest.param([], id="empty-list"),
    ],
)
def test_falsy_provider_row_is_an_empty_row(filler: object) -> None:
    _provider_id, listing, _provider_doc = _models_dev_listing(
        {
            "zzz": filler,
            "acme": {
                "name": "Elsewhere",
                "models": {"orbit-2": {"id": "orbit-2", "name": "Orbit 2"}},
            },
        },
        "Acme",
        "Orbit 2",
        source_url=_MODELS_DEV,
    )
    assert listing["name"] == "Orbit 2"


@pytest.mark.parametrize(
    "filler",
    [
        pytest.param(None, id="null"),
        pytest.param(0, id="zero"),
        pytest.param("", id="empty-string"),
        pytest.param([], id="empty-list"),
    ],
)
def test_falsy_matching_provider_row_has_no_models_map(filler: object) -> None:
    with pytest.raises(RequiredSourceError, match="provider row has no models map"):
        _models_dev_listing(
            {"acme": filler},
            "Acme",
            "Orbit 2",
            source_url=_MODELS_DEV,
        )


def test_provider_matches_by_key_alone() -> None:
    provider_id, listing, _provider_doc = _models_dev_listing(
        {"acme": {"models": {"orbit-2": {"id": "orbit-2", "name": "Orbit 2"}}}},
        "Acme",
        "Orbit 2",
        source_url=_MODELS_DEV,
    )
    assert provider_id == "acme"
    assert listing["id"] == "orbit-2"


def test_provider_matches_by_name_alone() -> None:
    provider_id, listing, _provider_doc = _models_dev_listing(
        {
            "labs": {
                "name": "Acme",
                "models": {"orbit-2": {"id": "orbit-2", "name": "Orbit 2"}},
            },
        },
        "Acme",
        "Orbit 2",
        source_url=_MODELS_DEV,
    )
    assert provider_id == "labs"
    assert listing["id"] == "orbit-2"


def test_required_source_error_bounds_the_built_message() -> None:
    url = _PRIMARY
    long_detail = "x" * 100000 + "\nsecond line"
    long_error = RequiredSourceError(url, long_detail)
    long_text = str(long_error)
    assert len(long_text) <= 500
    assert long_text.startswith(f"required source {url} failed: ")
    assert "\n" not in long_text
    assert "\r" not in long_text
    assert long_detail[:4] in long_text

    short_detail = "kept whole\nsecond line"
    short_text = str(RequiredSourceError(url, short_detail))
    assert short_text == f"required source {url} failed: kept whole second line"
    assert "\n" not in short_text
    assert "\r" not in short_text


def test_required_source_error_bounds_a_long_url() -> None:
    url = ("h" * 300) + "Z" + ("h" * 99699)
    error = RequiredSourceError(url, "detail")
    rendered = str(error)
    flat = url.replace("\r", " ").replace("\n", " ")
    assert error.url == url
    assert len(rendered) <= 500
    assert "\n" not in rendered
    assert "\r" not in rendered
    assert rendered.startswith("required source " + flat[:300] + "...")
    assert "Z" not in rendered


def test_required_source_error_flattens_a_url_line_break() -> None:
    url = "https://acme.example/a\r\nb"
    error = RequiredSourceError(url, "detail")
    rendered = str(error)
    flat = url.replace("\r", " ").replace("\n", " ")
    assert error.url == url
    assert len(rendered) <= 500
    assert "\n" not in rendered
    assert "\r" not in rendered
    assert rendered.startswith("required source " + flat[:300])
    assert rendered.startswith(f"required source {flat} failed: ")


def test_required_source_error_keeps_a_short_url_message() -> None:
    url = _PRIMARY
    detail = "models.dev returned no provider map"
    error = RequiredSourceError(url, detail)
    assert error.url == url
    assert str(error) == f"required source {url} failed: {detail}"


_HOMEPAGE = "https://acme.example/models/orbit-1"
_HF_ORBIT_1 = "https://huggingface.co/api/models?search=Orbit+1&limit=20"
_MALFORMED_RELEASE_URLS = [
    pytest.param("/orbit/notes", id="relative-path"),
    pytest.param("javascript:alert(1)", id="javascript"),
    pytest.param("https:///orbit", id="no-host"),
    pytest.param({"href": "https://acme.example/not-a-string"}, id="non-string"),
    pytest.param("q" * 100000, id="hundred-thousand-characters"),
    pytest.param("https://[::1", id="unclosed-ipv6"),
    pytest.param("https://[x]/", id="invalid-ipv6"),
    pytest.param("http://acme.example/orbit", id="http-not-https"),
]


def _listing_payload(release_url: object, *, homepage: str | None) -> dict:
    listing: dict[str, object] = {
        "id": "orbit-1", "name": "Orbit 1", "release_url": release_url,
    }
    if homepage is not None:
        listing["homepage"] = homepage
    return {
        "acme": {
            "name": "Acme",
            "models": {
                "orbit-1": listing,
                "orbit-9": {
                    "id": "orbit-9",
                    "name": "Orbit 9",
                    "release_url": "q" * 100000,
                },
            },
        }
    }


@pytest.mark.parametrize("release_url", _MALFORMED_RELEASE_URLS)
def test_malformed_release_url_is_not_a_primary_source(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, release_url: object,
) -> None:
    _write_card(tmp_path, "acme", "orbit-1", display="Orbit 1", version="orbit-1")
    pending = tmp_path / "pending.json"
    result_path = tmp_path / "result.json"
    pending.write_text(json.dumps({"signals": [signal(model_name="Orbit 1")]}))
    payload = _listing_payload(release_url, homepage=_HOMEPAGE)
    replies = {
        _MODELS_DEV: FetchResult(
            _MODELS_DEV, json.dumps(payload).encode(), "application/json",
        ),
        _HOMEPAGE: FetchResult(
            _HOMEPAGE, b"<html><body>Acme releases Orbit 1.</body></html>", "text/html",
        ),
        _HF_ORBIT_1: FetchResult(_HF_ORBIT_1, b"[]", "application/json"),
    }
    requested: list[str] = []

    def fetch(url: str) -> FetchResult:
        requested.append(url)
        assert url in replies, url
        return replies[url]

    def run_refresh(**_kwargs: object):
        return processor.refresh_leaderboards.RefreshReport()

    monkeypatch.setattr(processor, "_fetch", fetch)
    monkeypatch.setattr(processor.refresh_leaderboards, "run", run_refresh)
    monkeypatch.setattr(sys, "argv", [
        "process_release_signals",
        "--root", str(tmp_path),
        "--pending", str(pending),
        "--result", str(result_path),
    ])

    assert processor.main() == 0
    result = json.loads(result_path.read_text(encoding="utf-8"))
    assert result["status"] == "existing"
    assert result["sources"][0] == _HOMEPAGE
    assert release_url not in requested
    assert _HOMEPAGE in requested


@pytest.mark.parametrize("release_url", _MALFORMED_RELEASE_URLS)
def test_malformed_release_url_matches_a_missing_field(
    tmp_path: Path, release_url: object,
) -> None:
    _write_card(tmp_path, "acme", "orbit-1", display="Orbit 1", version="orbit-1")
    present = {
        "acme": {
            "name": "Acme",
            "models": {
                "orbit-2": {"id": "orbit-2", "name": "Orbit 2", "release_url": release_url},
            },
        }
    }
    absent = {
        "acme": {
            "name": "Acme",
            "models": {"orbit-2": {"id": "orbit-2", "name": "Orbit 2"}},
        }
    }

    def fetch_for(body: dict):
        encoded = json.dumps(body).encode()

        def fetch(url: str) -> FetchResult:
            assert url == _MODELS_DEV, url
            return FetchResult(url, encoded, "application/json")

        return fetch

    with pytest.raises(ValueError, match="does not name a primary provider source") as bad:
        draft_signal(
            ReleaseSignal.parse(signal()), root=tmp_path, fetch=fetch_for(present),
            read_date=date(2026, 9, 26),
        )
    with pytest.raises(ValueError, match="does not name a primary provider source") as gone:
        draft_signal(
            ReleaseSignal.parse(signal()), root=tmp_path, fetch=fetch_for(absent),
            read_date=date(2026, 9, 26),
        )
    assert str(bad.value) == str(gone.value)


def _hostile_json_ld_page(payload: str) -> bytes:
    readable = (
        '<script type="application/ld+json">'
        '{"name":"Orbit 2","publisher":{"name":"Acme"},'
        '"datePublished":"2026-09-26"}</script>'
    )
    return (
        '<script type="application/ld+json">' + payload + "</script>"
        + readable
        + "<h1>Acme launches Orbit 2.</h1>"
    ).encode()


def _release_date(result: DraftResult) -> str:
    assert result.card_path is not None
    front = yaml.safe_load(result.card_path.read_text(encoding="utf-8").split("---", 2)[1])
    return str(front["release_date"])


def test_json_ld_with_a_long_integer_is_skipped(tmp_path: Path) -> None:
    payload = (
        '{"name":"Orbit 2","publisher":{"name":"Acme"},'
        '"datePublished":"2026-01-15","n":' + ("9" * 5000) + "}"
    )
    result = _draft_visible_signal(tmp_path, _hostile_json_ld_page(payload))
    assert result.resolution.status == "new"
    assert _release_date(result) == "2026-09-26"


def test_json_ld_nested_past_the_depth_bound_is_skipped(tmp_path: Path) -> None:
    nested = '{"a":' * 2000 + "1" + "}" * 2000
    payload = (
        '{"name":"Orbit 2","publisher":{"name":"Acme"},'
        '"datePublished":"2026-01-15","extra":' + nested + "}"
    )
    result = _draft_visible_signal(tmp_path, _hostile_json_ld_page(payload))
    assert result.resolution.status == "new"
    assert _release_date(result) == "2026-09-26"


def _json_ld_page(payload: str) -> bytes:
    return (
        '<script type="application/ld+json">' + payload + "</script>"
        "<h1>Acme launches Orbit 2.</h1>"
    ).encode()


def _json_ld_documents(page: bytes) -> list[dict]:
    parser = _JsonLd()
    parser.feed(page.decode())
    return parser.documents


def _identity_json(depth: int, published: str) -> str:
    extra = '{"k":' * (depth - 1) + "1" + "}" * (depth - 1)
    return (
        '{"name":"Orbit 2","publisher":{"name":"Acme"},'
        f'"datePublished":"{published}","extra":{extra}}}'
    )


def test_json_ld_list_of_seventy_siblings_is_read(tmp_path: Path) -> None:
    rows = [{"name": f"Sibling {index}"} for index in range(69)]
    rows.append({
        "name": "Orbit 2",
        "publisher": {"name": "Acme"},
        "datePublished": "2026-03-03",
    })
    page = _json_ld_page(json.dumps(rows, separators=(",", ":")))
    documents = _json_ld_documents(page)
    names = [row["name"] for row in documents]
    assert names == [f"Sibling {index}" for index in range(69)] + ["Orbit 2"]
    result = _draft_visible_signal(tmp_path, page)
    assert result.resolution.status == "new"
    assert _release_date(result) == "2026-03-03"


def test_json_ld_graph_of_seventy_objects_is_read(tmp_path: Path) -> None:
    payload = json.dumps({
        "name": "Orbit 2",
        "publisher": {"name": "Acme"},
        "datePublished": "2026-03-04",
        "@graph": [{"name": f"Node {index}"} for index in range(70)],
    }, separators=(",", ":"))
    page = _json_ld_page(payload)
    documents = _json_ld_documents(page)
    assert len(documents) == 1
    assert [row["name"] for row in documents[0]["@graph"]] == [
        f"Node {index}" for index in range(70)
    ]
    result = _draft_visible_signal(tmp_path, page)
    assert result.resolution.status == "new"
    assert _release_date(result) == "2026-03-04"


def test_json_ld_nested_at_the_depth_bound_is_read(tmp_path: Path) -> None:
    assert _JSON_LD_MAX_DEPTH == 64
    page = _json_ld_page(_identity_json(_JSON_LD_MAX_DEPTH, "2026-04-04"))
    documents = _json_ld_documents(page)
    assert len(documents) == 1
    assert documents[0]["datePublished"] == "2026-04-04"
    result = _draft_visible_signal(tmp_path, page)
    assert result.resolution.status == "new"
    assert _release_date(result) == "2026-04-04"


def test_json_ld_one_level_past_the_depth_bound_is_skipped(tmp_path: Path) -> None:
    payload = _identity_json(_JSON_LD_MAX_DEPTH + 1, "2026-01-15")
    result = _draft_visible_signal(tmp_path, _hostile_json_ld_page(payload))
    assert result.resolution.status == "new"
    assert _release_date(result) == "2026-09-26"


@pytest.mark.parametrize("width", [2000, 5000])
def test_json_ld_integer_longer_than_the_digit_bound_is_skipped(
    tmp_path: Path, width: int,
) -> None:
    payload = (
        '{"name":"Orbit 2","publisher":{"name":"Acme"},'
        '"datePublished":"2026-01-15","n":' + ("9" * width) + "}"
    )
    result = _draft_visible_signal(tmp_path, _hostile_json_ld_page(payload))
    assert result.resolution.status == "new"
    assert _release_date(result) == "2026-09-26"


def test_json_ld_two_thousand_level_nest_is_skipped(tmp_path: Path) -> None:
    nested = '{"a":' * 2000 + "1" + "}" * 2000
    payload = (
        '{"name":"Orbit 2","publisher":{"name":"Acme"},'
        '"datePublished":"2026-01-15","extra":' + nested + "}"
    )
    result = _draft_visible_signal(tmp_path, _hostile_json_ld_page(payload))
    assert result.resolution.status == "new"
    assert _release_date(result) == "2026-09-26"


class _PriceFetcher:
    credits_spent = 0


def _watch_lab(root: Path, host: str) -> None:
    registry = root / "registry"
    registry.mkdir(parents=True, exist_ok=True)
    (registry / "release-watch.yaml").write_text(
        "sources:\n"
        "- id: acme-models\n"
        "  kind: page\n"
        f"  url: https://{host}/models\n"
        "  provider: acme\n"
        "  pattern: orbit\n"
        "  confidence: 0.9\n",
        encoding="utf-8",
    )


def _empty_models_dev() -> dict[str, FetchResult]:
    url = "https://models.dev/api.json"
    return {
        url: FetchResult(
            url,
            json.dumps({"acme": {"name": "Acme", "models": {}}}).encode(),
            "application/json",
        ),
    }


def test_a_lab_host_matches_exactly_or_a_registered_wildcard() -> None:
    from release_signals.pipeline import first_seen_host_class

    community = "https://community.openai.com/topic"
    platform = "https://platform.openai.com/docs"
    docs = "https://docs.platform.openai.com/docs"
    assert first_seen_host_class(community, frozenset({"platform.openai.com"})) == "unregistered"
    assert first_seen_host_class(community, frozenset({"openai.com"})) == "unregistered"
    assert first_seen_host_class(platform, frozenset({"platform.openai.com"})) == "lab"
    assert first_seen_host_class(
        "https://www.platform.openai.com/docs", frozenset({"platform.openai.com"}),
    ) == "lab"
    assert first_seen_host_class(docs, frozenset({"platform.openai.com"})) == "unregistered"
    assert first_seen_host_class(docs, frozenset({"*.platform.openai.com"})) == "lab"
    assert first_seen_host_class(community, frozenset({"*.openai.com"})) == "lab"


def test_a_display_provider_uses_the_resolved_lab_hosts(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    card = tmp_path / "models" / "mistral" / "small.md"
    card.parent.mkdir(parents=True)
    card.write_text(
        "---\n"
        "model_id: mistral/small\n"
        "display_name: Mistral Small\n"
        "provider: mistral\n"
        "provider_display: Mistral AI\n"
        "version: small\n"
        "---\n",
        encoding="utf-8",
    )
    page = "https://mistral.ai/news/new-chat"
    pending = tmp_path / "pending.json"
    result_path = tmp_path / "result.json"
    pending.write_text(json.dumps({"signals": [signal(
        model_name="New Chat",
        provider="Mistral AI",
        signal_id="watch:mistral:new-chat",
        first_seen_url=page,
    )]}))
    models_dev = "https://models.dev/api.json"
    replies = {
        models_dev: FetchResult(models_dev, b"{}", "application/json"),
        page: FetchResult(page, b"<h1>Mistral AI launches New Chat.</h1>", "text/html"),
    }
    seen: list[str] = []

    def fetch(url: str) -> FetchResult:
        seen.append(url)
        if url in replies:
            return replies[url]
        if url.startswith("https://huggingface.co/"):
            return FetchResult(url, b"[]", "application/json")
        raise AssertionError(url)

    monkeypatch.setattr(processor, "_fetch", fetch)
    monkeypatch.setattr(
        processor.refresh_leaderboards, "run",
        lambda **_: processor.refresh_leaderboards.RefreshReport(),
    )

    result = processor.process(
        pending, result_path, root=tmp_path, price_fetcher=_PriceFetcher(),
    )

    assert result["status"] == "new"
    assert result["model_id"] == "mistral/new-chat"
    assert page in seen
    assert (tmp_path / "models" / "mistral" / "new-chat.md").is_file()


def test_zero_models_dev_rows_are_not_listed_and_several_stay_uncertain() -> None:
    with pytest.raises(ModelsDevNotListed):
        _models_dev_listing(
            {"other": {"name": "Other", "models": {"x": {"name": "X"}}}},
            "Acme", "Orbit 9", source_url="https://models.dev/api.json",
        )
    with pytest.raises(ModelsDevNotListed):
        _models_dev_listing(
            {"acme": {"name": "Acme", "models": {}}},
            "Acme", "Orbit 9", source_url="https://models.dev/api.json",
        )
    with pytest.raises(IdentityUncertainError, match="exactly one model"):
        _models_dev_listing(
            {"acme": {"name": "Acme", "models": {
                "a": {"id": "a", "name": "Orbit 9"},
                "b": {"id": "b", "name": "Orbit 9"},
            }}},
            "Acme", "Orbit 9", source_url="https://models.dev/api.json",
        )


def test_not_listed_uses_a_registered_lab_page_and_names_other_host_classes(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    from urllib.parse import urlencode

    from decision.retention import cite_only_hosts

    _write_card(tmp_path, "acme", "orbit-1", display="Orbit 1", version="orbit-1")
    host = "models.acme.example"
    _watch_lab(tmp_path, host)
    primary = f"https://{host}/orbit-9"
    pending = tmp_path / "pending.json"
    result_path = tmp_path / "result.json"
    queued = signal(
        model_name="Orbit 9",
        signal_id="watch:acme:orbit-9",
        first_seen_url=primary,
    )
    pending.write_text(json.dumps({"signals": [queued]}))
    search = "https://huggingface.co/api/models?" + urlencode({"search": "Orbit 9", "limit": 20})
    replies = _empty_models_dev()
    replies[primary] = FetchResult(primary, b"<h1>Acme launches Orbit 9.</h1>", "text/html")
    replies[search] = FetchResult(search, b"[]", "application/json")
    requested: list[str] = []

    def fetch(url: str) -> FetchResult:
        requested.append(url)
        return replies[url]

    monkeypatch.setattr(processor, "_fetch", fetch)
    monkeypatch.setattr(
        processor.refresh_leaderboards, "run",
        lambda **_: processor.refresh_leaderboards.RefreshReport(),
    )

    result = processor.process(
        pending, result_path, root=tmp_path, price_fetcher=_PriceFetcher(),
    )

    assert result["status"] == "new"
    assert result["model_id"] == "acme/orbit-9"
    card = tmp_path / "models" / "acme" / "orbit-9.md"
    assert card.is_file()
    assert primary in card.read_text(encoding="utf-8")
    assert "https://models.dev/api.json" in requested
    assert primary in requested
    assert result["models_dev"] == "not_listed"
    assert result["primary_host"] == host
    assert all("models.dev" not in url for url in result["sources"])
    drafted_front = yaml.safe_load(card.read_text(encoding="utf-8").split("---", 2)[1])
    assert "last_scraped_models_dev" not in drafted_front["sources"]
    assert "https://models.dev" not in card.read_text(encoding="utf-8")

    def run_blocked(row: dict[str, object], forbidden: str) -> dict:
        drafted = tmp_path / "models" / "acme" / "orbit-9.md"
        if drafted.exists():
            drafted.unlink()
        blocked_pending = tmp_path / "blocked.json"
        blocked_result = tmp_path / "blocked-result.json"
        blocked_pending.write_text(json.dumps({"signals": [row]}))
        seen: list[str] = []

        def blocked_fetch(url: str) -> FetchResult:
            seen.append(url)
            if forbidden in url:
                raise AssertionError(f"fetched a refused host: {url}")
            return _empty_models_dev()["https://models.dev/api.json"]

        monkeypatch.setattr(processor, "_fetch", blocked_fetch)
        outcome = processor.process(
            blocked_pending, blocked_result, root=tmp_path, price_fetcher=_PriceFetcher(),
        )
        assert all(forbidden not in url for url in seen)
        assert not drafted.exists()
        return outcome

    tweet = run_blocked(signal(model_name="Orbit 9", signal_id="grok-orbit-9"), "x.com")
    assert tweet["status"] == "uncertain"
    assert tweet["model_id"] is None
    assert "host class signal-only" in tweet["reason"]

    outsider = run_blocked(signal(
        model_name="Orbit 9",
        signal_id="watch:acme:news",
        first_seen_url="https://news.example/orbit-9",
    ), "https://news.example/orbit-9")
    assert outsider["status"] == "uncertain"
    assert "host class unregistered" in outsider["reason"]

    excluded_host = sorted(REMOVED_HOSTS)[0]
    lab_page = f"https://{host}/orbit-excluded"
    excluded_card = tmp_path / "models" / "acme" / "orbit-9.md"
    if excluded_card.exists():
        excluded_card.unlink()
    excluded_pending = tmp_path / "excluded.json"
    excluded_result = tmp_path / "excluded-result.json"
    excluded_pending.write_text(json.dumps({"signals": [signal(
        model_name="Orbit 9",
        signal_id="watch:acme:excluded",
        first_seen_url=lab_page,
    )]}))
    excluded_seen: list[str] = []

    def excluded_fetch(url: str) -> FetchResult:
        excluded_seen.append(url)
        if excluded_host in url:
            raise AssertionError(f"fetched a refused host: {url}")
        if url == lab_page:
            return FetchResult(
                f"https://{excluded_host}/orbit-9",
                b"<h1>Acme launches Orbit 9.</h1>",
                "text/html",
            )
        return _empty_models_dev()["https://models.dev/api.json"]

    monkeypatch.setattr(processor, "_fetch", excluded_fetch)
    excluded = processor.process(
        excluded_pending, excluded_result, root=tmp_path, price_fetcher=_PriceFetcher(),
    )
    assert all(excluded_host not in url for url in excluded_seen)
    assert not excluded_card.exists()
    assert excluded["status"] == "uncertain"
    assert "host class excluded" in excluded["reason"]

    cite_host = cite_only_hosts()[0]
    cited = run_blocked(signal(
        model_name="Orbit 9",
        signal_id="watch:acme:cited",
        first_seen_url=f"https://{cite_host}/orbit-9",
    ), f"https://{cite_host}/orbit-9")
    assert cited["status"] == "uncertain"
    assert "host class cite-only" in cited["reason"]


def test_several_models_dev_listings_are_not_guessed(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    _write_card(tmp_path, "acme", "orbit-1", display="Orbit 1", version="orbit-1")
    pending = tmp_path / "pending.json"
    result_path = tmp_path / "result.json"
    pending.write_text(json.dumps({"signals": [signal(model_name="Orbit 9")]}))
    payload = {"acme": {"name": "Acme", "models": {
        "a": {"id": "a", "name": "Orbit 9", "release_url": "https://models.acme.example/a"},
        "b": {"id": "b", "name": "Orbit 9", "release_url": "https://models.acme.example/b"},
    }}}
    models_dev_url = "https://models.dev/api.json"
    monkeypatch.setattr(processor, "_fetch", lambda url: FetchResult(
        url, json.dumps(payload).encode(), "application/json",
    ))

    result = processor.process(pending, result_path, root=tmp_path)

    assert result["status"] == "uncertain"
    assert result["model_id"] is None
    assert "exactly one" in result["reason"]
    assert not (tmp_path / "models" / "acme" / "orbit-9.md").exists()


def test_existing_card_stays_existing_when_models_dev_does_not_list_it(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    card = _write_card(tmp_path, "acme", "orbit-1", display="Orbit 1", version="orbit-1")
    before = card.read_bytes()
    pending = tmp_path / "pending.json"
    result_path = tmp_path / "result.json"
    pending.write_text(json.dumps({"signals": [signal(model_name="Orbit 1")]}))
    monkeypatch.setattr(
        processor, "_fetch", lambda url: _empty_models_dev()["https://models.dev/api.json"],
    )
    refreshed: dict[str, object] = {}

    def run_refresh(**kwargs: object):
        refreshed.update(kwargs)
        return processor.refresh_leaderboards.RefreshReport()

    monkeypatch.setattr(processor.refresh_leaderboards, "run", run_refresh)

    result = processor.process(pending, result_path, root=tmp_path)

    assert result["status"] == "existing"
    assert result["model_id"] == "acme/orbit-1"
    assert "not_listed" in result["identity_error"]
    assert card.read_bytes() == before
    assert refreshed["model_ids"] == ("acme/orbit-1",)


def test_a_dotted_successor_stays_new_when_only_the_predecessor_is_carded(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    card = _write_card(tmp_path, "acme", "orbit-6", display="Orbit 6", version="orbit-6")
    before = card.read_bytes()
    found = resolve_signal(
        ReleaseSignal.parse(signal(model_name="Orbit 6.1")), tmp_path,
    )

    assert found.status == "new"
    assert found.model_id == "acme/orbit-6-1"
    assert found.candidates == ()

    pending = tmp_path / "pending.json"
    result_path = tmp_path / "result.json"
    pending.write_text(json.dumps({"signals": [signal(model_name="Orbit 6.1")]}))
    monkeypatch.setattr(
        processor, "_fetch",
        lambda url: _empty_models_dev()["https://models.dev/api.json"],
    )

    result = processor.process(pending, result_path, root=tmp_path)

    assert result.get("model_id") != "acme/orbit-6"
    assert result["status"] != "existing"
    assert "suffix_stripped" not in result
    assert card.read_bytes() == before
    assert not (tmp_path / "models" / "acme" / "orbit-6-1.md").exists()


def test_a_suffixed_name_that_is_itself_a_card_resolves_to_that_card(tmp_path: Path) -> None:
    _write_card(tmp_path, "acme", "orbit-1", display="Orbit 1", version="orbit-1")
    _write_card(tmp_path, "acme", "orbit-1-1", display="Orbit 1.1", version="orbit-1.1")

    found = resolve_signal(
        ReleaseSignal.parse(signal(model_name="Orbit 1.1")), tmp_path,
    )

    assert (found.status, found.model_id) == ("existing", "acme/orbit-1-1")


def test_a_dotted_name_does_not_attach_to_unsuffixed_cards(tmp_path: Path) -> None:
    _write_card(tmp_path, "acme", "shared-a", display="Shared", version="shared")
    _write_card(tmp_path, "acme", "shared-b", display="Shared", version="shared")

    found = resolve_signal(
        ReleaseSignal.parse(signal(model_name="Shared.1")), tmp_path,
    )

    assert found.status == "new"
    assert found.model_id == "acme/shared-1"
    assert found.candidates == ()


def test_existing_card_stays_existing_when_the_source_refresh_misses_the_lab(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    card = _write_card(tmp_path, "acme", "orbit-1", display="Orbit 1", version="orbit-1")
    before = card.read_bytes()
    pending = tmp_path / "pending.json"
    result_path = tmp_path / "result.json"
    pending.write_text(json.dumps({"signals": [signal(model_name="Orbit 1")]}))
    models_dev_url = "https://models.dev/api.json"
    primary_url = "https://acme.example/models/orbit-1"
    payload = {
        "acme": {
            "name": "Acme",
            "models": {
                "orbit-1": {
                    "id": "orbit-1", "name": "Orbit 1", "release_url": primary_url,
                },
            },
        },
    }
    replies = {
        models_dev_url: FetchResult(
            models_dev_url, json.dumps(payload).encode(), "application/json",
        ),
        primary_url: FetchResult(
            primary_url, b"<p>Orbit 1 by Other Lab.</p>", "text/html",
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
    assert result["model_id"] == "acme/orbit-1"
    assert result["identity_error"] == "the primary source does not identify the stated lab"
    assert card.read_bytes() == before
    assert refreshed["model_ids"] == ("acme/orbit-1",)
    assert json.loads(result_path.read_text(encoding="utf-8"))["status"] == "existing"


def test_json_ld_brackets_inside_strings_do_not_change_depth(tmp_path: Path) -> None:
    note = 'quote \\" then ' + ("{[" * 80) + ("}]" * 80)
    payload = json.dumps({
        "name": "Orbit 2",
        "publisher": {"name": "Acme"},
        "datePublished": "2026-05-05",
        "note": note,
    }, separators=(",", ":"))
    page = _json_ld_page(payload)
    documents = _json_ld_documents(page)
    assert len(documents) == 1
    assert documents[0]["note"] == note
    result = _draft_visible_signal(tmp_path, page)
    assert result.resolution.status == "new"
    assert _release_date(result) == "2026-05-05"


def test_a_registered_lab_page_that_names_the_model_identifies_the_lab(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    from urllib.parse import urlencode

    bare = FetchResult(
        "https://models.acme.example/orbit-9", b"<h1>Orbit 9</h1>", "text/html",
    )
    with pytest.raises(IdentityUncertainError, match="stated lab"):
        _primary_identity(bare, "Orbit 9", "Acme")
    assert _primary_identity(
        bare, "Orbit 9", "Acme", lab_hosts=frozenset({"models.acme.example"}),
    ) == ("Orbit 9", "", "page-text")
    credited = FetchResult(
        "https://models.acme.example/orbit-9",
        b"<p>Orbit 9 by Other Lab.</p>",
        "text/html",
    )
    with pytest.raises(IdentityUncertainError, match="stated lab"):
        _primary_identity(
            credited, "Orbit 9", "Acme", lab_hosts=frozenset({"models.acme.example"}),
        )
    wrong_publisher = FetchResult(
        "https://models.acme.example/orbit-9",
        b'<script type="application/ld+json">'
        b'{"name":"Orbit 9","publisher":{"name":"Other Lab"}}'
        b"</script><h1>Orbit 9</h1>",
        "text/html",
    )
    with pytest.raises(IdentityUncertainError, match="stated lab"):
        _primary_identity(
            wrong_publisher, "Orbit 9", "Acme",
            lab_hosts=frozenset({"models.acme.example"}),
        )

    _write_card(tmp_path, "acme", "orbit-1", display="Orbit 1", version="orbit-1")
    host = "models.acme.example"
    _watch_lab(tmp_path, host)
    primary = f"https://{host}/orbit-9"
    pending = tmp_path / "pending.json"
    result_path = tmp_path / "result.json"
    pending.write_text(json.dumps({"signals": [signal(
        model_name="Orbit 9",
        signal_id="watch:acme:orbit-9",
        first_seen_url=primary,
    )]}))
    search = "https://huggingface.co/api/models?" + urlencode({"search": "Orbit 9", "limit": 20})
    replies = _empty_models_dev()
    replies[primary] = FetchResult(primary, b"<h1>Orbit 9</h1>", "text/html")
    replies[search] = FetchResult(search, b"[]", "application/json")
    monkeypatch.setattr(processor, "_fetch", lambda url: replies[url])
    monkeypatch.setattr(
        processor.refresh_leaderboards, "run",
        lambda **_: processor.refresh_leaderboards.RefreshReport(),
    )

    result = processor.process(
        pending, result_path, root=tmp_path, price_fetcher=_PriceFetcher(),
    )

    assert result["status"] == "new"
    assert result["model_id"] == "acme/orbit-9"
    assert primary in (tmp_path / "models" / "acme" / "orbit-9.md").read_text(encoding="utf-8")


def test_a_test_signal_is_ignored_and_writes_no_catalogue_files(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    _write_card(tmp_path, "acme", "orbit-1", display="Orbit 1", version="orbit-1")
    before = (tmp_path / "models" / "acme" / "orbit-1.md").read_bytes()
    pending = tmp_path / "pending.json"
    result_path = tmp_path / "result.json"
    audit_path = tmp_path / "audit.json"
    pending.write_text(json.dumps({"signals": [signal(
        model_name="acme-embodied-walker",
        signal_id="test-orbit-9",
    )]}))
    fetched: list[str] = []

    def fetch(url: str) -> FetchResult:
        fetched.append(url)
        raise AssertionError(f"fetched {url}")

    monkeypatch.setattr(processor, "_fetch", fetch)

    result = processor.process(
        pending, result_path, root=tmp_path, audit_path=audit_path,
    )

    assert result["status"] == "ignored"
    assert result["reason"] == "test signal"
    assert result["model_id"] is None
    assert result["signal_id"] == "test-orbit-9"
    assert fetched == []
    assert json.loads(result_path.read_text(encoding="utf-8"))["status"] == "ignored"
    assert not audit_path.exists()
    assert (tmp_path / "models" / "acme" / "orbit-1.md").read_bytes() == before
    assert not (tmp_path / "models" / "acme" / "orbit-9.md").exists()
    assert not (tmp_path / "offerings").exists()


def _watch_sources(root: Path, body: str) -> None:
    registry = root / "registry"
    registry.mkdir(parents=True, exist_ok=True)
    (registry / "release-watch.yaml").write_text(body, encoding="utf-8")


def _huggingface_watch(root: Path, *orgs: str, provider: str = "acme") -> None:
    lines = ["sources:"]
    for index, org in enumerate(orgs, start=1):
        lines.extend([
            f"- id: hf-{index}",
            "  kind: huggingface",
            f"  org: {org}",
            f"  provider: {provider}",
            "  confidence: 0.7",
        ])
    _watch_sources(root, "\n".join(lines) + "\n")


def _run_unlisted(
    monkeypatch: pytest.MonkeyPatch,
    root: Path,
    row: dict[str, object],
    pages: dict[str, FetchResult],
) -> tuple[dict, list[str]]:
    pending = root / "pending.json"
    result_path = root / "result.json"
    pending.write_text(json.dumps({"signals": [row]}), encoding="utf-8")
    seen: list[str] = []
    models_dev = "https://models.dev/api.json"

    def fetch(url: str) -> FetchResult:
        seen.append(url)
        if url in pages:
            return pages[url]
        if url == models_dev:
            return FetchResult(models_dev, b"{}", "application/json")
        if url.startswith("https://huggingface.co/api/"):
            return FetchResult(url, b"[]", "application/json")
        raise AssertionError(url)

    monkeypatch.setattr(processor, "_fetch", fetch)
    monkeypatch.setattr(
        processor.refresh_leaderboards, "run",
        lambda **_: processor.refresh_leaderboards.RefreshReport(),
    )
    result = processor.process(
        pending, result_path, root=root, price_fetcher=_PriceFetcher(),
    )
    return result, seen


def test_a_registered_huggingface_org_is_the_labs_page(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    from release_signals.pipeline import first_seen_host_class, registered_lab_hosts

    _write_card(tmp_path, "acme", "orbit-1", display="Orbit 1", version="orbit-1")
    _huggingface_watch(tmp_path, "AcmeLab")
    page = "https://huggingface.co/AcmeLab/orbit-9"
    hosts = registered_lab_hosts(tmp_path, "acme")
    assert "huggingface.co" not in hosts
    assert first_seen_host_class(page, hosts) == "unregistered"
    result, seen = _run_unlisted(
        monkeypatch, tmp_path,
        signal(
            model_name="Orbit 9",
            signal_id="watch:acme:orbit-9",
            first_seen_url=page,
        ),
        {page: FetchResult(page, b"<html><title>weights</title></html>", "text/html")},
    )

    assert result["status"] == "new"
    assert result["model_id"] == "acme/orbit-9"
    assert result["models_dev"] == "not_listed"
    assert result["primary_host"] == "huggingface.co"
    assert result["primary_kind"] == "huggingface-org"
    assert page in seen
    card = (tmp_path / "models" / "acme" / "orbit-9.md").read_text(encoding="utf-8")
    assert page in card


def test_another_huggingface_user_is_not_the_labs_page(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    _write_card(tmp_path, "acme", "orbit-1", display="Orbit 1", version="orbit-1")
    _huggingface_watch(tmp_path, "AcmeLab")
    page = "https://huggingface.co/other-user/orbit-9"
    result, seen = _run_unlisted(
        monkeypatch, tmp_path,
        signal(
            model_name="Orbit 9",
            signal_id="watch:acme:other-user",
            first_seen_url=page,
        ),
        {},
    )

    assert result["status"] == "uncertain"
    assert result["model_id"] is None
    assert "host class unregistered" in result["reason"]
    assert page not in seen
    assert not (tmp_path / "models" / "acme" / "orbit-9.md").exists()


def test_huggingface_spaces_datasets_and_a_bare_org_are_not_the_labs_page(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    _write_card(tmp_path, "acme", "orbit-1", display="Orbit 1", version="orbit-1")
    _huggingface_watch(tmp_path, "AcmeLab")
    for page, signal_id in (
        ("https://huggingface.co/spaces/AcmeLab/orbit-9", "watch:acme:spaces"),
        ("https://huggingface.co/datasets/AcmeLab/orbit-9", "watch:acme:datasets"),
        ("https://huggingface.co/AcmeLab", "watch:acme:bare-org"),
    ):
        drafted = tmp_path / "models" / "acme" / "orbit-9.md"
        if drafted.exists():
            drafted.unlink()
        result, seen = _run_unlisted(
            monkeypatch, tmp_path,
            signal(model_name="Orbit 9", signal_id=signal_id, first_seen_url=page),
            {},
        )
        assert result["status"] == "uncertain", page
        assert "host class unregistered" in result["reason"]
        assert page not in seen
        assert not drafted.exists()


def test_a_huggingface_org_match_is_case_insensitive(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    _write_card(tmp_path, "acme", "orbit-1", display="Orbit 1", version="orbit-1")
    _huggingface_watch(tmp_path, "AcmeLab")
    page = "https://huggingface.co/aCmElAb/orbit-9"
    result, seen = _run_unlisted(
        monkeypatch, tmp_path,
        signal(
            model_name="Orbit 9",
            signal_id="watch:acme:orbit-9-case",
            first_seen_url=page,
        ),
        {page: FetchResult(page, b"<html><title>weights</title></html>", "text/html")},
    )

    assert result["status"] == "new"
    assert result["primary_host"] == "huggingface.co"
    assert result["primary_kind"] == "huggingface-org"
    assert page in seen


def test_a_huggingface_repository_named_for_another_model_is_uncertain(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    _write_card(tmp_path, "acme", "orbit-1", display="Orbit 1", version="orbit-1")
    _huggingface_watch(tmp_path, "AcmeLab")
    mismatch = "https://huggingface.co/AcmeLab/other-model"
    result, seen = _run_unlisted(
        monkeypatch, tmp_path,
        signal(
            model_name="Orbit 9",
            signal_id="watch:acme:other-model",
            first_seen_url=mismatch,
        ),
        {mismatch: FetchResult(mismatch, b"<h1>Other Model</h1>", "text/html")},
    )

    assert result["status"] == "uncertain"
    assert result["model_id"] is None
    assert result["reason"] == "the primary source does not identify the stated lab"
    assert mismatch in seen
    assert not (tmp_path / "models" / "acme" / "orbit-9.md").exists()

    named_root = tmp_path / "named"
    _write_card(named_root, "acme", "orbit-1", display="Orbit 1", version="orbit-1")
    _huggingface_watch(named_root, "AcmeLab")
    named_result, named_seen = _run_unlisted(
        monkeypatch, named_root,
        signal(
            model_name="Orbit 9",
            signal_id="watch:acme:named-on-page",
            first_seen_url=mismatch,
        ),
        {mismatch: FetchResult(mismatch, b"<h1>Orbit 9</h1>", "text/html")},
    )
    assert named_result["status"] == "uncertain"
    assert named_result["model_id"] is None
    assert named_result["reason"] == "the primary source does not identify the stated lab"
    assert mismatch in named_seen
    assert not (named_root / "models" / "acme" / "orbit-9.md").exists()


def test_huggingface_org_identity_is_the_repository_name_only(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    page_text = (
        b'<script type="application/ld+json">'
        b'{"name":"Orbit 9","publisher":{"name":"Acme"}}'
        b"</script><p>Orbit 9</p>"
    )
    for repo in ("Orbit-9-GGUF", "Orbit-9-lora", "comet-1"):
        root = tmp_path / repo
        _write_card(root, "acme", "orbit-1", display="Orbit 1", version="orbit-1")
        _huggingface_watch(root, "AcmeLab")
        page = f"https://huggingface.co/AcmeLab/{repo}"
        result, seen = _run_unlisted(
            monkeypatch, root,
            signal(
                model_name="Orbit 9",
                signal_id=f"watch:acme:{repo}",
                first_seen_url=page,
            ),
            {page: FetchResult(page, page_text, "text/html")},
        )
        assert result["status"] == "uncertain", repo
        assert result["model_id"] is None
        assert result["reason"] == "the primary source does not identify the stated lab"
        assert "identity_basis" not in result
        assert page in seen
        assert not (root / "models" / "acme" / "orbit-9.md").exists()

    root = tmp_path / "exact"
    _write_card(root, "acme", "orbit-1", display="Orbit 1", version="orbit-1")
    _huggingface_watch(root, "AcmeLab")
    page = "https://huggingface.co/AcmeLab/Orbit-9"
    result, seen = _run_unlisted(
        monkeypatch, root,
        signal(
            model_name="Orbit 9",
            signal_id="watch:acme:orbit-9-exact",
            first_seen_url=page,
        ),
        {page: FetchResult(page, b"<html><title>weights</title></html>", "text/html")},
    )
    assert result["status"] == "new"
    assert result["model_id"] == "acme/orbit-9"
    assert result["identity_basis"] == "repo-name"
    assert page in seen


def test_a_huggingface_org_card_files_the_repository_as_huggingface_url(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    _write_card(tmp_path, "acme", "orbit-1", display="Orbit 1", version="orbit-1")
    _huggingface_watch(tmp_path, "AcmeLab")
    page = "https://huggingface.co/AcmeLab/orbit-9"
    result, _seen = _run_unlisted(
        monkeypatch, tmp_path,
        signal(
            model_name="Orbit 9",
            signal_id="watch:acme:filed-repo",
            first_seen_url=page,
        ),
        {page: FetchResult(page, b"<html><title>weights</title></html>", "text/html")},
    )

    assert result["status"] == "new"
    card = tmp_path / "models" / "acme" / "orbit-9.md"
    front = yaml.safe_load(card.read_text(encoding="utf-8").split("---", 2)[1])
    assert front["sources"]["huggingface_url"] == page
    assert front["sources"]["provider_docs_url"] == ""


def test_a_lab_page_records_page_text_or_json_ld_identity(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    host = "models.acme.example"
    visible = f"https://{host}/orbit-9"
    linked = f"https://{host}/orbit-8"
    linked_body = (
        b'<script type="application/ld+json">'
        b'{"name":"Orbit 8","publisher":{"name":"Acme"},"datePublished":"2026-09-26"}'
        b"</script>"
    )
    for page, model_name, body, basis in (
        (visible, "Orbit 9", b"<h1>Orbit 9</h1>", "page-text"),
        (linked, "Orbit 8", linked_body, "json-ld"),
    ):
        root = tmp_path / basis
        _write_card(root, "acme", "orbit-1", display="Orbit 1", version="orbit-1")
        _watch_lab(root, host)
        result, seen = _run_unlisted(
            monkeypatch, root,
            signal(
                model_name=model_name,
                signal_id=f"watch:acme:{basis}",
                first_seen_url=page,
            ),
            {page: FetchResult(page, body, "text/html")},
        )
        assert result["status"] == "new", basis
        assert result["identity_basis"] == basis
        assert page in seen


def test_a_provider_with_two_huggingface_orgs_accepts_both(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    _write_card(tmp_path, "acme", "orbit-1", display="Orbit 1", version="orbit-1")
    _huggingface_watch(tmp_path, "AcmeLab", "AcmeResearch")
    for org, model_name, slug in (
        ("AcmeLab", "Orbit 9", "orbit-9"),
        ("AcmeResearch", "Orbit 8", "orbit-8"),
    ):
        page = f"https://huggingface.co/{org}/{slug}"
        result, seen = _run_unlisted(
            monkeypatch, tmp_path,
            signal(
                model_name=model_name,
                signal_id=f"watch:acme:{slug}",
                first_seen_url=page,
            ),
            {page: FetchResult(page, b"<html><title>weights</title></html>", "text/html")},
        )
        assert result["status"] == "new", org
        assert result["model_id"] == f"acme/{slug}"
        assert result["primary_kind"] == "huggingface-org"
        assert page in seen

    outsider = "https://huggingface.co/other-user/orbit-7"
    refused, refused_seen = _run_unlisted(
        monkeypatch, tmp_path,
        signal(
            model_name="Orbit 7",
            signal_id="watch:acme:orbit-7",
            first_seen_url=outsider,
        ),
        {},
    )
    assert refused["status"] == "uncertain"
    assert "host class unregistered" in refused["reason"]
    assert outsider not in refused_seen


def _write_display_card(
    root: Path, provider: str, slug: str, *, display_name: str, provider_display: str,
) -> None:
    path = root / "models" / provider / f"{slug}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "---\n"
        f"model_id: {provider}/{slug}\n"
        f"display_name: {display_name}\n"
        f"provider: {provider}\n"
        f"provider_display: {provider_display}\n"
        f"version: {slug}\n"
        "---\n",
        encoding="utf-8",
    )


def test_a_huggingface_org_matches_a_provider_that_resolves_to_the_lab(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    _write_display_card(
        tmp_path, "beta", "kept",
        display_name="Kept", provider_display="Alpha / Beta Team",
    )
    _huggingface_watch(tmp_path, "BetaLab", provider="Alpha / Beta Team")
    page = "https://huggingface.co/BetaLab/orbit-9"
    result, seen = _run_unlisted(
        monkeypatch, tmp_path,
        signal(
            model_name="Orbit 9",
            provider="Beta",
            signal_id="watch:beta:orbit-9",
            first_seen_url=page,
        ),
        {page: FetchResult(page, b"<html><title>weights</title></html>", "text/html")},
    )

    assert result["status"] == "new"
    assert result["model_id"] == "beta/orbit-9"
    assert result["primary_kind"] == "huggingface-org"
    assert page in seen


def test_a_huggingface_org_does_not_match_a_different_lab(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    _write_display_card(
        tmp_path, "beta", "kept",
        display_name="Kept", provider_display="Alpha / Beta Team",
    )
    _write_card(tmp_path, "gamma", "kept", display="Kept", version="kept")
    _huggingface_watch(tmp_path, "BetaLab", provider="Alpha / Beta Team")
    page = "https://huggingface.co/BetaLab/orbit-9"
    result, seen = _run_unlisted(
        monkeypatch, tmp_path,
        signal(
            model_name="Orbit 9",
            provider="Gamma",
            signal_id="watch:gamma:orbit-9",
            first_seen_url=page,
        ),
        {page: FetchResult(page, b"<h1>Orbit 9</h1>", "text/html")},
    )

    assert result["status"] == "uncertain"
    assert result["model_id"] is None
    assert "host class unregistered" in result["reason"]
    assert page not in seen
    assert not (tmp_path / "models" / "gamma" / "orbit-9.md").exists()


def test_a_cite_only_huggingface_host_stays_unfetched(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    _write_card(tmp_path, "acme", "orbit-1", display="Orbit 1", version="orbit-1")
    _huggingface_watch(tmp_path, "AcmeLab")
    page = "https://huggingface.co/AcmeLab/orbit-9"
    monkeypatch.setattr(
        "decision.retention.cite_only_hosts", lambda: ("huggingface.co",),
    )
    result, seen = _run_unlisted(monkeypatch, tmp_path, signal(
        model_name="Orbit 9",
        signal_id="watch:acme:cite-only",
        first_seen_url=page,
    ), {})

    assert result["status"] == "uncertain"
    assert "host class cite-only" in result["reason"]
    assert page not in seen
    assert not (tmp_path / "models" / "acme" / "orbit-9.md").exists()


def test_a_huggingface_org_for_another_provider_is_not_fetched(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    _write_card(tmp_path, "acme", "orbit-1", display="Orbit 1", version="orbit-1")
    _huggingface_watch(tmp_path, "AcmeLab", provider="other")
    page = "https://huggingface.co/AcmeLab/orbit-9"
    result, seen = _run_unlisted(
        monkeypatch, tmp_path,
        signal(
            model_name="Orbit 9",
            signal_id="watch:acme:other-provider",
            first_seen_url=page,
        ),
        {page: FetchResult(page, b"<h1>Orbit 9</h1>", "text/html")},
    )

    assert result["status"] == "uncertain"
    assert result["model_id"] is None
    assert "host class unregistered" in result["reason"]
    assert page not in seen
    assert not (tmp_path / "models" / "acme" / "orbit-9.md").exists()


def test_a_huggingface_redirect_to_another_owner_stays_unregistered(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    _write_card(tmp_path, "acme", "orbit-1", display="Orbit 1", version="orbit-1")
    _huggingface_watch(tmp_path, "AcmeLab")
    requested = "https://huggingface.co/AcmeLab/orbit-9"
    final = "https://huggingface.co/other-user/orbit-9"
    result, seen = _run_unlisted(
        monkeypatch, tmp_path,
        signal(
            model_name="Orbit 9",
            signal_id="watch:acme:redirected-owner",
            first_seen_url=requested,
        ),
        {requested: FetchResult(final, b"<h1>Orbit 9</h1>", "text/html")},
    )

    assert result["status"] == "uncertain"
    assert result["model_id"] is None
    assert "host class unregistered" in result["reason"]
    assert requested in seen
    assert not (tmp_path / "models" / "acme" / "orbit-9.md").exists()


@pytest.mark.parametrize(
    "path",
    [
        "/AcmeLab/%2e%2e/evil/x",
        "//AcmeLab/orbit-9",
        "/AcmeLab/orbit-9/discussions/7",
        "/AcmeLab/orbit-9/tree/main",
    ],
)
def test_a_huggingface_path_other_than_the_repository_is_not_the_labs_page(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, path: str,
) -> None:
    _write_card(tmp_path, "acme", "orbit-1", display="Orbit 1", version="orbit-1")
    _huggingface_watch(tmp_path, "AcmeLab")
    page = "https://huggingface.co" + path
    result, seen = _run_unlisted(
        monkeypatch, tmp_path,
        signal(
            model_name="Orbit 9",
            signal_id="watch:acme:" + path.strip("/").replace("/", "-").replace("%", "p"),
            first_seen_url=page,
        ),
        {page: FetchResult(page, b"<h1>Orbit 9</h1>", "text/html")},
    )

    assert result["status"] == "uncertain", path
    assert result["model_id"] is None
    assert "host class unregistered" in result["reason"]
    assert page not in seen
    assert not (tmp_path / "models" / "acme" / "orbit-9.md").exists()


def test_a_huggingface_repository_with_one_trailing_slash_is_the_labs_page(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    _write_card(tmp_path, "acme", "orbit-1", display="Orbit 1", version="orbit-1")
    _huggingface_watch(tmp_path, "AcmeLab")
    page = "https://huggingface.co/AcmeLab/orbit-9/"
    result, seen = _run_unlisted(
        monkeypatch, tmp_path,
        signal(
            model_name="Orbit 9",
            signal_id="watch:acme:trailing-slash",
            first_seen_url=page,
        ),
        {page: FetchResult(page, b"<html><title>weights</title></html>", "text/html")},
    )

    assert result["status"] == "new"
    assert result["model_id"] == "acme/orbit-9"
    assert result["primary_kind"] == "huggingface-org"
    assert page in seen


def test_a_huggingface_redirect_onto_a_longer_path_is_not_the_labs_page(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    _write_card(tmp_path, "acme", "orbit-1", display="Orbit 1", version="orbit-1")
    _huggingface_watch(tmp_path, "AcmeLab")
    requested = "https://huggingface.co/AcmeLab/orbit-9"
    final = "https://huggingface.co/AcmeLab/orbit-9/tree/main"
    result, seen = _run_unlisted(
        monkeypatch, tmp_path,
        signal(
            model_name="Orbit 9",
            signal_id="watch:acme:redirected-tree",
            first_seen_url=requested,
        ),
        {requested: FetchResult(final, b"<h1>Orbit 9</h1>", "text/html")},
    )

    assert result["status"] == "uncertain"
    assert result["model_id"] is None
    assert "host class unregistered" in result["reason"]
    assert requested in seen
    assert not (tmp_path / "models" / "acme" / "orbit-9.md").exists()


def _listed_doc_payload(doc: str) -> bytes:
    return json.dumps({
        "acme": {
            "name": "Acme",
            "doc": doc,
            "models": {"orbit-9": {"id": "orbit-9", "name": "Orbit 9"}},
        },
    }).encode()


def test_a_provider_doc_on_an_unregistered_host_yields_to_the_labs_page(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    _write_card(tmp_path, "acme", "orbit-1", display="Orbit 1", version="orbit-1")
    host = "models.acme.example"
    _watch_lab(tmp_path, host)
    page = f"https://{host}/orbit-9"
    sibling = "https://docs.sibling.example/orbit-9"
    models_dev = "https://models.dev/api.json"
    seen: list[str] = []

    def fetch(url: str) -> FetchResult:
        seen.append(url)
        if url == models_dev:
            return FetchResult(models_dev, _listed_doc_payload(sibling), "application/json")
        if url == page:
            return FetchResult(page, b"<h1>Orbit 9</h1>", "text/html")
        if url == sibling:
            return FetchResult(sibling, b"<h1>Orbit 9</h1>", "text/html")
        if url.startswith("https://huggingface.co/api/"):
            return FetchResult(url, b"[]", "application/json")
        raise AssertionError(url)

    monkeypatch.setattr(processor, "_fetch", fetch)
    monkeypatch.setattr(
        processor.refresh_leaderboards, "run",
        lambda **_: processor.refresh_leaderboards.RefreshReport(),
    )
    pending = tmp_path / "pending.json"
    pending.write_text(json.dumps({"signals": [signal(
        model_name="Orbit 9",
        signal_id="watch:acme:first-seen-page",
        first_seen_url=page,
    )]}), encoding="utf-8")
    result = processor.process(
        pending, tmp_path / "result.json", root=tmp_path, price_fetcher=_PriceFetcher(),
    )

    assert result["status"] == "new"
    assert result["model_id"] == "acme/orbit-9"
    assert sibling not in seen
    assert page in seen
    card = (tmp_path / "models" / "acme" / "orbit-9.md").read_text(encoding="utf-8")
    assert page in card
    assert sibling not in card


def test_a_provider_doc_on_an_unregistered_host_yields_to_the_org_repository(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    _write_card(tmp_path, "acme", "orbit-1", display="Orbit 1", version="orbit-1")
    _huggingface_watch(tmp_path, "AcmeLab")
    page = "https://huggingface.co/AcmeLab/orbit-9"
    sibling = "https://docs.sibling.example/orbit-9"
    models_dev = "https://models.dev/api.json"
    seen: list[str] = []

    def fetch(url: str) -> FetchResult:
        seen.append(url)
        if url == models_dev:
            return FetchResult(models_dev, _listed_doc_payload(sibling), "application/json")
        if url == page:
            return FetchResult(page, b"<html><title>weights</title></html>", "text/html")
        if url == sibling:
            return FetchResult(sibling, b"<h1>Orbit 9</h1>", "text/html")
        if url.startswith("https://huggingface.co/api/"):
            return FetchResult(url, b"[]", "application/json")
        raise AssertionError(url)

    monkeypatch.setattr(processor, "_fetch", fetch)
    monkeypatch.setattr(
        processor.refresh_leaderboards, "run",
        lambda **_: processor.refresh_leaderboards.RefreshReport(),
    )
    pending = tmp_path / "pending.json"
    pending.write_text(json.dumps({"signals": [signal(
        model_name="Orbit 9",
        signal_id="watch:acme:first-seen-repo",
        first_seen_url=page,
    )]}), encoding="utf-8")
    result = processor.process(
        pending, tmp_path / "result.json", root=tmp_path, price_fetcher=_PriceFetcher(),
    )

    assert result["status"] == "new"
    assert sibling not in seen
    assert page in seen
    assert result["identity_basis"] == "repo-name"
    card = tmp_path / "models" / "acme" / "orbit-9.md"
    front = yaml.safe_load(card.read_text(encoding="utf-8").split("---", 2)[1])
    assert front["sources"]["huggingface_url"] == page
    assert front["sources"]["provider_docs_url"] == ""


def test_an_unregistered_first_seen_url_keeps_the_provider_doc(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    _write_card(tmp_path, "acme", "orbit-1", display="Orbit 1", version="orbit-1")
    first_seen = "https://news.example/orbit-9"
    doc = "https://docs.sibling.example/orbit-9"
    models_dev = "https://models.dev/api.json"
    body = (
        b'<script type="application/ld+json">'
        b'{"name":"Orbit 9","publisher":{"name":"Acme"},"datePublished":"2026-09-26"}'
        b"</script>"
    )
    seen: list[str] = []

    def fetch(url: str) -> FetchResult:
        seen.append(url)
        if url == models_dev:
            return FetchResult(models_dev, _listed_doc_payload(doc), "application/json")
        if url == doc:
            return FetchResult(doc, body, "text/html")
        if url == first_seen:
            raise AssertionError(url)
        if url.startswith("https://huggingface.co/api/"):
            return FetchResult(url, b"[]", "application/json")
        raise AssertionError(url)

    monkeypatch.setattr(processor, "_fetch", fetch)
    monkeypatch.setattr(
        processor.refresh_leaderboards, "run",
        lambda **_: processor.refresh_leaderboards.RefreshReport(),
    )
    pending = tmp_path / "pending.json"
    pending.write_text(json.dumps({"signals": [signal(
        model_name="Orbit 9",
        signal_id="watch:acme:unregistered-first-seen",
        first_seen_url=first_seen,
    )]}), encoding="utf-8")
    result = processor.process(
        pending, tmp_path / "result.json", root=tmp_path, price_fetcher=_PriceFetcher(),
    )

    assert result["status"] == "new"
    assert result["model_id"] == "acme/orbit-9"
    assert doc in seen
    assert first_seen not in seen
    assert doc in (tmp_path / "models" / "acme" / "orbit-9.md").read_text(encoding="utf-8")


def test_one_gather_signal_scans_the_catalogue_at_most_once(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    """Thirty Hugging Face sources must not re-read every card."""
    from release_signals.pipeline import clear_catalogue_cache, gather_signal

    clear_catalogue_cache()
    _write_card(tmp_path, "acme", "orbit-1", display="Orbit 1", version="orbit-1")
    lines = ["sources:"]
    for index in range(30):
        lines.extend([
            f"- id: hf-{index}",
            "  kind: huggingface",
            f"  org: lab-{index}",
            f"  provider: Fixture Lab {index}",
            "  confidence: 0.7",
        ])
    _watch_sources(tmp_path, "\n".join(lines) + "\n")
    models_dev = "https://models.dev/api.json"
    primary = "https://acme.example/models/orbit-1"
    payload = json.dumps({
        "acme": {
            "name": "Acme",
            "models": {
                "orbit-1": {"id": "orbit-1", "name": "Orbit 1", "release_url": primary},
            },
        },
    }).encode()
    page = b"<html><body>Acme releases Orbit 1.</body></html>"
    scans = 0
    original_glob = Path.glob

    def counting_glob(self: Path, pattern: str):
        nonlocal scans
        if pattern == "*/*.md" and self.name == "models":
            scans += 1
        return original_glob(self, pattern)

    monkeypatch.setattr(Path, "glob", counting_glob)
    row = ReleaseSignal.parse(signal(model_name="Orbit 1"))

    def fetch(url: str) -> FetchResult:
        if url == models_dev:
            return FetchResult(models_dev, payload, "application/json")
        if url == primary:
            return FetchResult(primary, page, "text/html")
        raise AssertionError(url)

    gathered = gather_signal(row, root=tmp_path, fetch=fetch)

    assert gathered.resolution.status == "existing"
    assert scans <= 1

    clear_catalogue_cache()
    scans = 0
    again = gather_signal(row, root=tmp_path, fetch=fetch)
    assert again.resolution.status == "existing"
    assert scans == 1


def _run_listed(
    monkeypatch: pytest.MonkeyPatch,
    root: Path,
    row: dict[str, object],
    pages: dict[str, FetchResult],
    *,
    doc: str,
) -> tuple[dict, list[str]]:
    pending = root / "pending.json"
    pending.write_text(json.dumps({"signals": [row]}), encoding="utf-8")
    seen: list[str] = []
    models_dev = "https://models.dev/api.json"

    def fetch(url: str) -> FetchResult:
        seen.append(url)
        if url in pages:
            return pages[url]
        if url == models_dev:
            return FetchResult(models_dev, _listed_doc_payload(doc), "application/json")
        if url.startswith("https://huggingface.co/api/"):
            return FetchResult(url, b"[]", "application/json")
        raise AssertionError(url)

    monkeypatch.setattr(processor, "_fetch", fetch)
    monkeypatch.setattr(
        processor.refresh_leaderboards, "run",
        lambda **_: processor.refresh_leaderboards.RefreshReport(),
    )
    result = processor.process(
        pending, root / "result.json", root=root, price_fetcher=_PriceFetcher(),
    )
    return result, seen


def _watch_lab_and_org(root: Path, host: str, org: str) -> None:
    _watch_sources(
        root,
        "sources:\n"
        "- id: acme-models\n"
        "  kind: page\n"
        f"  url: https://{host}/models\n"
        "  provider: acme\n"
        "  pattern: orbit\n"
        "  confidence: 0.9\n"
        "- id: hf-1\n"
        "  kind: huggingface\n"
        f"  org: {org}\n"
        "  provider: acme\n"
        "  confidence: 0.7\n",
    )


def test_a_first_seen_org_redirect_to_another_owner_stays_unregistered(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    _write_card(tmp_path, "acme", "orbit-1", display="Orbit 1", version="orbit-1")
    _huggingface_watch(tmp_path, "AcmeLab")
    requested = "https://huggingface.co/AcmeLab/orbit-9"
    final = "https://huggingface.co/other-user/orbit-9"
    doc = "https://docs.sibling.example/orbit-9"
    result, seen = _run_listed(
        monkeypatch, tmp_path,
        signal(
            model_name="Orbit 9",
            signal_id="watch:acme:listed-redirect-owner",
            first_seen_url=requested,
        ),
        {
            requested: FetchResult(final, b"<h1>Acme releases Orbit 9</h1>", "text/html"),
            doc: FetchResult(doc, b"<html><title>weights</title></html>", "text/html"),
        },
        doc=doc,
    )

    assert result["status"] == "uncertain"
    assert result["model_id"] is None
    assert result["reason"] == (
        "host class unregistered; the primary source does not identify the stated lab"
    )
    assert doc in seen
    assert not (tmp_path / "models" / "acme" / "orbit-9.md").exists()


def test_a_first_seen_lab_redirect_to_an_unregistered_host_stays_unregistered(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    _write_card(tmp_path, "acme", "orbit-1", display="Orbit 1", version="orbit-1")
    host = "models.acme.example"
    _watch_lab(tmp_path, host)
    requested = f"https://{host}/changelog/orbit-9"
    final = "https://news.example/orbit-9"
    doc = "https://docs.sibling.example/orbit-9"
    result, seen = _run_listed(
        monkeypatch, tmp_path,
        signal(
            model_name="Orbit 9",
            signal_id="watch:acme:listed-redirect-host",
            first_seen_url=requested,
        ),
        {
            requested: FetchResult(final, b"<h1>Acme releases Orbit 9</h1>", "text/html"),
            doc: FetchResult(doc, b"<html><title>weights</title></html>", "text/html"),
        },
        doc=doc,
    )

    assert result["status"] == "uncertain"
    assert result["model_id"] is None
    assert result["reason"] == (
        "host class unregistered; the primary source does not identify the stated lab"
    )
    assert doc in seen
    assert not (tmp_path / "models" / "acme" / "orbit-9.md").exists()


def test_a_first_seen_lab_redirect_to_the_org_repository_uses_the_repo_name(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    _write_card(tmp_path, "acme", "orbit-1", display="Orbit 1", version="orbit-1")
    host = "models.acme.example"
    _watch_lab_and_org(tmp_path, host, "AcmeLab")
    requested = f"https://{host}/changelog/orbit-9"
    final = "https://huggingface.co/AcmeLab/orbit-9"
    doc = "https://docs.sibling.example/orbit-9"
    result, seen = _run_listed(
        monkeypatch, tmp_path,
        signal(
            model_name="Orbit 9",
            signal_id="watch:acme:listed-redirect-repo",
            first_seen_url=requested,
        ),
        {requested: FetchResult(final, b"<h1>Orbit 9</h1>", "text/html")},
        doc=doc,
    )

    assert result["status"] == "new"
    assert result["model_id"] == "acme/orbit-9"
    assert result["identity_basis"] == "repo-name"
    assert doc not in seen
    card = tmp_path / "models" / "acme" / "orbit-9.md"
    front = yaml.safe_load(card.read_text(encoding="utf-8").split("---", 2)[1])
    assert front["sources"]["huggingface_url"] == final
    assert front["sources"]["provider_docs_url"] == ""
    assert requested not in front["sources"].values()


def _existing_card_with_urls(
    root: Path, *, huggingface_url: str = "https://huggingface.co/acme/kept-orbit-1",
) -> Path:
    card = _write_card(root, "acme", "orbit-1", display="Orbit 1", version="orbit-1")
    text = card.read_text(encoding="utf-8")
    front = yaml.safe_load(text.split("---", 2)[1])
    sources = {"provider_docs_url": "https://docs.acme.example/orbit-1"}
    if huggingface_url:
        sources["huggingface_url"] = huggingface_url
    front["sources"] = sources
    card.write_text(
        "---\n" + yaml.dump(front, sort_keys=False) + "---" + text.split("---", 2)[2],
        encoding="utf-8",
    )
    return card


def _process_existing_first_seen(
    monkeypatch: pytest.MonkeyPatch,
    root: Path,
    *,
    first_seen: str,
    page: FetchResult,
    signal_id: str,
) -> dict:
    doc = "https://docs.sibling.example/orbit-1"
    models_dev = "https://models.dev/api.json"
    payload = _listed_doc_payload(doc).replace(b"orbit-9", b"orbit-1").replace(b"Orbit 9", b"Orbit 1")
    seen: list[str] = []

    def fetch(url: str) -> FetchResult:
        seen.append(url)
        if url == models_dev:
            return FetchResult(models_dev, payload, "application/json")
        if url == first_seen:
            return page
        if url.startswith("https://huggingface.co/api/"):
            return FetchResult(url, b"[]", "application/json")
        raise AssertionError(url)

    monkeypatch.setattr(processor, "_fetch", fetch)
    monkeypatch.setattr(
        processor.refresh_leaderboards, "run",
        lambda **_: processor.refresh_leaderboards.RefreshReport(),
    )
    pending = root / "pending.json"
    pending.write_text(json.dumps({"signals": [signal(
        model_name="Orbit 1",
        signal_id=signal_id,
        first_seen_url=first_seen,
    )]}), encoding="utf-8")
    result = processor.process(
        pending, root / "result.json", root=root,
    )
    result["_seen"] = seen
    return result


@pytest.mark.parametrize(
    ("where", "first_seen", "body"),
    [
        (
            "repository",
            "https://huggingface.co/AcmeLab/orbit-1",
            b"<html><title>weights</title></html>",
        ),
        (
            "changelog",
            "https://models.acme.example/changelog/orbit-1",
            b"<h1>Orbit 1</h1>",
        ),
    ],
)
def test_an_existing_card_keeps_its_urls(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, where: str, first_seen: str, body: bytes,
) -> None:
    kept_hf = "https://huggingface.co/acme/kept-orbit-1"
    kept_docs = "https://docs.acme.example/orbit-1"
    _existing_card_with_urls(tmp_path, huggingface_url=kept_hf)
    if where == "repository":
        _huggingface_watch(tmp_path, "AcmeLab")
    else:
        _watch_lab(tmp_path, "models.acme.example")
    result = _process_existing_first_seen(
        monkeypatch, tmp_path,
        first_seen=first_seen,
        page=FetchResult(first_seen, body, "text/html"),
        signal_id=f"watch:acme:keep-urls-{where}",
    )

    assert result["status"] == "existing"
    assert "identity_error" not in result
    front = yaml.safe_load(
        (tmp_path / "models" / "acme" / "orbit-1.md").read_text(encoding="utf-8").split("---", 2)[1]
    )
    assert front["sources"]["provider_docs_url"] == kept_docs
    assert front["sources"]["huggingface_url"] == kept_hf


def test_an_existing_huggingface_primary_fills_an_empty_huggingface_url(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    kept_docs = "https://docs.acme.example/orbit-1"
    _existing_card_with_urls(tmp_path, huggingface_url="")
    _huggingface_watch(tmp_path, "AcmeLab")
    page = "https://huggingface.co/AcmeLab/orbit-1"
    result = _process_existing_first_seen(
        monkeypatch, tmp_path,
        first_seen=page,
        page=FetchResult(page, b"<html><title>weights</title></html>", "text/html"),
        signal_id="watch:acme:fill-huggingface-url",
    )

    assert result["status"] == "existing"
    assert "identity_error" not in result
    front = yaml.safe_load(
        (tmp_path / "models" / "acme" / "orbit-1.md").read_text(encoding="utf-8").split("---", 2)[1]
    )
    assert front["sources"]["provider_docs_url"] == kept_docs
    assert front["sources"]["huggingface_url"] == page


_DOC_IDENTITY = (
    b'<script type="application/ld+json">'
    b'{"name":"Orbit 9","publisher":{"name":"Acme"},"datePublished":"2026-09-26"}'
    b"</script>"
)


def test_a_first_seen_page_without_the_name_falls_back_to_the_provider_doc(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    _write_card(tmp_path, "acme", "orbit-1", display="Orbit 1", version="orbit-1")
    host = "models.acme.example"
    _watch_lab(tmp_path, host)
    page = f"https://{host}/orbit-9"
    doc = "https://docs.sibling.example/orbit-9"
    result, seen = _run_listed(
        monkeypatch, tmp_path,
        signal(
            model_name="Orbit 9",
            signal_id="watch:acme:doc-fallback",
            first_seen_url=page,
        ),
        {
            page: FetchResult(page, b"<html><title>weights</title></html>", "text/html"),
            doc: FetchResult(doc, _DOC_IDENTITY, "text/html"),
        },
        doc=doc,
    )

    assert result["status"] == "new"
    assert result["model_id"] == "acme/orbit-9"
    assert result["identity_basis"] == "json-ld"
    assert page in seen
    assert doc in seen
    card = tmp_path / "models" / "acme" / "orbit-9.md"
    text = card.read_text(encoding="utf-8")
    front = yaml.safe_load(text.split("---", 2)[1])
    assert front["sources"]["provider_docs_url"] == doc
    assert str(front["release_date"]) == "2026-09-26"
    assert page not in text


def test_the_provider_doc_is_not_requested_when_the_first_seen_page_succeeds(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    _write_card(tmp_path, "acme", "orbit-1", display="Orbit 1", version="orbit-1")
    host = "models.acme.example"
    _watch_lab(tmp_path, host)
    page = f"https://{host}/orbit-9"
    doc = "https://docs.sibling.example/orbit-9"
    result, seen = _run_listed(
        monkeypatch, tmp_path,
        signal(
            model_name="Orbit 9",
            signal_id="watch:acme:doc-not-requested",
            first_seen_url=page,
        ),
        {
            page: FetchResult(page, b"<h1>Orbit 9</h1>", "text/html"),
            doc: FetchResult(doc, _DOC_IDENTITY, "text/html"),
        },
        doc=doc,
    )

    assert result["status"] == "new"
    assert result["model_id"] == "acme/orbit-9"
    assert doc not in seen
    assert page in (tmp_path / "models" / "acme" / "orbit-9.md").read_text(encoding="utf-8")


def test_both_identity_pages_fail_before_a_card_is_drafted(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    _write_card(tmp_path, "acme", "orbit-1", display="Orbit 1", version="orbit-1")
    host = "models.acme.example"
    _watch_lab(tmp_path, host)
    page = f"https://{host}/orbit-9"
    doc = "https://docs.sibling.example/orbit-9"
    blank = b"<html><title>weights</title></html>"
    result, seen = _run_listed(
        monkeypatch, tmp_path,
        signal(
            model_name="Orbit 9",
            signal_id="watch:acme:both-uncertain",
            first_seen_url=page,
        ),
        {
            page: FetchResult(page, blank, "text/html"),
            doc: FetchResult(doc, blank, "text/html"),
        },
        doc=doc,
    )

    assert result["status"] == "uncertain"
    assert doc in seen
    assert not (tmp_path / "models" / "acme" / "orbit-9.md").exists()


def test_primary_identity_reports_how_the_page_matched() -> None:
    import typing

    assert typing.get_type_hints(_primary_identity)["return"] == tuple[str, str, str]


def test_an_explicit_empty_api_docs_url_is_left_empty() -> None:
    doc = "https://docs.sibling.example/orbit-9"
    _provider_id, listing, provider_doc = _models_dev_listing(
        {"acme": {
            "name": "Acme",
            "doc": doc,
            "models": {"orbit-9": {"id": "orbit-9", "name": "Orbit 9", "api_docs_url": ""}},
        }},
        "Acme",
        "Orbit 9",
        source_url="https://models.dev/api.json",
    )

    assert listing["api_docs_url"] == ""
    assert provider_doc is None
    assert listing.get("_provider_doc") != doc


def test_a_model_row_does_not_supply_the_provider_doc() -> None:
    doc = "https://docs.sibling.example/orbit-9"
    evil = "https://evil.example/stolen"
    _provider_id, listing, provider_doc = _models_dev_listing(
        {"acme": {
            "name": "Acme",
            "doc": doc,
            "models": {"orbit-9": {
                "id": "orbit-9", "name": "Orbit 9", "_provider_doc": evil,
            }},
        }},
        "Acme",
        "Orbit 9",
        source_url="https://models.dev/api.json",
    )

    assert listing["_provider_doc"] == evil
    assert listing["api_docs_url"] == doc
    assert provider_doc == doc


def test_a_prohibited_supporting_url_does_not_raise_before_identity(tmp_path: Path) -> None:
    from release_signals.pipeline import gather_signal

    prohibited = "https://" + "artificial" + "analysis.ai" + "/orbit-9"
    release = "https://acme.example/models/orbit-9"
    models_dev = "https://models.dev/api.json"
    payload = json.dumps({"acme": {
        "name": "Acme",
        "models": {"orbit-9": {
            "id": "orbit-9", "name": "Orbit 9",
            "release_url": release,
            "api_docs_url": prohibited,
        }},
    }}).encode()
    _write_card(tmp_path, "acme", "orbit-1", display="Orbit 1", version="orbit-1")

    def fetch(url: str) -> FetchResult:
        if url == models_dev:
            return FetchResult(models_dev, payload, "application/json")
        if url == release:
            return FetchResult(release, b"<html><title>weights</title></html>", "text/html")
        raise AssertionError(url)

    gathered = gather_signal(
        ReleaseSignal.parse(signal(model_name="Orbit 9")),
        root=tmp_path,
        fetch=fetch,
    )

    assert gathered.resolution.status == "uncertain"
    assert "does not identify" in gathered.resolution.reason


def test_a_prohibited_supporting_url_is_refused_after_identity(tmp_path: Path) -> None:
    from release_signals.pipeline import gather_signal

    prohibited = "https://" + "artificial" + "analysis.ai" + "/orbit-9"
    release = "https://acme.example/models/orbit-9"
    models_dev = "https://models.dev/api.json"
    payload = json.dumps({"acme": {
        "name": "Acme",
        "models": {"orbit-9": {
            "id": "orbit-9", "name": "Orbit 9",
            "release_url": release,
            "api_docs_url": prohibited,
        }},
    }}).encode()
    _write_card(tmp_path, "acme", "orbit-1", display="Orbit 1", version="orbit-1")

    def fetch(url: str) -> FetchResult:
        if url == models_dev:
            return FetchResult(models_dev, payload, "application/json")
        if url == release:
            return FetchResult(release, b"<h1>Acme releases Orbit 9</h1>", "text/html")
        raise AssertionError(url)

    with pytest.raises(ValueError, match="excluded source"):
        gather_signal(
            ReleaseSignal.parse(signal(model_name="Orbit 9")),
            root=tmp_path,
            fetch=fetch,
        )


def _http_error(url: str, status: int) -> httpx.HTTPStatusError:
    request = httpx.Request("GET", url)
    response = httpx.Response(status, request=request)
    return httpx.HTTPStatusError(str(status), request=request, response=response)


def _prepare_job(
    monkeypatch: pytest.MonkeyPatch,
    root: Path,
    row: dict[str, object],
    fetch,
) -> tuple[Path, Path, list[str]]:
    pending = root / "pending.json"
    result_path = root / "result.json"
    pending.write_text(json.dumps({"signals": [row]}), encoding="utf-8")
    seen: list[str] = []

    def wrapped(url: str) -> FetchResult:
        seen.append(url)
        return fetch(url)

    monkeypatch.setattr(processor, "_fetch", wrapped)
    monkeypatch.setattr(
        processor.refresh_leaderboards, "run",
        lambda **_: processor.refresh_leaderboards.RefreshReport(),
    )
    return pending, result_path, seen


def test_a_dead_first_seen_page_falls_back_to_the_provider_doc(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    _write_card(tmp_path, "acme", "orbit-1", display="Orbit 1", version="orbit-1")
    host = "models.acme.example"
    _watch_lab(tmp_path, host)
    page = f"https://{host}/orbit-9"
    doc = "https://docs.sibling.example/orbit-9"
    models_dev = "https://models.dev/api.json"
    row = signal(
        model_name="Orbit 9",
        signal_id="watch:acme:dead-first-seen",
        first_seen_url=page,
    )

    def fetch(url: str) -> FetchResult:
        if url == models_dev:
            return FetchResult(models_dev, _listed_doc_payload(doc), "application/json")
        if url == page:
            raise _http_error(url, 404)
        if url == doc:
            return FetchResult(doc, _DOC_IDENTITY, "text/html")
        if url.startswith("https://huggingface.co/api/"):
            return FetchResult(url, b"[]", "application/json")
        raise AssertionError(url)

    pending, result_path, seen = _prepare_job(monkeypatch, tmp_path, row, fetch)
    result = processor.process(
        pending, result_path, root=tmp_path, price_fetcher=_PriceFetcher(),
    )

    assert result["status"] == "new"
    assert result["model_id"] == "acme/orbit-9"
    assert result["identity_basis"] == "json-ld"
    assert result["gather_failures"] == [f"{host}: HTTPStatusError"]
    assert page in seen
    assert doc in seen
    card = tmp_path / "models" / "acme" / "orbit-9.md"
    text = card.read_text(encoding="utf-8")
    front = yaml.safe_load(text.split("---", 2)[1])
    assert front["sources"]["provider_docs_url"] == doc
    assert str(front["release_date"]) == "2026-09-26"
    assert page not in text
    assert result_path.is_file()


def test_a_dead_first_seen_page_and_a_dead_doc_are_uncertain(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _write_card(tmp_path, "acme", "orbit-1", display="Orbit 1", version="orbit-1")
    host = "models.acme.example"
    doc_host = "docs.sibling.example"
    _watch_lab(tmp_path, host)
    page = f"https://{host}/orbit-9"
    doc = f"https://{doc_host}/orbit-9"
    models_dev = "https://models.dev/api.json"
    reason = f"{host}: HTTPStatusError; {doc_host}: HTTPStatusError"
    row = signal(
        model_name="Orbit 9",
        signal_id="watch:acme:dead-first-seen-and-doc",
        first_seen_url=page,
    )

    def fetch(url: str) -> FetchResult:
        if url == models_dev:
            return FetchResult(models_dev, _listed_doc_payload(doc), "application/json")
        if url == page or url == doc:
            raise _http_error(url, 404)
        if url.startswith("https://huggingface.co/api/"):
            return FetchResult(url, b"[]", "application/json")
        raise AssertionError(url)

    pending, result_path, seen = _prepare_job(monkeypatch, tmp_path, row, fetch)
    monkeypatch.setattr(sys, "argv", [
        "process_release_signals",
        "--root", str(tmp_path),
        "--pending", str(pending),
        "--result", str(result_path),
    ])

    assert processor.main() == 0
    output = capsys.readouterr()
    assert "Traceback" not in output.out
    assert "Traceback" not in output.err
    result = json.loads(result_path.read_text(encoding="utf-8"))
    assert result["status"] == "uncertain"
    assert result["model_id"] is None
    assert result["reason"] == reason
    assert page in seen
    assert doc in seen
    assert not (tmp_path / "models" / "acme" / "orbit-9.md").exists()

    from release_signals.pipeline import gather_signal

    clear_catalogue_cache()
    gathered = gather_signal(
        ReleaseSignal.from_queue(row),
        root=tmp_path,
        fetch=fetch,
        discover_huggingface=False,
    )
    assert gathered.resolution.status == "uncertain"
    assert gathered.resolution.reason == reason
    assert gathered.gather_failures == (
        f"{host}: HTTPStatusError",
        f"{doc_host}: HTTPStatusError",
    )


def test_a_first_seen_redirect_to_another_owner_falls_back_to_the_provider_doc(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    _write_card(tmp_path, "acme", "orbit-1", display="Orbit 1", version="orbit-1")
    _huggingface_watch(tmp_path, "AcmeLab")
    requested = "https://huggingface.co/AcmeLab/orbit-9"
    final = "https://huggingface.co/other-user/orbit-9"
    doc = "https://docs.sibling.example/orbit-9"
    models_dev = "https://models.dev/api.json"
    row = signal(
        model_name="Orbit 9",
        signal_id="watch:acme:redirect-owner-doc",
        first_seen_url=requested,
    )

    def fetch(url: str) -> FetchResult:
        if url == models_dev:
            return FetchResult(models_dev, _listed_doc_payload(doc), "application/json")
        if url == requested:
            return FetchResult(final, b"<h1>Acme releases Orbit 9</h1>", "text/html")
        if url == doc:
            return FetchResult(doc, _DOC_IDENTITY, "text/html")
        if url.startswith("https://huggingface.co/api/"):
            return FetchResult(url, b"[]", "application/json")
        raise AssertionError(url)

    pending, result_path, seen = _prepare_job(monkeypatch, tmp_path, row, fetch)
    result = processor.process(
        pending, result_path, root=tmp_path, price_fetcher=_PriceFetcher(),
    )

    assert result["status"] == "new"
    assert result["model_id"] == "acme/orbit-9"
    assert result["identity_basis"] == "json-ld"
    assert result["gather_failures"] == []
    assert requested in seen
    assert doc in seen
    text = (tmp_path / "models" / "acme" / "orbit-9.md").read_text(encoding="utf-8")
    front = yaml.safe_load(text.split("---", 2)[1])
    assert front["sources"]["provider_docs_url"] == doc
    assert str(front["release_date"]) == "2026-09-26"
    assert final not in text
    assert "other-user" not in text


def test_a_gate_refusal_on_the_preferred_first_seen_url_still_raises(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    _write_card(tmp_path, "acme", "orbit-1", display="Orbit 1", version="orbit-1")
    host = "models.acme.example"
    _watch_lab(tmp_path, host)
    page = f"https://{host}/orbit-9"
    doc = "https://docs.sibling.example/orbit-9"
    prohibited = "https://" + "artificial" + "analysis.ai" + "/orbit-9"
    models_dev = "https://models.dev/api.json"
    row = signal(
        model_name="Orbit 9",
        signal_id="watch:acme:gated-first-seen",
        first_seen_url=page,
    )

    def fetch(url: str) -> FetchResult:
        if url == models_dev:
            return FetchResult(models_dev, _listed_doc_payload(doc), "application/json")
        if url == page:
            return FetchResult(prohibited, b"<h1>Acme releases Orbit 9</h1>", "text/html")
        raise AssertionError(url)

    pending, result_path, seen = _prepare_job(monkeypatch, tmp_path, row, fetch)
    with pytest.raises(ValueError, match="excluded source") as caught:
        processor.process(
            pending, result_path, root=tmp_path, price_fetcher=_PriceFetcher(),
        )

    assert not isinstance(caught.value, RequiredSourceError)
    assert page in seen
    assert doc not in seen
    assert not result_path.exists()
    assert not (tmp_path / "models" / "acme" / "orbit-9.md").exists()


def test_a_release_signal_test_starts_with_an_empty_catalogue_cache() -> None:
    from release_signals import pipeline as release_pipeline

    assert release_pipeline._SLUG_INDEX == {}
    assert release_pipeline._HF_ORG_INDEX == {}
