"""Delete all MODEL-437 acceptance scratch after public reports are copied."""
from pathlib import Path
import shutil
import sys

root = Path('/tmp/model-437-scratch/acceptance')
if sys.argv[1:] != ['--confirmed-public-evidence-copied']:
    raise SystemExit('Copy reviewed public artifacts first, then supply --confirmed-public-evidence-copied')
if root.is_symlink() or root.resolve() != Path('/private/tmp/model-437-scratch/acceptance'):
    raise SystemExit('Unexpected scratch location')
shutil.rmtree(root)
print('Removed acceptance private clone, linked repair view, exports, bundles, logs and scratch.')
