# Use-case pages from decision templates

MODEL-219 slice 1 publishes dated worked examples of the Decide templates.
Comparison pages and a marketing plan are outside this slice.

## URLs and discovery

The index lives at `/use-cases/`. Each template has one canonical page at
`/use-cases/<category-id>/<template-id>/`. Category and template IDs come
from `registry/templates.yaml` through `decision/templates.py`.
The index groups categories by their registry kind, `use` or `constraint`,
and lists every template, including examples without an answer.
A shared footer links to the index. The top navigation stays as it is.
The live Pages composition must retain the directory and its sitemap entries.

## Public source and date

The examples always read the frozen data in the public repository root,
even when another build operation uses a private data overlay. They never
fetch the Worker or the network. The date is `data-image.json`'s `as_of`
when that manifest exists. Until the first lagged image has a manifest,
the public eligibility report's `as_of` supplies the date. Missing source
dates fail the example build instead of falling back to the clock.

Each page says "as of <date>, from the public data image". That date drives
the engine snapshot, JSON-LD date, and sitemap `lastmod`. The page contains
no build timestamp or build commit, so rebuilding the same image produces
identical bytes. A live Decide result can differ because it uses current data.

## From template to decision

Load the public registry and validated template catalogue. Build and load
an in-memory decision snapshot with the image date and the existing repository
snapshot builder. Parse each template's expanded `spec` with `parse_spec`,
then call `decision.engine.decide`, the engine used by `/v1/decide`.
No alternate ranking, cost sort, or ranking override is introduced.

Template-specific copy comes directly from `name`, `tradeoff`, `purpose`,
`where`, `weights`, and `teaches`. The page shows the applied spec so a reader
can inspect the assumptions. Results, model identifiers, bands, estimates,
intervals, and P(best) come from the engine response, without invented values.

An empty answer or an answer with only undetermined evidence says that no
recommendation is available. The page remains accessible from the index but
has `noindex, follow` and no sitemap entry. Unavailable template coverage is
explained beside the result. Engine and registry failures fail the build;
they are not disguised as missing evidence.

## Page anatomy and evidence

Every page leads with the shared AoA entity sentence. A template page has its
registry title and purpose, the public-image date, requirements with their
registry reasons, preferences, the computed answer, and the template lesson.
The answer shows all returned bands and their members. A tie stays a tie and
shows the engine's cheapest, open-weights, and best-measured tie-breakers.
The cheapest member is identified only as a tie-breaker. Intervals and P(best)
retain the values and nulls supplied by the decision contract. Undetermined
members are labelled as such and never promoted to recommendations.

A link opens `/decide/?template=<template-id>` with the template applied.
Human lookup is free. Any CLI, API, or MCP access statement says that a key
is required. The page links to `/legal/neutrality/` without restating the
commitment. It contains no competitor comparisons or affiliate links.

JSON-LD uses the existing structured-data helpers for breadcrumbs and a dated
Article whose title and description also appear in visible text. All new pages,
including noindex examples, are covered by the surface lint. The lint rejects
"instructions for AI" and "AI assistants should" and checks the entity lead.

## Verification

Red-first tests exercise generated HTML and the static build integration.
They cover public-root isolation, image dating, registry copy, engine values,
ties and thin evidence, neutrality, JSON-LD and lint, keyed machine access,
contract preservation, reproducibility, grouped discovery, and live retention.
The build, web build and tests, and full pytest suite under the shared lock
provide the broader gate. No decision contract, ranking floor, neutrality
commitment, legal text, frozen data, or production switch changes in this slice.
