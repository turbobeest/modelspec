"""A decision as a router or gateway allow-list (MODEL-208).

ModelSpec decides which models belong on the list; a router picks among them
per request. This module writes that list as configuration and nothing else:
it never proxies inference, never holds a prompt, never calls a router, and
never embeds a credential.

What goes on the list is the decision's bands (MODEL-206): ``best`` always,
``rest`` (the other models that passed every Must, with enough evidence) on
request, and ``thin`` (not enough evidence yet) only on an explicit request,
labelled as such. A listed model carries every ranked offering it has in the
decision, the band's own offering first.

The snapshot does not publish each provider's own model ID, or a router's, so
those are written as ``<...>`` placeholders. A router rejects a placeholder, so
an unedited file admits nothing rather than something ModelSpec guessed.

Formats, each checked against the tool's own published schema in the tests:

- ``litellm``: a LiteLLM proxy ``config.yaml`` ``model_list`` (``ConfigYAML``
  in ``litellm.proxy._types``). One ``model_name`` per model, one deployment
  per offering, so LiteLLM load-balances across a model's qualifying routes.
- ``openrouter``: the body of OpenRouter's ``POST /api/v1/guardrails``
  (``CreateGuardrailRequest`` in https://openrouter.ai/openapi.json), with
  ``allowed_models`` and ``allowed_providers``.
- ``json``: ModelSpec's own format, ``schemas/router-config-v1.schema.json``.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Literal

import yaml

from decision import contract

Format = Literal["litellm", "openrouter", "json"]
FORMATS: tuple[Format, ...] = ("litellm", "openrouter", "json")
Band = Literal["best", "rest", "thin"]

GENERIC_FORMAT = "modelspec.router-config"
GENERIC_FORMAT_VERSION = "1.0"

#: ModelSpec provider ID (registry/providers.yaml) -> LiteLLM provider prefix.
#: Every value is in ``litellm.provider_list`` (checked against litellm 1.103.0).
LITELLM_PROVIDERS = {
    "openai": "openai",
    "anthropic": "anthropic",
    "google-gemini-api": "gemini",
    "xai": "xai",
    "mistral": "mistral",
    "cohere": "cohere",
    "deepseek": "deepseek",
    "alibaba-model-studio": "dashscope",
    "moonshot": "moonshot",
    "zai": "zai",
    "minimax": "minimax",
    "ai21": "ai21",
    "meta-model-api": "meta_llama",
    "aws-bedrock": "bedrock",
    "google-vertex-ai": "vertex_ai",
    "azure-ai-foundry": "azure",
    "groq": "groq",
    "together-ai": "together_ai",
    "fireworks-ai": "fireworks_ai",
    "deepinfra": "deepinfra",
    "cerebras": "cerebras",
    "sambanova": "sambanova",
    "nvidia-nim": "nvidia_nim",
    "replicate": "replicate",
    "openrouter": "openrouter",
}

#: ModelSpec provider ID -> OpenRouter provider slug, from
#: https://openrouter.ai/api/v1/providers (read 2026-09-29).
OPENROUTER_PROVIDERS = {
    "openai": "openai",
    "anthropic": "anthropic",
    "google-gemini-api": "google-ai-studio",
    "xai": "xai",
    "mistral": "mistral",
    "cohere": "cohere",
    "deepseek": "deepseek",
    "alibaba-model-studio": "alibaba",
    "moonshot": "moonshotai",
    "zai": "z-ai",
    "minimax": "minimax",
    "ai21": "ai21",
    "meta-model-api": "meta",
    "typesafe": "typesafe",
    "aws-bedrock": "amazon-bedrock",
    "google-vertex-ai": "google-vertex",
    "azure-ai-foundry": "azure",
    "groq": "groq",
    "together-ai": "together",
    "fireworks-ai": "fireworks",
    "deepinfra": "deepinfra",
    "cerebras": "cerebras",
    "sambanova": "sambanova",
    "nvidia-nim": "nvidia",
}

#: OpenRouter's ``description`` and ``name`` limits (CreateGuardrailRequest).
OPENROUTER_DESCRIPTION_MAX = 1000
OPENROUTER_NAME_MAX = 200


class EmptyAllowListError(ValueError):
    """The decision puts no model on the requested list. ``code`` is the CLI error code."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class Route:
    """One qualifying offering of a listed model."""

    offering: contract.OfferingRef
    cost_per_task: float | None
    rank: int | None

    @property
    def offering_id(self) -> str:
        ref = self.offering
        return "/".join(part or "-" for part in (ref.provider, ref.model, ref.region, ref.tier))


@dataclass(frozen=True)
class Listed:
    """One model on the list: its band, its band entry and its routes, band offering first."""

    band: Band
    entry: contract.BandEntry
    routes: tuple[Route, ...]

    @property
    def model(self) -> str:
        return self.entry.model


def listed(
    decision: contract.Decision, *, include_rest: bool = False, include_thin: bool = False,
) -> list[Listed]:
    """The models to list, best band first, then rest, then thin, each in band order."""
    bands = decision.bands
    if bands is None:
        if decision.status == "no_feasible":
            raise EmptyAllowListError("no_qualifying_models",
                                "no model passed every Must, so there is nothing to list")
        raise EmptyAllowListError(
            "no_bands",
            "this decision has no probability bands (a lexicographic or Pareto objective, "
            "or no ranked result); a router config needs a weighted or single-facet objective",
        )
    chosen: list[tuple[Band, list[contract.BandEntry]]] = [("best", bands.best)]
    if include_rest:
        chosen.append(("rest", bands.rest))
    if include_thin:
        chosen.append(("thin", bands.thin))
    rows: list[Listed] = []
    for band, entries in chosen:
        for entry in entries:
            rows.append(Listed(band=band, entry=entry, routes=_routes(decision, entry)))
    if not rows:
        hint = []
        if not include_rest and bands.rest:
            hint.append(f"--include-rest adds {len(bands.rest)}")
        if not include_thin and bands.thin:
            hint.append(f"--include-thin adds {len(bands.thin)} with not enough evidence yet")
        message = "the selected bands are empty: no model has enough evidence to lead"
        if hint:
            message += "; " + ", ".join(hint)
        raise EmptyAllowListError("empty_allow_list", message)
    return rows


def _routes(decision: contract.Decision, entry: contract.BandEntry) -> tuple[Route, ...]:
    first = Route(entry.offering, entry.cost_per_task, None)
    routes = [first]
    for row in decision.results:
        if row.offering.model != entry.model:
            continue
        if row.offering == entry.offering:
            routes[0] = Route(row.offering, row.cost_per_task, row.rank)
        else:
            routes.append(Route(row.offering, row.cost_per_task, row.rank))
    return tuple(routes)


def placeholder(where: str | None, model: str) -> str:
    """The fail-closed stand-in for an ID the snapshot does not publish.

    ``where`` is the provider or router; None for a model-level candidate,
    which the decision names without a provider (a model you host yourself).
    """
    return f"<{where or 'your deployment'} model id for {model}>"


def _bands_included(include_rest: bool, include_thin: bool) -> list[Band]:
    return ["best"] + (["rest"] if include_rest else []) + (["thin"] if include_thin else [])


def _reasons(row: Listed, bands: contract.Bands) -> list[str]:
    entry = row.entry
    if row.band == "best":
        if entry.model == bands.leader:
            why = "best band: the leader, the best weighted score among models with enough evidence"
        else:
            why = (f"best band: P(score >= leader's) = {entry.p_beats_leader:.2f}, at least "
                   f"{bands.band_probability:g}")
    elif row.band == "rest":
        p = "unknown" if entry.p_beats_leader is None else f"{entry.p_beats_leader:.2f}"
        why = f"rest band: P(score >= leader's) = {p}, below {bands.band_probability:g}"
    else:
        why = (f"thin: not enough evidence yet (a weighted capability's 80% interval is wider "
               f"than {bands.thin_interval_width:g}); listed only because it was asked for")
    return ["passed every Must", why]


def _audit(decision: contract.Decision, command: str | None) -> dict[str, object]:
    audit: dict[str, object] = {
        "generated_by": "modelspec decide --emit-router-config",
        "decision_id": decision.decision_id,
        "spec_hash": decision.spec_hash,
        "snapshot": decision.snapshot,
        "contract_version": decision.contract_version,
        "signature_verified": decision.signature_verified,
    }
    if command is not None:
        audit["regenerate"] = command
    return audit


def render(
    decision: contract.Decision,
    fmt: Format,
    *,
    include_rest: bool = False,
    include_thin: bool = False,
    command: str | None = None,
) -> str:
    """The config file's text. Raises ``EmptyAllowListError`` when nothing qualifies."""
    rows = listed(decision, include_rest=include_rest, include_thin=include_thin)
    assert decision.bands is not None
    included = _bands_included(include_rest, include_thin)
    audit = _audit(decision, command)
    if fmt == "litellm":
        return _litellm(rows, audit, included)
    if fmt == "openrouter":
        return _openrouter(rows, audit, included)
    if fmt == "json":
        return _generic(rows, decision.bands, audit, included)
    raise ValueError(f"unknown router config format {fmt!r}; valid: {', '.join(FORMATS)}")


def _litellm(rows: list[Listed], audit: dict[str, object], included: list[Band]) -> str:
    model_list = []
    for row in rows:
        for route in row.routes:
            provider = route.offering.provider
            prefix = LITELLM_PROVIDERS.get(
                provider or "", f"<litellm provider for {provider or 'your deployment'}>")
            model_list.append({
                "model_name": row.model,
                "litellm_params": {"model": f"{prefix}/{placeholder(provider, row.model)}"},
                # LiteLLM's ConfigYAML schema requires these three keys; null
                # mode and base_model leave LiteLLM's own defaults in place.
                "model_info": {"id": f"modelspec:{route.offering_id}", "mode": None,
                               "base_model": None},
            })
    header = [f"{key}: {value}" for key, value in audit.items()]
    header += [
        f"bands: {', '.join(included)}",
        "",
        "Written by ModelSpec: configuration only. ModelSpec never proxies inference,",
        "holds prompts, calls this router, or embeds credentials. No api_key is set:",
        "LiteLLM reads each provider's own environment variables; add",
        "api_key: os.environ/NAME, api_base or a region where your deployment needs it.",
        "Replace every <...> with the provider's own model ID before use.",
        "",
    ]
    for row in rows:
        label = " [thin: not enough evidence yet]" if row.band == "thin" else ""
        header.append(f"{row.band}: {row.model}{label}")
    comment = "".join(f"# {line}".rstrip() + "\n" for line in header)
    body = yaml.safe_dump({"model_list": model_list}, sort_keys=False, allow_unicode=True)
    return comment + body


def _openrouter(rows: list[Listed], audit: dict[str, object], included: list[Band]) -> str:
    routes = [route for row in rows for route in row.routes]
    providers: list[str] = []
    for route in routes:
        # A model-level candidate (a model you host yourself) names no provider.
        if (provider := route.offering.provider) is None:
            continue
        slug = OPENROUTER_PROVIDERS.get(provider, f"<openrouter provider for {provider}>")
        if slug not in providers:
            providers.append(slug)
    unnamed = [row.model for row in rows if not any(r.offering.provider for r in row.routes)]
    thin = [row.model for row in rows if row.band == "thin"]
    description = (
        f"Written by ModelSpec (configuration only). decision {audit['decision_id']}; "
        f"spec {audit['spec_hash']}; snapshot {audit['snapshot']}; "
        f"contract {audit['contract_version']}; bands: {', '.join(included)}. "
        "Replace every <...> with the OpenRouter model slug. "
        + ("allowed_providers applies to every allowed model, so it can admit a model "
           "through a provider where that model did not qualify."
           if providers else
           "No allowed_providers: this decision ties no listed model to a provider.")
    )
    if providers and unnamed:
        # Fail closed: keep the providers the decision names rather than drop the list.
        description += (" No provider named for " + ", ".join(unnamed)
                        + "; reachable only through allowed_providers.")
    if thin:
        description += " Thin, not enough evidence yet: " + ", ".join(thin)
    if len(description) > OPENROUTER_DESCRIPTION_MAX:
        description = description[: OPENROUTER_DESCRIPTION_MAX - 3] + "..."
    body: dict[str, object] = {
        "name": f"modelspec {audit['decision_id']}"[:OPENROUTER_NAME_MAX],
        "description": description,
        "allowed_models": [placeholder("openrouter", row.model) for row in rows],
    }
    if providers:
        body["allowed_providers"] = providers
    return json.dumps(body, indent=2, ensure_ascii=False) + "\n"


def _generic(rows: list[Listed], bands: contract.Bands, audit: dict[str, object],
             included: list[Band]) -> str:
    body = {
        "format": GENERIC_FORMAT,
        "format_version": GENERIC_FORMAT_VERSION,
        "audit": audit,
        "bands": {
            "included": included,
            "basis": bands.basis,
            "band_probability": bands.band_probability,
            "thin_interval_width": bands.thin_interval_width,
            "leader": bands.leader,
        },
        "models": [
            {
                "model": row.model,
                "band": row.band,
                "thin": row.band == "thin",
                "p_best": row.entry.p_best,
                "p_beats_leader": row.entry.p_beats_leader,
                "score": row.entry.score,
                "score_interval": list(row.entry.score_interval),
                "routes": [
                    {
                        "offering_id": route.offering_id,
                        "provider": route.offering.provider,
                        "region": route.offering.region,
                        "tier": route.offering.tier,
                        "rank": route.rank,
                        "cost_per_task": route.cost_per_task,
                        "provider_model_id": None,
                    }
                    for route in row.routes
                ],
                "reasons": _reasons(row, bands),
            }
            for row in rows
        ],
    }
    return json.dumps(body, indent=2, ensure_ascii=False) + "\n"
