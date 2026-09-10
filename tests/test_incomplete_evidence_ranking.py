"""MODEL-34: absence is uncertainty, not a measured failure."""

import json
from dataclasses import asdict
from pathlib import Path

import pytest

from pipeline.ranking import Candidate, score, rank, rank_report, format_report, build_candidates
from api.ranking.engine import (
    USE_CASE_PROFILES, IncompleteEvidenceError, ModelData, RankingEngine,
    MIN_BENCHMARK_COVERAGE, _benchmark_evidence,
)
from schema.card import ModelCard
from schema.graph import CollectingSink


def candidate(name, scores):
    return Candidate(name, name, 'Test', None, benchmark_scores=scores)


def measured(name='measured', value=50.0):
    return candidate(name, {b: value for b in USE_CASE_PROFILES['coding']['benchmark_weights']})


def test_single_verified_high_score_is_unranked():
    candidate = Candidate(
        'lucky', 'Lucky', 'Test', 'llm-code',
        benchmark_scores={'scicode': 100.0},
        verified_benchmarks={'scicode'},
    )
    result = score(candidate, USE_CASE_PROFILES['coding'])
    assert result['score'] is None
    assert result['rank_status'] == 'unranked'
    assert result['evidence_basis'] != 'verified'


@pytest.mark.parametrize('profile,benchmark', [
    ('coding', 'scicode'), ('reasoning', 'critpt'),
])
def test_real_astra_is_visible_unranked_instead_of_ranked_low(profile, benchmark):
    """Sparse real-card evidence is visible and unranked, never a low numeric rank.

    GPT-6 Astra is the fixture. Coverage will rise as evidence is attached; when
    it reaches MIN_BENCHMARK_COVERAGE this test should fail and the fixture
    should be replaced, not the assertion weakened to let a rankable model pass.
    """
    path = Path(__file__).resolve().parents[1] / 'models/openai/gpt-6-astra.md'
    astra = build_candidates([ModelCard.from_yaml_file(path)], CollectingSink())[0]
    report = rank_report([astra], profile, limit=10)
    assert report['ranking_status'] == 'unavailable'
    assert report['ranked'] == []
    row, = report['unranked']
    assert row['model_id'] == 'openai/gpt-6-astra'
    assert row['rank'] is row['score'] is None
    assert row['unranked_reason'] == 'insufficient_benchmark_evidence'
    assert 0 < row['benchmark_coverage'] < MIN_BENCHMARK_COVERAGE
    assert row['benchmark_count'] >= 1
    assert row['benchmark_estimate'] is not None
    assert row['score_upper_bound'] > row['score_lower_bound']
    assert row['evidence_basis'] != 'verified'
    assert benchmark in row['benchmark_contributions']
    text = format_report(report)
    assert 'UNRANKED  GPT-6 Astra' in text
    assert 'not ranked low' in text


def test_lucky_model_cannot_top_profile_even_with_all_auxiliary_bonuses():
    lucky = candidate('Lucky', {'scicode': 100.0})
    lucky.model_type = 'llm-code'
    lucky.capability_tiers = {k: 'tier-1' for k in USE_CASE_PROFILES['coding']['capability_weights']}
    lucky.context_window = 10_000_000
    lucky.cost_input = 0.0
    report = rank_report([lucky, measured(value=0.0)], 'coding', limit=1, cost_weight=0.25)
    assert report['ranking_status'] == 'partial'
    assert [r['model_id'] for r in report['ranked']] == ['measured']
    assert report['ranked'][0]['score'] == 0.0
    assert report['ranked'][0]['rank'] == 1
    assert report['unranked'][0]['model_id'] == 'Lucky'
    assert report['unranked'][0]['score'] is None
    assert report['unranked'][0]['score_lower_bound'] > report['ranked'][0]['score']


def test_measured_zero_and_absence_have_different_meaning():
    profile = {'benchmark_weights': {'scicode': 0.5, 'critpt': 0.5}, 'context_weight': 0}
    zero = score(candidate('zero', {'scicode': 0.0, 'critpt': 0.0}), profile)
    absent = score(candidate('absent', {}), profile)
    assert zero['score'] == zero['benchmark_estimate'] == 0.0
    assert zero['rank_status'] == 'ranked'
    assert zero['score_lower_bound'] == zero['score_upper_bound'] == 0.0
    assert absent['score'] is absent['benchmark_estimate'] is None
    assert absent['score_lower_bound'] == 0.0
    # Bound formula: 40 * missing weight. Here M=1 on a benchmarks-only profile.
    # Update if the coefficient in _benchmark_evidence changes, not if the catalogue does.
    assert absent['score_upper_bound'] == 40.0
    assert absent['evidence_basis'] == 'none'


# Cases sit on MIN_BENCHMARK_COVERAGE / MIN_BENCHMARK_COUNT. They move with those
# constants; do not retune the fractions to match a catalogue snapshot.
@pytest.mark.parametrize('weights,scores,expected', [
    ({'a': MIN_BENCHMARK_COVERAGE / 2, 'b': MIN_BENCHMARK_COVERAGE / 2,
      'c': 1 - MIN_BENCHMARK_COVERAGE}, {'a': 90, 'b': 90}, 'ranked'),
    ({'a': MIN_BENCHMARK_COVERAGE / 2 - 0.01, 'b': MIN_BENCHMARK_COVERAGE / 2,
      'c': 1 - (MIN_BENCHMARK_COVERAGE - 0.01)}, {'a': 90, 'b': 90}, 'unranked'),
    ({'a': .9, 'b': .1}, {'a': 100}, 'unranked'),
    ({'a': 1.0}, {'a': 0}, 'ranked'),
    ({'a': 0, 'b': 1}, {'a': 100}, 'unranked'),
    ({}, {}, 'unranked'),
])
def test_eligibility_requires_weighted_coverage_and_count(weights, scores, expected):
    result = _benchmark_evidence(scores, {'benchmark_weights': weights})
    assert result['rank_status'] == expected


@pytest.mark.parametrize('value', [float('nan'), float('inf'), -float('inf'), None])
def test_nonfinite_or_null_measurements_are_absent(value):
    result = _benchmark_evidence({'scicode': value}, {'benchmark_weights': {'scicode': 1}})
    assert result['benchmark_count'] == 0
    assert result['benchmark_estimate'] is None
    assert result['benchmark_coverage'] == 0


def test_coverage_does_not_change_when_an_unmeasured_candidate_is_added():
    pool = [measured()]
    original = rank_report(pool, 'coding')
    enlarged = rank_report([*pool, candidate('new', {})], 'coding')
    assert original['ranked'] == enlarged['ranked']
    assert enlarged['unranked_count'] == 1


def test_deleting_a_measurement_widens_bounds_without_imputation():
    profile = {'benchmark_weights': {'scicode': .5, 'critpt': .25, 'hle': .25}}
    full = _benchmark_evidence({'scicode': 60, 'critpt': 40, 'hle': 20}, profile)
    partial = _benchmark_evidence({'scicode': 60, 'critpt': 40}, profile)
    assert partial['rank_status'] == 'ranked'
    assert partial['benchmark_lower_bound'] < full['benchmark_lower_bound']
    assert partial['benchmark_upper_bound'] > full['benchmark_upper_bound']
    assert partial['benchmark_estimate'] == pytest.approx((60 * .5 + 40 * .25) / .75)
    # Width is 40 * missing weight (hle 0.25). Update if the bound coefficient changes.
    assert partial['benchmark_upper_bound'] - partial['benchmark_lower_bound'] == 10


def test_verified_index_is_not_renormalized_into_a_dominant_contribution():
    weights = USE_CASE_PROFILES['coding']['benchmark_weights']
    scicode_w = weights['scicode']
    row = score(candidate('sparse', {'scicode': 100}), USE_CASE_PROFILES['coding'])
    assert row['rank_status'] == 'unranked'
    assert row['benchmark_estimate'] == pytest.approx(100)
    # 0.40 / 40 are the bound coefficients in _benchmark_evidence; scicode_w is
    # whatever share the cap currently assigns. A renormalized 100 would miss both.
    assert row['benchmark_lower_bound'] == pytest.approx(0.40 * 100 * scicode_w)
    missing_weight = sum(w for b, w in weights.items() if b != 'scicode')
    assert row['benchmark_upper_bound'] == pytest.approx(
        row['benchmark_lower_bound'] + 40.0 * missing_weight)


def test_verified_requires_complete_profile_inputs_and_weighted_coverage():
    full = measured()
    full.verified_benchmarks = set(full.benchmark_scores)
    assert score(full, USE_CASE_PROFILES['coding'])['evidence_basis'] == 'verified'
    del full.benchmark_scores['terminal_bench']
    row = score(full, USE_CASE_PROFILES['coding'])
    assert row['rank_status'] == 'ranked'
    assert row['evidence_basis'] == 'partial-verified'
    deleted = USE_CASE_PROFILES['coding']['benchmark_weights']['terminal_bench']
    assert row['verified_benchmark_coverage'] == pytest.approx(1.0 - deleted)


def test_legacy_list_caller_gets_ranked_models_when_others_lack_evidence():
    mixed = [measured(), candidate('no evidence', {})]
    ranked = rank(mixed, 'coding', limit=1)
    assert [r['model_id'] for r in ranked] == ['measured']
    assert ranked[0]['rank'] == 1
    report = rank_report(mixed, 'coding', limit=1)
    assert report['ranking_status'] == 'partial'
    assert report['unranked_count'] == 1
    assert report['unranked'][0]['score'] is None
    assert rank([measured()], 'coding')[0]['rank'] == 1
    assert rank([], 'coding') == []
    assert rank([candidate('no evidence', {})], 'coding') == []


def test_incomplete_evidence_error_still_wraps_a_report_for_strict_callers():
    report = rank_report([candidate('x', {})], 'coding')
    error = IncompleteEvidenceError(report)
    assert error.report is report
    assert 'not ranked low' in str(error)


def test_http_rank_response_discloses_withheld_count():
    from api.main import RankResponse
    # 1103 is a payload fixture to prove the field round-trips, not a live count.
    payload = RankResponse(
        ranked=[], use_case='coding', total=0,
        unranked_count=1103, ranking_status='unavailable',
    )
    dumped = payload.model_dump()
    assert dumped['unranked_count'] == 1103
    assert dumped['ranking_status'] == 'unavailable'
    assert dumped['ranked'] == []


def test_empty_unavailable_and_truncated_are_distinct():
    assert rank_report([], 'coding')['ranking_status'] == 'empty'
    empty_evidence = rank_report([candidate('x', {})], 'coding', limit=0)
    assert empty_evidence['ranking_status'] == 'unavailable'
    assert empty_evidence['unranked_count'] == len(empty_evidence['unranked']) == 1
    truncated = rank_report([measured()], 'coding', limit=0)
    assert truncated['ranking_status'] == 'complete'
    assert truncated['ranked_count'] == 1
    assert truncated['ranked'] == []


def test_engine_and_offline_scoring_share_evidence_semantics():
    sparse = candidate('sparse', {'scicode': 100})
    for c in [sparse, measured()]:
        model = ModelData(c.model_id, c.display_name, benchmark_scores=c.benchmark_scores)
        engine_row = asdict(RankingEngine(None)._score(model, USE_CASE_PROFILES['coding']))
        offline_row = score(c, USE_CASE_PROFILES['coding'])
        for key in ['rank_status', 'score', 'benchmark_estimate', 'benchmark_coverage',
                    'benchmark_lower_bound', 'benchmark_upper_bound', 'missing_benchmarks',
                    'score_lower_bound', 'score_upper_bound', 'benchmark_contributions']:
            assert engine_row[key] == offline_row[key], key


def test_graph_engine_list_interface_returns_ranked_and_report_keeps_unranked(monkeypatch):
    engine = RankingEngine(None)
    models = [ModelData('x', 'Unknown'), ModelData('y', 'Measured',
              benchmark_scores=measured().benchmark_scores)]
    monkeypatch.setattr(engine, '_fetch_candidates', lambda *args: models)
    report = engine.rank_report('coding', limit=1)
    assert report['ranking_status'] == 'partial'
    assert report['ranked'][0].rank == 1
    assert report['unranked'][0].score is None
    assert 'Unranked for insufficient' in report['unranked'][0].reasons[0]
    ranked = engine.rank('coding', limit=1)
    assert [row.model_id for row in ranked] == ['y']
    assert ranked[0].rank == 1


def test_export_versions_changed_shape_and_keeps_unranked_models(tmp_path, monkeypatch):
    from pipeline import ranking
    monkeypatch.setattr(ranking, 'build_candidates', lambda *args: [measured(), candidate('x', {})])
    ranking.write_export(tmp_path, [], CollectingSink(), {'commit': 'test'})
    payload = json.loads((tmp_path / 'rankings.json').read_text())
    assert payload['schema_version'] == '2.0'
    report = payload['rankings']['coding']
    assert report['ranking_status'] == 'partial'
    assert report['ranked'][0]['rank'] == 1
    assert report['unranked'][0]['model_id'] == 'x'
    assert report['unranked'][0]['score'] is None
    profiles = json.loads((tmp_path / 'profiles.json').read_text())
    assert profiles['ranking_policy'] == report['policy']


def test_cli_report_is_explicit_in_json_and_text(monkeypatch, capsys):
    from pipeline import ranking
    monkeypatch.setattr(ModelCard, 'from_yaml_file', lambda path: None)
    monkeypatch.setattr('schema.graph.derive_graph', lambda cards: CollectingSink())
    monkeypatch.setattr(ranking, 'build_candidates', lambda *args: [measured(), candidate('Absent', {})])
    monkeypatch.setattr('sys.argv', ['pipeline.ranking', 'coding', '--json'])
    ranking.main()
    payload = json.loads(capsys.readouterr().out)
    assert payload['schema_version'] == '2.0'
    assert payload['unranked'][0]['rank'] is None
    monkeypatch.setattr('sys.argv', ['pipeline.ranking', 'coding'])
    ranking.main()
    output = capsys.readouterr().out
    assert '1. ' in output and '  measured  coverage 100%' in output
    assert 'UNRANKED  Absent' in output
    assert 'not ranked low' in output
