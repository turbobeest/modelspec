# MODEL-458-SITE verification

Base SHA: `5dd0eb5a16637d254c23f2903a5b97fb134ef9c3`.
Verified implementation SHA: `4b9f9ea26cdf1b88043d03d43aeac9e95f64617e`. The final commit only adds this verification record; its full SHA is reported in the executor completion line and can be read with `git rev-parse HEAD`. A commit cannot embed its own SHA in a tracked file.

Environment: Python 3.14.4, pytest 9.1.1, git 2.50.1, gh 2.103.3, Node v22.22.3 at `/Users/terbeest/.nvm/versions/node/v22.22.3/bin`. Tests run serially from the assigned worktree, with `PYTHONPATH=$PWD` and `SOCIAL_CARDS_RENDER=false`. No local full pytest suite is run.

## AUD-05-F3

Inline display exclusion and inherited visibility govern JSON-LD and presence checks. Visible descendants can override visibility; hidden display ancestors remain excluded. Red assertions reported `jsonld.visible` absent and hidden text present. Synthetic name, description, presence, sibling and override controls now pass.

```sh
env PYTHONPATH=$PWD SOCIAL_CARDS_RENDER=false /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider /tmp/MODEL-458-SITE-scratch/root/test_AUD_05_F3.py
```

f3-repro: exit 1; `2 failed in 0.39s`.

```sh
env PYTHONPATH=$PWD SOCIAL_CARDS_RENDER=false /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_surface_lint.py -k 'invisible_text or inline_visibility'
```

f3-red: exit 1; `17 failed, 10 passed, 174 deselected in 0.69s`.

```sh
env PYTHONPATH=$PWD SOCIAL_CARDS_RENDER=false /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_surface_lint.py -k inline_hidden_copy
```

f3-presence-red: exit 1; `2 failed, 201 deselected in 0.75s`.

```sh
env PYTHONPATH=$PWD SOCIAL_CARDS_RENDER=false /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_surface_lint.py /tmp/MODEL-458-SITE-scratch/root/test_AUD_05_F3.py
```

f3-green: exit 0; `205 passed in 3.22s`.

## AUD-05-F1

Method downloads and availability copy follow files in the output tree, including either-file and neither-file cases. Same-origin absolute hrefs are checked with root-relative links; other origins remain excluded. The red build probe listed two absent decision artifacts. A test setup initially passed a nonexistent dataclass field; it was corrected to the existing environment boundary before implementation.

```sh
env PYTHONPATH=$PWD SOCIAL_CARDS_RENDER=false /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider /tmp/MODEL-458-SITE-scratch/root/test_AUD_05_F1.py
```

f1-repro: exit 1; `1 failed in 0.02s`.

```sh
env PYTHONPATH=$PWD SOCIAL_CARDS_RENDER=false /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_method.py tests/test_pipeline.py -k 'method_downloads or method_private or same_origin_missing or absolute_existing'
```

f1-red-corrected: exit 1; `7 failed, 3 passed, 78 deselected in 0.90s`.

```sh
env PYTHONPATH=$PWD SOCIAL_CARDS_RENDER=false /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_method.py tests/test_pipeline.py -k 'not test_build_'
```

f1-green: exit 0; `88 passed in 27.28s`.

## AUD-05-F2

Benchmark fact Markdown uses the existing HTML-body destination policy. Sibling and repository paths are normalized, disallowed destinations become plain labels, and escaped examples and code spans retain their text. The red reproduction emitted `beir.md`; the expected published destination is `/b/beir/`. A permanent output-tree test checks every benchmark twin.

```sh
env PYTHONPATH=$PWD SOCIAL_CARDS_RENDER=false /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider /tmp/MODEL-458-SITE-scratch/root/test_AUD_05_F2.py
```

f2-repro: exit 1; `1 failed in 0.16s`.

```sh
env PYTHONPATH=$PWD SOCIAL_CARDS_RENDER=false /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_agent_ready.py -k benchmark_markdown_fact_destinations
```

f2-red: exit 1; `7 failed, 4 passed, 34 deselected in 0.45s`.

```sh
env PYTHONPATH=$PWD SOCIAL_CARDS_RENDER=false /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_benchmark_body_render.py tests/test_agent_ready.py /tmp/MODEL-458-SITE-scratch/root/test_AUD_05_F2.py -k 'not built'
```

f2-green: exit 0; `44 passed, 15 deselected in 1.82s`.

## AUD-05-F4

The method page Open Graph URL matches its canonical `/method/` URL and retains the existing fallback image. The red assertion compared the homepage URL to the method URL.

```sh
env PYTHONPATH=$PWD SOCIAL_CARDS_RENDER=false /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider /tmp/MODEL-458-SITE-scratch/root/test_AUD_05_F4.py
```

f4-repro: exit 1; `1 failed in 0.02s`.

```sh
env PYTHONPATH=$PWD SOCIAL_CARDS_RENDER=false /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_method.py -k method_open_graph
```

f4-red: exit 1; `1 failed, 17 deselected in 0.84s`.

```sh
env PYTHONPATH=$PWD SOCIAL_CARDS_RENDER=false /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_method.py tests/test_brand.py
```

f4-green: exit 0; `27 passed in 1.54s`.

## AUD-05-F5

Generated product, template, comparison, use-case and guide pages receive page-specific Open Graph fields. Attribute escaping happens once. Existing static registrations and blog shell ownership remain compatible. Baseline output reported 132 incomplete pages, including 85 without any of the five fields. The first broad run found two old raw-attribute assertions; they now compare escaped/decoded content. Existing optional card-rendering behavior remains unchanged; only newly introduced image references use the locally available fallback.

```sh
env PYTHONPATH=$PWD SOCIAL_CARDS_RENDER=false /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider /tmp/MODEL-458-SITE-scratch/root/test_AUD_05_F5.py
```

f5-repro: exit 1; `1 failed in 0.17s`.

```sh
env PYTHONPATH=$PWD SOCIAL_CARDS_RENDER=false /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_brand.py tests/test_pipeline.py tests/test_social_cards.py -k 'escapes_complete or example_shell_has or template_card_and_page_preserve'
```

f5-red-corrected: exit 1; `5 failed, 107 deselected in 0.59s`.

```sh
env PYTHONPATH=$PWD SOCIAL_CARDS_RENDER=false /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_brand.py tests/test_method.py tests/test_about.py tests/test_pipeline.py tests/test_comparison_pages.py tests/test_guides.py tests/test_social_cards.py -k 'not renderer_writes and not chromium and not build_without and not build_with and not build_emits and not template_card_failures and not blog_fixture_is_readable'
```

Intermediate broad run, f5-green: exit 1; `2 failed, 151 passed, 9 deselected in 91.68s (0:01:31)`.

```sh
env PYTHONPATH=$PWD SOCIAL_CARDS_RENDER=false /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_social_cards.py tests/test_feedback_page.py tests/test_brand_page.py tests/test_pricing_page.py tests/test_landing.py tests/test_orchestrators.py -k 'not renderer_writes and not chromium and not build_without and not build_with and not build_emits and not template_card_failures and not blog_fixture_is_readable and not behaviour_in_browser and not recipe_is_discoverable'
```

f5-caller-green: exit 0; `91 passed, 22 deselected in 89.45s (0:01:29)`.

```sh
env PYTHONPATH=$PWD SOCIAL_CARDS_RENDER=false /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_brand.py tests/test_method.py tests/test_about.py tests/test_pipeline.py tests/test_social_cards.py -k 'escapes_complete or example_shell_has or template_card_and_page_preserve or registry_drives or landing_card_html or each_page_points'
```

f5-regressions-green: exit 0; `8 passed, 130 deselected in 0.98s`.

## AUD-05-F6

Provider sections use h2; ungrouped benchmark titles use h3 and grouped titles remain h4. Affected model pages extend existing strip styling to h3 without changing the no-evidence golden shell. Red assertions observed heading sequences `h1` followed by `h3`, and `h2` followed by `h4`. All instrument and model-guide tests, including the byte-identical golden fixture, pass.

```sh
env PYTHONPATH=$PWD SOCIAL_CARDS_RENDER=false /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider /tmp/MODEL-458-SITE-scratch/root/test_AUD_05_F6.py
```

f6-repro: exit 1; `1 failed in 0.03s`.

```sh
env PYTHONPATH=$PWD SOCIAL_CARDS_RENDER=false /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_pipeline.py -k 'heading_follows or model_strips_group_subsets'
```

f6-red-corrected: exit 1; `2 failed, 1 passed, 73 deselected in 0.39s`.

```sh
env PYTHONPATH=$PWD SOCIAL_CARDS_RENDER=false /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_pipeline.py tests/test_instrument_render.py tests/test_model_guide_render.py -k 'model_strip or model_page or heading_follows or test_card_without or guided_card or guide or hardware or lineage or capability or platform or competitor or quantisation or chain'
```

f6-green: exit 0; `22 passed, 97 deselected in 5.26s`.

```sh
env PYTHONPATH=$PWD SOCIAL_CARDS_RENDER=false /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_instrument_render.py tests/test_model_guide_render.py
```

f6-render-green: exit 0; `43 passed in 3.86s`.

## AUD-05-F7

Published corrections are validated before HTML or feeds are written. Dates cannot exceed the publication cutoff, and referenced revisions must be among those being published. The signed synthetic fixture rejected future, absent and unpublished revision cases; historical correction timestamps, links and append-only behavior remain valid. The original standalone probe exited 0 while printing ACCEPTED for invalid cases; the permanent red tests failed with DID NOT RAISE ValueError.

```sh
env PYTHONPATH=$PWD SOCIAL_CARDS_RENDER=false /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_blog.py -k 'invalid_corrections or corrections_update'
```

f7-red: exit 1; `3 failed, 1 passed, 19 deselected in 0.43s`.

```sh
env PYTHONPATH=$PWD SOCIAL_CARDS_RENDER=false /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_blog.py tests/test_blog_append_only.py -k 'not site_build_includes_fixture'
```

f7-green: exit 0; `54 passed, 1 deselected in 4.44s`.

Standalone reproduction:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python /tmp/MODEL-458-SITE-scratch/root/test_AUD_05_F7.py
```

Exit 0. Historical control: `feed.updated=2026-10-01T00:00:00Z`, target exists. Future case: `feed.updated=2999-01-01T00:00:00Z`. Missing revision case: `target_exists=False`, `revision_link_present=True`.

## AUD-09-F9

llms.txt describes the initial frozen image and the configured delayed-image policy, with data-image.json as provenance. It makes no measured age claim. The red regression found "about nine months old" despite the absence of a lag manifest. Existing lag, keyed access, snapshot and legal behavior checks remain green.

```sh
env PYTHONPATH=$PWD SOCIAL_CARDS_RENDER=false /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_llms_txt.py -k measured_nine_month
```

f9-red: exit 1; `1 failed, 5 deselected in 0.30s`.

```sh
env PYTHONPATH=$PWD SOCIAL_CARDS_RENDER=false /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_access_wiring.py::test_on_an_unkeyed_request_is_refused_and_told_how_to_get_a_key tests/test_agent_guide.py::test_generated_guide_and_constants_are_stable_and_within_budget tests/test_agent_guide.py::test_all_guide_specs_parse_against_the_registry tests/test_llms_txt.py
```

f9-green: exit 0; `10 passed in 1.61s`.

```sh
env PYTHONPATH=$PWD SOCIAL_CARDS_RENDER=false /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_data_lag.py::test_no_commit_old_enough_changes_nothing tests/test_data_lag.py::test_the_seed_publishes_on_the_ninth_month tests/test_decide_worker.py::test_a_requested_snapshot_must_be_the_loaded_snapshot tests/test_legal.py::test_the_commitment_rides_with_the_floors tests/test_legal.py::test_every_neutrality_assertion_is_false tests/test_legal.py::test_the_rule_and_the_pledge_appear_verbatim_in_the_commitment tests/test_legal.py::test_the_access_model_wording_is_in_the_terms_neutrality_and_licence tests/test_legal.py::test_the_privacy_statement_matches_what_the_worker_binds tests/test_legal.py::test_the_privacy_statement_discloses_cloudflare_observability tests/test_legal.py::test_the_terms_state_the_plans_and_packs_that_are_configured tests/test_legal.py::test_x402_privacy_moves_the_payment_disclosure_out_of_not_yet_live
```

f9-invariants-green: exit 0; `17 passed in 1.35s`.

Standalone reproduction:

```sh
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python /tmp/MODEL-458-SITE-scratch/root/f9-repro.py
```

Exit 0. No lag manifest; cutoff `2026-02-09`; 221 public cards were released after that cutoff, with latest public release date `2026-09-28`. The generated sentence claimed a measured age of about nine months.

## Review regression checks

Read-only review identified equivalent-origin URL forms and an exact-backtick-run Markdown case. Both gained failing regressions, were corrected, and were folded into their original finding commits.

```sh
env PYTHONPATH=$PWD SOCIAL_CARDS_RENDER=false /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_pipeline.py -k 'same_origin_missing or absolute_existing'
```

f1-origin-red: exit 1; `2 failed, 5 passed, 71 deselected in 0.43s`.

```sh
env PYTHONPATH=$PWD SOCIAL_CARDS_RENDER=false /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_pipeline.py -k href
```

f1-origin-green: exit 0; `10 passed, 68 deselected in 0.41s`.

```sh
env PYTHONPATH=$PWD SOCIAL_CARDS_RENDER=false /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_agent_ready.py -k benchmark_markdown_fact_destinations
```

f2-code-red: exit 1; `1 failed, 11 passed, 36 deselected in 0.42s`.

```sh
env PYTHONPATH=$PWD SOCIAL_CARDS_RENDER=false /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_benchmark_body_render.py tests/test_agent_ready.py -k 'not built'
```

f2-code-green: exit 0; `44 passed, 17 deselected in 1.28s`.

## Final site verification

The final focused site suite builds both output trees once through the required heavy wrapper. The original site probes then reuse that tree. All required new metadata fields, canonical identities, Markdown destinations, model heading levels and the full-tree surface lint pass.

```sh
env PYTHONPATH=$PWD SOCIAL_CARDS_RENDER=false /Users/terbeest/.codex-g2/heavy.sh /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider --basetemp /tmp/MODEL-458-SITE-scratch/root/pytest-final-site tests/test_agent_ready.py
```

final-site: exit 0; `48 passed in 66.99s (0:01:06)`.

```sh
env PYTHONPATH=$PWD SOCIAL_CARDS_RENDER=false /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider --basetemp /tmp/MODEL-458-SITE-scratch/root/pytest-final-reproductions /tmp/MODEL-458-SITE-scratch/root/test_final_F3.py /tmp/MODEL-458-SITE-scratch/root/test_final_F1.py /tmp/MODEL-458-SITE-scratch/root/test_final_F2.py /tmp/MODEL-458-SITE-scratch/root/test_final_F4.py /tmp/MODEL-458-SITE-scratch/root/test_final_F5.py /tmp/MODEL-458-SITE-scratch/root/test_final_F6.py
```

final-reproductions: exit 0; `7 passed in 0.40s`.

Baseline site generation, before implementation, exited 0:

```sh
/Users/terbeest/.codex-g2/heavy.sh env PYTHONPATH=$PWD SOCIAL_CARDS_RENDER=false /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.build --out /tmp/MODEL-458-SITE-scratch/baseline
```

The generated-output inspection ran with:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python /tmp/MODEL-458-SITE-scratch/root/inspect_tree.py /tmp/MODEL-458-SITE-scratch/baseline
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python /tmp/MODEL-458-SITE-scratch/root/inspect_tree.py /tmp/MODEL-458-SITE-scratch/root/pytest-final-site/dist0
```

Both exited 0. The permanent built-tree tests enforce these output checks.

| Output check | Baseline | Final |
|---|---:|---:|
| Benchmark Markdown twins checked | 1,153 | 1,153 |
| Missing Markdown link occurrences | 33, comprising 27 distinct destinations across 23 pages | 0 |
| Pages with a heading jump | 505 | 0 across 1,372 model pages and the model index |
| Product/example/template pages missing OG fields | 132 | 0 |
| Existing optional social images absent | 42 | 42 |

Standalone corrected probes also exited 0:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python /tmp/MODEL-458-SITE-scratch/root/f7-final.py
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python /tmp/MODEL-458-SITE-scratch/root/f9-repro.py
```

The blog probe accepts the historical control and reports `REFUSED blog correction date is in the future` and `REFUSED blog correction must reference a published revision`. The llms.txt probe reports the policy statement, with no lag manifest and the same underlying public-image dates.

## Unresolved acceptance item

AUD-05-F5 asks that "each image resolves locally" while requiring preservation of the existing card registry, tests and optional rendering behavior, and forbidding browser image generation. The default build intentionally omits 42 referenced optional card files: the landing card, pricing card and 40 template cards. `test_build_without_the_flag_needs_no_npm_or_chromium` explicitly pins the missing files and registered image URLs. Universal image resolution therefore remains unmet under these constraints. All 85 newly introduced image references use the existing local fallback and pass resolution checks. No optional rendering or production switch was enabled.

## Observation limits

All observations are local. No production requests, social-service scrapes, browser image generation, paid-provider calls, deployment, Linear writes, merges or release actions were performed. External stylesheet cascades and runtime visibility were not evaluated. Blog behavior was observed using the signed synthetic fixture; the default build publishes no blog posts. Optional browser/layout suites and separate full-build fixtures were excluded; the final agent-readiness suite supplied the one final build. CI retains responsibility for the full repository suite and required remote checks.

Frozen data, legal text, ranking floors, contract ranges, prices, plans, Worker variables and production switches are unchanged. The baseline build emitted existing public hardware source-registration warnings. No background process remains. Scratch probes and build output are removed after the draft PR is opened, as required by the executor overrides.

## Round 2

Head at the start of this round: `77348c1f0ed51b99edcdf0cdade707ad93035767`. Image-baseline commit: `2702a3a1a48cface63f0ccfd0af519f0790d038e`. Guidance-hash commit: `2a09e2fbd96626506e37abe82e679fbf1823e001`. This section is a later commit.

### CI install failure

Required pytest jobs, the package smoke test, the Rank Worker bundle, and Worker memory headroom all failed while installing the package. `hatch_build.py` compares each `source_hashes` entry in `cli/modelspec/agent-bundle.json` with the file bytes and raises `ValueError: CLI guidance is stale`. The only stale source was `pipeline/pricing.py`. The pricing page now passes its description into the existing social metadata helper, which changes the file hash. The generated guidance text did not change.

A local hash comparison printed `stale ['pipeline/pricing.py']`. `python -m pipeline.agent_copy write` rewrote the bundle and left a one-line hash diff. The other generated files matched what was already committed.

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.agent_copy write
```

write: exit 0.

```sh
env PYTHONPATH=$PWD SOCIAL_CARDS_RENDER=false /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_agent_copy.py -k 'cli_bundle_and_schemas or all_agent_artifacts'
```

guidance-green: exit 0; `2 passed, 15 deselected in 4.78s`. A second hash comparison printed `stale []`.

Worker memory headroom exited during that same install and did not measure. This round does not change Worker export fields, rank rows, or the engine import graph. The 115 MiB and 120 MiB gates are unchanged. The packaged guidance gained no text.

### AUD-05-F5 image baseline

The accepted rule is narrower than universal local resolution. A new same-origin `og:image` or `twitter:image` with no file fails the site build. The 42 optional images the default build already references and does not write are listed, with that count, in `pipeline/optional_social_images.txt`. The loader rejects a list longer than 42. Default-build behaviour for those images is unchanged, and `MODELSPEC_RENDER_SOCIAL_CARDS=1` still writes them. When a default build starts writing one of the listed files, the list and the count have to shrink to match. The built-tree test requires the unresolved set to equal the list.

```sh
env PYTHONPATH=$PWD SOCIAL_CARDS_RENDER=false /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_pipeline.py -k 'social_image or optional_social_image or same_origin_missing or absolute_existing or example_shell_has_complete'
```

f5-baseline: exit 0; `15 passed, 68 deselected in 0.36s`.

```sh
env -u MODELSPEC_RENDER_SOCIAL_CARDS PYTHONPATH=$PWD SOCIAL_CARDS_RENDER=false /Users/terbeest/.codex-g2/heavy.sh /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.build --out /tmp/MODEL-458-SITE-scratch/dist
```

default-build: exit 0. Unresolved social images equalled the baseline: 42 names, no extra path, no stale path.

The eight findings from round 1 stay in place. Frozen data, legal text, ranking floors, contract ranges, prices, plans, Worker variables and production switches stay unchanged.

### CI after the baseline push

Worker memory headroom passed on Pyodide 0.28.3. The 115 MiB job limit and the 120 MiB ceiling are unchanged. Main, measured in that job: current peak 110.10 MiB (115450867 bytes), steady 109.31 MiB; successor peak 105.71 MiB (110843603 bytes), steady 104.92 MiB. PR bundle under `--limit-mib 115`: current peak 105.72 MiB (110858769 bytes), steady 104.94 MiB (110035777 bytes); successor peak 105.72 MiB (110857809 bytes), steady 104.94 MiB (110036097 bytes). Wasm peak is 59.875 MiB in every period. The PR is under main on the current period and matches the successor.

Two pytest shards failed for this change.

`tests/test_blog.py::test_site_build_includes_fixture_blog_from_public_root_only` got `build.main` return code 2. Post pages named `og:image` and `twitter:image` at `blog/<slug>/rN/og-card.png`. That file is written only when `MODELSPEC_RENDER_SOCIAL_CARDS` is on, and the path is not one of the 42 baseline names. The baseline was not grown. Flag-off post pages now use `og-card.png`, the site card the build copies. Flag-on builds still write and name the per-post card. Commit `e30bd7de197179148f483dac975542ea5ec1575d`.

`tests/test_entity.py::test_the_method_page_says_what_is_public_in_both_data_states` calls `method.page` with both availability flags at their default, false. AUD-05-F1 no longer prints "public, versioned and free to fetch" for that call. The three `DATA_SPLIT_ENABLED=true` assertions stayed: "free to fetch" absent, `snapshot.json.gz` absent, "frozen public image" present. The flag-off assertion now expects the absent-download sentences and no `snapshot.json.gz`. Commit `54899f53bcbac7612d327cda8b865b66dc332e86`.

```sh
env PYTHONPATH=$PWD SOCIAL_CARDS_RENDER=false /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_entity.py -k test_the_method_page_says_what_is_public_in_both_data_states tests/test_blog.py -k 'published_markdown or corrections_update or preview_writes or draft_post'
```

ci-focused: exit 0; `4 passed, 34 deselected in 1.09s`.

```sh
env PYTHONPATH=$PWD SOCIAL_CARDS_RENDER=false /Users/terbeest/.codex-g2/heavy.sh /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_blog.py::test_site_build_includes_fixture_blog_from_public_root_only
```

ci-blog-build: exit 0; `1 passed in 51.27s`.

This follow-up does not change Worker imports, packaged guidance text, ranking floors, legal text, contract ranges, prices, plans, or production switches.

## Round 3

Head at the start of this round: `cb1ad6478ff9bc6801fd01f0f3bc7fdaf95b882c`. Merge commit: `9317c434e2a5242681768f93745f20e2c15dcee2`, from `origin/main` at `f0f8ca5c76e7dd5b4d906ae25fac85856a3cfd17`. The merge was clean. This section is the following commit.

### Companions

The merge did not leave a generated file stale.

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.agent_copy check
```

agent-copy: exit 0.

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python api/worker/openapi.py --check
```

openapi: exit 0. `openapi.yaml` matches the implementation.

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -c 'import json; from pathlib import Path; from qa.contracts import capture_tools; recorded = json.loads(Path("qa/fixtures/mcp-tools.json").read_text()); raise SystemExit(0 if recorded == capture_tools() else 1)'
```

mcp-tools: exit 0.

### Tests on the merge

```sh
env PYTHONPATH=$PWD SOCIAL_CARDS_RENDER=false /Users/terbeest/.codex-g2/heavy.sh /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_agent_ready.py tests/test_blog.py tests/test_brand.py tests/test_entity.py tests/test_llms_txt.py tests/test_method.py tests/test_pipeline.py tests/test_social_cards.py tests/test_surface_lint.py -k 'not renderer_writes and not chromium_layout and not every_frozen_template_card and not build_emits and not blog_fixture_is_readable'
```

merge-focused: exit 0. `429 passed, 5 deselected in 266.11s`.

### Provider headings

Provider headings on `/models/` stay `h2` and carry `provider-heading`. The models index adds a rule for `.page h2.provider-heading`. The base `h3` rule in `pipeline/render.py` at `5dd0eb5a16637d254c23f2903a5b97fb134ef9c3` is `font-family:var(--sans);font-weight:700;font-size:16px;letter-spacing:-.01em;margin:22px 0 6px`. That rule sets no text transform, colour, border, or padding. The class rule uses those values and sets `text-transform:none`, `color:inherit`, `border-bottom:0`, `padding-bottom:0`, `position:static`, and `counter-increment:none`. Its `::before` content is `none`. `.page h2.provider-heading` is more specific than `:where(.page) h2`, and the rule does not use `!important`. The rule is inserted on the models index only, so the shared stylesheet and the no-guide model-page fixture stay byte-identical.

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_pipeline.py -k 'provider_headings_keep_the_base_measure or ungrouped_strip_title_keeps_the_strip_measure'
```

r3-red: exit 1. `2 failed, 83 deselected in 0.38s`. The provider assertion compared `['', '']` with the `provider-heading` class. The strip assertion did not find `font-weight:700` in `font-family:var(--sans);font-size:14px;margin:0 0 5px`.

With the class present and the class rule removed, the same provider test failed at `assert rule is not None`. Exit 1. `1 failed in 0.94s`.

### Other heading levels

```sh
git diff 5dd0eb5a16637d254c23f2903a5b97fb134ef9c3 -U0 -- pipeline/render.py | rg '^[+-].*<h[1-6]'
```

The only heading-tag changes are the models index provider, from `h3` to `h2`, and the ungrouped benchmark-strip title, from `h4` to `h3` when the strip has no group. Group headings stay `h3`. Grouped strip titles stay `h4`. Section headings on the model page stay `h2`. They already matched `:where(.page) h2` on the base, so this round does not restyle them.

An ungrouped strip title is an `h3`, so it matches the generic `h3` rule and `.strip-group h3`. The existing `.benchmark-strip :is(h3,h4)` rule already sets the 14px size and the `0 0 5px` margin. `letter-spacing:-.01em` from the generic `h3` rule and `color:var(--mute)` from `.strip-group h3` still applied. On pages that render strips, that rule now also sets `font-weight:700`, `letter-spacing:normal`, and `color:inherit`. The link and hover selectors still use `:is(h3,h4)`.

### Green

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_pipeline.py::test_models_index_provider_headings_keep_the_base_measure tests/test_pipeline.py::test_ungrouped_strip_title_keeps_the_strip_measure tests/test_pipeline.py::test_models_index_provider_heading_follows_page_title tests/test_pipeline.py::test_ungrouped_benchmark_strip_heading_follows_its_section tests/test_pipeline.py::test_model_page_passes_coverage_to_benchmark_strips tests/test_model_guide_render.py::test_card_without_guide_is_byte_identical_to_main
```

r3-green: exit 0. `6 passed in 1.28s`.

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_pipeline.py tests/test_instrument_render.py tests/test_model_guide_render.py
```

r3-render: exit 0. `128 passed in 31.59s`.

```sh
env -u MODELSPEC_RENDER_SOCIAL_CARDS PYTHONPATH=$PWD SOCIAL_CARDS_RENDER=false /Users/terbeest/.codex-g2/heavy.sh /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.build --out /tmp/MODEL-458-SITE-scratch/dist
```

default-build: exit 0. The build printed the existing unregistered hardware source notices.

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pipeline.surface_lint --tree /tmp/MODEL-458-SITE-scratch/dist/modelspec
```

surface-lint: exit 0. `0 findings; 5366 files checked`.

The optional-image baseline length is 42. Unresolved social images on that tree equal the baseline, 42 names. `missing_social_images` is empty. `/models/index.html` has 83 `h2` elements, each with `provider-heading`, and no `h3`.

Heading levels are unchanged in this round. No existing assertion was removed or loosened. Frozen data, legal text, ranking floors, contract ranges, prices, plans, Worker variables, and production switches are unchanged. The 120 MiB, 115 MiB, and 100 ms gates are unchanged.
