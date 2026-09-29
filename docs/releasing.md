# Release the CLI to PyPI

ModelSpec publishes the `modelspec-dev` distribution. The installed command is
`modelspec`.

## Release notes

### 0.2.0 (2026-09-29)

**Decision contract 2.x.** This is the first CLI release on contract 2.x, and it is breaking for 1.x consumers. `optimize.weights` values may be `{prefer, weight}` value preferences as well as numbers. Numeric specs still work. See `docs/decision-contract.md`.

- Answers are tie-aware and use probability bands: "Best for your weights", "Not enough evidence yet", and the rest. The blend is named, with each dimension's own order, and the capability intervals are recalibrated.
- Plans ask how you'll use a model (`access`: chat app, coding tool, own software, own hardware) and account for what you already have (`estate`, `with_estate`). They cover subscriptions (including Cursor, Copilot and Perplexity), plan break-even, and hardware fit.
- Refinements such as Rust or Python under coding enter the ranking.
- You can exclude benchmarks and refit, and Prefer works on every facet.
- Results have flat fields (`model`, `model_rank`, `cost_per_task`), a `by_model` view, `--why-not MODEL_ID`, and a readable summary without `--json`.
- New: `--emit-router-config litellm|openrouter|json` writes a router or gateway allow-list from a decision. It is configuration only.
- There are 40 templates in 9 categories, each in 5 tiers.
- `decide` leads the help, and the v1 commands are marked legacy.

### 0.1.1 (2026-09-28)

- Sign snapshots with Ed25519 and publish the verification key.
- Compare decisions against another snapshot with `--compare-to`.
- Include the CLI fixes merged since 0.1.0.

## Configure the first release

Jamie must complete these steps once:

1. Create a PyPI account, or log in to the existing account. Enable two-factor
   authentication.
2. Open **Publishing** in PyPI and add a pending Trusted Publisher with these
   values:

   - PyPI project name: `modelspec-dev`
   - Owner: `turbobeest`
   - Repository: `modelspec`
   - Workflow: `release-pypi.yml`
   - Environment: `pypi`

3. In the GitHub repository settings, create an environment named `pypi`.
4. Push the first version tag:

   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```

The tag starts `.github/workflows/release-pypi.yml`. The workflow builds the
source distribution and wheel, then authenticates through PyPI Trusted
Publishing. Do not add a PyPI API token to GitHub.

For later releases, update the explicit version in `pyproject.toml`, merge that
change, and push the matching `v*` tag.
