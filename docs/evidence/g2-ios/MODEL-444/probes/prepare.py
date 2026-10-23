from pathlib import Path
import io
import json
import os
import subprocess
import tarfile

root = Path('/Users/terbeest/dev/worktrees/model-444')
out = Path('/tmp/model-444-scratch/probes')
base = '7e3d8ba6c95eac6f03e438366686c5299499b6bc'
engine = out / 'engine-base'
if not engine.exists():
    archive = subprocess.run(['git', 'archive', '--format=tar', base], cwd=root, capture_output=True, check=True)
    engine.mkdir()
    with tarfile.open(fileobj=io.BytesIO(archive.stdout), mode='r:') as stream:
        stream.extractall(engine, filter='data')
versions = {}
for name, command in {
    'python': ['/Users/terbeest/dev/modelspec/.venv/bin/python', '--version'],
    'node': ['/Users/terbeest/.nvm/versions/node/v22.22.3/bin/node', '--version'],
    'python_dependencies': ['/Users/terbeest/dev/modelspec/.venv/bin/python', '-c', 'import pydantic,yaml,httpx,cryptography; print(pydantic.__version__,yaml.__version__,httpx.__version__,cryptography.__version__)'],
    'data_head': ['git', '-C', '/tmp/model-444-scratch/data', 'rev-parse', 'HEAD'],
}.items():
    result = subprocess.run(command, text=True, capture_output=True, check=True)
    versions[name] = result.stdout.strip()
versions['engine_base'] = base
(out / 'versions.json').write_text(json.dumps(versions, indent=2)+'\n')
print(json.dumps(versions), flush=True)
env = dict(os.environ, PATH='/Users/terbeest/.nvm/versions/node/v22.22.3/bin:' + os.environ['PATH'])
command = ['/Users/terbeest/.nvm/versions/node/v22.22.3/bin/npm', 'install', '--prefix', str(out / 'runtime'), '--no-save', 'pyodide@0.28.3']
result = subprocess.run(command, cwd=out, env=env)
(out / 'runtime-install.json').write_text(json.dumps({'command':command,'exit_code':result.returncode}, indent=2)+'\n')
raise SystemExit(result.returncode)
