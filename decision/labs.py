"""Lab-level facts inherited by every model of that lab (MODEL-344).

``origin.lab_jurisdiction`` is a property of the lab, not of one model page.
``registry/labs.yaml`` records it once. The snapshot build copies a known value
onto each of that lab's models. A model card that already states a different
known set fails the build. A card that states the same set, or nothing, takes
the lab record.

A known set is the training entity's country of incorporation plus the ultimate
parent's, when the parent is a different entity. Each code has its own source.
A missing code is not recorded as the other one: that record is an explicit
null, not a shorter set.

An explicit null is a lab whose own legal, terms, imprint, or privacy page, or
an official registry, was read and does not yield a complete set. The cited
text has to be non-empty. A Hugging Face README, an empty page, or a marketing
homepage is not that source. That lab's models are exempt from the jurisdiction
gate. A lab with no such page is a coverage gap, and the gate still requires
a value for its models.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping
from urllib.parse import urlsplit

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
    entity_code: str | None = None
    parent_code: str | None = None

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
            "sources": [
                {key: value for key, value in source.items() if key != "party"}
                for source in self.sources
            ],
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


def load_labs(root: Path, *, copy_store: Any = None) -> dict[str, Lab]:
    """Read ``registry/labs.yaml``. A missing file is an empty registry.

    The public checkout has no copy. A build from it does not invent labs.
    A known code and an explicit null are checked against the retained copy.
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
    _require_source_text(Path(root), labs, copy_store)
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
    if state not in ("known", "not_disclosed", "gap"):
        raise LabRegistryError(f"{where}: jurisdiction.state must be known, not_disclosed, or gap")
    value = jurisdiction.get("value")
    if state == "known":
        if not isinstance(value, list) or not value or len(value) != len(set(value)):
            raise LabRegistryError(f"{where}: a known jurisdiction is a non-empty set of codes")
        if any(not isinstance(code, str) or not _CODE.match(code) for code in value):
            raise LabRegistryError(f"{where}: jurisdiction codes are ISO 3166-1 alpha-2")
        codes: tuple[str, ...] | None = tuple(value)
    else:
        if value is not None:
            raise LabRegistryError(f"{where}: {state} jurisdiction has no value")
        codes = None
    note = raw.get("note")
    read_date = raw.get("read_date")
    if not isinstance(note, str) or not note.strip():
        raise LabRegistryError(f"{where}: note is required")
    if not isinstance(read_date, str) or not _DATE.match(read_date):
        raise LabRegistryError(f"{where}: read_date must be YYYY-MM-DD")
    entity = raw.get("entity")
    parent = raw.get("parent_entity")
    entity_code = raw.get("entity_code")
    parent_code = raw.get("parent_code")
    if entity is not None and not isinstance(entity, str):
        raise LabRegistryError(f"{where}: entity must be a string")
    if parent is not None and not isinstance(parent, str):
        raise LabRegistryError(f"{where}: parent_entity must be a string")
    if entity_code is not None and (not isinstance(entity_code, str) or not _CODE.match(entity_code)):
        raise LabRegistryError(f"{where}: entity_code must be ISO 3166-1 alpha-2")
    if parent_code is not None and (not isinstance(parent_code, str) or not _CODE.match(parent_code)):
        raise LabRegistryError(f"{where}: parent_code must be ISO 3166-1 alpha-2")
    raw_sources = jurisdiction.get("sources")
    if state == "gap":
        if raw_sources:
            raise LabRegistryError(f"{where}: a coverage gap has no source; it is not an explicit null")
        sources: tuple[dict[str, Any], ...] = ()
    else:
        sources = _sources(raw_sources, where=where)
    if state == "known":
        _known_parties(
            where,
            entity=entity,
            parent=parent,
            entity_code=entity_code,
            parent_code=parent_code,
            codes=set(codes or ()),
            sources=sources,
        )
    elif state == "not_disclosed" and not sources:
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
        entity_code=entity_code,
        parent_code=parent_code,
    )


def _known_parties(where: str, *, entity: str | None, parent: str | None,
                   entity_code: str | None, parent_code: str | None,
                   codes: set[str], sources: tuple[dict[str, Any], ...]) -> None:
    """A known set names each entity's code and a source that carries it."""
    if not entity:
        raise LabRegistryError(f"{where}: a known jurisdiction names the entity")
    if not entity_code:
        raise LabRegistryError(f"{where}: a known jurisdiction names entity_code")
    parties = [source.get("party") for source in sources]
    if any(party not in ("entity", "parent") for party in parties):
        raise LabRegistryError(f"{where}: each source names party entity or parent")
    if "entity" not in parties:
        raise LabRegistryError(f"{where}: the training entity needs its own source")
    expected = {entity_code}
    if parent is not None:
        if parent.strip() == entity.strip():
            raise LabRegistryError(f"{where}: parent_entity must differ from entity")
        if not parent_code:
            raise LabRegistryError(
                f"{where}: a parent that differs from the entity needs its own sourced code"
            )
        if "parent" not in parties:
            raise LabRegistryError(f"{where}: the parent needs its own source")
        expected.add(parent_code)
    elif parent_code is not None or "parent" in parties:
        raise LabRegistryError(f"{where}: parent_code requires a different parent_entity")
    if codes != expected:
        raise LabRegistryError(
            f"{where}: jurisdiction value must be exactly the sourced entity codes"
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
        item = {
            "source_id": source_id,
            "snapshot_ref": ref,
            "cited_regions": list(regions),
        }
        if "party" in source:
            item["party"] = source.get("party")
        out.append(item)
    return tuple(out)


_NULL_PAGE = re.compile(r"legal|terms|privacy|imprint|policies|agreement", re.IGNORECASE)


def _null_url_problem(url: str) -> str | None:
    """Why this URL cannot support an explicit null, or None when it can."""
    parts = urlsplit(url)
    host = (parts.hostname or "").casefold()
    path = parts.path or "/"
    if host == "huggingface.co" or host.endswith(".huggingface.co") or "readme.md" in url.casefold():
        return "a Hugging Face README is not a lab legal page or a registry"
    if host == "sec.gov" or host.endswith(".sec.gov"):
        return None
    if path in ("", "/"):
        return "a marketing homepage does not state incorporation"
    if _NULL_PAGE.search(path) is None:
        return "an explicit null cites the lab's legal, terms, imprint, or privacy page, or a registry"
    return None


def _require_source_text(root: Path, labs: Mapping[str, Lab], copy_store: Any) -> None:
    """Known codes and explicit nulls have to be present in the retained copy."""
    if not labs:
        return
    from decision.sources import CopyStore, load_sources
    from decision.verify import StoredRegions, jurisdiction_codes

    registered = load_sources(root / "registry" / "sources.yaml")
    store = copy_store if copy_store is not None else CopyStore()
    regions = StoredRegions(store, registered)
    for lab in labs.values():
        if lab.state == "gap":
            continue
        for source in lab.sources:
            record = registered.get(source["source_id"])
            if record is None:
                raise LabRegistryError(f"{lab.id}: source {source['source_id']} is not registered")
            if lab.explicit_null:
                problem = _null_url_problem(str(record.url))
                if problem:
                    raise LabRegistryError(f"{lab.id}: {problem}")
            for region_id in source["cited_regions"]:
                text = regions.text(source["source_id"], source["snapshot_ref"], region_id)
                if text is None or not text.strip():
                    raise LabRegistryError(
                        f"{lab.id}: {source['source_id']}#{region_id} has no retained text"
                    )
                if lab.state != "known":
                    continue
                found = jurisdiction_codes(text)
                wanted = lab.entity_code if source.get("party") == "entity" else lab.parent_code
                if wanted not in found:
                    raise LabRegistryError(
                        f"{lab.id}: {source['source_id']} does not state {wanted} "
                        f"(read {sorted(found) or 'nothing'})"
                    )
                extra = found - set(lab.value or ())
                if extra:
                    raise LabRegistryError(
                        f"{lab.id}: {source['source_id']} states {sorted(extra)}, "
                        "which is outside the recorded set"
                    )
