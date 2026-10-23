from pathlib import Path
import json
import os
import subprocess
import sys

root = Path('/tmp/model-444-scratch/probes')
engine = root/'engine-base'
data = root/'raw103'
out = root/'red'
out.mkdir(exist_ok=False)
(out/'tmp').mkdir()
env = dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONPATH=str(engine),MODELSPEC_REQUIRE_DATA_DIR='1',DATA_SPLIT_ENABLED='false',MODELSPEC_SNAPSHOT_KEY='model439-private-proof-throwaway-key',TMPDIR=str(out/'tmp'))
for key in ('MODELSPEC_SOURCE_CACHE','MODELSPEC_DATA_DIR'):
    env.pop(key,None)
record = {}
for name,command in {
    'vendor':[sys.executable,str(engine/'api/worker/vendor.py'),'--data-dir',str(data),'--out',str(out/'bundle')],
    'gate':[sys.executable,str(root/'gate.py'),str(engine),str(data),str(out)],
}.items():
    with (out/(name+'.log')).open('w') as log:
        result = subprocess.run(command,cwd=engine,env=env,stdout=log,stderr=log)
    record[name] = {'command':command,'exit_code':result.returncode}
    (out/'commands.json').write_text(json.dumps(record,indent=2)+'\n')
    print(name,'exit',result.returncode,flush=True)
print((out/'gate.public.json').read_text(),flush=True)
assert record['vendor']['exit_code']==2
assert record['gate']['exit_code']==1
assert json.loads((out/'gate.public.json').read_text())['gap_count']==113
