"""The release breakdown generator (MODEL-224; design docs/design/release-blog.md §3).

Every test builds real signed snapshots and runs the real decision engine.
"""

from __future__ import annotations

import base64
import json
from datetime import date
from pathlib import Path

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from decision.contract import parse_spec
from decision.engine import decide
from decision.model import evidence_verification_value
from decision.registry import default as default_registry
from decision.snapshot import Ed25519Signer, SnapshotInputs, build_snapshot, load_snapshot_bytes
from release_blog import smoothing
from release_blog.__main__ import main
from release_blog.breakdown import build_breakdown, to_bytes
from release_blog.gates import BreakdownError, guard_output, load_signed
from release_blog.model import SCHEMA_PATH, Breakdown, Cited, schema
from release_blog.render import render, untraced_numbers
from release_blog.tone import refused_words
from release_blog.wording import headline
from tests.snapshot_records import SOURCES, evidence, fact, model, offering, verification

AS_OF = date(2026, 9, 26)
KEY_ID = "ed25519-test"
PRIVATE = Ed25519PrivateKey.generate()
PUBLIC = {KEY_ID: PRIVATE.public_key().public_bytes(
    serialization.Encoding.Raw, serialization.PublicFormat.Raw)}
SIGNER = Ed25519Signer(KEY_ID, base64.b64encode(PRIVATE.private_bytes(
    serialization.Encoding.Raw, serialization.PrivateFormat.Raw,
    serialization.NoEncryption())).decode("ascii"))
NEW = "lab/alpha"
TAGS = {
    "swe_bench_pro": [("software_engineering", "direct")],
    "terminal_bench": [("software_engineering", "direct")],
    "livecodebench": [("software_engineering", "direct")],
    "cursorbench": [("software_engineering", "proxy")],
    "mmlu_pro": [("reasoning", "direct")],
}
SOURCES_ALL = {**SOURCES, "src-lab-page": "https://lab.example.com/alpha-launch"}
ACCURACY = {"profile": "pr", "status": "pass"}


def _model(mid: str) -> dict:
    row = model(mid)
    row["facts"] += [fact("model", mid, "model.class", "text-generator"),
                     fact("model", mid, "model.lifecycle", "active")]
    return row


def _offering(mid: str, price: float) -> dict:
    row = offering(mid)
    oid = f"lab-api/{mid}/global/standard"
    row["facts"] = [
        fact("offering", oid, "offering.price.input", price, source="src-pricing"),
        fact("offering", oid, "offering.price.output", price * 4, source="src-pricing"),
    ]
    return row


def _row(mid, bench, score, *, unit="percent", **kw) -> dict:
    """An evidence row whose verification matches it after any edit."""
    row = evidence(mid, bench, score, **kw)
    row["unit"] = unit
    if kw.get("measured_by") == "provider_self_report":
        row["sources"][0]["source_id"] = "src-lab-page"
        row["source_url"] = SOURCES_ALL["src-lab-page"]
        row["source_kind"] = "provider_self_report"
    if kw.get("outcome", "verified"):
        row["verification"] = verification(
            "evidence", row["id"], kw.get("outcome", "verified"),
            value=evidence_verification_value(row))
    return row


def _plans() -> list[dict]:
    def plan(name: str, facts: list[dict]) -> dict:
        return {"kind": "subscription", "provider": "lab-api", "plan": name,
                "name": name.title(), "facts": facts}

    def f(plan_id: str, facet: str, value) -> dict:
        return fact("offering", f"lab-api/subscription/{plan_id}", facet, value,
                    source="src-pricing")

    return [
        plan("pro", [f("pro", "offering.subscription.price", 20),
                     f("pro", "offering.subscription.billing_period", "monthly"),
                     f("pro", "offering.subscription.models_covered", [NEW])]),
        plan("team", [f("team", "offering.subscription.price", 300),
                      f("team", "offering.subscription.billing_period", "annual")]),
        plan("lite", [f("lite", "offering.subscription.price", 5),
                      f("lite", "offering.subscription.billing_period", "monthly"),
                      f("lite", "offering.subscription.models_covered", ["lab/beta"])]),
    ]


def _others() -> list[dict]:
    rows = []
    for mid, base in (("lab/beta", 60.0), ("lab/gamma", 50.0)):
        rows += [_row(mid, "swe_bench_pro", base), _row(mid, "terminal_bench", base - 5),
                 _row(mid, "livecodebench", base + 5), _row(mid, "mmlu_pro", base + 10)]
    return rows


def _new_rows(*, claim_source: str = "src-lab-page") -> list[dict]:
    rows = [
        # same setup: a difference is computed
        _row(NEW, "swe_bench_pro", 70.0, measured_by="provider_self_report"),
        _row(NEW, "swe_bench_pro", 67.9),
        # effort differs: both shown, no difference
        _row(NEW, "terminal_bench", 50.0, measured_by="provider_self_report", effort="high"),
        _row(NEW, "terminal_bench", 48.0, effort="medium"),
        # unit differs: not compared
        _row(NEW, "mmlu_pro", 80.0, measured_by="provider_self_report"),
        _row(NEW, "mmlu_pro", 0.78, unit="fraction"),
        # a claim nobody has read yet
        _row(NEW, "cursorbench", 55.0, measured_by="provider_self_report"),
        # an independent reading the lab did not report
        _row(NEW, "livecodebench", 72.0),
        # a reading without a second key: held back, never shown
        _row(NEW, "livecodebench", 99.0, eid="alpha-unverified", outcome="mismatch"),
    ]
    if claim_source != "src-lab-page":
        for row in rows:
            if row["measured_by"] == "provider_self_report":
                row["sources"][0]["source_id"] = claim_source
                row["verification"] = verification(
                    "evidence", row["id"], value=evidence_verification_value(row))
    return rows


def _write(path: Path, *, with_new: bool, sources=None, claim_source="src-lab-page",
           signer=SIGNER) -> Path:
    models = [_model("lab/beta"), _model("lab/gamma")]
    offerings = [_offering("lab/beta", 1.0), _offering("lab/gamma", 0.5)]
    rows = _others()
    if with_new:
        models.append(_model(NEW))
        offerings.append(_offering(NEW, 2.0))
        rows += _new_rows(claim_source=claim_source)
    built = build_snapshot(
        SnapshotInputs(models=models, offerings=offerings,
                       subscriptions=_plans() if with_new else [], evidence=rows,
                       sources=sources or SOURCES_ALL, benchmark_domains=TAGS,
                       benchmark_metadata={b: {"direction": "higher_is_better"} for b in TAGS}),
        gate=False, as_of=AS_OF)
    path.write_bytes(built.to_bytes(key=None, ed25519_signer=signer))
    return path


@pytest.fixture(scope="module")
def pair(tmp_path_factory):
    root = tmp_path_factory.mktemp("release-blog")
    after = load_signed(_write(root / "after.json.gz", with_new=True), public_keys=PUBLIC)
    before = load_signed(_write(root / "before.json.gz", with_new=False), public_keys=PUBLIC)
    return root, after, before


def _build(after, before, **kw) -> Breakdown:
    return build_breakdown(model_id=NEW, after=after, before=before,
                           accuracy={**ACCURACY, "snapshot": after.snapshot_id},
                           name="Alpha 2.5", **kw)


@pytest.fixture(scope="module")
def breakdown(pair) -> Breakdown:
    _, after, before = pair
    return _build(after, before)


def _claim(b: Breakdown, bench: str):
    return next(row for row in b.claims_vs_evidence.claims if row.benchmark == bench)


# ── reproducibility and provenance ─────────────────────────────────────────


def test_same_inputs_give_the_same_bytes(pair, breakdown) -> None:
    _, after, before = pair
    again = _build(after, before)
    assert to_bytes(again) == to_bytes(breakdown)
    assert render(again) == render(breakdown)


def test_every_decision_id_reproduces_from_its_spec(pair, breakdown) -> None:
    _, after, before = pair
    registry = default_registry()
    by_id = {after.snapshot_id: after, before.snapshot_id: before}
    assert {d.purpose for d in breakdown.decisions} >= {
        "standing.software_engineering", "standing.reasoning"}
    for ref in breakdown.decisions:
        again = decide(parse_spec(ref.spec, facets=registry.facet), by_id[ref.snapshot_id],
                       facets=registry.facet)
        assert (again.decision_id, again.spec_hash) == (ref.decision_id, ref.spec_hash)


def _numbers_outside_cited(value, path=""):
    if isinstance(value, dict):
        if "read_date" in value and "value" in value:
            return []
        return [hit for key, item in value.items()
                for hit in _numbers_outside_cited(item, f"{path}/{key}")]
    if isinstance(value, list):
        return [hit for i, item in enumerate(value)
                for hit in _numbers_outside_cited(item, f"{path}/{i}")]
    if isinstance(value, int | float) and not isinstance(value, bool):
        return [path]
    return []


def test_every_number_in_breakdown_json_is_cited(breakdown) -> None:
    raw = json.loads(to_bytes(breakdown))
    stray = _numbers_outside_cited(raw)
    # Spec inputs and bookkeeping, not findings: the revision, the task size a
    # cost is for, and the re-check day offsets the standard fixes.
    allowed = {"/revision"}
    stray = [p for p in stray if p not in allowed
             and not p.endswith(("/task/input", "/task/output"))
             and not (p.startswith("/recheck/schedule/") and p.endswith("/day"))
             and not p.startswith("/decisions/")]
    assert stray == []


def test_a_number_with_no_record_and_no_computation_is_invalid() -> None:
    with pytest.raises(ValueError, match="needs a record_id or a computed origin"):
        Cited(value=1.0, read_date=AS_OF)


def test_schema_file_is_generated_from_the_model() -> None:
    assert json.loads(SCHEMA_PATH.read_text(encoding="utf-8")) == schema()


# ── claims vs evidence (§3.3) ──────────────────────────────────────────────


def test_same_setup_reading_states_the_difference(breakdown) -> None:
    row = _claim(breakdown, "swe_bench_pro")
    assert row.claim.value == 70.0 and row.claim.record_id is not None
    assert row.status == "read"
    [reading] = row.readings
    assert reading.comparability == "same_setup"
    assert reading.differs_in == []
    assert reading.difference is not None
    assert reading.difference.value == -2.1
    assert reading.difference.computed == "difference"
    assert sorted(reading.difference.records) == sorted(
        [row.claim.record_id, reading.value.record_id])


def test_different_effort_shows_both_numbers_without_a_difference(breakdown) -> None:
    [reading] = _claim(breakdown, "terminal_bench").readings
    assert (reading.comparability, reading.differs_in, reading.difference) == (
        "different_setup", ["effort"], None)
    assert reading.value.value == 48.0


def test_different_unit_is_not_compared(breakdown) -> None:
    [reading] = _claim(breakdown, "mmlu_pro").readings
    assert (reading.comparability, reading.differs_in, reading.difference) == (
        "not_comparable", ["unit"], None)


def test_claim_with_no_reading_is_marked_not_differenced(breakdown) -> None:
    row = _claim(breakdown, "cursorbench")
    assert (row.status, row.readings) == ("no_independent_reading_yet", [])
    assert breakdown.not_yet_measured.claims_without_reading == ["cursorbench"]


def test_unreported_lists_independent_readings_without_a_claim(breakdown) -> None:
    assert [(u.benchmark, u.reading.value) for u in breakdown.claims_vs_evidence.unreported] \
        == [("livecodebench", 72.0)]


def test_unverified_row_is_absent_and_counted_as_held_back(breakdown) -> None:
    values = [r.value.value for row in breakdown.claims_vs_evidence.claims for r in row.readings]
    values += [u.reading.value for u in breakdown.claims_vs_evidence.unreported]
    assert 99.0 not in values
    assert "99%" not in render(breakdown)[0]
    held = breakdown.not_yet_measured.held_back
    assert {reason: c.value for reason, c in held.items()} == {"quarantined": 1.0}
    assert held["quarantined"].computed == "snapshot.held_back"


# ── standing, templates, cost ──────────────────────────────────────────────


def test_standing_reports_estimate_band_and_p_best_from_the_decision(breakdown) -> None:
    rows = {row.domain.id: row for row in breakdown.standing}
    assert set(rows) == {"software_engineering", "reasoning"}
    se = rows["software_engineering"]
    assert se.estimate.computed == "capability.estimate"
    assert se.estimate.low < se.estimate.value < se.estimate.high
    assert se.p_best is not None and se.p_best.decision_id == se.decision
    assert se.band in ("best", "rest", "thin")
    assert se.ranked_models.value == 3.0


def test_template_changes_list_only_answers_the_model_is_in(breakdown) -> None:
    changes = breakdown.template_changes.changes
    assert changes, "the fixture's new model enters at least one template"
    assert all(c.band_after is not None or c.band_before is not None for c in changes)
    assert all(c.band_before is None for c in changes)  # it was not in the earlier snapshot


def test_backfill_says_why_there_are_no_template_changes(pair) -> None:
    _, after, _ = pair
    b = _build(after, None)
    assert b.template_changes.changes == []
    assert "no earlier snapshot" in b.template_changes.unavailable
    assert b.generated_from.before is None


def test_cost_per_task_is_computed_from_cited_prices(breakdown) -> None:
    [row] = [o for o in breakdown.cost.offerings if o.task.basis == "contract_default"]
    # (2 × 40,000 + 8 × 4,000) / 1,000,000
    assert row.cost_per_task.value == 0.112
    assert row.cost_per_task.computed == "offering.cost_per_task"
    assert row.cost_per_task.records == sorted(
        [row.price_input.record_id, row.price_output.record_id])


def test_plan_coverage_distinguishes_unknown_from_not_covered(breakdown) -> None:
    plans = {p.plan["id"]: p for p in breakdown.cost.plans}
    assert plans["lab-api/subscription/pro"].covers is True
    assert plans["lab-api/subscription/lite"].covers is False
    assert plans["lab-api/subscription/team"].covers == "unknown"
    team = plans["lab-api/subscription/team"].monthly
    assert (team.value, team.computed) == (25.0, "plan.monthly")


def test_closed_weights_have_no_hardware_section(breakdown) -> None:
    assert breakdown.hardware is None


def test_recheck_schedule_counts_from_first_publication(pair) -> None:
    _, after, before = pair
    b = _build(after, before, first_published=date(2026, 10, 1))
    assert [(r["day"], r["due"]) for r in b.recheck.schedule] == [
        (1, "2026-10-02"), (7, "2026-10-08"), (30, "2026-10-31")]


def test_a_later_revision_diffs_against_the_first(pair, breakdown) -> None:
    _, after, before = pair
    with pytest.raises(BreakdownError, match="needs revision 1"):
        _build(after, before, revision=2)
    second = _build(after, before, revision=2, first_revision=breakdown)
    assert second.changes_since_r1 == []


# ── refusals (§3.9) ────────────────────────────────────────────────────────


def test_unsigned_or_wrongly_signed_snapshot_is_refused(tmp_path) -> None:
    unsigned = _write(tmp_path / "unsigned.json.gz", with_new=True, signer=None)
    with pytest.raises(BreakdownError, match="Ed25519 signature"):
        load_signed(unsigned, public_keys=PUBLIC)
    other = Ed25519PrivateKey.generate().public_key().public_bytes(
        serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    signed = _write(tmp_path / "signed.json.gz", with_new=True)
    with pytest.raises(BreakdownError, match="does not verify"):
        load_signed(signed, public_keys={KEY_ID: other})
    with pytest.raises(BreakdownError, match="no pinned Ed25519 key"):
        load_signed(signed, public_keys={})


def test_a_signal_only_source_in_the_snapshot_is_refused(tmp_path) -> None:
    sources = {**SOURCES_ALL, "src-x-post": "https://x.com/lab/status/1"}
    path = _write(tmp_path / "x.json.gz", with_new=True, sources=sources,
                  claim_source="src-x-post")
    after = load_signed(path, public_keys=PUBLIC)
    with pytest.raises(BreakdownError, match="signal-only source"):
        _build(after, None)


def test_excluded_sources_are_refused() -> None:
    with pytest.raises(BreakdownError, match="excluded source"):
        guard_output({"s": "https://artificialanalysis.ai/models/x"}, "")
    with pytest.raises(BreakdownError, match="excluded source text"):
        guard_output({}, '{"note": "per Artificial Analysis"}')


def test_a_model_with_nothing_admitted_gets_no_breakdown(tmp_path, capsys) -> None:
    path = _write(tmp_path / "a.json.gz", with_new=True)
    after = load_snapshot_bytes(path.read_bytes(), key=None, public_keys=PUBLIC)
    with pytest.raises(BreakdownError, match="not a model"):
        build_breakdown(model_id="lab/none", after=after, before=None,
                        accuracy={**ACCURACY, "snapshot": after.snapshot_id})


def test_cli_refuses_and_writes_nothing_on_a_bad_accuracy_report(tmp_path, monkeypatch,
                                                                 capsys) -> None:
    import release_blog.gates as gates

    monkeypatch.setattr(gates, "load_public_keys", lambda: PUBLIC)
    path = _write(tmp_path / "a.json.gz", with_new=True)
    report = tmp_path / "accuracy.json"
    report.write_text(json.dumps({"status": "fail"}), encoding="utf-8")
    out = tmp_path / "draft"
    code = main(["draft", "--model", NEW, "--after", str(path), "--accuracy", str(report),
                 "--out-dir", str(out)])
    assert code == 2
    assert "refused" in capsys.readouterr().err
    assert not out.exists()


# ── the rendered post ──────────────────────────────────────────────────────


def test_every_number_in_the_post_has_a_footnote(breakdown) -> None:
    post, charts = render(breakdown)
    assert untraced_numbers(post, allowed=["Alpha 2.5", "Pro", "Team", "Lite"]) == []
    assert "67.9%[^" in post and "2.1[^" in post
    assert "The independent reading is 2.1" in post and "lower than the lab's figure" in post
    assert set(charts) == {"claims.svg", "standing.svg", "cost.svg"}
    assert refused_words(post) == []


def test_untraced_numbers_finds_a_bare_number() -> None:
    assert untraced_numbers("It scored 71.2 on it.") == ["71.2"]
    assert untraced_numbers("It scored 71.2%[^3] on `swe_bench_2`, 2026-09-28.") == []


def test_tone_list_refuses_characterising_a_lab() -> None:
    assert refused_words("The lab's figure looks inflated and cherry-picked.") == [
        "inflated", "cherry-picked"]
    assert refused_words("It is in the best band, higher than the lab's figure.") == []


def test_headline_rules_are_neutral_and_digit_free() -> None:
    text = headline(name="Alpha", best=[("Software engineering", False)], ranked_outside=[],
                    thin=[], claims=2, claims_read=1, same_setup=1)
    assert text.text == ("Alpha is in the leading band for software engineering; "
                         "independent readings sit beside the lab's figures")
    assert headline(name="Alpha", best=[], ranked_outside=[], thin=["Maths"], claims=1,
                    claims_read=0, same_setup=0).text == (
        "Alpha: evidence is too thin to rank yet in maths; "
        "the lab's figures await independent readings")
    long = headline(name="Alpha", best=[("Software engineering", False),
                                        ("Agentic and tool use", False)],
                    ranked_outside=[], thin=[], claims=1, claims_read=0, same_setup=0)
    assert long.text == ("Alpha is in the leading band for software engineering, "
                         "and agentic and tool use")
    assert long.rule == "leading_band+awaiting,dropped_for_length"
    assert headline(name="Alpha", best=[], ranked_outside=[], thin=[], claims=0,
                    claims_read=0, same_setup=0).rule == "no_estimate+no_claims"


# ── an LLM may smooth wording, and nothing else ────────────────────────────

PARAGRAPH = ("In software engineering, the model is in the leading band with 4[^4] other "
             "models; the evidence does not separate them.")


def _post(paragraph: str = PARAGRAPH) -> str:
    return f"# Title\n\n{paragraph}\n\n| a | b |\n|---|---|\n| 1[^1] | 2[^2] |\n\n[^1]: x"


def test_smoothing_keeps_a_rewording() -> None:
    reworded = ("In software engineering the model sits in the leading band alongside "
                "4[^4] other models; the evidence does not separate them.")
    assert smoothing.smooth(_post(), lambda block: reworded if "leading" in block
                            else block) == _post(reworded)


@pytest.mark.parametrize(("rewrite", "problem"), [
    (lambda p: p.replace("4[^4]", "5[^4]"), "numbers changed"),
    (lambda p: p.replace("[^4]", ""), "footnotes changed"),
    (lambda p: p.replace("does not separate", "does separate"), "claim words changed"),
    (lambda p: p.replace("leading band", "best band"), "claim words changed"),
    (lambda p: p + " It is the strongest release this year.", "a sentence was added"),
    (lambda p: p.replace("them.", "them, an impressive result."), "refused words"),
    (lambda p: p + " See https://lab.example.com.", "links changed"),
    (lambda p: p.replace("the model", "lab/alpha"), "model ids changed"),
])
def test_smoothing_refuses_a_changed_number_or_claim(rewrite, problem) -> None:
    with pytest.raises(smoothing.SmoothingError, match=problem):
        smoothing.smooth(_post(), lambda b: rewrite(b) if smoothing.is_prose(b)
                         and "leading" in b else b)


def test_smoothing_never_touches_tables_or_footnotes() -> None:
    changed = _post().replace("| 1[^1] |", "| 3[^1] |")
    with pytest.raises(smoothing.SmoothingError, match="not prose"):
        smoothing.check_smoothed(_post(), changed)


def test_smoothing_the_real_post_with_identity_passes(breakdown) -> None:
    post, _ = render(breakdown)
    assert smoothing.smooth(post, lambda block: block) == post


# ── the snapshot key (content.held_back) ───────────────────────────────────


def test_held_back_is_unknown_for_a_snapshot_that_predates_it(pair) -> None:
    _, after, _ = pair
    assert after.held_back(NEW) == {"quarantined": 1}
    assert after.held_back("lab/beta") == {}
    content = dict(after_content := json.loads(
        __import__("gzip").decompress((pair[0] / "after.json.gz").read_bytes()))["content"])
    assert after_content["held_back"] == {NEW: {"quarantined": 1}}
    content.pop("held_back")
    from decision.snapshot import LoadedSnapshot
    old = LoadedSnapshot({"snapshot_id": "snap_x", "content_hash": "sha256:x",
                          "content": content}, include_archive=False,
                         signature_verified=False)
    assert old.held_back(NEW) is None
