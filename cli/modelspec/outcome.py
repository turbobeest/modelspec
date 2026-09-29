"""Local, opt-in outcome records (MODEL-211; ADR 0004 step 1, REV-9).

An outcome record answers one question: was this recommendation adopted, and
did the task succeed? It holds nothing else. Every field is a closed literal, a
pattern-bound identifier, a bounded number or a boolean, so there is no field a
prompt, a key value or a customer name can be written into, and the model
refuses any field it does not name (``extra="forbid"``).

Everything here stays on this machine, under ``~/.modelspec`` (or
``MODELSPEC_HOME``). Nothing in this module opens a network connection; upload
is a separate, unbuilt design (``docs/design/outcome-upload.md``).
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
from collections.abc import Iterator
from datetime import UTC, datetime
from importlib import metadata
from pathlib import Path
from typing import Annotated, Any, Literal

from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    Field,
    StrictBool,
    StrictInt,
    TypeAdapter,
    model_validator,
)

from decision import contract

#: Bump when the consent text below changes what is recorded; an older consent
#: then no longer counts and ``enable`` must be run again.
CONSENT_VERSION = 1
#: The outcome record's own format. A new field is a new version.
RECORD_VERSION = 1
#: How many decision stubs ``decide`` keeps for ``record`` to resolve against.
STUB_LIMIT = 500

OUTCOMES_FILENAME = "outcomes.jsonl"
CONSENT_FILENAME = "outcomes-consent.json"
STUB_DIRECTORY = "decision-stubs"

RESULTS = ("success", "partial", "failure")
#: The adopted model when it is not in the ModelSpec catalogue. Its name is
#: never recorded: a private fine-tune's name can identify a customer.
OTHER = "other"

#: Exactly what the engine emits: "dec_" + sha256(spec_hash + snapshot)[:24]
#: (``decision/engine.py``). The contract's looser ``dec_<id>`` would carry text.
DECISION_ID_PATTERN = r"^dec_[0-9a-f]{24}$"
#: Exactly what ``decision.snapshot.snapshot_id_for`` emits.
SNAPSHOT_PATTERN = r"^snap_[0-9a-f]{16}$"
PROVIDER_PATTERN = r"^[a-z0-9][a-z0-9_-]{0,63}$"
CONTRACT_VERSION_PATTERN = r"^[0-9]{1,3}\.[0-9]{1,3}$"
#: A public release: no ``+local`` segment, which can carry a hostname or a git hash.
CLI_VERSION_PATTERN = r"^[0-9]{1,4}(\.[0-9]{1,4}){1,3}((a|b|rc)[0-9]{1,4})?(\.post[0-9]{1,4})?(\.dev[0-9]{1,4})?$"
#: Minute precision, UTC. Enough to order records; no finer.
RECORDED_AT_PATTERN = r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}Z$"

MAX_LATENCY_MS = 86_400_000  # one day
MAX_COST_USD = 10_000.0
MAX_ID_LENGTH = 128
#: Latency and cost are kept to this many significant figures, so neither can
#: carry more than a coarse measurement.
SIGNIFICANT_FIGURES = 3

CONSENT_TEXT = f"""\
ModelSpec outcome recording (consent version {CONSENT_VERSION})

When this is on, `modelspec outcome record` appends one line per call to
  {{path}}
Each line holds exactly these fields and nothing else:

  decision_id       the decision you acted on (dec_...)
  spec_hash         the hash of that decision's spec, not the spec itself
  snapshot          the ModelSpec snapshot the decision used
  contract_version  the decision contract version
  adopted_model     the model you used, if it is in the ModelSpec catalogue;
                    otherwise the word "other", never its name
  adopted_offering  the provider you used it through, if it is catalogued
  was_leader        whether that model was the decision's leader
  in_best_band      whether it was in the decision's best band
  result            success, partial or failure
  task_kind         optional, one of a fixed list (bug_fix, refactor, ...)
  latency_ms        optional, milliseconds, rounded to 3 significant figures
  cost_usd          optional, US dollars, rounded to 3 significant figures
  recorded_at       the time, to the minute, in UTC
  cli_version       this CLI's public release number
  record_version    the version of this record format

It never records your prompt or task text, your API keys or whether you have
them, file or repository names, user, customer or machine identifiers, or
anything else. A field the list above does not name is refused.

While this is on, `modelspec decide` also keeps the decision ID, spec hash,
snapshot, leader and best-band model IDs of up to {STUB_LIMIT} recent
decisions under {{stubs}}, so `record` can tell whether you adopted the leader.

Nothing is sent anywhere. The records stay on this machine until you delete
them. Turn it off at any time with:

  modelspec outcome disable            stop recording
  modelspec outcome disable --delete   stop recording and delete every record
"""


def _pattern(pattern: str, what: str, *, max_length: int = MAX_ID_LENGTH) -> Any:
    """A bounded string matching ``pattern``. The error never echoes the value."""
    compiled = re.compile(pattern)

    def check(value: str) -> str:
        if not compiled.fullmatch(value):
            raise ValueError(f"{what} (pattern {pattern})")
        return value

    return Annotated[str, Field(max_length=max_length), AfterValidator(check)]


DecisionId = _pattern(DECISION_ID_PATTERN, "a decision ID is dec_ and 24 hex")
SpecHash = _pattern(contract.SPEC_HASH_PATTERN, "a spec hash is sha256:<64 hex>")
SnapshotId = _pattern(SNAPSHOT_PATTERN, "a snapshot ID is snap_ and 16 hex")
ModelId = _pattern(contract.MODEL_PATTERN, "a model ID is lab/model")
ProviderId = _pattern(PROVIDER_PATTERN, "a provider is a lowercase slug")
ContractVersion = _pattern(CONTRACT_VERSION_PATTERN, "a contract version is major.minor")
CliVersion = _pattern(CLI_VERSION_PATTERN, "a CLI version is a release number")
RecordedAt = _pattern(RECORDED_AT_PATTERN, "recorded_at is YYYY-MM-DDTHH:MMZ, UTC")


def _finite(value: float) -> float:
    if not math.isfinite(value):
        raise ValueError("cost_usd must be a finite number")
    return value


def _coarse(value: float) -> float:
    """``value`` to ``SIGNIFICANT_FIGURES`` significant figures."""
    if value == 0 or not math.isfinite(value):
        return value
    return round(value, SIGNIFICANT_FIGURES - 1 - math.floor(math.log10(abs(value))))


def _coarse_int(value: int) -> int:
    if not math.isfinite(value) or value < 0:
        return value
    return int(_coarse(float(value)))


def _is_coarse(value: float) -> float:
    if _coarse(value) != value:
        raise ValueError(f"must be rounded to {SIGNIFICANT_FIGURES} significant figures")
    return value


class _Strict(BaseModel):
    """Unknown fields are refused, types are not coerced, and records are frozen."""

    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)


class OutcomeRecord(_Strict):
    """One outcome. These fields and no others; see ``CONSENT_TEXT``."""

    record_version: Literal[1]
    decision_id: DecisionId
    spec_hash: SpecHash | None
    snapshot: SnapshotId | None
    contract_version: ContractVersion | None
    adopted_model: ModelId | Literal["other"]
    adopted_offering: ProviderId | None
    was_leader: StrictBool | None
    in_best_band: StrictBool | None
    result: Literal["success", "partial", "failure"]
    task_kind: contract.TaskType | None
    latency_ms: Annotated[StrictInt, Field(ge=0, le=MAX_LATENCY_MS),
                          AfterValidator(_is_coarse)] | None
    cost_usd: Annotated[float, Field(ge=0, le=MAX_COST_USD),
                        AfterValidator(_finite), AfterValidator(_is_coarse)] | None
    recorded_at: RecordedAt
    cli_version: CliVersion | None


class DecisionStub(_Strict):
    """What ``record`` needs from a decision to say whether it was adopted."""

    decision_id: DecisionId
    spec_hash: SpecHash
    snapshot: SnapshotId
    contract_version: ContractVersion
    leader: ModelId | None
    best: list[ModelId] = Field(max_length=64)

    @model_validator(mode="after")
    def _bound(self) -> DecisionStub:
        # The ID is a hash of the other two, so a hand-made stub cannot pair
        # a real ID with made-up fields.
        digest = hashlib.sha256((self.spec_hash + self.snapshot).encode()).hexdigest()
        if self.decision_id != "dec_" + digest[:24]:
            raise ValueError("decision_id does not match spec_hash and snapshot")
        return self


_DECISION_ID = TypeAdapter(DecisionId)


def check_decision_id(value: str) -> str:
    """Validate a decision ID; the error never echoes it."""
    return _DECISION_ID.validate_python(value)


# ── where things live ─────────────────────────────────────────────────────


def home() -> Path:
    override = os.environ.get("MODELSPEC_HOME")
    return Path(override).expanduser() if override else Path("~/.modelspec").expanduser()


def outcomes_path() -> Path:
    return home() / OUTCOMES_FILENAME


def consent_path() -> Path:
    return home() / CONSENT_FILENAME


def stubs_path() -> Path:
    return home() / STUB_DIRECTORY


def consent_text() -> str:
    return CONSENT_TEXT.format(path=outcomes_path(), stubs=stubs_path())


def _private_dir(path: Path) -> None:
    """Create ``path`` 0700, and tighten it if it already existed looser."""
    path.mkdir(mode=0o700, parents=True, exist_ok=True)
    home().chmod(0o700)
    path.chmod(0o700)


def open_private(path: Path, flags: int) -> int:
    """Open a file 0600 without following a symlink, tightening an existing one."""
    descriptor = os.open(path, flags | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    os.fchmod(descriptor, 0o600)
    return descriptor


def _write_private(path: Path, text: str) -> None:
    _private_dir(path.parent)
    temporary = path.with_name(path.name + ".tmp")
    temporary.unlink(missing_ok=True)
    descriptor = open_private(temporary, os.O_WRONLY | os.O_EXCL)
    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        handle.write(text)
    os.replace(temporary, path)


# ── consent ───────────────────────────────────────────────────────────────


def enabled() -> bool:
    """True only for a consent file naming the current consent version."""
    try:
        value = json.loads(consent_path().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False
    return (isinstance(value, dict) and set(value) == {"consent_version"}
            and type(value["consent_version"]) is int
            and value["consent_version"] == CONSENT_VERSION)


def enable() -> None:
    _write_private(consent_path(), json.dumps({"consent_version": CONSENT_VERSION}) + "\n")


def disable(*, delete: bool) -> int:
    """Stop recording and drop the decision stubs; with ``delete``, the records too.

    Returns how many records remain on disk.
    """
    consent_path().unlink(missing_ok=True)
    stubs = stubs_path()
    if stubs.is_dir():
        for stub in stubs.iterdir():
            stub.unlink(missing_ok=True)
        try:
            stubs.rmdir()
        except OSError:
            pass
    if delete:
        outcomes_path().unlink(missing_ok=True)
        return 0
    return sum(1 for _ in _lines())


# ── decision stubs ────────────────────────────────────────────────────────


def stub_from_decision(decision: dict[str, Any]) -> DecisionStub:
    """Take only the stub's fields from a decision's JSON; drop everything else."""
    bands = decision.get("bands") or {}
    answer = decision.get("answer") or {}
    if not isinstance(bands, dict) or not isinstance(answer, dict):
        raise ValueError("bands and answer must be objects")
    entries = bands.get("best") or []
    if not isinstance(entries, list) or not all(isinstance(entry, dict) for entry in entries):
        raise ValueError("bands.best must be a list of objects")
    best = [entry.get("model") for entry in entries]
    if not best and answer:
        best = list(answer.get("members") or [])
    leader = bands.get("leader") or answer.get("leader") or (best[0] if best else None)
    return DecisionStub(
        decision_id=decision["decision_id"],
        spec_hash=decision["spec_hash"],
        snapshot=decision["snapshot"],
        contract_version=decision["contract_version"],
        leader=leader,
        best=best,
    )


def save_stub(stub: DecisionStub) -> None:
    """Keep a stub, and at most ``STUB_LIMIT`` of them. Only when recording is on."""
    if not enabled():
        return
    directory = stubs_path()
    _write_private(directory / f"{stub.decision_id}.json", stub.model_dump_json() + "\n")
    stubs = sorted(directory.glob("*.json"), key=lambda path: path.stat().st_mtime)
    for old in stubs[:-STUB_LIMIT]:
        old.unlink(missing_ok=True)


def load_stub(decision_id: str) -> DecisionStub | None:
    if re.fullmatch(DECISION_ID_PATTERN, decision_id) is None:
        return None
    try:
        text = (stubs_path() / f"{decision_id}.json").read_text(encoding="utf-8")
        return DecisionStub.model_validate_json(text)
    except (OSError, ValueError):
        return None


# ── records ───────────────────────────────────────────────────────────────


def cli_version() -> str | None:
    for distribution in ("modelspec-dev", "modelspec"):
        try:
            version = metadata.version(distribution)
        except metadata.PackageNotFoundError:
            continue
        # The public part only: a local segment (+hostname, +g<hash>) is dropped,
        # and a version the pattern still refuses is unknown, not an error.
        public = version.split("+", 1)[0]
        return public if re.fullmatch(CLI_VERSION_PATTERN, public) else None
    return None


def now_minute() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%MZ")


def build_record(
    *,
    decision_id: str,
    stub: DecisionStub | None,
    adopted_model: str,
    adopted_offering: str | None,
    result: str,
    task_kind: str | None,
    latency_ms: int | None,
    cost_usd: float | None,
) -> OutcomeRecord:
    """Validate CLI input into a record; anything off-schema raises ``ValidationError``."""
    return OutcomeRecord.model_validate({
        "record_version": RECORD_VERSION,
        "decision_id": decision_id,
        "spec_hash": stub.spec_hash if stub else None,
        "snapshot": stub.snapshot if stub else None,
        "contract_version": stub.contract_version if stub else None,
        "adopted_model": adopted_model,
        "adopted_offering": adopted_offering,
        "was_leader": (adopted_model == stub.leader) if stub else None,
        "in_best_band": (adopted_model in stub.best) if stub else None,
        "result": result,
        "task_kind": task_kind,
        "latency_ms": _coarse_int(latency_ms) if latency_ms is not None else None,
        "cost_usd": _coarse(cost_usd) if cost_usd is not None else None,
        "recorded_at": now_minute(),
        "cli_version": cli_version(),
    })


def append(record: OutcomeRecord) -> None:
    """Append one validated record. Only when recording is on."""
    if not enabled():
        raise PermissionError("outcome recording is off")
    path = outcomes_path()
    _private_dir(path.parent)
    line = OutcomeRecord.model_validate_json(record.model_dump_json()).model_dump_json()
    descriptor = open_private(path, os.O_WRONLY | os.O_APPEND)
    with os.fdopen(descriptor, "a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def _lines() -> Iterator[str]:
    try:
        with outcomes_path().open(encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    yield line
    except FileNotFoundError:
        return


def read() -> tuple[list[OutcomeRecord], int]:
    """Every record that still matches the schema, and how many lines did not.

    A hand-edited line with an extra field is refused here too, so ``show``
    and ``export`` can never emit more than the schema.
    """
    records: list[OutcomeRecord] = []
    refused = 0
    for line in _lines():
        try:
            records.append(OutcomeRecord.model_validate_json(line))
        except ValueError:
            refused += 1
    return records, refused
