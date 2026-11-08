# MODEL-235-readers-r3 final scope

The Mistral card-boundary changes are withdrawn. `_card_lines` is restored
byte-for-byte to the function in `ee16bf40`. The only production difference from
that pin is the MiniMax literal `<API Key>` placeholder handling in the two
subscription-reader paths. Both cross-model reviews confirmed that fix.

Review base: `c42f695e9fe3802a25209b28b938c244d8d19a50`.
Implementation commit: `892931a767fc0acf56953d917a8485dad46ebac8`.
Final delivery SHA is the commit containing this report, available with
`git log -1 --format=%H -- docs/evidence/g2-ios/MODEL-235-readers-r3-fix.md`
and in the executor's final output. The full REV-751b verdict was read before
changes. Work remains in the assigned worktree and branch.

## Decision and exact rollback

The failed premise was that flattened lines and a nearby price could establish
plan-card ownership. Two successive rules recovered one fact and exposed new
misattributions or premature boundaries. The orchestrator directed a rollback
instead of another heuristic.

The pinned function was extracted with `git show ee16bf40:decision/verify.py`
and Python AST line boundaries, then replaced as a complete function. The current
function text is asserted equal to the pinned text, including its docstring.
`git diff ee16bf40 -- decision/verify.py` shows only the two MiniMax placeholder
checks and their explanatory comment. No Mistral rule or helper remains in the
production diff.

Mistral Pro's coding-access fact is intentionally unreadable again. It is left
for the data side to re-cite to an appropriately scoped region and independently
verify the result. If an engine change is needed later, proper plan-card
segmentation should use the parsed DOM structure and explicit card ownership,
not a line-window heuristic. No data was edited in this PR.

## Tests retained and removed

The Pro positive assertion was removed as directed. The Mistral excerpt was
trimmed from 42 to 14 lines. It retains the Pro price and early features, the API
credit feature, and the following Team name, price, and domain-verification
feature required by the remaining fixture test.

All seven retained Mistral cases pass on the actual pinned engine:

- the fixture's rejection of Team's feature for Pro;
- probes A and B, including Team's verification of its own sentence;
- the bare-price and markdown-heading controls, including Team's rejection of
  the near sentence;
- `Generate Spreadsheets` and `Free` heading-like features, which deliberately
  leave Pro's own sentence at `mismatch` under the pinned reader.

Pinned safety result: `7 passed, 7 deselected in 0.25s`, exit 0. The command runs
from the pin export with pytest importlib mode, so pytest cannot prepend the
current repository package ahead of the pin.

The full new module against the pin returns exit 1 with three MiniMax positive
cases failing and the other eleven cases passing. The MiniMax tests remain
unchanged; they verify the three exact allowances and reject raw markup.
Focused current-reader suites: `767 passed in 17.19s`, exit 0.

### Pinned limitations are not misreported as passing safety assertions

The round-2 no-nearby-currency probes also verify the neighbour on the pin. They
cannot be retained as passing `mismatch` assertions while restoring the exact
pinned behavior. A diagnostic census ran before the rollback against both the
review head and the pin:

| Probe | Review head | Pin |
|---|---|---|
| No currency after Scale | verified neighbour | verified neighbour |
| Scale followed by `20%` | verified neighbour | verified neighbour |
| Scale followed by percentage wording | verified neighbour | verified neighbour |
| Scale followed by `100` | verified neighbour | verified neighbour |
| Scale followed by `1,000 users` | verified neighbour | verified neighbour |
| `Scale 20%` heading | verified neighbour | verified neighbour |
| Currency on the fifth following line | verified neighbour | verified neighbour |
| `Generate Spreadsheets` before Pro's own sentence | mismatch | mismatch |
| `Free` before Pro's own sentence | mismatch | mismatch |

The first seven remain known legacy limitations for a DOM-based follow-up. No
passing test claims that those cases are safe. The pinned behavior is restored,
not presented as a general solution to card ownership.

## Offline replay

The saved input set, data export `4d4f709621486e791107830680e7d2293ea450a7`, fixed
2026-10-14 date, and replay tool are unchanged. The tool blocks socket connects,
reads the supplied pages, and writes only this worktree's replay output.

| Readers | unchanged | changed | needs_review | unreadable | unreachable | not_reread |
|---|---:|---:|---:|---:|---:|---:|
| Pinned readers before the MiniMax fix | 335 | 0 | 13 | 120 | 43 | 44 |
| Reviewed R2 head | 339 | 0 | 13 | 116 | 43 | 44 |
| Final MiniMax-only production change | 338 | 0 | 13 | 117 | 43 | 44 |

Replay exit code: 0. Compared with R2, exactly one fact changes its status, value,
or reason: `mistral/subscription/pro#offering.subscription.programmatic_or_agent_use`
goes from unchanged to unreadable, with the expected sentence found as `None`.
All copy references are identical. The three MiniMax allowances remain verified.
The PR table and description are updated to this final scope.

The ≤15 target remains blocked by the existing citation, absent-value, and reader
coverage issues recorded in the main evidence note. Mistral now contributes one
additional unreadable fact. The rollback does not change the other 116 actions.

## Checks and commands

Tools remain Python 3.14.4, pytest 9.1.1, pytest-xdist 3.8.0, Ruff 0.16.6,
Node 22.22.3, Git 2.50.1, and GitHub CLI 2.102.0. The dependency and bundle files
`web/node_modules/@playwright/test/package.json` and `web/dist/decide.html` are
present in this executor worktree. The reviewer reported missing dependencies
in its separate worktree; no tests were weakened to accommodate that environment.

Commands run from the assigned worktree unless noted. Exit codes are read from
command completion. Logs are under `.artifacts/model-235-readers-r3/executor`.

```bash
# Whole production diff relative to the pin:
git diff ee16bf40 -- decision/verify.py

# Pinned Mistral safety, exit 0. Working directory: the pin export.
PYTHONPATH=/Users/terbeest/dev/worktrees/model-235-readers/.artifacts/model-235-readers/executor/pin /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest --import-mode=importlib -q /Users/terbeest/dev/worktrees/model-235-readers/tests/test_model_235_readers.py -k mistral

# All cases on the pin: exit 1, only the three MiniMax positives fail.
PYTHONPATH=/Users/terbeest/dev/worktrees/model-235-readers/.artifacts/model-235-readers/executor/pin /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest --import-mode=importlib -q /Users/terbeest/dev/worktrees/model-235-readers/tests/test_model_235_readers.py

# Focused current-reader checks, exit 0:
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_model_235_readers.py tests/test_price_reread.py tests/test_price_reread_fallback.py tests/test_decision_verify.py tests/test_decision_sources.py tests/test_model380_subscription_quotes.py tests/test_model380_subscription_types.py

# Full suite:
TZ=UTC PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4 --dist loadfile

# Offline replay, exit 0:
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python docs/evidence/g2-ios/MODEL-235-readers-replay.py --data-root .artifacts/model-235-readers/executor/data-main --copies /private/tmp/claude-501/-Users-terbeest-dev-modelspec/6b307b20-b183-41a5-91e6-14f65d035cbc/scratchpad/rr-38572656013/price-reread-copies --rendered /private/tmp/claude-501/-Users-terbeest-dev-modelspec/6b307b20-b183-41a5-91e6-14f65d035cbc/scratchpad/rr-38572656013/price-reread-rendered --out .artifacts/model-235-readers-r3/executor/replay

/Users/terbeest/dev/modelspec/.venv/bin/python -m ruff check tests/test_model_235_readers.py
git diff --check

# Delivery after checks:
CI_LOCAL_SKIP=1 git push -u origin model-235-readers
gh pr edit 751 --title 'price re-read: read MiniMax allowances (MODEL-235)' --body-file .artifacts/model-235-readers-r3/executor/pr-body.md
gh pr view model-235-readers --json number,url,isDraft,headRefName,headRefOid,baseRefName
```

Full-suite result: `11060 passed, 9 skipped, 11 warnings in 1289.30s (0:21:29)`, exit 0.

No live provider fetch, paid API, Firecrawl, workflow dispatch, Linear write,
production switch, PR ready transition, or merge ran. The PR remains a draft.
