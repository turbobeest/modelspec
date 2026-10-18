"""A retained-snapshot fetch can finish after the selected current prices expire."""

import asyncio
import sys
from datetime import UTC, datetime
from types import SimpleNamespace
from urllib.parse import urlparse

import pytest

from decision.snapshot import load_snapshot_bytes
from tests.test_snapshot_successor import (
    BOUNDARY,
    KEY,
    SPEC,
    deploy,
    request,
)
from tests.test_snapshot_successor import (
    signed_pair as signed_pair,
)
from tests.test_snapshot_successor import (
    utc_clock as utc_clock,
)
from tests.test_x402 import entry as entry


@pytest.mark.parametrize(
    "has_successor,pinned,history_status,expected_status,error_code",
    [
        (True, False, 200, 200, None),
        (True, True, 200, 409, "snapshot_changed"),
        (True, False, 404, 409, "comparison_snapshot_unavailable"),
        (False, False, 200, 503, "no_snapshot"),
        (False, False, 404, 503, "no_snapshot"),
    ],
    ids=["unpinned", "old-pin", "history-missing", "no-successor", "both-unavailable"],
)
def test_compare_refreshes_current_after_history_fetch_crosses_midnight(
    entry, monkeypatch, utc_clock, signed_pair,
    has_successor, pinned, history_status, expected_status, error_code,
):
    utc_clock[0][0] = datetime(2026, 11, 30, 23, 59, 59, tzinfo=UTC)
    worker, module, _ = deploy(entry, monkeypatch, utc_clock, signed_pair[0],
                               signed_pair[1] if has_successor else None)
    primary, successor = [load_snapshot_bytes(raw, key=KEY, public_keys={})
                          for raw in signed_pair]
    history_path = module.DECISION_HISTORY_TEMPLATE.format(snapshot_id=primary.snapshot_id)
    original_read = module._bundled_read
    selected_before_fetch = []

    def bundled_read(url):
        if urlparse(url).path == history_path:
            return False, None
        return original_read(url)

    class HistoryResponse:
        status = history_status
        headers = {"etag": "retained-primary"}

        async def arrayBuffer(self):  # noqa: N802 - Cloudflare fetch response API.
            return signed_pair[0]

    async def history_fetch(url, options):
        assert urlparse(url).path == history_path
        selected = module._decision_holder(worker.env.EXPORT_ORIGIN).snapshot
        assert selected is not None
        assert selected.snapshot_id == primary.snapshot_id
        selected_before_fetch.append(selected.snapshot_id)
        await asyncio.sleep(0)
        utc_clock[0][0] = BOUNDARY
        return HistoryResponse()

    monkeypatch.setattr(module, "_bundled_read", bundled_read)
    monkeypatch.setattr(module, "fetch", history_fetch)
    monkeypatch.setattr(sys.modules["js"], "Uint8Array", SimpleNamespace(
        new=lambda raw: SimpleNamespace(to_py=lambda: raw)), raising=False)

    response = request(worker, "/v1/compare", {
        "spec": SPEC,
        "compare_to": primary.snapshot_id,
    }, expected=primary.snapshot_id if pinned else None)

    assert selected_before_fetch == [primary.snapshot_id]
    body = response.json()
    assert response.status == expected_status, body
    if not has_successor:
        assert body["error"] == "no_snapshot"
        assert body["snapshot"] is None
        assert "x-modelspec-snapshot" not in response.headers
    else:
        assert body["snapshot"] == successor.snapshot_id
        assert response.headers["x-modelspec-snapshot"] == successor.snapshot_id
        if error_code is not None:
            assert body["error"]["code"] == error_code
        else:
            assert body["compare_to"] == primary.snapshot_id
