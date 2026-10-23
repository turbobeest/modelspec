from pathlib import Path
import io
import subprocess
import tarfile

repo = Path('/tmp/model-444-scratch/data')
root = Path('/tmp/model-444-scratch/probes')
for name,rev in [('data-main','ba03e11651513aa108f4031e56622717cf419acf'),('raw103','a9300cb6ce41fc2e238ccd38ff326d5e5a9700a7')]:
    target = root / name
    target.mkdir(exist_ok=False)
    archive = subprocess.run(['git','archive','--format=tar',rev],cwd=repo,capture_output=True,check=True)
    with tarfile.open(fileobj=io.BytesIO(archive.stdout),mode='r:') as stream:
        stream.extractall(target,filter='data')
    (root / (name+'.sha')).write_text(rev+'\n')
    print(name,rev,flush=True)
