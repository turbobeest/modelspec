"""The decision contract (MODEL-135).

A **spec** asks for a decision: conditions on facets, one objective, how much
explanation to return. A **decision** answers one spec against one snapshot.
The public document is ``docs/decision-contract.md``; the JSON Schema in
``docs/decision-contract.schema.json`` is generated from these types, and
``tests/test_decision_contract.py`` keeps the three in agreement.

Conditions have two spellings that parse to the same type: the YAML form (a
mapping) and the compact string form (``swe_bench_pro >= 55 @independent``).
``render_condition`` writes the canonical compact form back out.
"""

from __future__ import annotations

import hashlib
import json
import re
import typing
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import date
from functools import cache
from typing import Annotated, Any, Literal

import yaml
from pydantic import (
    AfterValidator,
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Discriminator,
    Field,
    SerializerFunctionWrapHandler,
    StringConstraints,
    Tag,
    ValidationError,
    WithJsonSchema,
    field_validator,
    model_serializer,
    model_validator,
)
from pydantic.fields import FieldInfo

CONTRACT_VERSION = "2.10"

# ── identifiers ────────────────────────────────────────────────────────────

FACET_PATTERN = r"^[a-z][a-z0-9_-]*(\.[a-z0-9_-]+)*$"
SIGNED_FACET_PATTERN = r"^-?[a-z][a-z0-9_-]*(\.[a-z0-9_-]+)*$"
#: A refinement's weight key, ``<parent domain or any>/<refinement>`` (MODEL-190).
REFINEMENT_KEY_PATTERN = r"^[a-z][a-z0-9_]*/[a-z][a-z0-9_]*$"
#: A weights key: a signed facet ID, or a signed refinement key. Added in 2.4.
WEIGHT_KEY_PATTERN = r"^-?[a-z][a-z0-9_-]*(\.[a-z0-9_-]+)*(/[a-z][a-z0-9_]*)?$"
MODEL_PATTERN = r"^[a-z0-9][a-z0-9._-]*/[a-z0-9][a-z0-9._-]*$"
HARNESS_PATTERN = r"^[a-z0-9][a-z0-9-]*@[0-9]+\.[0-9]+$"
HARNESS_NAME_PATTERN = r"^[a-z0-9][a-z0-9-]*$"
EFFORT_PATTERN = r"^[a-z0-9_-]+$"
SNAPSHOT_PATTERN = r"^snap_[A-Za-z0-9:._-]+$"
PROFILE_PATTERN = r"^profile:[a-z0-9][a-z0-9-]*$"
SAVE_AS_PATTERN = r"^[a-z0-9][a-z0-9-]{0,63}$"
DECISION_ID_PATTERN = r"^dec_[0-9A-Za-z]{8,}$"
SPEC_HASH_PATTERN = r"^sha256:[0-9a-f]{64}$"
CODE_PATTERN = r"^[a-z0-9_]+$"
URL_PATTERN = r"^https?://\S+$"


def _matching(pattern: str, what: str) -> Any:
    """A string type that fails with a message a person can act on."""
    compiled = re.compile(pattern)

    def check(value: str) -> str:
        if not compiled.fullmatch(value):
            raise ValueError(f"{what} (pattern {pattern}); got {value!r}")
        return value

    return Annotated[str, AfterValidator(check),
                     WithJsonSchema({"type": "string", "pattern": pattern})]


FacetId = _matching(FACET_PATTERN, "a facet ID is lowercase, dotted")
SignedFacetId = _matching(SIGNED_FACET_PATTERN,
                          "a facet ID is lowercase, dotted, with an optional leading - to minimise")
WeightKey = _matching(WEIGHT_KEY_PATTERN,
                      "a weights key is a facet ID, or a refinement key such as "
                      "software_engineering/rust, with an optional leading - to minimise")
RefinementKey = _matching(
    REFINEMENT_KEY_PATTERN,
    "a refinement key is <domain>/<refinement>, e.g. software_engineering/rust",
)
ModelId = _matching(MODEL_PATTERN, "a model ID is lab/model")
HarnessId = _matching(HARNESS_PATTERN, "a harness ID is name@major.minor, e.g. claude-code@2.1")
HarnessName = _matching(HARNESS_NAME_PATTERN,
                        "a harness is a registered name without a version, e.g. claude-code")
Effort = _matching(EFFORT_PATTERN, "an effort is a lowercase word")
SnapshotId = _matching(SNAPSHOT_PATTERN,
                       "a decision cites a snapshot ID like snap_2026-09-24T06:00Z")
ProfileId = _matching(PROFILE_PATTERN, "a profile ID is profile:<name>")
SaveAs = _matching(SAVE_AS_PATTERN, "save_as is a lowercase slug")
DecisionId = _matching(DECISION_ID_PATTERN, "a decision ID is dec_<id>")
SpecHash = _matching(SPEC_HASH_PATTERN, "a spec hash is sha256:<64 hex>")
Code = _matching(CODE_PATTERN, "a warning is a lowercase code")
Url = _matching(URL_PATTERN, "a source is an http(s) URL")


def _snapshot_ref(value: str) -> str:
    if value != "latest" and not re.fullmatch(SNAPSHOT_PATTERN, value):
        raise ValueError(f"must be 'latest' or a snapshot ID like snap_2026-09-24T06:00Z; "
                         f"got {value!r}")
    return value


SnapshotRef = Annotated[
    str, AfterValidator(_snapshot_ref),
    WithJsonSchema({"anyOf": [{"const": "latest"},
                              {"type": "string", "pattern": SNAPSHOT_PATTERN}]}),
]

# ── closed vocabularies ────────────────────────────────────────────────────

Op = Literal["=", "!=", "<", "<=", ">", ">="]
ORDERED_OPS = frozenset({"<", "<=", ">", ">="})
UnknownPolicy = Literal["list", "fail", "pass"]
MeasuredByQualifier = Literal["independent", "provider_self_report", "any"]
MeasuredBy = Literal["benchmark_author", "independent", "provider_self_report", "modelspec",
                     "outcome_protocol"]
Explain = Literal["none", "summary", "full"]
Status = Literal["answered", "partial", "no_feasible"]
ModelRowStatus = Literal["ranked", "may_qualify", "eliminated"]
DateType = Literal["observed", "published"]
Directness = Literal["direct", "proxy"]
CapabilityLevel = Literal["required", "preferred"]
PreferenceStatus = Literal["satisfied", "not_satisfied", "unknown"]
#: How an answer held up, as a person or an agent tells ModelSpec (MODEL-221).
#: The same five values `api/worker/src/feedback_service.py` accepts.
FeedbackRating = Literal["reliable", "unreliable", "trustworthy", "untrustworthy", "confusing"]
FEEDBACK_ENDPOINT = "https://api.modelspec.dev/v1/feedback"
FEEDBACK_SCHEMA = "https://modelspec.dev/api/feedback/v1.schema.json"
FEEDBACK_CLI = "modelspec feedback <decision_id> --rating <rating>"
# The outcome protocol's task types (DPF integration spec §9.3).
TaskType = Literal["new_feature", "bug_fix", "refactor", "test_writing", "docs", "migration",
                   "performance", "security_fix", "review", "analysis", "data_transform",
                   "config_infra"]

# Compact qualifier keywords that take no argument, and what they set.
_FLAG_QUALIFIERS: dict[str, tuple[str, Any]] = {
    "@independent": ("measured_by", "independent"),
    "@provider_self_report": ("measured_by", "provider_self_report"),
    "@any": ("measured_by", "any"),
    "@default_effort": ("effort", "default"),
    "@max_effort": ("effort", "max"),
    "@direct": ("direct", True),
}
_ARG_QUALIFIERS = {"@effort": "effort", "@harness": "harness"}
QUALIFIER_KEYWORDS = (*_FLAG_QUALIFIERS, "@effort(x)", "@harness(x)", "measured_after")

# Value types a facet can have that carry no order, so <, >, windows and max/min
# on them are refused. Any other value type from the registry is taken as ordered.
UNORDERED_VALUE_TYPES = frozenset({"bool", "boolean", "enum", "string", "str", "text", "set",
                                   "list"})


def _iso_date(value: Any) -> Any:
    if isinstance(value, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        try:
            return date.fromisoformat(value)
        except ValueError:
            raise ValueError(f"{value} is not a real date") from None
    return value


Scalar = Annotated[bool | int | float | date | str, BeforeValidator(_iso_date)]
#: For a field named ``date``, whose default would shadow the type in its class.
Day = date


#: ``Field(exclude_if=...)`` arrived in pydantic 2.12. Older versions, such as
#: the 2.10.6 that Pyodide gives the Worker, keep the predicate in
#: ``json_schema_extra`` and emit the field anyway, so the Worker's bytes drifted
#: from the CLI's. On those versions ``_Strict`` applies the predicate itself.
NATIVE_EXCLUDE_IF = "exclude_if" in FieldInfo.__slots__


@cache
def _exclude_if_fields(model_type: type[BaseModel]) -> tuple:
    fields = []
    for name, field in model_type.model_fields.items():
        extra = field.json_schema_extra
        excluded = getattr(field, "exclude_if", None) or (
            extra.get("exclude_if") if isinstance(extra, dict) else None)
        if callable(excluded):
            fields.append((name, field.serialization_alias or field.alias, excluded))
    return tuple(fields)


def apply_exclude_if(model: BaseModel, data: dict[str, Any]) -> dict[str, Any]:
    """Apply the native exclusion predicates on older Worker pydantic.

    Field metadata is fixed when pydantic builds each contract type. Inspect
    it once per type, rather than once per field of every serialized row.
    """
    for name, alias, excluded in _exclude_if_fields(type(model)):
        key = name if name in data else alias
        if key in data and excluded(getattr(model, name)):
            del data[key]
    return data


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    if not NATIVE_EXCLUDE_IF:
        @model_serializer(mode="wrap")
        def _exclude_if(self, handler: SerializerFunctionWrapHandler) -> dict[str, Any]:
            return apply_exclude_if(self, handler(self))


# ── conditions ─────────────────────────────────────────────────────────────


class Soft(_Strict):
    """A soft condition: violating it costs ``penalty`` of the objective instead of eliminating."""

    penalty: float = Field(gt=0, le=1)


class ModelRef(_Strict):
    """The right-hand side of a relative condition: ``coding >= model(openai/gpt-6-sol)``."""

    model: ModelId


class EvidenceQualifiers(_Strict):
    """Which evidence may satisfy a condition on an evidence facet."""

    measured_by: MeasuredByQualifier | None = None
    effort: Effort | None = None
    harness: HarnessId | None = None
    measured_after: date | None = None
    direct: bool = False

    def is_empty(self) -> bool:
        return self == EvidenceQualifiers()


def _drop_empty_qualifiers(value: Any) -> Any:
    return None if isinstance(value, EvidenceQualifiers) and value.is_empty() else value


Qualifiers = Annotated[EvidenceQualifiers | None, AfterValidator(_drop_empty_qualifiers)]


class Compare(_Strict):
    """``facet op value``; the value may be ``model(<id>)`` for a relative condition."""

    facet: FacetId
    op: Op
    value: ModelRef | Scalar
    qualifiers: Qualifiers = None
    soft: Soft | None = None
    unknown: UnknownPolicy | None = None


class Window(_Strict):
    """``facet in [low, high]``, both ends inclusive."""

    facet: FacetId
    between: tuple[Scalar, Scalar]
    qualifiers: Qualifiers = None
    soft: Soft | None = None
    unknown: UnknownPolicy | None = None

    @field_validator("between")
    @classmethod
    def _ordered(cls, value: tuple[Any, Any]) -> tuple[Any, Any]:
        low, high = value
        if _kind(low) != _kind(high) or _kind(low) in ("bool", "str"):
            raise ValueError("window ends must both be numbers or both be dates")
        if low > high:
            raise ValueError(f"window low bound {low} is above its high bound {high}")
        return value


class InSet(_Strict):
    """``facet in {a, b}`` or ``facet not in {a, b}``. Values are kept sorted and unique."""

    facet: FacetId
    in_: list[Scalar] | None = Field(default=None, alias="in")
    not_in: list[Scalar] | None = None
    soft: Soft | None = None
    unknown: UnknownPolicy | None = None

    @field_validator("in_", "not_in")
    @classmethod
    def _canonical(cls, value: list[Any] | None) -> list[Any] | None:
        if value is None:
            return None
        if not value:
            raise ValueError("the set is empty")
        unique = {json.dumps(v, default=str, sort_keys=True): v for v in value}
        return [unique[k] for k in sorted(unique)]

    @model_validator(mode="after")
    def _one_side(self) -> InSet:
        if (self.in_ is None) == (self.not_in is None):
            raise ValueError("a set condition takes exactly one of in, not_in")
        return self


class Known(_Strict):
    """``known(facet)``: passes when the facet is known. It is never unknown itself."""

    known: FacetId
    soft: Soft | None = None


def _at_least_two(value: list[Any]) -> list[Any]:
    if len(value) < 2:
        raise ValueError("a group needs at least two conditions")
    return value


class AnyOf(_Strict):
    any: Annotated[list[Condition], AfterValidator(_at_least_two)]
    soft: Soft | None = None
    unknown: UnknownPolicy | None = None


class AllOf(_Strict):
    all: Annotated[list[Condition], AfterValidator(_at_least_two)]
    soft: Soft | None = None
    unknown: UnknownPolicy | None = None


class NotOf(_Strict):
    not_: Condition = Field(alias="not")
    soft: Soft | None = None
    unknown: UnknownPolicy | None = None


CONDITION_TYPES = (Compare, Window, InSet, Known, AnyOf, AllOf, NotOf)
LEAF_TYPES = (Compare, Window, InSet, Known)


class ConditionError(ValueError):
    """An invalid condition: which one, on which field, and why."""

    def __init__(self, condition: str, field: str | None, reason: str, path: str = "") -> None:
        super().__init__(f"{condition!r}: {reason}")
        self.condition = condition
        self.field = field
        self.reason = reason
        self.path = path


def _coerce_condition(raw: Any) -> Any:
    if isinstance(raw, CONDITION_TYPES):
        return raw
    return parse_condition(raw)


Condition = Annotated[
    Compare | Window | InSet | Known | AnyOf | AllOf | NotOf,
    BeforeValidator(_coerce_condition,
                    json_schema_input_type=str | Compare | Window | InSet | Known | AnyOf | AllOf
                    | NotOf),
]

for _group in (AnyOf, AllOf, NotOf):
    _group.model_rebuild()


# ── parsing conditions ─────────────────────────────────────────────────────


def parse_condition(raw: str | Mapping[str, Any], _path: str = "") -> Any:
    """Parse one condition in either form. Raises ``ConditionError``."""
    if isinstance(raw, str):
        return _parse_compact(raw, _path)
    if isinstance(raw, Mapping):
        return _from_mapping(raw, _path, text=None)
    raise ConditionError(repr(raw), None, "a condition is a string or a mapping", _path)


_STRUCTURAL_KEYS = {"facet", "known", "any", "all", "not"}


def _from_mapping(raw: Mapping[str, Any], path: str, text: str | None) -> Any:
    text = text if text is not None else _describe(raw)
    keys = set(raw)
    if len(keys) == 1 and not keys & _STRUCTURAL_KEYS:
        [(key, value)] = raw.items()
        raise ConditionError(
            f"{key}: {value}", None,
            "YAML split this condition at ': '; quote it, or write soft(0.2) and unknown(fail) "
            "in the compact form", path)
    for group, cls in (("any", AnyOf), ("all", AllOf)):
        if group in keys:
            children = raw[group]
            if not isinstance(children, list):
                raise ConditionError(text, None, f"{group} takes a list of conditions", path)
            built = [parse_condition(child, _join(path, f"{group}[{i}]"))
                     for i, child in enumerate(children)]
            return _build(cls, {**raw, group: built}, text, None, path)
    if "not" in keys:
        child = parse_condition(raw["not"], _join(path, "not"))
        return _build(NotOf, {**raw, "not": child}, text, None, path)
    if "known" in keys:
        field = raw["known"] if isinstance(raw["known"], str) else None
        if "unknown" in keys:
            raise ConditionError(text, field,
                                 "known() is never unknown, so it takes no unknown policy", path)
        return _build(Known, raw, text, field, path)
    if "facet" in keys:
        field = raw["facet"] if isinstance(raw["facet"], str) else None
        if "op" in keys or "value" in keys:
            return _build(Compare, raw, text, field, path)
        if "between" in keys:
            return _build(Window, raw, text, field, path)
        if "in" in keys or "not_in" in keys:
            return _build(InSet, raw, text, field, path)
        raise ConditionError(text, field,
                             "a facet condition needs op and value, between, in, or not_in", path)
    raise ConditionError(text, None,
                         "not a condition: expected facet, known, any, all or not", path)


def _build(cls: type[BaseModel], data: Mapping[str, Any], text: str, field: str | None,
           path: str) -> Any:
    try:
        return cls.model_validate(data)
    except ValidationError as exc:
        errors = exc.errors()
        # A failed union reports every member; the value_error is the one that says why.
        first = next((e for e in errors if e["type"] == "value_error"), errors[0])
        nested = first.get("ctx", {}).get("error")
        if isinstance(nested, ConditionError):
            raise nested from None
        where = _loc(first["loc"])
        reason = _message(first)
        raise ConditionError(text, field, f"{where}: {reason}" if where else reason,
                             path) from None


def _describe(raw: Any) -> str:
    return json.dumps(raw, default=str, sort_keys=True)


def _join(path: str, part: str) -> str:
    return f"{path}.{part}" if path else part


# The compact grammar, tokenised. A word may contain ':' (aws-bedrock:us-east-1)
# and '@' (claude-code@2.1); a trailing ':' is split off so `unknown: fail` reads.
_TOKEN = re.compile(r"""
    (?P<space>\s+)
  | (?P<str>"(?:[^"\\]|\\.)*")
  | (?P<op>==|<=|>=|!=|=|<|>)
  | (?P<punct>[\[\]{}(),;])
  | (?P<qual>@[a-z_]+)
  | (?P<word>-?[A-Za-z0-9_][A-Za-z0-9_.:/+@-]*)
""", re.X)
_INT = re.compile(r"-?\d+")
_FLOAT = re.compile(r"-?(\d+\.\d*|\.\d+|\d+(\.\d*)?[eE][+-]?\d+)")
_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")


@dataclass
class _Tok:
    kind: str
    text: str
    start: int
    end: int


def _tokenise(text: str) -> list[_Tok]:
    tokens: list[_Tok] = []
    pos = 0
    while pos < len(text):
        m = _TOKEN.match(text, pos)
        if not m:
            raise _SyntaxError(None, f"unexpected character {text[pos]!r} at column {pos + 1}")
        kind = m.lastgroup or ""
        value = m.group()
        if kind == "word" and value.endswith(":") and len(value) > 1:
            tokens.append(_Tok("word", value[:-1], m.start(), m.end() - 1))
            tokens.append(_Tok("punct", ":", m.end() - 1, m.end()))
        elif kind != "space":
            tokens.append(_Tok(kind, value, m.start(), m.end()))
        pos = m.end()
    return tokens


class _SyntaxError(Exception):
    def __init__(self, field: str | None, reason: str) -> None:
        self.field = field
        self.reason = reason


class _Reader:
    def __init__(self, text: str) -> None:
        self.text = text
        self.tokens = _tokenise(text)
        self.i = 0
        self.field: str | None = None

    def peek(self, offset: int = 0) -> _Tok | None:
        j = self.i + offset
        return self.tokens[j] if j < len(self.tokens) else None

    def take(self) -> _Tok | None:
        tok = self.peek()
        if tok is not None:
            self.i += 1
        return tok

    def expect(self, text: str, context: str) -> _Tok:
        tok = self.take()
        if tok is None or tok.text != text:
            got = "the end" if tok is None else repr(tok.text)
            raise _SyntaxError(self.field, f"expected {text!r} {context}, got {got}")
        return tok

    def done(self) -> bool:
        return self.i >= len(self.tokens)


def _classify(word: str) -> Any:
    if word == "true":
        return True
    if word == "false":
        return False
    if _INT.fullmatch(word):
        return int(word)
    if _FLOAT.fullmatch(word):
        return float(word)
    if _DATE.fullmatch(word):
        try:
            return date.fromisoformat(word)
        except ValueError:
            return word
    return word


def _parse_compact(text: str, path: str) -> Any:
    stripped = text.strip()
    try:
        reader = _Reader(stripped)
        head = reader.peek()
        nxt = reader.peek(1)
        if head is None:
            raise _SyntaxError(None, "empty condition")
        if head.kind == "word" and head.text in ("any", "all", "not") and nxt and nxt.text == "(":
            return _compact_group(reader, stripped, path)
        raw = _compact_leaf(reader)
        _compact_modifiers(reader, raw)
    except _SyntaxError as bad:
        raise ConditionError(text, bad.field, bad.reason, path) from None
    return _from_mapping(raw, path, text=text)


def _compact_group(reader: _Reader, text: str, path: str) -> Any:
    name = reader.take().text  # type: ignore[union-attr]
    reader.take()  # "("
    children: list[str] = []
    depth = 0
    start = reader.peek().start if reader.peek() else len(text)
    while True:
        tok = reader.take()
        if tok is None:
            raise _SyntaxError(None, f"{name}( is not closed")
        if tok.text in "([{" and tok.kind == "punct":
            depth += 1
        elif tok.text in ")]}" and tok.kind == "punct":
            if depth == 0 and tok.text == ")":
                children.append(text[start:tok.start])
                break
            depth -= 1
        elif tok.text == ";" and depth == 0:
            children.append(text[start:tok.start])
            nxt = reader.peek()
            start = nxt.start if nxt else len(text)
    children = [child.strip() for child in children]
    modifiers: dict[str, Any] = {}
    _compact_modifiers(reader, modifiers)
    if name == "not":
        if len(children) != 1 or not children[0]:
            raise _SyntaxError(None, "not( takes exactly one condition")
        child = parse_condition(children[0], _join(path, "not"))
        return _build(NotOf, {"not": child, **modifiers}, text, None, path)
    if any(not child for child in children):
        raise _SyntaxError(None, f"{name}( has an empty condition")
    built = [parse_condition(child, _join(path, f"{name}[{i}]"))
             for i, child in enumerate(children)]
    return _build(AnyOf if name == "any" else AllOf, {name: built, **modifiers}, text, None, path)


def _compact_leaf(reader: _Reader) -> dict[str, Any]:
    head = reader.take()
    assert head is not None
    if head.kind == "word" and head.text == "known" and reader.peek() and \
            reader.peek().text == "(":  # type: ignore[union-attr]
        reader.take()
        facet = reader.take()
        if facet is None or facet.kind != "word":
            raise _SyntaxError(None, "known( needs a facet")
        reader.field = facet.text
        reader.expect(")", "after known(<facet>")
        return {"known": facet.text}
    if head.kind != "word":
        raise _SyntaxError(None, f"a condition starts with a facet, got {head.text!r}")
    reader.field = head.text
    tok = reader.take()
    if tok is None:
        raise _SyntaxError(head.text, "missing operator after the facet")
    if tok.kind == "op":
        if tok.text == "==":
            raise _SyntaxError(head.text, "unknown operator '=='; use =")
        return {"facet": head.text, "op": tok.text, "value": _compact_value(reader, tok.text)}
    negate = False
    if tok.text == "not":
        negate = True
        tok = reader.take()
    if tok is None or tok.text != "in":
        got = "the end" if tok is None else repr(tok.text)
        raise _SyntaxError(head.text, f"expected an operator (= != < <= > >=) or in, got {got}")
    opener = reader.take()
    if opener is not None and opener.text == "[":
        if negate:
            raise _SyntaxError(head.text, "not in takes a set {…}, not a window […]")
        low = _compact_value(reader, "[")
        reader.expect(",", "between the window's ends")
        high = _compact_value(reader, ",")
        reader.expect("]", "to close the window")
        return {"facet": head.text, "between": [low, high]}
    if opener is not None and opener.text == "{":
        values: list[Any] = []
        if reader.peek() and reader.peek().text == "}":  # type: ignore[union-attr]
            reader.take()
        else:
            while True:
                values.append(_compact_value(reader, "{"))
                sep = reader.take()
                if sep is not None and sep.text == "}":
                    break
                if sep is None or sep.text != ",":
                    raise _SyntaxError(head.text, "expected , or } in the set")
        return {"facet": head.text, ("not_in" if negate else "in"): values}
    raise _SyntaxError(head.text, "in takes a window [low, high] or a set {a, b}")


def _compact_value(reader: _Reader, after: str) -> Any:
    tok = reader.take()
    if tok is None or tok.kind not in ("word", "str"):
        raise _SyntaxError(reader.field, f"missing value after {after}")
    if tok.kind == "str":
        return json.loads(tok.text)
    if tok.text == "model" and reader.peek() and reader.peek().text == "(":  # type: ignore[union-attr]
        reader.take()
        parts = []
        while reader.peek() is not None and reader.peek().text != ")":  # type: ignore[union-attr]
            parts.append(reader.take().text)  # type: ignore[union-attr]
        reader.expect(")", "to close model(")
        return {"model": " ".join(parts)}
    return _classify(tok.text)


def _compact_modifiers(reader: _Reader, raw: dict[str, Any]) -> None:
    qualifiers: dict[str, Any] = {}
    field = reader.field

    def put(key: str, value: Any, spelled: str) -> None:
        if key in qualifiers and qualifiers[key] != value:
            raise _SyntaxError(
                field, f"{key} given twice ({spelled} conflicts with an earlier qualifier)")
        qualifiers[key] = value

    while not reader.done():
        tok = reader.take()
        assert tok is not None
        if tok.kind == "qual":
            if tok.text in _FLAG_QUALIFIERS:
                key, value = _FLAG_QUALIFIERS[tok.text]
                put(key, value, tok.text)
            elif tok.text in _ARG_QUALIFIERS:
                reader.expect("(", f"after {tok.text}")
                arg = reader.take()
                if arg is None or arg.kind != "word":
                    raise _SyntaxError(field, f"{tok.text}( needs a value")
                reader.expect(")", f"to close {tok.text}(")
                put(_ARG_QUALIFIERS[tok.text], arg.text, tok.text)
            else:
                known = ", ".join(QUALIFIER_KEYWORDS)
                raise _SyntaxError(field, f"unknown qualifier {tok.text}; expected one of {known}")
        elif tok.text == "measured_after":
            when = reader.take()
            value = _classify(when.text) if when is not None else None
            if not isinstance(value, date):
                got = "nothing" if when is None else repr(when.text)
                raise _SyntaxError(field, f"measured_after needs a date (YYYY-MM-DD), got {got}")
            put("measured_after", value.isoformat(), "measured_after")
        elif tok.text in ("soft", "unknown"):
            raw[tok.text] = _compact_call(reader, tok.text)
        else:
            raise _SyntaxError(field, f"unexpected {tok.text!r}; a condition ends with qualifiers, "
                              "measured_after, soft(…) or unknown(…)")
    if qualifiers:
        raw["qualifiers"] = qualifiers


def _compact_call(reader: _Reader, name: str) -> Any:
    """``soft(0.2)``, ``soft(penalty: 0.2)``, ``unknown(fail)`` or ``unknown: fail``."""
    field = reader.field
    tok = reader.take()
    if name == "unknown" and tok is not None and tok.text == ":":
        value = reader.take()
        if value is None:
            raise _SyntaxError(field, "unknown: needs list, fail or pass")
        return value.text
    if tok is None or tok.text != "(":
        raise _SyntaxError(field, f"{name} is written {name}(…)")
    arg = reader.take()
    if name == "soft" and arg is not None and arg.text == "penalty":
        reader.expect(":", "after soft(penalty")
        arg = reader.take()
    if arg is None or arg.kind != "word":
        raise _SyntaxError(field, f"{name}( needs a value")
    reader.expect(")", f"to close {name}(")
    return {"penalty": _classify(arg.text)} if name == "soft" else arg.text


# ── rendering conditions ───────────────────────────────────────────────────

_BARE = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_.:/+@-]*")
_RESERVED_WORDS = {"in", "not", "measured_after", "soft", "unknown"}


def _render_value(value: Any) -> str:
    if isinstance(value, ModelRef):
        return f"model({value.model})"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int | float):
        return json.dumps(value)
    if isinstance(value, date):
        return value.isoformat()
    if (_BARE.fullmatch(value) and not value.endswith(":") and _classify(value) == value
            and value not in _RESERVED_WORDS):
        return value
    return json.dumps(value)


def _render_modifiers(cond: Any) -> str:
    parts: list[str] = []
    q = getattr(cond, "qualifiers", None)
    if q is not None:
        if q.measured_by:
            parts.append(f"@{q.measured_by}")
        if q.effort in ("default", "max"):
            parts.append(f"@{q.effort}_effort")
        elif q.effort:
            parts.append(f"@effort({q.effort})")
        if q.harness:
            parts.append(f"@harness({q.harness})")
        if q.direct:
            parts.append("@direct")
        if q.measured_after:
            parts.append(f"measured_after {q.measured_after.isoformat()}")
    if cond.soft is not None:
        parts.append(f"soft({json.dumps(cond.soft.penalty)})")
    if getattr(cond, "unknown", None) is not None:
        parts.append(f"unknown({cond.unknown})")
    return "".join(f" {p}" for p in parts)


def render_condition(cond: Any) -> str:
    """The canonical compact form. ``parse_condition(render_condition(c)) == c``."""
    if isinstance(cond, Compare):
        body = f"{cond.facet} {cond.op} {_render_value(cond.value)}"
    elif isinstance(cond, Window):
        low, high = cond.between
        body = f"{cond.facet} in [{_render_value(low)}, {_render_value(high)}]"
    elif isinstance(cond, InSet):
        values = ", ".join(_render_value(v) for v in (cond.in_ or cond.not_in or []))
        body = f"{cond.facet} {'in' if cond.in_ is not None else 'not in'} {{{values}}}"
    elif isinstance(cond, Known):
        body = f"known({cond.known})"
    elif isinstance(cond, AnyOf | AllOf):
        name = "any" if isinstance(cond, AnyOf) else "all"
        children = cond.any if isinstance(cond, AnyOf) else cond.all
        body = f"{name}({'; '.join(render_condition(ch) for ch in children)})"
    elif isinstance(cond, NotOf):
        body = f"not({render_condition(cond.not_)})"
    else:
        raise TypeError(f"not a condition: {cond!r}")
    return body + _render_modifiers(cond)


# ── the objective ──────────────────────────────────────────────────────────


class Tolerance(_Strict):
    """How far below the best a lexicographic step may be and still tie: ``5%`` or a number."""

    relative: float | None = Field(default=None, gt=0, lt=1)
    absolute: float | None = Field(default=None, gt=0)

    @model_validator(mode="before")
    @classmethod
    def _from_shorthand(cls, value: Any) -> Any:
        if isinstance(value, str):
            text = value.strip()
            if text.endswith("%"):
                return {"relative": float(text[:-1]) / 100}
            return {"absolute": float(text)}
        if isinstance(value, int | float) and not isinstance(value, bool):
            return {"absolute": value}
        return value

    @model_validator(mode="after")
    def _one(self) -> Tolerance:
        if (self.relative is None) == (self.absolute is None):
            raise ValueError("a tolerance is exactly one of relative, absolute")
        return self


class LexStep(_Strict):
    max: FacetId | None = None
    min: FacetId | None = None
    within: Tolerance | None = None

    @model_validator(mode="before")
    @classmethod
    def _split_within(cls, value: Any) -> Any:
        if isinstance(value, Mapping):
            value = dict(value)
            for side in ("max", "min"):
                text = value.get(side)
                if isinstance(text, str) and " within " in text:
                    facet, tolerance = text.split(" within ", 1)
                    value[side] = facet.strip()
                    value["within"] = tolerance.strip()
        return value

    @model_validator(mode="after")
    def _one(self) -> LexStep:
        if (self.max is None) == (self.min is None):
            raise ValueError("a lexicographic step is exactly one of max, min")
        return self

    @property
    def facet(self) -> str:
        return self.max or self.min or ""


def _base(signed: str) -> str:
    return signed.removeprefix("-")


def _objective_term(text: str) -> tuple[str, EvidenceQualifiers | None]:
    try:
        reader = _Reader(text.strip())
        head = reader.take()
        if head is None or head.kind != "word":
            raise _SyntaxError(None, "an objective term starts with a facet")
        reader.field = head.text.removeprefix("-")
        raw: dict[str, Any] = {}
        _compact_modifiers(reader, raw)
        if set(raw) - {"qualifiers"}:
            raise _SyntaxError(reader.field, "objective terms take evidence qualifiers only")
        qualifiers = EvidenceQualifiers.model_validate(raw["qualifiers"]) \
            if raw.get("qualifiers") else None
        return head.text, qualifiers
    except _SyntaxError as exc:
        raise ValueError(exc.reason) from None


class Preference(_Strict):
    """A weighted preference for one value of a boolean or enum facet."""

    prefer: Scalar
    weight: float = Field(gt=0)


class Objective(_Strict):
    """Exactly one of ``max``, ``min``, ``lexicographic``, ``weights``, ``pareto``."""

    max: FacetId | None = None
    min: FacetId | None = None
    lexicographic: list[LexStep] | None = None
    #: A key may name a refinement, ``<domain>/<refinement>`` (2.4, MODEL-190).
    weights: dict[WeightKey, float | Preference] | None = None
    pareto: list[SignedFacetId] | None = None
    qualifiers: dict[FacetId, EvidenceQualifiers] = Field(default_factory=dict)

    @model_validator(mode="before")
    @classmethod
    def _qualified_terms(cls, value: Any) -> Any:
        if not isinstance(value, Mapping):
            return value
        data = dict(value)
        qualifiers = dict(data.get("qualifiers") or {})

        def parse(term: Any) -> Any:
            if not isinstance(term, str):
                return term
            facet, found = _objective_term(term)
            base = _base(facet)
            if found is not None:
                prior = qualifiers.get(base)
                dumped = found.model_dump(exclude_none=True)
                if prior is not None and EvidenceQualifiers.model_validate(prior) != found:
                    raise ValueError(f"conflicting evidence qualifiers for {base}")
                qualifiers[base] = dumped
            return facet

        for side in ("max", "min"):
            if side in data:
                data[side] = parse(data[side])
        if isinstance(data.get("weights"), Mapping):
            data["weights"] = {parse(term): weight for term, weight in data["weights"].items()}
        if isinstance(data.get("pareto"), list):
            data["pareto"] = [parse(term) for term in data["pareto"]]
        if isinstance(data.get("lexicographic"), list):
            steps = []
            for raw in data["lexicographic"]:
                if not isinstance(raw, Mapping):
                    steps.append(raw)
                    continue
                step = dict(raw)
                for side in ("max", "min"):
                    if side in step:
                        term = step[side]
                        if isinstance(term, str) and " within " in term:
                            term, tolerance = term.split(" within ", 1)
                            step["within"] = tolerance.strip()
                        step[side] = parse(term)
                steps.append(step)
            data["lexicographic"] = steps
        if qualifiers:
            data["qualifiers"] = qualifiers
        return data

    @field_validator("lexicographic")
    @classmethod
    def _lex(cls, steps: list[LexStep] | None) -> list[LexStep] | None:
        if steps is None:
            return None
        if len(steps) < 2:
            raise ValueError("lexicographic needs at least two steps; use max or min for one")
        if steps[-1].within is not None:
            raise ValueError("the last lexicographic step has nothing after it to break ties, "
                             "so it takes no within")
        return steps

    @field_validator("weights")
    @classmethod
    def _weights(
        cls, weights: dict[str, float | Preference] | None,
    ) -> dict[str, float | Preference] | None:
        if weights is None:
            return None
        if not weights:
            raise ValueError("weights is empty")
        for facet, term in weights.items():
            weight = term.weight if isinstance(term, Preference) else term
            if not weight > 0:
                raise ValueError(f"weight for {facet} must be positive; put - on the facet "
                                 "to minimise it")
        _no_twice(list(weights))
        return weights

    @field_validator("pareto")
    @classmethod
    def _pareto(cls, dims: list[str] | None) -> list[str] | None:
        if dims is None:
            return None
        if len(dims) < 2:
            raise ValueError("pareto needs at least two dimensions")
        _no_twice(dims)
        return dims

    @model_validator(mode="after")
    def _exactly_one(self) -> Objective:
        forms = [name for name in ("max", "min", "lexicographic", "weights", "pareto")
                 if getattr(self, name) is not None]
        if len(forms) != 1:
            got = ", ".join(forms) or "none"
            raise ValueError("optimize takes exactly one of max, min, lexicographic, weights, "
                             f"pareto; got {got}")
        return self


def _no_twice(signed: list[str]) -> None:
    seen: set[str] = set()
    for facet in signed:
        if _base(facet) in seen:
            raise ValueError(f"{_base(facet)} appears twice")
        seen.add(_base(facet))


# ── the inventory profile ──────────────────────────────────────────────────


class ProfileOffering(_Strict):
    model: ModelId
    provider: str
    region: str | None = None
    tier: str | None = None


class Hardware(_Strict):
    class_: str = Field(alias="class")
    count: int = Field(default=1, ge=1)
    memory_gb: float | None = Field(default=None, gt=0)


class LocalModel(_Strict):
    model: ModelId
    hardware: Hardware | None = None
    runtime: str | None = None


class Budget(_Strict):
    max_cost_per_task_usd: float | None = Field(default=None, gt=0)


class InventoryProfile(_Strict):
    profile_version: Literal[1]
    id: ProfileId | None = None
    offerings: list[ProfileOffering] = Field(default_factory=list)
    local: list[LocalModel] = Field(default_factory=list)
    harnesses: list[HarnessId] = Field(default_factory=list)
    rules: list[Condition] = Field(default_factory=list)
    budget: Budget | None = None


def _profile_tag(value: Any) -> str:
    return "<profile-id>" if isinstance(value, str) else "<profile-inline>"


ProfileRef = Annotated[
    Annotated[ProfileId, Tag("<profile-id>")] | Annotated[InventoryProfile,
                                                          Tag("<profile-inline>")],
    Discriminator(_profile_tag),
]

# ── the spec ───────────────────────────────────────────────────────────────


class TaskTokens(_Strict):
    """How many tokens one task takes. ``offering.cost_per_task`` is priced from it."""

    input: int = Field(ge=0)
    output: int = Field(ge=0)


#: What ``offering.cost_per_task`` is priced at when a spec gives no ``task_tokens``.
DEFAULT_TASK_TOKENS = TaskTokens(input=40000, output=4000)


MAX_ESTATE_IDS = 64
EstateId = Annotated[str, StringConstraints(min_length=1, max_length=120)]


def _canonical_ids(value: list[str]) -> list[str]:
    return sorted(set(value))


class Estate(_Strict):
    """What the caller holds, sent with the spec and never stored. Added in 2.3.

    ``providers`` are provider IDs the caller has a key for, ``plans`` are
    subscription plan IDs, ``devices`` are hardware SKU IDs. ``exhausted`` lists
    providers or plans that cannot be used right now; an exhausted provider
    takes its key and its plans with it.
    """

    providers: list[EstateId] = Field(
        default_factory=list, max_length=MAX_ESTATE_IDS, exclude_if=lambda value: not value)
    plans: list[EstateId] = Field(
        default_factory=list, max_length=MAX_ESTATE_IDS, exclude_if=lambda value: not value)
    devices: list[EstateId] = Field(
        default_factory=list, max_length=MAX_ESTATE_IDS, exclude_if=lambda value: not value)
    exhausted: list[EstateId] = Field(
        default_factory=list, max_length=MAX_ESTATE_IDS, exclude_if=lambda value: not value)

    _sorted = field_validator("providers", "plans", "devices", "exhausted")(_canonical_ids)


AccessKind = Literal["chat_app", "coding_tool", "own_software", "own_hardware"]


class Access(_Strict):
    """How the caller will use the model. Added in 2.6.

    ``chat_app``: a provider's chat app, through a subscription plan.
    ``coding_tool``: a coding harness, through a plan or pay-per-use;
    ``harness`` names one from ``registry/harnesses.yaml`` (any when absent).
    ``own_software``: the caller's own software, pay-per-use (or a plan whose
    surfaces include ``api``). ``own_hardware``: self-hosted on the caller's
    devices. A spec may give the bare kind as a string.
    """

    kind: AccessKind
    harness: HarnessName | None = Field(default=None, exclude_if=lambda value: value is None)

    @model_validator(mode="before")
    @classmethod
    def _bare_kind(cls, value: Any) -> Any:
        return {"kind": value} if isinstance(value, str) else value

    @model_validator(mode="after")
    def _harness_only_for_a_coding_tool(self) -> Access:
        if self.harness is not None and self.kind != "coding_tool":
            raise ValueError("harness is only for access kind coding_tool")
        return self


class Spec(_Strict):
    """A request for a decision."""

    spec_version: Literal[1]
    snapshot: SnapshotRef = "latest"
    profile: ProfileRef | None = None
    task: str | None = None
    task_type: TaskType | None = None
    capabilities: dict[FacetId, CapabilityLevel] | None = None
    #: Benchmarks whose evidence must not contribute to this decision. Added in 1.12.
    exclude_benchmarks: list[FacetId] = Field(
        default_factory=list,
        exclude_if=lambda value: not value,
    )
    #: Tokens per task, for ``offering.cost_per_task``. Added in 1.3.
    task_tokens: TaskTokens | None = None
    where: list[Condition] = Field(default_factory=list)
    optimize: Objective
    unknowns: Literal["default"] = "default"
    explain: Explain = "summary"
    limit: int = Field(default=20, ge=1, le=500)
    save_as: SaveAs | None = None
    #: What the caller holds. Added in 2.3.
    estate: Estate | None = Field(default=None, exclude_if=lambda value: value is None)
    #: How the caller will use the model; absent means it does not matter. Added in 2.6.
    access: Access | None = Field(default=None, exclude_if=lambda value: value is None)

    @field_validator("exclude_benchmarks")
    @classmethod
    def _canonical_excluded_benchmarks(cls, value: list[str]) -> list[str]:
        return sorted(set(value))


# ── the decision ───────────────────────────────────────────────────────────


class OfferingRef(_Strict):
    model: ModelId
    provider: str | None = None
    region: str | None = None
    tier: str | None = None


class EvidenceItem(_Strict):
    requested_domain: FacetId | None = None
    record_id: str | None = None
    benchmark: str
    version: str | None = None
    sub_category: str | None = None
    value: float
    unit: str | None = None
    n: int | None = Field(default=None, ge=1)
    interval: tuple[float, float] | None = None
    quality_flags: list[Literal["deprecated", "contamination_warning"]] = Field(
        default_factory=list
    )
    measured_by: MeasuredBy
    effort: Effort | None = None
    harness: HarnessId | None = None
    #: The evidence names a harness the registry does not know (MODEL-133's
    #: ``unregistered``). ``harness`` is then null. Added in 1.2.
    harness_unregistered: bool = False
    date: date
    date_type: DateType
    source: Url
    source_snapshot: str | None = None
    directness: Directness
    #: Directness loading used in the capability estimate. Added in 1.7.
    loading: float | None = None
    #: Share of the estimate's tagged measurement precision. Added in 1.7.
    estimate_weight: float | None = None
    #: Precision multiplier from the observation's age. Added in 1.7.
    recency_weight: float | None = Field(default=None, ge=0, le=1)

    @model_validator(mode="after")
    def _one_harness(self) -> EvidenceItem:
        if self.harness_unregistered and self.harness is not None:
            raise ValueError("an unregistered harness has no harness ID")
        return self


class DomainEvidence(_Strict):
    domain: FacetId
    items: list[EvidenceItem]


class Estimate(_Strict):
    domain: FacetId
    value: float
    interval: tuple[float, float]
    harness: HarnessId | None = None
    effort: Effort | None = None


class RefinementEstimate(_Strict):
    """A refinement estimate nested in its parent domain. Added in 2.4 (MODEL-190).

    ``evidence_count`` 0 means no refinement evidence: the value is the
    parent's estimate and the interval is wider by the refinement's spread.
    """

    key: RefinementKey
    #: The parent domain, or ``any`` for a cross-domain refinement.
    domain: FacetId
    refinement: FacetId
    value: float
    interval: tuple[float, float]
    evidence_count: int = Field(ge=0)


class BenchmarkEstimateChange(_Strict):
    """How one model's domain estimate changed after removing evidence. Added in 1.12."""

    model: ModelId
    domain: FacetId
    before: Estimate | None = None
    after: Estimate | None = None
    removed_drivers: list[EvidenceItem] = Field(default_factory=list)


class BenchmarkExclusions(_Strict):
    """Benchmarks a spec distrusted and their visible estimate effects. Added in 1.12."""

    benchmarks: list[FacetId]
    estimate_changes: list[BenchmarkEstimateChange] = Field(default_factory=list)


class Contribution(_Strict):
    raw_value: float | None = None
    unit: str | None = None
    records: list[str] = Field(default_factory=list)
    dimension: SignedFacetId
    weight: float | None = None
    value: float | None = None
    normalisation: str | None = None
    evidence: list[EvidenceItem] = Field(default_factory=list)
    #: How a computed raw value was reached, with the numbers. Added in 1.3.
    formula: str | None = None
    #: The requested value and its match state for a boolean or enum Prefer. Added in 2.0.
    preferred_value: Scalar | None = None
    preference_status: PreferenceStatus | None = None
    #: The refinement of ``dimension`` this contribution weighs. Added in 2.4.
    refinement: FacetId | None = Field(default=None, exclude_if=lambda value: value is None)


class PlanPrice(_Strict):
    """A plan's published list price for one billing period. Added in 2.6."""

    amount: float = Field(ge=0)
    currency: Literal["USD"]
    period: Literal["monthly", "annual"]


class PlanCoverage(_Strict):
    """Why a plan counts as covering a model. Added in 2.6.

    ``family`` and ``quote`` are the family the plan page names and the page's
    own words; both are absent when the plan's ``models_covered`` names the
    model directly. ``resolves_to`` is every model the entry reaches, by
    ``rule``.
    """

    family: str | None = None
    quote: str | None = None
    resolves_to: list[ModelId] = Field(default_factory=list)
    rule: str


class PlanAllowance(_Strict):
    """A plan's published usage allowance; each part is null unless published. Added in 2.6."""

    relative_to: str | None = None
    multiplier: float | None = Field(default=None, ge=0)
    window: str | None = None
    tokens: float | None = Field(default=None, ge=0)


class PlanRoute(_Strict):
    """A subscription plan that reaches a result on the spec's ``access``. Added in 2.6.

    ``break_even_tasks_per_month`` is the plan's monthly price divided by this
    result's pay-per-use cost per task, for ``access: coding_tool`` only, and
    null when either is unknown. ``basis`` says how it was computed or why not.
    ModelSpec never turns a plan price into a per-task cost.
    """

    plan: EstateId
    name: str
    surface: str
    price: PlanPrice | None = None
    price_monthly_usd: float | None = Field(default=None, ge=0)
    coverage: PlanCoverage
    allowance: PlanAllowance = Field(default_factory=PlanAllowance)
    break_even_tasks_per_month: float | None = Field(default=None, ge=0)
    basis: str


class Result(_Strict):
    rank: int = Field(ge=1)
    offering: OfferingRef
    #: The model, flat: ``offering.model``. Added in 2.5.
    model: ModelId | None = None
    #: The model's place among the returned models, 1 for the model of the
    #: top offering. It counts models, not offerings, and does not say whether
    #: two models are tied: ``Decision.answer`` does. Added in 2.5.
    model_rank: int | None = Field(default=None, ge=1)
    #: The task's cost through this offering, in dollars, or null when it has
    #: no known price. The same number as the cost contribution's
    #: ``raw_value``, present at every explain level. Added in 2.5.
    cost_per_task: float | None = None
    harness: HarnessId | None = None
    effort: Effort | None = None
    evidence: list[DomainEvidence] = Field(default_factory=list)
    estimates: list[Estimate] | None = None
    #: One per refinement key in ``optimize.weights``. Added in 2.4 (MODEL-190).
    refinement_estimates: list[RefinementEstimate] | None = Field(
        default=None, exclude_if=lambda value: value is None,
    )
    p_best: float | None = Field(default=None, ge=0, le=1)
    top3_stability: float | None = Field(default=None, ge=0, le=1)
    soft_penalty: float = Field(default=0.0, ge=0)
    contributions: list[Contribution] = Field(default_factory=list)
    warnings: list[Code] = Field(default_factory=list)
    #: The plans that reach this result on the spec's ``access``, cheapest
    #: first. Absent without ``access``. Added in 2.6.
    plans: list[PlanRoute] = Field(default_factory=list, exclude_if=lambda value: not value)

    @model_validator(mode="after")
    def _model_is_the_offerings(self) -> Result:
        if self.model is None:
            self.model = self.offering.model
        elif self.model != self.offering.model:
            raise ValueError(f"model {self.model!r} is not the offering's model {self.offering.model!r}")
        return self


class MayQualify(_Strict):
    model: ModelId
    offering: OfferingRef | None = None
    unknown: list[FacetId]


class FunnelStep(_Strict):
    condition: str
    before: int = Field(ge=0)
    after: int = Field(ge=0)
    may_qualify: int = Field(default=0, ge=0)
    #: Candidate-grained counts above remain for compatibility. These counts
    #: expose the same stage at the two grains people make decisions about.
    #: Added in 1.6.
    models_before: int = Field(default=0, ge=0)
    models_after: int = Field(default=0, ge=0)
    offerings_before: int = Field(default=0, ge=0)
    offerings_after: int = Field(default=0, ge=0)
    models_may_qualify: int = Field(default=0, ge=0)
    offerings_may_qualify: int = Field(default=0, ge=0)


class ModelElimination(_Strict):
    values: list[Scalar] = Field(default_factory=list)
    offering: OfferingRef | None = None
    unit: str | None = None
    records: list[str] = Field(default_factory=list)
    model: ModelId
    condition: str
    value: Scalar | None = None
    #: How a computed value was reached, with the numbers. Added in 1.3.
    formula: str | None = None


class OfferingElimination(_Strict):
    """Why one offering of an eliminated model left the lineup. Added in 1.6."""

    values: list[Scalar] = Field(default_factory=list)
    offering: OfferingRef
    unit: str | None = None
    records: list[str] = Field(default_factory=list)
    condition: str
    value: Scalar | None = None
    formula: str | None = None


class ModelEliminationGroup(_Strict):
    """One eliminated model, with its model row or offering rows. Added in 1.6."""

    model: ModelId
    model_elimination: ModelElimination | None = None
    offerings: list[OfferingElimination] = Field(default_factory=list)


class Eliminated(_Strict):
    funnel: list[FunnelStep] = Field(default_factory=list)
    models: list[ModelElimination] = Field(default_factory=list)
    #: The candidate-grained ``models`` list remains for older clients.
    #: Added in 1.6.
    model_groups: list[ModelEliminationGroup] = Field(default_factory=list)


class Truncated(_Strict):
    """Qualifying rows omitted only because of the requested result limit. Added in 1.9."""

    offerings: int = Field(default=0, ge=0)
    models: int = Field(default=0, ge=0)


class TieBreakers(_Strict):
    cheapest: ModelId | None = None
    open_weights: ModelId | None = None
    most_independently_measured: ModelId | None = None
    fastest: ModelId | None = None


class SeparatedAnswer(_Strict):
    kind: Literal["separated"]
    members: list[ModelId] = Field(min_length=1, max_length=1)
    leader: ModelId
    basis: str
    tie_breakers: TieBreakers
    deterministic_order: list[ModelId] = Field(min_length=1, max_length=1)

    @model_validator(mode="after")
    def _one_leader(self) -> SeparatedAnswer:
        if self.members != [self.leader] or self.deterministic_order != self.members:
            raise ValueError("a separated answer contains only its leader")
        if any(value is not None for value in self.tie_breakers.model_dump().values()):
            raise ValueError("a separated answer has no tie-breakers")
        return self


class TiedAnswer(_Strict):
    kind: Literal["tied"]
    members: list[ModelId] = Field(min_length=2)
    basis: str
    tie_breakers: TieBreakers
    deterministic_order: list[ModelId] = Field(min_length=2)

    @model_validator(mode="after")
    def _same_members(self) -> TiedAnswer:
        if len(set(self.members)) != len(self.members):
            raise ValueError("answer members are unique model IDs")
        if len(set(self.deterministic_order)) != len(self.deterministic_order) or set(
            self.deterministic_order
        ) != set(self.members):
            raise ValueError("deterministic_order contains every member exactly once")
        if any(
            value is not None and value not in self.members
            for value in self.tie_breakers.model_dump().values()
        ):
            raise ValueError("a tie-breaker names a member of the tied answer")
        return self


Answer = Annotated[SeparatedAnswer | TiedAnswer, Field(discriminator="kind")]


class DimensionEstimate(_Strict):
    """A band entry's estimate on one weighted capability. Added in 2.7 (MODEL-206)."""

    #: The signed weight key: a domain, or a refinement key.
    dimension: WeightKey
    value: float
    #: The 80% interval.
    interval: tuple[float, float]
    #: Distinct fitted benchmarks the model is measured on for this estimate.
    benchmarks: int = Field(ge=0)
    #: Of those, the benchmarks tagged direct for this dimension.
    direct_benchmarks: int = Field(ge=0)

    @model_validator(mode="after")
    def _direct_are_counted(self) -> DimensionEstimate:
        if self.direct_benchmarks > self.benchmarks:
            raise ValueError("direct_benchmarks counts some of benchmarks")
        return self


class BandEntry(_Strict):
    """One model in a band, through its best offering. Added in 2.7 (MODEL-206)."""

    model: ModelId
    offering: OfferingRef
    #: The weighted score and its interval, on the feasible set's normalised scale.
    score: float
    score_interval: tuple[float, float]
    p_best: float | None = Field(default=None, ge=0, le=1)
    #: P(this model's score >= the leader's). Null for the leader, and for a
    #: thin-evidence model when no model has enough evidence to lead.
    p_beats_leader: float | None = Field(default=None, ge=0, le=1)
    cost_per_task: float | None = None
    #: One per weighted capability, in objective order.
    estimates: list[DimensionEstimate] = Field(default_factory=list)


class Bands(_Strict):
    """The ranked models in three bands (MODEL-206). Added in 2.7.

    ``best`` is the leader and every model with enough evidence whose score is
    at least the leader's with probability ``band_probability`` or more,
    ordered by ``p_best``. ``rest`` holds the other models with enough
    evidence and ``thin`` the models with a weighted capability interval wider
    than ``thin_interval_width``, both in score order. Every ranked model is in
    exactly one band.
    """

    basis: str
    band_probability: float = Field(gt=0, lt=1)
    thin_interval_width: float = Field(gt=0)
    #: The best point score among models with enough evidence; null when none has.
    leader: ModelId | None = None
    best: list[BandEntry] = Field(default_factory=list)
    rest: list[BandEntry] = Field(default_factory=list)
    thin: list[BandEntry] = Field(default_factory=list)

    @model_validator(mode="after")
    def _one_band_each(self) -> Bands:
        models = [entry.model for band in (self.best, self.rest, self.thin) for entry in band]
        if len(set(models)) != len(models):
            raise ValueError("a model is in exactly one band")
        if (self.leader is None) != (not self.best):
            raise ValueError("the best band is empty exactly when there is no leader")
        if self.leader is not None and self.leader not in {entry.model for entry in self.best}:
            raise ValueError("the leader is in the best band")
        return self


class BlendTerm(_Strict):
    """One weighted dimension, its share, and the order on it alone. Added in 2.7 (MODEL-206).

    The weighted score mixes these dimensions; each term says who leads on
    that dimension by itself. A capability term leads with the best point
    estimate among models with enough evidence on it; ``thin`` lists the rest.
    An exact term (cost, a fact, a preference) can have several ``leaders``
    when they share the best value.
    """

    dimension: WeightKey
    weight: float
    #: ``weight`` over the sum of the objective's weights.
    share: float = Field(ge=0, le=1)
    #: Whether the dimension is a capability estimate rather than an exact value.
    estimated: bool
    leaders: list[ModelId] = Field(default_factory=list)
    #: The leaders' value on this dimension, in its own unit: an estimate, or a raw value.
    value: float | None = None
    #: Capability only: P(the leader is best on this dimension alone).
    p_best: float | None = Field(default=None, ge=0, le=1)
    runner_up: ModelId | None = None
    #: Capability only: P(the runner-up's estimate >= the leader's).
    p_runner_up: float | None = Field(default=None, ge=0, le=1)
    #: Models with enough evidence, best first on this dimension alone.
    order: list[ModelId] = Field(default_factory=list)
    thin: list[ModelId] = Field(default_factory=list)


class RefinementGain(_Strict):
    """``gain`` for one refinement dimension. Added in 2.4 (MODEL-190)."""

    dimension: SignedFacetId
    refinement: FacetId
    gain: float


class ConstraintCost(_Strict):
    units: dict[str, str | None] = Field(default_factory=dict)
    records: list[str] = Field(default_factory=list)
    condition: str
    admits: int = Field(ge=0)
    gain: dict[SignedFacetId, float] = Field(default_factory=dict)
    #: Gains on refinement dimensions, which ``gain`` cannot key. Added in 2.4.
    refinement_gains: list[RefinementGain] = Field(
        default_factory=list, exclude_if=lambda value: not value,
    )


class TippingPoint(_Strict):
    description: str
    dimension: SignedFacetId | None = None
    threshold: float | None = None
    new_top: ModelId | None = None
    #: The refinement of ``dimension`` whose weight tips. Added in 2.4.
    refinement: FacetId | None = Field(default=None, exclude_if=lambda value: value is None)


class NearMiss(_Strict):
    values: list[Scalar] = Field(default_factory=list)
    offering: OfferingRef
    condition: str
    facet: str | None = None
    value: Scalar | None = None
    distance: float | None = None
    unit: str | None = None
    records: list[str] = Field(default_factory=list)
    #: How a computed value was reached, with the numbers. Added in 1.3.
    formula: str | None = None


class ShownFact(_Strict):
    facet: str
    value: Scalar | list[Scalar] | None = None
    unit: str | None = None
    record_id: str | None = None
    #: A computed fact has no record of its own: the records it was computed
    #: from, and the formula with the numbers. Added in 1.3.
    records: list[str] = Field(default_factory=list)
    formula: str | None = None
    #: The registered sources behind ``record_id`` or ``records``, as IDs into
    #: ``Decision.sources``. Added in 1.4.
    source_ids: list[str] = Field(default_factory=list)


class CandidateValues(_Strict):
    offering: OfferingRef
    facts: list[ShownFact] = Field(default_factory=list)
    contributions: list[Contribution] = Field(default_factory=list)
    evidence: list[DomainEvidence] = Field(default_factory=list)


class CitedSource(_Strict):
    """One registered source, listed once per decision. Added in 1.4."""

    id: str
    url: Url
    #: The snapshot records no titles yet: null, never a guess.
    title: str | None = None
    #: The latest date a record in this decision citing it was verified.
    date: Day | None = None


class NumberOrigin(_Strict):
    path: str
    basis: str
    records: list[str] = Field(default_factory=list)
    #: Always empty from 1.4: ``source_ids`` name entries of ``Decision.sources``.
    sources: list[Url] = Field(default_factory=list)
    #: The registered sources behind ``records``. Added in 1.4.
    source_ids: list[str] = Field(default_factory=list)


class Relaxation(_Strict):
    """The smallest change to one numeric cap or floor that admits a model. Added in 1.5.

    ``condition`` is the spec's condition; ``relaxed`` is the same facet and
    direction at ``value``, in ``unit``, the nearest value any excluded
    candidate has; ``admits`` counts the models that then qualify.
    """

    condition: str
    relaxed: str
    facet: str
    value: float
    unit: str | None = None
    admits: int = Field(ge=1)


EstateKind = Literal["provider", "plan", "device"]
CostBasis = Literal["list_price", "plan_included", "owned_hardware"]


class EstateHold(_Strict):
    kind: EstateKind
    id: EstateId


class EstateMark(_Strict):
    """How the estate reaches one row, and what one more task costs the caller."""

    via: EstateHold
    cost_basis: CostBasis
    marginal_cost_per_task_usd: float | None = Field(default=None, ge=0)
    #: For a plan, why it covers this row's model. Added in 2.6.
    coverage: PlanCoverage | None = Field(default=None, exclude_if=lambda value: value is None)


class EstateResult(_Strict):
    rank: int = Field(ge=1)
    offering: OfferingRef
    estate: EstateMark
    soft_penalty: float = Field(default=0.0, ge=0)
    warnings: list[Code] = Field(default_factory=list)


class EstateGap(_Strict):
    """Why the two answers differ, or that they do not."""

    same_answer: bool
    #: Models the unrestricted ranking puts above the estate's leader, plus any
    #: member of a tied unrestricted answer, that the estate cannot reach, best first.
    unreachable_models: list[ModelId] = Field(default_factory=list)
    summary: str


class GainItem(_Strict):
    """One hold the caller does not have whose addition would change the answer."""

    add: EstateHold
    status: Status
    leader: ModelId | None = None
    answer: Answer | None = None


class WithEstate(_Strict):
    """The same question answered from what the caller holds. Added in 2.3."""

    status: Status
    answer: Answer | None = None
    results: list[EstateResult] = Field(default_factory=list)
    may_qualify: list[MayQualify] = Field(default_factory=list)
    truncated: Truncated = Field(default_factory=Truncated)
    gap: EstateGap
    gain: list[GainItem] = Field(default_factory=list)
    #: Codes about what the estate holds, such as ``plan_excludes_own_software``.
    #: Added in 2.6.
    warnings: list[Code] = Field(default_factory=list, exclude_if=lambda value: not value)


class ModelOffering(_Strict):
    """One offering of a model in ``by_model``, with why it is or is not ranked. Added in 2.5."""

    offering: OfferingRef
    status: ModelRowStatus
    #: The offering's rank in ``results``, for a ranked offering.
    rank: int | None = Field(default=None, ge=1)
    cost_per_task: float | None = None
    #: The facets a may-qualify offering is unknown on.
    unknown: list[FacetId] = Field(default_factory=list)
    #: The Must condition an eliminated offering failed. Only when the
    #: explanation carries eliminations (``explain: full``).
    reason: str | None = None


class ModelRow(_Strict):
    """One model, with all its offerings, in ranking order. Added in 2.5.

    A model is ``ranked`` when any offering is, else ``may_qualify`` when any
    is unknown on a facet, else ``eliminated``. ``rank`` is ``Result.model_rank``.
    Eliminated models appear only when the explanation carries eliminations.
    """

    model: ModelId
    status: ModelRowStatus
    rank: int | None = Field(default=None, ge=1)
    #: The best ranked offering's cost.
    cost_per_task: float | None = None
    offerings: list[ModelOffering] = Field(default_factory=list)


class FeedbackPointer(_Strict):
    """Where to say whether this answer held up. The same on every decision.

    Added in 2.10 (MODEL-221), so that an agent holding an answer finds the
    feedback endpoint without reading anything else. No key is needed.
    """

    endpoint: Literal["https://api.modelspec.dev/v1/feedback"] = FEEDBACK_ENDPOINT
    method: Literal["POST"] = "POST"
    request_schema: Literal["https://modelspec.dev/api/feedback/v1.schema.json"] = FEEDBACK_SCHEMA
    ratings: list[FeedbackRating] = Field(
        default_factory=lambda: list(typing.get_args(FeedbackRating)))
    cli: Literal["modelspec feedback <decision_id> --rating <rating>"] = FEEDBACK_CLI


class Decision(_Strict):
    """The engine's answer to one spec against one snapshot."""

    near_misses: list[NearMiss] = Field(default_factory=list)
    top: list[CandidateValues] = Field(default_factory=list)
    chart: str | None = None
    number_origins: list[NumberOrigin] = Field(default_factory=list)
    #: Every source the number origins cite, once each. Added in 1.4.
    sources: list[CitedSource] = Field(default_factory=list)
    benchmark_exclusions: BenchmarkExclusions | None = Field(
        default=None,
        exclude_if=lambda value: value is None,
    )
    contract_version: Literal["2.10"] = CONTRACT_VERSION
    decision_id: DecisionId
    snapshot: SnapshotId
    #: Whether this process verified a publisher signature. Added in 1.10.
    signature_verified: bool = False
    spec_hash: SpecHash
    explain: Explain
    status: Status
    #: The model-level answer: its members are ``bands.best`` (2.7; before,
    #: every model whose interval overlapped the leader's). Added in 2.1.
    answer: Answer | None = None
    #: The ranked models in three bands. Absent for a lexicographic or Pareto
    #: objective, or without results. Added in 2.7 (MODEL-206).
    bands: Bands | None = Field(default=None, exclude_if=lambda value: value is None)
    #: What the objective mixes: each weighted dimension's share and its own
    #: order. Absent when ``bands`` is. Added in 2.7 (MODEL-206).
    blend: list[BlendTerm] = Field(default_factory=list, exclude_if=lambda value: not value)
    results: list[Result] = Field(default_factory=list)
    #: The same candidates grouped by model: ranked, then may qualify, then
    #: eliminated. Added in 2.5.
    by_model: list[ModelRow] = Field(default_factory=list)
    may_qualify: list[MayQualify] = Field(default_factory=list)
    eliminated: Eliminated = Field(default_factory=Eliminated)
    truncated: Truncated = Field(default_factory=Truncated)
    constraint_costs: list[ConstraintCost] = Field(default_factory=list)
    tipping_points: list[TippingPoint] = Field(default_factory=list)
    relax: list[str] = Field(default_factory=list)
    #: For ``no_feasible`` only: the smallest change to each numeric cap or
    #: floor that admits a model. Added in 1.5.
    relax_to: list[Relaxation] = Field(default_factory=list)
    warnings: list[Code] = Field(default_factory=list)
    #: Active models the snapshot leaves out of the lineup. Added in 1.2.
    out_of_lineup: int = Field(default=0, ge=0)
    #: The same answer from what the spec's ``estate`` holds. Added in 2.3.
    with_estate: WithEstate | None = Field(default=None, exclude_if=lambda value: value is None)
    #: Where to report whether this answer held up. Added in 2.10 (MODEL-221).
    feedback: FeedbackPointer = Field(default_factory=FeedbackPointer)

    @model_validator(mode="after")
    def _status_agrees(self) -> Decision:
        if self.status == "no_feasible":
            if self.results:
                raise ValueError("a no_feasible decision has no results")
            if not self.relax:
                raise ValueError("a no_feasible decision names the fewest conditions to relax")
        elif self.relax or self.relax_to:
            raise ValueError(f"relax is only for no_feasible, not {self.status}")
        ranks = [r.rank for r in self.results]
        if ranks != list(range(1, len(ranks) + 1)):
            raise ValueError(f"result ranks must run 1..n in order; got {ranks}")
        return self


CONTRACT_TYPES: tuple[type[BaseModel], ...] = (
    Spec, TaskTokens, Objective, Preference, LexStep, Tolerance, EvidenceQualifiers, Soft, ModelRef,
    Compare, Window, InSet, Known, AnyOf, AllOf, NotOf,
    InventoryProfile, ProfileOffering, LocalModel, Hardware, Budget,
    Decision, Result, OfferingRef, DomainEvidence, EvidenceItem, Estimate,
    BenchmarkEstimateChange, BenchmarkExclusions, Contribution,
    MayQualify, Eliminated, FunnelStep, ModelElimination, OfferingElimination,
    Truncated, TieBreakers, SeparatedAnswer, TiedAnswer,
    DimensionEstimate, BandEntry, Bands, BlendTerm,
    ModelEliminationGroup, ConstraintCost, TippingPoint, ModelRow, ModelOffering,
    NearMiss, ShownFact, CandidateValues, NumberOrigin, CitedSource, Relaxation,
    Estate, EstateHold, EstateMark, EstateResult, EstateGap, GainItem, WithEstate,
    Access, PlanPrice, PlanCoverage, PlanAllowance, PlanRoute, FeedbackPointer,
)


def closed_values() -> list[str]:
    """Every value of every closed vocabulary in the contract, for the doc agreement test."""
    values: list[str] = []
    for alias in (Op, UnknownPolicy, MeasuredByQualifier, MeasuredBy, Explain, Status, DateType,
                  Directness, CapabilityLevel, PreferenceStatus, TaskType, ModelRowStatus,
                  AccessKind, FeedbackRating):
        values.extend(str(v) for v in typing.get_args(alias))
    values.extend(QUALIFIER_KEYWORDS)
    return sorted(set(values))


# ── errors ─────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class Issue:
    """One thing wrong with a spec."""

    condition: str | None
    field: str | None
    reason: str
    path: str

    def __str__(self) -> str:
        parts = [self.path]
        if self.condition is not None:
            parts.append(f"condition {self.condition!r}")
        if self.field is not None and self.field != self.path:
            parts.append(f"field {self.field}")
        return f"{', '.join(parts)}: {self.reason}"


class SpecError(ValueError):
    """An invalid spec. ``issues`` lists every problem found."""

    def __init__(self, issues: list[Issue]) -> None:
        self.issues = issues
        super().__init__("invalid spec:\n" + "\n".join(f"  {issue}" for issue in issues))


def _loc(loc: tuple[Any, ...]) -> str:
    out = ""
    for part in loc:
        if isinstance(part, int):
            out += f"[{part}]"
        elif part.startswith("<") or "[" in part or part in _UNION_TAGS:
            continue
        else:
            part = _ALIASES.get(part, part)
            out = f"{out}.{part}" if out else str(part)
    return out


_ALIASES = {"in_": "in", "not_": "not", "class_": "class"}


_UNION_TAGS = {"bool", "int", "float", "date", "str", "ModelRef", "tuple"}


def _message(error: Mapping[str, Any]) -> str:
    if error["type"] == "extra_forbidden":
        return "not a spec field" if len(error["loc"]) == 1 else "unexpected field"
    if error["type"] == "missing":
        return "required"
    return str(error["msg"]).removeprefix("Value error, ")


def _issues(exc: ValidationError) -> list[Issue]:
    issues: list[Issue] = []
    for error in exc.errors():
        where = _loc(error["loc"])
        nested = error.get("ctx", {}).get("error")
        if isinstance(nested, ConditionError):
            path = _join(where, nested.path) if nested.path else where
            issues.append(Issue(nested.condition, nested.field, nested.reason, path))
        else:
            issues.append(Issue(None, where, _message(error), where))
    return issues


# ── the registry check ─────────────────────────────────────────────────────


FacetLookup = Callable[[str], Any]


def _refinement_key_issues(key: str, term: Any, facets: FacetLookup) -> list[Issue]:
    """A refinement key names a domain (or ``any``) and takes a numeric weight.

    Whether the refinement is registered and rankable depends on the snapshot's
    evidence, so the engine checks that (``decision.engine.validate``).
    """
    parent = key.split("/", 1)[0]
    issues = []
    if parent != "any":
        try:
            info = facets(parent)
        except KeyError:
            info = None
        if getattr(getattr(info, "parameter", None), "name", None) != "domain":
            issues.append(Issue(None, key, f"refinement parent {parent!r} is not a domain",
                                "optimize.weights"))
    if isinstance(term, Preference):
        issues.append(Issue(None, key, "a refinement takes a numeric weight, not a preference",
                            "optimize.weights"))
    return issues


def check_facets(spec: Spec, facets: FacetLookup) -> list[Issue]:
    """Every facet a spec names must be registered, and ordered where it is ordered."""
    issues: list[Issue] = []

    def use(
        facet_id: str,
        ordered: bool,
        path: str,
        condition: str | None,
        qualifiers: EvidenceQualifiers | None = None,
    ) -> None:
        try:
            info = facets(facet_id)
        except KeyError as exc:
            detail = str(exc)
            reason = detail if detail.startswith("unknown facet ") else (
                f"unknown facet {facet_id!r}: not in the facet registry"
            )
            issues.append(Issue(condition, facet_id, reason, path))
            return
        if not getattr(info, "addressable", True):
            issues.append(Issue(
                condition,
                facet_id,
                f"{facet_id} is record-only and cannot be used in a spec until MODEL-179",
                path,
            ))
            return
        value_type = info.value_type
        kind = value_type if isinstance(value_type, str) else value_type.kind
        if qualifiers is not None and getattr(info, "subject", None) != "evidence":
            issues.append(Issue(
                condition,
                facet_id,
                "evidence qualifiers are only valid on evidence facets",
                path,
            ))
        if ordered and kind in UNORDERED_VALUE_TYPES:
            issues.append(Issue(condition, facet_id,
                                f"{facet_id} is a {kind} facet, which has no order; "
                                "use = or in {…}", path))

    def walk(cond: Any, path: str) -> None:
        if isinstance(cond, AnyOf | AllOf):
            name = "any" if isinstance(cond, AnyOf) else "all"
            for i, child in enumerate(cond.any if isinstance(cond, AnyOf) else cond.all):
                walk(child, f"{path}.{name}[{i}]")
        elif isinstance(cond, NotOf):
            walk(cond.not_, f"{path}.not")
        elif isinstance(cond, Known):
            use(cond.known, False, path, render_condition(cond))
        else:
            ordered = isinstance(cond, Window) or (isinstance(cond, Compare)
                                                   and cond.op in ORDERED_OPS)
            use(
                cond.facet,
                ordered,
                path,
                render_condition(cond),
                getattr(cond, "qualifiers", None),
            )

    for i, cond in enumerate(spec.where):
        walk(cond, f"where[{i}]")
    if isinstance(spec.profile, InventoryProfile):
        for i, cond in enumerate(spec.profile.rules):
            walk(cond, f"profile.rules[{i}]")
    objective = spec.optimize
    for side in ("max", "min"):
        if getattr(objective, side):
            facet_id = getattr(objective, side)
            use(
                facet_id,
                True,
                f"optimize.{side}",
                None,
                objective.qualifiers.get(facet_id),
            )
    for i, step in enumerate(objective.lexicographic or []):
        use(
            step.facet,
            True,
            f"optimize.lexicographic[{i}]",
            None,
            objective.qualifiers.get(step.facet),
        )
    if objective.weights is not None:
        for signed, term in objective.weights.items():
            facet_id = _base(signed)
            if "/" in facet_id:
                issues.extend(_refinement_key_issues(facet_id, term, facets))
                continue
            try:
                info = facets(facet_id)
            except KeyError:
                use(facet_id, True, "optimize.weights", None,
                    objective.qualifiers.get(facet_id))
                continue
            kind = info.value_type if isinstance(info.value_type, str) else info.value_type.kind
            if isinstance(term, Preference):
                use(facet_id, False, "optimize.weights", None,
                    objective.qualifiers.get(facet_id))
                if signed.startswith("-"):
                    issues.append(Issue(None, facet_id,
                                        "a value preference cannot use a minus prefix",
                                        "optimize.weights"))
                elif kind not in {"bool", "boolean", "enum"}:
                    issues.append(Issue(
                        None, facet_id,
                        f"{facet_id} is a continuous {kind} facet; use a numeric weight",
                        "optimize.weights",
                    ))
                elif kind in {"bool", "boolean"} and not isinstance(term.prefer, bool):
                    issues.append(Issue(None, facet_id, "a boolean preference needs true or false",
                                        "optimize.weights"))
                elif kind == "enum":
                    allowed = getattr(info, "preference_values", None)
                    if not isinstance(term.prefer, str) or (
                        allowed is not None and term.prefer not in allowed
                    ):
                        issues.append(Issue(
                            None, facet_id,
                            f"preferred value {term.prefer!r} is not a registered value",
                            "optimize.weights",
                        ))
            elif kind in UNORDERED_VALUE_TYPES:
                issues.append(Issue(
                    None, facet_id,
                    f"{facet_id} needs a preferred value as well as a weight",
                    "optimize.weights",
                ))
            else:
                use(facet_id, True, "optimize.weights", None,
                    objective.qualifiers.get(facet_id))
    for signed in objective.pareto or []:
        facet_id = _base(signed)
        use(facet_id, True, "optimize.pareto", None,
            objective.qualifiers.get(facet_id))
    return issues


# ── parsing a spec ─────────────────────────────────────────────────────────


class _StrictLoader(yaml.SafeLoader):
    """Safe YAML that refuses duplicate keys instead of keeping the last one."""


def _no_duplicates(loader: yaml.SafeLoader, node: yaml.MappingNode, deep: bool = False) -> Any:
    seen: set[Any] = set()
    for key_node, _ in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in seen:
            raise SpecError([Issue(None, str(key), f"duplicate key {key!r}", str(key))])
        seen.add(key)
    return yaml.SafeLoader.construct_mapping(loader, node, deep)


_StrictLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _no_duplicates)


def load_yaml(text: str) -> Any:
    try:
        return yaml.load(text, Loader=_StrictLoader)  # noqa: S506 - SafeLoader subclass
    except yaml.YAMLError as exc:
        raise SpecError([Issue(None, None, f"not valid YAML: {exc}", "")]) from None


def parse_spec(raw: str | Mapping[str, Any], *, facets: FacetLookup | None) -> Spec:
    """Parse and validate a spec (YAML text or a mapping).

    ``facets`` is the registry lookup (``decision.registry.facet``). ``None``
    checks structure only. Raises ``SpecError`` naming every problem.
    """
    data = load_yaml(raw) if isinstance(raw, str) else raw
    if not isinstance(data, Mapping):
        raise SpecError([Issue(None, None, "a spec is a mapping", "")])
    try:
        spec = Spec.model_validate(data)
    except ValidationError as exc:
        raise SpecError(_issues(exc)) from None
    issues = check_facets(spec, facets) if facets is not None else []
    if spec.task is not None:
        issues.append(Issue(None, "task",
                            "free-text task is not yet in slice 1; send task_type and "
                            "capabilities instead", "task"))
    if issues:
        raise SpecError(issues)
    return spec


# ── the canonical hash ─────────────────────────────────────────────────────


def _normalise(value: Any) -> Any:
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, dict):
        return {k: _normalise(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_normalise(v) for v in value]
    return value


def canonical_json(spec: Spec) -> str:
    """The spec in its structured form, defaults filled, keys sorted, no whitespace."""
    data = _normalise(spec.model_dump(mode="json", by_alias=True, exclude_none=True))
    # Contract 1.1 adds objective qualifiers without changing the canonical
    # representation of an existing 1.0 spec.
    if not data["optimize"].get("qualifiers"):
        data["optimize"].pop("qualifiers", None)
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def spec_hash(spec: Spec) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(spec).encode("utf-8")).hexdigest()


# ── the JSON Schema ────────────────────────────────────────────────────────


def json_schema() -> dict[str, Any]:
    from pydantic.json_schema import models_json_schema

    refs, defs = models_json_schema([(Spec, "validation"), (Decision, "serialization")],
                                    ref_template="#/$defs/{model}")
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "ModelSpec decision contract",
        "x-contract-version": CONTRACT_VERSION,
        "description": "Generated from decision/contract.py by `python -m decision.schema`. "
                       "Do not edit by hand. The prose is docs/decision-contract.md.",
        "anyOf": [refs[(Spec, "validation")], refs[(Decision, "serialization")]],
        **defs,
    }


def render_json_schema() -> str:
    return json.dumps(json_schema(), indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _kind(value: Any) -> str:
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int | float):
        return "number"
    if isinstance(value, date):
        return "date"
    return "str"
