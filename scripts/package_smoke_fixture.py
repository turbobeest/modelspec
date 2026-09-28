#!/usr/bin/env python3
"""Install a test-key-signed decision cache for the wheel smoke test."""

from __future__ import annotations

import argparse
import base64
import gzip
import json
import urllib.request
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from decision.snapshot import (
    PUBLIC_KEY_SET_PATH,
    Ed25519Signer,
    Snapshot,
    load_built_snapshot,
)

SNAPSHOT_ROUTE = "/api/decision/snapshot.json.gz"
VOCABULARY_ROUTE = "/api/decision/vocabulary.json"


def _download(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "modelspec-package-smoke/1"})
    with urllib.request.urlopen(request, timeout=60) as response:  # noqa: S310 - fixed CI origin
        return response.read()


def install_fixture(origin: str, cache: Path, key_id: str) -> str:
    """Cache the public decision data with an ephemeral Ed25519 signature."""
    origin = origin.rstrip("/")
    snapshot_data = _download(origin + SNAPSHOT_ROUTE)
    vocabulary = json.loads(_download(origin + VOCABULARY_ROUTE))
    envelope: dict[str, Any] = json.loads(gzip.decompress(snapshot_data))
    snapshot = Snapshot(
        envelope["content"],
        str(envelope["content_hash"]),
        str(envelope["snapshot_id"]),
    )
    loaded = load_built_snapshot(
        snapshot,
        include_archive=True,
        source=origin + SNAPSHOT_ROUTE,
    )
    if not isinstance(vocabulary, dict) or vocabulary.get("snapshot") != loaded.snapshot_id:
        raise ValueError("the public decision vocabulary does not match its snapshot")

    private = Ed25519PrivateKey.generate()
    private_raw = private.private_bytes(
        serialization.Encoding.Raw,
        serialization.PrivateFormat.Raw,
        serialization.NoEncryption(),
    )
    public_raw = private.public_key().public_bytes(
        serialization.Encoding.Raw,
        serialization.PublicFormat.Raw,
    )
    PUBLIC_KEY_SET_PATH.write_text(
        json.dumps({
            "format": "modelspec.snapshot-keys",
            "version": 1,
            "keys": [{
                "key_id": key_id,
                "alg": "ed25519",
                "public_key": base64.b64encode(public_raw).decode("ascii"),
            }],
        }),
        encoding="utf-8",
    )

    root = cache / "decision"
    generation = root / loaded.snapshot_id
    generation.mkdir(parents=True, exist_ok=True)
    snapshot.write(
        generation / "snapshot.json.gz",
        key=None,
        ed25519_signer=Ed25519Signer(key_id, private_raw),
    )
    (generation / "vocabulary.json").write_text(
        json.dumps(vocabulary),
        encoding="utf-8",
    )
    (root / "current").write_text(loaded.snapshot_id + "\n", encoding="utf-8")
    return loaded.snapshot_id


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--origin", default="https://modelspec.dev")
    parser.add_argument("--cache", type=Path, required=True)
    parser.add_argument("--key-id", required=True)
    args = parser.parse_args()
    install_fixture(args.origin, args.cache, args.key_id)


if __name__ == "__main__":
    main()
