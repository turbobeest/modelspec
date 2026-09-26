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

from decision.excluded import REMOVED_HOSTS
from release_signals.contract import ReleaseSignal, SignalError, sign
from release_signals.pipeline import (
    ChangePolicy,
    FetchResult,
    FirecrawlBudget,
    draft_signal,
    require_allowed_source,
    resolve_signal,
)

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


def test_v1_schema_accepts_the_documented_contract_and_rejects_guesses() -> None:
    schema = json.loads(
        (ROOT / "schemas" / "release-signal-v1.schema.json").read_text(encoding="utf-8")
    )

    parsed = ReleaseSignal.parse(signal())

    assert parsed.model_name == "Orbit 2"
    assert schema["$id"].endswith("release-signal-v1.schema.json")
    assert schema["required"] == [
        "model_name",
        "provider",
        "first_seen_url",
        "timestamp",
        "confidence",
        "signal_id",
    ]
    for bad in (
        signal(confidence=1.01),
        signal(timestamp="2026-09-26"),
        signal(first_seen_url="https://example.com/announcement"),
        signal(extra="not in v1"),
    ):
        with pytest.raises(SignalError):
            ReleaseSignal.parse(bad)


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


def test_fake_provider_page_drafts_a_valid_card_and_never_cites_x(tmp_path: Path) -> None:
    _write_card(tmp_path, "acme", "orbit-1", display="Orbit 1", version="orbit-1")
    primary_url = "https://acme.example/models/orbit-2"
    models_dev_url = "https://models.dev/api.json"
    models_dev = {
        "acme": {
            "name": "Acme",
            "models": {
                "orbit-2": {
                    "id": "orbit-2",
                    "name": "Orbit 2",
                    "release_url": primary_url,
                }
            },
        }
    }
    replies = {
        models_dev_url: FetchResult(
            url=models_dev_url,
            body=json.dumps(models_dev).encode(),
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
    assert front["sources"]["provider_docs_url"] == primary_url
    assert front["sources"]["models_dev_url"] == "https://models.dev/acme"
    assert front["sources"]["last_scraped_models_dev"] == "2026-09-26"
    assert "x.com" not in result.card_path.read_text(encoding="utf-8")
    assert result.evidence_urls == (primary_url, models_dev_url)
    assert result.firecrawl_credits == 0


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


def test_worker_endpoint_ships_off_and_vendors_the_shared_contract() -> None:
    wrangler = (ROOT / "api" / "worker" / "wrangler.jsonc").read_text(encoding="utf-8")
    vendor = (ROOT / "api" / "worker" / "vendor.py").read_text(encoding="utf-8")
    entry = (ROOT / "api" / "worker" / "src" / "entry.py").read_text(encoding="utf-8")

    assert '"SIGNALS_ENABLED": "false"' in wrangler
    assert 'Path("release_signals/contract.py")' in vendor
    assert '"POST /v1/signals"' in entry
    assert '"GET /v1/signals/pending"' in entry
