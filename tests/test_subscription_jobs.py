"""Offline MODEL-309 job contracts. Models, browser transport, credentials and PRs are mocked."""
from __future__ import annotations

import copy
import json
import os
import plistlib
import shutil
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
import yaml

from qa import agent_harness, subscription_aeo as aeo, subscription_jobs as jobs, subscription_ux as ux
from qa import tui_harness as harness, tui_homes as homes, tui_isolation as isolation, tui_providers as providers
from qa.docker.entrypoint import VENDOR_ENV
from qa.install_subscription_jobs import render, TEMPLATES, main as install
from scripts.aeo.engines import Answer


@pytest.fixture(autouse=True)
def subscription_environment(monkeypatch):
    # Tests never inherit the calling agent's credential environment or CI flag.
    for name in tuple(os.environ):
        if VENDOR_ENV.search(name) and not name.startswith('MODELSPEC_'):
            monkeypatch.delenv(name)
    monkeypatch.delenv('GITHUB_ACTIONS', raising=False)


@pytest.fixture
def config(tmp_path):
    return jobs.configuration(tmp_path, max_runs=400)


def ready(clis=providers.CLIS):
    return {c: {'verified': True, 'supported': True, 'reason': None} for c in clis}


def execution(answer='Visitor answer', status='completed'):
    return providers.Execution(providers.Transcript(final_answer=answer, terminal=True, tokens_in=12,
                                                   tokens_out=3, cost_usd=0.2), 0, 25, status)


@pytest.mark.parametrize('cli', providers.CLIS)
@pytest.mark.parametrize('purpose', ['scenario', 'judge', 'browser', 'search'])
def test_commands_select_only_the_requested_tools(cli, purpose, config, tmp_path):
    if purpose == 'browser':
        config['_mcp_servers'] = ux.PLAYWRIGHT_SERVER
    mcp = tmp_path / 'mcp.json'
    mcp.write_text(homes.home_config(cli, config, enabled=purpose in ('scenario', 'browser')))
    command = providers.build_command(cli, config['clis'][cli], tmp_path, 'private query', mcp, 8, purpose=purpose)
    if cli == 'claude':
        allowed = command[command.index('--allowedTools') + 1]
        assert allowed == ('WebSearch,WebFetch' if purpose == 'search' else 'mcp__playwright__*' if purpose == 'browser' else 'mcp__modelspec__*')
        assert command[command.index('--tools') + 1] == ('WebSearch,WebFetch' if purpose == 'search' else '')
    if cli == 'codex':
        assert ('web_search="live"' if purpose == 'search' else 'web_search="disabled"') in command
        assert 'forced_login_method="chatgpt"' in command
    if cli == 'grok':
        assert ('--disable-web-search' in command) == (purpose != 'search')
        assert command[command.index('--tools') + 1] == ('web_search,web_fetch,x_search' if purpose == 'search' else '')
    if purpose == 'browser':
        assert 'ux-mcp.mjs' in mcp.read_text()
        assert 'MODELSPEC_API_KEY' not in mcp.read_text()


@pytest.mark.parametrize('job', ['scenarios', 'ux', 'aeo'])
@pytest.mark.parametrize('name', ['OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'GEMINI_API_KEY', 'XAI_API_KEY'])
def test_every_job_refuses_even_empty_vendor_keys_before_any_work(job, name, tmp_path, monkeypatch):
    monkeypatch.setenv(name, '')
    monkeypatch.setattr(jobs, 'report_worktree', lambda *a: pytest.fail('git mutation'))
    assert jobs.main([job, '--dry-run', '--state-dir', str(tmp_path)]) == 2
    assert not (tmp_path / 'dry-run').exists()


def test_ci_is_refused(config, tmp_path, monkeypatch):
    monkeypatch.setenv('GITHUB_ACTIONS', 'true')
    assert jobs.main(['scenarios', '--dry-run', '--state-dir', str(tmp_path)]) == 2


@pytest.mark.parametrize('stamp', [None, 'bad', '2026-01-01T00:00:00', '2026-01-01T00:00:00+00:00', '2026-12-01T00:00:00+00:00'])
def test_missing_stale_and_future_receipts_do_not_query_auth(stamp, config, tmp_path, monkeypatch):
    if stamp is not None:
        isolation.receipt_file(homes.state_directory('codex', config)).write_text(json.dumps({'certified_at': stamp}))
    monkeypatch.setattr(jobs, 'authentication_status', lambda *a: pytest.fail('auth before valid receipt'))
    monkeypatch.setattr(jobs, 'isolation_result', lambda *a: pytest.fail('image before date check'))
    with pytest.raises(ValueError, match='missing or stale'):
        jobs.require_ready(config, ['codex'], tmp_path, now=datetime(2026, 10, 4, tzinfo=timezone.utc))


@pytest.mark.parametrize('auth', [{'verified': False, 'logged_in': True}, {'verified': True, 'logged_in': False}])
def test_all_receipts_and_subscription_logins_precede_tasks(auth, config, tmp_path, monkeypatch):
    for cli in ('codex', 'claude'):
        isolation.receipt_file(homes.state_directory(cli, config)).write_text(json.dumps({'certified_at': datetime.now(timezone.utc).isoformat()}))
    monkeypatch.setattr(jobs, 'isolation_result', lambda *a: ready()['codex'])
    queried = []
    def status(cli, *a):
        queried.append(cli)
        return {'verified': True, 'logged_in': True} if cli == 'codex' else auth
    monkeypatch.setattr(jobs, 'authentication_status', status)
    with pytest.raises(ValueError, match='subscription login required'):
        jobs.require_ready(config, ['codex', 'claude'], tmp_path)
    assert queried == ['codex', 'claude']


def test_weekly_scenario_report_retains_api_contract_and_labels(config, tmp_path, monkeypatch):
    scenarios = [agent_harness.load_scenarios()[0]]
    monkeypatch.setattr(jobs, 'require_ready', lambda *a: ready())
    seen = []
    verdict = {'passed': True, 'rationale': 'Evidence', 'answer_kind': 'abstain', 'top_models': [], 'missing_capabilities': []}
    def launch(cli, config, workspace, prompt, *, mcp_enabled, **kwargs):
        seen.append((cli, mcp_enabled))
        return execution('Visitor answer' if mcp_enabled else json.dumps(verdict))
    monkeypatch.setattr(harness, 'launch', launch)
    report = jobs.scenario_report(config, ['codex', 'grok'], scenarios, tmp_path, day='2026-10-04')
    old = json.loads((harness.HERE / 'reports/2026-10-01-agent-scenarios.json').read_text())
    assert set(old) <= report.keys()
    assert set(old['overall']) == set(report['overall'])
    assert set(old['runs'][0]) <= report['runs'][0].keys() | {'provider_error'}
    assert report['per_agent'].keys() == {'openai', 'grok'}
    assert seen == [('codex', True), ('claude', False), ('grok', True), ('claude', False)]
    assert report['runs'][0]['judges'][0]['cli'] == 'claude'
    assert report['budget']['estimated_spend_usd'] == 0
    assert report['metadata']['cli_invocations']['claude']['judge'] == 2
    jobs.write_pair(tmp_path / 'reports/agent-scenarios', '2026-10-04', report, agent_harness.markdown(report))
    assert (tmp_path / 'reports/agent-scenarios/2026-10-04.json').is_file()


@pytest.mark.parametrize('job', ['scenarios', 'ux', 'aeo'])
def test_report_publication_uses_scoped_paths_and_a_private_pr(job, tmp_path, monkeypatch):
    commands = []
    def run(command, **kwargs):
        commands.append(command)
        if command[0] == 'gh':
            body = Path(command[command.index('--body-file') + 1]).read_text()
            assert body == 'Aggregate only\n'
        return subprocess.CompletedProcess(command, 0, 'https://github.com/report/1\n', '')
    monkeypatch.setattr(jobs.subprocess, 'run', run)
    assert jobs.publish(tmp_path, job, 'qa/test', '2026-10-04', 'Aggregate only\n').startswith('https:')
    assert commands[0][-3:] == ['add', '--', jobs.REPORT_PATHS[job]]
    assert jobs.TRAILER in commands[1][-1]
    assert commands[2][-4:] == ['push', '-u', 'origin', 'qa/test']
    assert commands[-1][commands[-1].index('--repo') + 1] == jobs.REPOSITORIES[job]


def test_worktree_created_from_origin_main_and_kept_on_failure(tmp_path, monkeypatch):
    calls = []
    def git(repo, *args):
        calls.append(args)
        return 'https://github.com/turbobeest/modelspec-data.git' if args[0] == 'remote' else ''
    monkeypatch.setattr(jobs, 'git_command', git)
    with pytest.raises(RuntimeError):
        with jobs.report_worktree(tmp_path, 'ux', '2026-10-04', tmp_path):
            raise RuntimeError('PR failed')
    assert ('fetch', 'origin', 'main') in calls
    assert any(a[:2] == ('worktree', 'add') and a[-1] == 'origin/main' for a in calls)
    assert not any(a[:2] == ('worktree', 'remove') for a in calls)


def aeo_files(tmp_path, config):
    settings = {'monthly_cap_usd': 15, 'max_output_tokens': 2000, 'engines': {
        n: {'transport': 'subscription', 'cli': c, 'model': config['clis'][c]['model']} for n,c in aeo.ENGINE_CLIS.items()}}
    settings['engines']['perplexity'] = dict(model='sonar', key='op://test/sonar/credential', price_in=1, price_out=1, search_fee=0, est_call_usd=.007)
    path = tmp_path / 'engines.yaml'; path.write_text(yaml.safe_dump(settings))
    return path


def test_aeo_never_reads_four_vendor_keys_and_keeps_perplexity_adapter(config, tmp_path, monkeypatch):
    settings = aeo_files(tmp_path, config)
    prompts = [{'id': 'test', 'text': 'Choose a model', 'cluster': 'category', 'success': 'mentioned'}]
    monkeypatch.setattr(aeo.inventory, 'load', lambda p: prompts)
    monkeypatch.setattr(aeo, 'require_ready', lambda *a: ready())
    calls = []
    def launch(cli, cfg, workspace, prompt, **kw):
        calls.append((cli, kw['purpose']))
        result = execution('Use [ModelSpec](https://modelspec.dev/method/).')
        result.transcript.other_tool_calls = [{'name': next(n for n in providers.SEARCH_TOOLS[cli] if n not in {'WebFetch', 'web_fetch'}), 'arguments': {'query': 'choose'}, 'result_observed': True, 'result': {'isError': False}}]
        return result
    monkeypatch.setattr(harness, 'launch', launch)
    read = []
    monkeypatch.setattr(aeo.engines, 'op_read', lambda ref: read.append(ref) or 'dummy')
    monkeypatch.setattr(aeo.engines, 'perplexity_call', lambda model, secret, prompt, cap: Answer('ModelSpec', 'sonar', reported_cost_usd=.007))
    for name in aeo.ENGINE_CLIS:
        monkeypatch.setitem(aeo.engines.CALLS, name, lambda *a: pytest.fail('API fallback'))
    aeo.run(tmp_path / 'prompts.yaml', settings, tmp_path / 'runs', tmp_path, config, '2026-10-04')
    rows = [json.loads(l) for l in (tmp_path / 'runs/2026-10-04/runs.jsonl').read_text().splitlines()]
    assert len(rows) == 5 and sum(r['cost_usd'] for r in rows) == .007
    assert read == ['op://test/sonar/credential']
    assert calls == [(c, 'search') for c in aeo.ENGINE_CLIS.values()]
    assert all({'prompt_id','engine','surface','usage','cost_usd','detection','citations','searched','raw_blob_ref'} <= r.keys() for r in rows)
    assert rows[0]['surface'] == 'subscription-cli' and rows[-1]['surface'] == 'api'
    assert 'subscription CLIs' in (tmp_path / 'runs/2026-10-04/report.md').read_text()
    assert (tmp_path / 'runs/BASELINE').read_text() == '2026-10-04\n'


def test_search_claim_without_native_evidence_fails():
    with pytest.raises(ValueError, match='native web-search evidence'):
        aeo.answer_from_execution('codex', execution('I searched the web'))


@pytest.mark.parametrize('dry_run', [False, True])
def test_aeo_failed_searches_and_previews_keep_subscription_transport(config, tmp_path, monkeypatch, dry_run):
    settings = aeo_files(tmp_path, config)
    prompts = [{'id': 'test', 'text': 'Choose a model', 'cluster': 'category', 'success': 'mentioned'}]
    monkeypatch.setattr(aeo.inventory, 'load', lambda p: prompts)
    monkeypatch.setattr(aeo, 'require_ready', lambda *a: ready())
    monkeypatch.setattr(harness, 'launch', lambda *a, **kw: execution('I searched'))
    monkeypatch.setattr(aeo, 'preview', lambda *a, **kw: [])
    monkeypatch.setattr(aeo.engines, 'op_read', lambda ref: 'dummy')
    monkeypatch.setattr(aeo.engines, 'perplexity_call', lambda *a: Answer('ModelSpec', 'sonar'))
    output = tmp_path / 'runs'
    aeo.run(tmp_path / 'prompts.yaml', settings, output, tmp_path, config, '2026-10-04', dry_run=dry_run)
    rows = [json.loads(line) for line in (output / '2026-10-04/runs.jsonl').read_text().splitlines()]
    assert len(rows) == 5
    assert all(row['surface'] == 'subscription-cli' and 'error' in row for row in rows[:4])
    assert rows[-1]['surface'] == 'api'
    assert json.loads((output / '2026-10-04/summary.json').read_text())['surface'] == 'mixed'


def test_gemini_inventory_allows_only_the_configured_servers_notices():
    from qa.tui_inventory import gemini_skill_listing
    notice = "Server 'playwright' supports tool updates. Listening for changes..."
    unknown = "Server 'unapproved' supports tool updates. Listening for changes..."
    listing = notice + '\n' + unknown + '\nNo skills available'
    assert gemini_skill_listing(listing, ['playwright']) == unknown + '\nNo skills available'
    assert notice in gemini_skill_listing(listing)


def test_api_configuration_cannot_authorize_a_live_aeo_run(config, tmp_path):
    path = aeo_files(tmp_path, config)
    settings = yaml.safe_load(path.read_text()); settings['engines']['openai']['key'] = 'op://test/no'
    path.write_text(yaml.safe_dump(settings))
    with pytest.raises(ValueError, match='subscription transport'):
        aeo.engine_config(path, config)


@pytest.fixture
def private_ux(tmp_path):
    source = Path('/Users/terbeest/dev/modelspec-data/qa/ux')
    if not source.exists():
        pytest.skip('Private UX helper/report contract integration runs on the operator Mac')
    repo = tmp_path / 'private'; target = repo / 'qa/ux'; target.mkdir(parents=True)
    for name in ('core.py', 'reports.py', 'dom.js', 'run_ux_agents.py'):
        shutil.copyfile(source / name, target / name)
    tasks = [{'id': f'task-{i}', 'persona': 'Visitor', 'goal': 'Choose a model', 'success_criteria': ['An answer is visible'], 'checks': [{'kind':'selector','selector':'#answer'}]} for i in range(20)]
    (target / 'tasks.yaml').write_text(yaml.safe_dump({'version':1, 'tasks':tasks}))
    return repo, tasks


def test_ux_uses_private_catalogue_and_same_report_schema(config, private_ux, tmp_path, monkeypatch):
    repo, tasks = private_ux
    monkeypatch.setattr(ux, 'require_ready', lambda *a: ready())
    def attempt(repository, output, artifact, state, runner, task, cli, *args):
        assert repository == repo and task['success_criteria'] == ['An answer is visible']
        row = ux.result_for(task, cli); row.update(status='success', success=True)
        return row
    monkeypatch.setattr(ux, 'attempt', attempt)
    output = tmp_path / 'reports/ux'
    ux.run(repo, output, tmp_path, config, ['codex','grok'], 'https://modelspec.dev/decide/', '2026-10-04')
    report = json.loads((output / '2026-10-04.json').read_text())
    assert report['schema_version'] == 1 and report['drivers'] == ['openai','grok']
    assert len(report['results']) == 40
    assert {'date','started_at','base_url','drivers','models','spend_cap_usd','charged_usd','pricing_checked','limits','results','aggregation'} <= report.keys()
    assert {'task_id','persona','goal','success_criteria','driver','viewport','status','success','steps','confusion_points','findings','screenshots','checks','judge','wall_time_s','charged_usd','usage'} == report['results'][0].keys()
    assert {'tickets','overlap','by_driver'} == report['aggregation'].keys()


def test_ux_driver_claim_cannot_override_dom_checks(config, private_ux, tmp_path, monkeypatch):
    repo, tasks = private_ux
    runner = harness.Runner(config, tmp_path, ready())
    observed = []
    def launch(cli, cfg, workspace, prompt, *, mcp_enabled, **kwargs):
        observed.append((cli, mcp_enabled, prompt))
        if mcp_enabled:
            assert cfg['_mcp_servers'] == ux.PLAYWRIGHT_SERVER
            assert 'success_criteria' not in prompt and '#answer' not in prompt
            directory = workspace / 'evidence'; directory.mkdir()
            (directory/'shot.png').write_bytes(b'fake PNG')
            evidence = {'states':[{'records':[]}], 'steps':[], 'screenshots':['evidence/shot.png'],
                        'checks':[{'kind':'selector','selector':'#answer','passed':False}],
                        'lookups':{'requests':0,'events':[],'blocked':None}}
            (directory/'evidence.json').write_text(json.dumps(evidence))
            return execution('I succeeded')
        assert cfg['_judge_images']
        verdict = {'success':True,'criteria':[{'criterion':'An answer is visible','passed':True,'evidence':'Claim'}],
                   'rationale':'Claim','confusion_points':[], 'findings':[]}
        return execution(json.dumps(verdict))
    monkeypatch.setattr(harness, 'launch', launch)
    core, _ = ux.private_modules(repo)
    row = ux.attempt(repo, tmp_path, tmp_path/'artifacts', tmp_path, runner, tasks[0], 'codex', 'https://modelspec.dev/decide/', ux.judge_rubric(repo), core)
    assert row['status'] == 'failed' and row['success'] is False
    assert [(c,m) for c,m,_ in observed] == [('codex',True),('claude',False)]


def test_dry_run_scenarios_never_launch_or_publish(config, tmp_path, monkeypatch):
    monkeypatch.setattr(jobs, 'require_ready', lambda *a: pytest.fail('doctor/auth'))
    monkeypatch.setattr(harness, 'launch', lambda *a, **k: pytest.fail('CLI'))
    monkeypatch.setattr(jobs, 'publish', lambda *a: pytest.fail('PR'))
    assert jobs.main(['scenarios','--dry-run','--cli','codex','--scenario','budget-approved','--state-dir',str(tmp_path)]) == 0
    report = json.loads((tmp_path/'dry-run/scenarios/reports/agent-scenarios'/f'{datetime.now(timezone.utc).date()}.json').read_text())
    assert report['runs'][0]['status'] == 'dry_run' and report['overall']['success_rate'] == 0


def test_templates_keep_calendar_cadence_and_installer_never_loads(tmp_path, monkeypatch):
    monkeypatch.setattr(subprocess, 'run', lambda *a, **k: pytest.fail('launchctl called'))
    calendars = []
    for template in TEMPLATES.glob('*.plist'):
        value = render(template, Path('/tmp/engine & repo'), Path('/tmp/private'), tmp_path)
        calendars.append(value['StartCalendarInterval'])
        assert '--scheduled' in value['ProgramArguments']
        assert 'KeepAlive' not in value and 'RunAtLoad' not in value
    assert {'Weekday':2,'Hour':3,'Minute':23} in calendars
    assert {'Weekday':3,'Hour':4,'Minute':37} in calendars
    assert {'Day':1,'Hour':6,'Minute':0} in calendars
    assert install(['--destination',str(tmp_path/'agents'),'--logs',str(tmp_path/'logs'),'--repo','/tmp/engine']) == 0
    assert len(list((tmp_path/'agents').glob('*.plist'))) == 3
    assert install(['--destination',str(tmp_path/'dry'),'--dry-run']) == 0
    assert not (tmp_path/'dry').exists()


def test_native_api_errors_preserve_validation_misuse_and_retry_fields():
    envelope = {'origin':'https://api.modelspec.dev/v1/decide','status':400,
                'body':{'error':{'issues':[{'field':'fake.facet','reason':'unknown facet'}]}}}
    events = [{'type':'assistant','message':{'id':'one','content':[{'type':'tool_use','id':'a','name':'mcp__modelspec__decide','input':{}}]}},
              {'type':'user','message':{'content':[{'type':'tool_result','tool_use_id':'a','is_error':True,'content':[{'type':'text','text':json.dumps(envelope)}]}]}},
              {'type':'assistant','message':{'id':'two','content':[{'type':'tool_use','id':'b','name':'mcp__modelspec__decide','input':{}}]}}]
    parsed = providers.parse_transcript('claude', '\n'.join(json.dumps(e) for e in events))
    assert parsed.tool_calls[0]['unknown_facets'] == ['fake.facet']
    assert parsed.tool_calls[0]['validation_errors'] == envelope['body']['error']['issues']
    assert parsed.tool_calls[1]['retry_of'] == 'a'
    assert parsed.tool_calls[0]['turn'] is None
