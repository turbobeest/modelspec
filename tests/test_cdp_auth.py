"""MODEL-88: CDP REST JWT minting (claim construction + signature round-trip)."""

from __future__ import annotations

import asyncio
import base64
import json
import logging
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKER_SRC = REPO_ROOT / "api" / "worker" / "src"
sys.path.insert(0, str(WORKER_SRC))

import cdp_auth  # noqa: E402


def _pem_der(pem: bytes | str) -> bytes:
    text = pem.decode("ascii") if isinstance(pem, bytes) else pem
    lines = [
        line.strip() for line in text.splitlines()
        if line.strip() and not line.strip().startswith("-----")
    ]
    return base64.b64decode("".join(lines), validate=False)


def _pkcs8_pem(der: bytes) -> bytes:
    body = base64.encodebytes(der).decode("ascii")
    return (
        "-----BEGIN PRIVATE KEY-----\n" + body + "-----END PRIVATE KEY-----\n"
    ).encode("ascii")


def generate_ed25519() -> tuple[str, bytes, bytes]:
    """Return (CDP 64-byte secret, PKCS#8 DER, public PEM). Generated here, never a real key."""
    pem = subprocess.check_output(["openssl", "genpkey", "-algorithm", "Ed25519"])
    der = _pem_der(pem)
    seed = der[-32:]
    pub_pem = subprocess.check_output(["openssl", "pkey", "-pubout"], input=pem)
    public = _pem_der(pub_pem)[-32:]
    secret = base64.b64encode(seed + public).decode("ascii")
    return secret, der, pub_pem


def generate_es256_sec1() -> bytes:
    return subprocess.check_output(
        ["openssl", "ecparam", "-name", "prime256v1", "-genkey", "-noout"]
    )


def generate_es256_pkcs8() -> bytes:
    sec1 = generate_es256_sec1()
    return subprocess.check_output(
        ["openssl", "pkcs8", "-topk8", "-nocrypt"], input=sec1
    )


def _read_der_len(data: bytes, i: int) -> tuple[int, int]:
    ln = data[i]
    i += 1
    if ln < 0x80:
        return ln, i
    n = ln & 0x7F
    return int.from_bytes(data[i:i + n], "big"), i + n


def der_ecdsa_to_p1363(der: bytes, size: int = 32) -> bytes:
    assert der[0] == 0x30
    _, i = _read_der_len(der, 1)

    def read_int(pos: int) -> tuple[bytes, int]:
        assert der[pos] == 0x02
        ln, pos = _read_der_len(der, pos + 1)
        return der[pos:pos + ln], pos + ln

    r, i = read_int(i)
    s, _ = read_int(i)

    def pad(x: bytes) -> bytes:
        x = x.lstrip(b"\x00") or b"\x00"
        return x.rjust(size, b"\x00")[-size:]

    return pad(r) + pad(s)


def p1363_to_der(sig: bytes) -> bytes:
    r, s = sig[:32], sig[32:]

    def int_der(x: bytes) -> bytes:
        x = x.lstrip(b"\x00") or b"\x00"
        if x[0] & 0x80:
            x = b"\x00" + x
        return bytes([0x02, len(x)]) + x

    body = int_der(r) + int_der(s)
    return bytes([0x30, len(body)]) + body


def openssl_sign(alg: str, pkcs8: bytes, message: bytes) -> bytes:
    pem = _pkcs8_pem(pkcs8)
    with tempfile.TemporaryDirectory() as td:
        key_path = Path(td) / "key.pem"
        msg_path = Path(td) / "msg"
        key_path.write_bytes(pem)
        msg_path.write_bytes(message)
        if alg == cdp_auth.ALG_EDDSA:
            return subprocess.check_output([
                "openssl", "pkeyutl", "-sign", "-inkey", str(key_path),
                "-rawin", "-in", str(msg_path),
            ])
        if alg == cdp_auth.ALG_ES256:
            der = subprocess.check_output([
                "openssl", "dgst", "-sha256", "-sign", str(key_path), str(msg_path),
            ])
            return der_ecdsa_to_p1363(der)
        raise AssertionError(alg)


async def openssl_sign_async(alg: str, pkcs8: bytes, message: bytes) -> bytes:
    return openssl_sign(alg, pkcs8, message)


def openssl_verify(alg: str, pub_pem: bytes, message: bytes, signature: bytes) -> bool:
    with tempfile.TemporaryDirectory() as td:
        pub_path = Path(td) / "pub.pem"
        msg_path = Path(td) / "msg"
        sig_path = Path(td) / "sig"
        pub_path.write_bytes(pub_pem)
        msg_path.write_bytes(message)
        if alg == cdp_auth.ALG_EDDSA:
            sig_path.write_bytes(signature)
            result = subprocess.run(
                ["openssl", "pkeyutl", "-verify", "-pubin", "-inkey", str(pub_path),
                 "-rawin", "-in", str(msg_path), "-sigfile", str(sig_path)],
                capture_output=True, check=False,
            )
            return result.returncode == 0
        if alg == cdp_auth.ALG_ES256:
            sig_path.write_bytes(p1363_to_der(signature))
            result = subprocess.run(
                ["openssl", "dgst", "-sha256", "-verify", str(pub_path),
                 "-signature", str(sig_path), str(msg_path)],
                capture_output=True, check=False,
            )
            return result.returncode == 0
        raise AssertionError(alg)


def _b64json(segment: str) -> dict:
    padded = segment + "=" * (-len(segment) % 4)
    return json.loads(base64.urlsafe_b64decode(padded))


def decode_unverified(token: str) -> tuple[dict, dict, bytes]:
    header_b64, claims_b64, sig_b64 = token.split(".")
    signature = base64.urlsafe_b64decode(sig_b64 + "=" * (-len(sig_b64) % 4))
    return _b64json(header_b64), _b64json(claims_b64), signature


def _run(coro):
    return asyncio.run(coro)


VERIFY_URL = "https://api.cdp.coinbase.com/platform/v2/x402/verify"
SETTLE_URL = "https://api.cdp.coinbase.com/platform/v2/x402/settle"


def test_request_uri_is_method_host_path_without_scheme():
    assert cdp_auth.request_uri("POST", VERIFY_URL) == (
        "POST api.cdp.coinbase.com/platform/v2/x402/verify"
    )
    assert cdp_auth.request_uri("post", SETTLE_URL) == (
        "POST api.cdp.coinbase.com/platform/v2/x402/settle"
    )


def test_claims_match_cdp_jwt_authentication_docs():
    now = 1_700_000_000
    uri = "POST api.cdp.coinbase.com/platform/v2/x402/verify"
    claims = cdp_auth.jwt_claims("key-name", uri, now)
    assert claims["iss"] == "cdp"
    assert claims["sub"] == "key-name"
    assert claims["aud"] == ["cdp_service"]
    assert claims["nbf"] == now
    assert claims["exp"] == now + 120
    assert claims["uri"] == uri
    assert claims["uris"] == [uri]


def test_header_has_alg_typ_kid_nonce():
    header = cdp_auth.jwt_header("EdDSA", "key-name", "abc123")
    assert header == {"alg": "EdDSA", "typ": "JWT", "kid": "key-name", "nonce": "abc123"}


def test_signing_input_is_two_segments_and_does_not_sign():
    header = cdp_auth.jwt_header("EdDSA", "kid", "nonce")
    claims = cdp_auth.jwt_claims("kid", "POST host/path", now=10)
    message = cdp_auth.signing_input(header, claims)
    assert message.decode("ascii").count(".") == 1
    encoded = message.decode("ascii")
    header_b64, claims_b64 = encoded.split(".")
    assert _b64json(header_b64)["nonce"] == "nonce"
    decoded_claims = _b64json(claims_b64)
    assert decoded_claims["uri"] == "POST host/path"
    assert decoded_claims["exp"] == 130


def test_parse_secret_ed25519_and_es256():
    secret, der, _pub = generate_ed25519()
    ed = cdp_auth.parse_secret(secret)
    assert ed.alg == "EdDSA"
    assert ed.pkcs8 == der

    sec1 = generate_es256_sec1()
    es = cdp_auth.parse_secret(sec1.decode("ascii"))
    assert es.alg == "ES256"
    assert es.pkcs8.startswith(b"\x30")

    pkcs8 = generate_es256_pkcs8()
    wrapped = cdp_auth.parse_secret(pkcs8.decode("ascii"))
    assert wrapped.alg == "ES256"
    assert wrapped.pkcs8 == _pem_der(pkcs8)


def test_parse_secret_unescapes_literal_newlines_in_pem():
    sec1 = generate_es256_sec1().decode("ascii")
    escaped = sec1.replace("\n", "\\n")
    assert "\\n" in escaped
    assert cdp_auth.parse_secret(escaped).alg == "ES256"


def test_ed25519_signature_round_trips():
    secret, _der, pub_pem = generate_ed25519()
    key_id = str(uuid.uuid4())
    token = _run(cdp_auth.mint_jwt(
        key_id=key_id, secret=secret, method="POST", url=VERIFY_URL,
        sign=openssl_sign_async,
    ))
    header, claims, signature = decode_unverified(token)
    assert header["alg"] == "EdDSA"
    assert header["kid"] == key_id
    assert header["typ"] == "JWT"
    assert header["nonce"]
    assert claims["uri"] == "POST api.cdp.coinbase.com/platform/v2/x402/verify"
    assert claims["nbf"] <= int(time.time())
    assert claims["exp"] > int(time.time())
    assert claims["exp"] - claims["nbf"] == 120
    message = ".".join(token.split(".")[:2]).encode("ascii")
    assert openssl_verify("EdDSA", pub_pem, message, signature)


def test_es256_signature_round_trips():
    pem = generate_es256_pkcs8()
    pub_pem = subprocess.check_output(["openssl", "pkey", "-pubout"], input=pem)
    key_id = str(uuid.uuid4())
    token = _run(cdp_auth.mint_jwt(
        key_id=key_id, secret=pem.decode("ascii"), method="POST", url=SETTLE_URL,
        sign=openssl_sign_async,
    ))
    header, claims, signature = decode_unverified(token)
    assert header["alg"] == "ES256"
    assert claims["uri"] == "POST api.cdp.coinbase.com/platform/v2/x402/settle"
    message = ".".join(token.split(".")[:2]).encode("ascii")
    assert openssl_verify("ES256", pub_pem, message, signature)


def test_two_mints_get_different_nonces():
    secret, _der, _pub = generate_ed25519()
    key_id = str(uuid.uuid4())
    first = _run(cdp_auth.mint_jwt(
        key_id=key_id, secret=secret, method="POST", url=VERIFY_URL,
        sign=openssl_sign_async,
    ))
    second = _run(cdp_auth.mint_jwt(
        key_id=key_id, secret=secret, method="POST", url=VERIFY_URL,
        sign=openssl_sign_async,
    ))
    h1, _, _ = decode_unverified(first)
    h2, _, _ = decode_unverified(second)
    assert h1["nonce"] != h2["nonce"]
    assert first != second


def test_errors_do_not_echo_the_secret():
    secret = "not-a-real-key-and-not-valid-base64-$$$$"
    with pytest.raises(cdp_auth.CdpAuthError, match="not a PEM EC key") as exc:
        cdp_auth.parse_secret(secret)
    assert secret not in str(exc.value)


def test_secret_and_jwt_do_not_appear_in_logs(caplog, capsys):
    secret, _der, _pub = generate_ed25519()
    key_id = "test-key-id-model-88"
    caplog.set_level(logging.DEBUG)
    token = _run(cdp_auth.mint_jwt(
        key_id=key_id, secret=secret, method="POST", url=VERIFY_URL,
        sign=openssl_sign_async,
    ))
    captured = capsys.readouterr()
    haystack = "\n".join([caplog.text, captured.out, captured.err])
    assert secret not in haystack
    assert token not in haystack
    assert "Bearer " not in haystack
