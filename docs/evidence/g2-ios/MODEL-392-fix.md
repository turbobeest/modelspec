# MODEL-392 execution evidence

`SubscriptionOffering` now accepts the registry-defined optional
`offering.subscription.availability` fact. The public decision output is
unchanged. The final full engine suite passes with exit code **0**.

## Revisions and scope

- Engine base: `2bb355f25cdaaa917a623426c79b071642c011be`, the checked-out
  `origin/main` when this work began.
- Implementation commit: `c1aedd2d28ba7bb5749a4b59e4c9f32d6d268b27`.
- Worktree: `/Users/terbeest/dev/worktrees/model-392`.
- Branch: `model-392-availability-facet`.
- Final delivery SHA is the commit containing this report. Resolve it with
  `git log -1 --format=%H -- docs/evidence/g2-ios/MODEL-392-fix.md`.
  The PR body records the literal engine SHA.

The executor read the execution brief, the orchestrator's A and B instructions,
`AGENTS.md`, `CLAUDE.md`, `CONTEXT.md`, and `docs/handoff/README.md`.
There is no CodeGraph index in this worktree. Engine edits stayed here.
Private data and its pin were not copied into this engine branch or changed.

## Red before implementation

The new tests call `load_subscription_offerings` with a YAML file and the real
registry. The fixture has a registered provider and all required subscription
facts. The availability fact has the same structure that the real loader rejects.

Before the implementation change, `pytest -k 'subscription_file_'` returned
**1**, with **4 failed, 3 passed, 59 deselected** in 0.57 seconds.
[Complete red receipt](MODEL-392/red.log.gz).

The four failures were:

- `test_subscription_file_loads_registered_availability[open]`
- `test_subscription_file_loads_registered_availability[existing_subscribers_only]`
- `test_subscription_file_loads_registered_availability[retired]`
- `test_subscription_file_loads_unknown_availability_without_checked_sources`

Each failed with `missing=[], extra=['offering.subscription.availability']`.
The three rejection cases already passed: an unregistered subscription facet,
a registered metered-price facet on a subscription, and an invalid availability
enum value. Those guards remain active after the change.

## Change and focused green result

One entry was added to `SubscriptionOffering.PLAN_FACETS`. Required facets,
duplicate detection, source requirements, and registered-value validation are
unchanged. Unknown availability follows the existing optional-fact policy and
does not need checked sources. Missing availability remains valid.

The narrow allowlist preserves the loader's existing policy and registry
adapters that expose individual facet lookups. Replacing that policy with
registry-wide enumeration would change the adapter dependency and acceptance
rules beyond this defect.

The domain-model, subscription-routing, decision-contract, and MCP contract
version suites returned **0**, **347 passed in 40.03s**.
[Focused green receipt](MODEL-392/focused.log.gz).
This includes all seven new loader cases, existing absent-availability coverage,
complete and bounded availability output, and vocabulary behavior.

## Public contract output is unchanged

The contract assessment read `docs/decision-contract.md`, the relevant types in
`decision/contract.py`, the generated `docs/decision-contract.schema.json`, and
the schema generator. MODEL-384 already introduced availability under complete
contract **2.18** and bounded **1.5**. The existing schema includes the optional
`EstateMark.availability`, its three enum values, and `excluded_plans` on both
`Decision` and `WithEstate`. Vocabulary output already supports availability.

`decision/snapshot.py:collect_repo` reads raw subscription mappings from YAML.
It already admits the registered availability facet without this loader.
A search of production Python code finds no caller of
`load_subscription_offerings` outside its own definition and implementation.
The loader fix therefore repairs domain-record validation without changing the
production snapshot's admission or the public response.

There is no new optional response field and no widened response field. Under
MODEL-59, neither a minor nor a major bump applies. Complete **2.18**, bounded
**1.5**, and vocabulary **1** stay unchanged. `python -m decision.schema --check`
returned **0**, and the contract, schema, bounded projection, vocabulary, and MCP
version files are byte-identical to the base revision.
The schema SHA-256 remains
`1168a7427010b79dd3bffad40c61540bdc4848913a22388f1bdc52a45055d7b0`.

## Full suite and checks

The first required four-worker run returned **1**: **2 failed, 11,050 passed,
24 skipped, 11 warnings in 1623.74s**. Both failures were in
`tests/test_social_cards.py`:

- `test_build_emits_every_template_preview_and_card`
- `test_every_frozen_template_card_has_clean_chromium_layout`

Both reported `ERR_MODULE_NOT_FOUND` for `@playwright/test`. This fresh worktree
had no `web/node_modules`. The executor installed the locked web dependencies,
installed Chromium into this worktree, and built the frontend, following the
setup in `.github/workflows/test.yml`. All three setup commands returned **0**
and changed no tracked source file. The two failed tests then returned **0**,
**2 passed in 190.17s**. No application change or test relaxation was needed.
[Initial full receipt](MODEL-392/full-initial.log.gz) and
[corrected rendering receipt](MODEL-392/social-cards-green.log.gz).

The second full four-worker run used that prepared environment and returned
**0**: **11,067 passed, 9 skipped, 11 warnings in 1166.34s**.
[Final full receipt](MODEL-392/full-prepared.log.gz).
[checks.json](MODEL-392/checks.json) records the exit codes, summaries, and
compressed-receipt SHA-256 values for every pytest run.

The deferred repository-subscription test body and the snapshot test file are
unchanged from the base revision. Data tests 2 and 3 stay deferred until the
engine PR merges and the private data pin advances, as the orchestrator directed.
All foreground validation commands have completed.

Ruff and whitespace checks passed. No frozen model, offering, registry, or
verification data changed. No contract artifact was regenerated or edited.

## Commands and tools

Commands run from the engine worktree. Each pytest command redirected stdout and
stderr to its receipt and captured `result=$?` immediately afterward.

```bash
git rev-parse HEAD origin/main
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_decision_model.py -k 'subscription_file_'
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_decision_model.py tests/test_subscription_availability.py tests/test_decision_contract.py tests/test_mcp_contract_version.py
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m decision.schema --check
export PATH="/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH"
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile
export PATH="/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH"
npm ci --prefix web --no-audit --no-fund
export PLAYWRIGHT_BROWSERS_PATH="$PWD/.artifacts/model-392/browsers"
web/node_modules/.bin/playwright install chromium
npm run build --prefix web
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_social_cards.py::test_build_emits_every_template_preview_and_card tests/test_social_cards.py::test_every_frozen_template_card_has_clean_chromium_layout
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile
/Users/terbeest/dev/modelspec/.venv/bin/python -m ruff check decision/model.py tests/test_decision_model.py
git diff --exit-code 2bb355f25cdaaa917a623426c79b071642c011be -- decision/contract.py decision/bounded.py decision/vocabulary.py docs/decision-contract.md docs/decision-contract.schema.json mcp/src/contract-version.ts
git diff 2bb355f25cdaaa917a623426c79b071642c011be -- tests/test_decision_model.py tests/test_decision_snapshot.py
git diff --check
git diff --cached --check
```

Python **3.14.4**, pytest **9.1.1**, Pydantic **2.13.5**, PyYAML **6.0.3**,
Ruff **0.16.6**, Node **22.22.3**, npm **10.9.8**, Playwright **1.63.0**,
Git **2.50.1**, and gh **2.102.0** were used.
The host's load rose above 150 during the full suite. The executor waited
120 seconds before starting additional checks. The load then fell below 30.

No vendor API, Firecrawl, model inference, paid probe, real tmux operation,
device, glasses, source-cache upload, Linear write, SSH, SCP, workflow dispatch,
merge, production deployment, or independent cross-model approval was observed.
