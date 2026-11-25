# MODEL-468 interpretability scope

An artefact tag makes `tag_scope` return out of scope when the pipeline tag is absent or `feature-extraction`. The reason names the tag, for example `interpretability artefact (tag: transcoder)`. Any other pipeline tag leaves the repository in scope. This check runs before a keeping task tag.

The whole tag is matched after `_folded`, and an underscore counts as a hyphen. The set is `interpretability`, `mechanistic-interpretability`, `transcoder`, `cross-layer-transcoder`, `sparse-autoencoder`, `sparse-autoencoders`, `sae`, `saelens`, `sae-lens`, `crosscoder`. `relevant_hub_tags` keeps those tags. A filed signal gains no new field.

Catalogue replay matched `_CATALOGUE_SCOPE_EXCEPTIONS` and added no rejection. `tests/test_release_scope.py` reported 61 passed. The writer-isolation file and the three release-watch files reported 495 passed. Ruff reported no findings on the two edited Python files.

Base `60a3fe19768345086f9582b499e14cfb8030eea5`. Serial pytest, `-q -p no:cacheprovider`, no `-n`.
Python 3.14.4, pytest 9.1.1, ruff 0.16.6. CI runs the full suite after the push.
