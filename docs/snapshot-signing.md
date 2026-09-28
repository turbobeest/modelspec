# Provision snapshot signing

The site build signs each decision snapshot with Ed25519 when the
`MODELSPEC_SNAPSHOT_ED25519_KEY` repository secret is set. The CLI verifies
that signature offline against `decision/snapshot_keys.json`. The site publishes
the same file at
`https://modelspec.dev/.well-known/modelspec-snapshot-keys.json`.

The secret accepts either a PKCS8 PEM Ed25519 private key or the base64 encoding
of the 32-byte raw private key. Use PEM for the first key.

Signing selects a key ID by deriving the public key from the secret and matching
it against `decision/snapshot_keys.json`. If that file contains keys but none
matches, snapshot writing fails before it emits an unverifiable signature. An
empty key set is the one bootstrap exception: the build warns, omits the
Ed25519 signature, and still writes the HMAC signature when its key is set. This
keeps deployment available while the first public key commit lands. Internal
build-only snapshots, such as the landing page's data input, check their content
hash without requiring a publisher signature.

## Add the first key

Run these commands from the repository root. They generate the private key
locally, add it to the repository secret, and add only the public key to git.

```bash
umask 077
openssl genpkey -algorithm ED25519 -out modelspec-snapshot-ed25519.pem
gh secret set MODELSPEC_SNAPSHOT_ED25519_KEY < modelspec-snapshot-ed25519.pem
python - modelspec-snapshot-ed25519.pem decision/snapshot_keys.json <<'PY'
import base64
import hashlib
import json
import sys
from pathlib import Path

from cryptography.hazmat.primitives import serialization

private_path = Path(sys.argv[1])
key_set_path = Path(sys.argv[2])
private = serialization.load_pem_private_key(private_path.read_bytes(), password=None)
public = private.public_key().public_bytes(
    serialization.Encoding.Raw,
    serialization.PublicFormat.Raw,
)
key_id = "ed25519-" + hashlib.sha256(public).hexdigest()[:16]
key_set = json.loads(key_set_path.read_text(encoding="utf-8"))
key_set["keys"].append({
    "key_id": key_id,
    "alg": "ed25519",
    "public_key": base64.b64encode(public).decode("ascii"),
})
key_set_path.write_text(json.dumps(key_set, indent=2) + "\n", encoding="utf-8")
print(key_id)
PY
git add decision/snapshot_keys.json
git commit -s -m "snapshot: publish the Ed25519 verification key"
git push
```

Store `modelspec-snapshot-ed25519.pem` in the private key store after the
secret is set. Do not commit it.

The next build from `main` writes both signatures. The Worker verifies the
HMAC with `MODELSPEC_SNAPSHOT_KEY`. Public clients verify Ed25519 with the
pinned key set.

## Rotate a key

Repeat the commands with a new private-key filename. Keep the old public key in
`decision/snapshot_keys.json` while clients may still hold snapshots signed by
it. The build selects the key ID by matching the secret's public key against
the key set, so rotation does not need a second secret.

After old snapshots and old CLI releases no longer need the old key, remove its
entry in a separate commit. Never reuse a key ID with different key bytes.
