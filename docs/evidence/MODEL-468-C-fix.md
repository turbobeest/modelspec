# MODEL-468-C host identity evidence

Branch `model-468-c`. Base `58748fec44f4055a16e37229764f60467278a5a8`. The head is the commit that adds this file. Read it with `git log -1 --format=%H -- docs/evidence/MODEL-468-C-fix.md`.

Requirement commits:

- `eac1854c2cb63b8f0a217c1ac12cb66b87082fbd` registers a lab's own Hugging Face organisation.
- `d0b047e992054a69dc05c7d52e6ebc896c5aeaf1` registers the sibling docs hosts.
- `98dbb7e7779d74c4db095c619b5054786f050299` changes the imagine reason.

Python 3.14.4 and pytest 9.1.1, from the repository virtualenv. Focused pytest was serial, `env PYTHONPATH=$PWD python -m pytest -q -p no:cacheprovider`, with no `-n`. Exit codes were read directly.

## Hugging Face organisation

`test_a_registered_huggingface_org_is_the_labs_page`, `test_a_huggingface_org_match_is_case_insensitive`, `test_a_huggingface_repository_named_for_another_model_is_uncertain`, and `test_a_provider_with_two_huggingface_orgs_accepts_both` failed on the unchanged pipeline. A registered org stayed `uncertain` instead of `new`. A repository named for another model reported `models.dev not_listed; host class unregistered` instead of `the primary source does not identify the stated lab`. 4 failed, 3 passed, 191 deselected, 0.66s, exit 1.

The three passing tests were the refusal cases and the cite-only guard. Another user, `spaces/`, `datasets/`, and a bare org were already unregistered. A cite-only `huggingface.co` was already left unfetched.

After the org check, that selection passed. 7 passed, 191 deselected, 0.70s, exit 0. The whole of `tests/test_release_signals.py` then passed. 198 passed, 1.78s, exit 0.

The check sits beside the lab host set. `first_seen_host_class` for `https://huggingface.co/AcmeLab/orbit-9` stays `unregistered`, and `huggingface.co` is not added to the set. The pipeline accepts the page when the first path segment casefolds to a `kind: huggingface` org whose provider normalises to the signal provider or the resolved lab slug. The same orgs are passed into `_primary_identity` for a listed models.dev row as well as a not-listed signal.

The result keeps `primary_host` as `huggingface.co` and adds `primary_kind` with value `huggingface-org`. Identity still needs the model name. The repository name, normalised, must equal the signal's normalised model name, or the page text must contain that name under the existing name check. A repository named for a different model, whose page text does not contain the signal name, is `uncertain` and writes no card. That page is fetched, because the org matched.

`scripts/process_release_signals.py` copies `primary_kind` onto the JSON result when the field is set. That file is outside the spec's named list. The JSON result is where `primary_host` is recorded, so the new field has to be copied there.

## What the registries allow for huggingface.co

`registry/source-retention.json` does not list `huggingface.co` in `cite_only_hosts`. `decision/excluded.py` does not list it. `require_allowed_source` therefore allows an https URL on that host. `_huggingface_repo` already fetches the Hugging Face search API and a repository page through that gate. This repository has no `registry/source-terms.json`. The release-signal fetch does not consult source terms. No terms class was changed.

If `huggingface.co` is cite-only, the host class stays `cite-only` and the repository page is not fetched. `test_a_cite_only_huggingface_host_stays_unfetched` covers that. Page bytes are used for the name check. The card records the URL and does not store the page body.

## Sibling docs hosts

`test_sibling_docs_hosts_identify_the_lab_and_community_openai_is_refused` and `test_a_redirect_between_registered_hosts_records_the_final_host` failed before the host table change. Both expected `new` and got `uncertain`. 2 failed, 198 deselected, 0.51s, exit 1.

`LAB_HOSTS` in `scripts/admission_drafter.py` now includes `docs.anthropic.com`, `platform.openai.com`, and `platform.deepseek.com`.

Two readers use that table. `registered_lab_hosts` matches a host exactly, or a subdomain only when the entry is written `*.parent`. `source_block` matches the host or any subdomain.

Each added host is already a subdomain of a parent in the same table: `anthropic.com`, `openai.com`, and `deepseek.com`. A host that matches a new entry already matched that parent. That includes `community.openai.com`. Compared with the previous tuples, the admission match did not change for those hosts or for a one-label subdomain of each. With an empty terms map, `source_block` still returns `source-terms hold (MODEL-409)` for the three new hosts and for `community.openai.com`. The admission drafter still does not fetch them.

The pipeline matches exactly, so `community.openai.com` stays `unregistered` and is not fetched. The three added hosts are lab hosts.

`get_source_response` follows redirects, and the pipeline stores the fetch result's URL. When that final host is also registered for the same lab, `primary_host` is the final host. The redirect test returns a fetch result whose URL is `https://platform.claude.com/docs/en/orbit-9` for a request to `https://docs.anthropic.com/docs/orbit-9`. `platform.claude.com` is registered by the anthropic page source in the watch file. The result records `platform.claude.com`.

After the change, the two new tests passed, 0.66s, exit 0. `tests/test_release_signals.py` and `tests/test_admission_drafter.py` then passed. 241 passed, 6.10s, exit 0.

## Imagine

`test_review_names_follow_the_normalised_model_name` and `test_imagine_is_image_or_video_generation` failed with `assert 'image generation' == 'image or video generation'`. 2 failed, 3 passed, 0.36s, exit 1.

`imagine` is now its own rule. The reason is `image or video generation`. `flux`, `dall-e`, `stable-diffusion`, `gpt-image`, `imagen`, and `nano-banana` stay `image generation`.

`tests/test_release_signals.py`, `tests/test_release_scope.py`, and `tests/test_admission_drafter.py` then passed. 246 passed, 6.06s, exit 0.

## Not observed

No live network. No full pytest suite, no site build, and no shard remeasure. The new tests are in files that already have weights in `tests/shard_durations.json`. No Worker deploy, no Linear write, and no merge. CI on the pull request had not been observed when this file was written.
