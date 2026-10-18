"""MODEL-367 exact templates. All public page fixtures are synthetic."""

from dataclasses import replace
from datetime import date

import pytest

from decision import verify
from decision.model import CitedRegion, Source, SourceRef, TargetRef, VerificationActor
from decision.sources import CopyStore

TODAY = date(2026, 10, 18)
PREFIX = "offering.subscription."
LITE = "xai/subscription/supergrok-lite"
HEAVY = "xai/subscription/supergrok-heavy"
CHECK = '<svg viewBox="0 0 16 16"><path d="M3 8L6 11L13 4"/></svg>'
MINUS = '<svg viewBox="0 0 16 16"><path d="M3 8H13"/></svg>'
HEADER = '<tr><th>Feature</th><th>SuperGrok Lite</th><th>SuperGrok Heavy</th></tr>'
MODEL_ROW = f'<tr><th>Grok 4.6</th><td>{CHECK}</td><td>{CHECK}</td></tr>'
BUILD_ROW = f'<tr><th>Grok Build</th><td>{CHECK}</td><td>{CHECK}</td></tr>'
BOT_ROW = f'<tr><th>Grok Bot</th><td>{MINUS}</td><td>{CHECK}</td></tr>'
MATRIX = f'<section id="matrix"><table>{HEADER}{MODEL_ROW}{BUILD_ROW}{BOT_ROW}</table></section>'
PAGE = f'<html><body><h1>Synthetic test page</h1>{MATRIX}</body></html>'


class Fallback:
    """A reader that would admit the claim if exact-template dispatch leaked."""

    actor = VerificationActor(agent="fallback", model_family="mistral", method="fixture")

    def accepts(self, text):
        return True

    def extract(self, claim, text):
        value = ", ".join(claim.value) if isinstance(claim.value, list) else claim.value
        return [verify.Reading(claim.names[0], value)]


def check(tmp_path, page=PAGE, *, plan=LITE, field="models_covered", value=("xai/grok-4-6",),
          url="https://x.ai/pricing", kind="provider_documentation", readers=None,
          normaliser="text-default", region_id="page", damage=None, names=None,
          locator_value="", subject=None):
    store = CopyStore(tmp_path / "copies")
    ref = store.put(page.encode())
    source = Source(
        id="pricing", url=url, kind=kind, normaliser=normaliser,
        cited_regions=[CitedRegion(id=region_id, locator={"kind": "page", "value": locator_value})],
    )
    if damage == "corrupt":
        store.path(ref).write_text("corrupt bytes")
    elif damage == "missing":
        store.path(ref).unlink()
    claim = verify.Claim(
        target=TargetRef(kind="fact", id=f"{plan}#{PREFIX}{field}"), subject=subject or plan,
        names=names or (("SuperGrok Lite",) if plan == LITE else ("SuperGrok Heavy",)),
        field=PREFIX + field, value=list(value) if isinstance(value, tuple) else value,
        collector=VerificationActor(agent="fixture", model_family="openai", method="collect"),
        sources=(SourceRef(source_id=source.id, snapshot_ref=ref,
                           cited_regions=[region_id]),),
    )
    extractors = verify.deterministic_extractors() if readers is None else readers
    result = verify.verify(claim, verify.StoredRegions(store, {source.id: source}),
                           [*extractors, Fallback()], today=TODAY)
    return result, claim


MUTATIONS = {
    "reordered_columns": PAGE.replace(HEADER, HEADER.replace("Lite", "TEMP")
                                      .replace("Heavy", "Lite").replace("TEMP", "Heavy")),
    "extra_column": PAGE.replace(HEADER, HEADER.replace('</tr>', '<th>SuperGrok Extra</th></tr>')),
    "swapped_glyph": PAGE.replace(BOT_ROW, BOT_ROW.replace(MINUS, CHECK)),
    "renamed_plan": PAGE.replace("SuperGrok Lite", "SuperGrok Light"),
    "changed_row_label": PAGE.replace("Grok 4.6", "Grok 4.7"),
    "cell_moved_one_column": PAGE.replace(BOT_ROW, f'<tr><th>Grok Bot</th><td>{CHECK}</td>'
                                         f'<td>{MINUS}</td></tr>'),
    "unknown_glyph": PAGE.replace('d="M3 8H13"', 'd="M0 0L8 8"'),
    "duplicate_region": PAGE.replace(MATRIX, MATRIX + MATRIX),
    "missing_region": PAGE.replace(MATRIX, ""),
}


@pytest.mark.parametrize("mutation", MUTATIONS)
def test_unreviewed_matrix_never_falls_back(tmp_path, mutation):
    result, _ = check(tmp_path, MUTATIONS[mutation])
    assert result.outcome == "mismatch"
    assert result.reason.startswith("template drifted:")
    assert result.verification.verifier.method == "xai-exact-template@1"


@pytest.mark.parametrize("plan", [LITE, HEAVY])
@pytest.mark.parametrize("field", ["models_covered", "programmatic_or_agent_use",
                                    "usage_allowance", "coverage_quote"])
def test_no_approved_consumer_template_cannot_verify_absence(tmp_path, plan, field):
    result, _ = check(tmp_path, plan=plan, field=field, value=None)
    assert result.outcome == "mismatch"
    assert result.reason.startswith("template drifted:")


@pytest.mark.parametrize("url,kind", [
    ("https://x.ai.evil.test/pricing", "provider_documentation"),
    ("http://x.ai/pricing", "provider_documentation"),
    ("https://x.ai/pricing?different=1", "provider_documentation"),
    ("https://x.ai/pricing", "provider_terms"),
    ("https://x.ai/pricing", None),
])
def test_xai_claim_rejects_wrong_source_before_other_readers(tmp_path, url, kind):
    result, _ = check(tmp_path, url=url, kind=kind)
    assert result.outcome == "mismatch"
    assert result.reason.startswith("template drifted:")


@pytest.mark.parametrize("value", [None, "Grok Business includes Grok 4.6"])
def test_business_coverage_quote_cannot_use_a_stale_or_null_claim(tmp_path, value):
    result, _ = check(tmp_path, plan="xai/subscription/business", field="coverage_quote",
                      value=value, url="https://x.ai/grok/business", names=("Grok Business",))
    assert result.outcome == "mismatch"
    assert result.reason.startswith("template drifted:")


@pytest.mark.parametrize("damage", ["corrupt", "missing"])
def test_missing_or_corrupt_copy_stays_unreachable(tmp_path, damage):
    result, _ = check(tmp_path, damage=damage)
    assert result.outcome == "unreachable"


def test_template_drift_quarantines_an_earlier_verified_value(tmp_path):
    result, claim = check(tmp_path, MUTATIONS["swapped_glyph"])
    log = verify.VerificationLog(tmp_path / "verification")
    from decision.model import Verification, VerificationTarget, value_hash
    log.append(Verification(
        target=VerificationTarget(kind="fact", id=claim.target.id,
                                  value_hash=value_hash(claim.value)),
        collector=claim.collector,
        verifier=VerificationActor(agent="old-reader", model_family="deterministic", method="old"),
        method="old", outcome="verified", date=date(2026, 10, 17),
    ))
    assert not log.is_quarantined(claim.target)
    assert result.verification is not None
    log.append(result.verification)
    assert log.is_quarantined(claim.target)


@pytest.fixture
def reviewed_template():
    from decision.xai_matrix import MatrixColumn, MatrixRow, XaiMatrixTemplate

    return XaiMatrixTemplate(
        source_url="https://x.ai/pricing", region_id="page",
        document_sha256="9fe2ce668ebeb9ba1e4905a92cbe81976591412e4a89af1907e6ac14dfc69b40",
        region_sha256="edf4ac1deaaba301dd332945726950e86fda25d5a9e1042fe1287f9a26043836",
        region_path=(0, 0, 1),
        header_path=(0, 0), header_children=3,
        rows_path=(0,), rows_children=4,
        columns=(MatrixColumn("SuperGrok Lite", LITE, (0, 0, 1)),
                 MatrixColumn("SuperGrok Heavy", HEAVY, (0, 0, 2))),
        rows=(MatrixRow("Grok 4.6", (0, 1, 0), ((0, 1, 1), (0, 1, 2))),
              MatrixRow("Grok Build", (0, 2, 0), ((0, 2, 1), (0, 2, 2))),
              MatrixRow("Grok Bot", (0, 3, 0), ((0, 3, 1), (0, 3, 2)))),
        glyphs=(("e95aa0773a0e7d0adb8f380f68a88692510bc545941a170f60b918820a732470", True),
                ("c77e7b599af560a27dd393503d3328e8941733e528182bc2c9469f9c0be8f3e7", False)),
        models=(("Grok 4.6", "xai/grok-4-6"),),
        agent_products=("Grok Build", "Grok Bot"),
    )


@pytest.mark.parametrize("plan", [LITE, HEAVY])
def test_reviewed_synthetic_matrix_verifies_exact_models(tmp_path, reviewed_template, plan):
    result, _ = check(tmp_path, plan=plan,
                      readers=[verify.XaiMatrixExtractor(templates=(reviewed_template,))])
    assert result.outcome == "verified", result
    assert result.verification.verifier.method == "xai-exact-template@1"


@pytest.mark.parametrize("plan,value", [
    (LITE, "Grok Build included; Grok Bot not included"),
    (HEAVY, "Grok Build included; Grok Bot included"),
])
def test_reviewed_synthetic_matrix_preserves_each_product_cell(
    tmp_path, reviewed_template, plan, value,
):
    result, _ = check(tmp_path, plan=plan, field="programmatic_or_agent_use", value=value,
                      readers=[verify.XaiMatrixExtractor(templates=(reviewed_template,))])
    assert result.outcome == "verified", result
    wrong, _ = check(tmp_path, plan=plan, field="programmatic_or_agent_use", value="API included",
                     readers=[verify.XaiMatrixExtractor(templates=(reviewed_template,))])
    assert wrong.outcome == "mismatch"


@pytest.mark.parametrize("mutation", MUTATIONS)
def test_reviewed_matrix_mutation_cannot_fall_through(tmp_path, reviewed_template, mutation):
    result, _ = check(tmp_path, MUTATIONS[mutation],
                      readers=[verify.XaiMatrixExtractor(templates=(reviewed_template,))])
    assert result.outcome == "mismatch"
    assert result.reason.startswith("template drifted:")
    assert result.verification.verifier.method == "xai-exact-template@1"


@pytest.mark.parametrize("field,value", [
    ("models_covered", None),
    ("models_covered", ("xai/grok-4-7",)),
    ("coverage_quote", "SuperGrok Lite includes Grok 4.6"),
    ("usage_allowance", "100 messages per day"),
])
def test_reviewed_matrix_does_not_supply_unsupported_values(
    tmp_path, reviewed_template, field, value,
):
    result, _ = check(tmp_path, field=field, value=value,
                      readers=[verify.XaiMatrixExtractor(templates=(reviewed_template,))])
    assert result.outcome == "mismatch"


@pytest.mark.parametrize("change", [
    {"document_sha256": "0" * 64},
    {"region_sha256": "0" * 64},
    {"region_path": (9, 9)},
    {"header_children": 4},
    {"rows_children": 5},
    {"glyphs": ()},
    {"models": (("Grok 4.6", "xai/nonexistent-model"),)},
])
def test_incomplete_or_wrong_review_metadata_cannot_verify(tmp_path, reviewed_template, change):
    template = replace(reviewed_template, **change)
    result, _ = check(tmp_path, readers=[verify.XaiMatrixExtractor(templates=(template,))])
    assert result.outcome == "mismatch"
    assert result.reason.startswith("template drifted:")


@pytest.mark.parametrize("url,kind", [
    ("https://example.test/pricing", "provider_documentation"),
    ("https://x.ai/pricing", "provider_terms"),
])
def test_approved_bytes_need_exact_source_binding(tmp_path, reviewed_template, url, kind):
    result, _ = check(tmp_path, url=url, kind=kind,
                      readers=[verify.XaiMatrixExtractor(templates=(reviewed_template,))])
    assert result.outcome == "mismatch"
    assert result.reason.startswith("template drifted:")


def test_excerpt_cannot_hide_changed_document_ownership(tmp_path, reviewed_template):
    result, _ = check(
        tmp_path, PAGE + '<p>The preceding matrix is archived and no longer applies.</p>',
        locator_value="::excerpt=" + PAGE,
        readers=[verify.XaiMatrixExtractor(templates=(reviewed_template,))],
    )
    assert result.outcome == "mismatch"
    assert result.reason.startswith("template drifted:")


def test_targeted_fact_cannot_use_another_offering_subject(tmp_path, reviewed_template):
    result, _ = check(tmp_path, subject=HEAVY,
                      readers=[verify.XaiMatrixExtractor(templates=(reviewed_template,))])
    assert result.outcome == "mismatch"
    assert result.reason.startswith("template drifted:")


def test_html_normalizer_cannot_flatten_the_reviewed_matrix(tmp_path, reviewed_template):
    result, _ = check(tmp_path, normaliser="html-default",
                      readers=[verify.XaiMatrixExtractor(templates=(reviewed_template,))])
    assert result.outcome == "mismatch"
    assert result.reason.startswith("template drifted:")
