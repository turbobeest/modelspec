"""Table boundaries and billing columns keep readings with their published owner."""

from datetime import date

import pytest

from decision import verify
from decision.model import SourceRef, TargetRef, VerificationActor
from decision.normalise import NORMALISERS, normalise_document


class Page:
    def __init__(self, body):
        self.body = body

    def text(self, *_args):
        return self.body

    def source_url(self, *_args):
        return "https://fixture.example/source"


def read(body, value, *, field="model.context_window", label="Context window",
         unit=None, kind="fact"):
    claim = verify.Claim(
        target=TargetRef(kind=kind, id=f"fixture#{field}"), subject="lab/fixture",
        names=("Fixture Model",), field=field, label=label, value=value, unit=unit,
        collector=VerificationActor(agent="fixture-collector", model_family="human",
                                    method="fixture@1"),
        sources=(SourceRef(source_id="source", snapshot_ref="sha256:" + "0" * 64,
                           cited_regions=["page"]),),
    )
    return verify.verify(claim, Page(body), verify.deterministic_extractors(),
                         today=date(2026, 11, 5))


@pytest.mark.parametrize("next_header", ["Specification", "Comparison results"])
def test_adjacent_html_table_cannot_lend_its_sibling_column(next_header):
    html = (
        "<table><tr><th>Property</th><th>Fixture Model</th><th>Other Model</th></tr>"
        "<tr><td>Context window</td><td>4200</td><td>7000</td></tr></table>"
        f"<table><tr><th>{next_header}</th><th>Fixture Model Ultra</th><th>Other Model</th></tr>"
        "<tr><td>Context window</td><td>9000</td><td>7000</td></tr></table>"
    )
    body = normalise_document(html.encode(), NORMALISERS["html-default"]).text
    assert read(body, 4200).outcome == "verified"
    result = read(body, 9000)
    assert result.outcome == "mismatch", result
    assert any(diff.field == "value" and diff.found == "4200" for diff in result.diffs)


def test_text_and_boolean_facet_rows_do_not_end_the_model_columns():
    body = (
        "Property | Fixture Model | Other Model\n"
        "Architecture | Dense | MoE\n"
        "Input modalities | Text, image | Text\n"
        "Tool calling | Supported | Not supported\n"
        "Context window | 4200 | 7000\n"
    )
    assert read(body, 4200).outcome == "verified"


@pytest.mark.parametrize("new_names", [("Third Model", "Fourth Model"), ("3-unknown", "4-unknown")])
def test_an_unfamiliar_text_header_ends_the_previous_columns(new_names):
    body = ("Property | Fixture Model | Other Model\n"
            "Context window | 4200 | 7000\n"
            f"Dimension | {new_names[0]} | {new_names[1]}\n"
            "Context window | 9000 | 7000\n")
    result = read(body, 9000)
    assert result.outcome == "mismatch", result
    assert any(diff.field == "value" and diff.found == "4200" for diff in result.diffs)


def test_the_target_row_can_itself_have_unfamiliar_text_values():
    body = ("Property | Fixture Model | Other Model\n"
            "Specialization | Technical writing | General assistance\n")
    result = read(body, "Technical writing", field="fixture", label="Specialization")
    assert result.outcome == "verified", result


def test_known_quantities_before_the_target_keep_the_model_columns():
    body = ("Property | Fixture Model | Other Model\n"
            "Memory | 12 GB | 24 GB\nAccuracy | 83% | 81%\n"
            "Context window | 4200 | 7000\n")
    assert read(body, 4200).outcome == "verified"


@pytest.mark.parametrize("field,value", [("batch_input", 2), ("batch_output", 8)])
@pytest.mark.parametrize("batch_first", [False, True])
def test_batch_row_uses_its_explicit_batch_column(field, value, batch_first):
    columns = [("Standard Input Price", "$5"), ("Standard Output Price", "$9"),
               ("Batch Input Price (Cache Hit)", "$0.1"),
               ("Batch Input Price (Cache Miss)", "$2"), ("Batch Output Price", "$8")]
    if batch_first:
        columns = columns[2:] + columns[:2]
    body = "Model | " + " | ".join(name for name, _ in columns) + "\n"
    body += "Fixture Model (Batch) | " + " | ".join(amount for _, amount in columns) + "\n"
    body += "Prices are per million tokens.\n"
    result = read(body, value, field=f"offering.price.{field}", label=field.replace("_", " "),
                  unit="usd_per_1m_tokens")
    assert result.outcome == "verified", result
    standard = 5 if field == "batch_input" else 9
    assert read(body, standard, field=f"offering.price.{field}",
                label=field.replace("_", " "), unit="usd_per_1m_tokens").outcome != "verified"


@pytest.mark.parametrize("mode", ["Standard", "Priority", "Flex"])
def test_batch_row_does_not_use_an_explicit_other_mode_column(mode):
    body = (f"Model | {mode} Input Price | Output Price\n"
            "Fixture Model (Batch) | $5 | $9\nPrices per million tokens.\n")
    result = read(body, 5, field="offering.price.batch_input", label="batch input",
                  unit="usd_per_1m_tokens")
    assert result.outcome != "verified", result


@pytest.mark.parametrize("word", ["Manual", "Annotation", "Team"])
def test_unrelated_effort_prose_does_not_disable_a_transposed_score(word):
    body = (f"{word} effort was substantial.\n"
            "| Fixture Model | Other Model\n"
            "8 needle average | 42% | 24%\n")
    result = read(body, .42, field="fixture", label="8 needle average", unit="fraction",
                  kind="evidence")
    assert result.outcome == "verified", result


@pytest.mark.parametrize("effort", ["max", "standard"])
def test_actual_effort_caption_still_requires_a_condition_reader(effort):
    body = (f"All Fixture Model scores use {effort} effort.\n"
            "| Fixture Model | Other Model\n"
            "8 needle average | 42% | 24%\n")
    result = read(body, .42, field="fixture", label="8 needle average", unit="fraction",
                  kind="evidence")
    assert result.outcome != "verified", result
