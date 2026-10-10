#!/usr/bin/env python3
"""Collect deterministic HF architecture facts for open weights (MODEL-348).

Only modelspec verify writes outcomes. Dry runs retain HTTP copies and an
optional report, but never write to the data checkout. Configs and READMEs
are pinned to the API's commit SHA when available; main is the fallback.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlsplit

import yaml

from decision.model import CitedRegion, Fact, Source, SourceRef, TargetRef, VerificationActor
from decision.sources import CopyStore, Fetcher, load_sources, recheck
from decision.verify import (
    DENSE_ARCHITECTURES,
    Claim,
    DenseActiveEqualsTotalExtractor,
    HFConfigExtractor,
    HFParametersExtractor,
    ModelCardParamsExtractor,
    Queue,
    StoredRegions,
    VerificationLog,
    _hf_config,
    _nontext_tower,
    active_parameter_wording,
    hf_config_architecture,
    verify,
)
from scripts.policy.architecture_coverage import EXPERT_FACETS, FACETS
from scripts.policy.licence_coverage import _verified, open_weights_lineup

COLLECTOR = VerificationActor(
    agent="model-348-collector", model_family="openai", method="retained-hf-architecture@1"
)
READERS = (
    HFConfigExtractor(),
    HFParametersExtractor(),
    ModelCardParamsExtractor(),
    DenseActiveEqualsTotalExtractor(),
)
LEGACY = {
    "model.architecture": "type",
    "model.parameters_total": "total_parameters",
    "model.parameters_active": "active_parameters",
    "model.experts_total": "num_experts",
    "model.experts_per_token": "experts_per_token",
}


def _absence_reason(facet: str, pages: list[tuple[str, str]], reason: str | None = None) -> str:
    if reason == "retained_config_required":
        return (
            "no retained config.json; trimmed API metadata "
            "and README cannot establish config absence"
        )
    if reason == "non_dense_config_required":
        return "cited retained config does not establish a MoE, hybrid or SSM architecture"
    if reason == "retained_readme_required":
        return "no retained README to check for active or effective parameter wording"
    if reason == "retained_census_required":
        return "no cited retained HF API parameter census to establish active-parameter absence"
    if facet == "model.parameters_active":
        multimodal = any(
            (config := _hf_config(text)) is not None
            and hf_config_architecture(config) in DENSE_ARCHITECTURES
            and _nontext_tower(config)
            for text, url in pages if url.endswith("/config.json")
        )
        if multimodal:
            details = [
                line.strip() for text, url in pages if url.endswith("/README.md")
                for line in text.splitlines()
                if re.search(r"total parameters|(?:vision|audio).*encoder.*parameters", line, re.I)
            ]
            return (
                "no explicit active count for this variant; non-text encoder parameters "
                "in the census prevent dense equality; retained card total and encoder counts: "
                + "\n".join(details)
            )
        quotes = [
            quote
            for text, url in pages
            if url.endswith("/README.md")
            for quote in active_parameter_wording(text)
        ]
        if quotes:
            return (
                "active/effective parameter wording has no single bound scalar reading; quotes: "
                + "\n".join(quotes)
            )
        return "no explicit active-parameter reading for this model; dense equality does not apply"
    if facet in EXPERT_FACETS:
        return "config does not disclose a uniform routed-expert count under the registered rules"
    return "no explicit reading under the deterministic HF rules"


def _front(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n") or len(text.split("---", 2)) != 3:
        raise ValueError(f"{path}: no front matter")
    return yaml.safe_load(text.split("---", 2)[1]) or {}, text


def _repo(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    if re.fullmatch(r"[\w.-]+/[\w.-]+", value):
        return value
    url = urlsplit(value)
    if url.hostname != "huggingface.co" or url.scheme != "https":
        return None
    parts = url.path.strip("/").split("/")
    if parts[:2] == ["api", "models"]:
        parts = parts[2:]
    if len(parts) >= 2 and all(re.fullmatch(r"[\w.-]+", part) for part in parts[:2]):
        return "/".join(parts[:2])
    return None


def resolve_repo(front: dict, sources: dict[str, Source]) -> tuple[str | None, Source | None]:
    """Resolve only card HF fields and the total fact's existing HF API citation."""
    candidates = []
    api = None
    total = next(
        (f for f in front.get("facts", []) if f.get("facet") == "model.parameters_total"), {}
    )
    for ref in total.get("sources", []):
        source = sources.get(ref.get("source_id"))
        if source is not None and str(source.url).startswith("https://huggingface.co/api/models/"):
            candidates.append(_repo(str(source.url)))
            api = source
    hf = (front.get("availability") or {}).get("huggingface") or {}
    candidates.extend(
        _repo(value)
        for value in (
            hf.get("model_id"),
            hf.get("url"),
            (front.get("sources") or {}).get("huggingface_url"),
        )
    )

    def card_links(value):
        if isinstance(value, dict):
            for child in value.values():
                card_links(child)
        elif isinstance(value, list):
            for child in value:
                card_links(child)
        elif isinstance(value, str):
            repo = _repo(value)
            if repo is not None:
                candidates.append(repo)

    for key in ("huggingface", "links"):
        card_links(front.get(key))
    candidates = [repo for repo in candidates if repo]
    if len({repo.casefold() for repo in candidates}) != 1:
        return None, None
    return candidates[0], api


def _source(source_id: str, url: str) -> Source:
    return Source(
        id=source_id,
        url=url,
        fetch="http",
        normaliser="text-default" if url.endswith("/README.md") else "json-default",
        kind="weights_repository",
        cited_regions=[
            CitedRegion(id="page", locator={"kind": "page", "value": ""}),
        ],
    )


def _register(path: Path, wanted: dict[str, Source]) -> None:
    text = path.read_text(encoding="utf-8")
    registered = load_sources(path)
    additions = []
    for sid, source in wanted.items():
        old = registered.get(sid)
        if old is None:
            additions.append(source.model_dump(mode="json", exclude_defaults=True))
        elif str(old.url) != str(source.url):
            raise ValueError(f"{sid}: registered URL disagrees")
        elif old.kind is None and source.kind is not None:
            match = re.search(rf"(?m)^\s*- id: {re.escape(sid)}\s*$", text)
            if match is None:
                raise ValueError(f"{sid}: cannot locate registered source")
            text = text[: match.end()] + f"\n  kind: {source.kind}" + text[match.end() :]
    if additions:
        text = (
            text.rstrip("\n")
            + "\n# MODEL-348 retained HF architecture sources.\n"
            + yaml.safe_dump(additions, sort_keys=False, allow_unicode=True)
        )
    path.write_text(text, encoding="utf-8")
    load_sources(path)


def _block(text: str, key: str) -> tuple[int, int] | None:
    match = re.search(rf"(?m)^{key}:.*\n", text)
    if match is None:
        return None
    following = re.search(r"(?m)^(?:[A-Za-z_][\w]*:|---\s*$)", text[match.end() :])
    end = match.end() + following.start() if following else len(text)
    return match.start(), end


def _updated_card(text: str, facts: list[Fact], architecture: dict, read_on: str) -> str:
    bounds = _block(text, "facts")
    if bounds is None:
        raise ValueError("card has no facts block")
    start, end = bounds
    block = text[start:end]
    starts = [m.start() for m in re.finditer(r"(?m)^- (?:id|facet):", block)] + [len(block)]
    kept = block[: starts[0]]
    for left, right in zip(starts, starts[1:]):
        row = yaml.safe_load(block[left:right])
        if row[0].get("facet") not in FACETS:
            kept += block[left:right]
    rows = [
        fact.model_dump(mode="json", exclude={"id", "subject", "verification"}, exclude_none=True)
        for fact in facts
    ]
    for row in rows:
        if not row.get("checked_sources"):
            row.pop("checked_sources", None)
    text = (
        text[:start] + kept + yaml.safe_dump(rows, sort_keys=False, allow_unicode=True) + text[end:]
    )
    bounds = _block(text, "architecture")
    if bounds is None:
        raise ValueError("card has no architecture block")
    start, end = bounds
    text = (
        text[:start] + yaml.safe_dump({"architecture": architecture}, sort_keys=False) + text[end:]
    )
    return re.sub(r"(?m)^card_updated:.*$", f"card_updated: '{read_on}'", text)


def collect(
    root: Path,
    *,
    dry_run: bool,
    report_path: Path | None = None,
    fetcher: Fetcher | None = None,
    store: CopyStore | None = None,
) -> dict:
    root = root.resolve()
    if not dry_run and root == Path(__file__).resolve().parents[1]:
        raise ValueError("fresh facts belong in modelspec-data; use --dry-run for the engine image")
    now = datetime.now(UTC)
    registered = load_sources(root / "registry" / "sources.yaml")
    wanted = {}
    log = VerificationLog(root / "verification").latest()
    store = store or CopyStore(report_path.parent / "sources" if dry_run and report_path else None)
    if dry_run and (
        store.root.resolve().is_relative_to(root)
        or (report_path is not None and report_path.resolve().is_relative_to(root))
    ):
        raise ValueError("dry-run reports and retained copies must be outside the data checkout")
    fetcher = fetcher or Fetcher(timeout=30.0, retries=1, min_host_interval=0.4)
    prepared, rows, unresolved, problems = [], [], [], []
    for model_id in open_weights_lineup(root / "premier" / "slice-1.yaml"):
        path = root / "models" / f"{model_id}.md"
        front, card = _front(path)
        if front.get("model_id") != model_id:
            raise ValueError(f"{path}: wrong model_id")
        repo, api = resolve_repo(front, registered)
        if repo is None:
            unresolved.append(
                {
                    "model_id": model_id,
                    "reason": "no unique HF repo in card fields or total citation",
                }
            )
            continue
        prefix = "model-348-" + model_id.replace("/", "-")
        api = (
            api.model_copy(update={"kind": "weights_repository"})
            if api is not None
            else _source(prefix + "-hf-api", f"https://huggingface.co/api/models/{repo}")
        )
        fetched = recheck([api], {}, [], fetcher=fetcher, store=store, now=now)
        snap = fetched.states[api.id].snapshot
        api_text = (
            StoredRegions(store, {api.id: api}).text(
                api.id,
                snap.copy_ref,
                api.cited_regions[0].id,
            )
            if snap is not None
            else None
        )
        metadata = json.loads(api_text) if api_text else {}
        sha = metadata.get("sha")
        revision = sha if isinstance(sha, str) and re.fullmatch(r"[0-9a-f]{40}", sha) else "main"
        config = _source(
            prefix + "-config-" + revision[:12],
            f"https://huggingface.co/{repo}/resolve/{revision}/config.json",
        )
        readme = _source(
            prefix + "-readme-" + revision[:12],
            f"https://huggingface.co/{repo}/raw/{revision}/README.md",
        )
        files = recheck([config, readme], {}, [], fetcher=fetcher, store=store, now=now)
        all_sources = {s.id: s for s in (api, config, readme)}
        wanted.update(all_sources)
        states = {**fetched.states, **files.states}
        regions = StoredRegions(store, all_sources)
        pages, refs, failures = [], {}, {}
        for sid, source in all_sources.items():
            snapshot = states[sid].snapshot
            if snapshot is None:
                failures[sid] = next(
                    (r.detail for r in (*fetched.regions, *files.regions) if r.source_id == sid),
                    "no retained copy",
                )
                continue
            text = regions.text(sid, snapshot.copy_ref, source.cited_regions[0].id)
            if text is not None:
                pages.append((text, str(source.url)))
                refs[str(source.url)] = SourceRef(
                    source_id=sid,
                    snapshot_ref=snapshot.copy_ref,
                    cited_regions=[source.cited_regions[0].id],
                )
        if not pages:
            unresolved.append(
                {
                    "model_id": model_id,
                    "reason": "no retained public HF source",
                    "failures": failures,
                }
            )
            continue
        names = tuple(
            dict.fromkeys(
                name
                for name in (
                    front.get("display_name"),
                    model_id.rsplit("/", 1)[-1],
                    repo,
                    repo.rsplit("/", 1)[-1],
                )
                if isinstance(name, str) and name.strip()
            )
        )
        existing = {f["facet"]: f for f in front.get("facts", [])}
        architecture = dict(front.get("architecture") or {})
        filed = []
        dense = False
        for facet in FACETS:
            if facet in EXPERT_FACETS and dense:
                prior = architecture.get(LEGACY[facet])
                if prior is not None:
                    print(f"DISAGREE {model_id} architecture.{LEGACY[facet]} {prior} -> None")
                architecture[LEGACY[facet]] = None
                rows.append(
                    {
                        "model_id": model_id,
                        "facet": facet,
                        "state": "dense_exempt",
                        "value": None,
                        "reason": "dense backbone needs no expert facts after verification",
                        "previous_value": prior,
                        "disagreement": prior is not None,
                        "repo": repo,
                    }
                )
                continue
            template = Claim(
                target=TargetRef(kind="fact", id=f"{model_id}#{facet}"),
                subject=model_id,
                names=names,
                field=facet,
                value=None,
                collector=COLLECTOR,
                sources=tuple(refs.values()),
            )
            readings, citations, methods = [], [], []
            for text, url in pages:
                for reader in READERS:
                    if facet not in reader.fields or not reader.accepts(text):
                        continue
                    found = reader.extract(template, text, page_url=url, bindings=pages)
                    if found:
                        readings.extend(found)
                        citations.append(refs[url])
                        methods.append(reader.actor.method)
                        if (
                            isinstance(
                                reader, (DenseActiveEqualsTotalExtractor, ModelCardParamsExtractor)
                            )
                            and str(api.url) in refs
                        ):
                            citations.append(refs[str(api.url)])
                        if (
                            isinstance(reader, DenseActiveEqualsTotalExtractor)
                            and str(readme.url) in refs
                        ):
                            citations.append(refs[str(readme.url)])
            values = {r.value for r in readings}
            ambiguous_active = facet == "model.parameters_active" and len(values) > 1
            if len(values) > 1 and not ambiguous_active:
                problems.append(f"{model_id} {facet}: retained readings disagree: {sorted(values)}")
            value = readings[0].value if readings and not ambiguous_active else None
            old = existing.get(facet) or {}
            if facet == "model.parameters_total" and old.get("state") == "known":
                if not _verified(log, model_id, facet, old.get("value")):
                    problems.append(f"{model_id}: total parameter fact is not verified")
                if value != old.get("value"):
                    problems.append(
                        f"{model_id}: retained API total {value} "
                        f"!= verified total {old.get('value')}"
                    )
            if (
                facet == "model.parameters_active"
                and "dense-active-equals-total@1" in methods
                and not _verified(log, model_id, "model.parameters_total", value)
            ):
                problems.append(f"{model_id}: dense active parameters require a verified total")
            cited = (
                list({ref.source_id: ref for ref in citations}.values())
                if value is not None
                else list(refs.values())
            )
            fact = Fact(
                id=f"{model_id}#{facet}",
                subject={"kind": "model", "id": model_id},
                facet=facet,
                value=value,
                state="known" if value is not None else "not_disclosed",
                sources=cited,
                checked_sources=list(all_sources) if value is None else [],
            )
            unit = (
                None
                if facet == "model.architecture"
                else "experts"
                if facet in EXPERT_FACETS
                else "parameters"
            )
            claim = Claim.from_fact(fact, names=names, collector=COLLECTOR, unit=unit)
            checked = verify(claim, regions, READERS, today=now.date())
            gap = value is None and checked.outcome != "verified"
            if checked.outcome != "verified" and not gap:
                problems.append(
                    f"{model_id} {facet}: retained-copy check {checked.outcome}: {checked.reason}"
                )
            prior = architecture.get(LEGACY[facet])
            disagreement = prior is not None and prior != value
            if disagreement:
                print(f"DISAGREE {model_id} architecture.{LEGACY[facet]} {prior} -> {value}")
            if old.get("state") == "known" and old.get("value") != value:
                print(f"DISAGREE {model_id} {facet} {old.get('value')} -> {value}")
            architecture[LEGACY[facet]] = value
            if facet == "model.architecture":
                dense = value in DENSE_ARCHITECTURES
            if not gap:
                filed.append((fact, claim))
            rows.append(
                {
                    "model_id": model_id,
                    "facet": facet,
                    "state": "missing" if gap else fact.state,
                    "value": value,
                    "previous_value": prior,
                    "disagreement": disagreement,
                    "repo": repo,
                    "revision": revision,
                    "methods": sorted(set(methods)),
                    "sources": [
                        {**ref.model_dump(), "url": str(all_sources[ref.source_id].url)}
                        for ref in cited
                    ],
                    "checked_sources": list(all_sources),
                    "failures": failures,
                    "reason": _absence_reason(facet, pages, checked.reason)
                    if value is None
                    else None,
                }
            )
        prepared.append(
            (
                path,
                _updated_card(card, [f for f, _ in filed], architecture, now.date().isoformat()),
                filed,
            )
        )
        print(
            f"{model_id}: {architecture['type'] or 'gap'}, "
            f"active={architecture['active_parameters']}, rev={revision}"
        )
    payload = {
        "read_on": now.date().isoformat(),
        "dry_run": dry_run,
        "rows": rows,
        "unresolved": unresolved,
        "problems": problems,
        "copy_store": str(store.root),
    }
    if report_path is not None:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
    if problems or (unresolved and not dry_run):
        raise ValueError(
            "refusing to file HF facts: " + "; ".join(problems or [r["reason"] for r in unresolved])
        )
    if dry_run:
        print(
            f"dry-run: {len(rows)} facet decisions, {len(unresolved)} unresolved models; "
            "data checkout unchanged"
        )
        return payload
    _register(root / "registry" / "sources.yaml", wanted)
    queue = Queue(root / "verification")
    for path, card, filed in prepared:
        path.write_text(card, encoding="utf-8")
        for _, claim in filed:
            queue.file(claim, at=now)
    print(f"filed {sum(len(filed) for _, _, filed in prepared)} facts for {len(prepared)} models")
    return payload


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args(argv)
    collect(args.root, dry_run=args.dry_run, report_path=args.report)


if __name__ == "__main__":
    main()
