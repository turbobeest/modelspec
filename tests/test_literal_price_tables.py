"""Published literal table props are data; executable expressions are not read."""

from datetime import date

import pytest

from decision import verify
from decision.model import SourceRef, TargetRef, VerificationActor


class Page:
    def __init__(self, text):
        self.body = text

    def text(self, *_args):
        return self.body


def read(row, value=0.57, *, column='"Input Price (Cache Miss)"'):
    text = '''# Batch pricing
<DocTable
columns={[
{ title: "Model", width: "40%" },
{ title: "Unit", width: "20%" },
{ title: COLUMN, width: "20%" },
{ title: "Output Price", width: "20%" },
rows={[
ROW
Prices per million tokens.
'''.replace('COLUMN', column).replace('ROW', row)
    claim = verify.Claim(
        target=TargetRef(kind="fact", id="fixture#offering.price.batch_input"),
        subject="provider/lab/fixture/global/standard", names=("Fixture Model",),
        field="offering.price.batch_input", value=value, unit="usd_per_1m_tokens",
        collector=VerificationActor(agent="collector", model_family="human", method="manual@1"),
        sources=(SourceRef(source_id="page", snapshot_ref="sha256:" + "0" * 64,
                           cited_regions=["page"]),),
    )
    return verify.verify(claim, Page(text), verify.deterministic_extractors(), today=date(2026, 11, 5))


def test_literal_doc_table_selects_the_exact_model_and_price_column():
    rows = ('["Fixture Model Ultra (Batch)", "1M tokens", "$5", "$9"],\n'
            '["FIXTURE--Model (Batch)", "1M tokens", "$0.57", "$2.40"],')
    assert read(rows).outcome == "verified"
    assert read(rows, 5).outcome == "mismatch"


@pytest.mark.parametrize("row", [
    '["Fixture Model Ultra (Batch)", "1M tokens", "$0.57", "$2.40"],',
    '["Fixture Model (Batch)", "1M tokens", inputPrice(), "$2.40"],',
    '["Fixture Model (Batch)", "1M tokens", "$0.57" + surcharge, "$2.40"],',
    '["Fixture Model (Batch)", "1M tokens", "$0.57", "$2.40", "$9"],',
])
def test_literal_doc_table_refuses_siblings_expressions_and_shifted_cells(row):
    assert read(row).outcome != "verified"


def test_literal_doc_table_requires_a_literal_column_title():
    row = '["Fixture Model (Batch)", "1M tokens", "$0.57", "$2.40"],'
    assert read(row, column="columnTitle()").outcome != "verified"


def test_literal_doc_table_refuses_a_malformed_quoted_header():
    row = '["Fixture Model (Batch)", "1M tokens", "$0.57", "$2.40"],'
    assert read(row, column=r'"Input\q Price"').outcome != "verified"
