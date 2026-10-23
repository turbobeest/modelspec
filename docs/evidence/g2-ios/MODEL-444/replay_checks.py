"""Offline replay checks against the actual captured branch, without reading pages."""
import importlib.util
import os
from pathlib import Path
import shutil
import socket

import pytest

HERE = Path(__file__).parent
DATA = Path(os.environ['MODEL444_DATA_DIR'])
JOB = DATA / '.github/scripts/rendered_reread.py'
spec = importlib.util.spec_from_file_location('replay_rendered', HERE / 'replay_rendered.py')
replay = importlib.util.module_from_spec(spec)
spec.loader.exec_module(replay)


@pytest.fixture
def job():
    return replay.load_job(JOB)


@pytest.fixture
def receipt(job):
    return replay.plan(DATA, DATA, job)


def test_every_captured_record_has_an_explicit_non_admission_disposition(receipt):
    assert receipt['counts'] == dict(captured_results=287,
        dispositions={'not_reread':258,'cited':29}, log_appended=0,
        queue_appended=0, stale_queue_events=8)
    for stream, count in zip(replay.STREAMS, (269, 554), strict=True):
        mappings = receipt['streams'][stream]['mapping']
        assert len(mappings) == count
        assert all(row['report_indexes'] and row['line_sha256'].startswith('sha256:')
                   and row['disposition'] == 'attempt_only' and not row['appended']
                   for row in mappings)
    assert len({r['target'] for r in receipt['streams'][replay.STREAMS[1]]['mapping']
                if r['stale_against_main']}) == 4


def test_live_attempt_writer_replay_is_idempotent_and_leaves_main_exact(tmp_path, receipt, job, monkeypatch):
    monkeypatch.setattr(socket.socket, 'connect', replay.forbid_network)
    monkeypatch.setattr(socket, 'create_connection', replay.forbid_network)
    for path in replay.STREAMS:
        output = tmp_path / path
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(replay.object_bytes(DATA, replay.MAIN, path))
    replay.apply(tmp_path, job, receipt)
    before = {str(path.relative_to(tmp_path)): path.read_bytes()
              for path in tmp_path.rglob('*') if path.is_file()}
    assert len(before[replay.ATTEMPTS].splitlines()) == 287
    replay.apply(tmp_path, job, receipt)
    after = {str(path.relative_to(tmp_path)): path.read_bytes()
             for path in tmp_path.rglob('*') if path.is_file()}
    assert after == before
    for path in replay.STREAMS:
        assert after[path] == replay.object_bytes(DATA, replay.MAIN, path)


def test_replay_refuses_a_non_main_stream_before_writing(tmp_path, job):
    registry = tmp_path / 'registry'
    registry.mkdir()
    for name in ('sources.yaml', 'derived-copies.json', 'source-terms.json'):
        shutil.copyfile(DATA / 'registry' / name, registry / name)
    for path in replay.STREAMS:
        output = tmp_path / path
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(replay.object_bytes(DATA, replay.MAIN, path))
    with (tmp_path / replay.STREAMS[0]).open('ab') as output:
        output.write(b'{"unexpected":"append"}\n')
    with pytest.raises(AssertionError, match='target is not exact main'):
        replay.plan(DATA, tmp_path, job)
    assert not (tmp_path / replay.ATTEMPTS).exists()


def test_replay_keeps_only_metadata_and_the_actual_run_ledger(receipt):
    assert all(row['diff'] == [] for row in receipt['results'])
    assert all(row['diff'] == [] for row in receipt['corrected_report']['results'])
    assert receipt['corrected_state']['spend'] == {'39213106225': 12}
    assert not receipt['corrected_state']['failures']
    assert receipt['corrected_report']['captured_report_sha256'] == receipt['captured_report_sha256']
    assert all(set(value) == {'outcome','copy','error'}
               for value in receipt['corrected_report']['sources'].values())
    assert receipt['network_calls'] == 0 and receipt['retained_source_bytes'] == 0
