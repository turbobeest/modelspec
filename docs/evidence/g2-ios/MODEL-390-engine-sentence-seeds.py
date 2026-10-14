"""Derive reviewed sentence hashes offline; never print or save retained prose."""

import argparse
import gzip
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

import yaml

from decision.sources import CopyStore, load_sources
from decision.verify import StoredRegions, licence_sentence_hash, licence_sentences

DATA_SHA = "4bc5f4cfa9c1f29689aaf3142be22cabc44454db"
# Sentence positions are curator decisions in this exact data revision, not
# phrase searches. Only complete statements that support the filed value seed.
SEEDS = (
    ("model-390-gemini-api-terms", "gemini-api-terms", 81,
     "licence.output_training", "restricted", "Grounded-search output training restriction"),
    ("model-390-openai-services-agreement", "openai-services-agreement", 53,
     "licence.commercial_use", "permitted_with_conditions", "Customer access under agreement"),
    ("model-390-openai-services-agreement", "openai-services-agreement", 79,
     "licence.output_training", "restricted", "Competing-model output limits with exceptions"),
    ("model-390-typesafe-mca", "typesafe-mca", 33,
     "licence.commercial_use", "permitted_with_conditions", "Conditional customer/API licence"),
    ("model-390-typesafe-mca", "typesafe-mca", 40,
     "licence.output_training", "restricted", "Customer output distillation and imitation limits"),
    ("model-390-meta-api-terms", "meta-api-terms", 20,
     "licence.commercial_use", "permitted_with_conditions", "Conditional integrated-product grant"),
)


def refuse_network(event, _args):
    if event.startswith("socket."):
        raise RuntimeError("Sentence seeding is offline")


def derive(root):
    sys.addaudithook(refuse_network)
    revision = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"], check=True,
        capture_output=True, text=True,
    ).stdout.strip()
    if revision != DATA_SHA:
        raise ValueError("Sentence positions require the reviewed data revision")
    status = subprocess.run(
        ["git", "-C", str(root), "status", "--porcelain=v1", "--untracked-files=all"],
        check=True, capture_output=True, text=True,
    ).stdout.strip()
    if status:
        raise ValueError("Sentence seeding requires an unchanged data checkout")
    sources = load_sources(root / "registry/sources.yaml")
    refs = {}
    plan = json.loads((root / "research/model-390/resolution.json").read_text())
    for model in plan["models"]:
        path = root / "models" / (model["model"] + ".md")
        front = yaml.safe_load(path.read_text().split("---", 2)[1])
        for fact in front["facts"]:
            if fact["facet"] in model["values"]:
                for ref in fact.get("sources", []):
                    refs[ref["source_id"]] = ref
    manifest = json.loads((root / "research/model-390/http-manifest.json").read_text())
    result = []
    with TemporaryDirectory(prefix="model390-sentence-seeds-", dir="/tmp") as scratch:
        store = CopyStore(Path(scratch))
        for row in manifest:
            if "copy" not in row:
                continue
            body = gzip.decompress((root / row["copy"]).read_bytes())
            if hashlib.sha256(body).hexdigest() != row["sha256"]:
                raise ValueError("Retained bytes differ from their manifest")
            store.put(body)
        regions = StoredRegions(store, sources, cache_documents=True)
        for sid, family, index, facet, value, label in SEEDS:
            ref = refs[sid]
            text = regions.text(sid, ref["snapshot_ref"], ref["cited_regions"][0])
            sentences = licence_sentences(text)
            if index >= len(sentences):
                raise ValueError("The reviewed sentence position is absent")
            sentence = sentences[index]
            if not sentence.endswith("."):
                raise ValueError("A seed must be a complete declarative sentence")
            result.append({
                "source_family": family, "source_url": str(sources[sid].url),
                "region_sha256": licence_sentence_hash(text),
                # licence_sentences already returned normalised plain text.
                "sentence_sha256": hashlib.sha256(sentence.encode("utf-8")).hexdigest(),
                "facet": facet, "value": value, "label": label,
            })
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(derive(args.data.resolve()), indent=2))
