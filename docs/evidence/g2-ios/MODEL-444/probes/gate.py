"""Run the production completeness gate, reporting aggregates only."""
from pathlib import Path
import collections
from dataclasses import asdict
from datetime import datetime, UTC
import json
import os
import sys

engine,data,out = map(Path,sys.argv[1:])
sys.path.insert(0,str(engine))
from pipeline.data_source import overlay
from decision import registry,snapshot
out.mkdir(parents=True,exist_ok=True)
root = overlay(engine,data,out/'gate-root')
registry.use_root(root)
try:
    result = snapshot.build_from_repo(root,premier=root/'premier/slice-1.yaml',as_of=datetime.now(UTC).date())
except snapshot.CompletenessError as error:
    private = {'gaps':[asdict(gap) for gap in error.gaps], 'coverage':asdict(error.coverage) if error.coverage else None}
    (out/'gate.private.json').write_text(json.dumps(private,indent=2)+'\n')
    public = {'enabled':True,'gap_count':len(error.gaps),'by_facet':dict(collections.Counter(gap.facet for gap in error.gaps)),'by_reason':dict(collections.Counter(gap.reason for gap in error.gaps))}
    status = 1
else:
    public = {'enabled':True,'gap_count':0,'snapshot_id':result.snapshot_id}
    status = 0
(out/'gate.public.json').write_text(json.dumps(public,indent=2)+'\n')
print(json.dumps(public,indent=2))
raise SystemExit(status)
