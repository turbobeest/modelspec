"""Read the repository's sources of truth into plain Python objects.

Three sources, in dependency order:

* `models/`     — one Markdown file per model card, YAML front matter.
* `benchmarks/` — one Markdown file per benchmark page, YAML front matter.
* the eligibility report — which benchmarks may be presented as current.

Nothing here reaches the network and nothing writes. The loader is deliberately
tolerant about *absent* data and strict about *malformed* data: a missing
optional field is normal in a 692-field schema where null means "not yet
researched", but a file that claims to be a card and will not parse is a defect
worth surfacing.
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from schema import private_data, redacted_error
from schema.yaml_loader import DuplicateKeyError, load_yaml, load_yaml_unique

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parent.parent
FRONT_MATTER = re.compile(r"^---\n(.*?)\n---\n?(.*)\Z", re.S)

#: Prose that lives beside the data and is not itself data.
NOT_CONTENT = {"LICENSE.md", "README.md", "AUTHORING.md", "CONTRIBUTING.md"}


class LoadError(RuntimeError):
    """A file that should have parsed did not."""


#: The frozen public image's ten benchmark pages that repeat ``aliases`` from before MODEL-554,
#: by file name and the SHA-256 of the whole file. The data repository has fixed them; the
#: image, which this repository may not change, has not. A page warns (as a count, keeping the
#: last value) only when it is read at ``benchmarks/<that name>``, the text parsed hashes to these,
#: and ``aliases`` is its only repeated key; tests stand copies of the image in for private
#: data, so the root may differ. Anything else that repeats a key is refused: an edited page,
#: a copy under another name, the same text as a card. Drop an entry once the image is fixed.
FROZEN_DUPLICATE_PAGES = {
    "aime_2024.md": "d0b612a0e51afe1bef63a67f2a8d47453d02bdc1e5c614afb1e48ed90c8bd250",
    "aime_2026.md": "803907c48d2ac4e660a738ad48c04b4400a94cbf8cfd2a5cc65eef73b61c8839",
    "arc_challenge.md": "688473a466cac5d595805f8e70c995b4e168ddc6118da5c0f1c65744b5a1b235",
    "bbh.md": "cc037545ec97340ff06ccdb3cf56e0eb87870c8b8fb1b1e2ee7e0c0532b261ca",
    "big_bench.md": "b0bae3290e9ec40b9dc49b3bc83d7a8cd757e18e5f9bbe515fcadf4303c85662",
    "gpqa.md": "93020240ac7ad9cde162e316324eac2e0e5946c25c4deeb97ffe966909e5db14",
    "humaneval.md": "cb3e3260777e062c57d1b5979954a613a18048408eb084f1d41246a57721974e",
    "mbpp.md": "43182a51a1c169c6492779f0a48a586b8eb93fc6fa43316e165bad234972b7d0",
    "model_written_evals.md": "297623b58c9fc308594d74a7fca3c2f545525090f8356e64cce4ef1d1d59cba7",
    "siqa.md": "02a315b5ca35ac46e75497d2f2e46c30f918d8ad52f8bf9df4ca97b40ff654ae",
}
_FROZEN_REPEATED_KEYS = frozenset({"aliases"})


def _frozen_duplicate(text: str, path: Path | None, exc: DuplicateKeyError) -> bool:
    """Whether a refused page is one of ``FROZEN_DUPLICATE_PAGES``, exactly. The hash is of the
    text that was parsed (UTF-8), never of a second read of the file."""
    if path is None or path.parent.name != "benchmarks" or set(exc.keys) != _FROZEN_REPEATED_KEYS:
        return False
    expected = FROZEN_DUPLICATE_PAGES.get(path.name)
    return expected is not None and hashlib.sha256(text.encode("utf-8")).hexdigest() == expected


def split_front_matter(text: str, *, path: Path | None = None,
                       duplicates: str | None = None) -> tuple[dict[str, Any], str]:
    """The front matter and the body. A repeated key is refused (``LoadError``), unless
    ``duplicates`` is ``"warn"`` (by default, only for a page in ``FROZEN_DUPLICATE_PAGES``):
    then it is logged as a count and the last value is kept."""
    match = FRONT_MATTER.match(text)
    if not match:
        raise LoadError("no YAML front matter")
    try:
        # One loader for fact YAML on every path (MODEL-554): a repeated key is refused.
        front = load_yaml_unique(match.group(1))
    except DuplicateKeyError as exc:
        # Counts and a location only, so the message is safe for private data too.
        message = f"{path or 'front matter'}: {exc.diagnostic(line_offset=1)}"
        if duplicates is None and _frozen_duplicate(text, path, exc):
            duplicates = "warn"
        if duplicates != "warn":
            raise LoadError(message) from None
        logger.warning("%s; the last value is kept", message)
        front = load_yaml(match.group(1))
    except yaml.YAMLError as exc:
        if private_data(path):
            raise LoadError(redacted_error(exc, path, line_offset=1)) from None
        raise LoadError(f"front matter is not valid YAML: {exc}") from exc
    if not isinstance(front, dict):
        raise LoadError("front matter is not a mapping")
    return front, match.group(2)


@dataclass(frozen=True)
class Model:
    model_id: str
    path: Path
    front: dict[str, Any]
    body: str
    cited_facts: list[dict[str, Any]] = field(default_factory=list)
    #: Facets of facts that claim an owner ruling that does not stand (MODEL-551): kept out of
    #: every export, as the snapshot keeps them out.
    withheld_facets: tuple[str, ...] = ()

    @property
    def cited_evidence(self) -> list[dict[str, Any]]:
        from decision.retention import is_cite_only_restrictive

        return [record for record in self.evidence
                if is_cite_only_restrictive(str(record.get("source_url") or ""))]

    @property
    def slug(self) -> str:
        return self.model_id

    @property
    def display_name(self) -> str:
        return str(self.front.get("display_name") or self.model_id)

    @property
    def provider(self) -> str:
        return str(self.front.get("provider") or self.path.parent.name)

    @property
    def provider_display(self) -> str:
        return str(self.front.get("provider_display") or self.provider)

    @property
    def scores(self) -> dict[str, float]:
        block = self.front.get("benchmarks") or {}
        raw = block.get("scores") if isinstance(block, dict) else None
        if not isinstance(raw, dict):
            return {}
        return {k: v for k, v in raw.items() if isinstance(v, (int, float))}

    @property
    def evidence(self) -> list[dict[str, Any]]:
        """Reviewed per-score records, each with its own source and date."""
        block = self.front.get("benchmarks") or {}
        raw = block.get("evidence") if isinstance(block, dict) else None
        if not isinstance(raw, list):
            return []
        return [r for r in raw if isinstance(r, dict) and r.get("benchmark_id")
                and isinstance(r.get("score"), (int, float))]

    @property
    def scores_as_of(self) -> str | None:
        block = self.front.get("benchmarks") or {}
        value = block.get("benchmark_as_of") if isinstance(block, dict) else None
        return str(value) if value else None

    @property
    def scores_source(self) -> str | None:
        block = self.front.get("benchmarks") or {}
        value = block.get("benchmark_source") if isinstance(block, dict) else None
        return str(value) if value else None

    @property
    def scores_citation(self) -> dict[str, str] | None:
        from decision.retention import is_cite_only_restrictive

        source = self.scores_source
        if self.scores and source and is_cite_only_restrictive(source):
            return {"status": "cited", "url": source}
        return None


@dataclass(frozen=True)
class Benchmark:
    benchmark_id: str
    path: Path
    front: dict[str, Any]
    body: str

    @property
    def name(self) -> str:
        return str(self.front.get("name") or self.benchmark_id)

    @property
    def category(self) -> str:
        return str(self.front.get("category") or "uncategorised")

    @property
    def summary(self) -> str:
        return str(self.front.get("summary") or "").strip()

    @property
    def aliases(self) -> list[str]:
        raw = self.front.get("aliases")
        return [str(a) for a in raw] if isinstance(raw, list) else []

    @property
    def lower_is_better(self) -> bool:
        metric = self.front.get("metric")
        return isinstance(metric, dict) and metric.get("direction") == "lower_is_better"


@dataclass(frozen=True)
class Disposition:
    """One benchmark's standing in the active catalogue.

    `status` is the spec's vocabulary: active, historical, unverified, alias, or
    unassessed for a discovery lead nobody has evaluated yet. `unassessed` is not
    a judgement — the spec is explicit that missing evidence is not staleness and
    not illegitimacy.
    """

    status: str
    canonical_id: str
    reasons: tuple[str, ...] = ()
    results: tuple[dict[str, Any], ...] = ()

    @property
    def is_active(self) -> bool:
        return self.status == "active"

    @property
    def cited_results(self) -> tuple[dict[str, Any], ...]:
        from decision.retention import is_cite_only_restrictive

        return tuple({**record, "citation": {"status": "cited", "url": record["source_url"]}}
                     for record in self.results if is_cite_only_restrictive(record.get("source_url") or ""))

    @property
    def verified_results(self) -> tuple[dict[str, Any], ...]:
        from decision.retention import is_cite_only_restrictive

        return tuple(record for record in self.results
                     if not is_cite_only_restrictive(record.get("source_url") or ""))


@dataclass
class Catalogue:
    as_of: date
    dispositions: dict[str, Disposition] = field(default_factory=dict)

    def for_benchmark(self, benchmark_id: str) -> Disposition:
        return self.dispositions.get(
            benchmark_id, Disposition(status="unassessed", canonical_id=benchmark_id)
        )

    @property
    def active_ids(self) -> list[str]:
        return sorted(i for i, d in self.dispositions.items() if d.is_active)


def load_models(root: Path | None = None, *, as_of: date | None = None) -> list[Model]:
    """Every card. ``as_of`` is the build's day, as the snapshot build is given it: a ruled
    fact is withheld unless its ruling stands at min(as_of, the UTC day)."""
    from decision.citation import fact_citation
    from decision.owner_ruling import (
        RepeatedKeyError,
        has_ruling,
        read_ruling_inputs,
        ruling_refused,
        served_fact,
    )
    from decision.reconfirmation import is_reconfirmation, reconfirmation_problem
    from decision.retained_correction import is_correction
    from decision.sources import configured_copy_store, load_sources

    root = root or REPO_ROOT
    directory = root / "models"
    sources = {sid: str(source.url) for sid, source in
               load_sources(root / "registry" / "sources.yaml").items()}
    rulings = None  # read once, and only when a card claims a ruling
    corrections = None  # read once, and only when a card carries a retained-page correction
    #: The snapshot build's copy store (``build_from_repo``), so a ruled fact's citation is
    #: decided here exactly as there; other facts keep the registry-only citation.
    store = configured_copy_store()
    out: list[Model] = []
    for path in sorted(directory.rglob("*.md")):
        if path.name in NOT_CONTENT:
            continue
        front, body = split_front_matter(path.read_text(encoding="utf-8", errors="replace"), path=path)
        model_id = front.get("model_id")
        if not model_id:
            # Prose without a model_id is not a card; skip rather than fail, the
            # same rule the PR validator applies.
            continue
        cited, withheld = [], []
        for fact in front.get("facts") or []:
            valid = True
            try:
                citation = fact_citation(fact, sources, store if has_ruling(fact) else None)
            except ValueError:
                # Fail closed for this fact only (MODEL-420): never shown as
                # verified, and one bad citation does not stop the build.
                logger.warning("%s: a fact's citation is invalid; shown as cited", model_id)
                citation, valid = {"status": "cited", "sources": []}, False
            if has_ruling(fact):
                # The snapshot's "ruling stands at cutoff" test and served form (MODEL-551).
                if rulings is None:
                    try:
                        rulings = read_ruling_inputs(root)
                    except RepeatedKeyError as error:
                        # The counts-only message every path gives (MODEL-554).
                        raise LoadError(str(error)) from None
                    except (OSError, ValueError, KeyError, TypeError) as error:
                        raise LoadError(f"owner rulings: {type(error).__name__}") from None
                if ruling_refused(fact, str(model_id), cited=bool(citation) and valid,
                                  inputs=rulings, sources=sources, as_of=as_of):
                    logger.warning("%s: a fact's owner ruling does not stand; withheld", model_id)
                    withheld.append(str(fact.get("facet")))
                    continue
            if is_reconfirmation(fact) and reconfirmation_problem(fact) is not None:
                # The snapshot's own test (MODEL-572): a reconfirmation that fails it is withheld.
                logger.warning("%s: a fact's reconfirmation does not stand; withheld", model_id)
                withheld.append(str(fact.get("facet")))
                continue
            if is_correction(fact):
                # A retained-page correction (MODEL-573) is shown, as cited, only when the
                # snapshot's own test admits it, whatever its references are; otherwise it is
                # withheld.
                if corrections is None:
                    corrections = _correction_inputs(root, as_of)
                citation = _corrected_citation(fact, str(model_id), corrections, sources)
                if citation is None:
                    logger.warning("%s: a fact's retained-page correction does not stand; "
                                   "withheld", model_id)
                    withheld.append(str(fact.get("facet")))
                    continue
            if citation:
                cited.append({**served_fact(fact), "verification": None, "citation": citation})
        block = front.get("benchmarks")
        rows = block.get("evidence") if isinstance(block, dict) else None
        if isinstance(rows, list) and any(isinstance(r, dict) and has_ruling(r) for r in rows):
            # A board row that claims an owner's ruling (MODEL-569) is shown only while its
            # ruling stands, by the snapshot's own test; otherwise it is withheld.
            if rulings is None:
                try:
                    rulings = read_ruling_inputs(root)
                except RepeatedKeyError as error:
                    raise LoadError(str(error)) from None
                except (OSError, ValueError, KeyError, TypeError) as error:
                    raise LoadError(f"owner rulings: {type(error).__name__}") from None
            kept = [r for r in rows if not (isinstance(r, dict) and has_ruling(r)
                                            and _ruled_row_withheld(root, r, str(model_id),
                                                                    rulings, sources, store,
                                                                    as_of))]
            if len(kept) != len(rows):
                logger.warning("%s: a board row's owner ruling does not stand; withheld",
                               model_id)
                front = {**front, "benchmarks": {**block, "evidence": kept}}
        out.append(Model(str(model_id), path, front, body, cited, tuple(withheld)))
    return out


def _correction_inputs(root: Path, as_of: date | None) -> tuple[Any, Any, date]:
    """The attempt log, the ranked verification log and the cutoff the snapshot build reads a
    retained-page correction against (MODEL-573)."""
    from decision.cited_change import VERIFICATION_LOG
    from decision.cited_reader import ATTEMPTS_FILE
    from decision.owner_ruling import RepeatedKeyError, read_json_lines, ruling_cutoff
    from decision.quarantine_clearing import AttemptLog
    from decision.snapshot import _Compiler

    try:
        log = AttemptLog.read(root / ATTEMPTS_FILE)
        verdicts = _Compiler._verification_log(read_json_lines(root / VERIFICATION_LOG))
    except RepeatedKeyError as error:
        raise LoadError(str(error)) from None
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise LoadError(f"retained-page corrections: {type(error).__name__}") from None
    return log, verdicts, ruling_cutoff(as_of)


def _corrected_citation(fact: dict[str, Any], model_id: str, inputs: tuple[Any, Any, date],
                        sources: dict[str, str]) -> dict[str, Any] | None:
    """The snapshot's citation for a correction its test admits, or ``None``."""
    from decision.retained_correction import correction_citation, correction_problem

    log, verdicts, cutoff = inputs
    if correction_problem(fact, model_id, log=log, verdicts=verdicts, sources=sources,
                          cutoff=cutoff) is not None:
        return None
    try:
        return correction_citation(fact, sources)
    except ValueError:
        return None


def _ruled_row_withheld(root: Path, row: dict[str, Any], model_id: str, rulings: Any,
                        sources: dict[str, str], store: Any, as_of: date | None) -> bool:
    """Whether a board row that claims an owner ruling is withheld (MODEL-569): the snapshot's
    test (``decision.board_ruling.row_refused``), with the verdicts ``reading_held`` finds."""
    from decision.board_ruling import BoardRegistry, row_refused
    from decision.citation import fact_citation
    from decision.quarantine_clearing import (
        QUEUE_FILE,
        queue_history,
        reading_candidates,
        reading_held,
    )

    try:
        citation = fact_citation(row, sources, store)
    except ValueError:
        return True
    try:
        own = str(row.get("id") or "")
        earlier = {key[1] for key, _ in reading_candidates(rulings.verdicts, row,
                                                           model_id=model_id) if key[1] != own}
        history = queue_history(root / QUEUE_FILE, earlier) if earlier else {}
        held = reading_held(rulings.verdicts, row, model_id=model_id, history=history)
        registry = BoardRegistry.read(root)
        page = root / "benchmarks" / f"{row.get('benchmark_id')}.md"
        metric = {}
        if page.is_file():
            bench, _ = split_front_matter(page.read_text(encoding="utf-8"), path=page)
            metric = bench.get("metric") if isinstance(bench.get("metric"), dict) else {}
    except (OSError, ValueError, KeyError, TypeError, AttributeError, LoadError):
        return True
    return row_refused(row, model_id, cited=citation is not None, rulings=rulings.rulings,
                       attempts=rulings.attempts, sources=sources,
                       max_score=metric.get("max_score"), held=held, as_of=as_of,
                       registry=registry, reopened=rulings.reopened)


def load_benchmarks(root: Path | None = None) -> list[Benchmark]:
    directory = (root or REPO_ROOT) / "benchmarks"
    out: list[Benchmark] = []
    seen: dict[str, Path] = {}
    for path in sorted(directory.glob("*.md")):
        if path.name in NOT_CONTENT:
            continue
        front, body = split_front_matter(path.read_text(encoding="utf-8", errors="replace"), path=path)
        benchmark_id = front.get("id")
        if not benchmark_id:
            raise LoadError(f"{path}: benchmark page has no id")
        benchmark_id = str(benchmark_id)
        if benchmark_id in seen:
            raise LoadError(f"duplicate benchmark id {benchmark_id!r}: {seen[benchmark_id]} and {path}")
        seen[benchmark_id] = path
        out.append(Benchmark(benchmark_id, path, front, body))
    return out


def load_catalogue(root: Path | None = None) -> Catalogue:
    """Read the eligibility report.

    Absent report means an empty active set, which the spec says is a valid
    outcome. It must never fall back to treating the census queue as a catalogue.
    """
    path = (root or REPO_ROOT) / "benchmarks/_census/eligibility/current-report.json"
    if not path.is_file():
        return Catalogue(as_of=datetime.now(timezone.utc).date())
    report = json.loads(path.read_text(encoding="utf-8"))
    as_of = date.fromisoformat(str(report["as_of"]))
    dispositions: dict[str, Disposition] = {}
    for row in report.get("rows", []):
        dispositions[str(row["candidate_id"])] = Disposition(
            status=str(row["status"]),
            canonical_id=str(row.get("canonical_id") or row["candidate_id"]),
            reasons=tuple(str(r) for r in row.get("reasons", [])),
            results=tuple(row.get("accepted_results", [])),
        )
    return Catalogue(as_of=as_of, dispositions=dispositions)
