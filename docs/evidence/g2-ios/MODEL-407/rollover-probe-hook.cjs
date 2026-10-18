'use strict';

// Public-only instrumentation for the unchanged CI probe. It never reads the
// private bundle itself. Private paths and values stay in the probe process.
const Module = require('node:module');
const path = require('node:path');
const mode = process.env.MODEL407_MEMORY_MODE;
if (!['cold', 'warm'].includes(mode)) {
  throw new Error('MODEL407_MEMORY_MODE must be cold or warm');
}
const probe = path.resolve(process.argv[1]);
const originalCompile = Module.prototype._compile;
function replaceOnce(source, needle, replacement) {
  if (source.split(needle).length !== 2) {
    throw new Error('CI memory probe instrumentation marker changed');
  }
  return source.replace(needle, replacement);
}
const setup = `from datetime import UTC, date, datetime
import weakref
import decision.snapshot as snapshot_runtime
rollover_holder = entry._decision_holder("https://modelspec.dev")
rollover_metadata = rollover_holder._bundled_successor
assert isinstance(rollover_metadata, dict), 'successor descriptor required'
rollover_date = date.fromisoformat(rollover_metadata['valid_from'])
rollover_current = weakref.ref(entry._bundled_decision_snapshot)
rollover_previous_id = entry._bundled_decision_snapshot.snapshot_id
assert rollover_previous_id != rollover_metadata['snapshot_id']
rollover_original_read = bundled_data.read
rollover_reads = 0
def rollover_read(path):
    global rollover_reads
    if path == '/api/decision/snapshot-successor.json.gz':
        assert rollover_current() is None, 'previous snapshot remains resident at successor read'
        rollover_reads += 1
    return rollover_original_read(path)
bundled_data.read = rollover_read
class BoundaryClock(datetime):
    @classmethod
    def now(cls, tz=None):
        instant = datetime.combine(rollover_date, datetime.min.time(), tzinfo=UTC)
        return instant.astimezone(tz) if tz is not None else instant.replace(tzinfo=None)
snapshot_runtime.datetime = BoundaryClock
rollover_holder._today = lambda: rollover_date
`;
const verified = `assert rollover_holder._bundle_verified
assert rollover_holder._successor_loaded
assert rollover_reads == 1
assert rollover_current() is None
assert held is rollover_holder.snapshot
assert held is rollover_holder._bundled_snapshot
assert held is entry._bundled_decision_snapshot
assert held.signature_verified
assert held.snapshot_id == rollover_metadata['snapshot_id']
assert json.loads(response.body)['snapshot'] == held.snapshot_id
assert response.headers['x-modelspec-snapshot'] == held.snapshot_id
`;
Module.prototype._compile = function instrument(source, filename) {
  if (path.resolve(filename) === probe) {
    Module.prototype._compile = originalCompile;
    const loaded = 'assert len(held._corpus_sections) == 2\n';
    if (mode === 'cold') {
      const beforeRequest = '# The real request loads and retains the complete signed corpus, including archive.\n';
      source = replaceOnce(source, beforeRequest, setup + beforeRequest);
      source = replaceOnce(source, loaded, loaded + verified);
    } else {
      source = replaceOnce(source, loaded, loaded + `record_peak()
record_stage('after_current_decide')
` + setup + `del held
response = await worker.fetch(Request('POST', '/v1/decide', {'spec_version':1, 'snapshot':'latest', 'optimize': {'max':'gpqa_diamond'}, 'limit':1, 'explain':'none'}))
assert response.status == 200
held = rollover_holder.snapshot
assert len(held._corpus_sections) == 2
` + verified);
      source = replaceOnce(source, "requests: ['POST /v1/decide', 'GET /v1/vocabulary'",
        "requests: ['POST /v1/decide (current)', 'POST /v1/decide (successor)', 'GET /v1/vocabulary'");
    }
    source = replaceOnce(source, '  const assessment = assessMemory(result, { limitMiB, baseline });',
      `  result.period = 'successor';\n  result.rollover = { mode: '${mode}', successor_loaded: true, predecessor_released_before_read: true };\n` +
      '  const assessment = assessMemory(result, { limitMiB, baseline });');
  }
  return originalCompile.call(this, source, filename);
};
