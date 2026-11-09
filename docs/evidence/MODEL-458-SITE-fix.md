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

