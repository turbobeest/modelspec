#!/usr/bin/env python3
"""Write the MODEL-344 lab-jurisdiction registry from retained pages.

The set on a known lab is the training entity's country plus its ultimate
parent's, each from its own cited region. A missing code is an explicit null,
not a shorter set. A lab with no legal page or registry filing is a coverage
gap and has no source row.

``--claims`` files the known-lab claims with ``Queue.file``. It does not write
``verification/log.jsonl``. Restore that log and ``verification/queue/events.jsonl``
from ``origin/main`` before filing, and file once: a second ``--claims`` appends
another collected event.

Run with the code worktree on ``PYTHONPATH`` or pass ``--code`` (inserted first):

    python scripts/model_344_lab_jurisdiction.py \\
        --code <code worktree> --data <data worktree> --fetch <fetch dir>
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

READ_DATE = "2026-10-08"
FILED_AT = datetime(2026, 10, 8, tzinfo=UTC)
MARKER = re.compile(r"(?m)^- id: lab-jurisdiction-")
KNOWN_CARD = (
    "- facet: origin.lab_jurisdiction\n"
    "  value:\n"
    "  - US\n"
    "  state: known\n"
)
NULL_CARD = (
    "- facet: origin.lab_jurisdiction\n"
    "  value: null\n"
    "  state: not_disclosed\n"
)
DEMOTE = (
    "models/jcorners/ingot-8b-r3.md",
    "models/openai/gpt-5-4.md",
    "models/openai/gpt-5-6-sol.md",
    "models/openai/gpt-6-astra.md",
    "models/openai/gpt-6-sol.md",
    "models/typesafe/jev-1-13.md",
    "models/xai/grok-4-7.md",
)


@dataclass(frozen=True)
class Src:
    id: str
    url: str
    file: str
    fetch: str
    normaliser: str
    kind: str
    locator: str


@dataclass(frozen=True)
class Party:
    source_id: str
    role: str
    code: str


@dataclass(frozen=True)
class LabRow:
    id: str
    state: str
    note: str
    entity: str | None = None
    parties: tuple[Party, ...] = ()
    parent_entity: str | None = None


def sources() -> tuple[Src, ...]:
    page = ("page", "")
    rows = [
        ("lab-jurisdiction-annamodels", "https://www.lgresearch.ai/policies",
         "lg-policies.html", "http", "html-default", page),
        ("lab-jurisdiction-anthropic", "https://www.anthropic.com/news/the-long-term-benefit-trust",
         "retained/anthropic", "http", "html-default", page),
        ("lab-jurisdiction-bytedance", "https://www.doubao.com/legal/terms",
         "doubao-terms.html", "http", "html-default", page),
        ("lab-jurisdiction-cerebras", "https://data.sec.gov/submissions/CIK0002021728.json",
         "retained/cerebras", "http", "text-default", page),
        ("lab-jurisdiction-deepseek",
         "https://cdn.deepseek.com/policies/en-US/deepseek-open-platform-terms-of-service.html",
         "retained/deepseek", "http", "html-default", page),
        ("lab-jurisdiction-google-alphabet", "https://data.sec.gov/submissions/CIK0001652044.json",
         "retained/google", "http", "text-default", page),
        ("lab-jurisdiction-google-llc",
         "https://www.sec.gov/Archives/edgar/data/1652044/000165204426000018/googexhibit2101q42025.htm",
         "alphabet-ex21.htm", "http", "html-default",
         ("css", "table::excerpt=Google LLC | Delaware")),
        ("lab-jurisdiction-jcorners", "https://voxell.ai/terms",
         "retained/jcorners", "http", "html-default", page),
        ("lab-jurisdiction-jina", "https://jina.ai/legal/",
         "retained/jina", "http", "html-default", ("heading", "imprint")),
        ("lab-jurisdiction-jina-elastic",
         "https://www.sec.gov/Archives/edgar/data/1707753/000170775326000018/estc-20260430.htm",
         "estc-20260430.htm", "http", "html-default",
         ("css", '[name="dei:EntityIncorporationStateCountryCode"]')),
        ("lab-jurisdiction-kingsoft", "https://www.wps.com/privacy-policy/",
         "probe/wps-privacy", "http", "html-default", page),
        ("lab-jurisdiction-meta", "https://data.sec.gov/submissions/CIK0001326801.json",
         "retained/meta", "http", "text-default", page),
        ("lab-jurisdiction-microsoft", "https://data.sec.gov/submissions/CIK0000789019.json",
         "retained/microsoft", "http", "text-default", page),
        ("lab-jurisdiction-minimax", "https://agent.minimax.io/doc/zh/terms-of-service.html",
         "retained/minimax", "http", "html-default", page),
        ("lab-jurisdiction-moonshot", "https://platform.moonshot.ai/docs/agreement/modeluse",
         "retained/moonshot", "http", "html-default", page),
        ("lab-jurisdiction-nvidia", "https://data.sec.gov/submissions/CIK0001045810.json",
         "retained/nvidia", "http", "text-default", page),
        ("lab-jurisdiction-openai", "https://openai.com/policies/terms-of-use/",
         "openai-terms.html", "rendered", "html-default",
         ("page", "::excerpt=OpenAI OpCo, LLC, a Delaware company")),
        ("lab-jurisdiction-querit", "https://querit.ai/en/terms",
         "probe/querit-en-terms", "http", "html-default", page),
        ("lab-jurisdiction-qwen",
         "https://www.sec.gov/Archives/edgar/data/1577552/000119312526231755/baba-20260331.htm",
         "retained/qwen", "http", "html-default",
         ("css", '[name="dei:EntityIncorporationStateCountryCode"]')),
        ("lab-jurisdiction-tencent", "https://data.sec.gov/submissions/CIK0001293451.json",
         "retained/tencent", "http", "text-default", page),
        ("lab-jurisdiction-typesafe", "https://typesafe.ai/legal/terms",
         "retained/typesafe", "http", "html-default", page),
        ("lab-jurisdiction-xai", "https://x.ai/legal/terms-of-service",
         "retained/xai", "rendered", "html-default",
         ("page", "::excerpt=SpaceXAI LLC is a Nevada company")),
        ("lab-jurisdiction-zhipu", "https://docs.z.ai/legal-agreement/terms-of-use.md",
         "retained/zhipu", "http", "text-default", page),
    ]
    return tuple(
        Src(sid, url, file, fetch, normaliser, kind, locator)
        for sid, url, file, fetch, normaliser, (kind, locator) in rows
    )


def labs() -> tuple[LabRow, ...]:
    return (
        LabRow("annamodels", "not_disclosed",
               "The LG AI Research policies page states a copyright and privacy notice for "
               "LG AI연구원. It does not state a country of incorporation.",
               parties=(Party("lab-jurisdiction-annamodels", "", ""),)),
        LabRow("anthropic", "known",
               "The long-term benefit trust post says Anthropic is a Delaware public benefit "
               "corporation. No different parent is named.",
               entity="Anthropic",
               parties=(Party("lab-jurisdiction-anthropic", "entity", "US"),)),
        LabRow("bytedance", "not_disclosed",
               "The Doubao user agreement names 北京春田知韵科技有限公司及/或关联方 as the operator. "
               "The page does not state a country of incorporation.",
               parties=(Party("lab-jurisdiction-bytedance", "", ""),)),
        LabRow("cerebras", "known",
               "SEC submissions for Cerebras Systems Inc. give stateOfIncorporation DE. "
               "No different parent is named.",
               entity="Cerebras Systems Inc.",
               parties=(Party("lab-jurisdiction-cerebras", "entity", "US"),)),
        LabRow("codefuse", "gap",
               "codefuse.ai normalises to empty text. No legal, terms, imprint, privacy, or "
               "registry page with retained text was found."),
        LabRow("deepseek", "not_disclosed",
               "DeepSeek's open-platform terms say the service is owned and operated by "
               "Hangzhou DeepSeek Artificial Intelligence Co., Ltd. and set PRC governing law. "
               "They do not state a country of incorporation.",
               parties=(Party("lab-jurisdiction-deepseek", "", ""),)),
        LabRow("google", "known",
               "Alphabet's Form 10-K Exhibit 21 lists Google LLC in Delaware. SEC submissions "
               "for Alphabet Inc. give stateOfIncorporation DE. The Gemma terms name Google LLC "
               "as the licensor. Those terms do not name DeepMind Technologies Ltd as the party "
               "that trained the models.",
               entity="Google LLC", parent_entity="Alphabet Inc.",
               parties=(
                   Party("lab-jurisdiction-google-llc", "entity", "US"),
                   Party("lab-jurisdiction-google-alphabet", "parent", "US"),
               )),
        LabRow("infgrad", "gap",
               "No legal, terms, imprint, privacy, or registry page for this lab was found. "
               "A model-card README is not a source for this facet."),
        LabRow("jcorners", "not_disclosed",
               "Voxell terms name Voxell, Inc. and do not state a country of incorporation.",
               parties=(Party("lab-jurisdiction-jcorners", "", ""),)),
        LabRow("jina", "known",
               "The legal-page imprint names Jina AI GmbH and Amtsgericht Berlin HRB 218021. "
               "Elastic N.V.'s Form 10-K cover element dei:EntityIncorporationStateCountryCode "
               "reads Netherlands.",
               entity="Jina AI GmbH", parent_entity="Elastic N.V.",
               parties=(
                   Party("lab-jurisdiction-jina", "entity", "DE"),
                   Party("lab-jurisdiction-jina-elastic", "parent", "NL"),
               )),
        LabRow("kingsoft", "not_disclosed",
               "The WPS privacy policy names WPS Software Pte. Ltd. The page does not state "
               "the training lab's country of incorporation.",
               parties=(Party("lab-jurisdiction-kingsoft", "", ""),)),
        LabRow("meta", "known",
               "SEC submissions for Meta Platforms, Inc. give stateOfIncorporation DE.",
               entity="Meta Platforms, Inc.",
               parties=(Party("lab-jurisdiction-meta", "entity", "US"),)),
        LabRow("microsoft", "known",
               "SEC submissions for MICROSOFT CORP give stateOfIncorporation WA.",
               entity="MICROSOFT CORP",
               parties=(Party("lab-jurisdiction-microsoft", "entity", "US"),)),
        LabRow("minimax", "not_disclosed",
               "MiniMax's user terms name the operator 上海稀宇科技有限公司 and a Shanghai address. "
               "They do not state a country of incorporation.",
               parties=(Party("lab-jurisdiction-minimax", "", ""),)),
        LabRow("moonshot", "not_disclosed",
               "The Kimi Open Platform terms name Moonshot AI PTE. LTD. as the API contracting "
               "party. The page does not state that company's parent or the training lab's "
               "country of incorporation.",
               entity="Moonshot AI PTE. LTD.",
               parties=(Party("lab-jurisdiction-moonshot", "", ""),)),
        LabRow("nvidia", "known",
               "SEC submissions for NVIDIA CORP give stateOfIncorporation DE.",
               entity="NVIDIA CORP",
               parties=(Party("lab-jurisdiction-nvidia", "entity", "US"),)),
        LabRow("openai", "not_disclosed",
               "The global terms name OpenAI OpCo, LLC, a Delaware company. Pages on openai.com "
               "name OpenAI Group PBC and the OpenAI Foundation and do not state either parent's "
               "country of incorporation. The retained copy is the rendered page; a plain HTTP "
               "fetch returned 403.",
               entity="OpenAI OpCo, LLC",
               parties=(Party("lab-jurisdiction-openai", "", ""),)),
        LabRow("querit", "not_disclosed",
               "The Querit services agreement names Querit Private Limited. The page does not "
               "state a country of incorporation.",
               entity="Querit Private Limited",
               parties=(Party("lab-jurisdiction-querit", "", ""),)),
        LabRow("qwen", "not_disclosed",
               "Alibaba Group Holding Limited's Form 20-F cover element reads Cayman Islands. "
               "The filing's cover does not state the PRC training entity's country of "
               "incorporation, so the lab set is null.",
               entity="Alibaba Group Holding Limited",
               parties=(Party("lab-jurisdiction-qwen", "", ""),)),
        LabRow("tencent", "not_disclosed",
               "SEC submissions for Tencent Holdings Ltd describe incorporation in the Cayman "
               "Islands. The record does not state the PRC training entity's country of "
               "incorporation, so the lab set is null.",
               entity="Tencent Holdings Ltd",
               parties=(Party("lab-jurisdiction-tencent", "", ""),)),
        LabRow("typesafe", "not_disclosed",
               "TypeSafe terms name TypeSafe AI, Inc. and choose Delaware governing law. They "
               "do not state where the company is incorporated.",
               parties=(Party("lab-jurisdiction-typesafe", "", ""),)),
        LabRow("xai", "not_disclosed",
               "The consumer terms name SpaceXAI LLC, a Nevada company. They do not name a "
               "parent company. A SpaceX registration statement names X.AI Holdings and X.AI LLC, "
               "not SpaceXAI LLC, so it is not this entity's parent. The retained copy is the "
               "rendered page; a plain HTTP fetch returned 403.",
               entity="SpaceXAI LLC",
               parties=(Party("lab-jurisdiction-xai", "", ""),)),
        LabRow("zhipu", "not_disclosed",
               "Z.ai terms name JINGSHENG HENGXING TECHNOLOGY PTE.LTD, with a Singapore "
               "registered address, as the service provider. They do not state where the "
               "training lab is incorporated.",
               parties=(Party("lab-jurisdiction-zhipu", "", ""),)),
    )


def yaml_scalar(value: str) -> str:
    import json
    return json.dumps(value, ensure_ascii=False)


def atomic_write(path: Path, text: str) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def retain(fetch: Path, store) -> dict[str, str]:
    refs: dict[str, str] = {}
    for src in sources():
        path = fetch / src.file
        if not path.is_file():
            raise SystemExit(f"missing fetch file: {path}")
        refs[src.id] = store.put(path.read_bytes())
    return refs


def region_text(src: Src, body: bytes) -> str:
    from decision.normalise import NORMALISERS, Locator, normalise_document, select_region
    doc = normalise_document(body, NORMALISERS[src.normaliser])
    text = select_region(doc, Locator(src.kind, src.locator))
    if text is None or not text.strip():
        raise SystemExit(f"{src.id}: cited region is empty")
    return text


def check_regions(fetch: Path) -> dict[str, str]:
    from decision.labs import _null_url_problem
    from decision.verify import jurisdiction_codes
    by_id = {src.id: src for src in sources()}
    reports: dict[str, str] = {}
    for lab in labs():
        if lab.state == "gap":
            if lab.parties:
                raise SystemExit(f"{lab.id}: a gap has no source")
            continue
        if not lab.parties:
            raise SystemExit(f"{lab.id}: needs a source")
        found: set[str] = set()
        for party in lab.parties:
            src = by_id[party.source_id]
            text = region_text(src, (fetch / src.file).read_bytes())
            codes = jurisdiction_codes(text)
            reports[src.id] = f"{sorted(codes) or 'nothing'} ({len(text.strip())} chars)"
            if lab.state == "not_disclosed":
                problem = _null_url_problem(src.url)
                if problem:
                    raise SystemExit(f"{lab.id}: {problem}")
                continue
            if party.code not in codes:
                raise SystemExit(f"{lab.id}: {src.id} does not state {party.code} (read {sorted(codes)})")
            found |= set(codes)
        if lab.state == "known":
            expected = {party.code for party in lab.parties}
            extra = found - expected
            if extra or found != expected:
                raise SystemExit(f"{lab.id}: regions read {sorted(found)}, record is {sorted(expected)}")
    return reports


def render_labs(refs: dict[str, str]) -> str:
    lines = ["schema_version: 1", "labs:"]
    for lab in labs():
        lines.append(f"- id: {lab.id}")
        lines.append(f"  entity: {yaml_scalar(lab.entity) if lab.entity else 'null'}")
        if lab.state == "known":
            entity_code = next(party.code for party in lab.parties if party.role == "entity")
            lines.append(f"  entity_code: {entity_code}")
            if lab.parent_entity:
                parent_code = next(party.code for party in lab.parties if party.role == "parent")
                lines.append(f"  parent_entity: {yaml_scalar(lab.parent_entity)}")
                lines.append(f"  parent_code: {parent_code}")
        lines.append(f"  note: {yaml_scalar(lab.note)}")
        lines.append(f"  read_date: '{READ_DATE}'")
        lines.append("  jurisdiction:")
        lines.append(f"    state: {lab.state}")
        if lab.state == "known":
            codes = sorted({party.code for party in lab.parties})
            lines.append("    value:")
            lines.extend(f"    - {code}" for code in codes)
        else:
            lines.append("    value: null")
        if lab.state == "gap":
            continue
        lines.append("    sources:")
        for party in lab.parties:
            lines.append(f"    - source_id: {party.source_id}")
            lines.append(f"      snapshot_ref: {refs[party.source_id]}")
            lines.append("      cited_regions:")
            lines.append("      - incorporation")
            if party.role:
                lines.append(f"      party: {party.role}")
    return "\n".join(lines) + "\n"


def render_sources() -> str:
    lines = []
    for src in sources():
        lines.append(f"- id: {src.id}")
        lines.append(f"  url: {yaml_scalar(src.url)}")
        lines.append("  volatility: static")
        lines.append(f"  fetch: {src.fetch}")
        lines.append(f"  normaliser: {src.normaliser}")
        lines.append("  cited_regions:")
        lines.append("  - id: incorporation")
        lines.append("    locator:")
        lines.append(f"      kind: {src.kind}")
        lines.append(f"      value: {yaml_scalar(src.locator)}")
    return "\n".join(lines) + "\n"


def splice_sources(path: Path, block: str) -> None:
    text = path.read_text(encoding="utf-8")
    match = MARKER.search(text)
    if match is None:
        raise SystemExit(f"{path}: no lab-jurisdiction source block")
    rest = text[match.start():]
    ids = re.findall(r"(?m)^- id: (\S+)", rest)
    foreign = [item for item in ids if not item.startswith("lab-jurisdiction-")]
    if foreign:
        raise SystemExit(f"{path}: refusing to replace non-lab sources {foreign}")
    if not text[:match.start()].endswith("\n"):
        raise SystemExit(f"{path}: lab block does not start on its own line")
    atomic_write(path, text[:match.start()] + block)


def demote_cards(root: Path) -> list[str]:
    changed = []
    for rel in DEMOTE:
        path = root / rel
        text = path.read_text(encoding="utf-8")
        count = text.count(KNOWN_CARD)
        if count > 1:
            raise SystemExit(f"{rel}: jurisdiction block appears {count} times")
        if count == 1:
            atomic_write(path, text.replace(KNOWN_CARD, NULL_CARD, 1))
            changed.append(rel)
            continue
        if NULL_CARD not in text:
            raise SystemExit(f"{rel}: jurisdiction is neither known US nor not_disclosed")
    return changed


def file_claims(data: Path) -> int:
    from decision.labs import FACET, load_labs
    from decision.model import SourceRef, TargetRef, VerificationActor
    from decision.verify import Claim, Queue
    labs_now = load_labs(data)
    queue = Queue(data / "verification")
    collector = VerificationActor(agent="grok", model_family="grok", method="lab-registry@1")
    filed = 0
    for lab_id in sorted(labs_now):
        lab = labs_now[lab_id]
        if lab.state != "known" or lab.entity is None:
            continue
        fact = lab.fact()
        claim = Claim(
            target=TargetRef(kind="fact", id=fact["id"]),
            subject=f"lab:{lab.id}",
            names=(lab.entity,),
            field=FACET,
            value=fact["value"],
            collector=collector,
            sources=tuple(SourceRef.model_validate(source) for source in fact["sources"]),
        )
        queue.file(claim, at=FILED_AT)
        filed += 1
    return filed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--code", type=Path, required=True, help="ModelSpec code worktree")
    parser.add_argument("--data", type=Path, required=True, help="modelspec-data worktree")
    parser.add_argument("--fetch", type=Path, required=True, help="Directory of retained page bodies")
    parser.add_argument("--claims", action="store_true",
                        help="File known-lab claims after writing the registry")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    code = args.code.resolve()
    data = args.data.resolve()
    fetch = args.fetch.resolve()
    sys.path.insert(0, str(code))
    from decision.labs import load_labs
    from decision.sources import CopyStore, load_sources

    if not (code / "decision" / "labs.py").is_file():
        raise SystemExit(f"--code is not the ModelSpec tree: {code}")
    if not (data / "registry" / "sources.yaml").is_file():
        raise SystemExit(f"--data has no registry: {data}")
    reports = check_regions(fetch)
    store = CopyStore()
    refs = retain(fetch, store)
    atomic_write(data / "registry" / "labs.yaml", render_labs(refs))
    splice_sources(data / "registry" / "sources.yaml", render_sources())
    changed = demote_cards(data)
    load_sources(data / "registry" / "sources.yaml")
    loaded = load_labs(data, copy_store=store)
    known = sorted(lab_id for lab_id, lab in loaded.items() if lab.state == "known")
    nulls = sorted(lab_id for lab_id, lab in loaded.items() if lab.explicit_null)
    gaps = sorted(lab_id for lab_id, lab in loaded.items() if lab.state == "gap")
    print(f"copy store: {store.root}")
    print(f"known {len(known)}: {', '.join(known)}")
    print(f"explicit null {len(nulls)}: {', '.join(nulls)}")
    print(f"gap {len(gaps)}: {', '.join(gaps)}")
    for src in sources():
        print(f"  {src.id}: {reports[src.id]} {refs[src.id]}")
    print(f"cards demoted: {', '.join(changed) or 'none'}")
    if args.claims:
        print(f"claims filed: {file_claims(data)}")


if __name__ == "__main__":
    main()
