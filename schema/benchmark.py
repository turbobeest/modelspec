"""BenchmarkCard: the schema for one benchmark wiki page (benchmarks/<id>.md front matter).

The template IS the schema, as with model cards: every field here is a front-matter key.
Unknown = empty/None, never a guess. `models_covered` is derived from the model cards at build time
and must not be authored.
"""
from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel, Field, field_validator

from schema.enums import BenchmarkCategory

ID_RE = re.compile(r"^[a-z0-9][a-z0-9_]{1,80}$")


class Metric(BaseModel):
    name: str = ""                       # e.g. "accuracy", "pass@1", "% resolved", "Elo"
    direction: Literal["higher_is_better", "lower_is_better"] = "higher_is_better"
    unit: str = ""                       # "%", "points", "Elo"
    max_score: float | None = None
    random_baseline: float | None = None
    human_baseline: float | None = None
    baseline_note: str = ""


class Dataset(BaseModel):
    size: int | None = None              # number of items/tasks/questions
    size_note: str = ""                  # "500 tasks", "57 subjects x ~14k questions"
    url: str = ""
    license: str = ""                    # SPDX id or the licence name as published
    languages: list[str] = Field(default_factory=list)
    modalities: list[str] = Field(default_factory=list)   # text, code, image, video, audio
    splits: str = ""
    public_test_set: bool | None = None  # False when answers are held out


class Publisher(BaseModel):
    org: str = ""
    authors: list[str] = Field(default_factory=list)
    url: str = ""


class Paper(BaseModel):
    title: str = ""
    arxiv: str = ""                      # e.g. "2310.06770"
    url: str = ""
    year: int | None = None


class Lineage(BaseModel):
    family: str = ""                     # id of the family page, e.g. "mmlu", "swe_bench"
    predecessor: str = ""                # id
    successors: list[str] = Field(default_factory=list)   # ids
    variants: list[str] = Field(default_factory=list)     # ids of subsets / language / category variants


class Saturation(BaseModel):
    status: Literal["open", "watch", "saturated", "unknown"] = "unknown"
    top_score: float | None = None
    as_of: str = ""                      # YYYY-MM
    note: str = ""


class Contamination(BaseModel):
    risk: Literal["low", "medium", "high", "unknown"] = "unknown"
    note: str = ""


class Harness(BaseModel):
    lm_eval: str = ""                    # lm-evaluation-harness task name
    inspect_evals: str = ""              # inspect_evals id
    helm: str = ""                       # HELM scenario
    opencompass: str = ""                # OpenCompass dataset
    bigbench: str = ""                   # BIG-bench task
    other: str = ""


class Source(BaseModel):
    url: str
    title: str = ""
    accessed: str = ""                   # YYYY-MM-DD

    @field_validator("url")
    @classmethod
    def _http(cls, v: str) -> str:
        if not v.startswith(("http://", "https://")):
            raise ValueError("source url must be http(s)")
        return v


class Freshness(BaseModel):
    researched: str = ""                 # YYYY-MM-DD
    researched_by: str = ""              # "sonnet-5 agent, batch 1"
    reviewed: str = ""
    reviewed_by: str = ""


class BenchmarkCard(BaseModel):
    id: str
    name: str
    aliases: list[str] = Field(default_factory=list)
    page_kind: Literal["benchmark", "family", "subset"] = "benchmark"
    category: BenchmarkCategory
    subcategory: str = ""
    status: Literal["active", "saturated", "deprecated", "superseded", "proposed", "unknown"] = "unknown"
    summary: str = ""                    # one sentence, <= 200 chars
    measures: str = ""                   # one paragraph
    task_format: str = ""
    metric: Metric = Metric()
    dataset: Dataset = Dataset()
    publisher: Publisher = Publisher()
    paper: Paper = Paper()
    leaderboard_url: str = ""
    repo_url: str = ""
    released: str = ""                   # YYYY or YYYY-MM
    last_updated: str = ""
    lineage: Lineage = Lineage()
    saturation: Saturation = Saturation()
    contamination: Contamination = Contamination()
    harness: Harness = Harness()
    tags: list[str] = Field(default_factory=list)
    sources: list[Source] = Field(default_factory=list)
    freshness: Freshness = Freshness()

    @field_validator("id")
    @classmethod
    def _id(cls, v: str) -> str:
        if not ID_RE.match(v):
            raise ValueError("id must be snake_case: lowercase letters, digits, underscores")
        return v

    @field_validator("summary")
    @classmethod
    def _summary(cls, v: str) -> str:
        if len(v) > 220:
            raise ValueError("summary must be one sentence, at most 220 characters")
        return v


REQUIRED_SECTIONS = {
    "benchmark": ["What it measures", "How it is scored", "Dataset and licence", "Who publishes it", "Lineage",
                  "Saturation and contamination", "How to run it", "Reading the numbers"],
    "family": ["What it measures", "How it is scored", "Dataset and licence", "Who publishes it", "Lineage",
               "Saturation and contamination", "How to run it", "Reading the numbers"],
    "subset": ["What it measures", "Reading the numbers"],
}
