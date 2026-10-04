"""Board scale checks at the writer and snapshot boundaries."""
from pathlib import Path

import pytest

from schema.benchmark_values import validate_value
from scripts import refresh_leaderboards as refresh


@pytest.mark.parametrize('score,unit', [(1.1, ''), (-0.1, ''), (float('nan'), ''),
                                       (float('inf'), ''), (True, ''), (.5, 'percent')])
def test_fraction_board_refuses_invalid_values_before_write(tmp_path: Path, score, unit):
    (tmp_path / 'benchmarks').mkdir()
    (tmp_path / 'benchmarks' / 'fixture.md').write_text(
        '---\nmetric: {unit: "", max_score: 1}\n---\n')
    card = tmp_path / 'models' / 'lab' / 'model.md'
    card.parent.mkdir(parents=True)
    original = '---\nmodel_id: lab/model\nbenchmarks:\n  evidence: []\n---\n'
    card.write_text(original)
    with pytest.raises(ValueError):
        refresh._append_evidence(card, [{'benchmark_id': 'fixture', 'score': score, 'unit': unit}])
    assert card.read_text() == original


@pytest.mark.parametrize('score,unit,metric', [
    (0, '', {'max_score': 1}), (1, 'fraction', {'max_score': 1}),
    (100, '%', {'unit': 'percent', 'max_score': 100}),
    (-2, 'points', {'unit': 'points', 'min_score': -2, 'max_score': 5}),
])
def test_declared_boundaries_and_unit_aliases_are_accepted(score, unit, metric):
    validate_value(score, unit, metric)


def test_valid_number_on_wrong_scale_is_refused():
    with pytest.raises(ValueError, match='unit'):
        validate_value(.5, 'fraction', {'unit': '%', 'max_score': 100})


@pytest.mark.parametrize('writer', ['refresh-rewrite', 'historical-rewrite', 'board-rewrite',
                                   'board-append', 'research-rewrite'])
def test_each_evidence_writer_refuses_invalid_batch_before_modifying_card(tmp_path: Path, writer):
    from scripts import model_143_evidence, model_160_evidence, model_163_evidence

    (tmp_path / 'benchmarks').mkdir()
    (tmp_path / 'benchmarks' / 'fixture.md').write_text(
        '---\nmetric: {unit: percent, max_score: 100}\n---\n')
    card = tmp_path / 'models' / 'lab' / 'model.md'
    card.parent.mkdir(parents=True)
    original = '---\nmodel_id: lab/model\nbenchmarks:\n  evidence: []\n---\n'
    card.write_text(original)
    row = {'benchmark_id': 'fixture', 'score': 101, 'unit': 'percent'}
    updates = [(('fixture',), row)]
    with pytest.raises(ValueError, match='range'):
        if writer == 'refresh-rewrite':
            refresh._rewrite_card(card, updates)
        elif writer == 'historical-rewrite':
            model_143_evidence.replace_evidence(card, original, updates)
        elif writer == 'board-rewrite':
            model_160_evidence.rewrite_rows(card, original, updates)
        elif writer == 'board-append':
            model_160_evidence.append_rows(card, [model_160_evidence.new_row_block(row)])
        else:
            model_163_evidence.replace_evidence(card, original, ('fixture',), row)
    assert card.read_text() == original


def test_open_scale_boards_keep_negative_scores():
    # MODEL-276 review: Vending-Bench 2 reports a money balance in USD with no
    # declared floor, and GPT-5 mini (-31.18) is a valid live row.
    validate_value(-31.18, "USD", {"unit": "USD", "max_score": None})


@pytest.mark.parametrize("unit,high", [("%", 100), ("fraction", 1), ("", 1), (None, 100)])
def test_bounded_scales_still_refuse_negative_scores(unit, high):
    with pytest.raises(ValueError):
        validate_value(-1, unit, {"unit": unit, "max_score": high})


@pytest.mark.parametrize("score", [-100, -2.9, 0, 5.388066666666667, 100])
@pytest.mark.parametrize("declared", [{}, {"max_score": 100},
                                     {"min_score": -100, "max_score": 100}])
def test_pmrr_accepts_its_signed_scale(score, declared):
    validate_value(score, "p-MRR (x100)", {"unit": "p-MRR (x100)", **declared})


@pytest.mark.parametrize("score", [-100.1, 100.1])
@pytest.mark.parametrize("declared", [{}, {"min_score": -200, "max_score": 200}])
def test_pmrr_refuses_values_outside_its_signed_scale(score, declared):
    with pytest.raises(ValueError, match="range"):
        validate_value(score, "p-MRR (x100)", {"unit": "p-MRR (x100)", **declared})


def test_pmrr_is_not_labelled_as_percent():
    with pytest.raises(ValueError, match="unit"):
        validate_value(5.388066666666667, "percent",
                       {"unit": "p-MRR (x100)", "min_score": -100, "max_score": 100})


def test_pmrr_writer_preserves_a_negative_value(tmp_path: Path):
    (tmp_path / "benchmarks").mkdir()
    (tmp_path / "benchmarks" / "followir.md").write_text(
        '---\nmetric: {unit: "p-MRR (x100)", min_score: -100, max_score: 100}\n---\n')
    card = tmp_path / "models" / "lab" / "model.md"
    card.parent.mkdir(parents=True)
    card.write_text('---\nmodel_id: lab/model\nbenchmarks:\n  evidence: []\n---\n')
    refresh._append_evidence(card, [{"benchmark_id": "followir", "score": -2.9,
                                   "unit": "p-MRR (x100)"}])
    assert refresh._front(card)["benchmarks"]["evidence"] == [
        {"benchmark_id": "followir", "score": -2.9, "unit": "p-MRR (x100)"}
    ]
