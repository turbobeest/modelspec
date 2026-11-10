"""Offline contracts for subscription-job report-out. No CLI, network or PR."""
from __future__ import annotations

import fcntl
import os
import stat
import subprocess
import time
from datetime import datetime
from pathlib import Path

import pytest
import yaml

from qa import agent_harness, subscription_aeo as aeo, subscription_jobs as jobs
from qa import tui_harness as harness, tui_providers as providers
from qa.docker.entrypoint import VENDOR_ENV
from scripts.aeo.engines import Answer


ROOT = Path(__file__).resolve().parents[1]
DAY = '2026-10-04'
ENGINE = 'engine-sha'
ALPHA = {'id': 'alpha', 'family': 'F1', 'persona': 'p', 'request': 'r', 'constraints': {}}
DATA_REMOTE = 'https://github.com/turbobeest/modelspec-data.git'
BUSINESS_REMOTE = 'https://github.com/turbobeest/modelspec-business.git'


@pytest.fixture(autouse=True)
def subscription_environment(monkeypatch):
    for name in tuple(os.environ):
        if VENDOR_ENV.search(name) and not name.startswith('MODELSPEC_'):
            monkeypatch.delenv(name)
    monkeypatch.delenv('GITHUB_ACTIONS', raising=False)
    monkeypatch.delenv('MODELSPEC_API_KEY', raising=False)


def _git_args(command):
    if not command or command[0] != 'git':
        return None
    if len(command) >= 3 and command[1] == '-C':
        return command[3:]
    return command[1:]


def _publish_commands(commands):
    found = []
    for command in commands:
        if command[0] == 'gh':
            found.append(command)
            continue
        args = _git_args(command)
        if args and args[0] in {'add', 'commit', 'push'}:
            found.append(command)
    return found


def _install_git(monkeypatch, remote, on_worktree=None):
    commands = []
    bodies = []

    def run(command, **kwargs):
        command = list(command)
        commands.append(command)
        args = _git_args(command) or []
        if args[:2] == ['rev-parse', 'HEAD']:
            return subprocess.CompletedProcess(command, 0, ENGINE + '\n', '')
        if args[:2] == ['remote', 'get-url']:
            return subprocess.CompletedProcess(command, 0, remote + '\n', '')
        if args[:2] == ['worktree', 'add']:
            destination = Path(args[4])
            destination.mkdir(parents=True, exist_ok=True)
            if on_worktree:
                on_worktree(destination)
            return subprocess.CompletedProcess(command, 0, '', '')
        if command[0] == 'gh':
            body = Path(command[command.index('--body-file') + 1]).read_text(encoding='utf-8')
            bodies.append(body)
            return subprocess.CompletedProcess(command, 0, 'https://github.com/report/1\n', '')
        return subprocess.CompletedProcess(command, 0, '', '')

    monkeypatch.setattr(jobs.subprocess, 'run', run)
    return commands, bodies


def _scenario_runner(monkeypatch, caps):
    monkeypatch.setattr(jobs, 'require_ready', lambda *a: {})
    monkeypatch.setattr(agent_harness, 'load_scenarios', lambda directory=None: [ALPHA])

    class Runner:
        def __init__(self, config, output, isolation):
            caps.append(config['max_runs_per_cli'])
            self.config = config
            self.counts = {cli: {'agent': 0, 'judge': 0} for cli in providers.CLIS}

        def scenario(self, scenario, cli):
            self.counts[cli]['agent'] += 1
            return harness.empty_row(scenario, cli, self.config, 'completed')

    monkeypatch.setattr(harness, 'Runner', Runner)


def _argv(tmp_path, job, *extra, remote_flag='--data-repo'):
    state = tmp_path / 'state'
    repo = tmp_path / 'repo'
    return [
        job, remote_flag, str(repo), '--state-dir', str(state), '--date', DAY, *extra,
    ]


def _modes(path):
    return stat.S_IMODE(path.stat().st_mode)


def test_report_file_path_follows_the_job(tmp_path):
    for job, relative in (
        ('scenarios', f'reports/agent-scenarios/{DAY}.md'),
        ('ux', f'reports/ux/{DAY}.md'),
        ('aeo', f'aeo/runs/{DAY}/report.md'),
    ):
        path = tmp_path / relative
        path.parent.mkdir(parents=True)
        path.write_text('report')
        assert jobs.job_report_file(tmp_path, job, DAY) == path


def test_report_flags_are_refused_unless_paired(tmp_path, capsys):
    state = tmp_path / 'state'
    out = tmp_path / 'out'
    missing_out = jobs.main(['scenarios', '--no-publish', '--state-dir', str(state)])
    missing_flag = jobs.main(['scenarios', '--report-out', str(out), '--state-dir', str(state)])
    text = capsys.readouterr().out
    assert missing_out == 2 and missing_flag == 2
    assert text.count('--no-publish and --report-out must be set together') == 2
    assert not out.exists()


def test_report_flags_are_refused_with_dry_run(tmp_path, capsys):
    out = tmp_path / 'out'
    code = jobs.main([
        'scenarios', '--dry-run', '--no-publish', '--report-out', str(out),
        '--state-dir', str(tmp_path / 'state'),
    ])
    assert code == 2
    assert '--dry-run' in capsys.readouterr().out
    assert not out.exists()
    assert not (tmp_path / 'state' / 'dry-run').exists()


def test_shell_forwards_subscription_args_unchanged():
    text = (ROOT / 'qa/run-subscription-job.sh').read_text(encoding='utf-8')
    assert '-m qa.subscription_jobs "$@"' in text


def test_readme_describes_report_out_and_retired_gemini_skip():
    text = (ROOT / 'qa/README.md').read_text(encoding='utf-8')
    assert 'refuses until its engine set changes' not in text
    assert '--no-publish' in text and '--report-out' in text
    assert 'skipped (retired)' in text


def test_aeo_engine_file_must_still_name_gemini(tmp_path):
    config = jobs.configuration(tmp_path / 'state', max_runs=64)
    settings = {'monthly_cap_usd': 15, 'engines': {
        name: {'transport': 'subscription', 'cli': cli, 'model': config['clis'][cli]['model']}
        for name, cli in aeo.ENGINE_CLIS.items() if cli != 'gemini'
    }}
    settings['engines']['perplexity'] = {
        'model': 'sonar', 'key': 'op://test/sonar/credential',
        'price_in': 1, 'price_out': 1, 'search_fee': 0, 'est_call_usd': 0.007,
    }
    path = tmp_path / 'engines.yaml'
    path.write_text(yaml.safe_dump(settings))
    with pytest.raises(ValueError, match='four subscription engines'):
        aeo.engine_config(path, config)


def test_default_publication_is_unchanged_and_no_publish_skips_git_and_gh(tmp_path, monkeypatch, capsys):
    caps = []
    commands, bodies = _install_git(monkeypatch, DATA_REMOTE)
    _scenario_runner(monkeypatch, caps)
    published = jobs.main(_argv(tmp_path / 'publish', 'scenarios', '--cli', 'codex', '--scenario', 'alpha'))
    publish_commands = _publish_commands(commands)
    assert published == 0
    assert [command[3] if command[0] == 'git' else command[0] for command in publish_commands] == [
        'add', 'commit', 'push', 'gh',
    ]
    assert publish_commands[0][-3:] == ['add', '--', jobs.REPORT_PATHS['scenarios']]
    assert jobs.TRAILER in publish_commands[1][-1]
    assert publish_commands[2][-4:-1] == ['push', '-u', 'origin']
    assert 'https://github.com/report/1' in capsys.readouterr().out
    assert caps == [400]

    commands.clear()
    bodies.clear()
    caps.clear()
    out = tmp_path / 'out'
    out.mkdir(mode=0o755)
    code = jobs.main(_argv(
        tmp_path / 'local', 'scenarios', '--cli', 'codex', '--scenario', 'alpha',
        '--no-publish', '--report-out', str(out),
    ))
    assert code == 0
    assert _publish_commands(commands) == []
    assert any(_git_args(command)[:2] == ['worktree', 'remove'] for command in commands)
    assert _modes(out) == 0o700
    assert _modes(out / 'report.md') == 0o600
    assert _modes(out / 'body.md') == 0o600
    report = (out / 'report.md').read_text(encoding='utf-8')
    body = (out / 'body.md').read_text(encoding='utf-8')
    assert report.startswith('# Agent scenarios, 2026-10-04')
    assert body.startswith('# Agent scenarios')
    assert 'Vendor API spend: $0.00' in body
    assert body != report
    assert caps == [400]
    assert 'No git add' in capsys.readouterr().out


def test_no_publish_retains_the_worktree_when_the_job_fails(tmp_path, monkeypatch, capsys):
    commands, _bodies = _install_git(monkeypatch, DATA_REMOTE)
    monkeypatch.setattr(jobs, 'require_ready', lambda *a: {})
    monkeypatch.setattr(agent_harness, 'load_scenarios', lambda directory=None: [ALPHA])

    class Runner:
        def __init__(self, config, output, isolation):
            self.counts = {cli: {'agent': 0, 'judge': 0} for cli in providers.CLIS}

        def scenario(self, scenario, cli):
            raise ValueError('measurement failed')

    monkeypatch.setattr(harness, 'Runner', Runner)
    out = tmp_path / 'out'
    code = jobs.main(_argv(
        tmp_path, 'scenarios', '--cli', 'codex', '--scenario', 'alpha',
        '--no-publish', '--report-out', str(out),
    ))
    output = capsys.readouterr().out
    assert code == 2
    assert 'measurement failed' in output
    assert 'Publication incomplete' in output
    assert 'retained' in output
    assert any(_git_args(command)[:2] == ['worktree', 'add'] for command in commands)
    assert not any(_git_args(command)[:2] == ['worktree', 'remove'] for command in commands)
    assert _publish_commands(commands) == []
    assert not out.exists() or not any(out.iterdir())


def test_report_out_refuses_a_symlink_or_a_non_empty_directory(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(jobs, 'report_worktree', lambda *a: pytest.fail('worktree'))
    link = tmp_path / 'link'
    link.symlink_to(tmp_path / 'elsewhere', target_is_directory=True)
    occupied = tmp_path / 'occupied'
    occupied.mkdir()
    (occupied / 'keep').write_text('keep')
    symlink_code = jobs.main(_argv(
        tmp_path / 'a', 'scenarios', '--no-publish', '--report-out', str(link),
    ))
    occupied_code = jobs.main(_argv(
        tmp_path / 'b', 'scenarios', '--no-publish', '--report-out', str(occupied),
    ))
    text = capsys.readouterr().out
    assert symlink_code == 2 and occupied_code == 2
    assert 'symlink' in text and 'not empty' in text
    assert (occupied / 'keep').read_text() == 'keep'


def test_no_publish_still_refuses_gemini_quiet_hours_vendor_keys_and_missing_receipts(
    tmp_path, monkeypatch, capsys,
):
    monkeypatch.setattr(jobs, 'report_worktree', lambda *a: pytest.fail('worktree'))
    out = tmp_path / 'out'

    def invoke(*extra):
        return jobs.main([
            'aeo', '--business-repo', str(tmp_path / 'biz'), '--state-dir', str(tmp_path / 'state'),
            '--no-publish', '--report-out', str(out), *extra,
        ])

    assert invoke('--cli', 'gemini') == 2
    assert 'Google stopped serving Gemini CLI' in capsys.readouterr().out

    class Frozen(datetime):
        @classmethod
        def now(cls, tz=None):
            return datetime(2026, 10, 4, 10, 0, tzinfo=tz)

    monkeypatch.setattr(harness, 'datetime', Frozen)
    assert invoke('--cli', 'codex', '--quiet-hours') == 2
    assert 'Quiet hours' in capsys.readouterr().out

    monkeypatch.setenv('OPENAI_API_KEY', '')
    assert invoke('--cli', 'codex') == 2
    assert 'vendor API-key' in capsys.readouterr().out
    monkeypatch.delenv('OPENAI_API_KEY')

    assert invoke('--cli', 'codex') == 2
    assert 'doctor receipt' in capsys.readouterr().out
    assert not out.exists()


def test_no_publish_still_waits_on_the_job_lock(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(jobs, 'report_worktree', lambda *a: pytest.fail('worktree'))
    elapsed = [0.0]
    monkeypatch.setattr(time, 'monotonic', lambda: elapsed[0])

    def sleep(seconds):
        elapsed[0] += seconds

    monkeypatch.setattr(time, 'sleep', sleep)
    state = harness.private_output(tmp_path / 'state')
    state.mkdir()
    with (state / 'subscription-jobs.lock').open('a') as holder:
        fcntl.flock(holder, fcntl.LOCK_EX | fcntl.LOCK_NB)
        code = jobs.main([
            'aeo', '--cli', 'codex', '--business-repo', str(tmp_path / 'biz'),
            '--state-dir', str(state), '--no-publish', '--report-out', str(tmp_path / 'out'),
        ])
    assert code == 2
    assert elapsed[0] == 21600
    assert 'lock' in capsys.readouterr().out.lower()


def _engines(directory, config):
    settings = {'monthly_cap_usd': 15, 'max_output_tokens': 2000, 'engines': {
        name: {'transport': 'subscription', 'cli': cli, 'model': config['clis'][cli]['model']}
        for name, cli in aeo.ENGINE_CLIS.items()
    }}
    settings['engines']['perplexity'] = {
        'model': 'sonar', 'key': 'op://test/sonar/credential',
        'price_in': 1, 'price_out': 1, 'search_fee': 0, 'est_call_usd': 0.007,
    }
    path = directory / 'aeo'
    path.mkdir(parents=True, exist_ok=True)
    (path / 'engines.yaml').write_text(yaml.safe_dump(settings))
    (path / 'prompts.yaml').write_text('prompts\n')


def test_no_publish_aeo_keeps_the_64_cap_partial_label_and_writes_no_baseline(
    tmp_path, monkeypatch, capsys,
):
    config = jobs.configuration(tmp_path / 'models', max_runs=64)
    trees = []
    commands, _bodies = _install_git(
        monkeypatch, BUSINESS_REMOTE, on_worktree=lambda dest: (_engines(dest, config), trees.append(dest)),
    )
    monkeypatch.setattr(jobs, 'require_ready', lambda *a: {})
    monkeypatch.setattr(aeo, 'require_ready', lambda *a: {})
    monkeypatch.setattr(aeo.inventory, 'load', lambda path: [
        {'id': 'test', 'text': 'Choose a model', 'cluster': 'category', 'success': 'mentioned'},
    ])
    monkeypatch.setattr(aeo.engines, 'op_read', lambda ref: 'dummy')
    monkeypatch.setattr(
        aeo.engines, 'perplexity_call',
        lambda model, secret, prompt, cap: Answer('ModelSpec', 'sonar', reported_cost_usd=0.007),
    )
    caps = []

    def refusal(self, cli, role):
        caps.append(self.config['max_runs_per_cli'])
        return 'max_runs', 'CLI invocation quota reached (includes judges)'

    monkeypatch.setattr(harness.Runner, 'refusal', refusal)
    monkeypatch.setattr(harness, 'launch', lambda *a, **k: pytest.fail('CLI started'))
    out = tmp_path / 'out'
    code = jobs.main([
        'aeo', '--business-repo', str(tmp_path / 'biz'), '--state-dir', str(tmp_path / 'state'),
        '--date', DAY, '--no-publish', '--report-out', str(out),
    ])
    assert code == 0, capsys.readouterr().out
    assert caps and set(caps) == {64}
    assert _publish_commands(commands) == []
    tree = trees[-1]
    assert not (tree / 'aeo/runs/BASELINE').exists()
    rows = (tree / 'aeo/runs' / DAY / 'runs.jsonl').read_text(encoding='utf-8')
    assert 'skipped (retired)' in rows
    report = (out / 'report.md').read_text(encoding='utf-8')
    assert report.startswith(f'# Answer-engine visibility, {DAY} (partial)')
    assert report == (tree / 'aeo/runs' / DAY / 'report.md').read_text(encoding='utf-8')
    assert (out / 'body.md').read_text(encoding='utf-8') == report
    assert '**gemini: skipped**: retired' in report
