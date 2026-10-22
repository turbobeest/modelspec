"""Reproduce public golden bytes and isolate snapshot-format identity changes."""
from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path
import subprocess
from unittest.mock import patch

import pytest

from decision import snapshot as snapshot_module
from decision.bands import BASIS
from decision.contract import parse_spec
from decision.engine import decide
from tests import test_decision_link as link
from tests import test_decision_plans as plans
from tests import test_decide_worker as worker
from tests.test_x402 import entry

OUT = Path('/tmp/model-437-scratch/contract-audit')
OUT.mkdir(parents=True, exist_ok=True)


def changes(before, after, path='$'):
    if type(before) is not type(after):
        return [{'path': path, 'before': before, 'after': after}]
    if isinstance(before, dict):
        result = []
        for key in sorted(before.keys() | after.keys()):
            if key not in before or key not in after:
                result.append({'path': f'{path}.{key}',
                               'before': before.get(key), 'after': after.get(key)})
            else:
                result.extend(changes(before[key], after[key], f'{path}.{key}'))
        return result
    if isinstance(before, list):
        if len(before) != len(after):
            return [{'path': path, 'before': before, 'after': after}]
        return [item for index, (a, b) in enumerate(zip(before, after))
                for item in changes(a, b, f'{path}[{index}]')]
    return [] if before == after else [{'path': path, 'before': before, 'after': after}]


def plan_projection(decision, golden):
    body = decision.model_dump(mode='json')
    body['contract_version'] = golden['contract_version']
    for key in ('bands', 'blend', 'feedback', 'reading'):
        body.pop(key, None)
    return json.loads(json.dumps(body, sort_keys=True).replace(
        json.dumps(BASIS),
        json.dumps('leader-overlap score intervals; capability estimates use 80% intervals')))


report = {'base_commit': '44f3bdb5',
          'method': 'Only decision.snapshot.FORMAT_VERSION varies between fixture builds.',
          'plan_snapshots': [], 'plans': [], 'worker_snapshot': {}, 'link': []}
goldens = json.loads(subprocess.check_output(
    ['git', 'show', '44f3bdb5:tests/fixtures/model-200-no-access.json'], text=True))
for covered, group, count in ((False, 'undisclosed', len(plans.NO_ACCESS_SPECS)),
                              (True, 'sourced_without_estate', 3)):
    snapshots = {}
    contents = {}
    for version in (1, 2):
        with patch.object(snapshot_module, 'FORMAT_VERSION', version):
            raw, snapshots[version] = plans._load(covered)
        contents[version] = json.loads(gzip.decompress(raw))['content']
    content_diffs = changes(contents[1], contents[2])
    assert content_diffs == [{'path': '$.format_version', 'before': 1, 'after': 2}], content_diffs
    report['plan_snapshots'].append({'group': group, 'diffs': content_diffs,
                                    'format1': snapshots[1].snapshot_id,
                                    'format2': snapshots[2].snapshot_id})
    for index in range(count):
        golden = goldens[group][index]
        spec = parse_spec(plans.NO_ACCESS_SPECS[index], facets=None)
        bodies = {version: plan_projection(decide(spec, value), golden)
                  for version, value in snapshots.items()}
        assert bodies[1] == golden, changes(golden, bodies[1])
        diffs = changes(bodies[1], bodies[2])
        assert {row['path'] for row in diffs} == {'$.decision_id', '$.snapshot'}, diffs
        report['plans'].append({'group': group, 'index': index,
                                'format1_matches_original_golden': True, 'diffs': diffs})

snapshots = {}
contents = {}
for version in (1, 2):
    with patch.object(snapshot_module, 'FORMAT_VERSION', version):
        raw = worker.snapshot_bytes.__wrapped__()
        snapshots[version] = worker.snapshot.__wrapped__(raw)
    contents[version] = json.loads(gzip.decompress(raw))['content']
content_diffs = changes(contents[1], contents[2])
assert content_diffs == [{'path': '$.format_version', 'before': 1, 'after': 2}], content_diffs
report['worker_snapshot'] = {'diffs': content_diffs, 'format1': snapshots[1].snapshot_id,
                             'format2': snapshots[2].snapshot_id}
cases = (
    ({'fields': None}, '3dbe68054a3b321009d03eb836960864293a75f254450e8f81d3f034feecc657'),
    ({'fields': ['model']}, 'a1a9d9368d44471a8df735a172e72cd1097503eb97963e96b5eba3a6d7fa7e02'),
    ({'fields': None, 'evidence_for': 'lab/a'}, '53882129c52ad97377f85e828b63fe01b86f344e23c3954a70ebc758736b4dd3'),
)
for controls, old_digest in cases:
    bodies = {}
    digests = {}
    for version in (1, 2):
        with pytest.MonkeyPatch.context() as monkeypatch:
            module = entry.__wrapped__(monkeypatch)
            app = link.worker_for(module, snapshots[version], monkeypatch,
                                  DECISION_LINK_ENABLED='false')
            response = link.decide(app, **controls)
            assert response.status == 200
            raw = link._response_bytes_at_base_contract(response)
            bodies[version] = json.loads(raw)
            digests[version] = hashlib.sha256(raw).hexdigest()
    assert digests[1] == old_digest, (controls, digests)
    diffs = changes(bodies[1], bodies[2])
    assert {row['path'] for row in diffs} == {
        '$.decision_id', '$.snapshot', '$.coverage.snapshot'}, diffs
    report['link'].append({'controls': controls, 'format1_matches_original_digest': True,
                           'digests': digests, 'diffs': diffs})

path = OUT / 'golden_identity_audit.json'
path.write_text(json.dumps(report, indent=2) + '\n')
print(f'PASS: 9 plan golden responses and 3 Worker golden hashes reproduced at format1; '
      f'format2 changes only snapshot and decision IDs. Evidence: {path}')
