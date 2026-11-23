"""BenchmarkCard: the schema for one benchmark wiki page (benchmarks/<id>.md front matter).

The template IS the schema, as with model cards: every field here is a front-matter key.
Unknown = empty/None, never a guess. `models_covered` is derived from the model cards at build time
and must not be authored.
"""
from __future__ import annotations

import re
from typing import Literal, get_args, get_origin

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from schema.enums import BenchmarkCategory

ID_RE = re.compile(r"^[a-z0-9][a-z0-9_]{1,80}$")


class Metric(BaseModel):
    name: str = ""                       # e.g. "accuracy", "pass@1", "% resolved", "Elo"
    direction: Literal["higher_is_better", "lower_is_better"] = "higher_is_better"
    unit: str = ""                       # "%", "points", "Elo"
    min_score: float = 0
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


class DomainTag(BaseModel):
    """One domain a benchmark measures, and how directly (MODEL-133).

    `id` names a domain in `registry/domains.yaml`; `tests/test_decision_registry.py`
    checks every tag against it. `direct`: the benchmark's tasks are instances of
    the domain. `proxy`: correlated with it, a slice of it, or preference rather
    than correctness. An absent tag means "not tagged", never "no domain".
    """

    model_config = ConfigDict(extra="forbid")

    id: str
    directness: Literal["direct", "proxy"]


class RefinementTag(BaseModel):
    """One registered refinement isolated directly or measured by proxy."""

    model_config = ConfigDict(extra="forbid")

    id: str
    directness: Literal["direct", "proxy"]


SCORING_KINDS = ("exact", "programmatic", "llm_judge", "human_judge", "mixed")
JUDGED_SCORING = frozenset({"llm_judge", "human_judge", "mixed"})


class Freshness(BaseModel):
    researched: str = ""                 # YYYY-MM-DD
    researched_by: str = ""              # "sonnet-5 agent, batch 1"
    reviewed: str = ""
    reviewed_by: str = ""


class BenchmarkCard(BaseModel):
    id: str
    name: str
    aliases: list[str] = Field(default_factory=list)
    #: Internal. Slugs the census used for this page, read only by
    #: `scripts/benchmarks/next_batch.py` to skip written pages. Never served or exported
    #: (`INTERNAL_PAGE_KEYS`); `aliases` is the display list ("Also known as").
    slug_aliases: list[str] = Field(default_factory=list)
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
    #: Optional and additive: pages without it still load (MODEL-133).
    domains: list[DomainTag] = Field(default_factory=list)
    #: Optional and additive: tags name entries in registry/refinements.yaml.
    refinements: list[RefinementTag] = Field(default_factory=list)
    sources: list[Source] = Field(default_factory=list)
    freshness: Freshness = Freshness()
    #: Internal (MODEL-536), additive and absent on existing pages: how the benchmark is
    #: scored. Never exported (`INTERNAL_PAGE_KEYS`) and in no public contract.
    scoring: Literal["exact", "programmatic", "llm_judge", "human_judge", "mixed"] | None = None
    #: Only for judged scoring. `not_stated` is a real value (the source is silent), never a guess.
    judge_blind: Literal["blind", "not_blind", "not_stated"] | None = None
    #: The page the scoring or blinding was read from; required whenever `scoring` is set.
    scoring_source: str = ""
    #: How the value was derived when no source was read: `page_methodology` means it was taken
    #: from this page's own "How it is scored" section. Then `scoring_source` stays empty, so no
    #: source is claimed that was not read.
    scoring_derivation: Literal["page_methodology"] | None = None

    @model_validator(mode="after")
    def _scoring_fields(self) -> BenchmarkCard:
        if self.scoring is None:
            if self.judge_blind is not None or self.scoring_source or self.scoring_derivation:
                raise ValueError("judge_blind, scoring_source and scoring_derivation need scoring to be set")
            return self
        judged = self.scoring in JUDGED_SCORING
        if self.judge_blind is not None and not judged:
            raise ValueError("judge_blind applies only to llm_judge, human_judge or mixed scoring")
        if judged and self.judge_blind is None:
            raise ValueError("judged scoring must say judge_blind: blind, not_blind or not_stated")
        if self.scoring_source:
            from decision.excluded import excluded_sources

            if excluded_sources().url(self.scoring_source):
                raise ValueError("scoring_source may not name an excluded source (S1)")
        if self.scoring_derivation and self.scoring_source:
            raise ValueError("scoring_source claims a source that was read; "
                             "scoring_derivation: page_methodology claims none. Use one")
        if not self.scoring_derivation and not self.scoring_source.startswith(("http://", "https://")):
            raise ValueError("scoring needs scoring_source (an http(s) URL actually read) "
                             "or scoring_derivation: page_methodology")
        return self

    @field_validator("id")
    @classmethod
    def _id(cls, v: str) -> str:
        if not ID_RE.match(v):
            raise ValueError("id must be snake_case: lowercase letters, digits, underscores")
        return v

    @field_validator("domains")
    @classmethod
    def _one_tag_per_domain(cls, v: list[DomainTag]) -> list[DomainTag]:
        ids = [tag.id for tag in v]
        repeated = sorted({i for i in ids if ids.count(i) > 1})
        if repeated:
            raise ValueError(f"a domain may be tagged once per page: {', '.join(repeated)}")
        return v

    @field_validator("refinements")
    @classmethod
    def _one_tag_per_refinement(cls, v: list[RefinementTag]) -> list[RefinementTag]:
        ids = [tag.id for tag in v]
        repeated = sorted({i for i in ids if ids.count(i) > 1})
        if repeated:
            raise ValueError(f"a refinement may be tagged once per page: {', '.join(repeated)}")
        return v

    @field_validator("summary")
    @classmethod
    def _summary(cls, v: str) -> str:
        if len(v) > 220:
            raise ValueError("summary must be one sentence, at most 220 characters")
        return v


#: Front-matter keys that stay in the repository: export writers drop them from the page they publish.
INTERNAL_PAGE_KEYS = ("slug_aliases", "scoring", "judge_blind", "scoring_source",
                      "scoring_derivation")


def unknown_key_paths(front: dict) -> list[str]:
    """Return schema-owned parents of unknown keys, never the authored keys.

    This is an authoring/audit check, separate from runtime model construction.
    Model-card facts and evidence have their own schemas and are not inspected.
    """
    paths = set()

    def walk(value, model, path):
        if not isinstance(value, dict):
            return
        if value.keys() - model.model_fields.keys():
            paths.add(path or "benchmark")
        for name, field in model.model_fields.items():
            annotation = field.annotation
            child = value.get(name)
            child_path = f"{path}.{name}" if path else name
            if get_origin(annotation) is list:
                annotation = get_args(annotation)[0]
                children = child if isinstance(child, list) else []
            else:
                children = [child]
            if isinstance(annotation, type) and issubclass(annotation, BaseModel):
                for item in children:
                    walk(item, annotation, child_path)

    walk(front, BenchmarkCard, "")
    return sorted(paths)


REQUIRED_SECTIONS = {
    "benchmark": ["What it measures", "How it is scored", "Dataset and licence", "Who publishes it", "Lineage",
                  "Saturation and contamination", "How to run it", "Reading the numbers"],
    "family": ["What it measures", "How it is scored", "Dataset and licence", "Who publishes it", "Lineage",
               "Saturation and contamination", "How to run it", "Reading the numbers"],
    "subset": ["What it measures", "Reading the numbers"],
}
