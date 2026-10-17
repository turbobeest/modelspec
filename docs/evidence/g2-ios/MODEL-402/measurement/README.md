# Reproduce the MODEL-402 bundle measurements

Run these commands from the MODEL-402 worktree root:

```bash
/Users/terbeest/dev/modelspec/.venv/bin/python docs/evidence/g2-ios/MODEL-402/measurement/run_measurements.py
/Users/terbeest/dev/modelspec/.venv/bin/python docs/evidence/g2-ios/MODEL-402/measurement/measure_baseline.py
```

`run_measurements.py` exports the entire frozen public repository through the
real `api/worker/vendor.py --data-dir` path. It then signs two copies of the
complete compiled snapshot with a synthetic HMAC key and synthetic validity
dates. The successor starts tomorrow in UTC. Both copies retain every compiled
candidate, facet, and verification record. Each snapshot has 87 lineup
candidates and an empty archive in this frozen fixture. Both corpus sections
remain present.

The fixture also includes two copies of the full frozen vocabulary, each with
the corresponding snapshot reference. It does not measure the private production catalogue.
The synthetic validity dates do not describe the frozen prices' actual
schedules. The behavior tests separately exercise real scheduled prices.

The runner copies the handwritten Worker source and dependency locks into
`api/worker/.scratch-model402-measurement/worker`. Its isolated Wrangler
configuration has no account, route, binding, or production variable.
The only Wrangler build command is `deploy --dry-run`. The runner strips
Cloudflare credentials from child environments and disables Wrangler metrics.
The runner installs the workflow's pinned uv 0.12.19 in the scratch directory.
The preinstalled uv 0.7.13 cannot run this pywrangler version.

The runner caches Pyodide's five dependency wheels in a separate setup process
before it measures memory. The memory probe uses the repository's Pyodide 0.28.3 probe
with added assertions
for both held snapshots and a clock change to the successor. It drives a
decision before and after handover, vocabulary, rank, and policy-check. The
stubbed Worker fetch refuses every attempted network request.

`measure_baseline.py` removes only the successor snapshot and vocabulary from
the same generated bundle. It runs another dry build and the original memory
probe, then restores the dual-snapshot bundle in a `finally` block.

The runners record commands, tool versions, output, and direct exit codes in
the adjacent text and JSON files. `fixture.json` records the payload sizes and
candidate counts. `summary.json` and `baseline-summary.json` record the
measurements. `upload-manifest.json` records each dual-snapshot output file's
size and SHA-256 digest.

The observed dual-snapshot upload totals 10,304,957 bytes, or 10,063.43 KiB,
with 3,371.42 KiB gzip. The one-snapshot baseline totals 9,588.66 KiB,
with 3,011.64 KiB gzip. Both dry builds and the dual output import check exit 0.

The cached dual memory probe measures 116.3317 MiB steady and 116.3965 MiB peak
and exits 0. The prior cached run measures 116.3312 MiB steady and
116.3961 MiB peak and exits 0. Both use 71.875 MiB of Wasm memory.
The baseline measures 103.8661 MiB steady and 104.2666 MiB peak and exits 0.
The dual probe increases steady memory by about 12.47 MiB over that baseline.

An earlier dual probe downloads the five dependency wheels in the measured
process. It measures 120.7204 MiB steady and 120.7852 MiB peak and exits 1
because it exceeds the unchanged 120 MiB safety threshold. Every request
assertion passes. That run has the same 71.875 MiB Wasm allocation as the
cached runs and about 4.39 MiB more retained non-Wasm memory. The package
downloads and memory difference suggest setup overhead; the probe does not
prove the cause. `memory-cold-download.txt` preserves this result.

These measurements use Node with Pyodide, rather than a deployed Cloudflare
isolate. They do not establish the private production catalogue's memory use.
The [Cloudflare Workers limits](https://developers.cloudflare.com/workers/platform/limits/)
last updated on October 12, 2026 specify 64 MiB of uncompressed Worker code and
128 MB of isolate memory. The measured upload uses 15.36 percent of the code
limit. All observed memory totals also remain below 128,000,000 bytes,
but the cold-download observation fails the repository's
stricter 120 MiB safety threshold.

Generated source, dependencies, and upload files stay under the ignored scratch
directory. The runners start no persistent services and make no vendor API
calls.
