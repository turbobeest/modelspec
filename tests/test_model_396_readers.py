"""MODEL-396 readers use retained primary sources and preserve exact sets."""

from __future__ import annotations

from datetime import date

import pytest

from decision.model import CitedRegion, Source, SourceRef, TargetRef, VerificationActor
from decision.sources import CopyStore
from decision.verify import Claim, StoredRegions, deterministic_extractors, verify

TODAY = date(2026, 10, 14)
MODEL = "mistral/mistral-small-2603"
URL = "https://docs.mistral.ai/models/mistral-small-4-0-26-03.md"
COLLECTOR = VerificationActor(agent="codex", model_family="openai", method="collect")


def read(tmp_path, text, *, field="model.output_modalities", value=None,
         subject=MODEL, names=("Mistral Small 4",), url=URL, kind="lab_documentation",
         normaliser="text-default", label=None):
    if normaliser == "text-default":
        text += "\nFeatures\n"
    store = CopyStore(tmp_path / "copies")
    ref = store.put(text.encode())
    source = Source(
        id="primary", url=url, kind=kind, normaliser=normaliser,
        cited_regions=[CitedRegion(id="page", locator={"kind": "page"})],
    )
    claim = Claim(
        target=TargetRef(kind="fact", id=f"{subject}#{field}"), subject=subject,
        names=names, field=field, value=["text"] if value is None else value,
        unit="tokens" if field == "model.max_output_tokens" else None, label=label,
        collector=COLLECTOR,
        sources=(SourceRef(source_id="primary", snapshot_ref=ref, cited_regions=["page"]),),
    )
    return verify(claim, StoredRegions(store, {source.id: source}),
                  deterministic_extractors(), today=TODAY)


@pytest.mark.parametrize("text,normaliser", [
    ("# Mistral Small 4\n- Input: text, image\n- Output: reasoning, text\n", "text-default"),
    ("Mistral Small 4\nOutput: TEXT, Reasoning\n", "text-default"),
    ("Mistral Small 4\nOutput | Reasoning, Text\n", "text-default"),
    ("# Mistral Small 4\n| Output | reasoning, text |\n", "text-default"),
    ("<main><h1>Mistral Small 4</h1><p>Output</p>"
     "<p>Reasoning, Text</p></main>", "html-default"),
    ("<main><h1>Mistral Small 4</h1><p>Output</p>"
     "<p>Reasoning</p><p>Text</p><h2>Features</h2></main>", "html-default"),
    ("<main><h1>Mistral Small 4</h1><table><tr><td>Output</td>"
     "<td>Reasoning, Text</td></tr></table></main>", "html-default"),
])
def test_mistral_reasoning_output_label_verifies_exact_text_set(tmp_path, text, normaliser):
    result = read(tmp_path, text, normaliser=normaliser)
    assert result.outcome == "verified"
    assert result.verification.verifier.method == "mistral-output-labels@1"


@pytest.mark.parametrize("labels", [
    "reasoning, text, image", "reasoning, text, smell", "reasoning, text, reasoning_trace",
    "reasoning, text, reasoning output", "reasoning", "reasoning text", "reasonings, text",
    "reasoning, text, not reasoning",
])
def test_mistral_rule_preserves_every_label_except_exact_reasoning(tmp_path, labels):
    result = read(tmp_path, f"Mistral Small 4\nOutput: {labels}\n")
    assert result.outcome == "mismatch"


def test_mistral_rule_keeps_real_output_labels(tmp_path):
    text = "Mistral Small 4\nOutput: reasoning, text, image\n"
    result = read(tmp_path, text, value=["text", "image"])
    assert result.outcome == "verified"
    assert result.verification.verifier.method == "mistral-output-labels@1"


@pytest.mark.parametrize("text", [
    "Mistral Small 4\nOutput: text\nOutput: reasoning, text, image\n",
    "Mistral Small 4\nOutput | text\nOutput | reasoning, text, image\n",
    "Mistral Small 4\nOutput\nText\nFeatures\nOutput\nText, image\n",
])
def test_mistral_rule_refuses_conflicting_output_blocks_even_with_claim_label(tmp_path, text):
    assert read(tmp_path, text, label="Output").outcome == "mismatch"


@pytest.mark.parametrize("url", [
    "https://docs.mistral.ai.evil.test/models/mistral-small-4-0-26-03.md",
    "https://mistral.ai/models/mistral-small-4-0-26-03.md",
    "https://docs.mistral.ai/capabilities/mistral-small-4-0-26-03.md",
    "https://docs.mistral.ai/models-other/mistral-small-4-0-26-03.md",
    "https://docs.mistral.ai:8443/models/mistral-small-4-0-26-03.md",
    "http://docs.mistral.ai/models/mistral-small-4-0-26-03.md",
    "https://docs.mistral.ai/models/../capabilities/mistral-small-4-0-26-03.md",
])
def test_mistral_rule_requires_exact_primary_host_and_model_path(tmp_path, url):
    result = read(tmp_path, "Mistral Small 4\nOutput: reasoning, text\n", url=url)
    assert result.outcome == "mismatch"


@pytest.mark.parametrize("subject,names,text", [
    ("other/model", ("Other Model",), "Other Model\nOutput: reasoning, text\n"),
    (MODEL, ("Mistral Small 4",), "Mistral Small 4 Pro\nOutput: reasoning, text\n"),
    (MODEL, ("Mistral Small 4",), "Mistral Medium 4\nOutput: reasoning, text\n"),
    (MODEL, ("Mistral Small 4",), "Mistral-Small-4-Pro\nOutput: reasoning, text\n"),
])
def test_mistral_rule_requires_exact_model_identity(tmp_path, subject, names, text):
    assert read(tmp_path, text, subject=subject, names=names).outcome == "mismatch"


def test_mistral_output_rule_does_not_drop_input_reasoning(tmp_path):
    result = read(tmp_path, "Mistral Small 4\nInput: reasoning, text\n",
                  field="model.input_modalities", label="Input")
    assert result.outcome == "mismatch"


def test_mistral_rule_does_not_rewrite_generic_output_set(tmp_path):
    result = read(tmp_path, "Mistral Small 4\nmodel.output_modalities: reasoning, text\n")
    assert result.outcome == "mismatch"


def test_mistral_rule_requires_primary_documentation_kind(tmp_path):
    result = read(tmp_path, "Mistral Small 4\nOutput: reasoning, text\n",
                  kind="lab_announcement")
    assert result.outcome == "mismatch"


PROPERTIES = (
    "Mistral Small 4\n2. Model properties\n"
    "Input type | Maximum size | Output type | Maximum size\n"
    "Text | 128k tokens | Text | 256k tokens\n"
    "Image | 128k tokens | Image | N/A\n"
    "Audio | N/A | Audio | N/A\n"
)


def test_model_properties_reads_output_maximum_not_input_maximum(tmp_path):
    result = read(tmp_path, PROPERTIES, field="model.max_output_tokens", value=256000,
                  url="https://legal.mistral.ai/technical-documentation.pdf")
    assert result.outcome == "verified"
    assert result.verification.verifier.method == "model-properties-output-limit@1"
    assert read(tmp_path, PROPERTIES, field="model.max_output_tokens", value=128000).outcome \
        == "mismatch"


@pytest.mark.parametrize("text", [
    PROPERTIES.replace("Text | 128k tokens | Text | 256k tokens",
                       "Text | 256k tokens | Text | N/A"),
    PROPERTIES.replace(" | Text | 256k tokens", " | Image | 256k tokens"),
    PROPERTIES.replace(" | Text | 256k tokens", " | Text | 256k"),
    PROPERTIES.replace(" | Text | 256k tokens", " | Text | 256k bytes"),
    PROPERTIES.replace(" | Text | 256k tokens", " | Text | 256k tokens plus image"),
    PROPERTIES.replace(" | Text | 256k tokens", " | Text | -256k tokens"),
    PROPERTIES.replace(" | Text | 256k tokens", " | Text | 0 tokens"),
    PROPERTIES.replace("Output type | Maximum size", "Output type | Maximum context size"),
    PROPERTIES.replace("Text | 128k tokens | Text | 256k tokens",
                       "Text | 128k tokens | 256k tokens"),
    PROPERTIES.replace("Mistral Small 4", "Mistral Small 4 Pro"),
    PROPERTIES + "Text | 128k tokens | Text | 128k tokens\n",
    PROPERTIES + PROPERTIES.replace("256k tokens", "512k tokens"),
])
def test_model_properties_refuses_missing_conflicting_or_malformed_output(tmp_path, text):
    assert read(tmp_path, text, field="model.max_output_tokens", value=256000).outcome \
        == "mismatch"


def test_model_properties_requires_lab_documentation(tmp_path):
    assert read(tmp_path, PROPERTIES, field="model.max_output_tokens", value=256000,
                kind="lab_announcement").outcome == "mismatch"

