"""The decide reference describes the current hosted transport."""

import gzip
import json
import re
from pathlib import Path

from decision.contract import CONTRACT_VERSION
from pipeline.public_data import restrict
from tests.test_snapshot_successor import signed_pair as signed_pair, utc_clock as utc_clock
from tests.test_x402 import entry as entry

ROOT = Path(__file__).resolve().parents[1]


def test_decide_reference_current_contract_matches_implementation():
    text = (ROOT / 'docs/decide-api.md').read_text()
    current = re.search(r'current compatible contract release is\s*`([^`]+)`', text)
    assert current is not None
    assert current.group(1) == CONTRACT_VERSION
    examples = [json.loads(block) for block in re.findall(r'```json\n(.*?)```', text, re.S)]
    versions = [body['contract_version'] for body in examples if 'contract_version' in body]
    assert versions and set(versions) == {CONTRACT_VERSION}


def test_decide_reference_describes_split_serving_and_legacy_exports(tmp_path):
    (tmp_path / '_headers').write_text('')
    snapshot = tmp_path / 'api/decision/snapshot.json.gz'
    snapshot.parent.mkdir(parents=True)
    snapshot.write_bytes(gzip.compress(b'{"snapshot_id":"synthetic"}'))
    restrict(tmp_path)
    assert json.loads(gzip.decompress(snapshot.read_bytes()))['error'] == 'removed'
    assert json.loads((tmp_path / 'api/decision/vocabulary.json').read_text())['error'] == 'removed'

    text = (ROOT / 'docs/decide-api.md').read_text()
    architecture = text.split('## Request')[0]
    assert 'DATA_SPLIT_ENABLED' in architecture
    assert 'bundled_data.py' in architecture
    assert 'thin HTTP client' in architecture
    assert 'tombstone' in architecture
    assert 'legacy' in architecture.lower()
    refresh = text.split('## Snapshot refresh')[1].split('## Access')[0]
    assert '/v1/vocabulary' in refresh
    assert 'Worker deploy' in refresh
    assert 'legacy' in refresh.lower()


def test_decide_reference_bundled_comparison_does_not_fetch_public_history(
    entry, monkeypatch, utc_clock, signed_pair,
):
    from datetime import UTC, datetime

    from tests.test_snapshot_successor import SPEC, deploy, request

    utc_clock[0][0] = datetime(2026, 11, 30, tzinfo=UTC)
    worker, module, bundle = deploy(entry, monkeypatch, utc_clock, *signed_pair)
    current = request(worker)
    assert current.status == 200
    snapshot_id = current.json()['snapshot']
    path = module.DECISION_HISTORY_TEMPLATE.format(snapshot_id=snapshot_id)
    bundle.blobs.pop(path)

    async def unexpected_fetch(*args, **kwargs):
        raise AssertionError('a bundled comparison must not fetch public history')

    monkeypatch.setattr(module, 'fetch', unexpected_fetch)
    response = request(worker, '/v1/compare', {'spec': SPEC, 'compare_to': snapshot_id})
    assert response.status == 409
    assert response.json()['error']['code'] == 'comparison_snapshot_unavailable'
    text = (ROOT / 'docs/decide-api.md').read_text()
    section = ' '.join(text.split('### Comparing snapshots')[1].split('## Response')[0].split())
    assert 'never falls back to the public origin' in section
    assert 'absent from that bundle' in section
    assert 'legacy non-split' in section
    recovery = next(line for line in text.splitlines()
                    if line.startswith('| 409 | `comparison_snapshot_unavailable`'))
    assert 'public blog availability alone is insufficient' in recovery


def test_decide_reference_describes_bundled_successor_transition(
    entry, monkeypatch, utc_clock, signed_pair,
):
    from datetime import UTC, datetime

    from tests.test_snapshot_successor import BOUNDARY, SPEC, deploy, request

    utc_clock[0][0] = datetime(2026, 11, 30, 23, 59, 59, tzinfo=UTC)
    worker, _, _ = deploy(entry, monkeypatch, utc_clock, *signed_pair)
    before = request(worker)
    assert before.status == 200
    old_id = before.json()['snapshot']
    utc_clock[0][0] = BOUNDARY
    after = request(worker)
    assert after.status == 200
    assert after.json()['snapshot'] != old_id
    pinned = request(worker, payload=SPEC | {'snapshot': old_id})
    assert pinned.status == 409
    assert pinned.json()['error']['code'] == 'snapshot_not_loaded'
    vocabulary = request(worker, '/v1/vocabulary')
    assert vocabulary.status == 200
    assert vocabulary.json()['snapshot'] == after.json()['snapshot']
    text = (ROOT / 'docs/decide-api.md').read_text()
    refresh = ' '.join(text.split('## Snapshot refresh')[1].split('## Access')[0].split())
    assert 'successor' in refresh
    assert 'without a deploy' in refresh
    assert 'current valid period' in refresh
