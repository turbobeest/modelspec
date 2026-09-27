"""Social drafts are deterministic views of an approved decision snapshot."""

from __future__ import annotations

import ast
import hashlib
import json
from datetime import date
from pathlib import Path

import pytest

from decision.snapshot import SnapshotInputs, build_snapshot
from scripts.social import generator
from scripts.social.generator import PLATFORM_SIZES, generate
from tests.snapshot_records import SOURCES, evidence, fact, model, offering

KEY = b"social-fixture-signing-key"
AS_OF = date(2026, 9, 26)
DEVICE = "nvidia_rtx_4090"


def _model(model_id: str, *, fits: bool = True) -> dict:
    facts = [
        fact("model", model_id, "model.class", "text-generator"),
        fact("model", model_id, "model.fits_hardware", [DEVICE] if fits else []),
    ]
    return model(model_id, facts=facts)


def _offering(model_id: str, price: float) -> dict:
    row = offering(model_id, provider="openai")
    offering_id = f"openai/{model_id}/global/standard"
    row["facts"] = [
        fact("offering", offering_id, "offering.price.input", price, source="src-pricing"),
        fact("offering", offering_id, "offering.price.output", price * 2, source="src-pricing"),
    ]
    return row


def _snapshot(
    path: Path,
    scores: dict[str, float],
    *,
    non_fitting: set[str] | None = None,
) -> str:
    model_ids = ["lab/alpha", "lab/beta", "lab/gamma", "lab/delta"]
    non_fitting = {"lab/delta"} if non_fitting is None else non_fitting
    built = build_snapshot(
        SnapshotInputs(
            models=[_model(model_id, fits=model_id not in non_fitting) for model_id in model_ids],
            offerings=[
                _offering("lab/alpha", 1.0),
                _offering("lab/beta", 5.0),
                _offering("lab/gamma", 4.0),
                _offering("lab/delta", 0.5),
            ],
            evidence=[
                evidence(model_id, "swe_bench_pro", score, day=AS_OF.isoformat())
                for model_id, score in scores.items()
            ],
            sources=SOURCES,
            benchmark_domains={"swe_bench_pro": [("software_engineering", "direct")]},
        ),
        gate=False,
        as_of=AS_OF,
    )
    built.write(path, key=KEY)
    return built.snapshot_id


def _accuracy(path: Path, snapshot_id: str) -> None:
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "generated_at": "2026-09-26T12:00:00Z",
                "profile": "pr",
                "snapshot": snapshot_id,
                "status": "pass",
                "layers": [
                    {"name": "deterministic_correctness", "status": "pass", "gating": True},
                    {"name": "freshness", "status": "pass", "gating": True},
                    {"name": "golden_answers", "status": "pass", "gating": True},
                    {"name": "output_parity", "status": "pass", "gating": True},
                ],
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def _tree_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        digest.update(path.relative_to(root).as_posix().encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def test_fixture_snapshot_is_deterministic_and_has_no_unsourced_numbers(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(generator, "_png", lambda svg, png: False)
    current = tmp_path / "current.json.gz"
    previous = tmp_path / "previous.json.gz"
    snapshot_id = _snapshot(
        current,
        {"lab/alpha": 90.0, "lab/beta": 80.0, "lab/gamma": 70.0},
    )
    _snapshot(
        previous,
        {"lab/alpha": 60.0, "lab/beta": 90.0, "lab/gamma": 80.0},
    )
    report = tmp_path / "accuracy.json"
    _accuracy(report, snapshot_id)

    first = generate(
        model_id="lab/alpha",
        snapshot_path=current,
        previous_snapshot_path=previous,
        accuracy_report_path=report,
        output_dir=tmp_path / "first",
        device=DEVICE,
        snapshot_key=KEY,
    )
    second = generate(
        model_id="lab/alpha",
        snapshot_path=current,
        previous_snapshot_path=previous,
        accuracy_report_path=report,
        output_dir=tmp_path / "second",
        device=DEVICE,
        snapshot_key=KEY,
    )

    assert {draft["angle"] for draft in first["drafts"]} == {
        "new_entrant",
        "value",
        "local",
        "weekly_movers",
    }
    assert first == second
    assert _tree_digest(tmp_path / "first") == _tree_digest(tmp_path / "second")

    for draft in first["drafts"]:
        assert draft["claims"]
        assert all(claim["source"].startswith("https://") for claim in draft["claims"])
        assert all(date.fromisoformat(claim["date"]) <= AS_OF for claim in draft["claims"])
        for platform, (width, height) in PLATFORM_SIZES.items():
            files = draft["platforms"][platform]
            text = (tmp_path / "first" / files["text"]).read_text(encoding="utf-8")
            svg = (tmp_path / "first" / files["svg"]).read_text(encoding="utf-8")
            assert "No referral fees, no paid placement, no provider-paid visibility" in text
            assert f'width="{width}" height="{height}"' in svg
            if platform == "x":
                assert len(text.rstrip("\n")) <= 280
                assert "attached card" in text
            else:
                for claim in draft["claims"]:
                    assert claim["citation"] in text


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (lambda payload: payload.update(status="fail"), "did not pass"),
        (lambda payload: payload.update(snapshot="snap_wrong"), "covers 'snap_wrong'"),
        (lambda payload: payload.update(profile="nightly"), "must use the pr profile"),
        (lambda payload: payload.update(layers=[]), "exact pr layers"),
        (
            lambda payload: payload["layers"].__setitem__(
                0,
                {
                    "name": "deterministic_correctness",
                    "status": "fail",
                    "gating": True,
                },
            ),
            "did not pass",
        ),
    ],
)
def test_incomplete_or_mismatched_accuracy_report_is_refused(
    tmp_path: Path, mutate, message: str
) -> None:
    current = tmp_path / "current.json.gz"
    snapshot_id = _snapshot(current, {"lab/alpha": 90.0})
    report = tmp_path / "accuracy.json"
    _accuracy(report, snapshot_id)
    payload = json.loads(report.read_text())
    mutate(payload)
    report.write_text(json.dumps(payload))

    with pytest.raises(ValueError, match=message):
        generate(
            model_id="lab/alpha",
            snapshot_path=current,
            accuracy_report_path=report,
            output_dir=tmp_path / "out",
            snapshot_key=KEY,
        )


def test_rank_two_without_history_is_not_called_a_new_entrant(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(generator, "_png", lambda svg, png: False)
    current = tmp_path / "current.json.gz"
    snapshot_id = _snapshot(
        current,
        {"lab/alpha": 80.0, "lab/beta": 90.0, "lab/gamma": 70.0},
    )
    report = tmp_path / "accuracy.json"
    _accuracy(report, snapshot_id)

    manifest = generate(
        model_id="lab/alpha",
        snapshot_path=current,
        accuracy_report_path=report,
        output_dir=tmp_path / "out",
        device=DEVICE,
        snapshot_key=KEY,
    )

    assert "new_entrant" not in {draft["angle"] for draft in manifest["drafts"]}


def test_previously_unranked_model_entering_top_five_is_a_new_entrant(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(generator, "_png", lambda svg, png: False)
    current = tmp_path / "current.json.gz"
    previous = tmp_path / "previous.json.gz"
    snapshot_id = _snapshot(
        current,
        {"lab/alpha": 80.0, "lab/beta": 90.0, "lab/gamma": 70.0},
    )
    _snapshot(previous, {"lab/beta": 90.0, "lab/gamma": 70.0})
    report = tmp_path / "accuracy.json"
    _accuracy(report, snapshot_id)

    manifest = generate(
        model_id="lab/alpha",
        snapshot_path=current,
        previous_snapshot_path=previous,
        accuracy_report_path=report,
        output_dir=tmp_path / "out",
        device=DEVICE,
        snapshot_key=KEY,
    )

    entrant = next(draft for draft in manifest["drafts"] if draft["angle"] == "new_entrant")
    assert entrant["claims"][0]["text"].startswith("lab/alpha enters #2")


def test_price_claim_cites_each_contributing_fact_with_its_date(tmp_path: Path) -> None:
    current = tmp_path / "current.json.gz"
    row = _offering("lab/alpha", 1.0)
    input_fact, output_fact = row["facts"]
    input_fact["sources"][0]["source_id"] = "src-input-price"
    input_fact["verification"]["date"] = "2026-09-21"
    output_fact["sources"][0]["source_id"] = "src-output-price"
    output_fact["verification"]["date"] = "2026-09-22"
    built = build_snapshot(
        SnapshotInputs(
            models=[_model("lab/alpha")],
            offerings=[row],
            evidence=[evidence("lab/alpha", "swe_bench_pro", 90.0, day=AS_OF.isoformat())],
            sources={
                **SOURCES,
                "src-input-price": "https://prices.example.org/input",
                "src-output-price": "https://prices.example.org/output",
            },
            benchmark_domains={"swe_bench_pro": [("software_engineering", "direct")]},
        ),
        gate=False,
        as_of=AS_OF,
    )
    built.write(current, key=KEY)
    snapshot = generator._load_signed(current, KEY)
    offering_id = "openai/lab/alpha/global/standard"

    claim = generator._price_claim(snapshot, offering_id, 0.1234)

    assert "https://prices.example.org/input (read 2026-09-21)" in claim["citation"]
    assert "https://prices.example.org/output (read 2026-09-22)" in claim["citation"]


def test_value_angle_uses_one_offerings_evidence_and_cost(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(generator, "_png", lambda svg, png: False)
    current = tmp_path / "current.json.gz"
    offerings = [
        offering("lab/alpha", provider="p1"),
        offering("lab/alpha", provider="p2"),
        offering("lab/beta", provider="p1"),
    ]
    prices = {
        "p1/lab/alpha/global/standard": (0.125, 0.25),
        "p2/lab/alpha/global/standard": (0.1, 0.2),
        "p1/lab/beta/global/standard": (0.125, 0.25),
    }
    for row in offerings:
        offering_id = f"{row['provider']}/{row['model']}/global/standard"
        input_price, output_price = prices[offering_id]
        row["facts"] = [
            fact(
                "offering",
                offering_id,
                "offering.price.input",
                input_price,
                source="src-pricing",
            ),
            fact(
                "offering",
                offering_id,
                "offering.price.output",
                output_price,
                source="src-pricing",
            ),
        ]
    evidence_rows = []
    for offering_id, score in (
        ("p1/lab/alpha/global/standard", 60.0),
        ("p2/lab/alpha/global/standard", 55.0),
        ("p1/lab/beta/global/standard", 50.0),
    ):
        row = evidence(
            offering_id,
            "swe_bench_pro",
            score,
            subject_kind="offering",
        )
        row["model_id_as_evaluated"] = row["subject"]["id"].split("/global/", 1)[0].split("/", 1)[1]
        evidence_rows.append(row)
    built = build_snapshot(
        SnapshotInputs(
            models=[_model("lab/alpha"), _model("lab/beta")],
            offerings=offerings,
            evidence=evidence_rows,
            sources=SOURCES,
            benchmark_domains={"swe_bench_pro": [("software_engineering", "direct")]},
        ),
        gate=False,
        as_of=AS_OF,
    )
    built.write(current, key=KEY)
    report = tmp_path / "accuracy.json"
    _accuracy(report, built.snapshot_id)

    manifest = generate(
        model_id="lab/alpha",
        snapshot_path=current,
        accuracy_report_path=report,
        output_dir=tmp_path / "out",
        snapshot_key=KEY,
    )

    value = next(draft for draft in manifest["drafts"] if draft["angle"] == "value")
    evidence_claim = next(claim for claim in value["claims"] if "evidence:" in claim["text"])
    price_claim = next(claim for claim in value["claims"] if "list price:" in claim["text"])
    assert evidence_claim["text"] == "Verified swe_bench_pro evidence: 55 percent."
    assert price_claim["text"] == "Default task cost at list price: $0.0048."


def test_neutrality_disclosures_are_sourced_and_dated_for_every_model() -> None:
    ordinary = generator._disclosure("lab/alpha")
    supplier = generator._disclosure("typesafe/jev")

    for disclosure in (ordinary, supplier):
        assert "https://modelspec.dev/legal/neutrality/" in disclosure
        assert "read 2026-09-23" in disclosure


def test_x_fallback_keeps_compact_supplier_and_neutrality_disclosures() -> None:
    draft = {"title": "Value angle"}
    text = generator._post_text(
        draft,
        generator._disclosure("typesafe/jev"),
        "x",
        model_id="typesafe/jev",
    )

    assert len(text.rstrip("\n")) <= 280
    assert "TypeSafe" in text
    assert "ModelSpec pays" in text
    assert "No referral fees" in text
    assert "https://modelspec.dev/legal/neutrality/" in text
    assert "read 2026-09-23" in text


def test_local_fit_and_rank_are_separately_sourced(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(generator, "_png", lambda svg, png: False)
    current = tmp_path / "current.json.gz"
    snapshot_id = _snapshot(
        current,
        {"lab/alpha": 90.0, "lab/beta": 80.0, "lab/gamma": 70.0},
    )
    report = tmp_path / "accuracy.json"
    _accuracy(report, snapshot_id)

    manifest = generate(
        model_id="lab/alpha",
        snapshot_path=current,
        accuracy_report_path=report,
        output_dir=tmp_path / "out",
        device=DEVICE,
        snapshot_key=KEY,
    )

    local = next(draft for draft in manifest["drafts"] if draft["angle"] == "local")
    fit = next(claim for claim in local["claims"] if "estimated to fit" in claim["text"])
    rank = next(claim for claim in local["claims"] if "ranks #1" in claim["text"])
    assert fit["source"] == SOURCES["src-lab-docs"]
    assert rank["source"] == generator.SNAPSHOT_URL


def test_local_angle_calls_a_filtered_winner_number_one_among_fitting_models(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(generator, "_png", lambda svg, png: False)
    current = tmp_path / "current.json.gz"
    snapshot_id = _snapshot(
        current,
        {"lab/alpha": 80.0, "lab/beta": 90.0, "lab/gamma": 70.0},
        non_fitting={"lab/beta", "lab/delta"},
    )
    report = tmp_path / "accuracy.json"
    _accuracy(report, snapshot_id)

    manifest = generate(
        model_id="lab/alpha",
        snapshot_path=current,
        accuracy_report_path=report,
        output_dir=tmp_path / "out",
        device=DEVICE,
        snapshot_key=KEY,
    )

    local = next(draft for draft in manifest["drafts"] if draft["angle"] == "local")
    rank = next(claim for claim in local["claims"] if "ranks #1" in claim["text"])
    assert rank["text"] == (
        "lab/alpha ranks #1 among models fitting nvidia_rtx_4090 for Software engineering "
        "within the text generator class."
    )


def test_honest_gaps_omit_unknowns_belonging_to_an_unrelated_model(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(generator, "_png", lambda svg, png: False)
    current = tmp_path / "current.json.gz"
    snapshot_id = _snapshot(
        current,
        {"lab/alpha": 90.0, "lab/beta": 80.0, "lab/gamma": 70.0},
    )
    report = tmp_path / "accuracy.json"
    _accuracy(report, snapshot_id)

    manifest = generate(
        model_id="lab/alpha",
        snapshot_path=current,
        accuracy_report_path=report,
        output_dir=tmp_path / "out",
        snapshot_key=KEY,
    )

    assert "honest_gaps" not in {draft["angle"] for draft in manifest["drafts"]}


def test_honest_gaps_report_unknowns_for_the_requested_model(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(generator, "_png", lambda svg, png: False)
    current = tmp_path / "current.json.gz"
    snapshot_id = _snapshot(
        current,
        {"lab/alpha": 90.0, "lab/beta": 80.0, "lab/gamma": 70.0},
    )
    report = tmp_path / "accuracy.json"
    _accuracy(report, snapshot_id)

    manifest = generate(
        model_id="lab/delta",
        snapshot_path=current,
        accuracy_report_path=report,
        output_dir=tmp_path / "out",
        snapshot_key=KEY,
    )

    gaps = next(draft for draft in manifest["drafts"] if draft["angle"] == "honest_gaps")
    assert gaps["claims"][0]["text"].startswith("lab/delta is not yet ranked: 1 outstanding")


def test_weekly_mover_requires_the_targets_move_to_be_globally_largest(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(generator, "_png", lambda svg, png: False)
    current = tmp_path / "current.json.gz"
    previous = tmp_path / "previous.json.gz"
    snapshot_id = _snapshot(
        current,
        {"lab/delta": 95.0, "lab/alpha": 90.0, "lab/beta": 80.0, "lab/gamma": 70.0},
    )
    _snapshot(
        previous,
        {"lab/beta": 95.0, "lab/gamma": 90.0, "lab/alpha": 80.0, "lab/delta": 70.0},
    )
    report = tmp_path / "accuracy.json"
    _accuracy(report, snapshot_id)

    manifest = generate(
        model_id="lab/alpha",
        snapshot_path=current,
        previous_snapshot_path=previous,
        accuracy_report_path=report,
        output_dir=tmp_path / "out",
        device=DEVICE,
        snapshot_key=KEY,
    )

    assert "weekly_movers" not in {draft["angle"] for draft in manifest["drafts"]}


def test_social_generator_has_no_network_or_posting_client() -> None:
    root = Path(__file__).resolve().parents[1] / "scripts" / "social"
    forbidden_imports = {"httpx", "requests", "urllib", "socket", "tweepy", "linkedin"}
    for path in root.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                assert not ({alias.name.split(".")[0] for alias in node.names} & forbidden_imports)
            if isinstance(node, ast.ImportFrom):
                assert (node.module or "").split(".")[0] not in forbidden_imports
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                assert node.func.attr not in {"post", "put", "patch"}
