# MODEL-391-ttl execution evidence

Worktree: `/Users/terbeest/dev/worktrees/model-391`.
Branch: `sparksandsawdust/model-391-sale-alerts`.
Base SHA: `883b637a0b3b9b7ca834b0f37ce2c46d8e618ed2`.
This file is in the same commit as the change. That commit's SHA is `git rev-parse HEAD` on this branch.

## Change

The sale notice auto-deletes after 5 seconds. `_TTL_DEFAULT` is 5 and `_TTL_MIN` is 1. `_TTL_MAX` stays 86400. Production and staging `SALE_ALERT_TTL_SECONDS` are `"5"`. A configured `0` clamps to 1. An absent, blank, or non-numeric value uses 5. No sale history is kept beyond the dedupe marker. `scripts/sale_alert_test.py` uses the same default and floor so a manual probe does not stay up for 15 minutes.

## Red

Command:

`TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q tests/test_sale_alerts.py::test_ttl_clamps tests/test_sale_alerts.py::test_sale_alerts_ship_off tests/test_x402.py::test_staging_x402_config_is_isolated_on_base_sepolia --tb=line -p no:cacheprovider`

Pytest 9.1.1, Python 3.14.4. Exit 1. 8 failed, 2 passed in 0.13s.

- `test_ttl_clamps[None-5]`, `[-5]`, `[nope-5]`: payload `ttl` was `900`, expected `5`.
- `test_ttl_clamps[5-5]`: payload `ttl` was `60`, expected `5`.
- `test_ttl_clamps[0-1]` and `[1-1]`: payload `ttl` was `60`, expected `1`.
- `test_sale_alerts_ship_off`: production `SALE_ALERT_TTL_SECONDS` was `900`, expected `5`.
- `test_staging_x402_config_is_isolated_on_base_sepolia`: staging `SALE_ALERT_TTL_SECONDS` was `900`, expected `5`.

After the constants changed, two payload assertions and the bundle hash were still red. Exit 1. 3 failed, 129 passed.

- `test_a_stripe_pack_sale_pushes_once_with_ttl_900`: payload `ttl` was `5`, expected `900`.
- `test_x402_settle_pushes_once_and_a_replay_does_not`: payload `ttl` was `5`, expected `900`.
- `test_the_cli_bundle_and_schemas_are_generated_from_the_published_sources`: `api/worker/wrangler.jsonc` hash was `5f5e60203de2325623581822f9cb273ecb0433eb11bea5c5ccce3cd6de46161a`, bundle still had `6c1aea42f830054994ed4fdc6d068f5292ac81d82f5b754040e70889fbd5f0bc`.

## Green

Same interpreter. Focused command added the renamed payload tests, `tests/test_sale_alerts.py`, `tests/test_x402.py`, the bundle-hash test, `tests/test_cli_wheel.py`, and `tests/test_pypi_packaging.py`. Exit 0. 139 passed in 2.30s.

`web/` had no `node_modules`. Node v22.22.3, npm 10.9.8: `npm ci` in `web/`, then `npm run build` (exit 0). `web/dist/decide.html` exists after that build.

Full suite before the build, `CI=true`:

`TZ=UTC PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -n auto --dist loadfile -p no:cacheprovider`

Exit 1. 10749 passed, 9 skipped, 12 errors in 695.66s. Every error was `FileNotFoundError` for `web/dist/decide.html` in `test_landing_behaviour_in_browser`.

Landing browser file after the build: 12 passed, exit 0.

Full suite after the build, same command: exit 0. 10761 passed, 9 skipped, 11 warnings in 748.57s.

## Not observed

No Pushover request. `scripts/sale_alert_test.py` was not run. The Worker was not deployed. `SALE_ALERTS_ENABLED` is still `"0"`. Linear was not edited. The PR was not merged. `web/node_modules` and `web/dist` are local and uncommitted.
