"""Model documentation keeps page metadata and explicit values with their owner."""
from datetime import date

import pytest

from decision import verify
from decision.model import SourceRef, TargetRef, VerificationActor


class Page:
    def __init__(self, text, url=None):
        self.text_value, self.url = text, url

    def text(self, *args):
        return self.text_value

    def source_url(self, source_id):
        return self.url


def read(text, field="model.weights_openness", value="open_weights", *, url=None,
         names=("Fixture Model",), subject="fixture/model"):
    claim = verify.Claim(
        target=TargetRef(kind="fact", id=f"fixture#{field}"), subject=subject,
        names=names, field=field, label=field.removeprefix("model.").replace("_", " "),
        value=value,
        collector=VerificationActor(agent="collector", model_family="human", method="manual@1"),
        sources=(SourceRef(source_id="page", snapshot_ref="sha256:" + "a" * 64,
                           cited_regions=["page"]),),
    )
    return verify.verify(claim, Page(text, url), verify.deterministic_extractors(),
                         today=date(2026, 11, 5))


RICH = ("license: mit\nextra_gated_description: >-\n"
        "See the privacy statement for details.\nThe statement is linked here.\n"
        "tags:\n- code\n- text\n")


def test_folded_metadata_belongs_to_an_exact_model_card_title():
    assert read(RICH + "# Model Card for Fixture Model\nModel documentation.").outcome == "verified"


@pytest.mark.parametrize("title", ["# Fixture Model Ultra", "Model: Fixture Model Ultra"])
def test_folded_metadata_does_not_cross_a_foreign_title(title):
    text = RICH + title + "\n# Fixture Model\nModel documentation."
    assert read(text).outcome != "verified"


def test_model_absence_does_not_override_a_later_owned_value():
    text = ("# Fixture Model\nlicense: mit\nlibrary_name: transformers\n"
            "# Fixture Model\nContext window: 4200\n")
    assert read(text, "model.context_window", None).outcome != "verified"


def test_repository_metadata_and_foreign_body_have_separate_owners():
    text = "license: mit\n# Fixture Model Ultra\nContext window: 4200\nModel documentation."
    url = "https://huggingface.co/lab/Fixture-Model/raw/main/README.md"
    assert read(text, url=url).outcome == "verified"
    assert read(text, "model.context_window", 4200, url=url).outcome != "verified"


@pytest.mark.parametrize("file", ["config.json", "metadata.json"])
def test_generic_model_readers_do_not_bind_non_readme_urls(file):
    text = "license: mit\nlibrary_name: transformers\nModel documentation."
    url = f"https://huggingface.co/lab/Fixture-Model/raw/main/{file}"
    assert read(text, url=url).outcome != "verified"


def test_model_named_feature_sentence_binds_its_exact_subject():
    text = ("Other Model: Supports tool calling.\n"
            "Fixture Model: Supports toggling through the reasoning_effort parameter.\n"
            "More model documentation.")
    assert read(text, "feature.effort_controls", True).outcome == "verified"


def test_named_feature_sentence_does_not_borrow_an_extended_model_name():
    text = ("Fixture Model: Supports tool calling.\n"
            "Fixture Model Ultra: Supports toggling through the reasoning_effort parameter.\n"
            "More model documentation.")
    assert read(text, "feature.effort_controls", True).outcome != "verified"


def test_bulleted_model_metadata_keeps_values_with_its_named_title():
    text = ("# Fixture Model\n- Names: `fixture-model`, `fixture-model-latest`\n"
            "- Release date: 2026-10-01\n- Input: text, image\n")
    assert read(text, "model.release_date", "2026-10-01").outcome == "verified"


@pytest.mark.parametrize("label", ["Batch price", "Input/M Tokens", "Cached Input/M Tokens", "Chat Completions", "Built-in Tools"])
def test_generic_price_and_feature_labels_do_not_rename_the_model(label):
    text = (f"Fixture Model\n{label}\nFunction Calling\nSupported\n"
            "Structured Outputs\nSupported\n")
    assert read(text, "feature.tool_calling", True).outcome == "verified"


def test_code_example_headings_do_not_rename_a_repository_page():
    text = ("license: mit\nlibrary_name: transformers\n"
            "## Model details\nContext window: 4200\n"
            "```python\n# Load model\nmodel = load_model()\n```\n")
    url = "https://huggingface.co/lab/Fixture-Model/raw/main/README.md"
    assert read(text, "model.context_window", 4200, url=url).outcome == "verified"


def test_code_example_feature_mentions_are_not_model_facts():
    text = "# Fixture Model\n```python\n# Supports reasoning_effort\ncall(reasoning_effort='max')\n```\nModel details."
    assert read(text, "feature.effort_controls", True).outcome != "verified"


def test_visible_html_model_features_are_read_without_embedded_script_data():
    text = ('<!doctype html><html><body><main><h1>Fixture Model</h1>'
            '<h2>Capabilities</h2><p>Batch API</p><p>Supported</p>'
            '<script>{"Fixture Model Ultra": "reasoning effort"}</script></main></body></html>')
    assert read(text, "feature.batch", True).outcome == "verified"
    assert read(text, "feature.effort_controls", True).outcome != "verified"


def test_navigation_cannot_supply_a_feature_to_the_model():
    text = ('<!doctype html><html><body><nav>Batch API</nav><main>'
            '<h1>Fixture Model</h1><p>Model details.</p><p>Text generation.</p>'
            '</main></body></html>')
    assert read(text, "feature.batch", True).outcome != "verified"


@pytest.mark.parametrize("paragraph", [
    "- **Smarter tool calling**: Through training, the model's performance in tool usage is improved.",
    "**Post-training.** Training follows several steps. The model supports reasoning effort.",
])
def test_owned_feature_paragraphs_read_their_local_subject(paragraph):
    field = "feature.tool_calling" if "tool" in paragraph else "feature.effort_controls"
    text = "# Fixture Model\n## Introduction\n" + paragraph
    assert read(text, field, True).outcome == "verified"


def test_later_sibling_sentence_does_not_describe_the_page_model():
    text = "# Fixture Model\nTraining follows several steps. Fixture Model Ultra supports reasoning effort.\nModel details."
    assert read(text, "feature.effort_controls", True).outcome != "verified"


@pytest.fixture
def model_catalogue(tmp_path, monkeypatch):
    models = tmp_path / "models" / "fixture"
    models.mkdir(parents=True)
    (models / "model.md").write_text(
        "---\nmodel_id: fixture/fixture-model\ndisplay_name: Fixture Model\n"
        "sources:\n  huggingface_url: https://huggingface.co/lab/Fixture-Repository\n---\n")
    monkeypatch.setattr(verify, "REPO_ROOT", tmp_path)
    cached = (verify._catalogue_ids, verify._catalogue_model_aliases,
              verify._catalogue_display_names, verify._catalogue_model_index,
              verify._catalogue_readme_repositories)
    for function in cached:
        function.cache_clear()
    yield
    for function in cached:
        function.cache_clear()


def test_internal_catalogue_id_is_not_an_asserted_repository_namespace(model_catalogue):
    text = "license: mit\nlibrary_name: transformers\nModel documentation."
    url = "https://huggingface.co/lab/fixture-model/raw/main/README.md"
    assert read(text, url=url, names=("Fixture Model", "fixture/fixture-model"),
                subject="fixture/fixture-model").outcome == "verified"


def test_explicit_repository_alias_keeps_its_owner_constraint(model_catalogue):
    text = "license: mit\nlibrary_name: transformers\nModel documentation."
    url = "https://huggingface.co/wrong/fixture-model/raw/main/README.md"
    assert read(text, url=url, names=("Fixture Model", "fixture/fixture-model", "lab/fixture-model"),
                subject="fixture/fixture-model").outcome != "verified"


def test_feature_support_noun_is_not_parsed_as_a_foreign_subject():
    text = ("# Fixture Model\n## Introduction\n"
            "* **Coding capabilities** - Achieves improvements with native function-calling support.")
    assert read(text, "feature.tool_calling", True).outcome == "verified"


def test_generic_sibling_section_resumes_its_exact_parent_model():
    text = ("# Fixture Model\n## Fixture Model Ultra\nContext window: 9000\n"
            "## Prompt Encoding\nThis model supports tool calling.\n")
    assert read(text, "feature.tool_calling", True).outcome == "verified"
    assert read(text, "model.context_window", 9000).outcome != "verified"


def test_generic_child_section_stays_with_its_foreign_parent():
    text = ("# Fixture Model\n## Fixture Model Ultra\n"
            "### Prompt Encoding\nThis model supports tool calling.\n")
    assert read(text, "feature.tool_calling", True).outcome != "verified"


@pytest.mark.parametrize("subject,names", [
    ("fixture/fixture-model", ("Fixture Model", "fixture/fixture-model")),
    ("fixture/model-latest", ("Latest Model", "Fixture Model")),
])
def test_registered_repository_url_supplies_the_exact_source_identity(model_catalogue, subject, names):
    text = "license: mit\nlibrary_name: transformers\n# Fixture Repository\nModel documentation."
    url = "https://huggingface.co/lab/Fixture-Repository/raw/main/README.md"
    assert read(text, url=url, subject=subject, names=names).outcome == "verified"


@pytest.mark.parametrize("repository", ["lab/Fixture-Repository-Ultra", "wrong/Fixture-Repository"])
def test_registered_repository_does_not_bind_a_sibling_or_wrong_owner(model_catalogue, repository):
    text = "license: mit\nlibrary_name: transformers\nModel documentation."
    url = f"https://huggingface.co/{repository}/raw/main/README.md"
    assert read(text, url=url, subject="fixture/fixture-model").outcome != "verified"


@pytest.mark.parametrize("name", ["Fixture:Model", "Fixture Model: Special"])
def test_complete_registered_heading_identity_precedes_subtitle_grammar(name):
    text = f"# {name}\nContext window: 4200\nModel documentation."
    assert read(text, "model.context_window", 4200, names=(name,)).outcome == "verified"


def test_colon_inside_a_model_identifier_is_not_a_subtitle():
    text = "# Fixture Model:Ultra\nContext window: 4200\nModel documentation."
    assert read(text, "model.context_window", 4200).outcome != "verified"


def test_canonical_repository_is_not_replaced_by_another_cards_alias(model_catalogue, tmp_path):
    (tmp_path / "models/fixture/other.md").write_text(
        "---\nmodel_id: fixture/other-model\ndisplay_name: Other Model\n"
        "sources:\n  huggingface_url: https://huggingface.co/lab/Other-Repository\n---\n")
    text = "license: mit\nlibrary_name: transformers\nModel documentation."
    url = "https://huggingface.co/lab/Other-Repository/raw/main/README.md"
    assert read(text, url=url, subject="fixture/fixture-model",
                names=("Fixture Model", "Other Model")).outcome != "verified"


@pytest.mark.parametrize("verb", ["includes", "offers"])
def test_an_exact_named_declaration_owns_its_following_feature_list(verb):
    text = ("# Fixture Series\n"
            f"Fixture Model {verb} the following capabilities:\n"
            "- Reasoning effort is configurable per request.\n")
    assert read(text, "feature.effort_controls", True).outcome == "verified"


def test_a_sibling_named_declaration_closes_the_previous_feature_list():
    text = ("# Fixture Model\nFixture Model includes the following capabilities:\n"
            "- Function calling is supported.\n"
            "Fixture Model Ultra offers the following capabilities:\n"
            "- Reasoning effort is configurable per request.\n")
    assert read(text, "feature.effort_controls", True).outcome != "verified"
