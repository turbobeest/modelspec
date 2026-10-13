"""Regenerate the single synthetic blog fixture. No production data or keys."""

import base64
import json
from pathlib import Path

import yaml
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from decision.snapshot import Ed25519Signer
from release_blog.breakdown import to_bytes
from release_blog.gates import load_signed
from release_blog.render import write
from tests import test_release_blog as sample

ROOT = Path(__file__).resolve().parent
SLUG = "2026-09-26-alpha"


def main() -> None:
    private = Ed25519PrivateKey.from_private_bytes(bytes(range(32)))
    public = private.public_key().public_bytes(
        serialization.Encoding.Raw, serialization.PublicFormat.Raw
    )
    sample.SIGNER = Ed25519Signer(
        sample.KEY_ID,
        base64.b64encode(
            private.private_bytes(
                serialization.Encoding.Raw,
                serialization.PrivateFormat.Raw,
                serialization.NoEncryption(),
            )
        ).decode(),
    )
    keys = {sample.KEY_ID: public}
    snapshots = ROOT / "snapshots"
    snapshots.mkdir(exist_ok=True)
    loaded = []
    for name, with_new in (("before", False), ("after", True)):
        temporary = snapshots / f"{name}.json.gz"
        sample._write(temporary, with_new=with_new, signer=sample.SIGNER)
        snapshot = load_signed(temporary, public_keys=keys)
        temporary.rename(snapshots / f"{snapshot.snapshot_id}.json.gz")
        loaded.append(snapshot)
    before, after = loaded
    breakdown = sample._build(after, before)
    post = ROOT / "posts" / SLUG
    revision = post / "r1"
    revision.mkdir(parents=True, exist_ok=True)
    (revision / "breakdown.json").write_bytes(to_bytes(breakdown))
    write(breakdown, revision / "post.md")
    (post / "post.yaml").write_text(
        yaml.safe_dump(
            {
                "schema_version": 1,
                "model": "lab/alpha",
                "title": "Alpha model release breakdown",
                "status": "draft",
                "early_access": None,
                "revisions": [
                    {"revision": 1, "published": None, "approved_by": None, "approval": None}
                ],
            },
            sort_keys=False,
        )
    )
    (post / "commentary.md").write_text(
        "{{model:lab/alpha}} has a lab-reported reading of "
        "{{n:/claims_vs_evidence/claims/0/claim}}.\n"
    )
    (ROOT / "public-keys.json").write_text(
        json.dumps({sample.KEY_ID: base64.b64encode(public).decode()}, indent=2) + "\n"
    )


if __name__ == "__main__":
    main()
