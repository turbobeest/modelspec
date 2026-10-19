"""MODEL-408 parser controls. Every document here is synthetic.

Production citation assurance is covered in test_xai_consumer_citations.py.
"""

import pytest

from decision import verify
from tests.test_xai_matrix_reader import CHECK, MINUS, check

PLANS = ("free", "plus", "premium", "super", "ultra", "teams", "enterprise")
LABELS = ("Free", "Plus", "Premium", "Super", "Ultra", "Teams", "Enterprise")
PRICES = ("$0/month", "$8/month", "$30/month", "$100/month", "$200/month",
          "$30+/user/month", "Custom")
HEADER = "<tr><th>Feature</th>" + "".join(
    f"<th><span>{label}</span><span>{price}</span></th>"
    for label, price in zip(LABELS, PRICES)
) + "</tr>"
BUILD = "<tr><th>Grok Build</th><td><span>Limited</span></td>" + f"<td>{CHECK}</td>" * 6 + "</tr>"
BOT = "<tr><th>Grok Bot</th>" + f"<td>{MINUS}</td>" * 2 + f"<td>{CHECK}</td>" * 5 + "</tr>"
MATRIX = f'<section id="matrix"><table>{HEADER}{BUILD}{BOT}</table></section>'
PAGE = f"<html><body><h1>Synthetic current-plan page</h1>{MATRIX}</body></html>"
MUTATIONS = {
    "reordered_column": PAGE.replace("Free", "TEMP").replace("Plus", "Free")
    .replace("TEMP", "Plus"),
    "extra_column": PAGE.replace(HEADER, HEADER.replace("</tr>", "<th>Extra</th></tr>")),
    "swapped_glyph": PAGE.replace(BOT, BOT.replace(MINUS, CHECK, 1)),
    "renamed_plan": PAGE.replace("Premium", "Premium Extra"),
    "changed_row": PAGE.replace("Grok Build", "Grok Builder"),
    "moved_cell": PAGE.replace(BOT, BOT.replace(
        f"<td>{MINUS}</td><td>{CHECK}</td>", f"<td>{CHECK}</td><td>{MINUS}</td>", 1)),
}


@pytest.fixture(autouse=True)
def synthetic_consumer_parser_policy(monkeypatch):
    """Isolate parsing from retention, without changing the production policy."""
    monkeypatch.setattr("decision.retention.cite_only_hosts", lambda: ())


def current_check(tmp_path, *, plan="free", field="price", value=0, **kwargs):
    return check(tmp_path, plan=f"xai/subscription/{plan}", field=field,
                 value=value, names=(plan.title(),), **kwargs)[0]


@pytest.mark.parametrize("plan", PLANS)
@pytest.mark.parametrize("field", [
    "price", "billing_period", "models_covered", "programmatic_or_agent_use",
    "usage_allowance", "coverage_quote",
])
def test_current_plan_cannot_verify_an_unapproved_document_or_null(tmp_path, plan, field):
    result = current_check(tmp_path, page=PAGE, plan=plan, field=field, value=None)
    assert result.outcome == "mismatch"
    assert result.reason.startswith("template drifted:")
    assert result.verification.verifier.method == "xai-exact-template@1"


@pytest.mark.parametrize("mutation", MUTATIONS)
def test_current_matrix_mutation_cannot_fall_back(tmp_path, mutation):
    result = current_check(tmp_path, page=MUTATIONS[mutation])
    assert result.outcome == "mismatch"
    assert result.reason.startswith("template drifted:")
    assert result.verification.verifier.method == "xai-exact-template@1"


@pytest.fixture
def current_template():
    from decision.xai_matrix import MatrixColumn, MatrixRow, XaiMatrixTemplate

    return XaiMatrixTemplate(
        source_url="https://x.ai/pricing", region_id="page",
        copy_sha256="0bc6708fb8b71a76c1f6852fc374ea14e386f30de1bae582cd2e78768bd247c6",
        document_sha256="0bc6708fb8b71a76c1f6852fc374ea14e386f30de1bae582cd2e78768bd247c6",
        region_sha256="1a772312d0d003e92197e946f58e9987da445364ec579b66843fbaa93f7a0ac1",
        region_path=(0, 0, 1), header_path=(0, 0), header_children=8,
        rows_path=(0,), rows_children=3,
        columns=tuple(MatrixColumn(label, f"xai/subscription/{plan}", (0, 0, i, 0), (0, 0, i, 1))
                      for i, (label, plan) in enumerate(zip(LABELS, PLANS), 1)),
        rows=(MatrixRow("Grok Build", (0, 1, 0), tuple((0, 1, i) for i in range(1, 8))),
              MatrixRow("Grok Bot", (0, 2, 0), tuple((0, 2, i) for i in range(1, 8)))),
        glyphs=(("e95aa0773a0e7d0adb8f380f68a88692510bc545941a170f60b918820a732470", True),
                ("c77e7b599af560a27dd393503d3328e8941733e528182bc2c9469f9c0be8f3e7", False)),
        models=(), agent_products=("Grok Build", "Grok Bot"),
        text_cells=(("Limited", "limited"),),
    )


@pytest.mark.parametrize("plan,amount", [("free", 0), ("plus", 8), ("premium", 30),
                                        ("super", 100), ("ultra", 200)])
@pytest.mark.parametrize("field", ["price", "billing_period"])
def test_current_plan_reads_its_exact_monthly_price(
    tmp_path, current_template, plan, amount, field,
):
    result = current_check(tmp_path, page=PAGE, plan=plan, field=field,
                           value=amount if field == "price" else "monthly",
                           readers=[verify.XaiMatrixExtractor(templates=(current_template,))])
    assert result.outcome == "verified", result.reason
    assert result.verification.verifier.method == "xai-exact-template@1"


@pytest.mark.parametrize("plan,value", [
    ("free", "Grok Build limited; Grok Bot not included"),
    ("plus", "Grok Build included; Grok Bot not included"),
    ("premium", "Grok Build included; Grok Bot included"),
    ("super", "Grok Build included; Grok Bot included"),
    ("ultra", "Grok Build included; Grok Bot included"),
    ("teams", "Grok Build included; Grok Bot included"),
    ("enterprise", "Grok Build included; Grok Bot included"),
])
def test_current_plan_preserves_product_cell_meanings(tmp_path, current_template, plan, value):
    result = current_check(tmp_path, page=PAGE, plan=plan, field="programmatic_or_agent_use",
                           value=value,
                           readers=[verify.XaiMatrixExtractor(templates=(current_template,))])
    assert result.outcome == "verified", result.reason
    assert result.verification.verifier.method == "xai-exact-template@1"


@pytest.mark.parametrize("mutation", MUTATIONS)
@pytest.mark.parametrize("field,value", [("price", 0), ("billing_period", "monthly"),
    ("programmatic_or_agent_use", "Grok Build limited; Grok Bot not included"),
    ("models_covered", None)])
def test_approved_current_template_rejects_mutation(
    tmp_path, current_template, mutation, field, value,
):
    result = current_check(tmp_path, page=MUTATIONS[mutation], field=field, value=value,
                           readers=[verify.XaiMatrixExtractor(templates=(current_template,))])
    assert result.outcome == "mismatch"
    assert result.reason.startswith("template drifted:")
    assert result.verification.verifier.method == "xai-exact-template@1"


@pytest.mark.parametrize("plan,field,value", [
    ("teams", "price", 30), ("enterprise", "price", 0),
    ("teams", "price", None), ("enterprise", "price", None),
    ("free", "price", 8), ("plus", "price", 8.01), ("plus", "billing_period", "annual"),
    ("free", "programmatic_or_agent_use", "Grok Build included; Grok Bot not included"),
    ("plus", "programmatic_or_agent_use", "Grok API access included"),
    ("premium", "models_covered", ("xai/grok-4-7",)),
    ("premium", "models_covered", ("xai/grok-build-0-1",)),
    ("premium", "models_covered", None),
    ("premium", "models_covered", ()),
])
def test_current_template_never_infers_unsupported_facts(
    tmp_path, current_template, plan, field, value,
):
    result = current_check(tmp_path, page=PAGE, plan=plan, field=field, value=value,
                           readers=[verify.XaiMatrixExtractor(templates=(current_template,))])
    assert result.outcome == "mismatch"
    assert result.verification.verifier.method == "xai-exact-template@1"
