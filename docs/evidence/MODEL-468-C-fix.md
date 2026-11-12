# MODEL-468-C host identity evidence

Branch `model-468-c`. Base `58748fec44f4055a16e37229764f60467278a5a8`. The head is the commit that updates this file. Read it with `git log -1 --format=%H -- docs/evidence/MODEL-468-C-fix.md`.

Python 3.14.4 and pytest 9.1.1, from the repository virtualenv. Focused pytest was serial, `python -m pytest -q -p no:cacheprovider tests/test_release_signals.py tests/test_release_scope.py tests/test_admission_drafter.py`, with no `-n`. Exit codes were read directly. No live network.

## Hugging Face organisation

A `kind: huggingface` source names the lab's own repository when the URL host is `huggingface.co` and the path is exactly `/<org>/<repo>`. One trailing slash is allowed. Each segment matches `[A-Za-z0-9][A-Za-z0-9._-]*`. A percent sign, an empty segment, `spaces`, `datasets`, a bare org, another owner, a discussion, or a tree path is not that page. The same check runs on the URL after a redirect. `huggingface.co` is not added to the lab host set. A cite-only host is not fetched.

The source provider matches the signal provider, or it resolves to the same catalogue lab slug `resolve_signal` would use. A provider that resolves to a different lab does not match. An org registered only for another provider is not fetched.

Identity on that page is the repository name only. The name is normalised and compared with the signal's model name. Page text and JSON-LD do not identify this kind. `Orbit-9-GGUF`, `Orbit-9-lora`, and `comet-1` stay uncertain for a signal named `Orbit 9` even when the page names that model. The result records `identity_basis`: `repo-name` for this kind, `page-text` or `json-ld` for a lab host.

The drafted card sets `huggingface_url` to that repository and leaves `provider_docs_url` empty.

## Provider doc URL

`docs.anthropic.com`, `platform.openai.com`, and `platform.deepseek.com` are not in `LAB_HOSTS`. `scripts/admission_drafter.py` matches `origin/main`.

When a models.dev listing has no `release_url`, `homepage`, or `url`, and the primary would be the provider `doc` URL, the signal's first-seen URL is used instead when that URL is a registered lab page or a registered organisation repository. The provider doc host is not requested. A first-seen URL on an unregistered host still uses the provider doc. A host the existing fetch gate refuses is not fetched.

## Imagine

`imagine` is its own scope rule. The reason is `image or video generation`.

## Tests

Each review check failed on the code that lacked it, then passed after the change. The last focused run was 260 passed, exit 0.

Removing the provider comparison made an org registered for `other` draft a card. Removing the post-fetch classification reported an identity failure instead of `host class unregistered`. The four refused path shapes, and a redirect onto `/tree/main`, drafted cards. A repository whose page names the model drafted a card until identity was limited to the repository name. The drafted card left `huggingface_url` empty. A source provider `Alpha / Beta Team` that resolves to lab `beta` stayed unregistered for a `beta` signal. A listed model whose only URL was a provider doc on another host stayed uncertain instead of reading the registered first-seen page.

## Not observed

No full pytest suite, no site build, and no shard remeasure. The tests are in files that already have weights in `tests/shard_durations.json`. No Worker deploy, no Linear write, and no merge. CI on the pull request had not been observed when this file was written.
