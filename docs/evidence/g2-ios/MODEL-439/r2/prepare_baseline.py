"""Archive pinned acceptance inputs and copy the adjacent reproduction helpers."""
import argparse
from datetime import UTC,datetime
import io
import json
from pathlib import Path
import shutil
import subprocess
import tarfile


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo',type=Path,required=True)
    parser.add_argument('--data-dir',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--main-ref',default='36b2d184dcc5a67a90ceb1a9015275143c09691d')
    parser.add_argument('--data-ref',default='9d9de96f062ac031336ee483ae97c3b436bd3845')
    parser.add_argument('--policy-ref',default='82ebcf4627d255d7641303caff2d149e879cf359')
    args=parser.parse_args()
    out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
    commands=[]
    def git(root,*options):
        command=['git','-C',str(root),*options]
        result=subprocess.run(command,capture_output=True)
        commands.append({'argv':command,'exit_code':result.returncode})
        result.check_returncode()
        return result.stdout
    refs={'main':git(args.repo,'rev-parse',args.main_ref).decode().strip(),'baseline_data':git(args.data_dir,'rev-parse',args.data_ref).decode().strip(),'policy':git(args.repo,'rev-parse',args.policy_ref).decode().strip()}
    for source,rev,destination in [(args.repo,refs['main'],out/'main'),(args.data_dir,refs['baseline_data'],out/'baseline-data')]:
        destination.mkdir(exist_ok=False)
        with tarfile.open(fileobj=io.BytesIO(git(source,'archive',rev))) as archive:
            archive.extractall(destination,filter='data')
    (out/'hosts-866.json').write_bytes(git(args.repo,'show',refs['policy']+':registry/source-retention.json'))
    helpers=Path(__file__).resolve().parent
    for name in ['compare_private.py','check_completeness.py','diagnose_assurance.py','scope_assurance.py','run_recorded.py']:
        if helpers/name != out/name:shutil.copy2(helpers/name,out/name)
    (out/'prepare.commands.public.json').write_text(json.dumps(commands,indent=2)+'\n')
    identities={'revisions':refs,'prepared_at':datetime.now(UTC).isoformat()}
    (out/'identities.public.json').write_text(json.dumps(identities,indent=2)+'\n')
    print(json.dumps(identities))
    return 0

if __name__=='__main__':raise SystemExit(main())
