"""CDP REST JWT minting for the x402 facilitator (MODEL-88).

Coinbase CDP authenticates server-to-server REST calls with a JWT minted from
a Secret API Key, scoped to one HTTP method + host + path, and valid for two
minutes. Sources, read 2026-09-18:

* JWT authentication (header, claims, ``uri``, 120s lifetime, Ed25519 samples):
  https://docs.cdp.coinbase.com/get-started/authentication/jwt-authentication
* API keys (Ed25519 default, ECDSA/ES256 still issued; 120s Bearer tokens):
  https://docs.cdp.coinbase.com/get-started/authentication/cdp-api-keys
* Authentication overview (Ed25519 and ECDSA; CDP APIs accept both):
  https://docs.cdp.coinbase.com/get-started/authentication/overview
* JWT security (2-minute expiry, nonce in the header):
  https://docs.cdp.coinbase.com/get-started/authentication/security-best-practices
* x402 facilitator REST: POST /v2/x402/verify and /v2/x402/settle
  https://docs.cdp.coinbase.com/api-reference/v2/rest-api/x402-facilitator/x402-facilitator

Claim construction is pure Python. The Worker signs with Web Crypto
(``js.crypto.subtle`` via ``pyodide.ffi``); tests inject a signer. No pip
JWT package — this Worker sets ``disable_python_external_sdk``.
"""

from __future__ import annotations

import base64
import json
import secrets
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

#: JWT authentication samples and API-keys page, read 2026-09-18.
JWT_LIFETIME_SECONDS = 120
ISS = "cdp"
AUD = ["cdp_service"]

ALG_EDDSA = "EdDSA"
ALG_ES256 = "ES256"

SignFn = Callable[[str, bytes, bytes], Awaitable[bytes]]


class CdpAuthError(RuntimeError):
    """Minting failed. Message must never include the secret or the JWT."""


@dataclass(frozen=True)
class KeyMaterial:
    """PKCS#8 DER plus the JWT ``alg`` for one Secret API Key."""

    alg: str
    pkcs8: bytes


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def request_uri(method: str, url: str) -> str:
    """``POST api.cdp.coinbase.com/platform/v2/x402/verify`` (JWT docs, 2026-09-18)."""
    parsed = urlparse(url)
    return f"{method.upper()} {parsed.netloc}{parsed.path}"


def jwt_header(alg: str, key_id: str, nonce: str) -> dict[str, str]:
    """``alg``, ``typ``, ``kid``, ``nonce`` as in the JWT authentication samples."""
    return {"alg": alg, "typ": "JWT", "kid": key_id, "nonce": nonce}


def jwt_claims(key_id: str, uri: str, now: int,
               lifetime: int = JWT_LIFETIME_SECONDS) -> dict[str, Any]:
    """``iss``, ``sub``, ``aud``, ``nbf``, ``exp``, ``uri`` from the JWT docs.

    ``uris`` is the same value as an array. The JWT authentication page's
    language samples set ``uri`` (singular). The CDP SDK that those same pages
    recommend (``generateJwt`` / ``generate_jwt``) sets ``uris``. Extra claims
    are ignored by JWT verifiers that do not read them.
    """
    return {
        "sub": key_id,
        "iss": ISS,
        "aud": list(AUD),
        "nbf": now,
        "exp": now + lifetime,
        "uri": uri,
        "uris": [uri],
    }


def encode_segment(obj: dict[str, Any]) -> str:
    raw = json.dumps(obj, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return b64url(raw)


def signing_input(header: dict[str, Any], claims: dict[str, Any]) -> bytes:
    return f"{encode_segment(header)}.{encode_segment(claims)}".encode("ascii")


def random_nonce() -> str:
    """16 random bytes as hex. TS SDK ``nonce()`` and Ruby ``SecureRandom.hex(16)``."""
    try:
        from js import Uint8Array, crypto
        buf = Uint8Array.new(16)
        crypto.getRandomValues(buf)
        return "".join(f"{int(buf[i]):02x}" for i in range(16))
    except ImportError:
        return secrets.token_hex(16)


def _pem_der(pem: str) -> bytes:
    lines = [
        line.strip() for line in pem.replace("\\n", "\n").splitlines()
        if line.strip() and not line.strip().startswith("-----")
    ]
    if not lines:
        raise CdpAuthError("CDP API key secret PEM is empty")
    try:
        return base64.b64decode("".join(lines), validate=False)
    except Exception as exc:
        raise CdpAuthError("CDP API key secret PEM is not valid base64") from exc


def _der_len(n: int) -> bytes:
    if n < 0x80:
        return bytes([n])
    body = n.to_bytes((n.bit_length() + 7) // 8, "big")
    return bytes([0x80 | len(body)]) + body


def _tlv(tag: int, body: bytes) -> bytes:
    return bytes([tag]) + _der_len(len(body)) + body


def _seq(body: bytes) -> bytes:
    return _tlv(0x30, body)


def _octet(body: bytes) -> bytes:
    return _tlv(0x04, body)


#: RFC 8410 PKCS#8 prefix for an Ed25519 seed (OID 1.3.101.112).
_ED25519_PKCS8_PREFIX = bytes.fromhex("302e020100300506032b657004220420")
#: AlgorithmIdentifier for id-ecPublicKey + prime256v1.
_EC_P256_ALG = bytes.fromhex("301306072a8648ce3d020106082a8648ce3d030107")


def _ed25519_pkcs8(seed: bytes) -> bytes:
    if len(seed) != 32:
        raise CdpAuthError("Ed25519 seed is not 32 bytes")
    return _ED25519_PKCS8_PREFIX + seed


def _ec_sec1_to_pkcs8(sec1: bytes) -> bytes:
    inner = bytes([0x02, 0x01, 0x00]) + _EC_P256_ALG + _octet(sec1)
    return _seq(inner)


def parse_secret(secret: str) -> KeyMaterial:
    """Ed25519 (base64 64-byte seed||public) or ECDSA P-256 (SEC1 or PKCS#8 PEM)."""
    raw = (secret or "").strip()
    if not raw:
        raise CdpAuthError("CDP API key secret is empty")
    upper = raw.upper()
    if "BEGIN EC PRIVATE KEY" in upper:
        return KeyMaterial(ALG_ES256, _ec_sec1_to_pkcs8(_pem_der(raw)))
    if "BEGIN PRIVATE KEY" in upper:
        return KeyMaterial(ALG_ES256, _pem_der(raw))
    try:
        decoded = base64.b64decode(raw, validate=False)
    except Exception as exc:
        raise CdpAuthError(
            "CDP API key secret is not a PEM EC key or a 64-byte Ed25519 secret"
        ) from exc
    if len(decoded) != 64:
        raise CdpAuthError(
            "CDP API key secret is not a PEM EC key or a 64-byte Ed25519 secret"
        )
    return KeyMaterial(ALG_EDDSA, _ed25519_pkcs8(decoded[:32]))


def _u8(data: bytes):
    from js import Uint8Array
    view = Uint8Array.new(len(data))
    for i, byte in enumerate(data):
        view[i] = byte
    return view


def _from_buf(buf) -> bytes:
    from js import Uint8Array
    view = Uint8Array.new(buf)
    return bytes(int(view[i]) for i in range(int(view.length)))


async def webcrypto_sign(alg: str, pkcs8: bytes, message: bytes) -> bytes:
    """Worker signer. ``js.crypto.subtle`` through ``pyodide.ffi.to_js``."""
    from js import Object, crypto
    from pyodide.ffi import to_js

    if alg == ALG_EDDSA:
        import_alg = to_js({"name": "Ed25519"}, dict_converter=Object.fromEntries)
        sign_alg: Any = "Ed25519"
    elif alg == ALG_ES256:
        import_alg = to_js(
            {"name": "ECDSA", "namedCurve": "P-256"},
            dict_converter=Object.fromEntries,
        )
        sign_alg = to_js(
            {"name": "ECDSA", "hash": "SHA-256"},
            dict_converter=Object.fromEntries,
        )
    else:
        raise CdpAuthError("unsupported JWT alg")
    try:
        key = await crypto.subtle.importKey(
            "pkcs8", _u8(pkcs8), import_alg, False, to_js(["sign"]),
        )
        sig = await crypto.subtle.sign(sign_alg, key, _u8(message))
    except CdpAuthError:
        raise
    except Exception as exc:
        raise CdpAuthError("failed to mint CDP JWT") from exc
    return _from_buf(sig)


async def mint_jwt(
    *,
    key_id: str,
    secret: str,
    method: str,
    url: str,
    now: int | None = None,
    nonce: str | None = None,
    sign: SignFn | None = None,
    lifetime: int = JWT_LIFETIME_SECONDS,
) -> str:
    """Mint one JWT for this method and URL. Never logs the secret or the token."""
    if not (key_id or "").strip():
        raise CdpAuthError("CDP API key id is empty")
    material = parse_secret(secret)
    when = int(time.time()) if now is None else now
    header = jwt_header(material.alg, key_id.strip(), nonce or random_nonce())
    claims = jwt_claims(key_id.strip(), request_uri(method, url), when, lifetime)
    message = signing_input(header, claims)
    signer = sign or webcrypto_sign
    try:
        signature = await signer(material.alg, material.pkcs8, message)
    except CdpAuthError:
        raise
    except Exception as exc:
        raise CdpAuthError("failed to mint CDP JWT") from exc
    if not signature:
        raise CdpAuthError("failed to mint CDP JWT")
    return f"{message.decode('ascii')}.{b64url(signature)}"


def _env(env: Any, name: str) -> str:
    return str(getattr(env, name, "") or "").strip()


def auth_from_env(env: Any, *, mainnet: bool, sign: SignFn | None = None):
    """Per-call mint from ``CDP_API_KEY_ID`` + ``CDP_API_KEY_SECRET``.

    ``CDP_JWT`` is a local-testing override used only when those secrets are
    absent, and it is refused when ``X402_MAINNET`` is on: a static token expires
    in two minutes (JWT authentication docs, 2026-09-18).
    """
    key_id = _env(env, "CDP_API_KEY_ID")
    secret = _env(env, "CDP_API_KEY_SECRET")
    static = _env(env, "CDP_JWT")
    injected = sign if callable(sign) else None

    async def auth(method: str, url: str) -> dict[str, str]:
        if key_id and secret:
            token = await mint_jwt(
                key_id=key_id, secret=secret, method=method, url=url, sign=injected,
            )
            return {"Authorization": f"Bearer {token}"}
        if static:
            if mainnet:
                raise CdpAuthError(
                    "CDP_JWT is a local-testing override and is refused when "
                    "X402_MAINNET is on"
                )
            return {"Authorization": f"Bearer {static}"}
        return {}

    return auth
