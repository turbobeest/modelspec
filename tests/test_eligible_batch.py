import json
from datetime import date

import pytest

from scripts.benchmarks import next_batch
from tests.test_benchmark_eligibility import evidence, reference


class AssessmentDate(date):
    @classmethod
    def today(cls):
        return date(2026, 9, 8)


def test_batch_admits_only_recomputed_eligible_ids(tmp_path, monkeypatch):
    census = tmp_path / "benchmarks" / "_census"
    evidence_dir = census / "eligibility" / "evidence"
    evidence_dir.mkdir(parents=True)
    ref = census / "eligibility" / "reference-models.json"
    ref.write_text(reference().model_dump_json())
    (evidence_dir / "bench.json").write_text(evidence().model_dump_json())
    (census / "queue_p2.json").write_text(
        json.dumps(
            [
                {"slug": "unverified_candidate", "name": "Unverified"},
                {"slug": "bench", "name": "Verified benchmark"},
            ]
        )
    )
    monkeypatch.setattr(next_batch, "ROOT", tmp_path)
    monkeypatch.setattr(next_batch, "CENSUS", census)
    monkeypatch.setattr(next_batch, "date", AssessmentDate)
    monkeypatch.setattr("sys.argv", ["next_batch.py"])
    next_batch.main()
    output = census / "next_batch_eligible.json"
    payload = json.loads(output.read_text())
    assert payload["slices"] == {"A": ["bench"]}
    assert set(payload["hints"]) == {"bench"}
    assert not (census / "next_batch.json").exists()

    # An old successful output does not authorize today's expired reference set.
    ref.write_text(reference(as_of="2026-07-01").model_dump_json())
    next_batch.main()
    assert json.loads(output.read_text())["slices"] == {}

    # A missing evidence input invalidates the output, never falls back to census.
    ref.unlink()
    with pytest.raises(SystemExit):
        next_batch.main()
    assert not output.exists()
