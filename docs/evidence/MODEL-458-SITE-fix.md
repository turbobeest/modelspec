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

