# Comparing named models

MODEL-364 adds `modelspec compare A B [C D]` and the MCP `compare_models`
tool. Both call keyed `POST /v1/compare-models` and present the requested
models' sourced facts side by side. The existing snapshot comparison remains
`modelspec compare --spec|--template --to SNAP`.

## Endpoint choice

Option B adds one endpoint with `{"models": ["lab/a", "lab/b"]}`. The
request accepts two to four distinct model IDs. An unknown model refuses the
whole request and identifies its position. Successful rows retain caller
order, including when the models belong to different classes.

Option A would add `model.id` to the facet registry and snapshot index. That
would be useful for restricting a decision, but it does not provide a complete
comparison. A decision requires an objective, so a bare list of model names
would need an invented objective. Models lacking that objective's evidence can
be absent from ranked results, and the result limit counts offerings rather
than distinct models. The bounded representation also omits `top`, where the
complete Decision carries shown facts. Supporting every named model through
that route would require more changes than the endpoint.

The initial comparison has no optional Spec. It presents facts, offering
prices, and benchmark evidence from the verified snapshot. It computes no
quality score, rank, winner, or cost-to-correct. A class fact states each
model's class without ordering classes. A caller who needs a recommendation
uses `decide` with their own requirements and objective.

## Contracts and access

The named comparison has its own contract, `comparison_version: "1.0"`, on
success and refusal bodies. MODEL-59 applies to comparison fields under that
version. No shared Decision field widens, so its contract stays at 2.16. The
bounded decision representation stays at 1.2 and names
`projects_contract: "2.16"`. The CLI package version does not change in this
ticket.

The endpoint requires an API key even when `ACCESS_ENFORCED` is off. Browser
visit tokens do not admit it. Existing access quotas and billing apply, using
the `decide.full` credit weight. The endpoint never downloads private data to
the caller or creates a new free machine path.

## Facts, provenance, and response limits

Each model has its lifecycle, facts, offerings, and benchmark evidence. A
fact's `state` distinguishes a known value from an unknown one. Known sourced
values retain their record IDs and registered source IDs. The response's
`sources` list resolves those IDs to URLs. Evidence retains its benchmark and
available measurement qualifiers, so different harnesses or efforts remain
visible.

The success body is at most 14,000 compact UTF-8 bytes. This leaves room for
the MCP origin envelope within its 16,384-byte budget. Budget reduction removes
whole facts, offerings, or evidence items and increments `omitted` counts.
It never changes a known value to null or separates a retained value from its
provenance. Every requested model row stays present. An omission reports that
the response left something out, without claiming the model lacks that fact.

## Release

A CLI release requires operator review, a later package version change, wheel
and source distribution builds, and publication to PyPI. MODEL-364 changes the
repository implementation and tests without performing those release steps.
