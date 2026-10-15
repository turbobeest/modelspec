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
    if normaliser == "text-default" and field != "model.max_output_tokens":
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


def test_model_properties_never_reads_other_model_table_before_subject_title(tmp_path):
    text = (
        "# Other Model\n"
        "Input type | Maximum size | Output type | Maximum size\n"
        "Text | 1 token | Text | 999k tokens\n"
        "# Mistral Small 4\nSee the table above.\n"
    )
    result = read(tmp_path, text, field="model.max_output_tokens", value=999000)
    assert result.outcome == "mismatch"


def test_model_properties_never_reads_other_model_table_after_subject_title(tmp_path):
    text = (
        "# Mistral Small 4\n# Other Model\n"
        "Input type | Maximum size | Output type | Maximum size\n"
        "Text | 1 token | Text | 999k tokens\n"
    )
    result = read(tmp_path, text, field="model.max_output_tokens", value=999000)
    assert result.outcome == "mismatch"


def test_model_properties_refuses_html_normalized_other_model_heading(tmp_path):
    text = (
        "<main><h1>Mistral Small 4</h1><h2>Other Model</h2>"
        "<table><tr><th>Input type</th><th>Maximum size</th>"
        "<th>Output type</th><th>Maximum size</th></tr>"
        "<tr><td>Text</td><td>1 token</td><td>Text</td><td>999k tokens</td></tr>"
        "</table></main>"
    )
    assert read(tmp_path, text, field="model.max_output_tokens", value=999000,
                normaliser="html-default").outcome == "mismatch"


@pytest.mark.parametrize("text", [
    "# Mistral Small 4\n# Other Model\n" + PROPERTIES.split("2. Model properties\n")[1],
    "# Mistral Small 4\n2. Model properties\n# Other Model\n"
    + PROPERTIES.split("2. Model properties\n")[1],
    "# Mistral Small 4\n2. Model properties\n"
    "The properties of GPT-6 Sol are also described here.\n"
    + PROPERTIES.split("2. Model properties\n")[1],
    "# Mistral Small 4\n2. Model properties\nModel: Other Model\n"
    + PROPERTIES.split("2. Model properties\n")[1],
    "Mistral Small 4\n1. GPT-6 Sol\n2. Model properties\n"
    + PROPERTIES.split("2. Model properties\n")[1],
])
def test_model_properties_refuses_other_subjects_in_its_scope(tmp_path, text):
    assert read(tmp_path, text, field="model.max_output_tokens", value=256000).outcome \
        == "mismatch"


@pytest.mark.parametrize("title", [
    "Model: Mistral Small 4\n", "Model name | Mistral Small 4\n",
])
def test_model_properties_refuses_a_headingless_table(tmp_path, title):
    text = title + PROPERTIES.split("2. Model properties\n")[1]
    assert read(tmp_path, text, field="model.max_output_tokens", value=256000).outcome \
        == "mismatch"


def test_model_properties_accepts_the_subjects_direct_title(tmp_path):
    text = "Mistral Small 4\n" + PROPERTIES.split("2. Model properties\n")[1]
    assert read(tmp_path, text, field="model.max_output_tokens", value=256000).outcome \
        == "verified"


def test_model_properties_refuses_multiple_candidate_tables_even_at_same_value(tmp_path):
    text = PROPERTIES + "\n" + PROPERTIES.split("2. Model properties\n")[1]
    assert read(tmp_path, text, field="model.max_output_tokens", value=256000).outcome \
        == "mismatch"


def test_model_properties_uses_own_heading_scope_with_single_table(tmp_path):
    text = "# Mistral Small 4\n## Model properties\n" \
        + PROPERTIES.split("2. Model properties\n")[1]
    assert read(tmp_path, text, field="model.max_output_tokens", value=256000).outcome \
        == "verified"


def test_model_properties_does_not_borrow_table_from_following_numbered_section(tmp_path):
    text = "Mistral Small 4\n2. Model properties\nNo output limit disclosed.\n" \
        "3. Other model properties\n" + PROPERTIES.split("2. Model properties\n")[1]
    assert read(tmp_path, text, field="model.max_output_tokens", value=256000).outcome \
        == "mismatch"


@pytest.mark.parametrize("own_first", [True, False])
def test_model_properties_reads_only_its_subject_section_in_two_subject_document(
    tmp_path, own_first,
):
    own = "# Mistral Small 4\n## Model properties\n" \
        + PROPERTIES.split("2. Model properties\n")[1]
    other = (
        "# Other Model\n## Model properties\n"
        "Input type | Maximum size | Output type | Maximum size\n"
        "Text | 1 token | Text | 999k tokens\n"
    )
    text = own + other if own_first else other + own
    result = read(tmp_path, text, field="model.max_output_tokens", value=256000)
    assert result.outcome == "verified"
    assert result.verification.verifier.method == "model-properties-output-limit@1"
    assert read(tmp_path, text, field="model.max_output_tokens", value=999000).outcome \
        == "mismatch"


def test_model_properties_refuses_a_literal_headingless_table(tmp_path):
    text = PROPERTIES.split("2. Model properties\n")[1]
    assert read(tmp_path, text, field="model.max_output_tokens", value=256000).outcome \
        == "mismatch"


def test_model_properties_ignores_other_model_mentions_before_its_numbered_section(tmp_path):
    text = (
        "Mistral Small 4\n1. General information\nGPT-6 Sol\n"
        "2. Model properties\n" + PROPERTIES.split("2. Model properties\n")[1]
    )
    assert read(tmp_path, text, field="model.max_output_tokens", value=256000).outcome \
        == "verified"


@pytest.mark.parametrize("row", [
    "Other Model | 1 token | Text | 999k tokens",
    "Text | Other Model | Text | 999k tokens",
    "Text | 1 token | Other Model | 999k tokens",
    "Image | 1 token | Image | Other Model",
])
def test_model_properties_refuses_unknown_model_names_in_every_table_column(tmp_path, row):
    text = "Mistral Small 4\n2. Model properties\n" \
        "Input type | Maximum size | Output type | Maximum size\n" \
        "Text | 1 token | Text | 999k tokens\n" + row + "\n"
    assert read(tmp_path, text, field="model.max_output_tokens", value=999000).outcome \
        == "mismatch"


def test_model_properties_refuses_unknown_plain_heading_after_its_table(tmp_path):
    text = PROPERTIES + "Other Model\n"
    assert read(tmp_path, text, field="model.max_output_tokens", value=256000).outcome \
        == "mismatch"


@pytest.mark.parametrize("prelude", [
    "Model architecture | Other Model",
    "Range of parameters | Other Model",
    "Model architecture | Mixture of Experts, Other Model",
    "Model architecture | Mixture of Experts (Other Model)",
    "Range of parameters | ☐100B - 500B Other Model",
    "Range of parameters | ☐100B - 500B; Other Model",
])
def test_model_properties_refuses_foreign_names_in_metadata_values(tmp_path, prelude):
    text = "Mistral Small 4\n2. Model properties\n" + prelude + "\n" \
        "Input type | Maximum size | Output type | Maximum size\n" \
        "Text | 1 token | Text | 999k tokens\n"
    assert read(tmp_path, text, field="model.max_output_tokens", value=999000).outcome \
        == "mismatch"


def test_model_properties_accepts_the_documented_mistral_metadata_prelude(tmp_path):
    text = PROPERTIES.replace(
        "2. Model properties\n",
        "2. Model properties\nModel architecture | Mixture of Experts\n"
        "Range of parameters | ☐100B - 500B\nModalities\n",
    )
    assert read(tmp_path, text, field="model.max_output_tokens", value=256000).outcome \
        == "verified"


@pytest.mark.parametrize("heading", ["Leanstral", "UnknownSiblingName"])
def test_model_properties_unknown_numbered_heading_breaks_subject_ownership(tmp_path, heading):
    text = "Mistral Small 4\n1. " + heading + "\n2. Model properties\n" \
        "Input type | Maximum size | Output type | Maximum size\n" \
        "Text | 1 token | Text | 999k tokens\n"
    assert read(tmp_path, text, field="model.max_output_tokens", value=999000).outcome \
        == "mismatch"

