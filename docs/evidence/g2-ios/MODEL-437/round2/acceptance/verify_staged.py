"""Match the staged public engine sources to the measured implementation commit."""
from pathlib import Path
import hashlib
import io
import json
import subprocess
import tarfile

repo = Path('/Users/terbeest/dev/worktrees/model-437')
proof = Path('/tmp/model-437-scratch/acceptance')
revision = '6b9695fc75748bf31d8f07955bbf8fea89fc57f0'
raw = subprocess.run([
    'git', '-C', str(repo), 'archive', revision, 'decision', 'pipeline',
    'api/worker', 'cli', 'schema', 'tests/corpus', 'registry',
], check=True, capture_output=True).stdout
with tarfile.open(fileobj=io.BytesIO(raw)) as archive:
    entries = {member.name: archive.extractfile(member).read()
               for member in archive.getmembers()
               if member.isfile() and member.name != 'registry/source-retention.json'}
report = {}
for label in ('c', 'd'):
    code = proof / 'results' / label / 'code'
    differs = [name for name, content in entries.items()
               if not (code / name).exists() or (code / name).read_bytes() != content]
    digest = hashlib.sha256()
    for name, content in sorted(entries.items()):
        digest.update(name.encode() + b'\0' + content + b'\0')
    report[label] = dict(implementation_commit=revision, compared_files=len(entries),
                         matches_commit_except_intentional_policy=not differs,
                         different_files=differs, source_digest=digest.hexdigest())
(proof / 'staged-code.public.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
raise SystemExit(int(any(row['different_files'] for row in report.values())))
