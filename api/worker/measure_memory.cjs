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
  let peak = 0, wasmPeak = before;
  const recordPeak = () => {
    const usage = process.memoryUsage();
    peak = Math.max(peak, usage.heapUsed + usage.external);
    wasmPeak = Math.max(wasmPeak, py._module.HEAPU8.buffer.byteLength);
  };
  py.globals.set('record_peak', recordPeak);
  const sampling = setInterval(recordPeak, 5);
  try {
    await py.runPythonAsync(`import sys, json, types
sys.path.insert(0, '/bundle')
async def no_network(*args, **kwargs):
    raise AssertionError('bundle probe attempted a network request')
class Response:
    def __init__(self, body, status=200, headers=None):
        self.body, self.status, self.headers = body, status, headers or {}
class Headers(dict):
    def get(self, key, default=None):
        return super().get(key.lower(), default)
class Request:
    def __init__(self, method, path, payload=None):
        self.method, self.url = method, 'https://api.modelspec.dev' + path
        self.headers = Headers({'origin': 'https://modelspec.dev'})
        self.payload = json.dumps(payload) if payload else ''
    async def text(self):
        return self.payload
sys.modules['js'] = types.SimpleNamespace(fetch=no_network)
sys.modules['workers'] = types.SimpleNamespace(Response=Response, WorkerEntrypoint=type('WorkerEntrypoint', (), {}))
import bundled_data, entry
worker = entry.Default()
worker.env = types.SimpleNamespace(MODELSPEC_SNAPSHOT_KEY=verification_key, BUILD_COMMIT='memory-probe')
# The real request loads and retains the complete signed corpus, including archive.
response = await worker.fetch(Request('POST', '/v1/decide', {'spec_version':1, 'snapshot':'latest', 'optimize': {'max':'gpqa_diamond'}, 'limit':1, 'explain':'none'}))
assert response.status == 200
held = entry._decision_holder("https://modelspec.dev").snapshot
assert len(held._corpus_sections) == 2
record_peak()
response = await worker.fetch(Request('GET', '/v1/vocabulary'))
assert response.status == 200
record_peak()
`);
  } finally {
    clearInterval(sampling);
  }
  recordPeak();
  const result = { runtime: 'Pyodide 0.28.3', before_bytes: before,
    peak_bytes: peak, peak_mib: peak / 1048576,
    wasm_peak_bytes: wasmPeak, wasm_peak_mib: wasmPeak / 1048576,
    requests: ['POST /v1/decide', 'GET /v1/vocabulary'], limit_bytes: 112 * 1048576 };
  console.log(JSON.stringify(result));
  if (peak > result.limit_bytes || wasmPeak > result.limit_bytes) process.exitCode = 1;
})().catch(error => { console.error('Memory probe failed:', error.name); process.exitCode = 1; });
