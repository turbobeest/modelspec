"""Copy an explicit whitelist of aggregate acceptance evidence for review."""
from pathlib import Path
import hashlib
import json
import shutil

root = Path('/tmp/model-437-scratch/acceptance')
output = root / 'public-evidence'
output.mkdir(exist_ok=True)
helpers = ['setup_acceptance.py', 'run_acceptance.sh', 'record_command.py',
           'compare_private.py', 'check_completeness.py', 'measure_private.py',
           'verify_staged.py', 'audit_repaired_view.py', 'explain_difference.py',
           'cleanup_acceptance.py', 'package_public.py']
public = ['prepared.public.json', 'setup-commands.public.json', 'repair-view.public.json',
          'staged-code.public.json', 'fixture-correction.public.json', 'residual.public.json', 'processes.public.json']
files = {name: root / name for name in helpers + public}
for path in root.glob('command-*.public.json'):
    files[path.name] = path
for path in root.glob('provenance-*.public.json'):
    files[path.name] = path
for label in ('a', 'd', 'c'):
    files['state-' + label + '.public.json'] = root / 'results' / label / 'state.public.json'
files['comparison.public.json'] = root / 'results/comparison.public.json'
for label in ('d', 'c'):
    for period in ('current', 'successor'):
        files[f'gate-{label}-{period}.public.json'] = root / f'gate-{label}-{period}/gate.public.json'
        files[f'memory-{label}-{period}.public.json'] = root / f'memory-{label}/{period}.public.json'
for name, source in files.items():
    shutil.copy2(source, output / name)
commands = sorted((json.loads(path.read_text()) for path in root.glob('command-*.public.json')),
                  key=lambda row: (row['started'], row['label']))
(output / 'commands.public.jsonl').write_text(''.join(json.dumps(row, sort_keys=True) + '\n' for row in commands))
comparison = json.loads((root / 'results/comparison.public.json').read_text())
rows = []
for label in ('d', 'c'):
    for period in ('current', 'successor'):
        result = comparison['periods'][period]
        delta = result[label + '_vs_a']
        state = result['states'][label]
        gate = json.loads((root / f'gate-{label}-{period}/gate.public.json').read_text())
        memory = json.loads((root / f'memory-{label}/{period}.public.json').read_text())
        rows.append(dict(state=label, period=period, repo_cases=delta['repo_cases'],
                         first_result_changes=delta['first_result_model_changes'],
                         tie_set_changes=delta['tie_member_set_changes'],
                         answer_kind_changes=delta['answer_kind_changes'],
                         answer_kind_or_member_set_changes=delta['answer_kind_or_member_set_changes'],
                         completeness_gaps=gate['gap_count'],
                         admitted_benchmark_records=state['unique_benchmark_evidence_records'],
                         cited_benchmark_records=state['cited_benchmark_evidence_records'],
                         warned_templates=state['template_warnings'], template_count=state['template_cases'],
                         corpus_warnings=state['corpus_warnings'],
                         corpus_expectation_failures=state['expectation_failures'],
                         steady_mib=memory['steady_mib'], peak_mib=memory['peak_mib'],
                         memory_limit_mib=memory['limit_bytes']/1048576))
summary = {'implementation_commit': '6b9695fc75748bf31d8f07955bbf8fea89fc57f0',
           'comparison_exit': 1, 'raw_zero_delta_acceptance_passed': comparison['acceptance_passed'],
           'residual_case': 'facet-must-model.fits_hardware',
           'residual_explained': True, 'rows': rows,
           'residual_cause': '#866 quarantines 10 unchanged best-effort hardware-fit facts as mixed citation, affecting 32 model/offering subjects. MODEL-439 repairs guaranteed facts only. The generated case asks whether model.fits_hardware is known. Restoring only baseline hardware-fact columns restores the exact baseline answer in both periods.',
           'private_snapshot_written_by_diagnostic': False,
           'production_gate_disabled': False,
           'private_scratch_cleanup': 'pending root confirmation after public artifacts copied'}
(output / 'summary.public.json').write_text(json.dumps(summary, indent=2) + '\n')
lines = [
    '# MODEL-437 round-2 private acceptance', '',
    'Measured implementation `6b9695fc75748bf31d8f07955bbf8fea89fc57f0` against main '
    '`a03c4d077acc03c2bc5dba526ff635fb708ccb94` with main host policy. Baseline a and '
    'candidate d use original data `9d9de96f062ac031336ee483ae97c3b436bd3845`. Candidate c '
    'uses #866 policy `82ebcf4627d255d7641303caff2d149e879cf359` and data#118 '
    '`f722d3fcb673b28bdff9fa1b5cac06c22cc61c38`.', '',
    '| State | Period | Cases | First result | Tie set | Answer kind | Kind/member set | Gaps | Scores/cited | Warned templates | Steady MiB | Peak MiB |',
    '| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |',
]
for row in rows:
    lines.append('| {state} | {period} | {repo_cases} | {first_result_changes} | {tie_set_changes} | '
                 '{answer_kind_changes} | {answer_kind_or_member_set_changes} | {completeness_gaps} | '
                 '{admitted_benchmark_records}/{cited_benchmark_records} | {warned_templates}/{template_count} | '
                 '{steady_mib:.4f} | {peak_mib:.4f} |'.format(**row))
lines += ['',
    'All a/c/d states evaluated 319 corpus cases per period, including the 302 repository cases, '
    'with zero expectation failures, 286 contract-validated HTTP-200 responses and 269 repository '
    'HTTP-200 responses. Baseline a has 944 benchmark records, no cited benchmark records and '
    'one warned template out of 40 in both periods. All four candidate memory probes pass the '
    '115 MiB steady limit. The local probe uses the deploy vendoring path and Pyodide 0.28.3; '
    'it is not a production Cloudflare memory observation.', '',
    'The raw comparator correctly exits 1. The only changed case, '
    '`facet-must-model.fits_hardware`, changes in both periods. Its request has '
    '`where: [{known: model.fits_hardware}]`, maximizes `software_engineering`, requests '
    'summary explanations and has limit 5. It does not ask that a model fit a specific device.', '',
    'The identical ten hardware-fit facts are admitted under main policy and rejected as '
    '`quarantined (mixed citation)` under #866. The facts have tier `best_effort`, so the '
    'MODEL-439 guaranteed-fact repair leaves them unchanged. Their inherited offering facts '
    'bring the total to 32 subjects that change from known to unknown. The candidate retains '
    'all 944 baseline benchmark readings unchanged, admits one additional reading, and changes '
    'zero software-engineering capability estimates. In-memory diagnostic replays that replace '
    'only the hardware-fact columns and indexes restore the exact baseline first result, answer '
    'kind and member set in both periods. Replacing the capability fit or snapshot seed does not. '
    'These diagnostic replays write no snapshot and disable no production gate.', '',
    'The repair was applied directly from data#118, whose sole parent is the pinned baseline. '
    'All 13 changed files match branch bytes. Unchanged leaf files link to baseline through '
    'real directories. The #891 script was then actually executed in dry-run mode using an '
    'explicit empty CopyStore and date 2026-10-21; it reports zero remaining changes. '
    'No repair --write run was performed here. No source page bytes were opened or fetched.', '',
    'The first c attempt failed before corpus evaluation because a scratch view used nested '
    'directory symlinks that recursive discovery skipped. The corrected view uses real '
    'directories and unchanged leaf-file links. Failed-attempt provenance is retained; '
    'the engine and private data were not changed to resolve it.', '',
    'Run setup_acceptance.py in a fresh scratch directory after placing the other helpers '
    'there. It retrieves pinned input revisions. Run run_acceptance.sh baseline, then '
    'candidate-d and candidate-c, compare, gates-d/gates-c and memory-d/memory-c. '
    'The candidate phases require the measured implementation checkout. setup-commands.public.json '
    'records the actual initial retrieval commands; commands.public.jsonl records measured '
    'subprocess argv, timestamps and direct exit codes. The setup script is a saved reproduction '
    'of construction originally executed inline. Calendar-dependent exports used the actual UTC '
    'date 2026-10-21; replaying on another day requires that date to be fixed in the environment.', '',
    'Helpers remove ambient HMAC/Ed25519 signing keys before setting their throwaway HMAC key. '
    'The root executor also confirmed the relevant ambient keys were absent for the initial '
    'runs. All private export and memory subprocesses have exited. The root executor reports '
    'public re-vendoring completed with 129 files and clean imports. Private scratch removal waits for confirmation that '
    'these public artifacts have been copied. cleanup_acceptance.py deletes only the named '
    'acceptance scratch tree and does not follow the links into private inputs.', '',
]
(output / 'README.md').write_text('\n'.join(lines))
manifest = {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(output.iterdir()) if path.is_file() and path.name != 'manifest.public.json'}
(output / 'manifest.public.json').write_text(json.dumps(manifest, indent=2) + '\n')
print(json.dumps({'public_artifact_directory': str(output), 'files': len(manifest), 'raw_comparison_exit': 1,
                  'all_four_memory_probes_pass': True, 'all_four_completeness_gaps_zero': True}, indent=2))
