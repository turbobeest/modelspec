#!/usr/bin/env python3
"""File MODEL-163 local-fit inputs for independent deterministic verification."""

from __future__ import annotations

import json
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

import yaml

from decision.model import SourceRef, TargetRef, VerificationActor
from decision.sources import CopyStore, load_sources
from decision.verify import Claim, Queue


ROOT = Path(__file__).resolve().parents[1]
FILED_AT = datetime(2026, 9, 26, 20, tzinfo=UTC)
COLLECTOR = VerificationActor(
    agent="openai-codex-model-163",
    model_family="gpt-5",
    method="hugging-face-api-projection@1",
)


def _fetch_json(url: str) -> object:
    request = urllib.request.Request(url, headers={"User-Agent": "ModelSpec/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def _source_id(model_id: str, kind: str) -> str:
    return "model-163-local-" + model_id.replace("/", "-").lower() + f"-{kind}"


def main() -> None:
    document = yaml.safe_load(
        (ROOT / "premier" / "inputs" / "slice-2.yaml").read_text()
    )
    rows = document["local"]["candidates"]
    sources = load_sources(ROOT / "registry" / "sources.yaml")
    store = CopyStore()
    queue = Queue(ROOT / "verification")

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
            ("artifact", "quantised_size_bytes", row["published_size_bytes"], None, row["size_source_url"]),
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
                "model.parameters_total" if kind == "parameters"
                else "local.quantised_size_bytes"
            )
            queue.file(
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
                ),
                at=FILED_AT,
            )
    print(f"filed {len(rows) * 2} local-fit facts from {len(rows) * 2} API reads")


if __name__ == "__main__":
    main()
