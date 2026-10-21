"""Recreate pinned MODEL-437 round-2 inputs in a fresh scratch directory.

Private research files remain untouched in the required git clone. The repaired
view links unchanged files and reads only the 13 paths changed by data PR #118.
No source pages are fetched, opened, or copied by dataset preparation.
"""
from __future__ import annotations

import io
import json
import os
from pathlib import Path
import subprocess
import tarfile

ROOT = Path('/tmp/model-437-scratch/acceptance')
SHAS = {
    'engine_main': 'a03c4d077acc03c2bc5dba526ff635fb708ccb94',
    'host_policy': '82ebcf4627d255d7641303caff2d149e879cf359',
    'repair_engine': '77a9566822f7a23e322d2647913c755ad3cb7ed8',
    'baseline_data': '9d9de96f062ac031336ee483ae97c3b436bd3845',
    'repaired_data': 'f722d3fcb673b28bdff9fa1b5cac06c22cc61c38',
}


def call(*command):
    env = dict(os.environ, PATH='/Users/terbeest/.nvm/versions/node/v22.22.3/bin:' + os.environ.get('PATH', ''))
    return subprocess.run(command, check=True, capture_output=True, env=env).stdout


def git(repo, *args):
    return call('git', '-C', str(repo), *args)


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    refs = ROOT / 'engine-refs'
    data = ROOT / 'modelspec-data'
    prepared = ROOT / 'prepared'
    if any(path.exists() for path in (refs, data, prepared)):
        raise SystemExit('Use a fresh acceptance scratch directory; inputs already exist')
    call('git', 'clone', '--quiet', '--depth', '1',
         'https://github.com/turbobeest/modelspec-data.git', str(data))
    git(data, 'fetch', '--quiet', '--depth', '1', 'origin', SHAS['baseline_data'])
    git(data, 'checkout', '--quiet', '--detach', SHAS['baseline_data'])
    git(data, 'fetch', '--quiet', '--depth', '1', 'origin', SHAS['repaired_data'])
    call('git', 'init', '--quiet', str(refs))
    git(refs, 'remote', 'add', 'origin', 'https://github.com/turbobeest/modelspec.git')
    for name in ('engine_main', 'host_policy', 'repair_engine'):
        git(refs, 'fetch', '--quiet', '--depth', '1', 'origin', SHAS[name])
    prepared.mkdir()
    with tarfile.open(fileobj=io.BytesIO(git(refs, 'archive', SHAS['engine_main']))) as archive:
        archive.extractall(prepared / 'main', filter='data')
    (prepared / 'hosts-866.json').write_bytes(
        git(refs, 'show', SHAS['host_policy'] + ':registry/source-retention.json'))
    for name in ('compare_private.py', 'check_completeness.py', 'measure_private.py'):
        text = git(refs, 'show', SHAS['repair_engine'] +
                   ':docs/evidence/g2-ios/MODEL-439/' + name).decode()
        if name in {'compare_private.py', 'measure_private.py'}:
            text = text.replace('MODEL-439', 'MODEL-437 round 2').replace(
                'model439-private-proof-throwaway-key', 'model437-round2-private-proof-throwaway-key')
        if name == 'compare_private.py':
            text = text.replace('for label in "bc" if label in states',
                                'for label in "cd" if label in states')
        if name in {'compare_private.py', 'check_completeness.py'}:
            text = text.replace('os.environ.pop("MODELSPEC_SOURCE_CACHE", None)',
                                'os.environ.pop("MODELSPEC_SOURCE_CACHE", None)\n    os.environ.pop("MODELSPEC_SNAPSHOT_ED25519_KEY", None)')
        if name == 'measure_private.py':
            text = text.replace('env.pop("MODELSPEC_SOURCE_CACHE", None)',
                                'env.pop("MODELSPEC_SOURCE_CACHE", None)\n    env.pop("MODELSPEC_SNAPSHOT_ED25519_KEY", None)')
        (ROOT / name).write_text(text)
    (ROOT / 'refile_mixed_citations.py').write_bytes(git(
        refs, 'show', SHAS['repair_engine'] + ':scripts/refile_mixed_citations.py'))
    changed = [Path(p.decode()) for p in git(data, 'diff', '--name-only', '-z',
               SHAS['baseline_data'], SHAS['repaired_data']).split(b'\0') if p]
    repaired = prepared / 'repaired-data'

    def project(source, destination, relative=Path()):
        destination.mkdir()
        for entry in source.iterdir():
            if entry.name == '.git':
                continue
            item = relative / entry.name
            if item in changed:
                (destination / entry.name).write_bytes(git(
                    data, 'show', SHAS['repaired_data'] + ':' + str(item)))
            elif entry.is_dir():
                project(entry, destination / entry.name, item)
            else:
                (destination / entry.name).symlink_to(entry)

    project(data, repaired)
    for path in changed:
        assert (repaired / path).read_bytes() == git(
            data, 'show', SHAS['repaired_data'] + ':' + str(path))
    metadata = dict(SHAS, repaired_file_count=len(changed), repair_files_match_branch=True,
                    baseline_data_path=str(data), repaired_data_path=str(repaired),
                    baseline_engine_path=str(prepared / 'main'),
                    policy_path=str(prepared / 'hosts-866.json'),
                    private_research_copies='not read; linked unchanged from required clone')
    (ROOT / 'prepared.public.json').write_text(json.dumps(metadata, indent=2) + '\n')
    call('/Users/terbeest/.nvm/versions/node/v22.22.3/bin/npm', 'install',
         '--prefix', str(ROOT / 'memory-runtime'), '--no-save', 'pyodide@0.28.3')
    print(json.dumps(metadata, indent=2))


if __name__ == '__main__':
    main()
