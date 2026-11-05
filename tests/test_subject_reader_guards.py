"""Subject identity at the complete verifier's architecture and reader boundaries."""

import json
from dataclasses import replace
from datetime import date

import pytest

from decision.model import Source, SourceRef, TargetRef, VerificationActor
from decision.sources import CopyStore
from decision.verify import Claim, LLMExtractor, StoredRegions, deterministic_extractors, verify

TODAY = date(2026, 11, 4)
COLLECTOR = VerificationActor(agent="collector", model_family="openai", method="read")


def _claim(field, value, *, names=("Alpha", "lab/Alpha"), label=None, conditions=None):
    return Claim(
        TargetRef(kind="fact", id=f"fixture#{field}"), "lab/alpha", names,
        field, value, COLLECTOR,
        (SourceRef(source_id="fixture", snapshot_ref="sha256:" + "a" * 64,
                   cited_regions=["page"]),),
        unit="parameters" if "parameters" in field else "percent",
        label=label, conditions=conditions or {},
    )


def _readme(tmp_path, text):
    store = CopyStore(tmp_path)
    source = Source(id="fixture", url="https://huggingface.co/lab/Alpha/raw/main/README.md",
                    kind="weights_repository", normaliser="text-default",
                    cited_regions=[{"id": "page", "locator": {"kind": "page"}}])
    ref = SourceRef(source_id="fixture",
                    snapshot_ref=store.put(text.encode(), source_url="https://fixture.example/"),
                    cited_regions=["page"])
    return StoredRegions(store, {"fixture": source}), (ref,)


@pytest.mark.parametrize("name", ["Alpha ultra", "alpha ultra", "Alpha Ultra"])
def test_parameter_heading_cannot_lend_its_count_to_a_sibling(tmp_path, name):
    regions, refs = _readme(tmp_path, f"# {name}\nActive parameters: 3B\nA model card.")
    claim = replace(_claim("model.parameters_active", 3_000_000_000), sources=refs)
    result = verify(claim, regions, deterministic_extractors(), today=TODAY)
    assert result.outcome != "verified", result


@pytest.mark.parametrize("name", ["Ultra Alpha", "ultra Alpha", "Alpha ultra",
                                   "Alpha (ultra)", "Alpha [ultra]", "Alpha+"])
def test_parameter_prose_cannot_lend_its_count_to_a_sibling(tmp_path, name):
    regions, refs = _readme(tmp_path, f"# Alpha\n{name} uses 3B active parameters.\nA model card.")
    claim = replace(_claim("model.parameters_active", 3_000_000_000), sources=refs)
    result = verify(claim, regions, deterministic_extractors(), today=TODAY)
    assert result.outcome != "verified", result


@pytest.mark.parametrize("name", ["ALPHA", "Alpha Global"])
def test_parameter_heading_accepts_normalized_identity_and_registered_alias(tmp_path, name):
    regions, refs = _readme(tmp_path, f"# {name}\nActive parameters: 3B\nA model card.")
    claim = replace(_claim("model.parameters_active", 3_000_000_000,
                           names=("Alpha", "lab/Alpha", "Alpha Global")), sources=refs)
    assert verify(claim, regions, deterministic_extractors(), today=TODAY).outcome == "verified"


class _Regions:
    def __init__(self, text):
        self.body = text

    def text(self, *args):
        return self.body


@pytest.mark.parametrize("name", ["Fixture Model Ultra", "Ultra Fixture Model", "Fixture Model ultra"])
@pytest.mark.parametrize("position", ["caption", "heading"])
def test_effort_for_a_sibling_does_not_qualify_this_models_score(name, position):
    caption = f"{name} uses max effort."
    table = "Model | Coding\nFixture Model | 71.2\n"
    text = caption + "\n" + table if position == "heading" else table + caption
    rows = [{"subject": "Fixture Model", "value": "71.2", "unit": "percent", "effort": "max",
             "quoted_sentence": "Fixture Model | 71.2",
             "condition_sentence": caption if position == "caption" else None}]
    reader = LLMExtractor(lambda prompt: json.dumps(rows), agent="fixture-reader",
                          model="fixture", model_family="mistral")
    claim = _claim("coding", 71.2, names=("Fixture Model",), label="Coding",
                   conditions={"effort": "max"})
    result = verify(claim, _Regions(text), [reader], today=TODAY)
    assert result.outcome != "verified", result


@pytest.mark.parametrize("published,expected", [("Alpha (max effort)", "verified"),
                                                  ("Alpha Ultra (max effort)", "skipped"),
                                                  ("Alpha+ (max effort)", "skipped"),
                                                  ("Alpha (thinking)", "skipped")])
def test_structured_rows_keep_effort_qualifiers_separate_from_model_identity(published, expected):
    text = json.dumps([{"model": published, "Accuracy": 71.2, "effort": "max"}])
    claim = _claim("accuracy", 71.2, names=("Alpha",), label="Accuracy", conditions={"effort": "max"})
    result = verify(claim, _Regions(text), deterministic_extractors(), today=TODAY)
    assert result.outcome == expected, result


@pytest.mark.parametrize("subject,names,published,expected", [
    ("Fixture Model+", ("Fixture Model+",), "Fixture Model", "skipped"),
    ("Fixture Model", ("Fixture Model", "Fixture Model Global"), "Fixture Model Global", "verified"),
])
def test_effort_caption_uses_registered_model_identity(subject, names, published, expected):
    caption = f"{published} uses max effort."
    quote = f"{subject} | 71.2"
    rows = [{"subject": subject, "value": "71.2", "unit": "percent", "effort": "max",
             "quoted_sentence": quote, "condition_sentence": caption}]
    reader = LLMExtractor(lambda prompt: json.dumps(rows), agent="fixture-reader",
                          model="fixture", model_family="mistral")
    claim = _claim("coding", 71.2, names=names, label="Coding", conditions={"effort": "max"})
    result = verify(claim, _Regions(f"Model | Coding\n{quote}\n{caption}"), [reader], today=TODAY)
    assert result.outcome == expected, result


@pytest.mark.parametrize("template", ["{name} (max effort)", "{name}: max effort",
                                      "{name} at max effort"])
@pytest.mark.parametrize("name,expected", [("Fixture Model Ultra", "skipped"),
                                            ("FIXTURE--Model", "verified")])
def test_a_named_effort_heading_cannot_be_treated_as_generic(template, name, expected):
    heading = template.format(name=name)
    rows = [{"subject": "Fixture Model", "value": "71.2", "unit": "percent", "effort": "max",
             "quoted_sentence": "Fixture Model | 71.2"}]
    reader = LLMExtractor(lambda prompt: json.dumps(rows), agent="fixture-reader",
                          model="fixture", model_family="mistral")
    claim = _claim("coding", 71.2, names=("Fixture Model",), label="Coding",
                   conditions={"effort": "max"})
    result = verify(claim, _Regions(heading + "\nModel | Coding\nFixture Model | 71.2"),
                    [reader], today=TODAY)
    assert result.outcome == expected, result
