/** Load the complete bundled catalogue in the Worker's pinned Pyodide runtime.
 * npm install --prefix /tmp/modelspec-memory pyodide@0.28.3
 * NODE_PATH=/tmp/modelspec-memory/node_modules node api/worker/measure_memory.cjs BUNDLE
 * Use a synthetic signing key when generating the measurement bundle.
 * Prints only byte counts. No model, benchmark or price rows reach stdout.
 */
const fs = require('node:fs');
const path = require('node:path');
const { loadPyodide } = require('pyodide');

(async () => {
  const bundle = path.resolve(process.argv[2]);
  const py = await loadPyodide({ indexURL: path.dirname(require.resolve('pyodide')) + '/', packageBaseUrl: 'https://cdn.jsdelivr.net/pyodide/v0.28.3/full/', packageCacheDir: path.join(path.dirname(require.resolve('pyodide')), 'packages') });
  await py.loadPackage(['pydantic', 'pyyaml']);
  function copy(dir, target) {
    py.FS.mkdirTree(target);
    for (const name of fs.readdirSync(dir)) {
      if (name === '__pycache__') continue;
      const source = path.join(dir, name), dest = target + '/' + name;
      if (fs.statSync(source).isDirectory()) copy(source, dest);
      else py.FS.writeFile(dest, fs.readFileSync(source));
    }
  }
  copy(bundle, '/bundle');
  py.globals.set("verification_key", process.env.MODELSPEC_SNAPSHOT_KEY || "model247-memory-fixture-key");
  const before = py._module.HEAPU8.buffer.byteLength;
  await py.runPythonAsync(`
import sys, json, os, importlib
sys.path.insert(0, '/bundle')
import bundled_data
for module in ("rank_service", "policy_service", "decide_service"):
    if os.path.isfile("/bundle/" + module + ".py"):
        importlib.import_module(module)
from decision.snapshot import load_snapshot_bytes
# Retain every model, including the archive, rather than only the premier set.
snapshot = load_snapshot_bytes(bundled_data.read('/api/decision/snapshot.json.gz'),
    key=verification_key, include_archive=True)
candidates = json.loads(bundled_data.read('/api/rank/candidates.json'))
hardware = json.loads(bundled_data.read('/api/rank/hardware.json'))
policy = json.loads(bundled_data.read('/api/policy/catalogue.json'))
vocabulary = json.loads(bundled_data.read('/api/decision/vocabulary.json'))
`);
  const after = py._module.HEAPU8.buffer.byteLength;
  const usage = process.memoryUsage();
  const observed = usage.heapUsed + usage.external;
  const result = { runtime: 'Pyodide 0.28.3', before_bytes: before,
    v8_heap_and_external_bytes: observed, v8_heap_and_external_mib: observed / 1048576,
    loaded_bytes: after, loaded_mib: after / 1048576, limit_bytes: 128 * 1048576 };
  console.log(JSON.stringify(result));
  if (after > result.limit_bytes || observed > result.limit_bytes) process.exitCode = 1;
})().catch(error => { console.error('Memory probe failed:', error.name, error.message); process.exitCode = 1; });
