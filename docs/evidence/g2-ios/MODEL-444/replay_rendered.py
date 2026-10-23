"""Offline MODEL-444 outcome replay. Reads Git objects and metadata; never pages.

The live job's record_attempt API performs persistence. This program emits a
complete SHA256 mapping of the captured results and rejected log/queue additions.
It keeps main's log and queue byte-exact. No network library or subprocess other
than local git show/rev-parse/diff is used.
"""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import socket
import subprocess
import sys
from urllib.parse import urlsplit

MAIN = 'ba03e11651513aa108f4031e56622717cf419acf'
CAPTURE = 'a9300cb6ce41fc2e238ccd38ff326d5e5a9700a7'
REPORT = 'docs/evidence/g2-ios/MODEL-336-reread.json'
STATE = 'registry/rendered-reread-state.json'
STREAMS = ('verification/log.jsonl', 'verification/queue/events.jsonl')
ATTEMPTS = 'verification/rendered-reread-attempts.jsonl'


def sha(data):
    return 'sha256:' + hashlib.sha256(data).hexdigest()


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()


def git(repo, *args):
    return subprocess.run(['git', '-C', str(repo), *args], check=True,
                          capture_output=True, stdin=subprocess.DEVNULL).stdout


def object_bytes(repo, rev, path):
    return git(repo, 'show', f'{rev}:{path}')


def forbid_network(*args, **kwargs):
    raise AssertionError('offline replay attempted a network call')


def timestamp(value):
    stamp = datetime.fromisoformat(value)
    return stamp if stamp.tzinfo else stamp.replace(tzinfo=timezone.utc)


def identity(event):
    target = event['claim']['target'] if event['event'] == 'collected' else event['target']
    return target['kind'] + ':' + target['id']


def load_job(path):
    spec = importlib.util.spec_from_file_location('model444_rendered_job', path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def plan(repo, target, job):
    from decision.sources import load_sources
    from decision import retention

    raw_report = object_bytes(repo, CAPTURE, REPORT)
    report = json.loads(raw_report)
    sources = load_sources(target / 'registry/sources.yaml')
    derived = job.derived_copies(target, sources)
    omitted = set(derived) | job.recipe_sources(sources)
    terms = json.loads((target / 'registry/source-terms.json').read_text())
    current = []
    for index, result in enumerate(report['results'], 1):
        source_ids = result['sources']
        assert len(source_ids) == 1, 'capture has unexpected grouped source results'
        sid = source_ids[0]
        url = str(sources[sid].url)
        if sid in omitted:
            outcome = 'not_reread'
            reason = ('derived copy now excluded from the rendered reader' if sid in derived
                      else 'interaction recipe now excluded from the default rendered reader')
        elif retention.cite_only_origin_restrictive(url, ()) or terms.get(urlsplit(url).hostname) == 'forbids':
            outcome = 'cited'
            reason = 'current source retention policy permits citation metadata only'
        else:
            raise AssertionError(f'unexpected eligible capture needs a new disposition: {sid}')
        current.append(dict(index=index, captured_result_sha256=sha(encoded(result)),
                            target=result['target'], field=result['field'],
                            captured_outcome=result['outcome'], outcome=outcome,
                            reason=reason, sources=source_ids, diff=[]))
    state = json.loads(object_bytes(repo, CAPTURE, STATE))
    state.setdefault('retired', {})
    not_reread = {}
    for sid in sorted(omitted):
        reason = ('derived copy; owned by its registered collector' if sid in derived
                  else 'interaction recipe required; owned by the price reader')
        not_reread[sid] = reason
        old = {key: value for key, value in (
            ('failure', state['failures'].pop(sid, None)),
            ('last_read', state['last_read'].pop(sid, None))) if value is not None}
        if old:
            state['retired'][sid] = {**state['retired'].get(sid, {}), **old,
                                     'retired_on': report['checked_on'], 'reason': reason}
    for sid in report['sources']:
        if sid not in omitted:
            url = str(sources[sid].url)
            assert retention.cite_only_origin_restrictive(url, ()) or terms.get(urlsplit(url).hostname) == 'forbids'
            state['failures'].pop(sid, None)
    assert not state['failures'], 'capture contains an unresolved source outside the replay policy'
    corrected = {key: report[key] for key in (
        'run_id', 'checked_on', 'month', 'credits_spent', 'monthly_credits_reserved',
        'max_credits_per_run', 'max_credits_per_month', 'min_team_balance', 'slice_size',
        'selected', 'skipped', 'retry_skipped', 'team_balance', 'complete', 'duplicate')}
    corrected.update(offline_replay=True, capture_commit=CAPTURE,
                     captured_report_sha256=sha(raw_report), not_reread=not_reread,
                     alerts={}, unresolved={},
                     results=[{key: row[key] for key in ('target', 'field', 'outcome', 'reason', 'sources', 'diff')}
                              for row in current],
                     sources={sid: {'outcome': 'not_reread' if sid in omitted else 'cited',
                                    'copy': item['copy'], 'error': None}
                              for sid, item in report['sources'].items()})
    by_target = {}
    for row in current:
        by_target.setdefault(row['target'], []).append(row)
    streams = {}
    for path in STREAMS:
        main, captured = (object_bytes(repo, rev, path) for rev in (MAIN, CAPTURE))
        assert captured.startswith(main), f'{path}: captured branch lacks exact main prefix'
        assert (target / path).read_bytes() == main, f'{path}: target is not exact main'
        added = captured[len(main):].splitlines(keepends=True)
        latest = {}
        if path.endswith('events.jsonl'):
            for line in main.splitlines():
                if line.strip():
                    event = json.loads(line)
                    key = identity(event)
                    latest[key] = max(timestamp(event['at']), latest.get(key, timestamp(event['at'])))
        mapping = []
        for index, line in enumerate(added, 1):
            assert line.endswith(b'\n'), f'{path}: partial appended line'
            row = json.loads(line)
            key = identity(row) if 'event' in row else row['target']['kind'] + ':' + row['target']['id']
            matched = by_target[key]
            entry = dict(index=index, line_sha256=sha(line), target=key,
                         report_indexes=[item['index'] for item in matched],
                         disposition='attempt_only', appended=False)
            if 'event' in row:
                entry.update(event=row['event'], at=row['at'],
                             stale_against_main=key in latest and timestamp(row['at']) < latest[key])
                if key in latest:
                    entry['main_latest_at'] = latest[key].isoformat()
            else:
                entry['captured_outcome'] = row['outcome']
            mapping.append(entry)
        streams[path] = dict(main_sha256=sha(main), main_bytes=len(main),
                             captured_sha256=sha(captured), captured_added_rows=len(added),
                             preserved_main_prefix=True, accepted_rows=0, mapping=mapping)
    assert Counter(row['captured_outcome'] for row in current) == Counter(mismatch=200,unreachable=23,verified=48,skipped=16)
    assert Counter(row['outcome'] for row in current) == Counter(not_reread=258,cited=29)
    assert streams[STREAMS[0]]['captured_added_rows'] == 269
    assert streams[STREAMS[1]]['captured_added_rows'] == 554
    assert sum(row.get('stale_against_main',False) for row in streams[STREAMS[1]]['mapping']) == 8
    return dict(schema_version=1, main=MAIN, capture=CAPTURE,
                captured_report_sha256=sha(raw_report), run_id=report['run_id'],
                checked_on=report['checked_on'], results=current, streams=streams,
                counts=dict(captured_results=len(current),
                            dispositions=dict(Counter(row['outcome'] for row in current)),
                            log_appended=0, queue_appended=0, stale_queue_events=8),
                corrected_state=state, corrected_report=corrected,
                network_calls=0, retained_source_bytes=0)


def apply(target, job, receipt):
    # The live job owns attempt persistence and its idempotence rules.
    assert hasattr(job, 'record_attempt'), 'live job must export record_attempt'
    for row in receipt['results']:
        job.record_attempt(target, run_id=receipt['run_id'], checked_on=receipt['checked_on'],
                           target=row['target'], field=row['field'], outcome=row['outcome'],
                           reason=row['reason'], sources=row['sources'], diff=[])
    for path, value in ((STATE, receipt['corrected_state']), (REPORT, receipt['corrected_report'])):
        destination = target / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')
    for path in STREAMS:
        saved = receipt['streams'][path]
        assert sha((target / path).read_bytes()) == saved['main_sha256']
    return receipt


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--target', type=Path, required=True)
    parser.add_argument('--job-script', type=Path, required=True)
    parser.add_argument('--receipt', type=Path, required=True)
    parser.add_argument('--apply', action='store_true')
    args=parser.parse_args()
    socket.socket.connect=forbid_network
    socket.socket.connect_ex=forbid_network
    socket.create_connection=forbid_network
    job=load_job(args.job_script)
    receipt=plan(args.repo,args.target,job)
    if args.apply:
        apply(args.target,job,receipt)
    args.receipt.parent.mkdir(parents=True,exist_ok=True)
    args.receipt.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(json.dumps(receipt['counts'],sort_keys=True))


if __name__ == '__main__':
    main()
