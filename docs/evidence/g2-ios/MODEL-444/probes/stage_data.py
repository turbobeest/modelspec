from pathlib import Path
import io
import os
import subprocess
import tarfile

repo = Path('/tmp/model-444-scratch/data')
root = Path('/tmp/model-444-scratch/probes')
for name,rev in [('data-main',os.environ['MODELSPEC_EXPECTED_DATA_SHA']),('raw103','a9300cb6ce41fc2e238ccd38ff326d5e5a9700a7')]:
    target = root / name
    target.mkdir(exist_ok=False)
    try:
        archive = subprocess.run(['git','archive','--format=tar',rev],cwd=repo,capture_output=True,check=True)
    except subprocess.CalledProcessError as error:
        raise subprocess.CalledProcessError(
            error.returncode, ['git', 'archive', '--format=tar', '<revision supplied locally>'],
        ) from None
    with tarfile.open(fileobj=io.BytesIO(archive.stdout),mode='r:') as stream:
        stream.extractall(target,filter='data')
    (root / (name+'.sha')).write_text(rev+'\n')
    print(name,'staged',flush=True)
