/** Load the complete bundled catalogue in the Worker's pinned Pyodide runtime.
 * npm install --prefix /tmp/modelspec-memory pyodide@0.28.3
 * NODE_PATH=/tmp/modelspec-memory/node_modules node --expose-gc api/worker/measure_memory.cjs BUNDLE
 * Use a synthetic signing key when generating the measurement bundle.
 * Prints only byte counts. No model, benchmark or price rows reach stdout.
 */
const fs = require('node:fs');
const path = require('node:path');

function assessMemory(result, { limitMiB = 120, baseline = null } = {}) {
  if (!Number.isFinite(result.steady_bytes) || result.steady_bytes <= 0) {
    throw new Error('probe result has no valid steady memory count');
  }
  if (!Number.isFinite(limitMiB) || limitMiB <= 0 || limitMiB > 120) {
    throw new Error('memory limit must be positive and cannot exceed 120 MiB');
  }
  const period = result.period ?? 'current';
  if (!['current', 'successor'].includes(period)) throw new Error('invalid memory probe period');
  const warnings = [];
  if (baseline !== null) {
    if (!Number.isFinite(baseline.steady_bytes) || baseline.steady_bytes <= 0) {
      throw new Error('baseline has no valid steady memory count');
    }
    if ((baseline.period ?? 'current') !== period) {
      throw new Error('memory baseline period does not match the probe period');
    }
    if (result.steady_bytes - baseline.steady_bytes > 1048576) {
      warnings.push(`Steady memory increased by more than 1 MiB versus main (${((result.steady_bytes - baseline.steady_bytes) / 1048576).toFixed(2)} MiB)`);
    }
  }
  return { passed: result.steady_bytes <= limitMiB * 1048576, warnings };
}

async function main() {
  const { parseArgs } = require('node:util');
  const { values, positionals } = parseArgs({ allowPositionals: true, options: {
    'limit-mib': { type: 'string', default: '120' },
    baseline: { type: 'string' }, output: { type: 'string' },
    attribute: { type: 'boolean', default: false },
    successor: { type: 'boolean', default: false },
    'measure-only': { type: 'boolean', default: false },
  } });
  if (positionals.length !== 1) throw new Error('provide one Worker bundle directory');
  const limitMiB = Number(values['limit-mib']);
  const period = values.successor ? 'successor' : 'current';
  const baseline = values.baseline ? JSON.parse(fs.readFileSync(values.baseline, 'utf8')) : null;
  assessMemory({ steady_bytes: 1, period }, { limitMiB, baseline });
  const { loadPyodide } = require('pyodide');
  const bundle = path.resolve(positionals[0]);
  const py = await loadPyodide({ indexURL: path.dirname(require.resolve('pyodide')) + '/', packageBaseUrl: 'https://cdn.jsdelivr.net/pyodide/v0.28.3/full/', packageCacheDir: path.join(path.dirname(require.resolve('pyodide')), 'packages') });
  await py.loadPackage(['pydantic', 'pyyaml']);
  function copy(dir, target) {
    py.FS.mkdirTree(target);
    for (const name of fs.readdirSync(dir)) {
      if (name === '__pycache__') continue;
      const source = path.join(dir, name), dest = target + '/' + name;
      if (fs.statSync(source).isDirectory()) copy(source, dest);
      // Transfer the buffer into MEMFS instead of retaining a second file copy.
      else py.FS.writeFile(dest, fs.readFileSync(source), { canOwn: true });
    }
  }
  copy(bundle, '/bundle');
  py.globals.set("verification_key", process.env.MODELSPEC_SNAPSHOT_KEY || "model247-memory-fixture-key");
  py.globals.set('probe_successor', values.successor);
  if (!global.gc) throw new Error('probe requires --expose-gc');
  // Package/runtime setup precedes the Worker measurement. Release its
  // unreachable V8 temporaries before sampling imports and real requests.
  // Do not collect between those requests: all Worker caches remain resident.
  global.gc();
  const before = py._module.HEAPU8.buffer.byteLength;
  let peak = 0, wasmPeak = before;
  const stages = [];
  const recordPeak = () => {
    const usage = process.memoryUsage();
    peak = Math.max(peak, usage.heapUsed + usage.external);
    wasmPeak = Math.max(wasmPeak, py._module.HEAPU8.buffer.byteLength);
  };
  py.globals.set('record_peak', recordPeak);
  py.globals.set('record_stage', name => {
    const usage = process.memoryUsage();
    stages.push({ name, bytes: usage.heapUsed + usage.external,
      wasm_bytes: py._module.HEAPU8.buffer.byteLength });
  });
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
record_stage('before_worker_import')
import bundled_data, entry
record_stage('after_worker_import')
worker = entry.Default()
worker.env = types.SimpleNamespace(MODELSPEC_SNAPSHOT_KEY=verification_key, BUILD_COMMIT='memory-probe')
if probe_successor:
    from datetime import UTC, datetime
    import decision.snapshot as snapshot_runtime
    probe_boundary = entry._bundled_decision_snapshot.valid_until
    assert probe_boundary is not None, 'successor probe requires a bounded current snapshot'
    probe_previous_id = entry._bundled_decision_snapshot.snapshot_id
    class BoundaryClock(datetime):
        @classmethod
        def now(cls, tz=None):
            instant = datetime.combine(probe_boundary, datetime.min.time(), tzinfo=UTC)
            return instant.astimezone(tz) if tz is not None else instant.replace(tzinfo=None)
    snapshot_runtime.datetime = BoundaryClock
    entry._decision_holder("https://modelspec.dev")._today = lambda: probe_boundary
# The real request loads and retains the complete signed corpus, including archive.
response = await worker.fetch(Request('POST', '/v1/decide', {'spec_version':1, 'snapshot':'latest', 'optimize': {'max':'gpqa_diamond'}, 'limit':1, 'explain':'none'}))
assert response.status == 200
held = entry._decision_holder("https://modelspec.dev").snapshot
assert len(held._corpus_sections) == 2
if probe_successor:
    assert held.snapshot_id != probe_previous_id, 'successor probe still serves the current period'
    assert held.signature_verified
    assert json.loads(response.body)['snapshot'] == held.snapshot_id
    assert response.headers['x-modelspec-snapshot'] == held.snapshot_id
record_peak()
record_stage('after_decide')
response = await worker.fetch(Request('GET', '/v1/vocabulary'))
assert response.status == 200
if probe_successor:
    assert json.loads(response.body)['snapshot'] == held.snapshot_id
record_peak()
record_stage('after_vocabulary')
response = await worker.fetch(Request('POST', '/v1/rank', {'use_case': 'coding', 'limit': 100}))
assert response.status == 200
assert json.loads(response.body)['result']
record_peak()
record_stage('after_rank')
response = await worker.fetch(Request('POST', '/v1/policy-check', {'policy': {'commercial_use': {'required': True}}}))
assert response.status == 200
assert entry._policy_cache['catalogue'] is not None
record_peak()
record_stage('after_policy_check')
`);
  } finally {
    clearInterval(sampling);
  }
  recordPeak();
  // One collection after all requests gives the retained V8 memory. Wasm
  // allocation is counted in full; Node reports that buffer in external.
  global.gc();
  const live = process.memoryUsage();
  const wasm = py._module.HEAPU8.buffer.byteLength;
  const liveNonWasm = live.heapUsed + Math.max(0, live.external - wasm);
  const steady = wasm + liveNonWasm;
  const result = { runtime: 'Pyodide 0.28.3', period, before_bytes: before,
    peak_bytes: peak, peak_mib: peak / 1048576,
    wasm_peak_bytes: wasmPeak, wasm_peak_mib: wasmPeak / 1048576,
    steady_bytes: steady, steady_mib: steady / 1048576,
    live_non_wasm_bytes: liveNonWasm, wasm_bytes: wasm,
    requests: ['POST /v1/decide', 'GET /v1/vocabulary', 'POST /v1/rank', 'POST /v1/policy-check'], limit_bytes: limitMiB * 1048576, peak_warning_bytes: 112 * 1048576, stages };
  if (values.attribute) {
    // This traversal allocates bookkeeping memory, so run it only after the
    // gate sample. Category sizes overlap and describe Python objects, not RSS.
    result.attribution = JSON.parse(await py.runPythonAsync(`
def deep_bytes(value, seen=None):
    seen = set() if seen is None else seen
    identity = id(value)
    if identity in seen:
        return 0
    seen.add(identity)
    size = sys.getsizeof(value)
    if isinstance(value, dict):
        return size + sum(deep_bytes(k, seen) + deep_bytes(v, seen) for k, v in value.items())
    if isinstance(value, (list, tuple, set, frozenset)):
        return size + sum(deep_bytes(v, seen) for v in value)
    return size
snapshots = [value for value in (held, getattr(entry, '_bundled_decision_successor', None)) if value is not None]
details = []
for snapshot in snapshots:
    table = snapshot._record_table or {}
    fields = table.get('fields', [])
    verification_positions = {position for row in table.get('rows', {}).values()
                              for field, position in zip(fields, row)
                              if field and field[0] == 'verification' and position is not None}
    details.append({
        'snapshot_index_bytes': deep_bytes(vars(snapshot)),
        'provenance_table_bytes': deep_bytes(table),
        'provenance_fields': len(fields),
        'provenance_rows': len(table.get('rows', {})),
        'provenance_slots': sum(len(row) for row in table.get('rows', {}).values()),
        'verification_value_bytes': sum(sys.getsizeof(table['values'][i]) for i in verification_positions),
        'sources_bytes': deep_bytes(snapshot._sources),
        'hardware_fit_bytes': deep_bytes(getattr(snapshot, '_hardware_fit', None)),
        'hardware_provenance_bytes': deep_bytes(getattr(snapshot, '_hardware_fit_record_table', None)),
    })
json.dumps({'snapshots': details, 'vocabulary_bytes': deep_bytes([
    getattr(entry, '_bundled_vocabulary', None), getattr(entry, '_bundled_vocabulary_text', None),
    getattr(entry, '_bundled_successor_vocabulary', None), getattr(entry, '_bundled_successor_vocabulary_text', None),
])})
`));
  }
  const assessment = assessMemory(result, { limitMiB, baseline });
  if (values.output) fs.writeFileSync(values.output, JSON.stringify(result) + '\n');
  if (process.env.GITHUB_STEP_SUMMARY) {
    fs.appendFileSync(process.env.GITHUB_STEP_SUMMARY,
      `${values.output ? path.basename(values.output) : 'Worker'} (${period}): ${result.steady_mib.toFixed(2)} MiB steady; limit ${limitMiB} MiB.\n\n`);
  }
  console.log(JSON.stringify(result));
  if (peak > result.peak_warning_bytes) console.warn('::warning::Memory probe noisy peak exceeds 112 MiB');
  for (const warning of assessment.warnings) console.warn(`::warning::${warning}`);
  if (!assessment.passed && !values['measure-only']) {
    console.error(`::error::Steady memory exceeds ${limitMiB} MiB`);
    process.exitCode = 1;
  }
}

module.exports = { assessMemory };
if (require.main === module) {
  main().catch(error => { console.error('Memory probe failed:', error.name); process.exitCode = 1; });
}
