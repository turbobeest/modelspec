"""Inherit MODEL-443's reviewed source-retention removals without copying sources.

Local Git metadata supplies the two removal receipts and one sanitized manifest.
The exact 81 deletion paths must equal MAIN..CAPTURE's deletions. Every existing
file is hash-checked before any write; unknown files and symlinks are refused.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
from pathlib import Path
import subprocess
from urllib.parse import urlsplit

MAIN = 'ba03e11651513aa108f4031e56622717cf419acf'
CAPTURE = 'a9300cb6ce41fc2e238ccd38ff326d5e5a9700a7'
RECEIPTS = ('research/model-443/cite-only-retention-removal.json',
            'research/model-443/source-terms-retention-removal.json')
MANIFEST = 'research/model-393/http-manifest.json'


def git(repo, *args):
    return subprocess.run(['git','-C',str(repo),*args],check=True,capture_output=True,
                          stdin=subprocess.DEVNULL).stdout


def obj(repo, rev, path):
    return git(repo,'show',f'{rev}:{path}')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def safe_path(root, relative):
    rel = Path(relative)
    assert not rel.is_absolute() and '..' not in rel.parts, 'receipt path escapes root'
    current = root
    for part in rel.parts:
        current = current / part
        assert not current.is_symlink(), f'refusing symlink: {relative}'
    return current


def remove_pointer(document, pointer):
    parts = [part.replace('~1','/').replace('~0','~') for part in pointer.split('/')[1:]]
    node = document
    for part in parts[:-1]:
        node = node[int(part)] if isinstance(node,list) else node[part]
    key = int(parts[-1]) if isinstance(node,list) else parts[-1]
    value = node[key]
    del node[key]
    return value


def plan(repo, root):
    receipt_bytes = {path:obj(repo,CAPTURE,path) for path in RECEIPTS}
    receipts = [json.loads(receipt_bytes[path]) for path in RECEIPTS]
    files = [entry for receipt in receipts for entry in receipt['files']]
    paths = {entry['path'] for entry in files}
    assert len(files) == len(paths) == 81
    deleted = set(git(repo,'diff','--name-only','--diff-filter=D',MAIN,CAPTURE).decode().splitlines())
    assert deleted == paths, 'capture deletions differ from the two removal receipts'
    terms = json.loads(obj(repo,MAIN,'registry/source-terms.json'))
    for entry in files:
        assert entry['source_urls'] and all(terms.get(urlsplit(url).hostname) == 'forbids'
                                            for url in entry['source_urls']), entry['path']
    original = obj(repo,MAIN,MANIFEST)
    sanitized = obj(repo,CAPTURE,MANIFEST)
    old_json = json.loads(original)
    expected = copy.deepcopy(old_json)
    field_removals = receipts[1]['manifest_field_removals']
    assert len(field_removals) == 2
    for entry in field_removals:
        assert entry['path'] == MANIFEST and entry['json_pointer'].endswith('/visible_preview')
        assert all(terms.get(urlsplit(url).hostname) == 'forbids' for url in entry['source_urls'])
        removed = remove_pointer(expected,entry['json_pointer'])
        assert digest(removed.encode()) == entry['removed_utf8_sha256']
        assert len(removed.encode()) == entry['removed_utf8_bytes']
    assert json.loads(sanitized) == expected, 'sanitized manifest changes more than approved fields'
    pending = []
    for entry in files:
        path = safe_path(root,entry['path'])
        assert not entry['path'].endswith('.jsonl'), 'refusing deletion from append-only history'
        if path.exists():
            assert path.is_file(), f'not a file: {entry["path"]}'
            assert path.stat().st_size == entry['stored_bytes'], f'changed size: {entry["path"]}'
            assert digest(path.read_bytes()) == entry['file_sha256'], f'changed bytes: {entry["path"]}'
            pending.append(entry['path'])
    empties = receipts[1]['excluded_empty_hash_matches']['files']
    assert len(empties) == 45
    for entry in empties:
        path = safe_path(root,entry['path'])
        assert path.is_file() and digest(path.read_bytes()) == entry['file_sha256'], entry['path']
    destination = safe_path(root,MANIFEST)
    current_manifest = destination.read_bytes()
    assert current_manifest in (original,sanitized), 'target manifest differs from main and reviewed cleanup'
    writes = {MANIFEST:sanitized, **receipt_bytes}
    pending_writes = {}
    for relative, data in writes.items():
        path = safe_path(root,relative)
        if path.exists():
            current = path.read_bytes()
            if relative != MANIFEST:
                assert current == data, f'receipt changed: {relative}'
            if current == data:
                continue
        pending_writes[relative] = data
    return dict(files=files, pending_deletions=pending, pending_writes=pending_writes,
                source_files_removed=81, source_bytes_removed=sum(entry['stored_bytes'] for entry in files),
                preview_fields_removed=2, preview_utf8_bytes_removed=sum(entry['removed_utf8_bytes'] for entry in field_removals),
                empty_files_preserved=45, sanitized_manifest_sha256=digest(sanitized),
                receipts_sha256={path:digest(data) for path,data in receipt_bytes.items()})


def apply(root, planned):
    for relative in planned['pending_deletions']:
        safe_path(root,relative).unlink()
    for relative,data in planned['pending_writes'].items():
        path = safe_path(root,relative)
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(data)


def summary(planned):
    return {key:value for key,value in planned.items()
            if key not in ('files','pending_deletions','pending_writes')} | dict(
        pending_deletions=len(planned['pending_deletions']),
        pending_metadata_writes=list(planned['pending_writes']))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo',type=Path,required=True)
    parser.add_argument('--target',type=Path,required=True)
    parser.add_argument('--apply',action='store_true')
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    assert not(args.apply and args.check),'choose apply or check'
    planned=plan(args.repo,args.target)
    if args.apply:
        apply(args.target,planned)
        planned=plan(args.repo,args.target)
    print(json.dumps(summary(planned),indent=2,sort_keys=True))
    if args.check:
        assert not planned['pending_deletions'] and not planned['pending_writes'], 'cleanup remains pending'


if __name__ == '__main__':
    main()
