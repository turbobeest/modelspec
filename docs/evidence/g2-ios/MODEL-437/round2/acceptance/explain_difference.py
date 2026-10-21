"""Explain residual acceptance changes using in-memory diagnostic replays only.

No snapshot is written or gate disabled. Private responses and row identities
stay in scratch; the public report contains counts and replay outcomes only.
"""
from datetime import UTC, date, datetime
from collections import Counter
import gzip
import json
import os
from pathlib import Path
import sys

proof = Path('/tmp/model-437-scratch/acceptance')
code = proof / 'results/c/code'
sys.path.insert(0, str(code))
os.environ.pop('MODELSPEC_SOURCE_CACHE', None)
os.environ.pop('MODELSPEC_SNAPSHOT_ED25519_KEY', None)
os.environ['MODELSPEC_SNAPSHOT_KEY'] = 'model437-round2-private-proof-throwaway-key'
from decision import registry, retention, snapshot
import yaml
from tests.corpus import corpus
registry.use_root(proof / 'results/c/runtime-root')
case = next(case for case in corpus.load_cases() if case.id == 'facet-must-model.fits_hardware')
service = corpus.worker_service()
reports, private = {}, {}


def identity(index):
    status, raw = corpus.run_worker(case, index, service)
    body = json.loads(raw)
    answer = body.get('answer') or {}
    rows = body.get('results') or []
    return {'http': status, 'status': body.get('status'),
            'first_result': rows[0]['model'] if rows else None,
            'kind': answer.get('kind'), 'members': sorted(answer.get('members', []))}, body


def observations(index):
    return {row.record_id: (model, row.benchmark_id, row.value, row.unit, row.date,
            row.measured_by, row.version, row.subcategory, row.effort, row.harness,
            row.interval, row.n, row.quality_flags) for model, row in index.corpus_evidence()}


for period, filename in [('current', 'snapshot.json.gz'), ('successor', 'snapshot-successor.json.gz')]:
    contents = {label: json.loads(gzip.decompress((proof / 'results' / label / 'exports/decision' / filename).read_bytes()))
                for label in ('a', 'c', 'd')}
    day = date.fromisoformat(contents['a']['content']['as_of'])
    class Clock(datetime):
        @classmethod
        def now(cls, tz=None):
            instant = datetime.combine(day, datetime.min.time(), tzinfo=UTC)
            return instant.astimezone(tz) if tz else instant.replace(tzinfo=None)
    snapshot.datetime = Clock
    indexes = {label: snapshot.load_snapshot_bytes((proof / 'results' / label / 'exports/decision' / filename).read_bytes(),
               include_archive=True) for label in contents}
    a, c, d = (indexes[label] for label in ('a', 'c', 'd'))
    answers = {label: identity(index) for label, index in indexes.items()}
    a_rows, c_rows = observations(a), observations(c)
    extra = set(c_rows) - set(a_rows)
    common = set(a_rows) & set(c_rows)
    ids = set(a.candidates()) & set(c.candidates())
    fact_changes = sum((a.fact(cid, 'model.fits_hardware').state, a.fact(cid, 'model.fits_hardware').value) !=
                      (c.fact(cid, 'model.fits_hardware').state, c.fact(cid, 'model.fits_hardware').value) for cid in ids)
    fit_changes = sum(a.capability_estimate(cid, 'software_engineering') != c.capability_estimate(cid, 'software_engineering') for cid in ids)
    original_c_id = c.snapshot_id
    c.snapshot_id = a.snapshot_id
    same_seed, same_seed_body = identity(c)
    c.snapshot_id = original_c_id
    estimate_fields = ('_capability_estimates', '_capability_drivers', 'capability_method',
                       'capability_items', 'capability_source_offsets')
    saved = {name: getattr(c, name) for name in estimate_fields}
    for name in estimate_fields:
        setattr(c, name, getattr(a, name))
    old_fit, old_fit_body = identity(c)
    c.snapshot_id = a.snapshot_id
    old_fit_seed, old_fit_seed_body = identity(c)
    for name, value in saved.items():
        setattr(c, name, value)
    c.snapshot_id = original_c_id
    assert a._row == c._row
    hardware_fields = ['model.fits_hardware', 'model.hardware_fit_indeterminate']
    saved_hardware = {}
    for name in hardware_fields:
        for container in ('_facts', '_facet_bits'):
            mapping = getattr(c, container)
            saved_hardware[container, name] = mapping.get(name)
            if name in getattr(a, container):
                mapping[name] = getattr(a, container)[name]
            else:
                mapping.pop(name, None)
    old_hardware, old_hardware_body = identity(c)
    c.snapshot_id = a.snapshot_id
    old_hardware_seed, old_hardware_seed_body = identity(c)
    c.snapshot_id = original_c_id
    for (container, name), value in saved_hardware.items():
        if value is None:
            getattr(c, container).pop(name, None)
        else:
            getattr(c, container)[name] = value
    changed_subjects = [cid for cid in ids if
        (a.fact(cid, 'model.fits_hardware').state, a.fact(cid, 'model.fits_hardware').value) !=
        (c.fact(cid, 'model.fits_hardware').state, c.fact(cid, 'model.fits_hardware').value)]
    transitions = Counter(a.fact(cid, 'model.fits_hardware').state + '->' +
                          c.fact(cid, 'model.fits_hardware').state for cid in changed_subjects)
    changed_models = {c.model_of(cid) for cid in changed_subjects}
    admission = {}
    hardware_facts_unchanged_by_repair = True
    for policy_name, policy_path in [('main', proof / 'prepared/main/registry/source-retention.json'),
                                     ('866', proof / 'prepared/hosts-866.json')]:
        retention.POLICY_PATH = policy_path
        retention.cite_only_hosts.cache_clear()
        compiler = snapshot._Compiler(snapshot.SnapshotInputs(sources=a._sources),
                                      registry.default(), None, day, False)
        reasons = Counter()
        for model in sorted(changed_models):
            authored = []
            for data_root in [proof / 'modelspec-data', proof / 'prepared/repaired-data']:
                text = (data_root / 'models' / (model + '.md')).read_text()
                front = yaml.safe_load(text.split('---', 2)[1])
                authored.append(next(row for row in front['facts'] if row['facet'] == 'model.fits_hardware'))
            hardware_facts_unchanged_by_repair &= authored[0] == authored[1]
            record = a.record(a.fact(model, 'model.fits_hardware').record_id)
            compiler.add_model({'id': model, 'lifecycle': 'active', 'facts': [record]})
            reason = compiler.rejected.get((model, 'model.fits_hardware'))
            reasons['admitted' if reason is None else reason[0]] += 1
        admission[policy_name] = dict(reasons)
    retention.POLICY_PATH = proof / 'prepared/hosts-866.json'
    retention.cite_only_hosts.cache_clear()
    reports[period] = {
        'case': case.id, 'public_case_spec': case.spec,
        'hardware_fit_changed_models': len(changed_models),
        'hardware_facet_tier': registry.facet('model.fits_hardware').tier,
        'hardware_facts_unchanged_by_repair': hardware_facts_unchanged_by_repair,
        'identical_hardware_records_admission_by_policy': admission,
        'hardware_fit_state_transitions': dict(transitions),
        'candidate_with_baseline_hardware_facts_matches_baseline_answer': old_hardware == answers['a'][0],
        'candidate_with_baseline_hardware_facts_and_seed_matches_baseline_answer': old_hardware_seed == answers['a'][0], 'current_engine_baseline_matches_original': answers['a'][0] == answers['d'][0],
        'extra_admitted_evidence_records': len(extra), 'baseline_evidence_missing': len(set(a_rows)-set(c_rows)),
        'common_evidence_readings_changed': sum(a_rows[rid] != c_rows[rid] for rid in common),
        'candidate_subject_set_changed': set(a.candidates()) != set(c.candidates()),
        'hardware_fit_facet_values_changed': fact_changes,
        'software_engineering_estimates_changed': fit_changes,
        'candidate_with_baseline_snapshot_seed_matches_baseline_answer': same_seed == answers['a'][0],
        'candidate_with_baseline_capability_fit_matches_baseline_answer': old_fit == answers['a'][0],
        'candidate_with_baseline_fit_and_seed_matches_baseline_answer': old_fit_seed == answers['a'][0],
        'baseline_answer_member_count': len(answers['a'][0]['members']),
        'candidate_answer_member_count': len(answers['c'][0]['members']),
    }
    private[period] = {'baseline': answers['a'], 'candidate': answers['c'], 'same_seed': [same_seed, same_seed_body],
                      'old_fit': [old_fit, old_fit_body], 'old_fit_seed': [old_fit_seed, old_fit_seed_body],
                      'extra_records': sorted(extra), 'hardware_changed_models': sorted(changed_models),
                      'old_hardware': [old_hardware, old_hardware_body],
                      'old_hardware_seed': [old_hardware_seed, old_hardware_seed_body]}
(proof / 'residual.private.json').write_text(json.dumps(private, indent=2, default=str) + '\n')
(proof / 'residual.public.json').write_text(json.dumps(reports, indent=2) + '\n')
print(json.dumps(reports, indent=2))
