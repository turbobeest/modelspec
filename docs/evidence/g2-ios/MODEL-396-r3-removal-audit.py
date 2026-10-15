import importlib.util
from pathlib import Path
import subprocess
import tomllib

from decision.normalise import NORMALISERS
from decision.verify import deterministic_extractors

errors=[]
for name in ('decision/normalise.py','decision/model.py','decision/sources.py',
             'pyproject.toml','cli/modelspec/agent-bundle.json','tests/test_worker_vendor_imports.py',
             'api/worker/vendor.py','api/worker/uv.lock','api/worker/pylock.toml'):
    before=subprocess.check_output(['git','show','c9b62560:'+name])
    if Path(name).read_bytes()!=before:
        errors.append(name+' differs from the pre-PDF baseline')
for name in ('pdf_text','source_document'):
    if importlib.util.find_spec('decision.'+name) is not None:
        errors.append('offline PDF module remains: '+name)
if any(rule.content not in {'html','text','json'} for rule in NORMALISERS.values()):
    errors.append('unsupported normalization kind remains registered')
methods={extractor.actor.method for extractor in deterministic_extractors()}
if 'model-properties-output-limit@1' in methods:
    errors.append('heuristic model-properties reader remains registered')
if 'mistral-output-labels@1' not in methods:
    errors.append('Mistral output-label rule was lost')
project=tomllib.loads(Path('pyproject.toml').read_text())
if any('pypdf' in dependency for dependency in project['project']['optional-dependencies']['dev']):
    errors.append('PDF dependency remains declared')
for error in errors:
    print('FAIL:',error)
assert not errors, errors
print('PASS: only the Mistral label reader remains; PDF support and its bundle changes are absent')
