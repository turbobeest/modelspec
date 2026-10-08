"""Lab-level facts inherited by every model of that lab (MODEL-344).

``origin.lab_jurisdiction`` is a property of the lab, not of one model page.
``registry/labs.yaml`` records it once. The snapshot build copies a known value
onto each of that lab's models. A model card that already states a different
known set fails the build. A card that states the same set, or nothing, takes
the lab record.

An explicit null is a lab whose permitted pages were read and do not state a
country of incorporation: ``not_disclosed``, a note, a read date, and at least
one retained source. That lab's models are exempt from the jurisdiction gate.
A note with no source is not an exemption.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import yaml

FACET = "origin.lab_jurisdiction"
_CODE = re.compile(r"^[A-Z]{2}$")
_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_REF = re.compile(r"^sha256:[0-9a-f]{64}$")


class LabRegistryError(ValueError):
    """``registry/labs.yaml`` does not match the lab-jurisdiction record."""


@dataclass(frozen=True)
class Lab:
    id: str
    entity: str | None
    parent_entity: str | None
    note: str
    read_date: str
    state: str
    value: tuple[str, ...] | None
    sources: tuple[dict[str, Any], ...]

    @property
    def codes(self) -> frozenset[str] | None:
        """The known country set, or ``None`` when the lab discloses none."""
        if self.state != "known":
            return None
        return frozenset(self.value or ())

    @property
    def explicit_null(self) -> bool:
        """A sourced absence: the pages were read and stated no incorporation."""
        return (
            self.state == "not_disclosed"
            and not self.value
            and bool(self.note.strip())
            and bool(_DATE.match(self.read_date))
            and bool(self.sources)
        )

    def fact(self) -> dict[str, Any]:
        """The one fact dict every model of this lab shares. Known values only."""
        if self.codes is None:
            raise LabRegistryError(f"{self.id}: a null lab has no jurisdiction fact")
        return {
            "id": f"lab:{self.id}#{FACET}",
            "subject": {"kind": "model", "id": f"lab:{self.id}"},
            "facet": FACET,
            "state": "known",
            "value": sorted(self.codes),
            "sources": [dict(source) for source in self.sources],
        }


def lab_id_of(model_id: str) -> str:
    """The lab is the model id's prefix (``google/gemma-4`` -> ``google``)."""
    return model_id.split("/", 1)[0]


def stated_codes(fact: Mapping[str, Any]) -> frozenset[str] | None:
    """A model's known jurisdiction set, or ``None`` when it states none."""
    if str(fact.get("state")) != "known":
        return None
    value = fact.get("value")
    if not isinstance(value, list):
        return frozenset()
    return frozenset(str(item) for item in value)


def load_labs(root: Path) -> dict[str, Lab]:
    """Read ``registry/labs.yaml``. A missing file is an empty registry.

    The public checkout has no copy. A build from it does not invent labs.
    """
    path = Path(root) / "registry" / "labs.yaml"
    if not path.is_file():
        return {}
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise LabRegistryError(f"{path}: {exc}") from exc
    if not isinstance(data, Mapping) or data.get("schema_version") != 1:
        raise LabRegistryError(f"{path}: schema_version must be 1")
    rows = data.get("labs")
    if not isinstance(rows, list):
        raise LabRegistryError(f"{path}: labs must be a list")
    labs: dict[str, Lab] = {}
    for index, raw in enumerate(rows):
        lab = _lab(raw, where=f"{path}: labs[{index}]")
        if lab.id in labs:
            raise LabRegistryError(f"{path}: lab {lab.id} is listed twice")
        labs[lab.id] = lab
    return labs


def _lab(raw: Any, *, where: str) -> Lab:
    if not isinstance(raw, Mapping):
        raise LabRegistryError(f"{where}: a lab is a mapping")
    lab_id = raw.get("id")
    if not isinstance(lab_id, str) or not lab_id or "/" in lab_id:
        raise LabRegistryError(f"{where}: id must be a lab prefix")
    jurisdiction = raw.get("jurisdiction")
    if not isinstance(jurisdiction, Mapping):
        raise LabRegistryError(f"{where}: jurisdiction is required")
    state = jurisdiction.get("state")
    if state not in ("known", "not_disclosed"):
        raise LabRegistryError(f"{where}: jurisdiction.state must be known or not_disclosed")
    value = jurisdiction.get("value")
    if state == "known":
        if not isinstance(value, list) or not value or len(value) != len(set(value)):
            raise LabRegistryError(f"{where}: a known jurisdiction is a non-empty set of codes")
        if any(not isinstance(code, str) or not _CODE.match(code) for code in value):
            raise LabRegistryError(f"{where}: jurisdiction codes are ISO 3166-1 alpha-2")
        codes: tuple[str, ...] | None = tuple(value)
    else:
        if value is not None:
            raise LabRegistryError(f"{where}: not_disclosed jurisdiction has no value")
        codes = None
    note = raw.get("note")
    read_date = raw.get("read_date")
    if not isinstance(note, str) or not note.strip():
        raise LabRegistryError(f"{where}: note is required")
    if not isinstance(read_date, str) or not _DATE.match(read_date):
        raise LabRegistryError(f"{where}: read_date must be YYYY-MM-DD")
    sources = _sources(jurisdiction.get("sources"), where=where)
    entity = raw.get("entity")
    parent = raw.get("parent_entity")
    if entity is not None and not isinstance(entity, str):
        raise LabRegistryError(f"{where}: entity must be a string")
    if parent is not None and not isinstance(parent, str):
        raise LabRegistryError(f"{where}: parent_entity must be a string")
    if state == "known" and not entity:
        raise LabRegistryError(f"{where}: a known jurisdiction names the entity")
    if state == "not_disclosed" and not sources:
        raise LabRegistryError(
            f"{where}: an explicit null needs a source for the page that was read"
        )
    return Lab(
        id=lab_id,
        entity=entity,
        parent_entity=parent,
        note=note.strip(),
        read_date=read_date,
        state=state,
        value=codes,
        sources=sources,
    )


def _sources(raw: Any, *, where: str) -> tuple[dict[str, Any], ...]:
    if raw is None:
        return ()
    if not isinstance(raw, list) or not raw:
        raise LabRegistryError(f"{where}: sources must be a non-empty list")
    out = []
    for index, source in enumerate(raw):
        if not isinstance(source, Mapping):
            raise LabRegistryError(f"{where}: sources[{index}] is a mapping")
        source_id = source.get("source_id")
        ref = source.get("snapshot_ref")
        regions = source.get("cited_regions")
        if not isinstance(source_id, str) or not source_id:
            raise LabRegistryError(f"{where}: sources[{index}].source_id is required")
        if not isinstance(ref, str) or not _REF.match(ref):
            raise LabRegistryError(f"{where}: sources[{index}].snapshot_ref must be sha256:<64 hex>")
        if not isinstance(regions, list) or not regions or any(not isinstance(r, str) or not r for r in regions):
            raise LabRegistryError(f"{where}: sources[{index}].cited_regions must name regions")
        out.append({
            "source_id": source_id,
            "snapshot_ref": ref,
            "cited_regions": list(regions),
        })
    return tuple(out)
