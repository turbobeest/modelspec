"""Validate cleanup using already-clean metadata fixtures; never duplicate source pages."""
import importlib.util
import json
import os
from pathlib import Path

import pytest

HERE = Path(__file__).parent
DATA = Path(os.environ['MODEL444_DATA_DIR'])
spec = importlib.util.spec_from_file_location('inherit_retention_cleanup', HERE / 'inherit_retention_cleanup.py')
cleanup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cleanup)


@pytest.fixture
def sanitized_target(tmp_path):
    receipt = json.loads(cleanup.obj(DATA,cleanup.CAPTURE,cleanup.RECEIPTS[1]))
    for entry in receipt['excluded_empty_hash_matches']['files']:
        output = tmp_path / entry['path']
        output.parent.mkdir(parents=True,exist_ok=True)
        # These are 43 empty files and two gzip containers with empty payloads.
        raw = cleanup.obj(DATA,cleanup.MAIN,entry['path'])
        assert entry['content_bytes'] == 0
        output.write_bytes(raw)
    manifest = tmp_path / cleanup.MANIFEST
    manifest.parent.mkdir(parents=True,exist_ok=True)
    manifest.write_bytes(cleanup.obj(DATA,cleanup.CAPTURE,cleanup.MANIFEST))
    return tmp_path


def test_cleanup_metadata_equals_reviewed_capture_and_is_idempotent(sanitized_target):
    planned = cleanup.plan(DATA,sanitized_target)
    assert planned['source_files_removed'] == 81
    assert planned['source_bytes_removed'] == 4667409
    assert planned['preview_fields_removed'] == 2
    assert planned['preview_utf8_bytes_removed'] == 843
    assert planned['empty_files_preserved'] == 45
    cleanup.apply(sanitized_target,planned)
    again = cleanup.plan(DATA,sanitized_target)
    assert not again['pending_deletions'] and not again['pending_writes']
    for name in (*cleanup.RECEIPTS,cleanup.MANIFEST):
        assert (sanitized_target/name).read_bytes() == cleanup.obj(DATA,cleanup.CAPTURE,name)


def test_cleanup_refuses_changed_artifact_before_any_mutation(sanitized_target):
    receipt = json.loads(cleanup.obj(DATA,cleanup.CAPTURE,cleanup.RECEIPTS[0]))
    path = sanitized_target / receipt['files'][0]['path']
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(b'synthetic changed data')
    with pytest.raises(AssertionError,match='changed size'):
        cleanup.plan(DATA,sanitized_target)
    assert path.read_bytes() == b'synthetic changed data'
    assert not (sanitized_target/cleanup.RECEIPTS[0]).exists()


def test_cleanup_refuses_symlinks_and_keeps_unlisted_files(sanitized_target):
    receipt = json.loads(cleanup.obj(DATA,cleanup.CAPTURE,cleanup.RECEIPTS[0]))
    unlisted = sanitized_target / 'unlisted.txt'
    unlisted.write_text('keep')
    path = sanitized_target / receipt['files'][0]['path']
    path.parent.mkdir(parents=True,exist_ok=True)
    path.symlink_to(unlisted)
    with pytest.raises(AssertionError,match='refusing symlink'):
        cleanup.plan(DATA,sanitized_target)
    assert unlisted.read_text() == 'keep'
