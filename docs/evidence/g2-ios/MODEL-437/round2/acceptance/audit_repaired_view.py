"""Prove the repair view matches its branch without reading retained page bytes."""
from pathlib import Path
import json
import subprocess

root = Path('/tmp/model-437-scratch/acceptance')
data = root / 'modelspec-data'
repaired = root / 'prepared/repaired-data'
base = '9d9de96f062ac031336ee483ae97c3b436bd3845'
revision = 'f722d3fcb673b28bdff9fa1b5cac06c22cc61c38'


def git(*args):
    return subprocess.run(['git', '-C', str(data), *args], check=True, capture_output=True).stdout


changed = {Path(p.decode()) for p in git('diff', '--name-only', '-z', base, revision).split(b'\0') if p}
parents = [line.split()[1] for line in git('cat-file', '-p', revision).decode().splitlines()
           if line.startswith('parent ')]
links = 0
files = 0


def check(directory, relative=Path()):
    global links, files
    assert {p.name for p in directory.iterdir()} == {
        p.name for p in (data / relative).iterdir() if p.name != '.git'}
    for entry in directory.iterdir():
        item = relative / entry.name
        if entry.is_symlink():
            assert not any(item == path or item in path.parents for path in changed)
            assert entry.resolve() == (data / item).resolve()
            links += 1
        elif entry.is_dir():
            check(entry, item)
        else:
            assert item in changed
            assert entry.read_bytes() == git('show', revision + ':' + str(item))
            files += 1


check(repaired)
assert files == len(changed) == 13
report = {
    'baseline_data': base, 'repaired_data': revision, 'repair_commit_parents': parents,
    'repair_directly_descends_from_baseline': parents == [base],
    'changed_branch_files': len(changed), 'changed_files_match_branch_bytes': True,
    'unchanged_leaf_files_are_links_to_original': True, 'unchanged_link_count': links,
    'all_repaired_view_directories_are_real': True,
    'retained_page_bytes_read_for_audit': 0, 'repair_application': 'exact branch files applied directly',
    'repair_script_execution': 'dry-run only, no --write; explicit empty CopyStore',
}
private_log = root / 'repair-dry-run.private.log'
if private_log.exists():
    dry_run = json.loads(private_log.read_text())
    report['repair_dry_run_counts'] = dry_run['counts']
    report['repair_dry_run_remaining_changes'] = len(dry_run['changes'])
    assert not dry_run['changes']
(root / 'repair-view.public.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
