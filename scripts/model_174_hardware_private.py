#!/usr/bin/env python3
"""Collect MODEL-174 hardware-fit and private-deployment facts.

The retained projections make derived hardware results auditable: every row
contains the formula, verified parameter count, sourced device capacity, and
the fitting quantisations.  Read 2026-09-28.
"""

from __future__ import annotations

import json
import re
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from decision.hardware import DeviceInput, compute_fit
from decision.model import SourceRef, TargetRef, VerificationActor
from decision.sources import CopyStore, load_sources
from decision.verify import Claim, Queue

ROOT = Path(__file__).resolve().parents[1]
READ_DATE = "2026-09-28"
ME = VerificationActor(
    agent="codex-model-174",
    model_family="openai",
    method="retained-primary-source-projection@1",
)
USER_AGENT = "ModelSpec/1.0 (+https://modelspec.dev)"

HF_METADATA_URLS = {
    "deepseek/deepseek-flash":
        "https://huggingface.co/api/models/deepseek-ai/DeepSeek-V4.1-Flash",
    "deepseek/deepseek-v3-1":
        "https://huggingface.co/api/models/deepseek-ai/DeepSeek-V3.1",
    "google/gemma-4-26b-a4b-it":
        "https://huggingface.co/api/models/google/gemma-4-26b-a4b-it",
    "google/gemma-4-31b-it":
        "https://huggingface.co/api/models/google/gemma-4-31B-it",
    "google/gemma-4-e2b-it":
        "https://huggingface.co/api/models/google/gemma-4-E2B-it",
    "google/gemma-4-e4b-it":
        "https://huggingface.co/api/models/google/gemma-4-E4B-it",
    "microsoft/phi-4": "https://huggingface.co/api/models/microsoft/phi-4",
    "qwen/qwen3-embedding-8b":
        "https://huggingface.co/api/models/Qwen/Qwen3-Embedding-8B",
}

KNOWN_PRIVATE: dict[str, tuple[bool, str, str]] = {
    "azure-ai-foundry": (
        True,
        "provisioned throughput",
        "https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/provisioned-throughput-sizing",
    ),
    "aws-bedrock": (
        False,
        "not in the provider's exhaustive provisioned-throughput model table",
        "https://docs.aws.amazon.com/bedrock/latest/userguide/prov-thru-supported.html",
    ),
    "deepseek": (
        True,
        "self-host from the provider's open weights",
        "https://api-docs.deepseek.com/zh-cn/news/news260424/",
    ),
}
KNOWN_PRIVATE_BY_MODEL: dict[tuple[str, str], tuple[bool, str, str]] = {
    ("openai", "openai/gpt-5-4"): (
        True, "Scale Tier dedicated model capacity", "https://openai.com/api-scale-tier/"
    ),
    ("openai", "openai/gpt-5-6-sol"): (
        True, "Reserved Tier dedicated model capacity", "https://openai.com/api-reserved-tier/"
    ),
    ("google-vertex-ai", "google/gemini-3-8-flash"): (
        True,
        "Provisioned Throughput",
        "https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/gemini/3-8-flash",
    ),
    ("google-vertex-ai", "anthropic/claude-opus-5-5"): (
        True,
        "Provisioned Throughput",
        "https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/partner-models/claude/opus-5-5",
    ),
}


def fetch_json(url: str) -> dict[str, Any]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=180) as response:  # noqa: S310
        return json.load(response)


def projection(url: str, rows: list[dict[str, Any]], provenance: dict[str, Any]) -> bytes:
    return (json.dumps(
        {"source_url": url, "read_date": READ_DATE, "provenance": provenance, "rows": rows},
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ) + "\n").encode()


def source(source_id: str, url: str) -> dict[str, Any]:
    return {
        "id": source_id,
        "url": url,
        "fetch": "http",
        "normaliser": "text-default",
        "cited_regions": [{"id": "rows", "locator": {"kind": "page", "value": ""}}],
    }


def register(rows: list[dict[str, Any]]) -> None:
    path = ROOT / "registry/sources.yaml"
    known = load_sources(path)
    additions = [row for row in rows if row["id"] not in known]
    if not additions:
        return
    block = yaml.safe_dump(additions, sort_keys=False, allow_unicode=True, width=100)
    path.write_text(
        path.read_text(encoding="utf-8").rstrip("\n")
        + f"\n# MODEL-174: hardware fit and private deployment, read {READ_DATE}.\n"
        + block,
        encoding="utf-8",
    )
    load_sources(path)


def card_path(model_id: str) -> Path:
    lab, model = model_id.split("/", 1)
    return ROOT / "models" / lab / f"{model}.md"


def front(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8").split("---", 2)[1])


def replace_or_append_model_fact(path: Path, fact: dict[str, Any]) -> bool:
    text = path.read_text(encoding="utf-8")
    dumped = yaml.safe_dump([fact], sort_keys=False, allow_unicode=True, width=100).rstrip() + "\n"
    starts = [match.start() for match in re.finditer(r"(?m)^- (?:id|facet):", text)]
    starts.append(text.index("card_schema_version:"))
    bounds = None
    for start, end in zip(starts, starts[1:]):
        candidate = yaml.safe_load(text[start:end])
        if isinstance(candidate, list) and candidate[0].get("facet") == fact["facet"]:
            bounds = (start, end)
            break
    if bounds is None:
        at = text.index("card_schema_version:")
        updated = text[:at] + dumped + text[at:]
    else:
        updated = text[:bounds[0]] + dumped + text[bounds[1]:]
    updated = re.sub(r"(?m)^card_updated:.*$", f"card_updated: '{READ_DATE}'", updated)
    if updated == text:
        return False
    path.write_text(updated, encoding="utf-8")
    return True


def append_offering_fact(path: Path, fact: dict[str, Any]) -> bool:
    text = path.read_text(encoding="utf-8").rstrip("\n")
    if "facet: offering.private_deployment" in text:
        return False
    dumped = yaml.safe_dump([fact], sort_keys=False, allow_unicode=True, width=100).rstrip()
    path.write_text(text + "\n" + "\n".join(f"  {line}" for line in dumped.splitlines()) + "\n",
                    encoding="utf-8")
    return True


def fact_claim(subject: str, fact: dict[str, Any], names: tuple[str, ...], *,
               label: str, unit: str | None = None) -> Claim:
    return Claim(
        target=TargetRef(kind="fact", id=fact["id"]),
        subject=subject,
        names=tuple(dict.fromkeys(names)),
        field=fact["facet"],
        label=label,
        value=fact["value"],
        unit=unit,
        collector=ME,
        sources=tuple(SourceRef(**row) for row in fact["sources"]),
    )


def devices() -> tuple[list[DeviceInput], dict[str, dict[str, Any]]]:
    inputs: list[DeviceInput] = []
    provenance: dict[str, dict[str, Any]] = {}
    for path in sorted((ROOT / "hardware").glob("*.yaml")):
        if path.name == "_schema.yaml":
            continue
        row = yaml.safe_load(path.read_text(encoding="utf-8"))
        capacity = row.get("memory", {}).get("capacity_gb")
        if capacity is None:
            continue
        inputs.append(DeviceInput(
            id=row["id"],
            memory_capacity_gb=float(capacity),
            single_device_fit=row.get("single_device_fit", True),
            refusal_reason=row.get("single_device_fit_reason"),
        ))
        provenance[row["id"]] = {
            "memory_capacity_gb": capacity,
            "sources": row["sources"],
            "read_date": str(row["verified_at"]),
            "single_device_fit": row.get("single_device_fit", True),
            "refusal_reason": row.get("single_device_fit_reason"),
        }
    return inputs, provenance


def collect_hardware(store: CopyStore, registrations: list[dict[str, Any]],
                     claims: list[Claim]) -> None:
    lineup = yaml.safe_load((ROOT / "premier/slice-1.yaml").read_text())["models"]
    registered = load_sources(ROOT / "registry/sources.yaml")
    device_inputs, device_sources = devices()

    for lineup_row in lineup:
        model_id = lineup_row["model_id"]
        path = card_path(model_id)
        data = front(path)
        facts = data.get("facts") or []
        openness = next(row for row in facts if row["facet"] == "model.weights_openness")
        parameter_fact = next((row for row in facts if row["facet"] == "model.parameters_total"), None)
        parameter_needs_filing = parameter_fact is None or (
            parameter_fact["sources"][0]["source_id"].startswith("model-174-")
        )
        parameters = parameter_fact and int(parameter_fact["value"])
        metadata_url = HF_METADATA_URLS.get(model_id)

        if lineup_row["open_weights"] and parameters is None:
            if metadata_url is None:
                metadata_id = "model-143-hf-metadata-" + model_id.replace("/", "-")
                metadata_url = str(registered[metadata_id].url)
            safetensors = fetch_json(metadata_url)["safetensors"]
            # Some sharded repositories expose an index-entry count in ``total``;
            # the per-dtype parameter map remains the actual tensor census.
            parameters = sum(int(value) for value in safetensors["parameters"].values())
            architecture_total = int(data["architecture"]["total_parameters"])
            if parameters != architecture_total:
                raise RuntimeError(
                    f"{model_id}: Hugging Face {parameters} != card architecture {architecture_total}"
                )

        result = compute_fit(
            weights_openness=openness["value"],
            parameters_total=parameters,
            devices=device_inputs,
        )
        base_ref = parameter_fact["sources"][0] if parameter_fact else openness["sources"][0]
        base_url = metadata_url or str(registered[base_ref["source_id"]].url)
        source_id = "model-174-" + model_id.replace("/", "-") + "-hardware-fit"
        source_is_new = source_id not in registered
        fit_values = list(result.fits_hardware) if result.fits_hardware is not None else None
        device_rows = {
            device_id: {
                **device_sources[device_id],
                "fits": fit.fits,
                "best_quantisation": fit.best_quant,
                "fitting_quantisations": list(fit.quantisations),
                "weights_gb_at_best_quantisation": fit.weights_gb,
                "usable_memory_gb": fit.usable_memory_gb,
                "reason": fit.reason,
            }
            for device_id, fit in result.devices.items()
        }
        row: dict[str, Any] = {
            "model": data["display_name"],
            "fits_hardware": "none" if fit_values == [] else ", ".join(fit_values or []),
        }
        if parameters is not None:
            row["parameters_total"] = f"{parameters} parameters"
        body = projection(base_url, [row], {
            "formula": result.formula,
            "inputs": dict(result.inputs),
            "model_source": base_url,
            "devices": device_rows,
        })
        snapshot_ref = store.put(body)
        registrations.append(source(source_id, base_url))
        source_ref = [{
            "source_id": source_id,
            "snapshot_ref": snapshot_ref,
            "cited_regions": ["rows"],
        }]

        if parameter_needs_filing and parameters is not None:
            parameter_fact = {
                "id": f"{model_id}#model.parameters_total",
                "subject": {"kind": "model", "id": model_id},
                "facet": "model.parameters_total",
                "value": parameters,
                "state": "known",
                "sources": source_ref,
            }
            if replace_or_append_model_fact(path, parameter_fact) or source_is_new:
                claims.append(fact_claim(
                    model_id, parameter_fact,
                    (data["display_name"], model_id.rsplit("/", 1)[-1]),
                    label="parameters_total", unit="parameters",
                ))

        fit_fact = {
            "id": f"{model_id}#model.fits_hardware",
            "subject": {"kind": "model", "id": model_id},
            "facet": "model.fits_hardware",
            "value": fit_values,
            "state": "known" if fit_values is not None else "unknown",
        }
        if fit_values is None:
            fit_fact["checked_sources"] = [source_id]
        else:
            fit_fact["sources"] = source_ref
        changed = replace_or_append_model_fact(path, fit_fact)
        if fit_values is not None and (changed or source_is_new):
            claims.append(fact_claim(
                model_id, fit_fact, (data["display_name"], model_id.rsplit("/", 1)[-1]),
                label="fits_hardware",
            ))


def offering_paths() -> list[Path]:
    return sorted((ROOT / "offerings").glob("*/*/*.yaml"))


def collect_private_deployment(store: CopyStore, registrations: list[dict[str, Any]],
                               claims: list[Claim]) -> None:
    source_registry = load_sources(ROOT / "registry/sources.yaml")
    for path in offering_paths():
        rows = yaml.safe_load(path.read_text(encoding="utf-8"))
        for offering in rows:
            offering_id = (
                f"{offering['provider']}/{offering['model']}/"
                f"{offering['region']}/{offering['tier']}"
            )
            known = KNOWN_PRIVATE_BY_MODEL.get((offering["provider"], offering["model"]))
            known = known or KNOWN_PRIVATE.get(offering["provider"])
            fact: dict[str, Any] = {
                "id": f"{offering_id}#offering.private_deployment",
                "subject": {"kind": "offering", "id": offering_id},
                "facet": "offering.private_deployment",
                "value": None,
                "state": "unknown",
            }
            if known is None:
                checked = {
                    ref["source_id"]
                    for old_fact in offering.get("facts", [])
                    for key in ("sources",)
                    for ref in old_fact.get(key, [])
                    if ref["source_id"] in source_registry
                }
                checked.update(
                    source_id
                    for old_fact in offering.get("facts", [])
                    for source_id in old_fact.get("checked_sources", [])
                    if source_id in source_registry
                )
                if not checked:
                    raise RuntimeError(f"{offering_id}: no registered primary source to check")
                fact["checked_sources"] = sorted(checked)
            else:
                value, option, url = known
                source_id = "model-174-" + re.sub(r"[^a-z0-9]+", "-", offering_id).strip("-")
                source_is_new = source_id not in source_registry
                body = projection(url, [{
                    "model": offering_id,
                    "private_deployment": value,
                    "option": option,
                }], {"provider_statement": option})
                snapshot_ref = store.put(body)
                registrations.append(source(source_id, url))
                fact.update({
                    "value": value,
                    "state": "known",
                    "sources": [{
                        "source_id": source_id,
                        "snapshot_ref": snapshot_ref,
                        "cited_regions": ["rows"],
                    }],
                })
            changed = append_offering_fact(path, fact)
            if known is not None and (changed or source_is_new):
                claims.append(fact_claim(
                    offering_id,
                    fact,
                    (offering_id, offering["model"], offering["model"].rsplit("/", 1)[-1]),
                    label="private_deployment",
                ))


def main() -> None:
    store = CopyStore()
    registrations: list[dict[str, Any]] = []
    claims: list[Claim] = []
    collect_hardware(store, registrations, claims)
    collect_private_deployment(store, registrations, claims)
    register(registrations)
    queue = Queue(ROOT / "verification")
    filed_at = datetime.now(UTC)
    for claim in claims:
        queue.file(claim, at=filed_at)
    print(f"filed {len(claims)} claims from {len(registrations)} registered sources")


if __name__ == "__main__":
    main()
