/** Real Worker phase timings under the pinned Pyodide runtime, using Node's
 * live clock. Build the public fixture with vendor.py --data-dir . and the
 * synthetic MODELSPEC_SNAPSHOT_KEY=model247-memory-fixture-key first.
 * npm install --prefix /tmp/model269-profile --no-save pyodide@0.28.3
 * NODE_PATH=/tmp/model269-profile/node_modules node api/worker/profile_decide.cjs api/worker/src [output.json] [snapshot.json.gz] [spec-or-vocabulary.json]
 * PROFILE_RUNS sets the warm samples per explanation level, default 50.
 */
const fs = require('node:fs');
const path = require('node:path');
const { performance } = require('node:perf_hooks');
const { loadPyodide } = require('pyodide');
(async () => {
  const started = performance.now();
  const py = await loadPyodide({
    indexURL: path.dirname(require.resolve('pyodide')) + '/',
    packageBaseUrl: 'https://cdn.jsdelivr.net/pyodide/v0.28.3/full/',
    packageCacheDir: path.join(path.dirname(require.resolve('pyodide')), 'packages'),
  });
  const runtimeMs = performance.now() - started;
  const packagesStarted = performance.now();
  await py.loadPackage(['pydantic', 'pyyaml']);
  const packagesMs = performance.now() - packagesStarted;
  function copy(dir, target) {
    py.FS.mkdirTree(target);
    for (const name of fs.readdirSync(dir)) {
      if (name === '__pycache__') continue;
      const source = path.join(dir, name), dest = target + '/' + name;
      if (fs.statSync(source).isDirectory()) copy(source, dest);
      else py.FS.writeFile(dest, fs.readFileSync(source));
    }
  }
  copy(path.resolve(process.argv[2]), '/bundle');
  py.FS.writeFile('/profile_decide.py', fs.readFileSync(path.join(__dirname, '../../scripts/profile_decide.py')));
  if (process.argv[4]) py.FS.writeFile('/snapshot.json.gz', fs.readFileSync(process.argv[4]));
  if (process.argv[5]) py.FS.writeFile('/spec.json', fs.readFileSync(process.argv[5]));
  py.globals.set('spec_json', process.argv[5] ? fs.readFileSync(process.argv[5], 'utf8') : null);
  py.globals.set('snapshot_path', process.argv[4] ? '/snapshot.json.gz' : null);
  py.globals.set('verification_key', process.env.MODELSPEC_SNAPSHOT_KEY || 'model247-memory-fixture-key');
  py.globals.set('runs', Number(process.env.PROFILE_RUNS || 50));
  const copyMs = performance.now() - packagesStarted - packagesMs;
  const encoded = await py.runPythonAsync(`import os, sys, json
os.environ['MODELSPEC_SNAPSHOT_KEY'] = verification_key
sys.path.insert(0, '/')
from profile_decide import profile, profile_templates
selected = json.loads(spec_json) if spec_json else None
if selected and 'templates' in selected:
    result = await profile_templates('/bundle', selected, runs=runs, snapshot_path=snapshot_path)
else:
    result = await profile('/bundle', runs=runs, snapshot_path=snapshot_path, spec=selected)
result['runtime'] = 'Pyodide 0.28.3 / Python ' + sys.version.split()[0]
json.dumps(result, indent=2)
`);
  const result = JSON.parse(encoded);
  result.startup_ms = { runtime: runtimeMs, packages: packagesMs, bundle_copy: copyMs, imports: result.imports_ms };
  const output = JSON.stringify(result, null, 2);
  if (process.argv[3]) fs.writeFileSync(process.argv[3], output + '\n');
  console.log(output);
})().catch(error => { console.error(error); process.exitCode = 1; });
