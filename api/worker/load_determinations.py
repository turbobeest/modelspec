"""Load the private policy determinations into Workers KV (MODEL-80).

`POST /v1/policy-check` answers from two stores. One is public and lives in this
repository's export (`/api/policy/catalogue.json`). The other is the
determinations — `commercial_use` per model and `data_residency` per platform —
which are the paid product and are **never** in this repository, at any age, by
any route (`docs/business/decision-record.md` §2.2, §2.3). A Worker cannot read
a private git repository, so they are staged into Workers KV and the Worker
reads KV. This script is the only thing that writes them.

**It holds no data and no path to any.** Like `scripts/residency/determination.py`
it takes the store's location from its caller and defaults to nothing. It is
run from a checkout of the private repository, by whoever holds that checkout,
and it refuses outright to read a file from inside this repository or to write
its output into one — see `_refuse_repo_paths`. That refusal is the mechanical
half of the rule: prose in a decision record has never stopped a determination
being committed, and a `git add -A` in the wrong directory would publish the
whole product.

## What it writes

Three KV keys, and the order matters:

    determinations/commercial_use   one JSON object, model_id -> determination
    determinations/residency        one JSON object, platform -> determination
    determinations/manifest         written LAST; names the two, with the
                                    SHA-256 of each blob's exact bytes

The Worker reads the manifest first and verifies both blobs against it. A run
that dies halfway leaves a manifest describing the *previous* pair, so the
endpoint answers from a consistent snapshot or refuses — it never serves half a
load, and it never silently falls back to the free answer for a paid caller.

One key per model was considered and rejected: a policy check reads the whole
catalogue, and 1,339 KV reads per request is not an endpoint. Two blobs of
about a megabyte are two reads per cold isolate, cached for the isolate's life.

## Running it

    python load_determinations.py \\
        --commercial-use /path/to/private/enrichment/commercial_use.jsonl \\
        --residency      /path/to/private/enrichment/data_residency.jsonl \\
        --out            /some/scratch/dir

writes the three files and prints the `wrangler kv key put` commands. Add
`--put` to run them, which needs `CLOUDFLARE_API_TOKEN` with Workers KV
Storage:Edit and the namespace id in `--namespace-id` (or `wrangler.jsonc`'s
binding, via `--binding`).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

#: This repository. Anything under it is refused as both an input and an output.
REPO_ROOT = Path(__file__).resolve().parents[2]

#: Bumped when the blob shape changes incompatibly. The Worker refuses a bundle
#: it does not recognise rather than reading unfamiliar fields as absences.
BUNDLE_VERSION = "1"

KEY_COMMERCIAL_USE = "determinations/commercial_use"
KEY_RESIDENCY = "determinations/residency"
KEY_MANIFEST = "determinations/manifest"

#: Fields copied out of a `schema.enrichment.EnrichmentRecord`. Everything the
#: endpoint needs to give an answer it can defend, and nothing else: no
#: `determined_by`, because who made a call is internal, and no `published`,
#: because a record in this bundle is by definition not published.
_SOURCE_FIELDS = ("kind", "url", "read_on", "quote")


class LoadError(RuntimeError):
    """A refusal. Every one of these is a place the product could have leaked."""


def _refuse_repo_paths(path: Path, what: str) -> Path:
    """Never read determinations from, or write them into, the public repo."""
    resolved = path.resolve()
    if resolved == REPO_ROOT or REPO_ROOT in resolved.parents:
        raise LoadError(
            f"{what} is inside the public ModelSpec repository ({resolved}). "
            "Policy determinations are the paid product and never live here — "
            "decision-record.md §2.2. Point this at the private checkout.")
    return resolved


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    records = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            record = json.loads(line)
        except ValueError as exc:
            raise LoadError(f"{path}:{number} is not valid JSON: {exc}") from exc
        if not isinstance(record, dict):
            raise LoadError(f"{path}:{number} is not a JSON object")
        records.append(record)
    return records


def _source(raw: Any, where: str) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise LoadError(f"{where} has no source. A determination cites the document "
                        "it was read from, or it is an opinion.")
    source = {field: raw.get(field) or "" for field in _SOURCE_FIELDS}
    if source["kind"] == "legacy-import":
        raise LoadError(f"{where} carries a 'legacy-import' source, which is the "
                        "admission that nothing was read. schema/enrichment.py "
                        "forbids it and so does this.")
    if not source["url"] or not source["read_on"]:
        raise LoadError(f"{where} cites no url or no read date. An answer that "
                        "cannot be rechecked on the day it is questioned is not "
                        "an answer.")
    return source


def commercial_use_blob(records: list[dict[str, Any]]) -> dict[str, Any]:
    """`model_id -> determination`, from `EnrichmentRecord` lines.

    Only `commercial_use` records are taken. A `data_residency` record keyed by
    model would be the per-card residency MODEL-79 exists to prevent, so one in
    this file is an error rather than something to route elsewhere.
    """
    out: dict[str, Any] = {}
    for record in records:
        model_id = record.get("model_id")
        if not model_id:
            raise LoadError(f"a record has no model_id: {record!r:.120}")
        field = record.get("field")
        if field != "commercial_use":
            raise LoadError(
                f"{model_id}: this file is the commercial_use store and the record "
                f"says field={field!r}. Residency is determined per platform, not "
                "per model (MODEL-79); it does not belong here.")
        value = record.get("commercial_use")
        if value not in ("allowed", "restricted", "prohibited"):
            raise LoadError(
                f"{model_id}: commercial_use is {value!r}. A record exists because "
                "something was decided; 'unspecified' and 'withheld' describe a "
                "public card's contents, not a determination.")
        conditions = (record.get("conditions") or "").strip()
        if value == "restricted" and not conditions:
            raise LoadError(
                f"{model_id}: a 'restricted' grant with no conditions. "
                "'Allowed unless you exceed 700M monthly active users' is the "
                "answer a buyer pays for; 'restricted' on its own is not.")
        if model_id in out:
            raise LoadError(f"{model_id}: two commercial_use determinations. The "
                            "store would answer with whichever was written last.")
        out[model_id] = {
            "value": value,
            "conditions": conditions,
            "source": _source(record.get("source"), f"{model_id} commercial_use"),
            "determined_on": record.get("determined_on") or "",
        }
    return out


def _documents(checked: Any, determined_on: str, where: str) -> list[dict[str, str]]:
    """URLs that were read, each with the date the finding attaches to them.

    The store records `checked` as URL strings and one `determined_on` for the
    finding. Per-document read dates were not stored; inventing a different
    day is forbidden, so each document carries `determined_on`.
    """
    if checked is None:
        return []
    if not isinstance(checked, list):
        raise LoadError(f"{where}: checked must be a list of URLs")
    out: list[dict[str, str]] = []
    for item in checked:
        if isinstance(item, str):
            url, read_on = item.strip(), determined_on
        elif isinstance(item, dict):
            url = str(item.get("url") or "").strip()
            read_on = str(item.get("read_on") or determined_on or "").strip()
        else:
            raise LoadError(f"{where}: a checked document is not a URL")
        if not url:
            raise LoadError(f"{where}: a checked document has no URL")
        if not read_on:
            raise LoadError(
                f"{where}: {url} has no read date. A finding that cannot be "
                "rechecked on the day it is questioned is not an answer.")
        out.append({"url": url, "read_on": read_on})
    return out


def residency_blob(records: list[dict[str, Any]]) -> dict[str, Any]:
    """`platform -> determination`, from `PlatformResidency` lines.

    `undetermined` platforms are carried, not dropped. "Three documents were
    read and none of them publishes a region list" is a researched answer and
    the endpoint reports it as one; dropping those rows would make it
    indistinguishable from a platform nobody has looked at.

    A `no-commitment` finding is the paid-tier answer for a withheld card that
    has no region list: the documents, the day they were used, and what they
    said instead. The loader refuses one that cannot name those, because a
    withheld card with nothing behind it is the product handing a customer
    silence.

    An `unbounded` platform is refused, exactly as `determination.py` refuses to
    write one: a local runtime's residency is a property of the operator's
    machine, and a record here would be a region list attached to Ollama.
    """
    out: dict[str, Any] = {}
    for record in records:
        platform = record.get("platform")
        if not platform:
            raise LoadError(f"a residency record has no platform: {record!r:.120}")
        scope = record.get("scope")
        if scope == "unbounded":
            raise LoadError(
                f"{platform}: an 'unbounded' residency record. A local runtime's "
                "residency is wherever the operator put the machine; no region "
                "list can be true of it, so no record is stored for it.")
        if scope not in ("determined", "undetermined"):
            raise LoadError(f"{platform}: unknown residency scope {scope!r}")
        if platform in out:
            raise LoadError(f"{platform}: two residency determinations")
        determined_on = record.get("determined_on") or ""
        non_disclosure = record.get("non_disclosure") or None
        documents = _documents(record.get("checked"), determined_on, f"{platform} residency")
        entry: dict[str, Any] = {
            "scope": scope,
            "regions": None,
            "source": None,
            "reason": (record.get("reason") or "").strip(),
            "checked": [d["url"] for d in documents],
            "documents": documents,
            "non_disclosure": non_disclosure,
            "determined_on": determined_on,
            "notes": (record.get("notes") or "").strip(),
        }
        if scope == "determined":
            regions = record.get("regions")
            if regions is None or not isinstance(regions, list):
                raise LoadError(
                    f"{platform}: scope is 'determined' but regions is {regions!r}. "
                    "An empty list is a determination ('commits to no region'); "
                    "null is not an answer at all.")
            entry["regions"] = [str(r) for r in regions]
            entry["source"] = _source(record.get("source"), f"{platform} residency")
        if non_disclosure == "no-commitment":
            if not documents or not entry["reason"]:
                raise LoadError(
                    f"{platform}: a no-commitment finding must name the documents "
                    "that were read and what they said instead of a region list. "
                    "A withheld card with nothing behind it is silence.")
        out[platform] = entry
    return out


def _blob(kind: str, payload: dict[str, Any], generated_on: str) -> str:
    """One KV value, serialised exactly once so its hash describes its bytes."""
    return json.dumps(
        {"bundle_version": BUNDLE_VERSION, "kind": kind,
         "generated_on": generated_on, "count": len(payload), kind: payload},
        sort_keys=True, separators=(",", ":"))


def build(commercial_use: Path, residency: Path,
          generated_on: str | None = None) -> dict[str, str]:
    """Read both JSONL files and return `{key: serialised value}`.

    The manifest is last in the mapping and must be written last: it is what
    makes a half-finished load invisible to the endpoint.
    """
    stamp = generated_on or datetime.now(UTC).date().isoformat()
    cu = commercial_use_blob(_read_jsonl(commercial_use))
    res = residency_blob(_read_jsonl(residency))
    cu_text = _blob("commercial_use", cu, stamp)
    res_text = _blob("residency", res, stamp)
    manifest = json.dumps({
        "bundle_version": BUNDLE_VERSION,
        "generated_on": stamp,
        "blobs": {
            KEY_COMMERCIAL_USE: {
                "sha256": hashlib.sha256(cu_text.encode("utf-8")).hexdigest(),
                "bytes": len(cu_text.encode("utf-8")), "count": len(cu)},
            KEY_RESIDENCY: {
                "sha256": hashlib.sha256(res_text.encode("utf-8")).hexdigest(),
                "bytes": len(res_text.encode("utf-8")), "count": len(res)},
        },
    }, sort_keys=True, separators=(",", ":"))
    return {KEY_COMMERCIAL_USE: cu_text, KEY_RESIDENCY: res_text, KEY_MANIFEST: manifest}


def _file_for(key: str) -> str:
    return key.replace("/", "__") + ".json"


def write_files(blobs: dict[str, str], out: Path) -> list[Path]:
    out.mkdir(parents=True, exist_ok=True)
    written = []
    for key, text in blobs.items():
        path = out / _file_for(key)
        path.write_text(text, encoding="utf-8")
        written.append(path)
    return written


def put_commands(blobs: dict[str, str], out: Path, namespace_id: str | None,
                 binding: str | None, remote: bool) -> list[list[str]]:
    """The `wrangler kv key put` invocations, manifest last."""
    target = (["--namespace-id", namespace_id] if namespace_id
              else ["--binding", binding or "DETERMINATIONS"])
    scope = ["--remote"] if remote else []
    return [
        ["npx", "wrangler", "kv", "key", "put", key,
         "--path", str(out / _file_for(key)), *target, *scope]
        for key in blobs
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--commercial-use", required=True, type=Path,
                        help="commercial_use.jsonl from the private enrichment store")
    parser.add_argument("--residency", required=True, type=Path,
                        help="data_residency.jsonl from the private enrichment store")
    parser.add_argument("--out", required=True, type=Path,
                        help="scratch directory for the blobs; must be outside this repo")
    parser.add_argument("--namespace-id", default=None,
                        help="KV namespace id (otherwise the Worker binding is used)")
    parser.add_argument("--binding", default="DETERMINATIONS")
    parser.add_argument("--generated-on", default=None,
                        help="override the bundle date (ISO); defaults to today, UTC")
    parser.add_argument("--local", action="store_true",
                        help="target the local KV simulator instead of Cloudflare")
    parser.add_argument("--put", action="store_true",
                        help="run the wrangler commands instead of only printing them")
    args = parser.parse_args(argv)

    try:
        commercial_use = _refuse_repo_paths(args.commercial_use, "--commercial-use")
        residency = _refuse_repo_paths(args.residency, "--residency")
        out = _refuse_repo_paths(args.out, "--out")
        blobs = build(commercial_use, residency, args.generated_on)
    except LoadError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    write_files(blobs, out)
    manifest = json.loads(blobs[KEY_MANIFEST])
    print(f"bundle {manifest['bundle_version']} generated_on {manifest['generated_on']}")
    for key, meta in manifest["blobs"].items():
        print(f"  {key}: {meta['count']} records, {meta['bytes']} bytes, "
              f"sha256 {meta['sha256'][:12]}…")
    print(f"staged in {out}")

    commands = put_commands(blobs, out, args.namespace_id, args.binding, not args.local)
    if not args.put:
        print("\nrun these from api/worker/ (manifest LAST — it is what makes a "
              "half-finished load invisible):")
        for command in commands:
            print("  " + " ".join(command))
        return 0

    if shutil.which("npx") is None:
        print("error: --put needs npx on PATH", file=sys.stderr)
        return 1
    for command in commands:
        print("+ " + " ".join(command))
        result = subprocess.run(command, cwd=Path(__file__).resolve().parent, check=False)
        if result.returncode != 0:
            # Stopping here leaves the manifest describing the previous pair,
            # which is the whole point of writing it last.
            print(f"error: {command[5]} failed; the manifest was not advanced, so the "
                  "endpoint is still answering from the previous bundle",
                  file=sys.stderr)
            return result.returncode
    print("loaded")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
