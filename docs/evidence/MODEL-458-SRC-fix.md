# MODEL-458-SRC execution evidence

Base: `5dd0eb5a16637d254c23f2903a5b97fb134ef9c3`, confirmed against freshly fetched `origin/main`.
The final revision is the head of `model-458-src`; resolve it with `git rev-parse HEAD` after checkout. The executor's final receipt records its full SHA.

Environment: Python 3.14.4, pytest 9.1.1, HTTPX 0.28.1, git 2.50.1, GitHub CLI 2.103.3. Python changes retain 3.11 syntax compatibility.

## AUD-06-F1

Workflow source admission is enforced at HTTP request, redirect, cache and curation boundaries. Refused sources produce explicit failure results without new source content or classifications. The shared HTTP transport preserves HTTPX redirect credential handling. Existing retention classifications remain in force.

Permanent checks are in `tests/test_source_transports.py`:

- `test_shared_transport_enforces_source_admission`
- `test_curation_enforces_source_admission`
- `test_benchmark_transport_enforces_source_admission`
- `test_release_transport_enforces_source_admission`
- `test_paid_endpoint_enforces_source_admission`
- `test_usage_endpoint_enforces_source_admission`
- `test_allowed_redirects_preserve_response_and_origins`
- `test_source_redirect_preserves_httpx_credential_handling`

The initial focused red run reported `24 failed, 2 passed`, exit 1. Additional endpoint coverage reported `2 failed, 1 passed, 26 deselected`, exit 1. Metadata admission coverage reported `4 failed, 32 deselected`, exit 1. Detailed red output was held only in local scratch. The source, curation and retention checks then reported `128 passed, 3 deselected`, exit 0; the deselected cases belong to AUD-06-F2 and are included in its verification below.

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_source_transports.py
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_source_transports.py tests/test_curation_cite_only.py tests/test_curation_loop.py -k 'not (firecrawl_local_cap or firecrawl_cached_reads)'
```

No live provider request, private repository change, retained-private-data cleanup, deployment, production switch change or source-terms change was performed. Offline fixtures exercise engine-visible transport behavior. Provider-internal processing was not observed.

## AUD-06-F2

`CreditGuard` now reserves the request's worst-case cost before every POST attempt. The local reservation only increases. Provider balance deltas remain separate measurement fields. Cache hits require no reservation. Bounded PDF requests and permitted expensive formats share the same allowance check; unbounded cost is refused under a finite budget.

The offline reproduction returned `cap=2, posts=5, successful_reads=5, reported_spent=0, stopped=false`. The regression selection reported `11 failed, 72 deselected`, exit 1, before implementation. Its tests exercise actual scrape requests with fake responses and cover constant or replenished balances, retry, timeout, unavailable usage, cache reuse, expensive formats and curation stop behavior.

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_fetch.py tests/test_curation_loop.py -k 'local_allowance or reserves_each_retry or timeout_keeps or unavailable_usage or cache_hit_preserves or refuses_unbounded_cost or reserves_expensive or local_cap_stops or cached_reads_do_not_consume'
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_source_transports.py tests/test_fetch.py tests/test_curation_loop.py tests/test_curation_cite_only.py
```

The combined F1/F2 focused run reported `166 passed`, exit 0. The existing unbounded-request test now asserts refusal before a POST. The shrinking-page-cap fixture explicitly reserves seven credits first, then checks a remaining cap of three; its earlier first cap of ten was incompatible with a total reservation limit of ten. No configured cap increased.

Unknown outcomes keep their full reservation. This can reduce completed work relative to measured provider usage. No live provider consumption was measured.

## Broader source verification

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_source_transports.py tests/test_decision_sources.py tests/test_fetch.py tests/test_curation_cite_only.py tests/test_curation_loop.py tests/test_offering_fetch.py tests/test_release_signal_prices.py tests/test_removed_sources.py
```

Result: `329 passed, 2 skipped`, exit 0. This includes source exclusion, HTTP redirect behavior, existing curation retention, offering fetch and release-price coverage. No local full suite or site build was run. The changed files do not intersect the Worker's vendored source list, and neither exports nor the Worker runtime import graph changed.

## AUD-06-F3

`TypeSafeJudge` and `Attributor` share the stricter configured allowance. Every attempted request reserves 65,536 input tokens before transport, including each retry. Reservations are never refunded; reported consumption remains separate. The pinned model documents a 64k per-request context covering state and all questions. Requests remove the optional long-context header, disable redirects and client authentication retries, and refuse configurations without the verified bound. [TypeSafe model limits](https://docs.typesafe.ai/models), [request header and usage definitions](https://docs.typesafe.ai/api/system-one)

The configured limit remains 2,000,000 tokens. This permits at most 30 attempted requests per run, including retries. Cached and deterministic decisions remain free. This intentionally favors the documented maximum over an unverified token estimate.

The supplied offline reproduction used an allowance of one. Before implementation, the successful fixture sent one request and reported 800 tokens; the timeout fixture sent nine requests and reported zero. After implementation, both sent zero requests, and the successful fixture returned `unavailable`. Both reproduction invocations exited 0.

The permanent `input_allowance` tests reported `18 failed, 55 deselected`, exit 1, before implementation. Follow-up response and request-shape checks reported `5 failed, 17 passed, 55 deselected`, exit 1, before correction. The final tests cover low allowance, mismatched caps, Unicode, unknown configurations, request headers, redirects, authentication retries, timeouts, retryable responses, malformed replies, invalid or absent usage, cached decisions and deterministic decisions.

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_attribution.py -k input_allowance
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_attribution.py tests/test_seed_models_dev.py tests/test_research_failure_safety.py
```

Final focused result: `140 passed`, exit 0. No live token usage, provider billing, production job execution or provider acceptance was observed. Only offline HTTP fixtures exercised the transport. The supplier policy, model selection, thresholds and configured limits are unchanged.

## Final checks

The two final focused suite invocations total `469 passed, 2 skipped`. All changed Python files parse with Python 3.11 grammar under Python 3.14.4; a Python 3.11 runtime was not used locally. `git diff --check` passed. No frozen data, source-retention class, legal text, API contract, Worker variable or release tag changed. `release_signals/pipeline.py` remains unchanged.

The private workflow pin update is separate work after engine review and merge. Full CI and independent review remain pending on the draft PR.
