from copy import deepcopy
from datetime import date

import pytest
from pydantic import ValidationError

from decision.model import Fact
from decision.registry import default as default_registry
from decision.snapshot import (
    SnapshotBuildError, SnapshotInputs, build_snapshot, load_built_snapshot,
    load_snapshot_bytes,
)
from tests.snapshot_records import SOURCES, fact, model, evidence, offering, subscription

REGISTRY = default_registry()

@pytest.mark.parametrize('part,replacement', [('id', 'lab/unrelated#model.context_window'), ('kind', 'evidence')])
def test_snapshot_rejects_inline_verification_for_another_target(part, replacement):
    row = fact('model', 'lab/alpha', 'model.context_window', 128000)
    row['verification']['target'][part] = replacement
    with pytest.raises(ValidationError, match='target'):
        Fact.model_validate(row)
    built = build_snapshot(SnapshotInputs(models=[model('lab/alpha', facts=[row])], sources=SOURCES), registry=REGISTRY)
    actual = load_built_snapshot(built).fact('lab/alpha', 'model.context_window')
    assert actual.state == 'unknown', f'wrong target {part} admitted: state={actual.state}, value={actual.value}'

@pytest.mark.parametrize('part,replacement', [('id', 'lab/unrelated#quality'), ('kind', 'fact')])
def test_snapshot_rejects_evidence_inline_verification_for_another_target(part, replacement):
    row = evidence('lab/alpha', 'quality', 75)
    row['verification']['target'][part] = replacement
    built = build_snapshot(SnapshotInputs(models=[model('lab/alpha')], evidence=[row], sources=SOURCES), registry=REGISTRY)
    actual = load_built_snapshot(built).evidence('lab/alpha', 'quality')
    assert not actual, f'wrong evidence target {part} admitted: rows={len(actual)}'

@pytest.mark.parametrize('owner_kind', ['model', 'offering', 'subscription'])
@pytest.mark.parametrize('part', ['id', 'kind'])
def test_snapshot_rejects_verified_fact_owned_by_another_subject(owner_kind, part):
    from decision.model import Model, Offering
    from tests.snapshot_records import offering
    if owner_kind == 'model':
        facet = 'model.context_window'
        owner = 'lab/alpha'
        row = fact('model', 'lab/beta', facet, 128000)
        entity = model(owner, facts=[row])
        with pytest.raises(ValidationError, match='subject'):
            Model.model_validate(entity)
        supplied = SnapshotInputs(models=[entity], sources=SOURCES)
    elif owner_kind == 'offering':
        facet = 'offering.price.input'
        owner = 'sambanova/lab/alpha/global/standard'
        row = fact('offering', 'sambanova/lab/beta/global/standard', facet, 2)
        entity = offering('lab/alpha', facts=[row])
        with pytest.raises(ValidationError, match='subject'):
            Offering.model_validate(entity)
        supplied = SnapshotInputs(models=[model('lab/alpha')], offerings=[entity], sources=SOURCES)
    else:
        facet = 'offering.subscription.price'
        owner = 'sambanova/subscription/pro'
        row = fact('offering', 'sambanova/subscription/other', facet, 2)
        supplied = SnapshotInputs(subscriptions=[subscription(facts=[row])], sources=SOURCES)
    if part == 'kind':
        row['subject'] = {'id': owner, 'kind': 'offering' if owner_kind == 'model' else 'model'}
    with pytest.raises(SnapshotBuildError, match='owner|subject'):
        build_snapshot(supplied, registry=REGISTRY)

@pytest.mark.parametrize('defect', ['verification_target', 'fact_owner'])
def test_repository_build_rejects_misattributed_authored_fact(tmp_path, defect):
    import yaml
    from decision.snapshot import build_from_repo
    from tests.test_decision_snapshot import _mini_repo
    root = _mini_repo(tmp_path)
    path = root / 'offerings/sambanova/lab/alpha.yaml'
    rows = yaml.safe_load(path.read_text())
    if defect == 'verification_target':
        rows[0]['facts'][0]['verification']['target']['id'] = 'another-fact'
    else:
        rows[0]['facts'][0] = fact('offering', 'sambanova/lab/beta/global/standard', 'offering.price.input', 2)
    path.write_text(yaml.safe_dump(rows))
    if defect == 'fact_owner':
        with pytest.raises(SnapshotBuildError, match='owner|subject'):
            build_from_repo(root, premier=None, as_of=date(2026,9,24))
        return
    built = build_from_repo(root, premier=None, as_of=date(2026,9,24))
    actual = load_built_snapshot(built).fact('sambanova/lab/alpha/global/standard', 'offering.price.input')
    assert actual.state == 'unknown', f'repository build admitted {defect}: state={actual.state}'


@pytest.mark.parametrize('record_kind', ['fact', 'evidence'])
@pytest.mark.parametrize('loader', ['built', 'bytes'])
def test_matching_log_can_admit_record_with_unrelated_inline_verification(record_kind, loader):
    row = (fact('model', 'lab/alpha', 'model.context_window', 128000)
           if record_kind == 'fact' else evidence('lab/alpha', 'quality', 75))
    logged = deepcopy(row['verification'])
    row['verification']['target']['id'] = 'unrelated'
    row['verification']['outcome'] = 'mismatch'
    row['verification']['date'] = '2026-09-21'
    supplied = SnapshotInputs(
        models=[model('lab/alpha', facts=[row] if record_kind == 'fact' else None)],
        evidence=[row] if record_kind == 'evidence' else [],
        sources=SOURCES, verifications=[logged],
    )
    built = build_snapshot(supplied, registry=REGISTRY)
    index = (load_built_snapshot(built) if loader == 'built' else
             load_snapshot_bytes(built.to_bytes(None), key=None, public_keys={}))
    if record_kind == 'fact':
        assert index.fact('lab/alpha', 'model.context_window').value == 128000
    else:
        assert [item.value for item in index.evidence('lab/alpha', 'quality')] == [75]
