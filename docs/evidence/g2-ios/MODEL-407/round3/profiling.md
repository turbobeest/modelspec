# MODEL-407 round 3 public loader profile

Measured on 2026-10-18 with Python 3.14.4 on macOS arm64. The final loader's
best of five was **13.303 ms**, below the unchanged 100 ms test bound. An
independent local run measured 12.302 ms. These native CPU results do not
establish CI timing or Worker memory acceptance. See the
[main evidence report](../../MODEL-407-fix.md) for those checks.

The committed change uses the C JSON decoder for complete arrays already in
the reader's buffer. Arrays that need more input use the existing bounded
reader. This removes Python dispatch for most array elements without asking
for a larger buffer. A shared dictionary-key memo preserves retained index
size across both paths.

The earlier whole-document C decoder was faster, but failed the public
115 MiB memory gate. It measured 116.490 MiB for the native successor probe
and 116.549 MiB for warm rollover. Its source remains here as a rejected
prototype for reproducing the CPU comparison. It is not the final loader.

## Reproduce

Run from the repository root in an environment with the repository and test
dependencies installed. The recorded runs used
`/Users/terbeest/dev/modelspec/.venv/bin/python`.

```sh
PYTHONPATH=$PWD python docs/evidence/g2-ios/MODEL-407/round3/profile_snapshot.py \
  --variants baseline candidate --candidate-ref f6dbbcd8 --profile
```

The default output directory is `tmp/model-407/round3/profile-reproduction`.
The script writes no files into this evidence directory. `--out` selects a
different output directory. Omitting `--variants` also measures the historical
loader, rejected whole-document prototype, and original in-memory array
experiment. The default candidate is pinned to
`f6dbbcd86845e614a00d3bd7ce8dfa4d55c2f618`.

The script builds the real `thirty_models()` fixture using the registry and
date from `test_a_thirty_model_snapshot_is_small_and_loads_fast`. It performs
one warm load, then five timed file loads with GC disabled. Each previous
index remains alive during the next load, matching the test. It asserts
120 candidates, the existing 3 MB compressed-size bound, and a best time
below 100 ms. Signing credentials are explicitly disabled for this public
fixture. A missed time bound produces exit status 1 after saving results.

Each variant compiles frozen git source into its own module. The baseline is
`819ba9e1aeb4e5e8a91e305a044224ff061605ed`. Historical commit
`4443bb7a3ec8d02d509d60b05eae876354cce92e` includes the hardware-table change
and predates the streaming parser. `whole_c` installs the adjacent
[prototype helper](canonical_c_decoder.py) into the baseline snapshot module.
`fast_arrays` applies the original array experiment to the baseline reader in
memory. `candidate` loads the final committed reader and snapshot module.

The script saves source copies beside generated results so each run can be
inspected. Those copies and binary profiler files are not duplicated here.
The committed final reader is byte-identical to the standalone array
prototype used in the public memory experiments. Both saved final timing
runs also used that exact reader. Their JSON retains the original
`candidate_ref: WORKTREE` label; source equality with `f6dbbcd8` was checked
before publishing these files. The in-memory `fast_arrays` timing variant
uses wrappers for the same two changes and has a small extra call count.

## Saved timing and profiles

The fixture is 62,806 compressed bytes and 1,192,167 UTF-8 JSON bytes. Its
uncompressed SHA-256 is
`7a05ee0c93aee2e464c8048a2b958fa5fd76a7644a386d47bbaa05ca280aaf52`.
Every measured variant produced snapshot `snap_cbe0b1853f4c8052` and a
4,517,095-byte native index estimate. That recursive object-size estimate
compares representation size; it is not a Worker memory measurement.

| Recorded run | Variant | Five samples in milliseconds | Best |
| --- | --- | --- | ---: |
| [Initial](timing-initial.json) | Baseline | 76.654, 77.070, 74.712, 74.809, 75.150 | 74.712 |
| Initial | Historical C decoder | 5.947, 6.209, 6.098, 6.308, 6.002 | 5.947 |
| Initial | Rejected whole-document prototype | 5.621, 6.229, 6.123, 6.197, 6.044 | 5.621 |
| Initial | Buffered-array experiment | 11.602, 11.982, 12.405, 12.884, 12.913 | 11.602 |
| [Final](timing-final.json) | Baseline | 72.040, 70.149, 69.976, 72.475, 73.446 | 69.976 |
| Final | Committed candidate | 13.303, 13.813, 13.733, 13.723, 14.098 | 13.303 |
| [Confirmation](timing-confirmation.json) | Committed candidate | 12.302, 13.265, 13.115, 12.703, 12.770 | 12.302 |

Profiles use a separate single load after the five unprofiled timing samples.
The [final baseline profile](profile-final-baseline.txt) records 2,950,699
calls, including 150,297 `read_value`, 143,095 `_scalar`, 318,779 `_whitespace`,
and 611,093 `_starts` calls. The [final candidate profile](profile-final-candidate.txt)
records 214,235 calls. Snapshot indexing remains about 4.4 to 4.6 profiled
milliseconds in that run. The rejected whole-document and historical paths
make about 30,650 calls; their initial profile texts are included alongside
the initial baseline and array experiment profiles.

Profiler overhead affects the many-call baseline more than the candidate.
Use the unprofiled samples for the timing gate. Cumulative profile categories
overlap and must not be added together.

## Differential and lifetime checks

Run the check against the production reader in the current checkout:

```sh
PYTHONPATH=$PWD python docs/evidence/g2-ios/MODEL-407/round3/check_fast_arrays.py
```

The [saved result](differential-final.json) records commit `f6dbbcd8` and the
SHA-256 of `decision/json_stream.py`. It passed 16,040 comparisons with
standard `json.loads`, checking acceptance, values, and exact source hashes
at chunk sizes 1, 7, 64, and 65,536. The fixed random seed makes the case count
repeatable. Cases include Unicode, escapes, duplicate keys, incomplete
arrays, malformed parent framing, and mutations of generated documents.

Three additional cases check dictionary-key identity across streamed objects,
complete buffered arrays, and arrays whose first C decode fails after complete
dictionaries. Four cases check reader release with cyclic GC disabled after
success and failure, including failure after the dictionary hook has run.

The published scripts were executed from this directory. The differential
check and all five timing variants exited 0. Their default output path and
adjacent prototype helper were verified without a vendor build or full test
suite. Correctness and memory acceptance remain in the main evidence report.
