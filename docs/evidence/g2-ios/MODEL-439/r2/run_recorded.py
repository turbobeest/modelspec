import json, subprocess, sys, time
from datetime import UTC, datetime
from pathlib import Path
out=Path(__file__).resolve().parent
working=Path.cwd()
name=sys.argv[1]
command=sys.argv[2:]
started=datetime.now(UTC).isoformat();clock=time.monotonic()
log=out/(name+'.private.log')
print('Running '+name+'; log '+str(log),flush=True)
with log.open('w') as f:
    result=subprocess.run(command,cwd=working,stdout=f,stderr=f)
record={'name':name,'argv':command,'cwd':str(working),'started_at':started,'finished_at':datetime.now(UTC).isoformat(),'elapsed_seconds':round(time.monotonic()-clock,2),'exit_code':result.returncode,'log':str(log)}
with (out/'commands.jsonl').open('a') as f:f.write(json.dumps(record)+'\n')
print(json.dumps(record),flush=True)
raise SystemExit(result.returncode)
