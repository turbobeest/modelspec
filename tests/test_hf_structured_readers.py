"""MODEL-558: deterministic readers for facts a Hugging Face repository states in structured form.

Every fixture is synthetic: the repository ``acme/Widget-7B`` and its pages are made up here.
"""

import json
from datetime import date

import pytest
from decision.model import SourceRef, TargetRef, VerificationActor
from decision.verify import (
    Claim,
    HFConfigContextExtractor,
    HFReadmeSpecExtractor,
    HFRepoMetadataExtractor,
    _readers_for,
    compare,
    deterministic_extractors,
    hf_config_context_window,
    hf_readme_context_cells,
    hf_task_modalities,
    hf_weights_openness,
    verify,
)

REPO = "acme/Widget-7B"
README = f"https://huggingface.co/{REPO}/resolve/main/README.md"
CONFIG = f"https://huggingface.co/{REPO}/resolve/0123abc/config.json"
API = f"https://huggingface.co/api/models/{REPO}"
UNITS = {"model.context_window": "tokens"}


def claim(field, value, url=README):
    return Claim(
        target=TargetRef(kind="fact", id=f"acme/widget-7b#{field}"), subject="acme/widget-7b",
        names=("Widget 7B", "widget-7b"), field=field, value=value,
        collector=VerificationActor(agent="test-collector", model_family="anthropic",
                                    method="read"),
        sources=(SourceRef(source_id="s", snapshot_ref="sha256:" + "0" * 64,
                           cited_regions=["page"]),),
        unit=UNITS.get(field), label=field, state="known")


#: A README of the same repository that states no context window.
SILENT_README = ("# Widget 7B\n\nA text model.\n", README)


def read(extractor, field, value, text, url, bindings=(SILENT_README,)):
    c = claim(field, value, url)
    if isinstance(extractor, HFConfigContextExtractor):
        readings = extractor.extract(c, text, page_url=url, bindings=list(bindings))
    else:
        readings = extractor.extract(c, text, page_url=url)
    return readings, (compare(c, readings) if readings else None)


# --- config.json: the context window --------------------------------------------------------------


def config(**text):
    return json.dumps({"architectures": ["WidgetForCausalLM"], "model_type": "widget",
                       "num_attention_heads": 32, **text})


def test_config_window_without_scaling_is_read_and_agrees():
    readings, diffs = read(HFConfigContextExtractor(), "model.context_window", 131072,
                           config(max_position_embeddings=131072), CONFIG)
    assert [r.value for r in readings] == ["131072"] and diffs == []


def test_config_window_that_differs_is_a_mismatch_not_an_abstention():
    _, diffs = read(HFConfigContextExtractor(), "model.context_window", 128000,
                    config(max_position_embeddings=131072), CONFIG)
    assert diffs and diffs[0].field == "value"


def test_config_yarn_window_is_read_only_when_the_scaling_reaches_it():
    reached = {"type": "yarn", "factor": 32, "original_max_position_embeddings": 4096}
    assert hf_config_context_window(json.loads(config(
        max_position_embeddings=131072, rope_scaling=reached))) == 131072
    short = {"type": "yarn", "factor": 4, "original_max_position_embeddings": 32768}
    assert hf_config_context_window(json.loads(config(
        max_position_embeddings=32768, rope_scaling=short))) is None


@pytest.mark.parametrize("cfg", [
    {"max_position_embeddings": 131072, "rope_scaling": {"rope_type": "linear", "factor": 8.0}},
    {"max_position_embeddings": 131072, "rope_scaling": {"type": "dynamic", "factor": 2.0}},
    {"max_position_embeddings": 0},
    {"max_position_embeddings": True},
    {"max_position_embeddings": "131072"},
    {"text_config": {"max_position_embeddings": 8192, "model_type": "a"},
     "decoder": {"max_position_embeddings": 4096, "model_type": "b"}},
    # A nested encoder or decoder subconfig states a window beside the top-level one.
    {"max_position_embeddings": 8192, "encoder": {"max_position_embeddings": 512}},
    {"max_position_embeddings": 8192, "decoder": {"max_position_embeddings": 8192}},
    # Both levels state one.
    {"max_position_embeddings": 8192, "text_config": {"max_position_embeddings": 8192}},
    # RoPE scaling at the parent level over a text_config window.
    {"rope_scaling": {"type": "linear", "factor": 4.0},
     "text_config": {"max_position_embeddings": 8192}},
    {"rope_scaling": None, "text_config": {"max_position_embeddings": 8192}},
    # A rope_type and a type that name different kinds.
    {"max_position_embeddings": 131072, "rope_scaling": {
        "rope_type": "yarn", "type": "linear", "factor": 32,
        "original_max_position_embeddings": 4096}},
    {"max_position_embeddings": 131072, "rope_parameters": {"rope_type": "default"}},
])
def test_config_window_abstains_when_in_doubt(cfg):
    assert hf_config_context_window(json.loads(config(**cfg))) is None


def test_config_window_abstains_for_an_encoder_or_embedder():
    for arch in (["WidgetModel"], ["WidgetForSequenceClassification"], [], None):
        text = json.dumps({"architectures": arch, "model_type": "widget",
                           "num_attention_heads": 8, "max_position_embeddings": 32768})
        assert hf_config_context_window(json.loads(text)) is None


def test_config_window_reads_the_text_tower_only():
    text = json.loads(json.dumps({
        "architectures": ["WidgetForConditionalGeneration"], "model_type": "widget_vl",
        "text_config": {"max_position_embeddings": 262144, "num_attention_heads": 8},
        "vision_config": {"max_position_embeddings": 1024}}))
    assert hf_config_context_window(text) == 262144


@pytest.mark.parametrize("page", [
    "| **Context Length** | 256K |\n|---|---|\n",          # stated, even abbreviated
    "| **Context Length** | 131072 |\n|---|---|\n",
    "- Context window: 128k\n",
    "Trained with a context length of 131,072 tokens.\n",
    "It supports a 1M-token context window.\n",
])
def test_config_window_never_overrides_a_window_the_lab_states(page):
    # Jamie, MODEL-558: the facet stores the lab's stated value; a config sets it only when the
    # lab states none.
    readings, _ = read(HFConfigContextExtractor(), "model.context_window", 131072,
                       config(max_position_embeddings=131072), CONFIG, bindings=[(page, README)])
    assert readings == []


def test_config_window_needs_the_repositorys_readme_read_and_silent():
    text = config(max_position_embeddings=131072)
    assert read(HFConfigContextExtractor(), "model.context_window", 131072, text, CONFIG,
                bindings=[])[0] == []
    other = ("# Widget 7B\n", "https://huggingface.co/acme/Other-7B/resolve/main/README.md")
    assert read(HFConfigContextExtractor(), "model.context_window", 131072, text, CONFIG,
                bindings=[other])[0] == []
    # A silent README of the repository, with a lab page elsewhere that states a window.
    guide = ("The context window is 128k tokens.", "https://docs.acme.test/widget")
    assert read(HFConfigContextExtractor(), "model.context_window", 131072, text, CONFIG,
                bindings=[SILENT_README, guide])[0] == []


def test_config_reader_is_bound_to_the_subjects_own_config():
    other = "https://huggingface.co/acme/Other-7B/resolve/0123abc/config.json"
    readings, _ = read(HFConfigContextExtractor(), "model.context_window", 131072,
                       config(max_position_embeddings=131072), other)
    assert readings == []
    readings, _ = read(HFConfigContextExtractor(), "model.context_window", 131072,
                       config(max_position_embeddings=131072), README)
    assert readings == []


# --- README spec tables: the context window -------------------------------------------------------

TWO_COLUMN = """# Widget 7B

| | |
|---|---|
| **Embedding dimension** | 4096 |
| **Context length** | 32,768 tokens |
"""
PER_MODEL = """| Model | Parameters | Context Length |
|---|---|---|
| [widget-1b](https://huggingface.co/acme/widget-1b) | 1B | 8,192 |
| [widget-7b](https://huggingface.co/acme/widget-7b) | 7B | 32,768 |
"""
HTML_ROWS = """<table><tr>
<td align="center"><strong>Context Length</strong></td>
<td align="center">1048576</td>
</tr></table>"""


@pytest.mark.parametrize("text,value", [
    (TWO_COLUMN, 32768), (PER_MODEL, 32768), (HTML_ROWS, 1048576),
    ("- Context length: 65536\n", 65536),
])
def test_readme_window_layouts_are_read(text, value):
    readings, diffs = read(HFReadmeSpecExtractor(), "model.context_window", value, text, README)
    assert [r.value for r in readings] == [str(value)] and diffs == []


@pytest.mark.parametrize("text", [
    "| **Context Length** | 256K |\n|---|---|\n",
    "- Max Input Tokens: 32k\n",
    "| **Context Length** | 1M |\n|---|---|\n",
    "| **Context Length** | up to 128K |\n|---|---|\n",
    TWO_COLUMN + "\n- Context length: 8192\n",           # two different numbers
    "Long context: up to 8k context length.\n",           # prose is not a table
    "max_length = 32768\n",                               # code is not a table
    # Input or generation limits are not the context window (MODEL-558 review).
    "| **Max sequence length** | 32,768 tokens |\n|---|---|\n",
    "- Max Input Tokens: 32768\n",
    "| Model | Max Tokens |\n|---|---|\n| widget-7b | 32,768 |\n",
    "| **Max tokens** | 32768 |\n|---|---|\n",
])
def test_readme_window_abstains_on_abbreviations_conflicts_and_prose(text):
    readings, _ = read(HFReadmeSpecExtractor(), "model.context_window", 32768, text, README)
    assert readings == []


def test_readme_per_model_table_reads_the_subjects_row_only():
    assert hf_readme_context_cells(PER_MODEL, ("Widget 1B",)) == ["8,192"]
    readings, _ = read(HFReadmeSpecExtractor(), "model.context_window", 8192,
                       PER_MODEL.replace("widget-7b", "widget-9b"), README)
    assert readings == []


def test_readme_reader_is_bound_to_the_subjects_readme():
    other = "https://huggingface.co/acme/Other-7B/resolve/main/README.md"
    assert read(HFReadmeSpecExtractor(), "model.context_window", 32768, TWO_COLUMN, other)[0] == []
    assert read(HFReadmeSpecExtractor(), "model.context_window", 32768, TWO_COLUMN, API)[0] == []


# --- declared task: modalities --------------------------------------------------------------------


def api(**data):
    return json.dumps({"id": REPO, "private": False, "tags": [], "config": {
        "architectures": ["WidgetModel"], "model_type": "widget"}, **data})


@pytest.mark.parametrize("task,field,value", [
    ("sentence-similarity", "model.input_modalities", "text"),
    ("sentence-similarity", "model.output_modalities", "embedding"),
    ("feature-extraction", "model.output_modalities", "embedding"),
    ("text-generation", "model.input_modalities", "text"),
    ("text-generation", "model.output_modalities", "text"),
])
def test_declared_task_gives_the_modalities_it_leaves_in_no_doubt(task, field, value):
    assert hf_task_modalities(field, task, []) == value


@pytest.mark.parametrize("task,tags,model", [
    ("image-text-to-text", [], []),                  # names no full input set
    ("feature-extraction", ["vision", "clip"], []),
    ("feature-extraction", [], ["WidgetVisionModel"]),
    ("text-generation", ["multimodal"], []),
    ("text-generation", [], ["WidgetForConditionalGeneration"]),
    ("automatic-speech-recognition", [], []),
])
def test_text_input_abstains_when_anything_names_another_modality(task, tags, model):
    assert hf_task_modalities("model.input_modalities", task, tags, model) is None


@pytest.mark.parametrize("task,tags,model", [
    ("image-text-to-text", [], []),                  # the task itself is multimodal
    ("text-generation", ["vision"], []),
    ("text-generation", [], ["WidgetForConditionalGeneration"]),
    ("feature-extraction", ["multimodal"], []),
    ("sentence-similarity", [], ["WidgetVLModel"]),
])
def test_output_abstains_on_any_multimodal_hint(task, tags, model):
    assert hf_task_modalities("model.output_modalities", task, tags, model) is None


def test_modalities_from_the_api_json_and_the_readme_front_matter():
    readings, diffs = read(HFRepoMetadataExtractor(), "model.output_modalities", ["embedding"],
                           api(pipeline_tag="sentence-similarity"), API)
    assert [r.value for r in readings] == ["embedding"] and diffs == []
    front = "license: mit\npipeline_tag: feature-extraction\ntags:\n- mteb\n\n# Widget 7B\n"
    readings, diffs = read(HFRepoMetadataExtractor(), "model.input_modalities", ["text"],
                           front, README)
    assert [r.value for r in readings] == ["text"] and diffs == []


@pytest.mark.parametrize("filed", [["text", "image"], ["image"], [], ["text", "text"]])
def test_a_task_never_establishes_a_complete_set(filed):
    # A task tag proves one modality: a filed set that is not exactly it is no reading.
    readings, _ = read(HFRepoMetadataExtractor(), "model.input_modalities", filed,
                       api(pipeline_tag="text-generation"), API)
    assert readings == []


def test_metadata_of_another_repository_or_no_task_is_no_reading():
    assert read(HFRepoMetadataExtractor(), "model.output_modalities", ["text"],
                api(pipeline_tag="text-generation", id="acme/Other-7B"), API)[0] == []
    assert read(HFRepoMetadataExtractor(), "model.output_modalities", ["text"], api(), API)[0] == []
    assert read(HFRepoMetadataExtractor(), "model.output_modalities", ["text"],
                "# Widget 7B\nNo front matter.\n", README)[0] == []


# --- file list: weights openness ------------------------------------------------------------------


def files(*names, **data):
    return {"id": REPO, "private": False, "gated": False, "tags": [],
            "siblings": [{"rfilename": n} for n in names], **data}


def test_weight_files_read_open_and_no_weight_file_reads_closed():
    shard = "model-00001-of-00002.safetensors"
    assert hf_weights_openness(files("README.md", shard)) == "open_weights"
    assert hf_weights_openness(files("README.md", "widget.Q4_K_M.gguf")) == "open_weights"
    assert hf_weights_openness(files("pytorch_model.bin", "config.json")) == "open_weights"
    assert hf_weights_openness(files(".gitattributes", "README.md", "config.json",
                                     "handler.py")) == "closed_weights"


@pytest.mark.parametrize("data", [
    files(),                                                  # no file list
    files("README.md", "training_args.bin"),                  # a .bin that is not a checkpoint
    files("README.md", private=True),
    files("README.md", "handler.py", safetensors={"total": 0}),
    {"id": REPO, "private": False, "gated": False},
    # Gated, private, adapter-only and metadata-only repositories (MODEL-558 review).
    files("model.safetensors", gated="auto"),
    files("model.safetensors", gated="manual"),
    files("handler.py", gated=True),
    {k: v for k, v in files("model.safetensors").items() if k != "gated"},
    files("model.safetensors", private=True),
    files("adapter_config.json", "adapter_model.safetensors"),
    files("model.safetensors", tags=["peft"]),
    files("model.safetensors", tags=["lora"]),
    files(".gitattributes", "README.md", "config.json", "tokenizer_config.json"),
    files("README.md", "LICENSE", "assets/diagram.png"),
])
def test_weights_openness_abstains_when_in_doubt(data):
    assert hf_weights_openness(data) is None


def test_weights_openness_reads_only_the_api_json_of_the_subjects_repository():
    text = json.dumps(files("README.md", "config.json", "handler.py"))
    readings, diffs = read(HFRepoMetadataExtractor(), "model.weights_openness", "closed_weights",
                           text, API)
    assert [r.value for r in readings] == ["closed_weights"] and diffs == []
    other = "https://huggingface.co/api/models/acme/Other-7B"
    assert read(HFRepoMetadataExtractor(), "model.weights_openness", "closed_weights",
                text, other)[0] == []
    assert not HFRepoMetadataExtractor().bound_to(claim("model.weights_openness", "x"), README)


# --- routing and versions -------------------------------------------------------------------------


def test_each_reader_is_deterministic_versioned_and_registered():
    methods = {e.actor.method for e in deterministic_extractors()}
    assert {"hf-config-context@1", "hf-repo-metadata@1", "hf-readme-spec@1"} <= methods
    for e in (HFConfigContextExtractor(), HFRepoMetadataExtractor(), HFReadmeSpecExtractor()):
        assert e.actor.model_family == "deterministic"


def test_a_config_or_api_json_is_routed_to_its_reader_alone_and_a_readme_beside_the_rest():
    ordered = deterministic_extractors()
    c = claim("model.context_window", 131072)
    chosen = _readers_for(ordered, c, config(max_position_embeddings=131072), None,
                          source_url=CONFIG)
    assert [type(e) for e in chosen] == [HFConfigContextExtractor]
    chosen = _readers_for(ordered, claim("model.output_modalities", ["text"]),
                          api(pipeline_tag="text-generation"), None, source_url=API)
    assert [type(e) for e in chosen] == [HFRepoMetadataExtractor]
    chosen = _readers_for(ordered, c, TWO_COLUMN, None, source_url=README)
    assert HFReadmeSpecExtractor in {type(e) for e in chosen} and len(chosen) > 1
    # Another facet on the same config is not theirs.
    other = _readers_for(ordered, claim("model.release_date", "2026-01-01"),
                         config(max_position_embeddings=131072), None, source_url=CONFIG)
    assert HFConfigContextExtractor not in {type(e) for e in other}


class Regions:
    def __init__(self, text, url):
        self._text, self._url = text, url

    def text(self, source_id, copy_ref, region_id):
        return self._text

    def source_url(self, source_id):
        return self._url

    def source_kind(self, source_id):
        return "weights_repository"

    def source_publisher(self, source_id):
        return None

    def cite_only_status(self, source_id, copy_ref):
        return False


def test_verify_end_to_end_records_the_new_method():
    c = claim("model.weights_openness", "open_weights")
    result = verify(c, Regions(json.dumps(files("README.md", "model.safetensors")), API),
                    deterministic_extractors(), today=date(2026, 11, 25))
    assert result.outcome == "verified"
    assert result.verification.verifier.method == "hf-repo-metadata@1"
    result = verify(claim("model.context_window", 32768), Regions("- Max Input Tokens: 32k\n",
                    README), deterministic_extractors(), today=date(2026, 11, 25))
    assert result.outcome != "verified"
