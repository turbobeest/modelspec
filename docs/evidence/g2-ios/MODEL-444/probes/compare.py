"""Compare 302 catalogue outcomes and the separate 17 fixture outcomes."""
from pathlib import Path
import importlib.util
import json
import sys

root = Path('/tmp/model-444-scratch/probes')
base_dir, candidate_dir = map(Path, sys.argv[1:3])
base = json.loads((base_dir / 'state.private.json').read_text())
candidate = json.loads((candidate_dir / 'state.private.json').read_text())
helper = root / 'engine-base/docs/evidence/g2-ios/MODEL-439/r2/compare_private.py'
spec = importlib.util.spec_from_file_location('compare_private', helper)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
assert set(base) == set(candidate) == {'current','successor'}
report = {'baseline':base_dir.name,'candidate':candidate_dir.name,'periods':{}}
for period in base:
    before,after = base[period],candidate[period]
    assert before['as_of'] == after['as_of']
    summary = module.compare(before,after)
    predictions_before,predictions_after = before['predictions'],after['predictions']
    assert set(predictions_before) == set(predictions_after)
    fixtures = [case for case,value in predictions_before.items() if value['snapshot'] != 'repo']
    summary['fixture_cases'] = len(fixtures)
    summary['fixture_changed_cases'] = [case for case in fixtures if predictions_before[case] != predictions_after[case]]
    summary['changed_catalogue_fields'] = {case:[key for key,value in predictions_before[case].items() if value!=predictions_after[case][key]]
                                          for case in predictions_before if predictions_before[case]['snapshot']=='repo' and predictions_before[case]!=predictions_after[case]}
    summary['snapshot_id_equal'] = before['snapshot_id']==after['snapshot_id']
    summary['as_of'] = before['as_of']
    summary['baseline_expectation_failures'] = before['expectation_failures']
    summary['candidate_expectation_failures'] = after['expectation_failures']
    report['periods'][period] = summary
    assert summary['repo_cases']==302 and summary['fixture_cases']==17
public = candidate_dir / 'comparison.public.json'
public.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
raise SystemExit(int(any(row['candidate_expectation_failures'] or row['fixture_changed_cases'] for row in report['periods'].values())))
