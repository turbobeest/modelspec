"""The live and internal Pages artifacts are the same decide composition."""

import os
from pathlib import Path
import subprocess
import sys

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pipeline import brand, live as live_site, social_cards, structured_data  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / '.github/workflows/deploy-sites.yml'
DECIDE = Path(__file__).resolve().parents[1] / 'web' / 'decide.html'


def workflow():
    return yaml.safe_load(WORKFLOW.read_text())


def files(root):
    return {path.relative_to(root).as_posix(): path.read_bytes()
            for path in root.rglob('*') if path.is_file()}


def test_live_assembly_matches_internal_and_preserves_holding_byte_for_byte(tmp_path):
    fixture = {
        'dist/modelspec/index.html': b'<link rel="canonical" href="https://modelspec.dev/">landing',
        'dist/modelspec/api/index.json': b'{"live":true,"count":1}',
        'dist/modelspec/api/build.json': b'{"built_at":"2026-09-29T00:00:00+00:00","export_schema_version":"3.0"}',
        'dist/modelspec/.well-known/api-catalog': b'catalog',
        'dist/modelspec/.well-known/mcp.json': b'{}',
        'dist/modelspec/.well-known/agent-skills/index.json': b'{}',
        'dist/modelspec/.well-known/agent-skills/modelspec/SKILL.md': b'skill',
        'dist/modelspec/llms.txt': b'- https://modelspec.dev/auth.md\n',
        'dist/modelspec/llms-full.txt': b'v1 digest',
        'dist/modelspec/index.md': b'# ModelSpec',
        'dist/modelspec/auth.md': b'# Auth.md',
        'dist/modelspec/agents.md': b'# ModelSpec agent guide',
        'dist/modelspec/_headers': b'/*\n  Link: </llms.txt>; rel="describedby"\n',
        'dist/modelspec/legal/terms/index.html': b'terms',
        'dist/modelspec/legal/privacy/index.html': b'privacy',
        'dist/modelspec/legal/neutrality/index.html': b'neutrality',
        'dist/modelspec/openapi.yaml': b'openapi',
        'dist/modelspec/downselect/index.html': b'v1 wizard',
        'dist/modelspec/models/index.html': b'v1 rankings',
        'dist/modelspec/m/lab/model/index.html': b'unverified model page',
        'dist/modelspec/pricing/index.html': b'v1 pricing',
        'dist/modelspec/method/index.html': b'v1 method',
        'dist/modelspec/graph/index.html': b'<link rel="canonical" href="https://modelspec.dev/graph/">graph',
        'dist/modelspec/graph/vendor/three.min.js': b'three',
        'dist/modelspec/graph/vendor/3d-force-graph.min.js': b'force graph',
        'dist/modelspec/pricing-assets/pricing.css': b'pricing styles',
        'dist/modelspec/pricing-assets/pricing.js': b'pricing script',
        'dist/modelspec/landing-assets/landing.css': b'landing styles',
        'dist/modelspec/landing-assets/landing.js': b'landing script',
        'dist/modelspec/fonts/instrument-sans-latin-wdth-normal.woff2': b'instrument font',
        'dist/modelspec/feedback/index.html': b'feedback page',
        'dist/modelspec/feedback-assets/feedback.js': b'feedback control',
        'dist/modelspec/brand/index.html': b'brand kit page',
        'dist/benchgraph/_redirects': b'redirects',
        'dist-holding/modelspec/index.html': b'holding page',
        'dist-holding/modelspec/api/index.json': b'{"live":true,"count":1}',
        'dist-holding/modelspec/legal/terms/index.html': b'terms',
        'web/dist/index.html': b'old graph app, do not replace the site',
        # As Vite writes it: the source entry becomes the hashed bundle.
        'web/dist/decide.html': DECIDE.read_bytes().replace(b'/src/decide/main.tsx', b'/assets/decide-abc.js'),
        'web/dist/assets/decide-abc.js': b'decide bundle',
        'web/dist/assets/decide-abc.css': b'decide styles',
        'web/dist/assets/main-old.js': b'old graph bundle, harmless but unreachable',
        'web/dist/favicon.svg': b'old graph app icon',
        **{f'dist/modelspec/{name}': f'2a {name}'.encode() for name in brand.FILES},
        'dist/modelspec/og-card-landing.png': b'landing card',
        'dist/modelspec/og-card-decide.png': b'decide card',
        'dist/modelspec/og-card-pricing.png': b'pricing card',
    }
    for name, content in fixture.items():
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    holding = files(tmp_path / 'dist-holding')
    step = next(step for step in workflow()['jobs']['build']['steps']
                if step.get('name') == 'Assemble the live and internal decide sites')
    env = {**os.environ, 'PYTHONPATH': str(ROOT)}
    subprocess.run(['bash', '-e', '-c', step['run']], cwd=tmp_path, check=True, env=env)
    assert files(tmp_path / 'dist-holding') == holding
    assert files(tmp_path / 'dist-internal') == files(tmp_path / 'dist')
    live = files(tmp_path / 'dist')
    # Pages are copied unchanged apart from the JSON-LD block (MODEL-218).
    page = lambda rel: structured_data.strip(live[rel].decode()).encode()
    assert page('modelspec/index.html') == fixture['dist/modelspec/index.html']
    assert page('modelspec/decide/index.html') == fixture['web/dist/decide.html']
    assert b'noindex' in live['modelspec/404.html']
    index = live['modelspec/index.html'].decode()
    decide = live['modelspec/decide/index.html'].decode()
    headers = live['modelspec/_headers'].decode()
    assert '<link rel="canonical" href="https://modelspec.dev/">' in index
    assert '<link rel="canonical" href="https://modelspec.dev/decide/" />' in decide
    assert 'noindex' not in index.lower()
    assert 'x-robots-tag' not in headers.lower()
    assert headers.startswith('/*\n  Link: </llms.txt>; rel="describedby"\n')
    for name in ('llms.txt', 'index.md', 'auth.md'):
        assert live[f'modelspec/{name}'] == fixture[f'dist/modelspec/{name}'], name
    assert live['modelspec/api/index.json'] == fixture['dist/modelspec/api/index.json']
    assert page('modelspec/legal/terms/index.html') == b'terms'
    assert page('modelspec/pricing/index.html') == b'v1 pricing'
    assert page('modelspec/method/index.html') == b'v1 method'
    assert live['modelspec/pricing-assets/pricing.js'] == b'pricing script'
    assert live['modelspec/openapi.yaml'] == b'openapi'
    assert live['modelspec/.well-known/api-catalog'] == b'catalog'
    assert live['modelspec/assets/decide-abc.js'] == b'decide bundle'
    assert 'modelspec/assets/main-old.js' not in live
    assert 'modelspec/favicon.svg' not in live
    assert live['modelspec/_redirects'].decode() == live_site.REDIRECTS
    assert 'modelspec/landing/index.html' not in live
    for name in brand.FILES:
        assert live[f'modelspec/{name}'] == f'2a {name}'.encode(), name
    assert live['modelspec/og-card-landing.png'] == b'landing card'
    assert live['modelspec/og-card-decide.png'] == b'decide card'
    assert live['modelspec/og-card-pricing.png'] == b'pricing card'
    # MODEL-251: the v1 build may still hold a graph or a digest; live never does.
    assert 'modelspec/llms-full.txt' not in live
    for removed in ('downselect', 'models', 'm', 'graph'):
        assert not (tmp_path / 'dist' / 'modelspec' / removed).exists()
    # MODEL-221: the feedback page and its control, in the sitemap.
    assert page('modelspec/feedback/index.html') == b'feedback page'
    assert live['modelspec/feedback-assets/feedback.js'] == b'feedback control'
    assert b'/feedback/' in live['modelspec/sitemap.xml']


def test_live_workflow_keeps_api_legal_and_pricing():
    text = WORKFLOW.read_text(encoding='utf-8')
    assert 'python -m pipeline.live build --src dist-v1 --web web/dist --out dist' in text
    for kept in ('api', 'legal', 'pricing', 'pricing-assets', '.well-known'):
        assert kept in live_site.KEEP_DIRS, kept
    assert 'graph' not in live_site.KEEP_DIRS
    assert 'cmp -s' not in text  # compare full trees, not one representative file
    assert 'diff -r dist dist-internal' in text
    assert 'test ! -e dist/modelspec/graph' in text
    assert "grep -Fq '/graph/*  /  301' dist/modelspec/_redirects" in text
    for old_path in ('downselect', 'models', 'providers', 'benchmarks'):
        assert f'test -s dist/modelspec/{old_path}' not in text
        assert f'test ! -e dist/modelspec/{old_path}' in text
    assert 'test -s dist/modelspec/pricing/index.html' in text


def test_build_job_installs_chromium_before_python_renders_cards():
    steps = workflow()['jobs']['build']['steps']
    web_build = next(step['run'] for step in steps if step.get('name') == 'Build the decide app')
    assert 'npx playwright install --with-deps chromium' in web_build
    assert next(index for index, step in enumerate(steps)
                if step.get('name') == 'Build the decide app') < next(
                    index for index, step in enumerate(steps) if step.get('name') == 'Build')


def test_live_build_checks_canonical_and_indexability():
    checks = next(step['run'] for step in workflow()['jobs']['build']['steps']
                  if step.get('name') == 'Check the pages we promise actually exist')
    assert "grep -Fq '<link rel=\"canonical\" href=\"https://modelspec.dev/\"'" in checks
    assert "grep -Fq '<link rel=\"canonical\" href=\"https://modelspec.dev/decide/\"'" in checks
    assert "grep -Fq '<link rel=\"canonical\" href=\"https://modelspec.dev/pricing/\"'" in checks
    assert "if grep -Eiq '<meta[^>]+noindex'" in checks
    assert "if grep -Fiq 'X-Robots-Tag'" in checks


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
    assert set(brand.FILES) <= set(live_site.KEEP_FILES)
    checks = next(step for step in workflow()['jobs']['build']['steps']
                  if step.get('name') == 'Check the pages we promise actually exist')
    for name in brand.FILES:
        assert f'test -s dist/modelspec/{name}' in checks['run'], name
    assert 'for card in $(python -m pipeline.social_cards filenames); do test -s dist/modelspec/$card; done' in checks['run']


def test_the_deploy_build_renders_the_social_cards():
    build = next(step for step in workflow()['jobs']['build']['steps']
                 if step.get('id') == 'build')
    assert build['env'][social_cards.RENDER_ENV] == '1'
    assert 'pipeline.build' in build['run']
    assert 'continue-on-error' not in build
