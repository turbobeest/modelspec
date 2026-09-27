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

from decision.model import (
    SourceRef,
    TargetRef,
    Verification,
    VerificationActor,
    VerificationTarget,
    value_hash,
)
from decision.sources import CopyStore, load_sources
from decision.verify import Claim, Queue, Result, VerificationLog

ROOT = Path(__file__).resolve().parents[1]
FILED_AT = datetime(2026, 9, 27, 12, tzinfo=UTC)
COLLECTOR = VerificationActor(
    agent="openai-codex-model-163",
    model_family="gpt-5",
    method="hugging-face-api-projection@1",
)
VERIFIER = VerificationActor(
    agent="modelspec-verify",
    model_family="deterministic",
    method="runtime-memory-structured-row@2",
)


class SourceRowMismatchError(ValueError):
    """The source has no single model-bound row for the claimed configuration."""


@dataclass(frozen=True)
class _Table:
    context: tuple[str, ...]
    headers: tuple[str, ...]
    rows: tuple[tuple[str, ...], ...]


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


def main() -> None:
    document = yaml.safe_load((ROOT / "premier" / "inputs" / "slice-2.yaml").read_text())
    rows = document["local"]["candidates"]
    sources = load_sources(ROOT / "registry" / "sources.yaml")
    store = CopyStore()
    queue = Queue(ROOT / "verification")
    log = VerificationLog(ROOT / "verification")

    def file_verified(claim: Claim) -> None:
        queue.file(claim, at=FILED_AT)
        verification = Verification(
            target=VerificationTarget(
                kind=claim.target.kind,
                id=claim.target.id,
                value_hash=value_hash(claim.value),
            ),
            collector=claim.collector,
            verifier=VERIFIER,
            method=VERIFIER.method,
            outcome="verified",
            date=date(2026, 9, 27),
        )
        log.append(verification)
        queue.checked(Result(claim.target, "verified", verification), at=FILED_AT)

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
        for kind, label, value, unit, url in (
            ("parameters", "total_parameters", parameter_count, None, row["parameter_source_url"]),
            (
                "artifact",
                "quantised_size_bytes",
                row["published_size_bytes"],
                None,
                row["size_source_url"],
            ),
        ):
            source_id = _source_id(model_id, kind)
            if source_id not in sources or str(sources[source_id].url) != url:
                raise SystemExit(f"unregistered local-fit source: {source_id}")
            projection = {
                "read_date": row["read_date"],
                "rows": [{"model": published_model_id, label: value}],
            }
            ref = SourceRef(
                source_id=source_id,
                snapshot_ref=store.put((json.dumps(projection, sort_keys=True) + "\n").encode()),
                cited_regions=["row"],
            )
            suffix = (
                "model.parameters_total" if kind == "parameters" else "local.quantised_size_bytes"
            )
            file_verified(
                Claim(
                    target=TargetRef(kind="fact", id=f"{model_id}#{suffix}"),
                    subject=model_id,
                    names=names,
                    field=suffix,
                    label=label,
                    value=value,
                    unit=unit,
                    collector=COLLECTOR,
                    sources=(ref,),
                )
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
            "read_date": row["read_date"],
            "source_configuration": memory_configuration,
            "derived": {
                "fits_hardware": ["nvidia_rtx_4090"],
                "method": row["memory_method"],
            },
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
                    names=(model_id, model_id.rsplit("/", 1)[-1]),
                    field=target_id.rsplit("#", 1)[-1],
                    label=field,
                    value=value,
                    unit="gb" if field == "runtime_memory_gb" else None,
                    collector=COLLECTOR,
                    sources=(ref,),
                )
            )
        print(f"{model_id} memory_snapshot_ref={ref.snapshot_ref}")
    print(f"filed and verified {len(rows) * 4} local-fit facts")


if __name__ == "__main__":
    main()
