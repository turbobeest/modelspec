# MODEL-373 fix evidence

The monthly grant path no longer carries the unused optional flag. A new invoice still resets period overage usage, and a replay returns before changing the allowance or overage usage. The billing-disabled form test compares status, body bytes, and every header except per-request Server-Timing. It explicitly runs with cold and warm initial isolate states.

Worktree: `/Users/terbeest/dev/worktrees/model-373`.
Branch: `sparksandsawdust/model-373-cleanup-after-690`.
Base SHA: `50589d56a84d9f7ea99bb3ff2518faa9fd35bcd5`.
Final tested implementation SHA: `ddd3491d583e94d8524850ed58dab61982afe792`.

The final delivery commit adds only this evidence report to the tested implementation. Resolve its SHA with `git log -1 --format=%H -- docs/evidence/g2-ios/MODEL-373-fix.md`. The PR body and executor completion line also record that SHA. A report committed to Git cannot contain its own commit hash.

All commands below ran from the worktree above. The tool returned each pytest process's exit code directly; no test command used a pipe. Captured output below has trailing whitespace removed.

Tools: Python 3.14.4, pytest 9.1.1, pytest-xdist 3.8.0, Git 2.50.1, GitHub CLI 2.102.0, Node v22.22.3. The host reported macOS 27.2, arm64. Versions came from:

```bash
/Users/terbeest/dev/modelspec/.venv/bin/python - <<'PY'
import platform
import sys
from importlib.metadata import version
print('Python:', sys.version)
print('pytest:', version('pytest'))
print('pytest-xdist:', version('pytest-xdist'))
print('Platform:', platform.platform())
PY
git --version
gh --version
/Users/terbeest/.nvm/versions/node/v22.22.3/bin/node --version
```

The unchanged billing test failed on the base code when run alone.

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_billing.py::test_a_form_post_when_billing_is_off_is_refused_the_same_way_as_json
```

Exit code: `1`. Output:

```text
F                                                                        [100%]
=================================== FAILURES ===================================
_____ test_a_form_post_when_billing_is_off_is_refused_the_same_way_as_json _____

entry = <module 'modelspec_worker_entry_billing' from '/Users/terbeest/dev/worktrees/model-373/api/worker/src/entry.py'>

    def test_a_form_post_when_billing_is_off_is_refused_the_same_way_as_json(entry):
        form, form_capture = _form_post(
            entry, f"price_id={PACK5}", env=_billing_env(_Bind(), flag="false"))
        capture: dict[str, str] = {}
        previous = _patch_entry_fetch(entry, capture)
        try:
            worker = entry.Default()
            worker.env = _billing_env(_Bind(), flag="false")
            as_json = run(worker.fetch(_Req(
                "/v1/billing/checkout", body=json.dumps({"price_id": PACK5}),
                headers={"content-type": "application/json"})))
        finally:
            entry.fetch = previous
        assert form.status == as_json.status == 503
        assert form.json()["error"]["code"] == "billing_not_enabled"
        assert form.body == as_json.body
>       assert form.headers == as_json.headers
E       assert {'content-typ...ibedby"', ...} == {'content-typ...ibedby"', ...}
E
E         Omitting 6 identical items, use -vv to show
E         Differing items:
E         {'Server-Timing': 'isolate;desc="cold", startup;desc="runtime restore unobservable from Python"'} != {'Server-Timing': 'isolate;desc="warm"'}
E         Use -v to get more diff

tests/test_billing.py:1475: AssertionError
=========================== short test summary info ============================
FAILED tests/test_billing.py::test_a_form_post_when_billing_is_off_is_refused_the_same_way_as_json
1 failed in 0.57s
```

Before changing production code, I added `test_a_paid_invoice_grants_monthly_through_an_invoice_only_ledger`, which delivers a signed invoice fixture through a ledger with the reduced monthly method signature and asserts the resulting balance and paid access. I also parameterized the existing form comparison test with explicit cold and warm initial states.

The monthly-grant regression failed because `grant_monthly` forwarded the obsolete sixth ledger argument. The cold form comparison failed because sequential requests correctly had different isolate timing headers. The warm comparison passed.

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_billing.py::test_a_paid_invoice_grants_monthly_through_an_invoice_only_ledger tests/test_billing.py::test_a_form_post_when_billing_is_off_is_refused_the_same_way_as_json
```

Red exit code: `1`. Output against unchanged production code:

```text
FF.                                                                      [100%]
=================================== FAILURES ===================================
______ test_a_paid_invoice_grants_monthly_through_an_invoice_only_ledger _______

policy = AccessPolicy(version='access-v1', timezone='UTC', sandbox_prefix='test_', sandbox_tier='sandbox', live_prefix='live_',...ds=ReadsConfig(reads_per_credit=10, daily_cap=1000, burst_limit=30)), x402=X402ListPrice(list_usd_per_decision='0.02'))

    def test_a_paid_invoice_grants_monthly_through_an_invoice_only_ledger(policy):
        class InvoiceLedger(credits.MemoryLedger):
            async def set_monthly(self, holder, units, invoice_id, plan="", customer_id=""):
                return await super().set_monthly(holder, units, invoice_id, plan, customer_id)

        kv = MemoryKV()
        ledger = InvoiceLedger()
        key = _issue(kv, policy, tier="free")
        obj = invoice_obj(parent={"subscription_details": {
            "subscription": SUB,
            "metadata": {"modelspec_key_fingerprint": keys.fingerprint(key)},
        }})
>       outcome = run(apply(kv, policy, payload("invoice.paid", obj, "evt_invoice_only"),
                            ledger=ledger))

tests/test_billing.py:1195:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
tests/test_billing.py:50: in run
    return asyncio.run(coro)
           ^^^^^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.14/3.14.4_1/Frameworks/Python.framework/Versions/3.14/lib/python3.14/asyncio/runners.py:204: in run
    return runner.run(main)
           ^^^^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.14/3.14.4_1/Frameworks/Python.framework/Versions/3.14/lib/python3.14/asyncio/runners.py:127: in run
    return self._loop.run_until_complete(task)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.14/3.14.4_1/Frameworks/Python.framework/Versions/3.14/lib/python3.14/asyncio/base_events.py:719: in run_until_complete
    return future.result()
           ^^^^^^^^^^^^^^^
tests/test_billing.py:112: in apply
    return await billing.webhook(
api/worker/src/billing.py:614: in webhook
    return await apply_event(event, kv=kv, policy=policy, now=now,
api/worker/src/billing.py:414: in apply_event
    action, error = await _apply_invoice_paid(
api/worker/src/billing.py:564: in _apply_invoice_paid
    grant = await store.grant_monthly(
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

kv = <access_kv.MemoryKV object at 0x1081b8980>
subscription_id = 'sub_test_fixture'
ledger = <tests.test_billing.test_a_paid_invoice_grants_monthly_through_an_invoice_only_ledger.<locals>.InvoiceLedger object at 0x1081b8ad0>
units = 4000, invoice_id = 'in_test_1', plan = 'Solo', reset_overage = True

    async def grant_monthly(kv: Any, subscription_id: str, *, ledger: Any,
                            units: int, invoice_id: str, plan: str,
                            reset_overage: bool = True) -> str:
        """SET monthly on the claimed key, or remember it for claim. Packs untouched.

        `reset_overage` is false for a subscription update, which refills the
        allowance and leaves the overage cap. A paid invoice keeps the default.
        """
        stored = await load_subscription(kv, subscription_id)
        if stored is None:
            return "no_key"
        if stored.key_fingerprint and ledger is not None:
            try:
>               result = await ledger.set_monthly(
                    credits.holder_from_fingerprint(stored.key_fingerprint),
                    units, invoice_id, plan, stored.customer_id, reset_overage)
E                   TypeError: test_a_paid_invoice_grants_monthly_through_an_invoice_only_ledger.<locals>.InvoiceLedger.set_monthly() takes from 4 to 6 positional arguments but 7 were given

api/worker/src/access_billing.py:701: TypeError
__ test_a_form_post_when_billing_is_off_is_refused_the_same_way_as_json[cold] __

entry = <module 'modelspec_worker_entry_billing' from '/Users/terbeest/dev/worktrees/model-373/api/worker/src/entry.py'>
monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x107b27e10>
isolate_served = False

    @pytest.mark.parametrize("isolate_served", [False, True], ids=["cold", "warm"])
    def test_a_form_post_when_billing_is_off_is_refused_the_same_way_as_json(
            entry, monkeypatch, isolate_served):
        monkeypatch.setattr(entry, "_isolate_served", isolate_served)
        form, form_capture = _form_post(
            entry, f"price_id={PACK5}", env=_billing_env(_Bind(), flag="false"))
        capture: dict[str, str] = {}
        previous = _patch_entry_fetch(entry, capture)
        try:
            worker = entry.Default()
            worker.env = _billing_env(_Bind(), flag="false")
            as_json = run(worker.fetch(_Req(
                "/v1/billing/checkout", body=json.dumps({"price_id": PACK5}),
                headers={"content-type": "application/json"})))
        finally:
            entry.fetch = previous
        assert form.status == as_json.status == 503
        assert form.json()["error"]["code"] == "billing_not_enabled"
        assert form.body == as_json.body
>       assert form.headers == as_json.headers
E       assert {'content-typ...ibedby"', ...} == {'content-typ...ibedby"', ...}
E
E         Omitting 6 identical items, use -vv to show
E         Differing items:
E         {'Server-Timing': 'isolate;desc="cold", startup;desc="runtime restore unobservable from Python"'} != {'Server-Timing': 'isolate;desc="warm"'}
E         Use -v to get more diff

tests/test_billing.py:1497: AssertionError
=========================== short test summary info ============================
FAILED tests/test_billing.py::test_a_paid_invoice_grants_monthly_through_an_invoice_only_ledger
FAILED tests/test_billing.py::test_a_form_post_when_billing_is_off_is_refused_the_same_way_as_json[cold]
2 failed, 1 passed in 0.56s
```

After the fix, the same command returned exit code `0`:

```text
...                                                                      [100%]
3 passed in 0.49s
```

The required standalone test command above returned exit code `0` after the fix. Its two cases cover both initial isolate states:

```text
..                                                                       [100%]
2 passed in 0.52s
```

The focused suites include the existing overage reset, invoice replay, subscription update, memory ledger, and Durable Object storage checks.

```bash
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_billing.py tests/test_credits.py tests/test_credits_do.py tests/test_meter_id.py tests/test_pricing_v2.py
```

Exit code: `0`. Output:

```text
........................................................................ [ 39%]
........................................................................ [ 79%]
.....................................                                    [100%]
181 passed in 1.42s
```

The required full suite used four workers and the specified Node path:

```bash
export PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4
```

The first full run used the host's local timezone and returned exit code `1`:

```text
=================================== FAILURES ===================================
_____________________ test_built_tree_passes_surface_lint ______________________
[gw0] darwin -- Python 3.14.4 /Users/terbeest/dev/modelspec/.venv/bin/python

dist = PosixPath('/private/var/folders/r6/p2knzk9x65d45dhc3x6zlyqc0000gn/T/pytest-of-terbeest/pytest-8/popen-gw0/dist0')

    def test_built_tree_passes_surface_lint(dist: Path) -> None:
        from pipeline import surface_lint

>       assert surface_lint.main(["--tree", str(dist / "modelspec")]) == 0
E       AssertionError: assert 1 == 0
E        +  where 1 = <function main at 0x11744c880>(['--tree', '/private/var/folders/r6/p2knzk9x65d45dhc3x6zlyqc0000gn/T/pytest-of-terbeest/pytest-8/popen-gw0/dist0/modelspec'])
E        +    where <function main at 0x11744c880> = <module 'pipeline.surface_lint' from '/Users/terbeest/dev/worktrees/model-373/pipeline/surface_lint.py'>.main

tests/test_agent_ready.py:259: AssertionError
----------------------------- Captured stdout call -----------------------------
/ | freshness.source | 2026-10-10 | expected: 2026-10-11
/models/ | freshness.source | 2026-10-10 | expected: 2026-10-11
/providers/ | freshness.source | 2026-10-10 | expected: 2026-10-11
/m/01-ai/yi-1-5-34b-32k/ | freshness.source | 2026-10-10 | expected: 2026-10-11
/m/01-ai/yi-1-5-34b-chat-16k/ | freshness.source | 2026-10-10 | expected: 2026-10-11
/m/01-ai/yi-1-5-34b-chat/ | freshness.source | 2026-10-10 | expected: 2026-10-11
/m/01-ai/yi-1-5-34b/ | freshness.source | 2026-10-10 | expected: 2026-10-11
/m/01-ai/yi-1-5-6b-chat/ | freshness.source | 2026-10-10 | expected: 2026-10-11
/m/01-ai/yi-1-5-6b/ | freshness.source | 2026-10-10 | expected: 2026-10-11
/m/01-ai/yi-1-5-9b-32k/ | freshness.source | 2026-10-10 | expected: 2026-10-11
/m/01-ai/yi-1-5-9b-chat-16k/ | freshness.source | 2026-10-10 | expected: 2026-10-11
/m/01-ai/yi-1-5-9b-chat/ | freshness.source | 2026-10-10 | expected: 2026-10-11
/m/01-ai/yi-1-5-9b/ | freshness.source | 2026-10-10 | expected: 2026-10-11
/m/01-ai/yi-34b-200k/ | freshness.source | 2026-10-10 | expected: 2026-10-11
[Repeated freshness findings omitted. The linter reported 2618 findings across 5237 files.]
1 failed, 9638 passed, 22 skipped, 11 warnings in 1211.28s (0:20:11)
```

The failed test is `tests/test_agent_ready.py::test_built_tree_passes_surface_lint`. The sitemap builder uses local `date.today()`, while build metadata and the linter's expected last-modified dates use the UTC build timestamp. The host's local date was `2026-10-10` and its UTC date was `2026-10-11`.

These files are identical to the base, verified by the empty output of:

```bash
git diff 50589d56a84d9f7ea99bb3ff2518faa9fd35bcd5 HEAD -- tests/test_agent_ready.py pipeline/build.py pipeline/surface_lint.py
```

I also reproduced the failure with all four changed files temporarily restored to their base contents, then restored the implementation bytes in a `finally` block. HEAD remained on the assigned branch. This exact command ran the baseline test and propagated its pytest exit code directly. It prints representative diagnostics rather than all repeated freshness findings:

```bash
/Users/terbeest/dev/modelspec/.venv/bin/python - <<'PY'
import os
import subprocess
import sys
from pathlib import Path

base = '50589d56a84d9f7ea99bb3ff2518faa9fd35bcd5'
paths = [Path(path) for path in (
    'api/worker/src/access_billing.py',
    'api/worker/src/credits.py',
    'api/worker/src/credits_do.py',
    'tests/test_billing.py',
)]
saved = {path: path.read_bytes() for path in paths}
try:
    for path in paths:
        path.write_bytes(subprocess.run(
            ['git', 'show', f'{base}:{path}'],
            check=True, capture_output=True).stdout)
    env = os.environ.copy()
    env['PYTHONPATH'] = str(Path.cwd())
    env['PATH'] = '/Users/terbeest/.nvm/versions/node/v22.22.3/bin:' + env['PATH']
    args = [sys.executable, '-m', 'pytest', '-q',
            'tests/test_agent_ready.py::test_built_tree_passes_surface_lint']
    result = subprocess.run(args, env=env, capture_output=True, text=True)
finally:
    for path, content in saved.items():
        path.write_bytes(content)
lines = (result.stdout + result.stderr).splitlines()
print('\n'.join(lines[:35]))
if len(lines) > 60:
    print(f'... omitted {len(lines) - 60} repeated diagnostic lines ...')
print('\n'.join(lines[-25:]))
print('BASELINE_PYTEST_EXIT_CODE', result.returncode)
sys.exit(result.returncode)
PY
```

Baseline exit code: `1`. The output ended with:

```text
/brand/ | freshness.source | 2026-10-10 | expected: 2026-10-11
/private/var/folders/r6/p2knzk9x65d45dhc3x6zlyqc0000gn/T/pytest-of-terbeest/pytest-20/dist0/modelspec: 2618 findings; 5237 files checked
=========================== short test summary info ============================
FAILED tests/test_agent_ready.py::test_built_tree_passes_surface_lint - Asser...
1 failed in 83.98s (0:01:23)
BASELINE_PYTEST_EXIT_CODE 1
```

After restoration, `git diff --exit-code` returned `0`. With the implementation restored, the same test passed when the test process used UTC:

```bash
export PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH
TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_agent_ready.py::test_built_tree_passes_surface_lint
```

Exit code: `0`. Output:

```text
.                                                                        [100%]
1 passed in 192.37s (0:03:12)
```

The full suite was rerun with the process timezone aligned to UTC. This changes the test process environment and does not change the source or test assertions:

```bash
export PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:$PATH
export TZ=UTC
PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n 4
```

UTC full-suite exit code: `0`. Final summary:

```text
9639 passed, 22 skipped, 11 warnings in 1065.78s (0:17:45)
```


The initial parameter search found references only in `api/worker/src/access_billing.py`, `api/worker/src/credits.py`, and `api/worker/src/credits_do.py`. After the code change and before writing this report:

```bash
grep -rn reset_overage .
```

The search printed nothing and returned exit code `1`, meaning no matches. This report quotes the removed name and red output; those are evidence, not remaining code references.

The final scan of code and tests returned exit code `1` and printed nothing:

```bash
grep -rn reset_overage api/worker/src tests
```

The source changes and whitespace can be checked with:

```bash
git diff 50589d56a84d9f7ea99bb3ff2518faa9fd35bcd5 ddd3491d583e94d8524850ed58dab61982afe792 -- api/worker/src/access_billing.py api/worker/src/credits.py api/worker/src/credits_do.py tests/test_billing.py
git diff --check 50589d56a84d9f7ea99bb3ff2518faa9fd35bcd5 HEAD
```

Delivery commands:

```bash
git add api/worker/src/access_billing.py api/worker/src/credits.py api/worker/src/credits_do.py tests/test_billing.py
git commit -m 'MODEL-373: remove unused monthly grant flag and stabilize billing test

Co-Authored-By: ChatGPT Codex <noreply@openai.com>'
git add docs/evidence/g2-ios/MODEL-373-fix.md
git commit -m 'MODEL-373: record red-first and full-suite verification

Co-Authored-By: ChatGPT Codex <noreply@openai.com>'
CI_LOCAL_SKIP=1 git push -u origin sparksandsawdust/model-373-cleanup-after-690
gh pr create --draft --base main --title "MODEL-373: remove reset_overage; make the billing form test order-independent" --body-file docs/evidence/g2-ios/.model-373-executor/pr-body.md
```

The PR body ends with `Executed by ChatGPT Codex (GPT-6.1 Sol); cross-model review by Claude Haiku pending.`.

I observed local CPython tests using fixtures and stubs, including built-site fixtures. I did not observe live Stripe or paid-provider responses, the deployed Worker or Pyodide runtime, the orchestrator's gate, GitHub CI completion, or an independent review. I did not separately invoke the Build both sites workflow or the web npm suite. No deployment, production switch, price, plan grant, Stripe configuration, or frozen data changed.
