"""Offline MODEL-309 job contracts. Models, browser transport, credentials and PRs are mocked."""
from __future__ import annotations

import copy
import fcntl
import hashlib
import json
import os
import plistlib
import shutil
import subprocess
import time
import urllib.error
import urllib.request
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
import yaml
from markdown_it import MarkdownIt

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
    monkeypatch.setattr(urllib.request, 'urlopen', lambda *a, **k: pytest.fail('urlopen'))


@pytest.fixture
def config(tmp_path):
    return jobs.configuration(tmp_path, max_runs=400)


def ready(clis=providers.CLIS):
    return {c: {'verified': True, 'supported': True, 'reason': None} for c in clis}


def execution(answer='Visitor answer', status='completed'):
    return providers.Execution(providers.Transcript(final_answer=answer, terminal=True, tokens_in=12,
                                                   tokens_out=3, cost_usd=0.2), 0, 25, status)


def search_execution(cli):
    result = execution('Use [ModelSpec](https://modelspec.dev/method/).')
    result.transcript.other_tool_calls = [{
        'name': next(n for n in providers.SEARCH_TOOLS[cli] if n not in {'WebFetch', 'web_fetch'}),
        'arguments': {'query': 'choose'}, 'result_observed': True, 'result': {'isError': False},
    }]
    return result


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
        assert command[command.index('--tools') + 1] == ('web_search,web_fetch,x_search' if purpose == 'search' else 'search_tool,use_tool')
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
    assert report['partial'] is False
    jobs.write_pair(tmp_path / 'reports/agent-scenarios', '2026-10-04', report, agent_harness.markdown(report))
    assert (tmp_path / 'reports/agent-scenarios/2026-10-04.json').is_file()


def test_scenario_pr_summary_parses_as_a_five_column_table(config, tmp_path):
    report = jobs.scenario_report(config, ['codex'], [], tmp_path, day='2026-10-04', dry_run=True)
    tokens = MarkdownIt('commonmark').enable('table').parse(jobs.scenario_summary(report))
    assert sum(t.type == 'table_open' for t in tokens) == 1
    assert [tokens[i + 1].content for i, t in enumerate(tokens) if t.type == 'th_open'] == [
        'Group', 'Success', 'Mean calls', 'API p50 ms', 'API p95 ms',
    ]
    row_widths = []
    for token in tokens:
        if token.type == 'tr_open':
            row_widths.append(0)
        elif token.type in ('th_open', 'td_open'):
            row_widths[-1] += 1
    assert row_widths and all(width == 5 for width in row_widths)


@pytest.mark.parametrize('crossing_role', ['agent', 'judge'])
def test_scenarios_crossing_quiet_hours_keep_rows_and_mark_partial(
    config, tmp_path, monkeypatch, crossing_role,
):
    config['_quiet_hours'] = True
    hour = [7]
    guard = harness.quiet_hours_guard
    monkeypatch.setattr(harness, 'quiet_hours_guard', lambda enabled, force: guard(
        enabled, force, datetime(2026, 10, 4, hour[0]),
    ))
    monkeypatch.setattr(jobs, 'require_ready', lambda *a: ready())
    calls = []
    verdict = {'passed': True, 'rationale': 'Evidence', 'answer_kind': 'abstain',
               'top_models': [], 'missing_capabilities': []}
    def launch(cli, cfg, workspace, prompt, *, mcp_enabled, **kwargs):
        role = 'agent' if mcp_enabled else 'judge'
        calls.append(role)
        if role == crossing_role:
            hour[0] = 8
        return execution('Visitor answer' if mcp_enabled else json.dumps(verdict))
    monkeypatch.setattr(harness, 'launch', launch)
    report = jobs.scenario_report(config, ['codex', 'grok'], [agent_harness.load_scenarios()[0]],
                                  tmp_path, day='2026-10-04')
    assert calls == (['agent'] if crossing_role == 'agent' else ['agent', 'judge'])
    assert report['runs'][1]['status'] == 'quiet_hours'
    assert report['partial'] is True
    assert 'partial' in agent_harness.markdown(report).splitlines()[0].lower()
    assert 'quiet_hours' in agent_harness.markdown(report).splitlines()[0]
    assert 'partial' in jobs.scenario_summary(report).splitlines()[0].lower()


def test_scenario_cutoff_during_judge_preflight_records_quiet_hours(config, tmp_path, monkeypatch):
    config['_quiet_hours'] = True
    checks = []
    guard = harness.quiet_hours_guard
    def quiet_hours(enabled, force):
        checks.append(True)
        guard(enabled, force, datetime(2026, 10, 4, 7 if len(checks) == 1 else 8))
    monkeypatch.setattr(harness, 'quiet_hours_guard', quiet_hours)
    monkeypatch.setattr(jobs, 'require_ready', lambda *a: ready())
    monkeypatch.setattr(harness, 'launch', lambda *a, **kw: pytest.fail('CLI started after cutoff'))
    report = jobs.scenario_report(config, ['codex'], [agent_harness.load_scenarios()[0]],
                                  tmp_path, day='2026-10-04')
    assert report['runs'][0]['status'] == 'quiet_hours' and report['partial'] is True


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


def test_job_lock_waits_for_an_overlapping_job_and_logs_progress(tmp_path, monkeypatch, capsys):
    elapsed, waits = [0.0], []
    monkeypatch.setattr(time, 'monotonic', lambda: elapsed[0])
    with (tmp_path / 'subscription-jobs.lock').open('a') as holder:
        fcntl.flock(holder, fcntl.LOCK_EX | fcntl.LOCK_NB)
        def sleep(seconds):
            waits.append(seconds)
            elapsed[0] += seconds
            if len(waits) == 2:
                fcntl.flock(holder, fcntl.LOCK_UN)
        monkeypatch.setattr(time, 'sleep', sleep)
        with jobs.job_lock(tmp_path):
            assert waits == [300, 300]
        # The context releases the lock so the next job can start.
        fcntl.flock(holder, fcntl.LOCK_EX | fcntl.LOCK_NB)
    log = capsys.readouterr().out.lower()
    assert 'waiting' in log and '600' in log and 'acquired' in log


def test_job_lock_refuses_after_six_hours_without_running(tmp_path, monkeypatch, capsys):
    elapsed, waits = [0.0], []
    monkeypatch.setattr(time, 'monotonic', lambda: elapsed[0])
    def sleep(seconds):
        waits.append(seconds)
        elapsed[0] += seconds
    monkeypatch.setattr(time, 'sleep', sleep)
    with (tmp_path / 'subscription-jobs.lock').open('a') as holder:
        fcntl.flock(holder, fcntl.LOCK_EX | fcntl.LOCK_NB)
        with pytest.raises(ValueError, match='21600.*lock'):
            with jobs.job_lock(tmp_path):
                pytest.fail('Job ran while another held the lock')
    assert elapsed[0] == 21600 and waits == [300] * 72
    assert 'waiting' in capsys.readouterr().out.lower()


def test_default_scenarios_job_never_requires_retired_gemini(tmp_path, monkeypatch, capsys):
    needed = []
    def stop(config, clis, *a):
        needed.extend(clis)
        raise ValueError('stop')
    monkeypatch.setattr(jobs, 'require_ready', stop)
    assert jobs.main(['scenarios', '--state-dir', str(tmp_path)]) == 2
    assert needed == ['claude', 'codex', 'grok']


def test_gemini_readiness_names_google_retirement_before_receipts(config, tmp_path, monkeypatch):
    monkeypatch.setattr(jobs, 'receipt_file', lambda *a: pytest.fail('receipt read'))
    with pytest.raises(ValueError, match='^gemini: Google stopped serving Gemini CLI'):
        jobs.require_ready(config, ['gemini'], tmp_path)


def test_subprocess_timeout_refuses_cleanly(tmp_path, monkeypatch, capsys):
    def timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired(['docker', 'info'], 30)
    monkeypatch.setattr(jobs, 'require_ready', timeout)
    monkeypatch.setattr(jobs, 'report_worktree', lambda *a: pytest.fail('Publication started'))
    assert jobs.main(['scenarios', '--state-dir', str(tmp_path)]) == 2
    output = capsys.readouterr().out
    assert 'Subscription job refused/failed' in output and 'timed out' in output


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


def test_aeo_cli_selection_marks_unselected_engines_skipped_and_partial(config, tmp_path, monkeypatch):
    settings = aeo_files(tmp_path, config)
    prompts = [{'id': 'test', 'text': 'Choose a model', 'cluster': 'category', 'success': 'mentioned'}]
    monkeypatch.setattr(aeo.inventory, 'load', lambda p: prompts)
    checked = []
    monkeypatch.setattr(aeo, 'require_ready', lambda cfg, clis, state: checked.append(clis) or ready())
    calls = []
    def launch(cli, cfg, workspace, prompt, **kw):
        calls.append(cli)
        result = execution('Use [ModelSpec](https://modelspec.dev/method/).')
        result.transcript.other_tool_calls = [{'name': next(n for n in providers.SEARCH_TOOLS[cli] if n not in {'WebFetch', 'web_fetch'}), 'arguments': {'query': 'choose'}, 'result_observed': True, 'result': {'isError': False}}]
        return result
    monkeypatch.setattr(harness, 'launch', launch)
    monkeypatch.setattr(aeo.engines, 'op_read', lambda ref: 'dummy')
    monkeypatch.setattr(aeo.engines, 'perplexity_call', lambda model, secret, prompt, cap: Answer('ModelSpec', 'sonar', reported_cost_usd=.007))
    aeo.run(tmp_path / 'prompts.yaml', settings, tmp_path / 'runs', tmp_path, config, '2026-10-04',
            clis=['grok', 'claude', 'codex'])
    assert checked == [['claude', 'codex', 'grok']]
    assert calls == ['codex', 'claude', 'grok']
    rows = {r['engine']: r for r in map(json.loads, (tmp_path / 'runs/2026-10-04/runs.jsonl').read_text().splitlines())}
    assert len(rows) == 5 and rows['gemini']['error'] == 'skipped (retired)'
    log = json.loads((tmp_path / 'runs/2026-10-04/engines.json').read_text())
    assert log['partial'] is True
    assert {e['engine']: e['status'] for e in log['engines']}['gemini'] == 'skipped'
    assert not (tmp_path / 'runs/BASELINE').exists()


def test_aeo_perplexity_runs_after_cli_jobs_cross_0800(config, tmp_path, monkeypatch):
    config['_quiet_hours'] = True
    settings = aeo_files(tmp_path, config)
    prompts = [{'id': 'test', 'text': 'Choose a model', 'cluster': 'category', 'success': 'mentioned'}]
    monkeypatch.setattr(aeo.inventory, 'load', lambda p: prompts)
    monkeypatch.setattr(aeo, 'require_ready', lambda *a: ready())
    hour, launched = [7], []
    guard = harness.quiet_hours_guard
    monkeypatch.setattr(harness, 'quiet_hours_guard', lambda enabled, force: guard(
        enabled, force, datetime(2026, 10, 4, hour[0]),
    ))
    def launch(cli, *args, **kwargs):
        launched.append(cli)
        if len(launched) == 4:
            hour[0] = 8
        return search_execution(cli)
    monkeypatch.setattr(harness, 'launch', launch)
    monkeypatch.setattr(aeo.engines, 'op_read', lambda ref: 'dummy')
    api_calls = []
    def perplexity(*args):
        assert hour[0] == 8
        api_calls.append(args)
        return Answer('ModelSpec', 'sonar', reported_cost_usd=.007)
    monkeypatch.setattr(aeo.engines, 'perplexity_call', perplexity)
    output = tmp_path / 'runs'
    aeo.run(tmp_path / 'prompts.yaml', settings, output, tmp_path, config, '2026-10-04')
    rows = [json.loads(line) for line in (output / '2026-10-04/runs.jsonl').read_text().splitlines()]
    assert launched == list(aeo.ENGINE_CLIS.values()) and len(api_calls) == 1
    assert len(rows) == 5 and rows[-1]['cost_usd'] == .007
    assert (output / '2026-10-04/report.md').is_file()


@pytest.mark.parametrize('failure_engine', ['anthropic', 'perplexity'])
@pytest.mark.parametrize('failure', [RuntimeError('late failure'), OSError('late failure'),
                                   subprocess.TimeoutExpired(['adapter'], 30)])
def test_aeo_late_failures_publish_completed_and_skipped_cells(
    config, tmp_path, monkeypatch, failure_engine, failure,
):
    tree = tmp_path / 'private'
    (tree / 'aeo').mkdir(parents=True)
    settings = aeo_files(tmp_path, config)
    shutil.copyfile(settings, tree / 'aeo/engines.yaml')
    prompts = [{'id': f'p{i}', 'text': 'Choose a model', 'cluster': 'category',
                'success': 'mentioned'} for i in range(2)]
    monkeypatch.setattr(aeo.inventory, 'load', lambda p: prompts)
    monkeypatch.setattr(aeo, 'require_ready', lambda *a: ready())
    monkeypatch.setattr(jobs, 'require_ready', lambda *a: ready())
    @contextmanager
    def worktree(*args):
        yield tree, 'aeo/test'
    monkeypatch.setattr(jobs, 'report_worktree', worktree)
    def launch(cli, *args, **kwargs):
        if failure_engine == 'anthropic' and cli == 'claude':
            raise failure
        return search_execution(cli)
    monkeypatch.setattr(harness, 'launch', launch)
    monkeypatch.setattr(aeo.engines, 'op_read', lambda ref: 'dummy')
    api_calls = []
    def perplexity(*args):
        api_calls.append(args)
        if failure_engine == 'perplexity' and len(api_calls) == 2:
            raise failure
        return Answer('ModelSpec', 'sonar', reported_cost_usd=.007)
    monkeypatch.setattr(aeo.engines, 'perplexity_call', perplexity)
    publications = []
    def publish(worktree, job, branch, day, body):
        publications.append((worktree, job, branch, day, body))
        return 'https://github.com/private/report/1'
    monkeypatch.setattr(jobs, 'publish', publish)
    assert jobs.main(['aeo', '--state-dir', str(tmp_path / 'state'), '--date', '2026-10-04']) == 0
    out = tree / 'aeo/runs/2026-10-04'
    rows = [json.loads(line) for line in (out / 'runs.jsonl').read_text().splitlines()]
    assert len(rows) == 10
    answered = [r for r in rows if 'detection' in r]
    # The default selection leaves out the retired Gemini CLI.
    assert len(answered) == (2 if failure_engine == 'anthropic' else 7)
    assert [r['error'] for r in rows if r['engine'] == 'gemini'] == ['skipped (retired)'] * 2
    skipped = [r for r in rows if 'error' in r and r['engine'] != 'gemini']
    assert all(r['error'].startswith('skipped (') for r in skipped)
    assert all(('late failure' if not isinstance(failure, subprocess.TimeoutExpired) else 'timed out')
               in r['error'] for r in skipped)
    log = json.loads((out / 'engines.json').read_text())
    assert len(log['engines']) == 5 and log['partial'] is True
    assert log['month_spend_usd'] == (0 if failure_engine == 'anthropic' else .007)
    assert json.loads((out / 'summary.json').read_text())['partial'] is True
    assert publications[0][:4] == (tree, 'aeo', 'aeo/test', '2026-10-04')
    assert publications[0][4] == (out / 'report.md').read_text()
    assert 'partial' in publications[0][4].splitlines()[0].lower()
    assert not (tree / 'aeo/runs/BASELINE').exists()


@pytest.mark.parametrize('stop', ['quiet_hours', 'max_runs', 'budget', 'missing_key'])
def test_aeo_refusals_fill_every_unrun_cell(config, tmp_path, monkeypatch, stop):
    settings = aeo_files(tmp_path, config)
    prompts = [{'id': f'p{i}', 'text': 'Choose a model', 'cluster': 'category',
                'success': 'mentioned'} for i in range(2)]
    monkeypatch.setattr(aeo.inventory, 'load', lambda p: prompts)
    monkeypatch.setattr(aeo, 'require_ready', lambda *a: ready())
    monkeypatch.setattr(harness, 'launch', lambda cli, *a, **kw: search_execution(cli))
    if stop == 'quiet_hours':
        config['_quiet_hours'] = True
        guard = harness.quiet_hours_guard
        monkeypatch.setattr(harness, 'quiet_hours_guard', lambda enabled, force: guard(
            enabled, force, datetime(2026, 10, 4, 8),
        ))
    elif stop == 'max_runs':
        config['max_runs_per_cli'] = 1
    elif stop == 'budget':
        raw = yaml.safe_load(settings.read_text())
        raw['monthly_cap_usd'] = .001
        settings.write_text(yaml.safe_dump(raw))
    def key(ref):
        if stop == 'missing_key':
            raise aeo.engines.EngineUnavailable('Missing Perplexity key')
        return 'dummy'
    monkeypatch.setattr(aeo.engines, 'op_read', key)
    monkeypatch.setattr(aeo.engines, 'perplexity_call', lambda *a: Answer('ModelSpec', 'sonar'))
    output = tmp_path / 'runs'
    aeo.run(tmp_path / 'prompts.yaml', settings, output, tmp_path, config, '2026-10-04')
    rows = [json.loads(line) for line in (output / '2026-10-04/runs.jsonl').read_text().splitlines()]
    assert len(rows) == 10
    skipped = [row for row in rows if 'error' in row]
    assert len(skipped) == {'quiet_hours': 8, 'max_runs': 4, 'budget': 2, 'missing_key': 2}[stop]
    assert all(row['error'].startswith('skipped (') for row in skipped)
    assert all(row['surface'] == ('api' if row['engine'] == 'perplexity' else 'subscription-cli')
               for row in rows)
    assert json.loads((output / '2026-10-04/engines.json').read_text())['partial'] is True
    assert not (output / 'BASELINE').exists()


@pytest.mark.parametrize('problem', ['missing_baseline', 'corrupt_baseline', 'baseline_write',
                                   'cli_raw_write', 'api_raw_write'])
def test_aeo_late_file_failures_keep_reports(config, tmp_path, monkeypatch, problem):
    settings = aeo_files(tmp_path, config)
    prompts = [{'id': 'test', 'text': 'Choose a model', 'cluster': 'category', 'success': 'mentioned'}]
    monkeypatch.setattr(aeo.inventory, 'load', lambda p: prompts)
    monkeypatch.setattr(aeo, 'require_ready', lambda *a: ready())
    monkeypatch.setattr(harness, 'launch', lambda cli, *a, **kw: search_execution(cli))
    monkeypatch.setattr(aeo.engines, 'op_read', lambda ref: 'dummy')
    monkeypatch.setattr(aeo.engines, 'perplexity_call', lambda *a: Answer('ModelSpec', 'sonar', reported_cost_usd=.007))
    output = tmp_path / 'runs'
    output.mkdir()
    if problem in ('missing_baseline', 'corrupt_baseline'):
        (output / 'BASELINE').write_text('2026-10-01\n')
        if problem == 'corrupt_baseline':
            (output / '2026-10-01').mkdir()
            (output / '2026-10-01/summary.json').write_text('{')
    write = Path.write_text
    def write_text(path, *args, **kwargs):
        if ((problem == 'baseline_write' and path == output / 'BASELINE')
            or (problem == 'cli_raw_write' and path == output / '2026-10-04/raw/openai/test.json')
            or (problem == 'api_raw_write' and path == output / '2026-10-04/raw/perplexity/test.json')):
            raise OSError('disk write failed')
        return write(path, *args, **kwargs)
    monkeypatch.setattr(Path, 'write_text', write_text)
    body = aeo.run(tmp_path / 'prompts.yaml', settings, output, tmp_path, config, '2026-10-04')
    out = output / '2026-10-04'
    rows = [json.loads(line) for line in (out / 'runs.jsonl').read_text().splitlines()]
    assert len(rows) == 5 and rows[0]['answer_text'].startswith('Use [ModelSpec]')
    assert sum('detection' in row for row in rows) == (1 if problem == 'cli_raw_write' else 5)
    assert json.loads((out / 'engines.json').read_text())['partial'] is True
    assert json.loads((out / 'summary.json').read_text())['partial'] is True
    assert body == (out / 'report.md').read_text() and 'partial' in body.splitlines()[0]
    assert sum(row['cost_usd'] for row in rows) == (0 if problem == 'cli_raw_write' else .007)


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
    assert {'Day':1,'Hour':22,'Minute':15} in calendars
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


@pytest.mark.parametrize('key,error', [
    ('', 'not set'), ('op://vault/item/field', 'not set'), ('test_abcdefghijklmnop', 'sandbox'),
])
def test_key_launcher_refuses_missing_reference_or_sandbox_keys(key, error):
    from qa import run_with_modelspec_key as launcher
    with pytest.raises(ValueError, match=error):
        launcher.job_environment({'MODELSPEC_API_KEY': key, 'HOME': '/h'})


def test_key_launcher_passes_only_the_key_and_a_clean_environment():
    from qa import run_with_modelspec_key as launcher
    env = launcher.job_environment({
        'MODELSPEC_API_KEY': 'live_value', 'HOME': '/h', 'PATH': '/bin', 'TERM': 'xterm',
        'OPENAI_API_KEY': 'vendor', 'OP_SESSION_x': 'session', 'GITHUB_TOKEN': 'gh',
    })
    assert set(env) == {'MODELSPEC_API_KEY', 'HOME', 'PATH', 'TERM', 'LANG', 'PYTHONPATH'}
    assert env['MODELSPEC_API_KEY'] == 'live_value' and env['LANG'] == 'en_US.UTF-8'
    jobs.refuse_vendor_auth(env)  # The job's own guard accepts the result.


def _decide_report(*bodies, status=200):
    responses = {f'r{i}': {'content': [{'type': 'text', 'text': json.dumps(
        {'origin': 'https://api.modelspec.dev/v1/decide', 'status': status, 'body': body})}]}
        for i, body in enumerate(bodies)}
    calls = [{'name': 'decide', 'response_ref': ref} for ref in responses]
    return {'runs': [{'tool_calls': calls + [{'name': 'vocab', 'response_ref': 'missing'}]}],
            'tool_responses': responses}


def test_funded_key_check_counts_partial_but_refuses_exhausted_or_unauthorised():
    report = _decide_report({'status': 'decided'}, {'status': 'partial'})
    assert jobs.require_funded_key(report) == {
        'decide_answers': 2, 'credits_exhausted': 0, 'partial': 1, 'unauthorised': 0}
    with pytest.raises(ValueError, match='1 credits.exhausted'):
        jobs.require_funded_key(_decide_report(
            {'status': 'partial', 'credits': {'exhausted': True, 'available': 0}}))
    with pytest.raises(ValueError, match='1 unauthorised'):
        jobs.require_funded_key(_decide_report({'error': {'code': 'missing_api_key'}}, status=401))
    with pytest.raises(ValueError, match='1 unauthorised'):
        jobs.require_funded_key(_decide_report('Unauthorized', status=401))
    assert jobs.decide_health(_decide_report({'credits': 'odd'}))['credits_exhausted'] == 0


DAY = '2026-10-04'
ENGINE = 'engine-sha'
SECRET = 'sk-testsecretvalue123456'
ALPHA = {'id': 'alpha', 'family': 'F1', 'persona': 'p', 'request': 'r', 'constraints': {}}
BETA = {'id': 'beta', 'family': 'F2', 'persona': 'p', 'request': 'r', 'constraints': {}}
PAIR_ORDER = [('alpha', 'codex'), ('alpha', 'grok'), ('beta', 'codex'), ('beta', 'grok')]


def checkpoint_digest(selected, scenarios, day=DAY, engine=ENGINE, modelspec_key=None):
    if modelspec_key is None:
        modelspec_key = bool(os.environ.get('MODELSPEC_API_KEY'))
    payload = {'clis': selected, 'scenarios': [scenario['id'] for scenario in scenarios],
               'engine_sha': engine, 'day': day, 'modelspec_key': modelspec_key}
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:16]


def checkpoint_file(output, selected, scenarios, modelspec_key=None):
    digest = checkpoint_digest(selected, scenarios, modelspec_key=modelspec_key)
    return output / 'checkpoints' / f'scenarios-{DAY}-{digest}.jsonl'


def recording_runner(monkeypatch, config, on_call=None):
    calls = []

    class Runner:
        def __init__(self, cfg, output, isolation):
            self.counts = {cli: {'agent': 0, 'judge': 0} for cli in providers.CLIS}

        def scenario(self, scenario, cli):
            pair = (scenario['id'], cli)
            calls.append(pair)
            status, error = 'completed', SECRET
            if on_call is not None:
                outcome = on_call(pair, len(calls))
                if isinstance(outcome, tuple):
                    status, error = outcome
                elif outcome:
                    status = outcome
            row = harness.empty_row(scenario, cli, config, status, error)
            return row

    monkeypatch.setattr(harness, 'Runner', Runner)
    return calls


def offline_scenario_job(monkeypatch):
    monkeypatch.setattr(jobs, 'require_ready', lambda *a: ready())
    monkeypatch.setattr(jobs, 'git_command', lambda *a: ENGINE)
    monkeypatch.setattr(jobs, 'network_probe', lambda *a, **k: pytest.fail('probe'))


def test_fresh_scenario_run_checkpoints_each_row(config, tmp_path, monkeypatch, capsys):
    offline_scenario_job(monkeypatch)
    calls = recording_runner(monkeypatch, config)
    scenarios = [ALPHA, BETA]
    selected = ['codex', 'grok']
    synced = []
    monkeypatch.setattr(jobs.os, 'fsync', lambda fd: synced.append(fd))
    report = jobs.scenario_report(config, selected, scenarios, tmp_path, day=DAY)
    path = checkpoint_file(tmp_path, selected, scenarios)
    lines = path.read_text().splitlines()
    assert calls == PAIR_ORDER
    assert len(lines) == 4 and len(synced) == 4
    assert report['resumed'] == 0
    assert report['network_suspect'] == []
    assert report['metadata']['cli_invocations_scope'] == 'whole run'
    assert report['metadata']['cli_invocations_total'] == report['metadata']['cli_invocations']
    assert report['metadata']['cli_invocations_total'] is not report['metadata']['cli_invocations']
    assert report['runs'][0]['network'] == {'class': 'not_checked'}
    assert report['evidence_note'].endswith('Measured subscription run.')
    assert 'checkpoint' not in report['evidence_note']
    assert 'Resuming:' not in capsys.readouterr().out
    assert (tmp_path / 'checkpoints').stat().st_mode & 0o777 == 0o700
    first = json.loads(lines[0])
    assert first['scenario'] == 'alpha' and first['cli'] == 'codex' and first['agent'] == 'openai'
    assert first['estimated_cost_usd'] == 0.0 and first['judges'] == [] and first['billing_calls'] == []
    assert SECRET not in path.read_text() and '[REDACTED]' in path.read_text()
    assert report['runs'][0]['error'] == SECRET
    assert [(row['scenario'], row['cli']) for row in report['runs']] == PAIR_ORDER
    dry = tmp_path / 'dry'
    dry.mkdir()
    dry_report = jobs.scenario_report(config, ['codex'], [ALPHA], dry, day=DAY, dry_run=True)
    assert dry_report['resumed'] == 0 and dry_report['network_suspect'] == []
    assert 'network' not in dry_report['runs'][0]
    assert not (dry / 'checkpoints').exists()


def test_resume_continues_after_interrupt_and_keeps_fresh_order(config, tmp_path, monkeypatch, capsys):
    offline_scenario_job(monkeypatch)
    phase = {'arm': True}

    def on_call(pair, n):
        if phase['arm'] and n == 3:
            raise KeyboardInterrupt
        if phase['arm'] and pair == ('alpha', 'grok'):
            return 'failed'
        return 'completed'

    calls = recording_runner(monkeypatch, config, on_call)
    scenarios = [ALPHA, BETA]
    selected = ['codex', 'grok']
    with pytest.raises(KeyboardInterrupt):
        jobs.scenario_report(config, selected, scenarios, tmp_path, day=DAY)
    assert calls == [('alpha', 'codex'), ('alpha', 'grok'), ('beta', 'codex')]
    phase['arm'] = False
    calls.clear()
    report = jobs.scenario_report(config, selected, scenarios, tmp_path, day=DAY, resume=True)
    path = checkpoint_file(tmp_path, selected, scenarios)
    assert calls == [('beta', 'codex'), ('beta', 'grok')]
    assert [(row['scenario'], row['cli'], row['status']) for row in report['runs']] == [
        ('alpha', 'codex', 'completed'),
        ('alpha', 'grok', 'failed'),
        ('beta', 'codex', 'completed'),
        ('beta', 'grok', 'completed'),
    ]
    assert report['resumed'] == 2
    assert report['evidence_note'].endswith(
        'Measured subscription run. Resumed after an interruption: 2 rows came from the checkpoint.'
    )
    assert capsys.readouterr().out == f'Resuming: 2 of 4 rows already recorded in {path}\n'
    assert [json.loads(line)['status'] for line in path.read_text().splitlines()] == [
        'completed', 'failed', 'completed', 'completed',
    ]


def test_resume_ignores_a_truncated_final_line(config, tmp_path, monkeypatch):
    offline_scenario_job(monkeypatch)
    calls = recording_runner(monkeypatch, config)
    scenarios = [ALPHA, BETA]
    selected = ['codex', 'grok']
    jobs.scenario_report(config, selected, scenarios, tmp_path, day=DAY)
    path = checkpoint_file(tmp_path, selected, scenarios)
    lines = path.read_text().splitlines()
    path.write_text(lines[0] + '\n' + lines[1] + '\n' + lines[2][:12])
    calls.clear()
    report = jobs.scenario_report(config, selected, scenarios, tmp_path, day=DAY, resume=True)
    assert calls == [('beta', 'codex'), ('beta', 'grok')]
    assert report['resumed'] == 2
    assert [(row['scenario'], row['cli']) for row in report['runs']] == PAIR_ORDER
    reloaded = [json.loads(line) for line in path.read_text().splitlines()]
    assert [(row['scenario'], row['cli']) for row in reloaded] == PAIR_ORDER


def test_malformed_checkpoint_line_raises(config, tmp_path, monkeypatch):
    offline_scenario_job(monkeypatch)
    calls = recording_runner(monkeypatch, config)
    scenarios = [ALPHA, BETA]
    selected = ['codex', 'grok']
    jobs.scenario_report(config, selected, scenarios, tmp_path, day=DAY)
    path = checkpoint_file(tmp_path, selected, scenarios)
    lines = path.read_text().splitlines()
    path.write_text(lines[0] + '\n{broken\n' + lines[1] + '\n')
    calls.clear()
    with pytest.raises(ValueError, match='Malformed checkpoint line 2'):
        jobs.scenario_report(config, selected, scenarios, tmp_path, day=DAY, resume=True)
    assert calls == []
    assert '{broken' in path.read_text()


def test_existing_checkpoint_without_resume_is_refused(config, tmp_path, monkeypatch):
    ready_calls = []
    monkeypatch.setattr(jobs, 'require_ready', lambda *a: ready_calls.append(True) or ready())
    monkeypatch.setattr(jobs, 'git_command', lambda *a: ENGINE)
    calls = recording_runner(monkeypatch, config)
    scenarios = [ALPHA, BETA]
    selected = ['codex', 'grok']
    jobs.scenario_report(config, selected, scenarios, tmp_path, day=DAY)
    path = checkpoint_file(tmp_path, selected, scenarios)
    before = path.read_text()
    with pytest.raises(ValueError, match='--resume') as caught:
        jobs.scenario_report(config, selected, scenarios, tmp_path, day=DAY)
    assert str(path) in str(caught.value)
    assert 'delete it to start over' in str(caught.value)
    assert path.read_text() == before
    assert calls == PAIR_ORDER and ready_calls == [True]


def test_checkpoint_key_changes_with_clis_and_scenarios(config, tmp_path, monkeypatch):
    offline_scenario_job(monkeypatch)
    recording_runner(monkeypatch, config)
    jobs.scenario_report(config, ['codex'], [ALPHA], tmp_path, day=DAY)
    jobs.scenario_report(config, ['grok'], [ALPHA], tmp_path, day=DAY)
    jobs.scenario_report(config, ['codex'], [BETA], tmp_path, day=DAY)
    codex_alpha = checkpoint_file(tmp_path, ['codex'], [ALPHA])
    grok_alpha = checkpoint_file(tmp_path, ['grok'], [ALPHA])
    codex_beta = checkpoint_file(tmp_path, ['codex'], [BETA])
    assert codex_alpha.is_file() and grok_alpha.is_file() and codex_beta.is_file()
    assert len({codex_alpha.name, grok_alpha.name, codex_beta.name}) == 3
    assert checkpoint_digest(['codex'], [ALPHA]) != checkpoint_digest(['grok'], [ALPHA])
    assert checkpoint_digest(['codex'], [ALPHA]) != checkpoint_digest(['codex'], [BETA])
    assert len(checkpoint_digest(['codex'], [ALPHA])) == 16


def test_checkpoint_symlinks_are_refused(config, tmp_path, monkeypatch):
    monkeypatch.setattr(jobs, 'git_command', lambda *a: ENGINE)
    monkeypatch.setattr(jobs, 'require_ready', lambda *a: pytest.fail('ready'))
    link = tmp_path / 'checkpoints'
    link.symlink_to(tmp_path)
    with pytest.raises(ValueError, match='symlink'):
        jobs.scenario_report(config, ['codex'], [ALPHA], tmp_path, day=DAY)
    link.unlink()
    (tmp_path / 'checkpoints').mkdir()
    target = tmp_path / 'other.jsonl'
    target.write_text('')
    checkpoint_file(tmp_path, ['codex'], [ALPHA]).symlink_to(target)
    with pytest.raises(ValueError, match='symlink'):
        jobs.scenario_report(config, ['codex'], [ALPHA], tmp_path, day=DAY)


@pytest.mark.parametrize('argv', [
    ['scenarios', '--dry-run', '--resume', '--cli', 'codex'],
    ['ux', '--resume', '--cli', 'codex'],
    ['aeo', '--resume', '--cli', 'codex'],
])
def test_main_rejects_resume_outside_a_live_scenarios_job(argv, tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(jobs, 'git_command', lambda *a: pytest.fail('git'))
    monkeypatch.setattr(jobs, 'require_ready', lambda *a: pytest.fail('ready'))
    monkeypatch.setattr(harness, 'launch', lambda *a, **k: pytest.fail('launch'))
    assert jobs.main([*argv, '--state-dir', str(tmp_path), '--date', DAY]) == 2
    assert '--resume' in capsys.readouterr().out
    assert not (tmp_path / 'checkpoints').exists()


REACHABLE = {
    'reachable': True,
    'checks': [
        {'url': 'https://api.modelspec.dev/v1/health', 'reachable': True,
         'status': 200, 'error': None, 'ms': 1.0},
        {'url': 'https://www.cloudflare.com/cdn-cgi/trace', 'reachable': True,
         'status': 200, 'error': None, 'ms': 1.0},
    ],
    'checked_at': '2026-10-04T00:00:00+00:00',
}
UNREACHABLE = {
    'reachable': False,
    'checks': [
        {'url': 'https://api.modelspec.dev/v1/health', 'reachable': False,
         'status': None, 'error': 'URLError', 'ms': 1.0},
        {'url': 'https://www.cloudflare.com/cdn-cgi/trace', 'reachable': False,
         'status': None, 'error': 'URLError', 'ms': 1.0},
    ],
    'checked_at': '2026-10-04T00:00:00+00:00',
}


def scripted_probe(monkeypatch, results):
    pending = list(results)
    calls = []

    def probe():
        calls.append('called')
        return pending.pop(0)

    monkeypatch.setattr(jobs, 'network_probe', probe)
    return calls


def test_network_tag_marks_transport_text_even_when_the_probe_is_reachable(monkeypatch):
    calls = scripted_probe(monkeypatch, [REACHABLE])
    assert jobs.network_tag({'status': 'cli_error', 'error': 'read ECONNRESET'}) == {
        'class': 'network_suspect',
        'failed_stage': 'agent',
        'error_signature': True,
        'api_reachable': True,
        'probe': REACHABLE,
    }
    assert calls == ['called']


def test_network_tag_marks_a_clean_error_when_the_probe_is_unreachable(monkeypatch):
    scripted_probe(monkeypatch, [UNREACHABLE])
    assert jobs.network_tag({
        'status': 'timeout', 'error': 'rubric parser rejected the answer',
    }) == {
        'class': 'network_suspect',
        'failed_stage': 'agent',
        'error_signature': False,
        'api_reachable': False,
        'probe': UNREACHABLE,
    }


def test_network_tag_keeps_a_clean_error_when_the_probe_is_reachable(monkeypatch):
    scripted_probe(monkeypatch, [REACHABLE])
    assert jobs.network_tag({
        'status': 'transcript_error', 'error': 'rubric parser rejected the answer',
    }) == {
        'class': 'no_network_signal',
        'failed_stage': 'agent',
        'error_signature': False,
        'api_reachable': True,
        'probe': REACHABLE,
    }


def test_network_tag_names_the_judge_when_only_the_judge_failed(monkeypatch):
    scripted_probe(monkeypatch, [REACHABLE])
    assert jobs.network_tag({
        'status': 'completed',
        'error': 'rubric parser rejected the answer',
        'judge_execution': {'status': 'empty_answer', 'error': 'read ECONNRESET'},
    }) == {
        'class': 'network_suspect',
        'failed_stage': 'judge',
        'error_signature': True,
        'api_reachable': True,
        'probe': REACHABLE,
    }


def test_network_tag_skips_the_probe_unless_the_row_failed(monkeypatch):
    calls = scripted_probe(monkeypatch, [REACHABLE])
    row = {
        'status': 'completed',
        'error': 'read ECONNRESET',
        'judge_execution': {'status': 'completed', 'error': '502 Bad Gateway'},
    }
    assert jobs.network_tag(row) == {'class': 'not_checked'}
    assert calls == []


def test_report_lists_exactly_the_network_suspect_pairs(config, tmp_path, monkeypatch):
    offline_scenario_job(monkeypatch)
    scripted_probe(monkeypatch, [REACHABLE, UNREACHABLE, REACHABLE])

    def on_call(pair, n):
        if pair == ('alpha', 'codex'):
            return 'cli_error', 'read ECONNRESET'
        if pair == ('beta', 'codex'):
            return 'timeout', 'rubric parser rejected the answer'
        if pair == ('beta', 'grok'):
            return 'transcript_error', 'rubric parser rejected the answer'
        return 'completed'

    recording_runner(monkeypatch, config, on_call)
    report = jobs.scenario_report(config, ['codex', 'grok'], [ALPHA, BETA], tmp_path, day=DAY)
    assert [row['network'] for row in report['runs']] == [
        {'class': 'network_suspect', 'failed_stage': 'agent', 'error_signature': True,
         'api_reachable': True, 'probe': REACHABLE},
        {'class': 'not_checked'},
        {'class': 'network_suspect', 'failed_stage': 'agent', 'error_signature': False,
         'api_reachable': False, 'probe': UNREACHABLE},
        {'class': 'no_network_signal', 'failed_stage': 'agent', 'error_signature': False,
         'api_reachable': True, 'probe': REACHABLE},
    ]
    assert report['network_suspect'] == [['alpha', 'codex'], ['beta', 'codex']]
    assert report['evidence_note'].endswith(
        'Measured subscription run.'
        ' 2 failed rows are tagged network_suspect and can be excluded; see network_suspect.'
    )
    path = checkpoint_file(tmp_path, ['codex', 'grok'], [ALPHA, BETA])
    saved = [json.loads(line)['network']['class'] for line in path.read_text().splitlines()]
    assert saved == ['network_suspect', 'not_checked', 'network_suspect', 'no_network_signal']


def test_network_tag_survives_checkpoint_resume(config, tmp_path, monkeypatch):
    offline_scenario_job(monkeypatch)
    scripted_probe(monkeypatch, [REACHABLE])
    phase = {'stop': True}

    def on_call(pair, n):
        if phase['stop'] and n == 2:
            raise KeyboardInterrupt
        if pair == ('alpha', 'codex'):
            return 'cli_error', 'read ECONNRESET'
        return 'completed'

    calls = recording_runner(monkeypatch, config, on_call)
    with pytest.raises(KeyboardInterrupt):
        jobs.scenario_report(config, ['codex', 'grok'], [ALPHA], tmp_path, day=DAY)
    phase['stop'] = False
    calls.clear()
    monkeypatch.setattr(jobs, 'network_probe', lambda *a, **k: pytest.fail('probe'))
    report = jobs.scenario_report(
        config, ['codex', 'grok'], [ALPHA], tmp_path, day=DAY, resume=True)
    assert calls == [('alpha', 'grok')]
    assert report['runs'][0]['network'] == {
        'class': 'network_suspect',
        'failed_stage': 'agent',
        'error_signature': True,
        'api_reachable': True,
        'probe': REACHABLE,
    }
    assert report['runs'][1]['network'] == {'class': 'not_checked'}
    assert report['network_suspect'] == [['alpha', 'codex']]
    assert report['resumed'] == 1
    assert report['evidence_note'].endswith(
        'Measured subscription run. Resumed after an interruption: 1 rows came from the checkpoint.'
        ' 1 failed rows are tagged network_suspect and can be excluded; see network_suspect.'
    )


def test_network_probe_classifies_urlerror_and_httperror(monkeypatch):
    seen = []

    def raise_urlerror(request, timeout):
        seen.append((request.full_url, timeout, request.header_items()))
        raise urllib.error.URLError('offline')

    monkeypatch.setattr(urllib.request, 'urlopen', raise_urlerror)
    down = jobs.network_probe()
    assert seen == [
        ('https://api.modelspec.dev/v1/health', 5.0,
         [('User-agent', 'modelspec-qa-network-probe')]),
        ('https://www.cloudflare.com/cdn-cgi/trace', 5.0,
         [('User-agent', 'modelspec-qa-network-probe')]),
    ]
    assert down['reachable'] is False
    observed = [
        (item['url'], item['reachable'], item['status'], item['error']) for item in down['checks']
    ]
    assert observed == [
        ('https://api.modelspec.dev/v1/health', False, None, 'URLError'),
        ('https://www.cloudflare.com/cdn-cgi/trace', False, None, 'URLError'),
    ]
    assert all(type(item['ms']) is float and item['ms'] >= 0 for item in down['checks'])
    assert datetime.fromisoformat(down['checked_at']).utcoffset() == timedelta(0)

    def raise_httperror(request, timeout):
        raise urllib.error.HTTPError(request.full_url, 401, 'Unauthorized', None, None)

    monkeypatch.setattr(urllib.request, 'urlopen', raise_httperror)
    up = jobs.network_probe()
    assert up['reachable'] is True
    assert [(item['reachable'], item['status'], item['error']) for item in up['checks']] == [
        (True, 401, None),
        (True, 401, None),
    ]


def test_resume_without_a_checkpoint_names_the_expected_path(config, tmp_path, monkeypatch):
    monkeypatch.setattr(jobs, 'git_command', lambda *a: ENGINE)
    monkeypatch.setattr(jobs, 'require_ready', lambda *a: pytest.fail('ready'))
    monkeypatch.setattr(harness, 'Runner', lambda *a: pytest.fail('runner'))
    path = checkpoint_file(tmp_path, ['codex'], [ALPHA])
    with pytest.raises(ValueError) as caught:
        jobs.scenario_report(config, ['codex'], [ALPHA], tmp_path, day=DAY, resume=True)
    message = str(caught.value)
    assert str(path) in message
    assert 'CLIs' in message and 'scenarios' in message and '--date' in message
    assert 'engine commit' in message and 'ModelSpec key' in message
    assert not path.exists()


TRANSPORT_SIGNATURES = (
    'ECONNRESET',
    'ECONNREFUSED',
    'ETIMEDOUT',
    'ENOTFOUND',
    'EAI_AGAIN',
    'ENETUNREACH',
    'EHOSTUNREACH',
    'getaddrinfo',
    'connection reset by peer',
    'connection refused',
    'network is unreachable',
    'socket hang up',
    'stream disconnected',
    'TLS handshake',
    '502 Bad Gateway',
    '503 Service Unavailable',
    '504 Gateway Timeout',
    'econnreset',
)


def _split_probe(*, api, internet):
    def check(url, up):
        return {
            'url': url, 'reachable': up, 'status': 200 if up else None,
            'error': None if up else 'URLError', 'ms': 1.0,
        }
    return {
        'reachable': api and internet,
        'checks': [
            check(jobs.API_HEALTH_URL, api),
            check(jobs.INTERNET_PROBE_URL, internet),
        ],
        'checked_at': '2026-10-04T00:00:00+00:00',
    }


@pytest.mark.parametrize('text', TRANSPORT_SIGNATURES)
def test_transport_signatures_are_word_bounded_and_case_insensitive(text, monkeypatch):
    scripted_probe(monkeypatch, [REACHABLE])
    tag = jobs.network_tag({'status': 'cli_error', 'error': f'before {text} after'})
    assert tag['class'] == 'network_suspect'
    assert tag['error_signature'] is True
    assert tag['api_reachable'] is True


@pytest.mark.parametrize('text', [
    'CLI timed out',
    'network access disabled',
    'TLS',
    'connection reset',
    'temporarily unavailable',
    'the network',
    '504 Gateway Time-out',
    'xECONNRESET',
    'ETIMEDOUTX',
])
def test_ordinary_failure_text_is_not_a_transport_signature(text, monkeypatch):
    scripted_probe(monkeypatch, [REACHABLE])
    tag = jobs.network_tag({'status': 'timeout', 'error': text})
    assert tag['error_signature'] is False
    assert tag['class'] == 'no_network_signal'
    assert tag['api_reachable'] is True


def test_network_tag_splits_the_internet_probe_from_the_api_probe(monkeypatch):
    internet_down = _split_probe(api=True, internet=False)
    api_down = _split_probe(api=False, internet=True)
    scripted_probe(monkeypatch, [REACHABLE, REACHABLE, internet_down, api_down])
    timed_out = jobs.network_tag({'status': 'timeout', 'error': 'CLI timed out'})
    assert timed_out['class'] == 'no_network_signal'
    assert timed_out['error_signature'] is False
    assert timed_out['api_reachable'] is True
    disabled = jobs.network_tag({'status': 'cli_error', 'error': 'network access disabled'})
    assert disabled['class'] == 'no_network_signal'
    assert disabled['error_signature'] is False
    local = jobs.network_tag({'status': 'timeout', 'error': 'rubric parser rejected the answer'})
    assert local == {
        'class': 'network_suspect',
        'failed_stage': 'agent',
        'error_signature': False,
        'api_reachable': True,
        'probe': internet_down,
    }
    api = jobs.network_tag({'status': 'timeout', 'error': 'CLI timed out'})
    assert api['class'] == 'no_network_signal'
    assert api['error_signature'] is False
    assert api['api_reachable'] is False
    assert api['probe'] is api_down


def test_resumed_run_keeps_final_invocation_counts_and_totals_checkpoint_starts(
    config, tmp_path, monkeypatch,
):
    offline_scenario_job(monkeypatch)
    phase = {'stop': False}
    gamma = {'id': 'gamma', 'family': 'F3', 'persona': 'p', 'request': 'r', 'constraints': {}}

    class Runner:
        def __init__(self, cfg, output, isolation):
            self.counts = {cli: {'agent': 0, 'judge': 0} for cli in providers.CLIS}

        def scenario(self, scenario, cli):
            if phase['stop'] and scenario['id'] == 'gamma':
                raise KeyboardInterrupt
            self.counts[cli]['agent'] += 1
            row = harness.empty_row(scenario, cli, config, 'completed')
            if scenario['id'] == 'beta':
                row['judge_execution'] = {'status': 'completed'}
            else:
                judge = harness.judge_for(cli, config['judges'])
                self.counts[judge]['judge'] += 1
                row['judge_execution'] = {'cli': judge, 'status': 'completed'}
            return row

    monkeypatch.setattr(harness, 'Runner', Runner)
    fresh = jobs.scenario_report(config, ['codex'], [ALPHA], tmp_path / 'fresh', day=DAY)
    assert fresh['metadata']['cli_invocations_scope'] == 'whole run'
    assert fresh['metadata']['cli_invocations'] == {
        'claude': {'agent': 0, 'judge': 1},
        'codex': {'agent': 1, 'judge': 0},
        'gemini': {'agent': 0, 'judge': 0},
        'grok': {'agent': 0, 'judge': 0},
    }
    assert fresh['metadata']['cli_invocations_total'] == fresh['metadata']['cli_invocations']
    assert fresh['metadata']['cli_invocations_total'] is not fresh['metadata']['cli_invocations']
    phase['stop'] = True
    with pytest.raises(KeyboardInterrupt):
        jobs.scenario_report(config, ['codex'], [ALPHA, BETA, gamma], tmp_path, day=DAY)
    phase['stop'] = False
    report = jobs.scenario_report(
        config, ['codex'], [ALPHA, BETA, gamma], tmp_path, day=DAY, resume=True)
    assert report['resumed'] == 2
    assert [(row['scenario'], row['cli']) for row in report['runs']] == [
        ('alpha', 'codex'), ('beta', 'codex'), ('gamma', 'codex'),
    ]
    assert report['metadata']['cli_invocations_scope'] == 'final invocation only'
    assert report['metadata']['cli_invocations'] == {
        'claude': {'agent': 0, 'judge': 1},
        'codex': {'agent': 1, 'judge': 0},
        'gemini': {'agent': 0, 'judge': 0},
        'grok': {'agent': 0, 'judge': 0},
    }
    assert report['metadata']['cli_invocations_total'] == {
        'claude': {'agent': 0, 'judge': 2},
        'codex': {'agent': 3, 'judge': 0},
        'gemini': {'agent': 0, 'judge': 0},
        'grok': {'agent': 0, 'judge': 0},
    }


def _explicit_checkpoint_digest(key):
    payload = {
        'clis': ['codex'], 'scenarios': ['alpha'], 'engine_sha': ENGINE, 'day': DAY,
        'modelspec_key': key,
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:16]


def test_checkpoint_key_includes_whether_the_modelspec_key_is_set(config, tmp_path, monkeypatch):
    offline_scenario_job(monkeypatch)
    recording_runner(monkeypatch, config)
    monkeypatch.delenv('MODELSPEC_API_KEY', raising=False)
    jobs.scenario_report(config, ['codex'], [ALPHA], tmp_path, day=DAY)
    absent = tmp_path / 'checkpoints' / f'scenarios-{DAY}-{_explicit_checkpoint_digest(False)}.jsonl'
    assert absent.is_file()
    monkeypatch.setenv('MODELSPEC_API_KEY', 'present-for-test')
    jobs.scenario_report(config, ['codex'], [ALPHA], tmp_path, day=DAY)
    present = tmp_path / 'checkpoints' / f'scenarios-{DAY}-{_explicit_checkpoint_digest(True)}.jsonl'
    assert present.is_file()
    assert absent.name != present.name


def test_require_funded_key_names_the_checkpoint_resume_would_replay(tmp_path):
    report = _decide_report({'status': 'partial', 'credits': {'exhausted': True, 'available': 0}})
    path = tmp_path / 'checkpoints' / 'scenarios-day.jsonl'
    with pytest.raises(ValueError, match='1 credits.exhausted') as caught:
        jobs.require_funded_key(report, path)
    message = str(caught.value)
    assert str(path) in message
    assert 'replayed on --resume' in message
    assert 'delete the checkpoint' in message
    assert 'start over' in message
    with pytest.raises(ValueError, match='1 credits.exhausted') as old:
        jobs.require_funded_key(report)
    assert 'checkpoint' not in str(old.value)
    assert 'replayed' not in str(old.value)


def _main_scenario_guards(monkeypatch):
    calls = []

    def git(repo, *args):
        calls.append(args)
        assert args == ('rev-parse', 'HEAD'), args
        return ENGINE

    monkeypatch.setattr(jobs, 'git_command', git)
    monkeypatch.setattr(jobs, 'require_ready', lambda *a: ready())
    monkeypatch.setattr(jobs, 'report_worktree', lambda *a: pytest.fail('worktree'))
    monkeypatch.setattr(agent_harness, 'load_scenarios', lambda directory=None: [ALPHA])
    return calls


def test_main_refuses_an_existing_checkpoint_before_opening_a_worktree(tmp_path, monkeypatch, capsys):
    monkeypatch.delenv('MODELSPEC_API_KEY', raising=False)
    calls = _main_scenario_guards(monkeypatch)
    state = tmp_path / 'state'
    config = jobs.configuration(state, max_runs=400)
    resolved = harness.private_output(state)
    path = jobs._scenario_checkpoint(resolved, ['codex'], [ALPHA], DAY, ENGINE, config=config)
    path.write_text('{}\n')
    code = jobs.main([
        'scenarios', '--cli', 'codex', '--scenario', 'alpha',
        '--state-dir', str(state), '--date', DAY,
        '--data-repo', str(tmp_path / 'data'),
    ])
    out = capsys.readouterr().out
    assert code == 2
    assert str(path) in out
    assert '--resume' in out and 'delete it to start over' in out
    assert calls == [('rev-parse', 'HEAD')]


def test_main_refuses_a_missing_checkpoint_before_opening_a_worktree(tmp_path, monkeypatch, capsys):
    monkeypatch.delenv('MODELSPEC_API_KEY', raising=False)
    calls = _main_scenario_guards(monkeypatch)
    state = tmp_path / 'state'
    config = jobs.configuration(state, max_runs=400)
    resolved = harness.private_output(state)
    path = jobs._scenario_checkpoint(resolved, ['codex'], [ALPHA], DAY, ENGINE, config=config)
    assert not path.exists()
    code = jobs.main([
        'scenarios', '--resume', '--cli', 'codex', '--scenario', 'alpha',
        '--state-dir', str(state), '--date', DAY,
        '--data-repo', str(tmp_path / 'data'),
    ])
    out = capsys.readouterr().out
    assert code == 2
    assert str(path) in out and 'No checkpoint' in out
    assert calls == [('rev-parse', 'HEAD')]
    assert not path.exists()


def test_main_passes_the_checkpoint_path_into_the_funded_key_check(tmp_path, monkeypatch):
    monkeypatch.setenv('MODELSPEC_API_KEY', 'present-for-test')
    monkeypatch.setattr(jobs, 'require_ready', lambda *a: ready())

    def git(repo, *args):
        assert args == ('rev-parse', 'HEAD'), args
        return ENGINE

    monkeypatch.setattr(jobs, 'git_command', git)
    seen = {}

    def funded(report, checkpoint=None):
        seen['path'] = checkpoint
        raise ValueError('stop after key check')

    monkeypatch.setattr(jobs, 'require_funded_key', funded)

    @contextmanager
    def worktree(*args):
        yield tmp_path / 'tree', 'branch'

    monkeypatch.setattr(jobs, 'report_worktree', worktree)
    monkeypatch.setattr(jobs, 'publish', lambda *a: pytest.fail('publish'))
    monkeypatch.setattr(agent_harness, 'load_scenarios', lambda directory=None: [ALPHA])

    class Runner:
        def __init__(self, cfg, output, isolation):
            self.counts = {cli: {'agent': 0, 'judge': 0} for cli in providers.CLIS}

        def scenario(self, scenario, cli):
            self.counts[cli]['agent'] += 1
            return harness.empty_row(scenario, cli, config, 'completed')

    monkeypatch.setattr(harness, 'Runner', Runner)
    state = tmp_path / 'state'
    config = jobs.configuration(state, max_runs=400)
    resolved = harness.private_output(state)
    path = jobs._scenario_checkpoint(resolved, ['codex'], [ALPHA], DAY, ENGINE, config=config)
    assert jobs.main([
        'scenarios', '--cli', 'codex', '--scenario', 'alpha',
        '--state-dir', str(state), '--date', DAY,
        '--data-repo', str(tmp_path / 'data'),
    ]) == 2
    assert seen['path'] == path
