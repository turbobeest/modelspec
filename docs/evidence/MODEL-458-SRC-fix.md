# MODEL-458-SRC execution evidence

Base: `5dd0eb5a16637d254c23f2903a5b97fb134ef9c3`, confirmed against freshly fetched `origin/main`.
The final revision is the head of `model-458-src`; resolve it with `git rev-parse HEAD` after checkout. The executor's final receipt records its full SHA.

Environment: Python 3.14.4, pytest 9.1.1, HTTPX 0.28.1, git 2.50.1. Python changes retain 3.11 syntax compatibility.

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
