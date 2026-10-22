"""Prove regenerated public-budget probability changes come from snapshot identity."""
import gzip
import json
from pathlib import Path
import subprocess
from unittest.mock import patch

from decision import snapshot as snapshot_module
from qa import decide_budget
from tests.test_decide_worker import _load_service

OUT = Path('/tmp/model-437-scratch/contract-audit')
OUT.mkdir(parents=True, exist_ok=True)
baseline = json.loads(subprocess.check_output([
    'git', 'show', '44f3bdb5:mcp/test/fixtures/decide-budget.json']))
raw_path = OUT / 'budget_format1_snapshot.json.gz'
load = decide_budget.load_snapshot_bytes


def capture(raw, **kwargs):
    raw_path.write_bytes(raw)
    return load(raw, **kwargs)


if raw_path.exists():
    snapshot = load(raw_path.read_bytes(), key=decide_budget.KEY)
else:
    with patch.object(snapshot_module, 'FORMAT_VERSION', 1), \
            patch.object(decide_budget, 'load_snapshot_bytes', capture):
        snapshot = decide_budget.public_snapshot()
actual = decide_budget.responses(_load_service(), snapshot)
for key in ('default', 'drill_down', 'speech'):
    assert actual[key]['projects_contract'] == '2.19'
    assert baseline[key]['projects_contract'] == '2.18'
    actual[key]['projects_contract'] = '2.18'
(OUT / 'budget_format1_response.json').write_text(json.dumps(actual, indent=2) + '\n')


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


report = {
    'base_commit': '44f3bdb5',
    'format1_snapshot': snapshot.snapshot_id,
    'entire_original_fixture_reproduced': actual == baseline,
    'diffs': changes(baseline, actual),
    'normalization': 'projects_contract 2.19 -> 2.18 only, on all three response bodies',
}
content = json.loads(gzip.decompress(raw_path.read_bytes()))['content']
content['format_version'] = 2
digest = snapshot_module.content_hash(content)
built = snapshot_module.Snapshot(
    content=content, content_hash=digest,
    snapshot_id=snapshot_module.snapshot_id_for(digest))
format2 = load(built.to_bytes(key=decide_budget.KEY), key=decide_budget.KEY)
generated = json.loads(decide_budget.FIXTURE.read_text())
fresh = decide_budget.responses(_load_service(), format2)
assert fresh == generated, changes(generated, fresh)
report['format2_snapshot'] = format2.snapshot_id
report['format2_reproduces_regenerated_fixture'] = True
report['format2_changed_paths'] = changes(baseline, fresh)
report['cited_evidence_records'] = len(content.get('cited_evidence_records', []))
# Counterfactual seed replay: retain every estimate, record and current response
# field, changing only the snapshot identity supplied to the decision engine.
format2.snapshot_id = baseline['default']['snapshot']
seed_replay = decide_budget.responses(_load_service(), format2)
for key in ('default', 'drill_down', 'speech'):
    seed_replay[key]['projects_contract'] = '2.18'
assert seed_replay == baseline, changes(baseline, seed_replay)
report['old_snapshot_identity_reproduces_entire_original_fixture'] = True
report['interpretation'] = (
    'All observed response changes are contract versions and snapshot identity, '
    'including probability draws seeded by that identity. Original snapshot '
    'identity reproduces every original field and p_best value with current data.')
(OUT / 'budget_identity_audit.json').write_text(json.dumps(report, indent=2) + '\n')
print('PASS: format2 reproduces regenerated fixture; replaying original snapshot '
      'identity reproduces every original field including all p_best values.')
