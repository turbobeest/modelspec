"""Catalogue readers preserve safe YAML behavior without Python parser cost."""

from __future__ import annotations

import gc
import time
from collections.abc import Callable
from datetime import date
from pathlib import Path

import pytest
import yaml

from pipeline.load import LoadError, split_front_matter
from schema.card import ModelCard

CARD = """---
model_id: lab/yaml
display_name: YAML model
provider: lab
model_type: llm-chat
release_date: "2026-10-23"
tags: &tags [first, second]
architecture:
  total_parameters: 42
  active_parameters: null
cost:
  input: 1.25
benchmarks:
  scores:
    example: 82.5
adoption:
  is_common_finetune_base: yes
downselect:
  use_case_tags: *tags
observed_on: 2026-10-23
---
Body stays here.
"""


@pytest.fixture(params=[False, True], ids=["available-loader", "python-fallback"])
def loader_mode(request, monkeypatch):
    if request.param:
        monkeypatch.delattr(yaml, "CSafeLoader", raising=False)


def test_front_matter_preserves_values_aliases_and_read_isolation(loader_mode):
    expected = yaml.safe_load(CARD.split("---", 2)[1])
    first, body = split_front_matter(CARD)
    assert first == expected
    assert first["observed_on"] == date(2026, 10, 23)
    assert first["tags"] is first["downselect"]["use_case_tags"]
    assert body == "Body stays here.\n"

    first["tags"].append("changed")
    first["benchmarks"]["scores"]["example"] = 0
    second, second_body = split_front_matter(CARD)
    assert second == expected
    assert second_body == body


def test_model_card_preserves_values_aliases_and_read_isolation(loader_mode):
    first = ModelCard.from_yaml_string(CARD)
    assert first.identity.release_date == "2026-10-23"
    assert first.identity.tags == first.downselect.use_case_tags == ["first", "second"]
    assert first.architecture.total_parameters == 42
    assert first.architecture.active_parameters is None
    assert first.cost.input == 1.25
    assert first.adoption.is_common_finetune_base is True
    assert first.benchmarks.scores == {"example": 82.5}
    assert first.prose_body == "Body stays here."
    expected = first.model_dump()

    first.identity.tags.append("changed")
    first.benchmarks.scores["example"] = 0
    assert ModelCard.from_yaml_string(CARD).model_dump() == expected


@pytest.mark.parametrize(
    ("reader", "error"),
    [(split_front_matter, LoadError), (ModelCard.from_yaml_string, (yaml.YAMLError, ValueError))],
    ids=["front-matter", "model-card"],
)
def test_catalogue_reader_rejects_python_yaml_tags(loader_mode, reader, error):
    content = CARD.replace(
        "tags: &tags [first, second]", "tags: &tags !!python/tuple [first, second]"
    )
    with pytest.raises(error):
        reader(content)


@pytest.mark.parametrize(
    "reader", [split_front_matter, ModelCard.from_yaml_string],
    ids=["front-matter", "model-card"],
)
def test_malformed_public_yaml_preserves_python_diagnostics(loader_mode, monkeypatch, reader):
    monkeypatch.delenv("MODELSPEC_REQUIRE_DATA_DIR", raising=False)
    monkeypatch.delenv("MODELSPEC_DATA_DIR", raising=False)
    raw = "model_id: [unfinished"
    is_front_matter = reader is split_front_matter
    yaml_text = raw if is_front_matter else f"\n{raw}\n"
    with pytest.raises(yaml.YAMLError) as expected:
        yaml.safe_load(yaml_text)
    with pytest.raises(LoadError if is_front_matter else type(expected.value)) as found:
        reader(f"---\n{raw}\n---\n")

    prefix = "front matter is not valid YAML: " if is_front_matter else ""
    assert str(found.value) == prefix + str(expected.value)
    diagnostic = found.value.__cause__ if is_front_matter else found.value
    assert type(diagnostic) is type(expected.value)
    assert (diagnostic.problem_mark.line, diagnostic.problem_mark.column) == (
        expected.value.problem_mark.line, expected.value.problem_mark.column
    )
    assert diagnostic.__context__ is None


def _best_cpu_time(read: Callable[[], object]) -> float:
    read()
    was_enabled = gc.isenabled()
    gc.disable()
    try:
        samples = []
        for _ in range(3):
            start = time.process_time()
            for _ in range(5):
                read()
            samples.append(time.process_time() - start)
        return min(samples)
    finally:
        if was_enabled:
            gc.enable()


@pytest.mark.perf
@pytest.mark.skipif(not hasattr(yaml, "CSafeLoader"), reason="libyaml acceleration unavailable")
@pytest.mark.parametrize(
    "reader", [split_front_matter, ModelCard.from_yaml_string],
    ids=["front-matter", "model-card"],
)
def test_large_catalogue_card_uses_less_than_half_python_parser_cpu(reader):
    root = Path(__file__).resolve().parents[1]
    content = (root / "models/nous-research/nous-hermes-2-mixtral-8x7b-dpo.md").read_text(
        encoding="utf-8"
    )
    front = content.split("---", 2)[1]
    reference = _best_cpu_time(lambda: yaml.safe_load(front))
    elapsed = _best_cpu_time(lambda: reader(content))
    assert elapsed < reference * 0.5, (
        f"{reader.__name__} used {elapsed:.3f}s CPU against {reference:.3f}s for "
        f"Python safe_load, ratio {elapsed / reference:.2f}; expected less than 0.50"
    )
