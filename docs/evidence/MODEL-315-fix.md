# MODEL-315 execution evidence

Base SHA: `5dd0eb5a16637d254c23f2903a5b97fb134ef9c3`.
Branch: `model-315-agy-spike`.
The submitted head SHA is recorded in the PR body and executor completion line.

## Environment

Observed 2026-11-09 on Docker Desktop's Linux ARM64 engine.
Docker client/server 29.9.1; Docker Desktop 4.96.0; Buildx v0.38.0;
Python 3.14.4; pytest 9.1.1; git 2.50.1; GitHub CLI 2.103.3.

## Red-first checks

These are disposable Docker behavior probes, not changes to production code.
The digest-pinned harness base image was already local. No network, login or
model request is needed by these probes.

```sh
env SPIKE_IMAGE=node:22.20.0-bookworm-slim@sha256:b21fe589dfbe5cc39365d0544b9be3f1f33f55f3c86c87a76ff65a02f8f5848e /Users/terbeest/dev/modelspec/.venv/bin/python /tmp/MODEL-315-scratch/executor/probe.py
env SPIKE_IMAGE=node:22.20.0-bookworm-slim@sha256:b21fe589dfbe5cc39365d0544b9be3f1f33f55f3c86c87a76ff65a02f8f5848e /Users/terbeest/dev/modelspec/.venv/bin/python /tmp/MODEL-315-scratch/executor/probe-restart.py
```

Both processes exited 1, checked directly. The version assertion was tightened
from any semantic version to the manifest-resolved 1.5.3 before the green run.
The download page had advertised 1.5.2; the observed release manifest was newer.

| Probe | Red result |
| --- | --- |
| `test_cli_reports_pinned_version_without_network` | Exit 1; the base's Node entrypoint reports `Cannot find module '/agy'`. |
| `test_headless_keyring_round_trip_without_network` | Exit 127; `secret-tool: not found`. |
| `test_secret_survives_fresh_container_and_not_an_unmounted_home` | Exit 127; `secret-tool: not found`. The test's `finally` removed its dummy volume. |

## Offline regressions

```sh
env PYTHONPATH=$PWD /Users/terbeest/dev/modelspec/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_removed_sources.py tests/test_tui_harness.py tests/test_tui_auth_grok.py
```

Exit 0. `651 passed, 1 skipped in 62.20s`. This is serial and invokes no
subscription model. After staging both final documents, the same command
restricted to `tests/test_removed_sources.py` exited 0 again with
`46 passed, 1 skipped in 53.29s`. The full CI suite was not run locally.

## Runtime evidence

Both Docker builds exited 0 through the required machine-wide `heavy.sh` lock.
The first build downloaded and printed the installer inside `RUN`; it did not
execute it. Public release metadata was fetched by a separate named container.
The second build used the manifest's fixed archive URL and verified SHA-512.
The built CLI printed `1.5.3` in a `RUN --network=none` step.

- Archive SHA-256: `2d50060c7b1327995e5c81ec58829c91c2564ebb9fec165d3f9f1325ec188675`.
- Binary SHA-256: `bc4ddea9d28bec7e0b9887bee841500a267ac5762ee36f5cdd894c487bf2eb8e`.
- Inspector image ID: `sha256:08e6bed64d5c4782bbe0be70a886538597425e7c1a90edc1c60aed3eb26a7e43`.
- CLI image ID: `sha256:908dcfa5e00801e13a4dbbf2feaed938e5c14ea5639245f123d9e9d4781d808c`.
- Image-reported sizes before removal: 630893015 and 938024687 bytes respectively.
- Container packages: D-Bus `1.14.10-1~deb12u1`, GNOME Keyring `42.1-1+b2`,
  libsecret-tools `0.20.5-3`, Python `3.11.2-1+b1`.

Green commands, each checked directly for exit 0:

```sh
env SPIKE_IMAGE=modelspec-model-315-spike /Users/terbeest/dev/modelspec/.venv/bin/python /tmp/MODEL-315-scratch/executor/probe.py
env SPIKE_IMAGE=modelspec-model-315-spike /Users/terbeest/dev/modelspec/.venv/bin/python /tmp/MODEL-315-scratch/executor/probe-restart.py
```

The same three named probes passed: `Ran 2 tests in 0.396s / OK`, then
`Ran 1 test in 0.561s / OK`. The final probes also require empty stderr.
An earlier run passed with a D-Bus runtime-directory warning. Mounting the
private runtime tmpfs before D-Bus started removed that warning. The first
keyring-only successes were also measured on the inspector image before the
CLI installation.

The interactive command below reached the unsigned-in login-method menu.
No selection or other input was sent except two Ctrl-C presses, which exited
0. The first Ctrl-C asked for a second press. Networking was disabled and the
image set `BROWSER=/bin/false`.

```sh
docker run --rm -it --name modelspec-model-315-login --network=none --cap-drop=ALL --security-opt=no-new-privileges --tmpfs /tmp/model315-runtime:rw,uid=1001,gid=1001,mode=700 --env TERM=xterm-256color modelspec-model-315-spike agy
```

Observed screen text:

```text
Welcome to the Antigravity CLI. You are currently not signed in.
Select login method:
> 1. Google OAuth
  2. Use a Google Cloud project
```

`agy --help` also exited 0 without networking and listed print mode, structured
output, MCP and ACP controls. No print prompt, ACP session or scenario was run.

Exact help and package-metadata commands:

```sh
docker run --rm --name modelspec-model-315-help --network=none --cap-drop=ALL --security-opt=no-new-privileges modelspec-model-315-spike agy --help

docker run --rm --name modelspec-model-315-metadata --network=none --cap-drop=ALL --security-opt=no-new-privileges --entrypoint python3 modelspec-model-315-spike -c 'import json, pathlib, subprocess; print(pathlib.Path("/opt/model315/artifact.json").read_text()); print(subprocess.check_output(["dpkg-query", "-W", "dbus", "gnome-keyring", "libsecret-tools", "python3"], text=True))'
```

Both exited 0. The help invocation preceded the tmpfs correction and also
printed the missing-runtime-directory warning. The metadata command bypassed
the session entrypoint and read only build metadata and package versions.
The final three probe definitions were rerun against the unchanged base image
and still produced all three expected failures before cleanup.


## Reproduce the disposable experiment

Recreate the files below in `/tmp/MODEL-315-scratch/executor`, outside the repo.
These are the executed scratch artifacts. They are evidence, not a registered
provider or an account-login tool. The empty keyring password is dummy-only.
The Debian package versions were observed, not repository-snapshot pinned;
only the base digest and CLI archive/checksum are pinned by this recipe.

```sh
mkdir -p /tmp/MODEL-315-scratch/executor
/Users/terbeest/.codex-g2/heavy.sh docker build --progress plain --tag modelspec-model-315-inspect --file /tmp/MODEL-315-scratch/executor/Dockerfile.inspect /tmp/MODEL-315-scratch/executor

docker run --rm --name modelspec-model-315-manifest --cap-drop=ALL --security-opt=no-new-privileges --entrypoint python3 modelspec-model-315-inspect -c 'import urllib.request; print(urllib.request.urlopen("https://antigravity-cli-auto-updater-974169037036.us-central1.run.app/manifests/linux_arm64.json", timeout=30).read().decode())'

/Users/terbeest/.codex-g2/heavy.sh docker build --progress plain --tag modelspec-model-315-spike --file /tmp/MODEL-315-scratch/executor/Dockerfile.spike /tmp/MODEL-315-scratch/executor
```

The web tool could not fetch that manifest URL. The named Docker fetch above
succeeded and supplied the version, URL and checksum; the failed web request
is not the provenance for those values. A later manifest may resolve to a
newer release. The recorded second Dockerfile deliberately keeps 1.5.3.


### Dockerfile.inspect

```dockerfile
FROM node:22.20.0-bookworm-slim@sha256:b21fe589dfbe5cc39365d0544b9be3f1f33f55f3c86c87a76ff65a02f8f5848e
RUN apt-get update && apt-get install -y --no-install-recommends python3 ca-certificates dbus gnome-keyring libsecret-tools && rm -rf /var/lib/apt/lists/*
RUN python3 - <<'PY'
import hashlib, urllib.request
with urllib.request.urlopen('https://antigravity.google/cli/install.sh', timeout=60) as r:
    body=r.read()
print('INSTALLER_SHA256', hashlib.sha256(body).hexdigest())
print(body.decode())
PY
RUN useradd --create-home --uid 1001 --shell /bin/bash agent && mkdir /work && chown agent:agent /work
COPY session.sh /opt/model315/session.sh
ENV HOME=/home/agent XDG_CONFIG_HOME=/home/agent/.config XDG_DATA_HOME=/home/agent/.local/share XDG_CACHE_HOME=/home/agent/.cache XDG_RUNTIME_DIR=/tmp/model315-runtime AGY_CLI_DISABLE_AUTO_UPDATE=true BROWSER=/bin/false
USER agent
WORKDIR /work
ENTRYPOINT ["dbus-run-session", "--", "sh", "/opt/model315/session.sh"]
```

### session.sh

```sh
#!/bin/sh
set -eu
umask 077
mkdir -p "$XDG_RUNTIME_DIR" "$XDG_DATA_HOME/keyrings"
# Dummy-only experiment: an empty unlock password is not a production policy.
printf '\n' | gnome-keyring-daemon --unlock --components=secrets >/dev/null
exec "$@"
```

### Dockerfile.spike

```dockerfile
FROM modelspec-model-315-inspect
USER root
RUN python3 - <<'FETCH'
import hashlib, io, json, tarfile, urllib.request
from pathlib import Path
metadata = {'version': '1.5.3', 'url': 'https://storage.googleapis.com/antigravity-public/antigravity-cli/1.5.3-6604829099950080/linux-arm/cli_linux_arm64.tar.gz', 'sha512': 'c2fac818b3c1bb224079df03a714ccba99728b6a3a41d86d247ab2feb8582a43840c5032f1c2b75e72667623d5503e7ffda2712c4f37b6ee19f99c3fcfb25bae'}
with urllib.request.urlopen(metadata['url'], timeout=120) as response:
    payload = response.read()
assert hashlib.sha512(payload).hexdigest() == metadata['sha512'], 'archive checksum mismatch'
with tarfile.open(fileobj=io.BytesIO(payload), mode='r:gz') as archive:
    member = archive.getmember('antigravity')
    assert member.isfile()
    binary = archive.extractfile(member).read()
path = Path('/usr/local/bin/agy')
path.write_bytes(binary)
path.chmod(0o755)
metadata['archive_sha256'] = hashlib.sha256(payload).hexdigest()
metadata['binary_sha256'] = hashlib.sha256(binary).hexdigest()
Path('/opt/model315/artifact.json').write_text(json.dumps(metadata, indent=2))
print(json.dumps(metadata, indent=2))
FETCH
RUN --network=none agy --version
USER agent
```

### probe.py

```python
"""No-login behavioral probes. Run against a base image first, then the spike."""
import os
import subprocess
import unittest

IMAGE = os.environ.get('SPIKE_IMAGE', 'modelspec-model-315-inspect')

class SpikeProbe(unittest.TestCase):
    def run_container(self, *command):
        return subprocess.run([
            'docker', 'run', '--rm', '--name', 'modelspec-model-315-probe', '--network=none', '--cap-drop=ALL',
            '--security-opt=no-new-privileges', '--tmpfs', '/tmp/model315-runtime:rw,uid=1001,gid=1001,mode=700', IMAGE, *command,
        ], capture_output=True, text=True, timeout=30)

    def test_cli_reports_pinned_version_without_network(self):
        result = self.run_container('agy', '--version')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertRegex(result.stdout, r'\b1\.5\.3\b')

    def test_headless_keyring_round_trip_without_network(self):
        result = self.run_container('sh', '-ec',
            'printf model315-dummy | secret-tool store --label=MODEL-315 ticket MODEL-315; '
            'secret-tool lookup ticket MODEL-315')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertEqual(result.stdout.strip(), 'model315-dummy')

if __name__ == '__main__':
    unittest.main(verbosity=2)
```

### probe-restart.py

```python
"""Fresh-process persistence test; owns only its MODEL-315 dummy volume."""
import os
import subprocess
import unittest

IMAGE = os.environ.get('SPIKE_IMAGE', 'modelspec-model-315-inspect')
VOLUME = 'modelspec-model-315-dummy-auth'

class RestartProbe(unittest.TestCase):
    def command(self, args):
        result = subprocess.run(args, capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        return result.stdout.strip()

    def test_secret_survives_fresh_container_and_not_an_unmounted_home(self):
        # Reject a preexisting volume so this test cannot touch another run's data.
        exists = subprocess.run(['docker', 'volume', 'inspect', VOLUME], capture_output=True)
        self.assertNotEqual(exists.returncode, 0, 'Test volume already exists; refusing reuse')
        self.command(['docker', 'volume', 'create', VOLUME])
        base = ['docker', 'run', '--rm', '--name', 'modelspec-model-315-restart', '--network=none', '--cap-drop=ALL',
                '--security-opt=no-new-privileges', '--tmpfs', '/tmp/model315-runtime:rw,uid=1001,gid=1001,mode=700']
        mounted = base + ['--mount', f'type=volume,source={VOLUME},target=/home/agent', IMAGE]
        try:
            self.command(mounted + ['sh', '-ec',
                'printf model315-dummy | secret-tool store --label=MODEL-315 ticket MODEL-315'])
            self.assertEqual(self.command(mounted + ['secret-tool', 'lookup', 'ticket', 'MODEL-315']),
                             'model315-dummy')
            result = subprocess.run(base + [IMAGE, 'secret-tool', 'lookup', 'ticket', 'MODEL-315'],
                                    capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertEqual(result.stdout, '')
        finally:
            self.command(['docker', 'volume', 'rm', VOLUME])

if __name__ == '__main__':
    unittest.main(verbosity=2)
```

### scan-image.py

```python
"""Scan saved image layers, including compressed OCI blobs, for the test value."""
import gzip
import json
import subprocess
import tarfile

marker = b'model315-dummy'
result = subprocess.run(['docker', 'image', 'inspect', 'modelspec-model-315-spike',
    '--format', '{{.Id}}'], check=True, capture_output=True, text=True)
print('image_id', result.stdout.strip())
count = 0
with tarfile.open('/tmp/MODEL-315-scratch/executor/image.tar', 'r') as archive:
    for member in archive:
        if not member.isfile():
            continue
        with archive.extractfile(member) as raw:
            head = raw.read(2)
            raw.seek(0)
            stream = gzip.GzipFile(fileobj=raw) if head == b'\x1f\x8b' else raw
            tail = b''
            while chunk := stream.read(1024 * 1024):
                assert marker not in tail + chunk, 'dummy secret found in image: ' + member.name
                tail = chunk[-len(marker):]
            count += 1
print(json.dumps({'saved_image_files_scanned': count, 'dummy_secret_hits': 0}))
```

## Saved-image check and cleanup

```sh
docker image save --output /tmp/MODEL-315-scratch/executor/image.tar modelspec-model-315-spike
/Users/terbeest/dev/modelspec/.venv/bin/python /tmp/MODEL-315-scratch/executor/scan-image.py
docker image rm modelspec-model-315-spike modelspec-model-315-inspect
docker ps -a --filter name=modelspec-model-315 --format '{{.Names}}'
docker volume ls --filter name=modelspec-model-315 --format '{{.Name}}'
docker image ls --filter reference='modelspec-model-315-*' --format '{{.Repository}}:{{.Tag}}'
```

Image save, scan and image removal exited 0. Scan result:
`{"saved_image_files_scanned": 19, "dummy_secret_hits": 0}`.
This checks the saved image's files and decoded gzip layers for the known dummy
bytes, not every possible representation of future credentials.

Containers created, all removed: `modelspec-model-315-probe`,
`modelspec-model-315-restart`, `modelspec-model-315-manifest`,
`modelspec-model-315-help`, `modelspec-model-315-login`,
`modelspec-model-315-metadata`. Probe containers reuse their names sequentially
and use `--rm`. The dummy volume `modelspec-model-315-dummy-auth` was created
only after an absence check and removed in the restart test's `finally` block,
including the red run. No other auth volume was mounted or inspected.

Both ticket image tags and image IDs were removed. Existing images and the
shared builder cache remain; global cache pruning would affect concurrent
jobs. The saved image and `/tmp/MODEL-315-scratch` are deleted at completion.
No background process from this experiment remains.

## Not observed

No real Google login, real-token persistence/refresh, account entitlement,
post-selection OAuth flow, model turn, quota behavior, native subscription
status, effective customization inventory, isolation certification or AMD64
execution was observed. Permission for the QA integration remains unverified.
The technical successes do not establish any of those facts. No provider
adapter, production switch, schedule, frozen data or existing test was changed.

## Publication record

The final submitted SHA is the branch HEAD recorded in the draft PR body and
executor completion line. It can be reproduced with `git rev-parse HEAD` after
checking out that PR's head; embedding this document's own commit hash inside
it would change the hash. Publication used:

```sh
git diff --cached --check
CI_LOCAL_SKIP=1 git push -u origin model-315-agy-spike
```

The draft PR uses the exact ticket title, base `main`, head
`model-315-agy-spike`, and the ModelSpec executor footer. No merge or readiness
change is part of this task.
