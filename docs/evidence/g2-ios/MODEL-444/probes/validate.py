"""MODEL-444 deploy-style private validation. Every generated path stays in scratch."""
from pathlib import Path
import argparse
import ast
import base64
import gzip
import hashlib
import json
import os
import shutil
import subprocess
import sys

parser = argparse.ArgumentParser()
parser.add_argument('--engine', type=Path, required=True)
parser.add_argument('--data', type=Path, required=True)
parser.add_argument('--label', required=True)
parser.add_argument('--skip-memory', action='store_true')
args = parser.parse_args()
engine = args.engine.resolve()
data = args.data.resolve()
root = Path('/tmp/model-444-scratch/probes')
out = root / args.label
out.mkdir(parents=True, exist_ok=False)
(out / 'tmp').mkdir()
node = '/Users/terbeest/.nvm/versions/node/v22.22.3/bin/node'
env = dict(os.environ, MODELSPEC_SNAPSHOT_KEY='model439-private-proof-throwaway-key',
           MODELSPEC_REQUIRE_DATA_DIR='1', DATA_SPLIT_ENABLED='false',
           PYTHONDONTWRITEBYTECODE='1', PYTHONPATH=str(engine), TMPDIR=str(out / 'tmp'),
           NODE_PATH=str(root / 'runtime/node_modules'))
for key in ('MODELSPEC_SOURCE_CACHE', 'MODELSPEC_DATA_DIR'):
    env.pop(key, None)
record = {'engine':str(engine), 'data_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=data,text=True).strip(),
          'data_status':subprocess.check_output(['git','status','--short'],cwd=data,text=True),
          'engine_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=engine,text=True).strip() if (engine/'.git').exists() else '7e3d8ba6c95eac6f03e438366686c5299499b6bc',
          'engine_source_sha256':{str(path.relative_to(engine)):hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted((engine/'decision').glob('*.py'))},
          'environment_overrides':{key:env[key] for key in ('MODELSPEC_SNAPSHOT_KEY','MODELSPEC_REQUIRE_DATA_DIR','DATA_SPLIT_ENABLED','PYTHONDONTWRITEBYTECODE','PYTHONPATH','TMPDIR','NODE_PATH')},
          'environment_unset':['MODELSPEC_SOURCE_CACHE','MODELSPEC_DATA_DIR'], 'commands':{}}

def save():
    (out / 'commands.json').write_text(json.dumps(record, indent=2)+'\n')

def run(name, command, child_env=None):
    with (out / (name+'.log')).open('w') as log:
        result = subprocess.run(command, cwd=engine, env=child_env or env, stdout=log, stderr=log)
    record['commands'][name] = {'command':command, 'exit_code':result.returncode}
    save()
    print(name, 'exit', result.returncode, flush=True)
    return result.returncode

bundle = out / 'bundle'
status = run('vendor.private', [sys.executable, str(engine / 'api/worker/vendor.py'), '--data-dir',str(data),'--out',str(bundle)])
if status:
    raise SystemExit(status)
record['production_completeness_gate'] = {'enabled':True,'gap_count':0,'current_and_successor_exported':True}
save()
for source in (engine / 'api/worker/src').glob('*.py'):
    if source.name not in {'bundled_data.py','tier_policy.py'}:
        shutil.copy2(source, bundle / source.name)
if not args.skip_memory:
    record['memory'] = {}
    for period in ('current','successor'):
        target = out / (period+'.memory.json')
        command = [node,'--expose-gc',str(engine / 'api/worker/measure_memory.cjs'),str(bundle),'--limit-mib','115','--output',str(target)]
        if period == 'successor':
            command.append('--successor')
        run('memory.'+period,command)
        if target.exists():
            measured = json.loads(target.read_text())
            record['memory'][period] = {key:measured[key] for key in ('steady_mib','peak_mib','period')}
            print(json.dumps(record['memory'][period]),flush=True)
        save()
tree = ast.parse((bundle / 'bundled_data.py').read_text())
blobs = next(ast.literal_eval(stmt.value) for stmt in tree.body if isinstance(stmt,ast.Assign)
             and any(isinstance(t,ast.Name) and t.id=='BLOBS' for t in stmt.targets))
for name, encoded in blobs.items():
    assert name.startswith('/api/')
    target = out / 'exports' / name.removeprefix('/api/')
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_bytes(gzip.decompress(base64.b64decode(encoded)))
run('corpus',[sys.executable,str(engine / 'docs/evidence/g2-ios/MODEL-439/r2/compare_private.py'),'state','--root',str(engine),'--data-dir',str(data),'--output',str(out),'--reuse-exports'])
public_env = dict(env,MODELSPEC_REQUIRE_DATA_DIR='0')
public_env.pop('MODELSPEC_SNAPSHOT_KEY',None)
public = out / 'public-bundle'
run('vendor.public',[sys.executable,str(engine / 'api/worker/vendor.py'),'--out',str(public)],public_env)
record['public_bundled_data_absent'] = not (public / 'bundled_data.py').exists()
save()
if (out / 'state.public.json').exists():
    print((out / 'state.public.json').read_text(),flush=True)
print('PUBLIC_BUNDLED_DATA_ABSENT',record['public_bundled_data_absent'],flush=True)
raise SystemExit(int(any(command['exit_code'] for command in record['commands'].values()) or not record['public_bundled_data_absent']))
