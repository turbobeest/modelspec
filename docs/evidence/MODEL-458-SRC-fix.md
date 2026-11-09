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
