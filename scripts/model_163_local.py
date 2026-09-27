#!/usr/bin/env python3
"""File MODEL-163 local-fit inputs for independent deterministic verification."""

from __future__ import annotations

import html
import json
import re
import urllib.request
from dataclasses import dataclass
from datetime import UTC, date, datetime
from html.parser import HTMLParser
from pathlib import Path

import yaml

from decision.model import DETERMINISTIC, SourceRef, TargetRef, VerificationActor
from decision.sources import CopyStore, load_sources
from decision.verify import (
    Claim,
    ExtractorError,
    Queue,
    Reading,
    StoredRegions,
    VerificationLog,
    verify,
)

ROOT = Path(__file__).resolve().parents[1]
FILED_AT = datetime(2026, 9, 27, 12, tzinfo=UTC)
COLLECTOR = VerificationActor(
    agent="openai-codex-model-163",
    model_family="gpt-5",
    method="hugging-face-api-projection@1",
)
class SourceRowMismatchError(ValueError):
    """The source has no single model-bound row for the claimed configuration."""


@dataclass(frozen=True)
class _Table:
    context: tuple[str, ...]
    headers: tuple[str, ...]
    rows: tuple[tuple[str, ...], ...]


@dataclass(frozen=True)
class LocalProjectionExtractor:
    """Re-read one local-hardware fact from its retained structured projection."""

    quantisation: str | None
    context_tokens: int | None
    max_memory_gb: float = 24.0

    actor = VerificationActor(
        agent="modelspec-verify",
        model_family=DETERMINISTIC,
        method="local-fact-structured-row@1",
    )

    @staticmethod
    def _rows(text: str) -> list[dict] | None:
        try:
            document = json.loads(text)
        except (TypeError, ValueError):
            return None
        if not isinstance(document, dict) or document.get("projection") != "local-fact-v1":
            return None
        rows = document.get("rows")
        if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
            return None
        return rows

    def accepts(self, text: str) -> bool:
        return self._rows(text) is not None

    def extract(self, claim: Claim, text: str) -> list[Reading]:
        rows = self._rows(text)
        if rows is None:
            raise ExtractorError("not a local-fact projection")
        readings = []
        for row in rows:
            if row.get("fact") != claim.field or not row.get("model"):
                continue
            configuration_matches = (
                (self.quantisation is None or row.get("quantisation") == self.quantisation)
                and (
                    self.context_tokens is None
                    or row.get("context_tokens") == self.context_tokens
                )
            )
            value = row.get("value") if configuration_matches else None
            unit = row.get("unit")
            if claim.field == "model.fits_hardware" and configuration_matches:
                runtime = row.get("runtime_memory_gb")
                runtime_unit = row.get("runtime_unit")
                value = (
                    "nvidia_rtx_4090"
                    if runtime_unit == "gb"
                    and isinstance(runtime, (int, float))
                    and float(runtime) <= self.max_memory_gb
                    else None
                )
                unit = None
            elif isinstance(value, list):
                value = ", ".join(str(item) for item in value)
            readings.append(
                Reading(
                    subject=str(row["model"]),
                    value=None if value is None else str(value),
                    unit=None if unit is None else str(unit),
                )
            )
        return readings


class _StructuredTableReader(HTMLParser):
    """Retain page identity and exact HTML table cells without flattening the page."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.identity: list[str] = []
        self.blocks: list[str] = []
        self.tables: list[_Table] = []
        self._capture: str | None = None
        self._text: list[str] = []
        self._table_context: tuple[str, ...] = ()
        self._headers: list[str] = []
        self._rows: list[tuple[str, ...]] = []
        self._cells: list[str] = []
        self._cell_kinds: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"title", "h1", "h2", "p", "th", "td"}:
            self._capture = tag
            self._text = []
        if tag == "table":
            self._table_context = tuple(self.blocks[-4:])
            self._headers = []
            self._rows = []
        elif tag == "tr":
            self._cells = []
            self._cell_kinds = []

    def handle_data(self, data: str) -> None:
        if self._capture is not None:
            self._text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == self._capture:
            value = _normalise_text(" ".join(self._text))
            if value:
                if tag in {"title", "h1"}:
                    self.identity.append(value)
                if tag in {"title", "h1", "h2", "p"}:
                    self.blocks.append(value)
                if tag in {"th", "td"}:
                    self._cells.append(value)
                    self._cell_kinds.append(tag)
            self._capture = None
            self._text = []
        if tag == "tr" and self._cells:
            if self._cell_kinds and all(kind == "th" for kind in self._cell_kinds):
                self._headers = list(self._cells)
            else:
                self._rows.append(tuple(self._cells))
        elif tag == "table":
            self.tables.append(_Table(self._table_context, tuple(self._headers), tuple(self._rows)))


def _normalise_text(value: str) -> str:
    return " ".join(html.unescape(value).split())


def _normalise_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.casefold())


_PAGE_MODEL_PATTERNS = (
    re.compile(r"What (?:GPU|hardware) do I need to run (?P<model>.+?)\?", re.IGNORECASE),
    re.compile(r"(?P<model>.+?): Local LLM VRAM Requirements(?: \|.+)?", re.IGNORECASE),
    re.compile(r"(?P<model>.+?) VRAM Requirements(?::.+)?", re.IGNORECASE),
)


def _page_model(identity: str, wanted_names: set[str]) -> str | None:
    candidates = [identity]
    for pattern in _PAGE_MODEL_PATTERNS:
        match = pattern.fullmatch(identity)
        if match:
            candidates.append(match.group("model"))
    return next(
        (candidate for candidate in candidates if _normalise_name(candidate) in wanted_names),
        None,
    )


def _model_columns(headers: tuple[str, ...]) -> tuple[int, ...]:
    return tuple(
        index
        for index, header in enumerate(headers)
        if _normalise_name(header) in {"configuration", "model", "modelname"}
    )


def _row_model(
    row: tuple[str, ...],
    headers: tuple[str, ...],
    model_columns: tuple[int, ...],
    wanted_names: set[str],
    quantisation: str,
) -> str | None:
    for index in model_columns:
        if index >= len(row):
            continue
        candidate = row[index]
        if _normalise_name(headers[index]) == "configuration":
            configured = re.fullmatch(r"(.+?)\s*\(([^()]*)\)", candidate)
            if configured and quantisation.casefold() in configured.group(2).casefold():
                candidate = configured.group(1)
        if _normalise_name(candidate) in wanted_names:
            return candidate
    return None


def _markdown_tables(source: str) -> tuple[list[str], list[_Table]]:
    identity = [
        _normalise_text(line.lstrip("# ")) for line in source.splitlines() if line.startswith("# ")
    ]
    tables: list[_Table] = []
    prior: list[str] = []
    lines = source.splitlines()
    index = 0
    while index < len(lines):
        line = lines[index].strip()
        if not line.startswith("|"):
            if line:
                prior.append(_normalise_text(line))
            index += 1
            continue
        raw_rows = []
        while index < len(lines) and lines[index].strip().startswith("|"):
            raw_rows.append(
                tuple(_normalise_text(cell) for cell in lines[index].strip().strip("|").split("|"))
            )
            index += 1
        if len(raw_rows) < 3 or not all(re.fullmatch(r":?-{3,}:?", cell) for cell in raw_rows[1]):
            continue
        tables.append(_Table(tuple(prior[-4:]), raw_rows[0], tuple(raw_rows[2:])))
    return identity, tables


def _context_matches(text: str, context_tokens: int) -> bool:
    compact = text.casefold().replace(",", "")
    if re.search(rf"(?<!\d){context_tokens}(?!\d)", compact):
        return True
    if context_tokens % 1024:
        return False
    abbreviated = context_tokens // 1024
    return bool(re.search(rf"(?<!\d){abbreviated}\s*k(?![a-z0-9])", compact))


def _number_of_gb(cell: str) -> float | None:
    match = re.fullmatch(
        r"(?:approximately\s+|roughly\s+|~\s*)?(\d+(?:\.\d+)?)\s*gb", cell.casefold()
    )
    return float(match.group(1)) if match else None


def parse_memory_configuration(
    source: str,
    *,
    model_names: tuple[str, ...],
    quantisation: str,
    context_tokens: int,
    runtime_memory_gb: float,
) -> dict:
    """Return one exact source row only when it binds the whole configuration."""
    if "<table" in source.casefold():
        reader = _StructuredTableReader()
        reader.feed(source)
        identities, tables = reader.identity, reader.tables
    else:
        identities, tables = _markdown_tables(source)

    wanted_names = {_normalise_name(name) for name in model_names}
    for table in tables:
        context = " ".join((*table.context, *table.headers))
        if not _context_matches(context, context_tokens):
            continue
        model_columns = _model_columns(table.headers)
        memory_columns = [
            index
            for index, header in enumerate(table.headers)
            if "total" in header.casefold() or "vram" in header.casefold()
        ]
        for row in table.rows:
            page_identity = next(
                (
                    parsed
                    for identity in identities
                    if (parsed := _page_model(identity, wanted_names)) is not None
                ),
                None,
            )
            row_model = _row_model(
                row,
                table.headers,
                model_columns,
                wanted_names,
                quantisation,
            )
            if page_identity is None and row_model is None:
                continue
            if not any(
                cell.casefold() == quantisation.casefold()
                or quantisation.casefold() in cell.casefold()
                for cell in row
            ):
                continue
            matching_memory = [
                index
                for index in memory_columns
                if index < len(row) and _number_of_gb(row[index]) == float(runtime_memory_gb)
            ]
            if len(matching_memory) != 1:
                continue
            actual_model = row_model or page_identity
            return {
                "model": actual_model,
                "quantisation": next(
                    cell for cell in row if quantisation.casefold() in cell.casefold()
                ),
                "context_tokens": context_tokens,
                "runtime_memory_gb": runtime_memory_gb,
                "cited_region": {
                    "context": list(table.context),
                    "headers": list(table.headers),
                    "row": list(row),
                },
            }
    raise SourceRowMismatchError(
        f"no exact row binds {model_names!r}, {quantisation}, "
        f"{context_tokens} tokens, and {runtime_memory_gb} GB"
    )


def _fetch_json(url: str) -> object:
    request = urllib.request.Request(url, headers={"User-Agent": "ModelSpec/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def _fetch_text(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": "ModelSpec/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8", errors="replace")


def _source_id(model_id: str, kind: str) -> str:
    return "model-163-local-" + model_id.replace("/", "-").lower() + f"-{kind}"


def _artifact_model(url: str) -> str:
    path = url.partition("/api/models/")[2].partition("/tree/")[0]
    repository = path.rsplit("/", 1)[-1]
    return re.sub(r"(?i)(?:[-_.]gguf)$", "", repository)


def main() -> None:
    document = yaml.safe_load((ROOT / "premier" / "inputs" / "slice-2.yaml").read_text())
    rows = document["local"]["candidates"]
    sources = load_sources(ROOT / "registry" / "sources.yaml")
    store = CopyStore()
    queue = Queue(ROOT / "verification")
    log = VerificationLog(ROOT / "verification")
    regions = StoredRegions(store, sources)

    def file_verified(claim: Claim, extractor: LocalProjectionExtractor) -> None:
        queue.file(claim, at=FILED_AT)
        result = verify(claim, regions, [extractor], today=date(2026, 9, 27))
        if result.verification is not None:
            log.append(result.verification)
            queue.checked(result, at=FILED_AT)
        if result.outcome != "verified":
            diffs = [diff.to_dict() for diff in result.diffs]
            raise SystemExit(
                f"{claim.target.id}: retained projection {result.outcome}: "
                f"{diffs or result.reason}"
            )

    for row in rows:
        model_id = row["model_id"]
        parameter_source = _fetch_json(row["parameter_source_url"])
        if not isinstance(parameter_source, dict):
            raise SystemExit(f"{model_id}: parameter source is not an object")
        published_model_id = str(parameter_source.get("modelId") or "")
        parameter_count = (parameter_source.get("safetensors") or {}).get("total")
        if parameter_count != row["parameter_count"]:
            raise SystemExit(
                f"{model_id}: expected {row['parameter_count']} parameters, got {parameter_count}"
            )

        size_source = _fetch_json(row["size_source_url"])
        if not isinstance(size_source, list):
            raise SystemExit(f"{model_id}: artifact source is not a file list")
        matches = [item for item in size_source if item.get("path") == row["artifact"]]
        if len(matches) != 1 or matches[0].get("size") != row["published_size_bytes"]:
            found = [(item.get("path"), item.get("size")) for item in matches]
            raise SystemExit(f"{model_id}: artifact mismatch: {found}")

        names = tuple(dict.fromkeys((published_model_id, model_id, model_id.rsplit("/", 1)[-1])))
        for kind, value, unit, subject, url in (
            (
                "parameters",
                parameter_count,
                "parameters",
                published_model_id,
                row["parameter_source_url"],
            ),
            (
                "artifact",
                row["published_size_bytes"],
                "bytes",
                _artifact_model(row["size_source_url"]),
                row["size_source_url"],
            ),
        ):
            source_id = _source_id(model_id, kind)
            if source_id not in sources or str(sources[source_id].url) != url:
                raise SystemExit(f"unregistered local-fit source: {source_id}")
            suffix = (
                "model.parameters_total" if kind == "parameters" else "local.quantised_size_bytes"
            )
            projection = {
                "projection": "local-fact-v1",
                "read_date": row["read_date"],
                "rows": [
                    {
                        "model": subject,
                        "fact": suffix,
                        "value": value,
                        "unit": unit,
                        **(
                            {"quantisation": row["quantisation"], "artifact": row["artifact"]}
                            if kind == "artifact"
                            else {}
                        ),
                    }
                ],
            }
            ref = SourceRef(
                source_id=source_id,
                snapshot_ref=store.put((json.dumps(projection, sort_keys=True) + "\n").encode()),
                cited_regions=["row"],
            )
            file_verified(
                Claim(
                    target=TargetRef(kind="fact", id=f"{model_id}#{suffix}"),
                    subject=model_id,
                    names=names,
                    field=suffix,
                    value=value,
                    unit=unit,
                    collector=COLLECTOR,
                    sources=(ref,),
                ),
                LocalProjectionExtractor(
                    quantisation=row["quantisation"] if kind == "artifact" else None,
                    context_tokens=None,
                ),
            )

        memory_source = _fetch_text(row["memory_source_url"])
        context_tokens = int(row["context_tokens"])
        try:
            memory_configuration = parse_memory_configuration(
                memory_source,
                model_names=tuple(row["memory_model_names"]),
                quantisation=row["quantisation"],
                context_tokens=context_tokens,
                runtime_memory_gb=float(row["runtime_memory_gb"]),
            )
        except SourceRowMismatchError as error:
            raise SystemExit(f"{model_id}: {error}") from error

        source_id = _source_id(model_id, "memory")
        if source_id not in sources or str(sources[source_id].url) != row["memory_source_url"]:
            raise SystemExit(f"unregistered local-fit source: {source_id}")
        projection = {
            "projection": "local-fact-v1",
            "read_date": row["read_date"],
            "rows": [
                {
                    "model": memory_configuration["model"],
                    "fact": "local.runtime_memory_gb",
                    "value": memory_configuration["runtime_memory_gb"],
                    "unit": "gb",
                    "quantisation": row["quantisation"],
                    "context_tokens": context_tokens,
                    "cited_region": memory_configuration["cited_region"],
                },
                {
                    "model": memory_configuration["model"],
                    "fact": "model.fits_hardware",
                    "value": ["nvidia_rtx_4090"],
                    "quantisation": row["quantisation"],
                    "context_tokens": context_tokens,
                    "runtime_memory_gb": memory_configuration["runtime_memory_gb"],
                    "runtime_unit": "gb",
                    "hardware_limit_gb": float(document["local"]["max_memory_gb"]),
                    "method": row["memory_method"],
                    "cited_region": memory_configuration["cited_region"],
                },
            ],
        }
        ref = SourceRef(
            source_id=source_id,
            snapshot_ref=store.put((json.dumps(projection, sort_keys=True) + "\n").encode()),
            cited_regions=["row"],
        )
        for target_id, field, value in (
            (f"{model_id}#local.runtime_memory_gb", "runtime_memory_gb", row["runtime_memory_gb"]),
            (f"{model_id}#model.fits_hardware", "fits_hardware", ["nvidia_rtx_4090"]),
        ):
            file_verified(
                Claim(
                    target=TargetRef(kind="fact", id=target_id),
                    subject=model_id,
                    names=tuple(
                        dict.fromkeys(
                            (
                                model_id,
                                model_id.rsplit("/", 1)[-1],
                                *row["memory_model_names"],
                            )
                        )
                    ),
                    field=target_id.rsplit("#", 1)[-1],
                    label=field,
                    value=value,
                    unit="gb" if field == "runtime_memory_gb" else None,
                    collector=COLLECTOR,
                    sources=(ref,),
                ),
                LocalProjectionExtractor(
                    quantisation=row["quantisation"],
                    context_tokens=context_tokens,
                    max_memory_gb=float(document["local"]["max_memory_gb"]),
                ),
            )
        print(f"{model_id} memory_snapshot_ref={ref.snapshot_ref}")
    print(f"filed and verified {len(rows) * 4} local-fit facts")


if __name__ == "__main__":
    main()
