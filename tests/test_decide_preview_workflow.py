"""The live and internal Pages artifacts are the same decide composition."""

from pathlib import Path
import subprocess
import sys

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pipeline import brand  # noqa: E402


WORKFLOW = Path(__file__).resolve().parents[1] / '.github/workflows/deploy-sites.yml'


def workflow():
    return yaml.safe_load(WORKFLOW.read_text())


def files(root):
    return {path.relative_to(root).as_posix(): path.read_bytes()
            for path in root.rglob('*') if path.is_file()}


def test_live_assembly_matches_internal_and_preserves_holding_byte_for_byte(tmp_path):
    fixture = {
        'dist/modelspec/index.html': b'v1 landing',
        'dist/modelspec/api/index.json': b'{"live":true}',
        'dist/modelspec/.well-known/api-catalog': b'catalog',
        'dist/modelspec/legal/terms/index.html': b'terms',
        'dist/modelspec/legal/privacy/index.html': b'privacy',
        'dist/modelspec/legal/neutrality/index.html': b'neutrality',
        'dist/modelspec/openapi.yaml': b'openapi',
        'dist/modelspec/downselect/index.html': b'v1 wizard',
        'dist/modelspec/models/index.html': b'v1 rankings',
        'dist/modelspec/m/lab/model/index.html': b'unverified model page',
        'dist/modelspec/pricing/index.html': b'v1 pricing',
        'dist/benchgraph/_redirects': b'redirects',
        'dist-holding/modelspec/index.html': b'holding page',
        'dist-holding/modelspec/api/index.json': b'{"live":true}',
        'dist-holding/modelspec/legal/terms/index.html': b'terms',
        'web/dist/index.html': b'old graph app, do not replace the site',
        'web/dist/decide.html': b'<script src="/assets/decide-abc.js"></script>',
        'web/dist/assets/decide-abc.js': b'decide bundle',
        'web/dist/assets/decide-abc.css': b'decide styles',
        'web/dist/assets/main-old.js': b'old graph bundle, harmless but unreachable',
        'web/dist/favicon.svg': b'old graph app icon',
        **{f'dist/modelspec/{name}': f'2a {name}'.encode() for name in brand.FILES},
    }
    for name, content in fixture.items():
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    holding = files(tmp_path / 'dist-holding')
    step = next(step for step in workflow()['jobs']['build']['steps']
                if step.get('name') == 'Assemble the live and internal decide sites')
    subprocess.run(['bash', '-e', '-c', step['run']], cwd=tmp_path, check=True)
    assert files(tmp_path / 'dist-holding') == holding
    assert files(tmp_path / 'dist-internal') == files(tmp_path / 'dist')
    live = files(tmp_path / 'dist')
    assert live['modelspec/index.html'] == fixture['web/dist/decide.html']
    assert live['modelspec/404.html'] == fixture['web/dist/decide.html']
    assert live['modelspec/api/index.json'] == fixture['dist/modelspec/api/index.json']
    assert live['modelspec/legal/terms/index.html'] == b'terms'
    assert live['modelspec/openapi.yaml'] == b'openapi'
    assert live['modelspec/.well-known/api-catalog'] == b'catalog'
    assert live['modelspec/assets/decide-abc.js'] == b'decide bundle'
    assert 'modelspec/assets/main-old.js' not in live
    assert 'modelspec/favicon.svg' not in live
    for name in brand.FILES:
        assert live[f'modelspec/{name}'] == f'2a {name}'.encode(), name
    for removed in ('downselect', 'models', 'm', 'pricing'):
        assert not (tmp_path / 'dist' / 'modelspec' / removed).exists()


def test_live_workflow_keeps_api_and_legal_but_has_no_v1_navigation():
    text = WORKFLOW.read_text(encoding='utf-8')
    assert 'cp -a dist-v1/modelspec/api dist/modelspec/api' in text
    assert 'cp -a dist-v1/modelspec/legal dist/modelspec/legal' in text
    assert 'cmp -s' not in text  # compare full trees, not one representative file
    assert 'diff -r dist dist-internal' in text
    for old_path in ('downselect', 'models', 'providers', 'benchmarks', 'graph', 'pricing'):
        assert f'test -s dist/modelspec/{old_path}' not in text
        assert f'test ! -e dist/modelspec/{old_path}' in text


def test_preview_artifact_keeps_hidden_files_and_reaches_deploy():
    jobs = workflow()['jobs']
    upload = next(step['with'] for step in jobs['build']['steps']
                  if step.get('with', {}).get('name') == 'sites-internal')
    download = next(step['with'] for step in jobs['deploy']['steps']
                    if step.get('with', {}).get('name') == 'sites-internal')
    assert upload['path'] == download['path'] == 'dist-internal'
    assert upload['include-hidden-files'] is True


def test_live_mode_deploys_the_composed_dist_and_internal_deploys_its_identical_copy():
    jobs = workflow()['jobs']
    run = next(step['run'] for step in jobs['build']['steps']
               if step.get('name') == 'Build the holding trees, and pick what production gets')
    assert 'if [ "$mode" = "live" ]; then production=dist;' in run
    deploy = jobs['deploy']['steps']
    commands = [step.get('with', {}).get('command', '') for step in deploy]
    assert any('needs.build.outputs.production' in command and '--branch=main' in command
               for command in commands)
    assert any('pages deploy dist-internal/modelspec' in command and '--branch=internal' in command
               for command in commands)


def test_the_live_composition_copies_exactly_the_brand_icon_set():
    step = next(step for step in workflow()['jobs']['build']['steps']
                if step.get('name') == 'Assemble the live and internal decide sites')
    assert f"for icon in {' '.join(brand.FILES)}; do" in step['run']
    checks = next(step for step in workflow()['jobs']['build']['steps']
                  if step.get('name') == 'Check the pages we promise actually exist')
    for name in brand.FILES:
        assert f'test -s dist/modelspec/{name}' in checks['run'], name
