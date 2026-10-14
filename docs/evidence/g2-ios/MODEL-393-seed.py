"""Reproduce the reviewed Meta sentence hash from private retained HTTP bytes.

No source text is printed or retained in the public checkout. --check exercises
production readings and adversarial edits against those same private bytes.
"""

import argparse
import gzip
import hashlib
import json
import sys
from pathlib import Path

from decision.sources import load_sources
from decision.verify import (
    LicenceTermsExtractor,
    StoredRegions,
    licence_sentence_hash,
    licence_sentences,
)

COPY_SHA = "44954e49076689b7e52467f9e0aa37b9f980275a8a952239c0e93ad6f7d49dd8"
REGION_SHA = "d2c86ed7725d564d163114111fb629b28bd4e5989eeb893137aff91bbdfc70d4"
SOURCE_ID = "model-390-meta-api-terms"
SOURCE_URL = "https://dev.meta.ai/legal/terms-of-service"


class RetainedCopy:
    def __init__(self, body):
        self.body = body

    def has(self, ref):
        return ref == "sha256:" + COPY_SHA

    def get(self, ref):
        if not self.has(ref):
            raise ValueError("Unexpected retained copy")
        return self.body


def refuse_network(event, _args):
    if event.startswith("socket."):
        raise RuntimeError("The seed check is offline")


def derive(root, check, sentence_labels=False):
    sys.addaudithook(refuse_network)
    body = gzip.decompress((root / "research/model-390/copies" / (COPY_SHA + ".gz")).read_bytes())
    if hashlib.sha256(body).hexdigest() != COPY_SHA:
        raise ValueError("Retained copy differs from its reviewed digest")
    sources = load_sources(root / "registry/sources.yaml")
    if str(sources[SOURCE_ID].url) != SOURCE_URL:
        raise ValueError("The reviewed source URL changed")
    text = StoredRegions(RetainedCopy(body), sources).text(SOURCE_ID, "sha256:" + COPY_SHA, "page")
    if text is None or licence_sentence_hash(text) != REGION_SHA:
        raise ValueError("The reviewed cited region changed")
    sentences = licence_sentences(text)
    if len(sentences) <= 149:
        raise ValueError("Reviewed operative sentences are missing")
    sentence = sentences[148]
    if not sentence.endswith("."):
        raise ValueError("The operative item must be complete")
    if sentence_labels:
        labels = (
            (20, "Conditional service-use grant"),
            (138, "Prohibited-use list introduction"),
            (148, "Competing-model output training limits with authorization exception"),
            (149, "Evaluation exception"),
        )
        print(json.dumps([
            {"sentence_index": index,
             "sentence_sha256": hashlib.sha256(sentences[index].encode()).hexdigest(),
             "label": label}
            for index, label in labels
        ], indent=2))
        return
    row = dict(source_family="meta-api-terms", source_url=SOURCE_URL, region_sha256=REGION_SHA,
               sentence_sha256=hashlib.sha256(sentence.encode()).hexdigest(),
               facet="licence.output_training", value="restricted",
               label="Competing-model output training limits with authorization exception")
    if check:
        reader = LicenceTermsExtractor()
        normalized = "\n".join(sentences)
        if licence_sentence_hash(normalized) != REGION_SHA:
            raise ValueError("Normalized sentence reassembly changed the reviewed context")
        assert reader.values(row["facet"], text, licence_url=SOURCE_URL) == {"restricted"}, \
            "test_retained_meta_competing_output_clause_reads_restricted"
        for replacement in (
            "not " + sentence, sentence[:-1] + "?",
            sentence.replace("competes", "does not compete"),
        ):
            assert replacement != sentence
            changed = normalized.replace(sentence, replacement)
            assert reader.values(row["facet"], changed, licence_url=SOURCE_URL) == set(), \
                "test_near_identical_meta_output_clause_is_unread"
        for suffix in (" This prohibition is revoked.", " This is an illustrative example."):
            assert reader.values(row["facet"], text + suffix, licence_url=SOURCE_URL) == set(), \
                "test_changed_meta_context_is_unread"
        assert reader.values(row["facet"], text, licence_url=SOURCE_URL + "-other") == set(), \
            "test_meta_clause_cannot_be_borrowed_from_another_url"
        print("4 retained-region behavioral checks passed; no network or completion calls")
    print(json.dumps(row, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--sentence-labels", action="store_true")
    args = parser.parse_args()
    derive(args.data.resolve(), args.check, args.sentence_labels)
