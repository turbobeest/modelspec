# MODEL-458-SITE verification

Base SHA: `5dd0eb5a16637d254c23f2903a5b97fb134ef9c3`.
Final SHA: the commit containing this report, reproducible with `git rev-parse HEAD` in the reviewed checkout. The executor completion line records the full SHA.

Environment: Python 3.14.4, pytest 9.1.1, git 2.50.1. Tests run serially from the assigned worktree, with `PYTHONPATH=$PWD` and `SOCIAL_CARDS_RENDER=false`. No local full pytest suite is run.

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

f5-green: exit 1; `2 failed, 151 passed, 9 deselected in 91.68s (0:01:31)`.

```sh
env PYTHONPATH=$PWD SOCIAL_CARDS_RENDER=false /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_social_cards.py tests/test_feedback_page.py tests/test_brand_page.py tests/test_pricing_page.py tests/test_landing.py tests/test_orchestrators.py -k 'not renderer_writes and not chromium and not build_without and not build_with and not build_emits and not template_card_failures and not blog_fixture_is_readable and not behaviour_in_browser and not recipe_is_discoverable'
```

f5-caller-green: exit 0; `91 passed, 22 deselected in 89.45s (0:01:29)`.

```sh
env PYTHONPATH=$PWD SOCIAL_CARDS_RENDER=false /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_brand.py tests/test_method.py tests/test_about.py tests/test_pipeline.py tests/test_social_cards.py -k 'escapes_complete or example_shell_has or template_card_and_page_preserve or registry_drives or landing_card_html or each_page_points'
```

f5-regressions-green: exit 0; `8 passed, 130 deselected in 0.98s`.

## AUD-05-F6

Provider sections use h2; ungrouped benchmark titles use h3 and grouped titles remain h4. Affected model pages extend existing strip styling to h3 without changing the no-evidence golden shell. Red assertions observed heading sequences 1→3 and 2→4. All instrument and model-guide tests, including the byte-identical golden fixture, pass.

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

