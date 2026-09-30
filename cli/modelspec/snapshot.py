"""The free path: a local snapshot of the published export, usable offline.

The CLI's graph commands need FalkorDB on localhost:6382. That is fine for
someone exploring the graph locally and useless for everyone else, including
dpf's ticket author, who needs an answer on a machine that has never run a
database.

This module downloads the versioned export from modelspec.dev, caches it, and
answers from the cache. No credential, no account, no network once fetched.

MODEL-71 adds one thing and changes nothing else: `fetch` can present a key to
an origin that keys its export, so a caller entitled to the current tree gets a
snapshot whose `fetched_at` is now rather than one built from a 90-day-delayed
public export. The default origin is unkeyed and the free path is untouched —
without a credential this module behaves exactly as it did. The credential is
carried in a `Credential`, which has no printable form of the secret, so a key
cannot reach a log line by being interpolated into one.

The pin identity is `build.commit` plus `build.export_schema_version`. The
latter is the published JSON tree, not the CLI `--json` envelope
(`offline.SCHEMA_VERSION`) and not `rankings.json`'s `schema_version`.

The continuity rule matters more than freshness: an answer from a snapshot three
weeks old, clearly labelled as three weeks old, is far more useful than an error.
Callers are told the age and decide for themselves.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import secrets
import shutil
import time
import warnings
from collections.abc import Mapping
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

DEFAULT_ORIGIN = "https://modelspec.dev"

#: Where the credential for a keyed origin is read from. The environment is the
#: supported way to supply it: `docs/agent-commerce-assessment.md` §4 notes that
#: a credential on the command line lands in process listings, shell history and
#: logs, and an environment variable lands in fewer of those.
API_KEY_ENV = "MODELSPEC_API_KEY"

#: How a key identifies itself in a message a human or a log will see. The same
#: 12 hex characters of SHA-256 the origin calls `key_id` (MODEL-69,
#: `api/worker/src/access_keys.py`), so a support conversation can name the same
#: key from both ends without either end quoting the secret.
KEY_ID_LENGTH = 12

#: What replaces the secret if one ever reaches a string that is about to be
#: printed. Nothing should get that far; this is the backstop, not the plan.
REDACTED = "[redacted]"

#: Files that make a usable snapshot. Kept small on purpose — the whole point is
#: that this works on a laptop tethered to a phone.
PARTS = {
    "index": "/api/index.json",
    "candidates": "/api/rank/candidates.json",
    "profiles": "/api/rank/profiles.json",
    "hardware": "/api/graph/views/hardware.json",
}

#: Parts a snapshot may lack. An export older than MODEL-26 phase B has no
#: hosts.json; the snapshot still answers everything except `fit --host`.
OPTIONAL_PARTS = {
    "hosts": "/api/hosts.json",
}

DECISION_SNAPSHOT_ROUTE = "/api/decision/snapshot.json.gz"
DECISION_VOCABULARY_ROUTE = "/api/decision/vocabulary.json"
DECISION_DIRECTORY = "decision"
DECISION_SNAPSHOT_FILENAME = "snapshot.json.gz"
DECISION_VOCABULARY_FILENAME = "vocabulary.json"
DECISION_SNAPSHOT_ID = re.compile(r"snap_[0-9a-f]{16}")

#: Past this, the snapshot is still served but every answer says it is stale.
#: Model releases move weekly, so a month-old snapshot is a different world.
STALE_AFTER_DAYS = 30

#: Major.minor of `build.export_schema_version` this CLI will consume.
#: Must match `pipeline.export.EXPORT_SCHEMA_VERSION`. A different major is
#: refused so a breaking export cannot be ranked as if it were the old shape.
#: 2.0 since MODEL-77 reshaped the policy fields on the published cards.
EXPORT_SCHEMA_VERSION = "3.0"

#: What a snapshot with no `export_schema_version` at all actually is: an
#: export from before the field was added, which is the 1.x tree. It is named
#: rather than defaulted to the current version, because "the field is missing"
#: and "the field says whatever this CLI happens to be" stopped being the same
#: statement the moment the current version left 1.x — and assuming the latter
#: would read a pre-MODEL-77 card as if `commercial_use` were still a bool.
PRE_VERSIONED_EXPORT_SCHEMA_VERSION = "1.0"


def cache_dir() -> Path:
    """Respects XDG, so a user can point it somewhere else or clear it."""
    override = os.environ.get("MODELSPEC_CACHE")
    if override:
        return Path(override).expanduser()
    base = os.environ.get("XDG_CACHE_HOME") or "~/.cache"
    return Path(base).expanduser() / "modelspec"


def _decision_root(directory: Path | None = None) -> Path:
    return (directory or cache_dir()) / DECISION_DIRECTORY


def _validate_decision_generation(generation: Path, *, require_named: bool = True) -> str:
    from decision.snapshot import load_snapshot

    snapshot_path = generation / DECISION_SNAPSHOT_FILENAME
    vocabulary_path = generation / DECISION_VOCABULARY_FILENAME
    decision = load_snapshot(snapshot_path, key=None, include_archive=True)
    vocabulary = json.loads(vocabulary_path.read_text(encoding="utf-8"))
    if not isinstance(vocabulary, dict):
        raise ValueError("cached decision vocabulary is not a JSON object")
    if vocabulary.get("snapshot") != decision.snapshot_id:
        raise ValueError("cached decision vocabulary does not name the decision snapshot")
    from decision.snapshot import SnapshotIntegrityError, verify_vocabulary

    try:
        verify_vocabulary(vocabulary)
    except SnapshotIntegrityError as exc:
        raise ValueError(f"cached decision vocabulary: {exc}") from exc
    if require_named and generation.name != decision.snapshot_id:
        raise ValueError("cached decision generation does not name the decision snapshot")
    return decision.snapshot_id


def _current_decision_generation(
    directory: Path | None = None,
) -> tuple[Path | None, str | None]:
    root = _decision_root(directory)
    try:
        snapshot_id = (root / "current").read_text(encoding="utf-8").strip()
        if DECISION_SNAPSHOT_ID.fullmatch(snapshot_id) is None:
            raise ValueError("decision/current contains an invalid snapshot ID")
        generation = root / snapshot_id
        _validate_decision_generation(generation)
        return generation, None
    except FileNotFoundError:
        return None, None
    except (OSError, UnicodeError, ValueError, KeyError, json.JSONDecodeError) as exc:
        return None, str(exc)


def decision_snapshot_path(directory: Path | None = None) -> Path:
    generation, _error = _current_decision_generation(directory)
    return ((generation / DECISION_SNAPSHOT_FILENAME) if generation else
            (_decision_root(directory) / ".absent" / DECISION_SNAPSHOT_FILENAME))


def decision_vocabulary_path(directory: Path | None = None) -> Path:
    generation, _error = _current_decision_generation(directory)
    return ((generation / DECISION_VOCABULARY_FILENAME) if generation else
            (_decision_root(directory) / ".absent" / DECISION_VOCABULARY_FILENAME))


def cached_decision_generations(directory: Path | None = None) -> list[Path]:
    """Return valid retained generations, newest first."""
    root = _decision_root(directory)
    try:
        candidates = [path for path in root.iterdir()
                      if path.is_dir() and not path.name.startswith(".tmp-")]
    except OSError:
        return []
    valid = []
    for path in candidates:
        try:
            _validate_decision_generation(path)
        except (OSError, UnicodeError, ValueError, KeyError, json.JSONDecodeError):
            continue
        valid.append(path)
    return sorted(valid, key=lambda path: path.stat().st_mtime, reverse=True)


def resolve_decision_generation(reference: str, directory: Path | None = None) -> Path:
    """Resolve a retained snapshot ID or ``previous`` to its snapshot file."""
    generations = cached_decision_generations(directory)
    current, _error = _current_decision_generation(directory)
    if reference == "previous":
        choices = [path for path in generations if current is None or path != current]
        if choices:
            return choices[0] / DECISION_SNAPSHOT_FILENAME
    else:
        match = next((path for path in generations if path.name == reference), None)
        if match is not None:
            return match / DECISION_SNAPSHOT_FILENAME
    cached = ", ".join(sorted(path.name for path in generations)) or "none"
    raise ValueError(
        f"decision snapshot {reference!r} is not cached; cached snapshot ids: {cached}"
    )


@dataclass(frozen=True)
class Snapshot:
    path: Path
    fetched_at: datetime
    origin: str
    build_commit: str
    build_at: str
    data: dict[str, Any]
    export_schema_version: str = EXPORT_SCHEMA_VERSION
    decision_fetch: dict[str, Any] | None = None

    @property
    def age_days(self) -> float:
        return (datetime.now(UTC) - self.fetched_at).total_seconds() / 86400

    @property
    def is_stale(self) -> bool:
        return self.age_days > STALE_AFTER_DAYS

    def freshness(self) -> dict[str, Any]:
        """What every machine-readable answer carries, so nobody has to guess."""
        return {
            "fetched_at": self.fetched_at.isoformat(),
            "age_days": round(self.age_days, 2),
            "stale": self.is_stale,
            "stale_after_days": STALE_AFTER_DAYS,
            "origin": self.origin,
            "build_commit": self.build_commit,
            "built_at": self.build_at,
            "export_schema_version": self.export_schema_version,
        }


@dataclass(frozen=True, repr=False)
class Credential:
    """A key for a keyed origin, in a shape that cannot be printed by accident.

    The secret is a field with no `repr`, and `__repr__`/`__str__` are replaced
    by ones that emit the key id instead. That is the same reasoning the origin
    applies to its key store (`docs/api-access.md`, "Keys are never written
    down"): make "the secret is never logged" a property of the shape rather
    than a rule every future caller has to remember.
    """

    secret: str = field(repr=False)
    #: `environment` or `flag`. Reported so a message can name where a rejected
    #: key came from, and so the CLI can warn about the riskier of the two.
    source: str = "environment"

    @property
    def key_id(self) -> str:
        """The short, loggable identifier. It identifies; it cannot authenticate."""
        return hashlib.sha256(self.secret.encode("utf-8")).hexdigest()[:KEY_ID_LENGTH]

    def headers(self) -> dict[str, str]:
        """How the key is presented. A header, never a query parameter.

        URLs are written into access logs, proxy caches and referrer headers by
        everything they pass through. `Authorization` is also the one header
        httpx drops when a redirect crosses to another host, so a misconfigured
        redirect cannot carry the key somewhere it was not meant to go.
        """
        return {"Authorization": f"Bearer {self.secret}"}

    def redact(self, text: str) -> str:
        """Backstop: strip the secret out of anything on its way to a stream."""
        return text.replace(self.secret, REDACTED) if self.secret else text

    def __repr__(self) -> str:
        return f"Credential(source={self.source!r}, key_id={self.key_id!r})"

    __str__ = __repr__


def resolve_credential(flag: str | None = None,
                       environ: Mapping[str, str] | None = None) -> Credential | None:
    """The key to present, or `None` for the free, unkeyed path.

    The environment is the preferred source and the flag is the override: a
    caller who typed `--api-key` meant that key for this invocation. Preferring
    the environment is a recommendation about how to supply a key, not a rule
    that silently ignores the one in front of us.
    """
    if flag:
        return Credential(secret=flag, source="flag")
    from_env = (environ if environ is not None else os.environ).get(API_KEY_ENV)
    if from_env and from_env.strip():
        return Credential(secret=from_env.strip(), source="environment")
    return None


class SnapshotMissing(RuntimeError):  # noqa: N818 - public compatibility name
    """No snapshot has been fetched yet."""


class SnapshotInvalid(RuntimeError):  # noqa: N818 - follows SnapshotMissing naming
    """A snapshot exists but cannot be read or does not have the export shape."""


class FetchError(RuntimeError):
    """A fetch that failed for a reason the caller can act on.

    The four subclasses are the four things that go wrong against a keyed
    origin. They exist so the CLI can give each one its own exit code and its
    own sentence, instead of one `could not fetch` for everything.
    """


class OriginUnreachableError(FetchError):
    """The origin did not answer: DNS, TLS, connection, timeout."""


class KeyRequiredError(FetchError):
    """The origin wants a key and none was presented."""


class KeyRejectedError(FetchError):
    """The origin knows what a key is and will not accept this one."""


class RateLimitedError(FetchError):
    """The key is good and its window is spent."""

    def __init__(self, message: str, retry_after_seconds: int | None = None) -> None:
        super().__init__(message)
        self.retry_after_seconds = retry_after_seconds


def _export_schema_major(version: str) -> int:
    head = str(version).strip().split(".", 1)[0]
    if not head.isdigit():
        raise ValueError(
            f"export_schema_version {version!r} is not a dotted major.minor version"
        )
    return int(head)


def _declared_export_schema_version(data: dict[str, Any]) -> str:
    """Read the tree version from index.build.

    A missing value is not "whatever this CLI is". It is the tree as it stood
    before the field existed, which is 1.0 — so once this CLI moved past 1.x,
    such a snapshot is refused like any other incompatible major instead of
    being parsed as the current shape.
    """
    index = data.get("index")
    build = index.get("build") if isinstance(index, dict) else None
    if not isinstance(build, dict):
        return PRE_VERSIONED_EXPORT_SCHEMA_VERSION
    raw = build.get("export_schema_version")
    if raw is None:
        return PRE_VERSIONED_EXPORT_SCHEMA_VERSION
    return str(raw)


def _require_compatible_export_schema(version: str) -> str:
    try:
        major = _export_schema_major(version)
    except ValueError as exc:
        raise SnapshotInvalid(str(exc)) from exc
    expected = _export_schema_major(EXPORT_SCHEMA_VERSION)
    if major != expected:
        raise SnapshotInvalid(
            f"export_schema_version {version} is incompatible with this CLI "
            f"(expected {expected}.x). That field is the published JSON tree, "
            "not the CLI --json envelope schema_version."
        )
    return version


def _snapshot_from_raw(path: Path, raw: Any) -> Snapshot:
    if not isinstance(raw, dict):
        raise ValueError("top-level JSON value must be an object")
    meta = raw["meta"]
    data = raw["data"]
    if not isinstance(meta, dict) or not isinstance(data, dict):
        raise ValueError("meta and data must be objects")
    for key in ("fetched_at", "origin", "build_commit", "built_at"):
        if key not in meta:
            raise ValueError(f"meta is missing {key!r}")
    for key in ("index", "candidates", "profiles", "hardware"):
        if key not in data or not isinstance(data[key], dict):
            raise ValueError(f"data is missing object {key!r}")
    if not isinstance(data["candidates"].get("candidates"), list):
        raise ValueError("data.candidates.candidates must be a list")
    if not isinstance(data["profiles"].get("profiles"), dict):
        raise ValueError("data.profiles.profiles must be an object")
    if not isinstance(data["hardware"].get("nodes"), list):
        raise ValueError("data.hardware.nodes must be a list")
    fetched_at = datetime.fromisoformat(str(meta["fetched_at"]))
    if fetched_at.tzinfo is None:
        raise ValueError("meta.fetched_at must include a timezone")
    version = _require_compatible_export_schema(_declared_export_schema_version(data))
    return Snapshot(
        path=path,
        fetched_at=fetched_at,
        origin=str(meta["origin"]),
        build_commit=str(meta["build_commit"]),
        build_at=str(meta["built_at"]),
        data=data,
        export_schema_version=version,
    )


#: Statuses the origin uses to refuse a call it understood (MODEL-69,
#: `docs/api-access.md`). Anything else stays on the pre-existing path:
#: `raise_for_status`, wrapped by the CLI as a plain runtime error.
HTTP_UNAUTHORIZED = 401
HTTP_FORBIDDEN = 403
HTTP_TOO_MANY_REQUESTS = 429

#: `error.code` values the origin sends. Read to tell "you sent no key" from
#: "that key is not one of ours", which are different things for the caller.
MISSING_KEY_CODE = "missing_api_key"


def _origin_error(response: Any) -> tuple[str, str]:
    """The origin's own `(code, message)`, or empty strings if it sent neither.

    The origin's refusals already say the useful thing — where to get a key,
    when a window resets — so they are relayed rather than paraphrased. A body
    that is not the documented shape is not trusted to be one.
    """
    try:
        body = response.json()
    except Exception:  # noqa: BLE001 - a refusal is not required to be JSON
        return "", ""
    error = body.get("error") if isinstance(body, dict) else None
    if not isinstance(error, dict):
        return "", ""
    code = error.get("code")
    message = error.get("message")
    return (str(code) if code else "", str(message) if message else "")


def _retry_after(response: Any) -> int | None:
    header = str(response.headers.get("retry-after") or "").strip()
    if header.isdigit():
        return int(header)
    try:
        body = response.json()
    except Exception:  # noqa: BLE001 - as above
        return None
    error = body.get("error") if isinstance(body, dict) else None
    seconds = error.get("retry_after_seconds") if isinstance(error, dict) else None
    return int(seconds) if isinstance(seconds, int) else None


def _check_refusal(response: Any, origin: str, presented: Credential | None) -> None:
    """Turn the origin's refusal into the typed error that matches it.

    Nothing here interpolates the key. `key_id` is the short fingerprint, which
    identifies the key in the origin's logs without being usable against it.
    """
    status = response.status_code
    if status not in (HTTP_UNAUTHORIZED, HTTP_FORBIDDEN, HTTP_TOO_MANY_REQUESTS):
        return
    code, said = _origin_error(response)
    tail = f" The origin said: {said}" if said else ""
    if status == HTTP_TOO_MANY_REQUESTS:
        seconds = _retry_after(response)
        wait = f" Retry after {seconds}s." if seconds is not None else ""
        raise RateLimitedError(
            f"{origin} rate-limited this key"
            f"{f' (key {presented.key_id})' if presented else ''}."
            f"{wait}{tail}",
            retry_after_seconds=seconds,
        )
    if presented is None or code == MISSING_KEY_CODE:
        raise KeyRequiredError(
            f"{origin} requires an API key and none was presented. Set "
            f"{API_KEY_ENV} in the environment, or pass --api-key (which is "
            f"visible in shell history and in `ps`)." + tail
        )
    raise KeyRejectedError(
        f"{origin} rejected the API key supplied by the {presented.source} "
        f"(key {presented.key_id}). The key value is not shown and was not "
        f"logged.{tail}"
    )


def fetch(origin: str = DEFAULT_ORIGIN, target: Path | None = None,
          credential: Credential | None = None) -> Snapshot:
    """Download the export. The only command that needs the network.

    With no `credential` this is the call it has always been. With one, the key
    rides on an `Authorization` header — never in the URL, never in the cached
    snapshot — and the origin's refusals come back as typed errors.
    """
    import httpx

    directory = target or cache_dir()
    directory.mkdir(parents=True, exist_ok=True)
    payload: dict[str, Any] = {}
    headers = credential.headers() if credential is not None else {}

    def get(route: str) -> Any:
        try:
            response = client.get(origin + route)
        except httpx.HTTPError as exc:
            raise OriginUnreachableError(
                f"could not reach {origin}{route}: {type(exc).__name__}"
            ) from None
        _check_refusal(response, origin, credential)
        response.raise_for_status()
        return response

    with httpx.Client(timeout=60.0, follow_redirects=True, headers=headers) as client:
        for name, route in PARTS.items():
            payload[name] = get(route).json()
        for name, route in OPTIONAL_PARTS.items():
            try:
                payload[name] = get(route).json()
            except (KeyRequiredError, KeyRejectedError, RateLimitedError):
                # A credential problem is a credential problem on any route, and
                # saying so beats a snapshot that silently lost `fit --host`.
                # An unreachable optional route is still skipped, as before.
                raise
            except Exception:  # noqa: BLE001 - optional; `fit --host` reports its absence
                continue
    build = (payload.get("index") or {}).get("build") or {}
    meta = {
        "fetched_at": datetime.now(UTC).isoformat(),
        "origin": origin,
        "build_commit": build.get("commit", "unknown"),
        "built_at": build.get("built_at", "unknown"),
    }
    raw = {"meta": meta, "data": payload}
    final = directory / "snapshot.json"
    # Validate before replacing the cache, so a bad fetch cannot clobber a
    # snapshot that still answers.
    try:
        parsed = _snapshot_from_raw(final, raw)
    except SnapshotInvalid:
        raise
    except (TypeError, ValueError, KeyError) as exc:
        raise SnapshotInvalid(f"fetched export is unreadable or invalid: {exc}") from exc
    raw["meta"]["export_schema_version"] = parsed.export_schema_version
    writes = ((directory / f".snapshot.{os.getpid()}.tmp", final,
               json.dumps(raw).encode("utf-8")),)
    try:
        for tmp, _destination, data in writes:
            tmp.write_bytes(data)
        for tmp, destination, _data in writes:
            tmp.replace(destination)
    finally:
        for tmp, _destination, _data in writes:
            tmp.unlink(missing_ok=True)
    fetched = load(directory)
    decision_fetch = _fetch_decision_files(origin, directory, credential)
    return replace(fetched, decision_fetch=decision_fetch)


def _fetch_decision_files(origin: str, directory: Path,
                          credential: Credential | None) -> dict[str, Any]:
    """Try to refresh the public decision pair without affecting rank fetch."""
    import httpx

    from decision.snapshot import (
        SnapshotIntegrityError,
        load_snapshot_bytes,
        verify_vocabulary,
    )

    class DecisionRouteUnavailable(RuntimeError):  # noqa: N818 - describes route state
        pass

    def download(candidate_origin: str, *, send_credential: bool) -> tuple[bytes, Any]:
        candidate_headers = credential.headers() if credential and send_credential else {}
        with httpx.Client(timeout=60.0, follow_redirects=True,
                          headers=candidate_headers) as client:
            responses = []
            for route in (DECISION_SNAPSHOT_ROUTE, DECISION_VOCABULARY_ROUTE):
                try:
                    response = client.get(candidate_origin + route)
                except httpx.HTTPError as exc:
                    raise DecisionRouteUnavailable(
                        f"could not reach {candidate_origin}{route}: {type(exc).__name__}"
                    ) from None
                if response.status_code in {401, 403, 404}:
                    raise DecisionRouteUnavailable(
                        f"{candidate_origin}{route} returned HTTP {response.status_code}"
                    )
                try:
                    response.raise_for_status()
                except Exception as exc:  # noqa: BLE001 - optional download is reported
                    raise RuntimeError(
                        f"{candidate_origin}{route} returned HTTP {response.status_code}"
                    ) from exc
                responses.append(response)
        return responses[0].content, responses[1].json()

    source = origin
    try:
        try:
            decision_data, vocabulary_raw = download(origin, send_credential=True)
        except DecisionRouteUnavailable:
            if origin.rstrip("/") == DEFAULT_ORIGIN:
                raise
            source = DEFAULT_ORIGIN
            decision_data, vocabulary_raw = download(source, send_credential=False)

        # Public clients verify Ed25519 with the key set pinned in the package.
        # The loader permits hash-only validation only while that set is empty.
        decision = load_snapshot_bytes(
            decision_data, key=None, include_archive=True,
            source=source + DECISION_SNAPSHOT_ROUTE,
        )
        if not isinstance(vocabulary_raw, dict):
            raise SnapshotInvalid("fetched decision vocabulary is not a JSON object")
        if vocabulary_raw.get("snapshot") != decision.snapshot_id:
            raise SnapshotInvalid(
                "fetched decision vocabulary snapshot does not match the decision snapshot "
                f"({vocabulary_raw.get('snapshot')!r} != {decision.snapshot_id!r})"
            )
        vocabulary_status = verify_vocabulary(vocabulary_raw)
        if vocabulary_status != "verified":
            warnings.warn(
                f"the fetched decision vocabulary is {vocabulary_status}: it carries no "
                "Ed25519 signature the CLI can check, so its model and provider names, "
                "outcome records and templates are trusted on the snapshot ID alone.",
                RuntimeWarning,
                stacklevel=2,
            )
    except SnapshotIntegrityError as exc:
        return {"available": False,
                "error": f"fetched decision snapshot failed integrity check: {exc}"}
    except Exception as exc:  # noqa: BLE001 - decision data is optional for rank fetch
        return {"available": False, "error": str(exc)}

    root = _decision_root(directory)
    generation = root / decision.snapshot_id
    temporary = root / f".tmp-{os.getpid()}-{secrets.token_hex(6)}"
    current_tmp = root / f".current-{os.getpid()}.tmp"
    try:
        root.mkdir(parents=True, exist_ok=True)
        temporary.mkdir()
        (temporary / DECISION_SNAPSHOT_FILENAME).write_bytes(decision_data)
        (temporary / DECISION_VOCABULARY_FILENAME).write_text(
            json.dumps(vocabulary_raw), encoding="utf-8"
        )
        _validate_decision_generation(temporary, require_named=False)
        if generation.exists():
            try:
                _validate_decision_generation(generation)
                cached_vocabulary = json.loads(
                    (generation / DECISION_VOCABULARY_FILENAME).read_text(encoding="utf-8"))
                stale = cached_vocabulary != vocabulary_raw
            except (OSError, ValueError, KeyError, json.JSONDecodeError):
                stale = True
            if stale:
                shutil.rmtree(generation)
                os.replace(temporary, generation)
            else:
                shutil.rmtree(temporary)
        else:
            os.replace(temporary, generation)
        current_tmp.write_text(decision.snapshot_id + "\n", encoding="utf-8")
        os.replace(current_tmp, root / "current")
    except Exception as exc:  # noqa: BLE001 - decision data cannot fail rank fetch
        return {"available": False, "error": f"could not cache decision generation: {exc}"}
    finally:
        try:
            current_tmp.unlink(missing_ok=True)
        except OSError:
            pass
        shutil.rmtree(temporary, ignore_errors=True)

    _prune_decision_generations(root, decision.snapshot_id)
    return {
        "available": True,
        "origin": source,
        "snapshot_id": decision.snapshot_id,
        "signature_verified": decision.signature_verified,
        "signature_status": decision.signature_status,
        "signature_key_id": decision.signature_key_id,
        "vocabulary_signature": vocabulary_status,
    }


def _prune_decision_generations(root: Path, current_id: str) -> None:
    """Keep the active and previous generations; cleanup must not fail fetch."""
    try:
        generations = [
            path for path in root.iterdir()
            if path.is_dir() and not path.name.startswith(".tmp-")
        ]
        generations.sort(key=lambda path: path.stat().st_mtime, reverse=True)
        previous = [path.name for path in generations if path.name != current_id][:1]
        keep = {current_id, *previous}
        for path in generations:
            if path.name not in keep:
                shutil.rmtree(path, ignore_errors=True)
        for path in root.glob(".tmp-*"):
            shutil.rmtree(path, ignore_errors=True)
    except OSError:
        pass


def load(directory: Path | None = None) -> Snapshot:
    """Read the cached snapshot. Never touches the network."""
    path = (directory or cache_dir()) / "snapshot.json"
    if not path.exists():
        raise SnapshotMissing(
            f"no snapshot at {path}. Run `modelspec snapshot fetch` once; "
            "everything after that works offline."
        )
    try:
        if not path.is_file():
            raise ValueError("snapshot.json is not a regular file")
        raw = json.loads(path.read_text(encoding="utf-8"))
        return _snapshot_from_raw(path, raw)
    except SnapshotInvalid:
        raise
    except (OSError, UnicodeError, TypeError, ValueError, KeyError, json.JSONDecodeError) as exc:
        raise SnapshotInvalid(f"snapshot at {path} is unreadable or invalid: {exc}") from exc


def status(directory: Path | None = None) -> dict[str, Any]:
    directory = directory or cache_dir()
    generation, generation_error = _current_decision_generation(directory)
    decision_path = ((generation / DECISION_SNAPSHOT_FILENAME) if generation else
                     (_decision_root(directory) / "current"))
    if generation is not None:
        from decision.snapshot import load_snapshot

        try:
            decision = load_snapshot(decision_path, key=None, include_archive=True)
            decision_status: dict[str, Any] = {
                "present": True,
                "valid": True,
                "path": str(decision_path),
                "snapshot_id": decision.snapshot_id,
                "as_of": decision.as_of.isoformat() if decision.as_of else None,
                "age_days": round(age_of(decision_path), 2),
                "signature_verified": decision.signature_verified,
                "signature_status": decision.signature_status,
                "signature_key_id": decision.signature_key_id,
            }
        except (OSError, ValueError) as exc:
            decision_status = {
                "present": True,
                "valid": False,
                "path": str(decision_path),
                "error": f"cached decision snapshot is invalid: {exc}",
            }
    elif generation_error is not None:
        decision_status = {
            "present": True,
            "valid": False,
            "path": str(decision_path),
            "error": f"cached decision snapshot is invalid: {generation_error}",
        }
    else:
        decision_status = {"present": False, "path": str(decision_path)}
    try:
        snap = load(directory)
    except SnapshotMissing as exc:
        return {"present": False, "message": str(exc),
                "decision_snapshot": decision_status}
    size = snap.path.stat().st_size
    return {"present": True, "size_bytes": size, "path": str(snap.path),
            "decision_snapshot": decision_status, **snap.freshness()}


def age_of(path: Path) -> float:
    return (time.time() - path.stat().st_mtime) / 86400
