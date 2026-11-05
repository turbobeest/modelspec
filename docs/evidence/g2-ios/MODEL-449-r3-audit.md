# MODEL-449 round-three reader audit


The runtime `deterministic_extractors()` factory contains 18 readers. Adding the injected `LLMExtractor` and `LicenceExtractor` gives 20 concrete reader classes in the audited path.

| Reader | Identity binding observed |
| --- | --- |
| `XaiMatrixExtractor` | Canonical subject ID, exact source URL, region ID, copy hash and reviewed document hash. Published subject comes from the template reader. |
| `HFConfigExtractor` | `_hf_bound_subject` matches the full repository ID or registered repository alias through the shared matcher; Hub JSON ID must also equal that repository. |
| `ModelCardParamsExtractor` | Same repository binding. Candidate mentions expand to a whole source name and use the shared matcher. Named rows/headings/prose retain their source spelling; unnamed specification fields inherit the exactly bound repository. |
| `DenseActiveEqualsTotalExtractor` | Recomputes counts only across documents with the same exact repository binding. Its subject is the bound source repository. |
| `HFParametersExtractor` | Exact repository and Hub JSON ID binding, followed by numeric tensor-count parsing. |
| `CanonicalLicenceExtractor` | `_licence_subject` preserves a direct source name; exact-template and explicit base-model metadata rules remain canonical identity bindings. |
| `LicenceTermsExtractor` | Registered canonical model ID plus exact reviewed region and governing URL. No fuzzy page-name matching. |
| `StructuredDataExtractor` | Emits the original structured row subject. Final comparison uses `_reading_subject_matches` and the shared exact matcher. |
| `OfferingPriceExtractor` | Flat/grouped/transposed row names, scoped headings and cached prose use the shared exact matcher and keep source names. Metric-table ownership also requires exact declarations/headings. |
| `SubscriptionPageExtractor` | All plan identity decisions use the shared matcher after parsing complete names. Price/card searches stop at new explicit headings and possible sibling titles. See the rejection-only distinction below. |
| `PerplexityFaqExtractor` | Imported fixed template, inspected separately. Exact canonical subject and field, exact `/pro` source binding, structural hash and approved ordered items. Its published `Pro` identity is fixed by that reviewed template. |
| `TableExtractor` | Emits original row subjects without renaming. Final comparison uses the shared matcher. |
| `TransposedTableExtractor` | Exact whole model column header through the shared matcher; preserves that header. |
| `GovernanceProseExtractor` | Established provider-wide statements apply to the offering. A model-scoped retention clause now requires an exact parsed subject. Generic policy scope does not infer a sibling model identity. |
| `KeyValueExtractor` | Exact declared name or owning model section through the shared matcher. Foreign titles close the previous section. |
| `ModelPageExtractor` | Exact row names and independently scoped exact model sections. Labels and feature phrases are read only inside those sections. |
| `MistralOutputModalitiesExtractor` | Exact model sections plus its existing first-party URL/source-kind gate. Label matching reads modalities, not identity. |
| `LabJurisdictionExtractor` | Established lab-scoped source semantics. It reads the lab's incorporation jurisdiction, not a model name from prose. |
| `LLMExtractor` | `_llm_published_subject` checks the returned subject against complete source row/heading/declaration/grammatical candidates. It preserves the raw source candidate. Pronoun/label-only quotes use their owning section; a sibling-only source cannot be renamed by the JSON response. Empty absence responses require an independently matched source subject. |
| `LicenceExtractor` | Validates the quoted operative clause, then uses `_licence_subject` for exact source binding as above. Quoted-clause containment is content validation, not model identity matching. |

`_reading_subject_matches` permits only the separately modelled effort qualifier to be removed before exact identity comparison. Semantic `+` is preserved in shared matching and catalogue keys. No accepted model identity in this census comes from a substring or prefix match.

The explicit exception is `_plan_title_boundary`: it closes a price/content search when a following title extends the registered name. Its prefix/suffix check is rejection-only. It never produces a subject, a price, an alias, or a verified reading. This protects bare sibling titles while retaining existing provider descriptions such as `Power use` before a price. Three full-verifier red cases prove that wrong sibling prices were accepted before this guard; all existing descriptor fixtures still pass.

Additional final red/green observations:

- `tests/test_llm_subject_attribution.py`: six initial failures proved that an explicit JSON subject could rename sibling-only source rows, prose and headings, and that source spelling was lost. Log `llm-red.log`.
- A seventh plain-section quote case failed after the first LLM change and passed after ownership was enforced for plain sections too. Log `llm-plain-red.log`.
- `tests/test_subject_attribution.py -k price_search`: three failures before the subscription section-boundary fix. Log `card-scope-red.log`.
- Final focused command: `env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_llm_subject_attribution.py tests/test_subject_attribution.py tests/test_decision_verify.py tests/test_subscription_availability_reader.py tests/test_offering_drafter.py`, exit 0, **557 passed in 2.32 seconds**. Log `final-focused.log`.
- Removed the dead `_NAME_JOIN` constant after deleting the previous phrase matcher.

The remaining substring operations inspected in this file parse labels, quote presence, numeric units, value vocabulary, source paths, or rejection boundaries. No additional unsafe source-subject matcher was identified in this final read-only pass. This is an audit conclusion, not a claim that arbitrary prose interpretation is exhaustive.

## Red commands and boundary tests

All commands used `env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider` in the ticket worktree. Each selector below was run before its corresponding fix. The counts and retained output paths are in the main evidence table.

```sh
# Three-line rows, mixed rows, source heading and cached-prose cases through draft_offering.
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_offering_drafter.py -k model_page
# Full verifier fallback and page ownership.
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_decision_verify.py -k 'full_verifier_cannot_fall_through or full_verifier_keeps_model_headings'
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_decision_verify.py -k full_verifier_retention
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_decision_verify.py -k missing_llm_subject
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_model_396_readers.py -k inherit
# Subscription/metadata identities and card ownership.
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_subject_attribution.py
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_subject_attribution.py -k 'infer_missing or multiplier_source'
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_subject_attribution.py -k plus_sibling
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_subject_attribution.py -k price_search
# Parameter/effort identities, including registered alias and qualifier controls.
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_subject_reader_guards.py
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_subject_reader_guards.py -k effort_caption_uses_registered
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_subject_reader_guards.py -k parameter_prose
# Source binding of injected LLM responses; no provider calls.
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_llm_subject_attribution.py
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_subject_scopes.py -k feature_sentence
```

For the completed new boundary cases tested against the original verifier, the exact baseline-loading command was:

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python - <<'BASELINE'
import subprocess
import decision.verify as verifier
import pytest
baseline = subprocess.check_output(['git', 'show', '706d1cb0:decision/verify.py'], text=True)
exec(compile(baseline, verifier.__file__, 'exec'), verifier.__dict__)
raise SystemExit(pytest.main(['-q', '-p', 'no:cacheprovider', 'tests/test_decision_verify.py', 'tests/test_model_396_readers.py', '-k', 'full_verifier or inherit']))
BASELINE
```

That observed run failed 15 cases and passed 3. The later mixed-row baseline run used the same loading sequence with `tests/test_decision_verify.py -k full_verifier_keeps_exact_rows` and failed all 4 cases. Later additional full-verifier tests increase the selection in a fresh replay; no test expectation depends on the old count.
