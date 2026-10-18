"""Reviewed xAI DOM matrices, with no discovery or text-reader fallback."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass

from decision.normalise import Node, RuleSet, normalise_document

Path = tuple[int, ...]
_DOM_RULES = RuleSet("xai-exact-dom", "html", drop_page_chrome=False,
                     drop_furniture=False, strip_volatile=False, strip_tracking=False)


class TemplateDriftError(ValueError):
    def __init__(self, detail: str):
        super().__init__(f"template drifted: {detail}")


@dataclass(frozen=True)
class MatrixColumn:
    label: str
    subject: str
    path: Path
    price_path: Path | None = None


@dataclass(frozen=True)
class MatrixRow:
    label: str
    path: Path
    cells: tuple[Path, ...]


@dataclass(frozen=True)
class XaiMatrixTemplate:
    source_url: str
    region_id: str
    copy_sha256: str
    document_sha256: str
    region_sha256: str
    region_path: Path
    header_path: Path
    header_children: int
    rows_path: Path
    rows_children: int
    columns: tuple[MatrixColumn, ...]
    rows: tuple[MatrixRow, ...]
    glyphs: tuple[tuple[str, bool], ...]
    models: tuple[tuple[str, str], ...]
    agent_products: tuple[str, ...] = ()
    unversioned_products: tuple[str, ...] = ()
    text_cells: tuple[tuple[str, str], ...] = ()


def document_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _children(node: Node) -> list[Node]:
    return [child for child in node.children if isinstance(child, Node)]


def _at(node: Node, path: Path) -> Node:
    for index in path:
        children = _children(node)
        if index < 0 or index >= len(children):
            raise TemplateDriftError("recorded DOM path is absent")
        node = children[index]
    return node


def _shape(node: Node) -> list:
    return [node.tag, sorted(node.attrs.items()), [
        _shape(child) if isinstance(child, Node) else child for child in node.children
    ]]


def _dom_sha256(node: Node) -> str:
    return document_sha256(json.dumps(_shape(node), ensure_ascii=False, separators=(",", ":")))


def _text(node: Node) -> str:
    return "".join(_text(child) if isinstance(child, Node) else child
                   for child in node.children).strip()


def read_matrix(template: XaiMatrixTemplate, text: str, *, subject: str, facet: str,
                catalogue_ids: frozenset[str]) -> tuple[str, str]:
    """Read one approved matrix. Paths count element children, starting at zero."""
    # Do not parse an unknown document. An approved digest bounds parser input.
    if document_sha256(text) != template.document_sha256:
        raise TemplateDriftError("unreviewed document")
    root = normalise_document(text.encode("utf-8"), _DOM_RULES).root
    if root is None:
        raise TemplateDriftError("HTML document is absent")
    region = _at(root, template.region_path)
    if _dom_sha256(region) != template.region_sha256:
        raise TemplateDriftError("region hash changed")
    if len(_children(_at(region, template.header_path))) != template.header_children:
        raise TemplateDriftError("header width changed")
    if len(_children(_at(region, template.rows_path))) != template.rows_children:
        raise TemplateDriftError("row count changed")
    if tuple(_text(_at(region, col.path)) for col in template.columns) != tuple(
        col.label for col in template.columns
    ):
        raise TemplateDriftError("plan headers changed")
    if tuple(_text(_at(region, row.path)) for row in template.rows) != tuple(
        row.label for row in template.rows
    ):
        raise TemplateDriftError("row labels changed")
    subjects = [col.subject for col in template.columns]
    if subjects.count(subject) != 1:
        raise TemplateDriftError("offering has no unique reviewed column")
    column_index = subjects.index(subject)
    glyphs = dict(template.glyphs)
    for node in region.elements():
        if node.tag == "svg" and _dom_sha256(node) not in glyphs:
            raise TemplateDriftError("unknown SVG glyph")
    models = dict(template.models)
    if any(model_id not in catalogue_ids for model_id in models.values()):
        raise TemplateDriftError("model mapping is absent from the catalogue")
    approved_labels = (set(models) | set(template.agent_products)
                       | set(template.unversioned_products))
    if set(row.label for row in template.rows) != approved_labels:
        raise TemplateDriftError("row has no reviewed interpretation")
    cells = {}
    text_cells = dict(template.text_cells)
    for row in template.rows:
        if len(row.cells) != len(template.columns):
            raise TemplateDriftError("cell count differs from the recorded columns")
        values = []
        for path in row.cells:
            cell = _at(region, path)
            children = _children(cell)
            literal = _text(cell)
            if literal in text_cells and not any(node.tag == "svg" for node in cell.elements()):
                values.append(text_cells[literal])
                continue
            if len(children) != 1 or children[0].tag != "svg" or _text(cell):
                raise TemplateDriftError("cell is not exactly one SVG glyph")
            digest = _dom_sha256(children[0])
            if digest not in glyphs:
                raise TemplateDriftError("unknown cell glyph")
            values.append("included" if glyphs[digest] else "not included")
        cells[row.label] = values[column_index]
    if facet == "offering.subscription.models_covered":
        value = ", ".join(model_id for label, model_id in template.models
                          if cells[label] == "included")
        if not value:
            raise TemplateDriftError("no included canonical model")
    elif facet == "offering.subscription.programmatic_or_agent_use" and template.agent_products:
        value = "; ".join(f"{label} {cells[label]}"
                          for label in template.agent_products)
    elif facet in {"offering.subscription.price", "offering.subscription.billing_period"}:
        price_path = template.columns[column_index].price_path
        if price_path is None:
            raise TemplateDriftError("column has no reviewed price cell")
        price = re.fullmatch(r"\$([0-9]+(?:\.[0-9]+)?)/month", _text(_at(region, price_path)))
        if price is None:
            raise TemplateDriftError("price is not an exact monthly USD amount")
        value = price.group(1) if facet.endswith(".price") else "monthly"
    else:
        raise TemplateDriftError("facet has no reviewed reading")
    return template.columns[column_index].subject, value


# Reviewed private captures. Current plan identities never alias Lite or Heavy.
XAI_MATRIX_TEMPLATES = (
    XaiMatrixTemplate(
        source_url="https://x.ai/pricing", region_id="page",
        copy_sha256="bdf1848f0fe27294ccc7497f2016650cb32406e7252ccf191ab5d3b21d16ab21",
        document_sha256="c6fac83303fe97d19fd186eaf53ba0b828074e67b4bd7d626ba5431f81113bd7",
        region_sha256="a881126da00c7280c4a9b38810f75ee5e1db2c54cffc587034d2f204caee5708",
        region_path=(0, 1, 5, 0, 1),
        header_path=(0, 0), header_children=8, rows_path=(2,), rows_children=7,
        columns=tuple(
            MatrixColumn(label, f"xai/subscription/{plan}", (0, 0, i, 0, 0), (0, 0, i, 0, 1))
            for i, (label, plan) in enumerate((
                ("Free", "free"), ("Plus", "plus"), ("Premium", "premium"),
                ("Super", "super"), ("Ultra", "ultra"), ("Teams", "teams"),
                ("Enterprise", "enterprise"),
            ), 1)
        ),
        rows=(MatrixRow("Grok Build", (2, 5, 0), tuple((2, 5, i) for i in range(1, 8))),
              MatrixRow("Grok Bot", (2, 6, 0), tuple((2, 6, i) for i in range(1, 8)))),
        glyphs=(("9964a387eb4c5a7031a444a18bd241e15acd858e5ae07b8a9882b6dbd3f654ee", True),
                ("38e19557634105609fc861e56d5365a5deb57186a1f59064a3bf3111b1ac6efa", False)),
        models=(), agent_products=("Grok Build", "Grok Bot"),
        text_cells=(("Limited", "limited"),),
    ),
    XaiMatrixTemplate(
        source_url="https://x.ai/grok/business", region_id="page",
        copy_sha256="c1dd2ba990de3cfaead12b59c01762964a2f1af53cfe714ee972106564cf67c1",
        document_sha256="b2ec9fb2bce961f284869a87bfd214622cd13aaf5c48bdbc36d03ca35cdbbac8",
        region_sha256="a0db084e2b6c50678c984de5b5fad3d477abb10c3878831630d4e0a2fa793c3d",
        region_path=(0, 1, 6, 0, 0, 0),
        header_path=(0,), header_children=3, rows_path=(1, 0, 1), rows_children=3,
        columns=(MatrixColumn("Business", "xai/subscription/business", (0, 1, 0, 0)),
                 MatrixColumn("Enterprise", "xai/subscription/enterprise", (0, 2, 0, 0))),
        rows=(MatrixRow("Imagine", (1, 0, 1, 0, 0), ((1, 1, 1, 0), (1, 2, 1, 0))),
              MatrixRow("Voice", (1, 0, 1, 1, 0), ((1, 1, 1, 1), (1, 2, 1, 1))),
              MatrixRow("Grok 4.7", (1, 0, 1, 2, 0), ((1, 1, 1, 2), (1, 2, 1, 2)))),
        glyphs=(("1c29d6d9097ae11e88e3b8c22faadd4541cd4849fb54b8c23933d819b56d1ab3", True),),
        models=(("Grok 4.7", "xai/grok-4-7"),),
        unversioned_products=("Imagine", "Voice"),
    ),
)
