# Round 3 package and memory measurements

Measured on 2026-10-18 UTC from source commit
`7f04d05f78d5c07ff6604f0e2e9fffc7c7652798`. The Worker and decision source
directories were clean when exported. All 80 source-file hashes in
[fixture.json](fixture.json) match that commit, as checked by
[verify_sources.py](verify_sources.py) and recorded in
[source-verification.json](source-verification.json).

The fixture exports this checkout's complete frozen public catalogue through
the real `api/worker/vendor.py` path. It has 87 public candidates and zero
archive candidates. Both corpus sections are present. The measurement helper
applies synthetic validity dates and a public fixture HMAC key to two complete
copies of that export. It also supplies the matching vocabulary for each copy.
Both signatures are checked by the real loader. These dates test packaging and
handover, and do not describe production prices.

| Measurement | Two snapshots | Same source, successor blobs omitted |
| --- | ---: | ---: |
| Wrangler raw package | 10063.92 KiB | 9589.12 KiB |
| Wrangler gzip package | 3371.56 KiB | 3011.80 KiB |
| Exact two-snapshot artifact bytes, excluding generated README | 10305456 B | Not separately summed |
| Pyodide retained memory | 116.3546 MiB | 103.8663 MiB |
| Pyodide sampled peak | 116.5819 MiB | 104.2671 MiB |
| Memory probe exit code | 0 | 0 |

The two-snapshot raw package occupies 15.3563% of Cloudflare's documented
64 MiB uncompressed Worker limit. Cloudflare documents no compressed package
limit and 128 MB of memory per isolate. These limits were checked on
2026-10-18 UTC against the
[official Worker limits](https://developers.cloudflare.com/workers/platform/limits/).
The local memory probe retains its existing 120 MiB failure threshold. The
two-snapshot run emitted its existing warning for a peak above 112 MiB.

The memory process loads the pinned Pyodide 0.28.3 runtime, with package wheels
cached by a separate process. It imports the real bundle, makes a decide
request with the current snapshot, crosses the synthetic UTC boundary, and
makes another decide request with the successor. It then exercises vocabulary,
rank, and policy-check while retaining their caches and both signed snapshots.
Its network stub raises on every attempted application fetch. The single
snapshot baseline repeats the original probe after omitting only the successor
snapshot and vocabulary blobs, then restores the fixture.

Run these commands from the repository root. Each runner waits for its children
and records their direct exit codes. The complete child commands are in
[commands.json](commands.json), [worker-dry-run.txt](worker-dry-run.txt),
[memory.txt](memory.txt), [baseline-worker-dry-run.txt](baseline-worker-dry-run.txt),
and [baseline-memory.txt](baseline-memory.txt).

```bash
env PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH /Users/terbeest/dev/modelspec/.venv/bin/python docs/evidence/g2-ios/MODEL-402/round3/measurement/run_measurements.py
env PATH=/Users/terbeest/.nvm/versions/node/v22.22.3/bin:/Users/terbeest/dev/modelspec/.venv/bin:$PATH /Users/terbeest/dev/modelspec/.venv/bin/python docs/evidence/g2-ios/MODEL-402/round3/measurement/measure_baseline.py
/Users/terbeest/dev/modelspec/.venv/bin/python docs/evidence/g2-ios/MODEL-402/round3/measurement/verify_sources.py
```

The runners, every required child command, bundle import check, both dry runs,
and both memory probes exited 0. They use an isolated ignored directory at
`api/worker/.scratch-model402-round3-measurement`. No Worker was deployed or
uploaded. The commands remove Cloudflare and snapshot environment variables
before setting the public fixture signing key, and disable Wrangler metrics.
The recorded installed command help confirms `--dry-run` and `--outdir`.
Cloudflare's
[Wrangler command reference](https://developers.cloudflare.com/workers/wrangler/commands/workers/)
also specifies that this dry run compiles without deploying to live servers.

Tool versions were Python 3.14.4 for preparation, Python 3.13.15 for the Worker
build, Node v22.22.3, npm 10.9.8, uv 0.12.19, workers-py 1.17.4,
workers-runtime-sdk 1.9.0, Wrangler 4.139.0, and Pyodide 0.28.3. Their direct
outputs are saved beside this file.

After the logs and manifests were verified, the isolated scratch directory,
including its generated bundles and dependencies, was removed. No measurement
processes remained. [cleanup.json](cleanup.json) records the cleanup; all docs
evidence, web files, the shared Python environment, and global caches were
preserved. The rerun commands recreate the isolated directory.

The private production catalogue was not available and was not measured. These
local Node and Pyodide measurements do not measure Cloudflare's live isolate
memory, startup CPU, concurrency, or deployment acceptance. The earlier
[cold-download probe](../../measurement/memory-cold-download.json) remains
recorded with exit 1 at the unchanged 120 MiB gate. It measured the earlier
`ef31a864` source, with 120.7204 MiB retained and 120.7852 MiB peak. The Round 3
cached measurements do not replace that observation.
