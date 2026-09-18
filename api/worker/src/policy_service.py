"""`POST /v1/policy-check` — is this model permitted here, and which clause says so.

MODEL-80. `entry.py` is the Worker: it routes, reads the body, fetches the
published export, reads the determination store out of KV and writes the
response. Everything that decides *what the answer is* lives here, importing
nothing from the Workers runtime, so `tests/test_policy_check.py` exercises the
whole endpoint under CPython. That is the same split `rank_service.py` makes,
for the same reason.

## The third state is the product

A compliance answer has three states, not two:

* **pass** — every constraint in the caller's policy is satisfied, by a value
  that was read from a named document on a named day.
* **fail** — a constraint is violated. The response names *which* one and cites
  the document that eliminated the model.
* **undetermined** — nobody knows. This is the answer a governance buyer is
  paying to eliminate, and the one answer no competitor gives.

`undetermined` is therefore **structurally** distinct from `pass` in this
schema, not a flag on a pass and not a null: each check carries exactly one of
`satisfied`, `violated` or `undetermined` as a sibling key, and each row carries
exactly one of `passed`, `failed` or `undetermined`. A consumer that only knows
how to read `satisfied` finds no `satisfied` key on an undetermined check, so
the failure mode is a `KeyError` in the caller's code rather than a model
deployed on a licence nobody read. That asymmetry is deliberate: a tool that
silently treats a null as a pass is worse than no tool.

A caller who cannot act on "nobody knows" sets `require_no_undetermined: true`
and gets `HTTP_UNDETERMINED_PRESENT` — a documented hard failure naming every
undetermined constraint — instead of a 200 they have to audit.

## No verdict is ever inferred

Standing rules 1 and 2. Every one of these yields `undetermined`, never a
default and never a guess:

* a licence the card does not name;
* an origin country the card leaves blank;
* a `commercial_use` whose only citation is `legacy-import`, which is the
  card schema's own admission that nothing was read (`schema/card.py`);
* a platform whose residency nobody has published, or that was recorded as
  unreached;
* a local runtime, where residency is a property of the operator's machine and
  no region list can ever be truthful (`scripts/residency/platforms.py`);
* anything this request's tier is not entitled to read.

A withheld platform is never this third state on the paid tier. It resolves
to a cited region list, or to a no-commitment finding: the documents that
were read and what they said instead of a region. That finding is a `fail`
against a residency requirement — there is no region to match — not an
empty `not_determined`.

Residency regions are matched **literally** against the list the platform
itself published. Mapping "Germany" onto `eu-central-1`, or a country code onto
a cloud region, is an inference about a vendor's geography, and this endpoint
does not make inferences about the thing it is being paid to be certain about.
The published vocabulary is returned with the verdict so a caller can see what
they have to match.

## Per model *and* per platform

Residency is a property of the place a model is served from, not of the model
(MODEL-79). So a verdict is emitted for every (model, platform) pair the card
claims availability on, and a model that passes on one platform can fail on
another. A card naming no platform gets one row with `platform: null`, whose
residency check is `undetermined` rather than waved through.

## The free tier

The endpoint is free. The determinations are not
(`docs/business/decision-record.md` §3.2). A request with no entitlement to the
determination store is answered from the public export alone, and the response
says so in `determinations` — tier, what was read, and what each undetermined
check would have been answered by. The difference is legible on every row:
never a silent degradation, and never a `pass` that a paid answer would have
turned into a `fail`. When a request *is* entitled and the store cannot be
read, the request fails outright rather than quietly returning the free answer.
"""

from __future__ import annotations

from typing import Any

#: Bumped only for an incompatible change to this envelope. Independent of
#: `rank_service.SCHEMA_VERSION`, of the CLI envelope, and of
#: `build.export_schema_version`.
SCHEMA_VERSION = "1.0"

HTTP_OK = 200
HTTP_BAD_REQUEST = 400
#: A well-formed request the endpoint refuses to answer with a 200: the caller
#: demanded no undetermined rows and there are some. Documented, and never
#: downgraded to a 200 with a warning field nobody reads.
HTTP_UNDETERMINED_PRESENT = 422
#: The caller is entitled to the determinations and they could not be read.
#: Deliberately not "answer from the public export and mention it": a paid
#: caller silently receiving the free answer is the exact failure this product
#: exists to prevent.
HTTP_DETERMINATIONS_UNAVAILABLE = 503

#: A policy document is a few hundred bytes plus, at most, a model list.
MAX_BODY_BYTES = 256 * 1024

DEFAULT_LIMIT = 50
MAX_LIMIT = 500
#: How many models a caller may name explicitly. Beyond this, omit `models` and
#: page through the catalogue.
MAX_NAMED_MODELS = 500

VERDICTS = ("pass", "fail", "undetermined")

#: What a tier is allowed to read. `entry.py` decides which one a request gets;
#: MODEL-69 owns the key that decides it. Nothing in this module authenticates.
ENTITLEMENT_PUBLIC = "public_export"
ENTITLEMENT_DETERMINATIONS = "determinations"
ENTITLEMENTS = (ENTITLEMENT_PUBLIC, ENTITLEMENT_DETERMINATIONS)

#: The `commercial_use` values on a public card that assert something about a
#: licence. `unspecified` and `withheld` describe the file, not the world.
DETERMINED_PERMISSIONS = ("allowed", "restricted", "prohibited")

#: The source kind that means "nobody cited anything". `schema/card.py` keeps it
#: deliberately ugly and `schema/enrichment.py` forbids it outright; a
#: compliance answer treats it as no answer at all.
UNCITED_SOURCE_KIND = "legacy-import"

#: Why a check could not be answered. Each one leads somewhere different, so
#: they are kept apart rather than collapsed into "unknown".
WHY = {
    "tier": "this request's tier reads the public export only; the determination "
            "is a paid entitlement",
    "not_determined": "the determination store holds no determination for this",
    "not_on_card": "the public card does not carry this fact",
    "uncited": "the card carries a value whose only citation is 'legacy-import', "
               "which is the schema's own record that no document was read",
    "unbounded": "the model runs on hardware the operator controls, so residency "
                 "is a property of that deployment and no region list can be true "
                 "of the platform",
    "no_platform": "the card names no platform, so there is no place whose "
                   "residency could be determined",
}


class RequestError(ValueError):
    """A request this endpoint refuses, with the code the caller gets back."""

    def __init__(self, code: str, message: str, status: int = HTTP_BAD_REQUEST,
                 **detail: Any) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status = status
        self.detail = detail


# ── request parsing ──────────────────────────────────────────────────────────

def _object(value: Any, field: str) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise RequestError("invalid_request", f"{field} must be an object")
    return value


def _string_list(value: Any, field: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
        raise RequestError("invalid_request", f"{field} must be a list of strings")
    items = [v.strip() for v in value if v.strip()]
    if len(items) != len(value):
        raise RequestError("invalid_request", f"{field} must not contain empty strings")
    return items


def _bool(value: Any, field: str, default: bool) -> bool:
    if value is None:
        return default
    if not isinstance(value, bool):
        raise RequestError("invalid_request", f"{field} must be true or false")
    return value


def _reject_unknown(block: dict[str, Any], accepted: set[str], where: str) -> None:
    stray = sorted(set(block) - accepted)
    if stray:
        raise RequestError("invalid_request",
                           f"unknown {where} field(s): " + ", ".join(stray),
                           fields=stray, accepted=sorted(accepted))


def parse_policy(raw: Any) -> dict[str, Any]:
    """The caller's policy document, reduced to the four constraints it can state.

    An empty policy is refused rather than answered. "Every model passes"
    against no constraints is technically true and useless, and a caller who
    posted the wrong field name would receive it as a clean bill of health.
    """
    policy = _object(raw, "policy")
    _reject_unknown(policy, {"name", "licence", "origin", "residency", "commercial_use"},
                    "policy")

    parsed: dict[str, Any] = {"name": None, "constraints": {}}
    name = policy.get("name")
    if name is not None:
        if not isinstance(name, str) or not name.strip():
            raise RequestError("invalid_request", "policy.name must be a non-empty string")
        parsed["name"] = name.strip()

    if "licence" in policy:
        licence = _object(policy["licence"], "policy.licence")
        _reject_unknown(licence, {"allowed", "prohibited"}, "policy.licence")
        allowed = _string_list(licence.get("allowed"), "policy.licence.allowed")
        prohibited = _string_list(licence.get("prohibited"), "policy.licence.prohibited")
        if not allowed and not prohibited:
            raise RequestError("invalid_request",
                               "policy.licence must state allowed or prohibited licence types")
        overlap = sorted(set(allowed) & set(prohibited))
        if overlap:
            raise RequestError("invalid_request",
                               "policy.licence lists the same licence as allowed and "
                               "prohibited: " + ", ".join(overlap))
        parsed["constraints"]["licence"] = {"allowed": allowed, "prohibited": prohibited}

    if "origin" in policy:
        origin = _object(policy["origin"], "policy.origin")
        _reject_unknown(origin, {"permitted_countries", "prohibited_countries"},
                        "policy.origin")
        permitted = _string_list(origin.get("permitted_countries"),
                                 "policy.origin.permitted_countries")
        prohibited = _string_list(origin.get("prohibited_countries"),
                                  "policy.origin.prohibited_countries")
        if not permitted and not prohibited:
            raise RequestError("invalid_request",
                               "policy.origin must state permitted or prohibited countries")
        parsed["constraints"]["origin"] = {"permitted_countries": permitted,
                                           "prohibited_countries": prohibited}

    if "residency" in policy:
        residency = _object(policy["residency"], "policy.residency")
        _reject_unknown(residency, {"required_regions", "match"}, "policy.residency")
        regions = _string_list(residency.get("required_regions"),
                               "policy.residency.required_regions")
        if not regions:
            raise RequestError("invalid_request",
                               "policy.residency.required_regions must name at least "
                               "one region, spelled as the platform publishes it")
        match = residency.get("match", "any")
        if match not in ("any", "all"):
            raise RequestError("invalid_request",
                               "policy.residency.match must be 'any' or 'all'",
                               accepted=["any", "all"])
        parsed["constraints"]["residency"] = {"required_regions": regions, "match": match}

    if "commercial_use" in policy:
        commercial = _object(policy["commercial_use"], "policy.commercial_use")
        _reject_unknown(commercial, {"required", "accept_restricted"},
                        "policy.commercial_use")
        required = _bool(commercial.get("required"), "policy.commercial_use.required", True)
        if not required:
            raise RequestError(
                "invalid_request",
                "policy.commercial_use.required is false, which states no requirement. "
                "Omit the block instead, so the response does not report a constraint "
                "that constrains nothing.")
        parsed["constraints"]["commercial_use"] = {
            "required": True,
            # A `restricted` grant is not a pass by default. The caller has to
            # say they accept conditions, and they get the condition text either
            # way — "allowed unless you exceed 700M monthly active users" is the
            # answer a buyer needs; `true` is not.
            "accept_restricted": _bool(commercial.get("accept_restricted"),
                                       "policy.commercial_use.accept_restricted", False),
        }

    if not parsed["constraints"]:
        raise RequestError(
            "invalid_request",
            "the policy states no constraints, so every model would pass it. "
            "State at least one of licence, origin, residency or commercial_use.",
            accepted=["licence", "origin", "residency", "commercial_use"])
    return parsed


def parse_request(payload: Any, known_platforms: set[str]) -> dict[str, Any]:
    """Validate the body. Nothing here is defaulted into a constraint."""
    if not isinstance(payload, dict):
        raise RequestError("invalid_request", "the request body must be a JSON object")
    _reject_unknown(payload, {"policy", "require_no_undetermined", "models", "platforms",
                              "verdicts", "limit", "offset"}, "top-level")

    if "policy" not in payload:
        raise RequestError("invalid_request", "policy is required")
    policy = parse_policy(payload["policy"])

    models = _string_list(payload.get("models"), "models")
    if len(models) > MAX_NAMED_MODELS:
        raise RequestError("invalid_request",
                           f"models names {len(models)} models; the limit is "
                           f"{MAX_NAMED_MODELS}. Omit it to check the catalogue and page "
                           "with limit and offset.")

    platforms = _string_list(payload.get("platforms"), "platforms")
    unknown = sorted(set(platforms) - known_platforms)
    if unknown:
        # A typo'd platform would otherwise silently narrow the answer to
        # nothing, which reads as "no model is available anywhere".
        raise RequestError("unknown_platform",
                           "unknown platform(s): " + ", ".join(unknown),
                           fields=unknown, accepted=sorted(known_platforms))

    verdicts = _string_list(payload.get("verdicts"), "verdicts")
    bad = sorted(set(verdicts) - set(VERDICTS))
    if bad:
        raise RequestError("invalid_request", "unknown verdict(s): " + ", ".join(bad),
                           accepted=list(VERDICTS))

    limit = payload.get("limit", DEFAULT_LIMIT)
    if isinstance(limit, bool) or not isinstance(limit, int):
        raise RequestError("invalid_request", "limit must be an integer")
    if limit < 0:
        raise RequestError("invalid_request", "limit must be nonnegative")
    if limit > MAX_LIMIT:
        raise RequestError("invalid_request", f"limit must be at most {MAX_LIMIT}")

    offset = payload.get("offset", 0)
    if isinstance(offset, bool) or not isinstance(offset, int):
        raise RequestError("invalid_request", "offset must be an integer")
    if offset < 0:
        raise RequestError("invalid_request", "offset must be nonnegative")

    return {
        "policy": policy,
        "require_no_undetermined": _bool(payload.get("require_no_undetermined"),
                                         "require_no_undetermined", False),
        "models": models,
        "platforms": platforms,
        "verdicts": verdicts or list(VERDICTS),
        "limit": limit,
        "offset": offset,
    }


# ── check results: exactly one of satisfied / violated / undetermined ────────

def _satisfied(constraint: str, requirement: dict[str, Any],
               **evidence: Any) -> dict[str, Any]:
    return {"constraint": constraint, "requirement": requirement,
            "state": "satisfied", "satisfied": evidence}


def _violated(constraint: str, requirement: dict[str, Any],
              **evidence: Any) -> dict[str, Any]:
    return {"constraint": constraint, "requirement": requirement,
            "state": "violated", "violated": evidence}


def _undetermined(constraint: str, requirement: dict[str, Any], why: str,
                  **evidence: Any) -> dict[str, Any]:
    """The third state. Never a null, never a missing key on a pass."""
    body = {
        "why": why,
        "meaning": WHY[why],
        # Where the answer would come from. `null` when nothing can supply it —
        # a local runtime's residency is not for sale, it does not exist.
        "available_in_tier": "paid" if why == "tier" else None,
    }
    body.update(evidence)
    return {"constraint": constraint, "requirement": requirement,
            "state": "undetermined", "undetermined": body}


def _cite(source: dict[str, Any] | None) -> dict[str, Any] | None:
    """A citation reduced to what a customer has to be able to check later."""
    if not source:
        return None
    return {"kind": source.get("kind"), "url": source.get("url") or None,
            "read_on": source.get("read_on") or None,
            "quote": source.get("quote") or None}


def _is_cited(source: dict[str, Any] | None) -> bool:
    """A source good enough to hang a verdict on: a document, and a read date."""
    if not source:
        return False
    if source.get("kind") == UNCITED_SOURCE_KIND:
        return False
    return bool(source.get("url")) and bool(source.get("read_on"))


def _documents(determination: dict[str, Any]) -> list[dict[str, str]]:
    """Documents a negative finding rests on: each URL with the date it carries.

    Prefers the loader's `documents` objects. Falls back to `checked` URL
    strings plus `determined_on`, which is the date the store actually has —
    per-document read dates were not recorded.
    """
    determined_on = determination.get("determined_on") or ""
    raw = determination.get("documents")
    if isinstance(raw, list) and raw:
        out = []
        for item in raw:
            if not isinstance(item, dict):
                continue
            url = (item.get("url") or "").strip()
            if not url:
                continue
            read_on = (item.get("read_on") or determined_on or "").strip()
            out.append({"url": url, "read_on": read_on})
        return out
    out = []
    for item in determination.get("checked") or []:
        if isinstance(item, str) and item.strip():
            out.append({"url": item.strip(), "read_on": determined_on})
        elif isinstance(item, dict) and (item.get("url") or "").strip():
            out.append({
                "url": item["url"].strip(),
                "read_on": (item.get("read_on") or determined_on or "").strip(),
            })
    return out


# ── the four checks ──────────────────────────────────────────────────────────

def check_licence(row: dict[str, Any], requirement: dict[str, Any]) -> dict[str, Any]:
    """The licence the card names, against the caller's allow/deny lists."""
    licence = row.get("licence") or {}
    value = licence.get("license_type")
    evidence = {"license_type": value, "license_url": licence.get("license_url") or None}
    if not value:
        return _undetermined("licence", requirement, "not_on_card",
                             field="licensing.license_type", **evidence)
    if value in requirement["prohibited"]:
        return _violated("licence", requirement,
                         because=f"the licence is {value!r}, which the policy prohibits",
                         **evidence)
    if requirement["allowed"] and value not in requirement["allowed"]:
        return _violated("licence", requirement,
                         because=(f"the licence is {value!r}, which is not in the "
                                  "policy's allowed list"),
                         **evidence)
    return _satisfied("licence", requirement, **evidence)


def check_origin(row: dict[str, Any], requirement: dict[str, Any]) -> dict[str, Any]:
    """Where the model came from. A blank country is undetermined, never allowed."""
    origin = row.get("origin") or {}
    country = (origin.get("country") or "").strip()
    if not country:
        return _undetermined("origin", requirement, "not_on_card",
                             field="licensing.origin_country")
    evidence = {"origin_country": country, "org_type": origin.get("org_type")}
    if country in requirement["prohibited_countries"]:
        return _violated("origin", requirement,
                         because=(f"the model originates in {country}, which the policy "
                                  "prohibits"), **evidence)
    if requirement["permitted_countries"] and country not in requirement["permitted_countries"]:
        return _violated("origin", requirement,
                         because=(f"the model originates in {country}, which is not in "
                                  "the policy's permitted list"), **evidence)
    return _satisfied("origin", requirement, **evidence)


def check_commercial_use(row: dict[str, Any], requirement: dict[str, Any],
                         determination: dict[str, Any] | None,
                         entitled: bool) -> dict[str, Any]:
    """Is commercial use granted, and on what condition.

    The determination store wins when this request is entitled to it, because
    that is where the answer actually is. The public card is the free tier's
    only source and carries `unspecified` or `withheld` for almost every model,
    which is reported as such rather than read as "no".
    """
    if determination is not None:
        value = determination.get("value")
        conditions = (determination.get("conditions") or "").strip()
        source = _cite(determination.get("source"))
        origin_of_answer = "determinations"
        determined_on = determination.get("determined_on")
    else:
        public = row.get("commercial_use") or {}
        value = public.get("value")
        conditions = (public.get("conditions") or "").strip()
        raw_source = public.get("source")
        origin_of_answer = "public_export"
        determined_on = None
        if value not in DETERMINED_PERMISSIONS:
            # `unspecified` and `withheld` say something about this file, not
            # about the licence. Neither is a verdict.
            why = "tier" if not entitled else "not_determined"
            return _undetermined("commercial_use", requirement, why,
                                 field="licensing.commercial_use",
                                 public_state=value)
        if not _is_cited(raw_source):
            # A value with no document and no read date cannot be defended on
            # the day a customer is asked to defend it.
            return _undetermined("commercial_use", requirement, "uncited",
                                 field="licensing.commercial_use",
                                 public_state=value,
                                 source=_cite(raw_source))
        source = _cite(raw_source)

    evidence = {"commercial_use": value, "conditions": conditions or None,
                "source": source, "read_on": (source or {}).get("read_on"),
                "determined_on": determined_on, "answered_from": origin_of_answer}

    if value == "prohibited":
        return _violated("commercial_use", requirement,
                         because="the licence prohibits commercial use", **evidence)
    if value == "restricted":
        if not requirement["accept_restricted"]:
            return _violated(
                "commercial_use", requirement,
                because=("commercial use is granted only under conditions, and the "
                         "policy does not accept a conditional grant: " + conditions),
                **evidence)
        # Accepted, but never as a bare pass: the condition is the answer.
        return _satisfied("commercial_use", requirement, conditional=True, **evidence)
    if value == "allowed":
        return _satisfied("commercial_use", requirement, conditional=False, **evidence)
    return _undetermined("commercial_use", requirement, "not_determined",
                         field="licensing.commercial_use", public_state=value)


def check_residency(platform: str | None, requirement: dict[str, Any],
                    determination: dict[str, Any] | None,
                    unbounded_platforms: set[str], entitled: bool) -> dict[str, Any]:
    """Where this platform processes data, against the regions the policy needs.

    Matched literally against the list the platform published. Nothing is
    normalised: a country name is not mapped onto a cloud region, because that
    mapping is an inference about a vendor's geography and this endpoint does
    not infer. The published vocabulary comes back with the verdict.

    A no-commitment finding (`non_disclosure: no-commitment`) is a fail that
    cites the documents, not `not_determined`. A withheld card is a promise
    the paid tier has that answer.
    """
    required = requirement["required_regions"]
    if platform is None:
        return _undetermined("residency", requirement, "no_platform", platform=None)
    if platform in unbounded_platforms:
        return _undetermined("residency", requirement, "unbounded", platform=platform,
                             resolve=("determine residency against the infrastructure "
                                      "you run this on"))
    if determination is None:
        why = "tier" if not entitled else "not_determined"
        return _undetermined("residency", requirement, why, platform=platform)

    if determination.get("non_disclosure") == "no-commitment":
        # A withheld card with no region list. The paid answer is the finding:
        # the documents that were read, and what they said instead. Against a
        # residency requirement that is a fail — there is no region to match —
        # not "the store holds nothing", which is a different `why`.
        documents = _documents(determination)
        reason = (determination.get("reason") or "").strip()
        if not documents or not reason:
            return _undetermined("residency", requirement, "not_determined",
                                 platform=platform, store_scope=determination.get("scope"))
        read_on = documents[0].get("read_on") or determination.get("determined_on")
        return _violated(
            "residency", requirement,
            because=("the provider's documents were read and commit to no "
                     "processing region"),
            platform=platform,
            finding="no_commitment",
            published_regions=[],
            documents=documents,
            reason=reason,
            checked=[d["url"] for d in documents],
            determined_on=determination.get("determined_on") or None,
            read_on=read_on,
            source=None,
            matching="literal",
            missing=required,
        )

    scope = determination.get("scope")
    if scope != "determined":
        # Unreached, or an undetermined record that does not claim a
        # no-commitment finding. Still carries what was checked, which is more
        # than "unknown", but it is not a withheld answer.
        return _undetermined("residency", requirement, "not_determined", platform=platform,
                             store_scope=scope,
                             reason=determination.get("reason") or None,
                             checked=list(determination.get("checked") or []),
                             determined_on=determination.get("determined_on"))

    published = list(determination.get("regions") or [])
    source = _cite(determination.get("source"))
    evidence = {"platform": platform, "published_regions": published, "source": source,
                "read_on": (source or {}).get("read_on"),
                "determined_on": determination.get("determined_on"),
                "matching": "literal"}
    lowered = {r.strip().lower() for r in published}
    matched = [r for r in required if r.strip().lower() in lowered]
    missing = [r for r in required if r.strip().lower() not in lowered]

    if not published:
        # A determined empty list is an answer, and a bad one for this caller:
        # the platform published its terms and commits to no region.
        return _violated("residency", requirement,
                         because=("the platform publishes its terms and commits to no "
                                  "processing region"), missing=required, **evidence)
    if requirement["match"] == "all":
        if missing:
            return _violated("residency", requirement,
                             because=("the platform does not publish " +
                                      ", ".join(missing)),
                             matched=matched, missing=missing, **evidence)
        return _satisfied("residency", requirement, matched=matched, **evidence)
    if matched:
        return _satisfied("residency", requirement, matched=matched, **evidence)
    return _violated("residency", requirement,
                     because=("the platform publishes none of the required regions. "
                              "Regions are matched exactly as the platform spells them."),
                     matched=[], missing=required, **evidence)


# ── rows ─────────────────────────────────────────────────────────────────────

#: The order checks are applied and reported in. Cheapest and most decisive
#: first, so `failed.eliminated_by` is stable across runs of the same policy.
CONSTRAINT_ORDER = ("licence", "origin", "commercial_use", "residency")


def _row(model: dict[str, Any], platform: str | None,
         checks: list[dict[str, Any]]) -> dict[str, Any]:
    """One (model, platform) verdict, with the three states kept apart.

    Exactly one of `passed`, `failed` and `undetermined` is present. A row that
    both violates something and leaves something unknown is a `fail` — a
    violation that was actually found is decisive — but the unknowns are
    carried in `failed.also_undetermined` rather than dropped, because they are
    still unknown if the caller relaxes the constraint that eliminated it.
    """
    violated = [c for c in checks if c["state"] == "violated"]
    undetermined = [c for c in checks if c["state"] == "undetermined"]
    row = {
        "model_id": model["model_id"],
        "display_name": model.get("display_name"),
        "provider": model.get("provider"),
        "platform": platform,
        "checks": checks,
    }
    if violated:
        return {**row, "verdict": "fail", "failed": {
            "eliminated_by": violated[0],
            "constraint": violated[0]["constraint"],
            "also_violated": [c["constraint"] for c in violated[1:]],
            "also_undetermined": [c["constraint"] for c in undetermined],
        }}
    if undetermined:
        return {**row, "verdict": "undetermined", "undetermined": {
            "constraints": [c["constraint"] for c in undetermined],
            "checks": undetermined,
        }}
    conditions = [
        {"constraint": c["constraint"], "text": c["satisfied"].get("conditions"),
         "source": c["satisfied"].get("source")}
        for c in checks if c["satisfied"].get("conditional")
    ]
    return {**row, "verdict": "pass", "passed": {
        "constraints": [c["constraint"] for c in checks],
        # A conditional pass states its condition here too, so a caller reading
        # only the verdict block still sees it.
        "conditions": conditions,
    }}


def _platforms_for(model: dict[str, Any], wanted: list[str]) -> list[str | None]:
    available = [p["platform"] for p in (model.get("platforms") or [])]
    if wanted:
        available = [p for p in available if p in wanted]
        return list(available)
    # No platform on the card means no place whose residency can be determined.
    # That is a row, not a silence.
    return list(available) if available else [None]


def evaluate(model: dict[str, Any], platform: str | None, constraints: dict[str, Any],
             store: dict[str, Any], unbounded: set[str], entitled: bool) -> dict[str, Any]:
    """Every constraint the policy states, against one (model, platform) pair."""
    commercial = (store.get("commercial_use") or {}).get(model["model_id"]) if entitled else None
    residency = (store.get("residency") or {}).get(platform) if entitled and platform else None

    checks: list[dict[str, Any]] = []
    for name in CONSTRAINT_ORDER:
        requirement = constraints.get(name)
        if requirement is None:
            continue
        if name == "licence":
            checks.append(check_licence(model, requirement))
        elif name == "origin":
            checks.append(check_origin(model, requirement))
        elif name == "commercial_use":
            checks.append(check_commercial_use(model, requirement, commercial, entitled))
        elif name == "residency":
            checks.append(check_residency(platform, requirement, residency, unbounded,
                                          entitled))
    return _row(model, platform, checks)


# ── the answer ───────────────────────────────────────────────────────────────

def _blank_tally() -> dict[str, int]:
    return {"satisfied": 0, "violated": 0, "undetermined": 0}


def _envelope(export: dict[str, Any], service_commit: str, origin: str) -> dict[str, Any]:
    build = export.get("build") or {}
    return {
        "schema_version": SCHEMA_VERSION,
        "endpoint": "policy-check",
        "build": {
            "commit": build.get("commit"),
            "built_at": build.get("built_at"),
            "eligibility_as_of": build.get("eligibility_as_of"),
            "export_schema_version": build.get("export_schema_version"),
        },
        "service_commit": service_commit,
        "export_origin": origin,
    }


def _determinations_block(entitled: bool, store: dict[str, Any],
                          tier_blocked: int) -> dict[str, Any]:
    """What this answer was computed from, and what a different tier would add.

    Present on every response including the failures, because "which tier
    answered this" is the first thing an auditor asks and the last thing a
    caller should have to infer from the shape of the body.

    `tier_blocked` is the count of checks this tier could not settle *and a
    paid one could*. It is the whole free/paid difference, stated as a number
    on every response rather than left for the caller to discover by diffing
    two answers.
    """
    return {
        "entitlement": ENTITLEMENT_DETERMINATIONS if entitled else ENTITLEMENT_PUBLIC,
        "included": entitled,
        "answered_from": ("the public export and the determination store" if entitled
                          else "the public export only"),
        "store": {
            "loaded": entitled,
            "generated_on": store.get("generated_on") if entitled else None,
            "commercial_use_records": len(store.get("commercial_use") or {}) if entitled else 0,
            "residency_platforms": len(store.get("residency") or {}) if entitled else 0,
        },
        "undetermined_for_lack_of_entitlement": tier_blocked,
        "why": (None if entitled else
                "commercial_use and data_residency are determinations, and "
                "determinations are the paid tier. The endpoint itself is free and "
                "this answer is complete for every constraint the public export can "
                "settle; the checks it could not settle say so individually, with "
                "available_in_tier: paid."),
    }


def _read_dates(rows: list[dict[str, Any]]) -> dict[str, list[str]]:
    """Every read date this answer rests on, so it can be audited later.

    An answer is only defensible with the day each document was read, because
    licences and region lists are rewritten without notice.
    """
    dates: dict[str, set[str]] = {}
    for row in rows:
        for check in row["checks"]:
            body = check.get("satisfied") or check.get("violated") or {}
            found: set[str] = set()
            source = body.get("source") or {}
            if source.get("read_on"):
                found.add(source["read_on"])
            if body.get("read_on"):
                found.add(body["read_on"])
            for document in body.get("documents") or []:
                if isinstance(document, dict) and document.get("read_on"):
                    found.add(document["read_on"])
            if found:
                dates.setdefault(check["constraint"], set()).update(found)
    return {k: sorted(v) for k, v in sorted(dates.items())}


def check(payload: Any, export: dict[str, Any], store: dict[str, Any] | None,
          entitlement: str, service_commit: str, origin: str) -> tuple[int, dict[str, Any]]:
    """Answer one `POST /v1/policy-check`. Returns the status code and the body."""
    if entitlement not in ENTITLEMENTS:
        raise ValueError(f"unknown entitlement {entitlement!r}")
    entitled = entitlement == ENTITLEMENT_DETERMINATIONS
    if entitled and store is None:
        # Deliberately not a downgrade. See HTTP_DETERMINATIONS_UNAVAILABLE.
        raise RequestError(
            "determinations_unavailable",
            "this request is entitled to the determinations and the store could not "
            "be read. The free answer is not returned in its place, because a paid "
            "caller cannot tell one from the other and would deploy on the difference.",
            status=HTTP_DETERMINATIONS_UNAVAILABLE)
    store = store or {}

    catalogue = list(export.get("models") or [])
    known_platforms = set(export.get("platform_classes", {}).get("all") or [])
    unbounded = set(export.get("platform_classes", {}).get("unbounded") or [])
    request = parse_request(payload, known_platforms)
    constraints = request["policy"]["constraints"]

    if request["models"]:
        by_id = {m["model_id"]: m for m in catalogue}
        missing = [m for m in request["models"] if m not in by_id]
        if missing:
            raise RequestError("unknown_model",
                               "unknown model(s): " + ", ".join(sorted(missing)[:20]),
                               fields=sorted(missing))
        catalogue = [by_id[m] for m in request["models"]]

    rows: list[dict[str, Any]] = []
    for model in sorted(catalogue, key=lambda m: m["model_id"]):
        for platform in _platforms_for(model, request["platforms"]):
            rows.append(evaluate(model, platform, constraints, store, unbounded, entitled))

    verdict_counts = {v: 0 for v in VERDICTS}
    tallies = {name: _blank_tally() for name in constraints}
    models_by_verdict: dict[str, set[str]] = {v: set() for v in VERDICTS}
    tier_blocked = 0
    for row in rows:
        verdict_counts[row["verdict"]] += 1
        models_by_verdict[row["verdict"]].add(row["model_id"])
        for c in row["checks"]:
            tallies[c["constraint"]][c["state"]] += 1
            if c["state"] == "undetermined" and c["undetermined"]["why"] == "tier":
                tier_blocked += 1

    summary = {
        "models_checked": len({r["model_id"] for r in rows}),
        "rows": len(rows),
        "verdicts": verdict_counts,
        # Counted over models, not rows: "47 models pass somewhere" and "47
        # models pass everywhere" are different facts and a per-platform product
        # has to keep them apart.
        "models_with_a_passing_platform": len(models_by_verdict["pass"]),
        "models_undetermined_somewhere": len(models_by_verdict["undetermined"]),
        "by_constraint": tallies,
    }

    envelope = _envelope(export, service_commit, origin)
    determinations = _determinations_block(entitled, store, tier_blocked)
    common = {
        **envelope,
        "policy": {"name": request["policy"]["name"], "constraints": constraints,
                   "require_no_undetermined": request["require_no_undetermined"]},
        "determinations": determinations,
        "summary": summary,
    }

    if request["require_no_undetermined"] and verdict_counts["undetermined"]:
        offenders = [r for r in rows if r["verdict"] == "undetermined"]
        return HTTP_UNDETERMINED_PRESENT, {
            **common,
            "error": {
                "code": "undetermined_present",
                "message": (
                    f"{verdict_counts['undetermined']} of {len(rows)} (model, platform) "
                    "rows are undetermined, and the request required none. No verdict "
                    "was inferred for them and none will be."),
                "undetermined_rows": verdict_counts["undetermined"],
                "undetermined_by_constraint": {
                    name: tally["undetermined"] for name, tally in tallies.items()
                    if tally["undetermined"]},
                "remedy": (
                    "narrow the request with `models` or `platforms`, drop "
                    "`require_no_undetermined`, or obtain the determinations"
                    if not entitled else
                    "narrow the request with `models` or `platforms`, or drop "
                    "`require_no_undetermined`"),
                "examples": offenders[:10],
            },
            "provenance": {"determination_read_dates": _read_dates(rows)},
            "result": [],
        }

    shown = [r for r in rows if r["verdict"] in request["verdicts"]]
    page = shown[request["offset"]:request["offset"] + request["limit"]]
    return HTTP_OK, {
        **common,
        "provenance": {
            "determination_read_dates": _read_dates(rows),
            "determinations_generated_on": (store.get("generated_on") if entitled else None),
        },
        "page": {
            "offset": request["offset"], "limit": request["limit"],
            "returned": len(page),
            # `summary` always describes the whole catalogue. Only the rows are
            # paged, and the response says so rather than letting a caller read
            # a page as the answer.
            "matching_rows": len(shown),
            "truncated": request["offset"] + len(page) < len(shown),
            "verdicts_shown": request["verdicts"],
        },
        "result": page,
    }


def error_response(error: RequestError, export: dict[str, Any] | None,
                   service_commit: str, origin: str) -> tuple[int, dict[str, Any]]:
    envelope = _envelope(export or {}, service_commit, origin)
    body: dict[str, Any] = {"code": error.code, "message": error.message}
    body.update(error.detail)
    return error.status, {**envelope, "error": body, "result": []}
