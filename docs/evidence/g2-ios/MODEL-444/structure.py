from pathlib import Path
import hashlib,json,subprocess
root=Path('/tmp/model-444-scratch/data')
base='ba03e11651513aa108f4031e56622717cf419acf'
engine=Path('/Users/terbeest/dev/worktrees/model-444')
def git(cwd,*args):
    return subprocess.run(['git','-C',str(cwd),*args],check=True,capture_output=True).stdout
files=git(root,'ls-tree','-r','--name-only',base).decode().splitlines()
streams=[]
for name in files:
    if name.endswith('.jsonl'):
        before=git(root,'show',f'{base}:{name}')
        after=(root/name).read_bytes()
        assert after.startswith(before),name
        streams.append({'path':name,'unchanged':after==before,'prefix_bytes':len(before)})
assert all(row['unchanged'] for row in streams)
pin=(root/'.engine-pin').read_text().strip()
git(engine,'merge-base','--is-ancestor',pin,'origin/main')
git(root,'merge-base','--is-ancestor',base,'HEAD')
print(json.dumps({'data_base':base,'engine_pin':pin,'pin_on_engine_main':True,'main_ancestor':True,'main_jsonl_streams':len(streams),'all_main_streams_byte_identical':True,'new_attempt_rows':len((root/'verification/rendered-reread-attempts.jsonl').read_text().splitlines())},indent=2))
