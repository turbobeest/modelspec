"""Audit source-only data refiling without reading retained page bytes.

All output is aggregate. Input data values are compared in memory and never emitted.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path
import subprocess
import sys
import yaml


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args])


def document(path, body):
    text = body.decode('utf-8')
    if path.suffix == '.md':
        parts = text.splitlines(keepends=True)
        assert parts[0].strip() == '---', 'Missing model front matter'
        end = next(i for i in range(1, len(parts)) if parts[i].strip() == '---')
        return yaml.safe_load(''.join(parts[1:end])), ''.join(parts[end:])
    return yaml.safe_load(text), None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-root', type=Path, required=True)
    parser.add_argument('--engine-root', type=Path, required=True)
    parser.add_argument('--base', required=True)
    parser.add_argument('--policy-ref', default='origin/pr-866')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root, engine = args.data_root.resolve(), args.engine_root.resolve()
    sys.path.insert(0, str(engine))
    from decision.citation import fact_citation, ref_states
    from decision.model import SourceRef, fact_verification_value
    from decision.verify import Claim, claim_verification_value
    from decision.sources import load_sources
    import decision.retention as retention
    policy = json.loads(git(engine, 'show', f'{args.policy_ref}:registry/source-retention.json'))
    retention.cite_only_hosts = lambda: tuple(policy['cite_only_hosts'])
    sources = {sid: str(s.url) for sid, s in load_sources(root/'registry/sources.yaml').items()}
    changed = git(root, 'diff', '--name-only', args.base).decode().splitlines()
    allowed_logs = {'verification/log.jsonl', 'verification/queue/events.jsonl'}
    cards, changed_rows = 0, {}
    counts = Counter()
    for relative in changed:
        path = root/relative
        if relative == '.engine-pin' or relative in allowed_logs:
            continue
        assert relative.startswith(('models/', 'offerings/')), 'Changed path outside authorized data scope'
        before = git(root, 'show', f'{args.base}:{relative}')
        after = path.read_bytes()
        old, old_body = document(path, before)
        new, new_body = document(path, after)
        assert old_body == new_body, 'Model Markdown body changed'
        old_parents = [old] if path.suffix == '.md' else old
        new_parents = [new] if path.suffix == '.md' else new
        assert len(old_parents) == len(new_parents), 'Parent added or removed'
        for old_parent, new_parent in zip(old_parents, new_parents):
            assert {k:v for k,v in old_parent.items() if k != 'facts'} == {k:v for k,v in new_parent.items() if k != 'facts'}, 'Non-fact metadata changed'
            old_facts, new_facts = old_parent.get('facts', []), new_parent.get('facts', [])
            assert len(old_facts) == len(new_facts), 'Fact added or removed'
            if path.suffix == '.md':
                subject = new_parent['model_id']
            elif 'plan' in new_parent:
                subject = f"{new_parent['provider']}/subscription/{new_parent['plan']}"
            else:
                subject = '/'.join(new_parent[k] for k in ('provider','model','region','tier'))
            for old_row, new_row in zip(old_facts, new_facts):
                assert {k:v for k,v in old_row.items() if k != 'sources'} == {k:v for k,v in new_row.items() if k != 'sources'}, 'Non-source fact field changed'
                if old_row == new_row:
                    continue
                old_refs, new_refs = old_row['sources'], new_row['sources']
                expected = [r for r, state in zip(old_refs, ref_states(old_row, sources)) if state == 'cited']
                assert new_refs == expected, 'Source change is not exactly retained-source deletion'
                assert 0 < len(new_refs) < len(old_refs), 'Invalid deletion count'
                assert all(state == 'cited' for state in ref_states(new_row, sources)), 'Mixed or retained ref remains'
                assert fact_citation(new_row, sources)['status'] == 'cited', 'Invalid final citation'
                rid = new_row.get('id', f"{subject}#{new_row['facet']}")
                assert rid not in changed_rows, 'Repeated changed fact id'
                changed_rows[rid] = new_row
                counts['facts_changed'] += 1
                counts['source_refs_deleted'] += len(old_refs) - len(new_refs)
                counts['source_refs_preserved'] += len(new_refs)
        cards += 1
    streams = {}
    collected, checked = {}, {}
    for relative in sorted(allowed_logs):
        old = git(root, 'show', f'{args.base}:{relative}')
        new = (root/relative).read_bytes()
        assert new.startswith(old), 'Append-only prefix bytes changed'
        tail = new[len(old):]
        assert not tail or (old.endswith(b'\n') and tail.endswith(b'\n')), 'Append is not whole lines'
        streams[relative] = {'prefix_bytes_preserved': True, 'unchanged': new == old, 'appended_lines': len(tail.splitlines())}
        if relative.endswith('/log.jsonl'):
            assert new == old, 'Verification log changed on all-cited repair'
            continue
        for raw in tail.splitlines():
            event = json.loads(raw)
            if event['event'] == 'collected':
                claim = Claim.from_dict(event['claim'])
                row = changed_rows[claim.target.id]
                assert claim.target.kind == 'fact', 'Non-fact claim added'
                assert claim_verification_value(claim) == fact_verification_value(row), 'Queued value differs from current card'
                assert [r.model_dump(mode='json') for r in claim.sources] == [SourceRef.model_validate(r).model_dump(mode='json') for r in row['sources']], 'Queued sources differ from current card'
                assert claim.field == row['facet'], 'Queued facet differs'
                assert claim.target.id not in collected, 'Repeated collected claim'
                collected[claim.target.id] = True
            else:
                assert event['event'] == 'checked' and event['outcome'] == 'cited' and event['diff'] == [], 'Unexpected appended queue event'
                rid = event['target']['id']
                assert event['target']['kind'] == 'fact' and rid in changed_rows and rid not in checked, 'Invalid checked target'
                checked[rid] = True
    assert set(collected) == set(checked) == set(changed_rows), 'Queue and changed facts differ'
    main_sha = git(engine, 'rev-parse', 'origin/main').decode().strip()
    assert (root/'.engine-pin').read_text().strip() == main_sha, 'Engine pin differs from origin/main'
    guard = subprocess.run([sys.executable, '-I', str(root/'.github/scripts/check_linked_data.py'), '--engine', str(engine), '--data', str(root)], capture_output=True, text=True)
    assert guard.returncode == 0, 'Linked-data guard failed'
    report = {'passed': True, 'data_base': git(root, 'rev-parse', args.base).decode().strip(), 'engine_main': main_sha, 'data_files_changed': cards, **counts, 'non_source_semantics_unchanged': True, 'all_final_refs_cite_only': True, 'queue_values_match_current_cards': True, 'queue_collected_events': len(collected), 'queue_checked_events': len(checked), 'streams': streams, 'engine_pin_matches_main': True, 'linked_data_guard_passed': True, 'source_page_bytes_read': False}
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True)+'\n')
    print(json.dumps(report, indent=2, sort_keys=True))

if __name__ == '__main__':
    main()
