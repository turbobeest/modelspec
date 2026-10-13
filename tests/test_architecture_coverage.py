"""MODEL-348 coverage requires verified facts or a verified dense exemption."""

from __future__ import annotations

from datetime import date

import yaml

from decision.model import Verification, VerificationActor, VerificationTarget, value_hash
from decision.verify import VerificationLog
from scripts.policy.architecture_coverage import FACETS, coverage_report, main


def tree(root, facts, architecture=None):
    (root / "models" / "lab").mkdir(parents=True)
    (root / "premier").mkdir()
    (root / "registry").mkdir()
    (root / "premier" / "slice-1.yaml").write_text(
        yaml.safe_dump(
            {
                "models": [
                    {"model_id": "lab/alpha", "open_weights": True},
                ]
            }
        )
    )
    (root / "registry" / "sources.yaml").write_text(
        yaml.safe_dump(
            {
                "schema_version": 1,
                "sources": [
                    {
                        "id": "hf",
                        "url": "https://huggingface.co/api/models/lab/Alpha",
                        "kind": "weights_repository",
                    },
                    {"id": "untrusted", "url": "https://example.test", "kind": "provider_terms"},
                ],
            }
        )
    )
    (root / "models" / "lab" / "alpha.md").write_text(
        "---\n"
        + yaml.safe_dump(
            {
                "model_id": "lab/alpha",
                "facts": facts,
                "architecture": architecture or {},
            }
        )
        + "---\n"
    )


def fact(facet, value, state="known", source="hf"):
    return {
        "facet": facet,
        "value": value,
        "state": state,
        "sources": [
            {"source_id": source, "snapshot_ref": "sha256:" + "a" * 64, "cited_regions": ["page"]}
        ],
        "checked_sources": [source] if state == "not_disclosed" else [],
    }


def verified(root, facet, value, outcome="verified"):
    VerificationLog(root / "verification").append(
        Verification(
            target=VerificationTarget(
                kind="fact", id=f"lab/alpha#{facet}", value_hash=value_hash(value)
            ),
            collector=VerificationActor(agent="collector", model_family="openai", method="test"),
            verifier=VerificationActor(
                agent="verifier", model_family="deterministic", method="test"
            ),
            method="test",
            outcome=outcome,
            date=date(2026, 10, 10),
            diff="changed" if outcome == "mismatch" else None,
        )
    )


def test_empty_lineup_facts_exit_nonzero_and_count_legacy_active_parameters(tmp_path, capsys):
    tree(tmp_path, [], {"type": "dense-transformer", "active_parameters": 100})
    report = coverage_report(tmp_path)
    assert all(
        row == {"known_verified": 0, "not_disclosed_cited": 0, "dense_exempt": 0, "missing": 1}
        for row in report["counts"].values()
    )
    assert report["catalogue"] == {"active_parameters": 1, "cards": 1}
    assert main(["--root", str(tmp_path)]) == 1
    assert "catalogue architecture.active_parameters=1 of 1 cards" in capsys.readouterr().out


def test_verified_dense_backbone_covers_expert_facets_without_inventing_fact_states(tmp_path):
    values = {
        "model.architecture": "dense-transformer",
        "model.parameters_total": 100,
        "model.parameters_active": 100,
    }
    tree(tmp_path, [fact(facet, value) for facet, value in values.items()])
    for facet, value in values.items():
        verified(tmp_path, facet, value)
    report = coverage_report(tmp_path)
    assert not report["gaps"]
    assert report["counts"]["model.experts_total"]["dense_exempt"] == 1
    assert report["counts"]["model.experts_per_token"]["dense_exempt"] == 1
    assert main(["--root", str(tmp_path)]) == 0
    verified(tmp_path, "model.architecture", "dense-transformer", "mismatch")
    assert coverage_report(tmp_path)["counts"]["model.experts_total"]["missing"] == 1


def test_sourced_verified_absence_counts_but_wrong_source_or_unchecked_absence_fails(tmp_path):
    facts = [fact(facet, None, "not_disclosed") for facet in FACETS]
    tree(tmp_path, facts)
    for facet in FACETS:
        verified(tmp_path, facet, None)
    assert main(["--root", str(tmp_path)]) == 0
    assert all(
        row["not_disclosed_cited"] == 1 for row in coverage_report(tmp_path)["counts"].values()
    )
    card = tmp_path / "models" / "lab" / "alpha.md"
    front = yaml.safe_load(card.read_text().split("---", 2)[1])
    front["facts"][0] = fact("model.architecture", None, "not_disclosed", "untrusted")
    front["facts"][1]["checked_sources"] = []
    card.write_text("---\n" + yaml.safe_dump(front) + "---\n")
    report = coverage_report(tmp_path)
    assert report["counts"]["model.architecture"]["missing"] == 1
    assert report["counts"]["model.parameters_total"]["missing"] == 1
    assert main(["--root", str(tmp_path)]) == 1


def test_a_log_for_a_different_value_does_not_cover_a_known_fact(tmp_path):
    tree(tmp_path, [fact("model.parameters_total", 100)])
    verified(tmp_path, "model.parameters_total", 101)
    assert coverage_report(tmp_path)["counts"]["model.parameters_total"]["missing"] == 1
