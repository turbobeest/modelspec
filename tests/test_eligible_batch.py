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


def _page(root, stem, front):
    (root / "benchmarks").mkdir(exist_ok=True)
    (root / "benchmarks" / f"{stem}.md").write_text(f"---\nid: {stem}\n{front}name: X\n---\nbody\n")


def test_written_reads_slug_aliases_and_falls_back_to_line_two_aliases(tmp_path, monkeypatch):
    monkeypatch.setattr(next_batch, "ROOT", tmp_path)
    _page(tmp_path, "aime_2024", 'aliases: ["aime2024"]\n')  # old form: line 2
    assert next_batch.written() == {"aime2024"}  # stem and slug normalise alike

    _page(tmp_path, "gpqa", 'aliases: ["gpqa_main"]\n')
    _page(tmp_path, "arc_challenge", 'slug_aliases: ["arc_c", "arcchallenge2"]\naliases:\n  - ARC-C\n')
    _page(tmp_path, "bbh", 'slug_aliases: ["bigbenchhard"]\naliases: ["BBH display"]\n')
    have = next_batch.written()
    # fallback page, dedicated-key pages; display aliases are never treated as slugs
    assert {"gpqa", "gpqamain", "arcchallenge", "arcc", "arcchallenge2", "bbh", "bigbenchhard"} <= have
    assert "bbhdisplay" not in have


def test_skip_set_is_the_same_before_and_after_moving_the_key(tmp_path, monkeypatch):
    monkeypatch.setattr(next_batch, "ROOT", tmp_path)
    _page(tmp_path, "aime_2024", 'aliases: ["aime2024"]\n')
    _page(tmp_path, "gpqa", 'aliases: ["gpqa_main", "gpqa_extended"]\n')
    before = next_batch.written()
    for stem in ("aime_2024", "gpqa"):
        p = tmp_path / "benchmarks" / f"{stem}.md"
        p.write_text(p.read_text().replace("aliases:", "slug_aliases:", 1))
    assert next_batch.written() == before
