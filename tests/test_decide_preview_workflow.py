"""The decide app is added only to the internal Pages artifact."""

from pathlib import Path
import subprocess

import yaml


WORKFLOW = Path(__file__).resolve().parents[1] / '.github/workflows/deploy-sites.yml'


def workflow():
    return yaml.safe_load(WORKFLOW.read_text())


def files(root):
    return {path.relative_to(root).as_posix(): path.read_bytes()
            for path in root.rglob('*') if path.is_file()}


def test_preview_assembly_preserves_both_production_trees(tmp_path):
    fixture = {
        'dist/modelspec/index.html': b'live site',
        'dist/modelspec/api/index.json': b'{"live":true}',
        'dist/modelspec/.well-known/api-catalog': b'catalog',
        'dist/modelspec/assets/site.css': b'existing styles',
        'dist/benchgraph/_redirects': b'redirects',
        'dist-holding/modelspec/index.html': b'holding page',
        'dist-holding/modelspec/api/index.json': b'{"live":true}',
        'web/dist/index.html': b'old graph app, do not replace the site',
        'web/dist/decide.html': b'<script src="/assets/decide-abc.js"></script>',
        'web/dist/assets/decide-abc.js': b'decide bundle',
        'web/dist/assets/decide-abc.css': b'decide styles',
    }
    for name, content in fixture.items():
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    live = files(tmp_path / 'dist')
    holding = files(tmp_path / 'dist-holding')
    step = next(step for step in workflow()['jobs']['build']['steps']
                if step.get('name') == 'Assemble the internal decide preview')
    subprocess.run(['bash', '-e', '-c', step['run']], cwd=tmp_path, check=True)
    assert files(tmp_path / 'dist') == live
    assert files(tmp_path / 'dist-holding') == holding
    assert files(tmp_path / 'dist-internal') == {
        **live,
        'modelspec/decide.html': fixture['web/dist/decide.html'],
        'modelspec/assets/decide-abc.js': b'decide bundle',
        'modelspec/assets/decide-abc.css': b'decide styles',
    }


def test_preview_artifact_keeps_hidden_files_and_reaches_deploy():
    jobs = workflow()['jobs']
    upload = next(step['with'] for step in jobs['build']['steps']
                  if step.get('with', {}).get('name') == 'sites-internal')
    download = next(step['with'] for step in jobs['deploy']['steps']
                    if step.get('with', {}).get('name') == 'sites-internal')
    assert upload['path'] == download['path'] == 'dist-internal'
    assert upload['include-hidden-files'] is True
