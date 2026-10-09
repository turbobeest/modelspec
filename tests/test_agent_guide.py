"""Agent entry context stays small, generated, and faithful to the contracts."""
import asyncio
import copy
import json

import pytest
import yaml

from pipeline import agent_copy, agent_ready, live
from pipeline.agent_overhead import ROOT, measure, tokens
from decision.contract import parse_spec
from decision.registry import default
from api.worker import openapi
from qa.agent_harness import agent_context, agent_tools, HttpTools
from qa.contracts import capture_tools
from tests.test_x402 import entry, _entry_env, _Req  # noqa: F401


def test_conduct_rules_are_on_every_agent_surface():
    """MODEL-320: the eight conduct rules, verbatim, on each surface an agent reads."""
    from datetime import date

    from pipeline.build import llms_txt
    from pipeline.export import Build

    rules = agent_copy.CONDUCT_RULES
    assert len(rules) == 8
    copy = agent_copy.copy()
    spec = yaml.safe_load((ROOT / 'api/worker/openapi.yaml').read_text())
    openapi_descriptions = []
    for operations in spec['paths'].values():
        for operation in operations.values():
            if isinstance(operation, dict) and isinstance(operation.get('description'), str):
                openapi_descriptions.append(operation['description'])
    cli = agent_copy.cli_text()
    surfaces = {
        'agents.md': agent_copy.guide()[1],
        'llms.txt': llms_txt(
            site='ModelSpec', base='https://modelspec.dev',
            build=Build(commit='a' * 12, built_at='2026-10-04T00:00:00+00:00',
                        as_of=date(2026, 10, 4))),
        'MCP tool descriptions': '\n'.join(copy['tools'].values()),
        'OpenAPI descriptions': '\n'.join(openapi_descriptions),
        'CLI help': '\n'.join(cli['help'].values()) + '\n' + cli['answers'],
    }
    for name, text in surfaces.items():
        for rule in rules:
            assert rule in text, (name, rule)


def test_generated_guide_and_constants_are_stable_and_within_budget():
    from api.worker.src.agent_guide import GUIDE_URL, GUIDE_VERSION
    version, markdown = agent_copy.guide()
    assert (version, markdown) == agent_copy.guide()
    assert version == GUIDE_VERSION
    assert GUIDE_URL in markdown
    assert agent_copy.GUIDE_OUT.read_text() == markdown
    assert tokens(markdown) <= 4000
    data = agent_copy.copy()
    assert data['guide_version'] == version
    assert tokens(data['instructions']) <= 1000
    assert all(tokens(d) <= 1500 for d in data['tools'].values())
    assert "at most 16 KB" in markdown
    assert "POST /v1/decide without `fields`" in markdown
    assert "explanation.fetch" in data["tools"]["decide"]
    # Client snippets are part of the versioned source, with explicit loading rules.
    for snippet in ('CLAUDE.md', 'AGENTS.md', '.cursor/rules/modelspec.mdc',
                    'initialize.result.instructions', 'tools/list'):
        assert snippet in markdown


def test_coverage_pointer_keeps_all_three_mcp_first_turns_under_budget(capsys):
    """Each provider's first MCP turn stays within 10,000 estimated tokens."""
    from qa.agent_harness import main
    assert main(["--first-turn-breakdown"]) == 0
    report = json.loads(capsys.readouterr().out)
    assert set(report) == {"claude", "openai", "gemini"}
    assert all(row["total"] <= 10_000 for row in report.values()), report
    guide = agent_copy.copy()["context_guide"]
    assert guide.count("https://modelspec.dev/api/coverage.json") == 1
    assert "catalogued_not_decidable" not in guide
    assert len(guide) <= 8648  # The MODEL-308 entry guide was 8,648 characters.


def test_all_guide_specs_parse_against_the_registry():
    registry = default()
    parse_spec(agent_copy.MINIMAL_SPEC, facets=registry.facet)
    examples = agent_copy.guide_examples()
    assert len(examples) == 4
    for row in examples:
        parsed = parse_spec(row['spec'], facets=registry.facet)
        assert parsed.spec_version == 1
    hardware = examples[2]['spec']['where'][-1]
    assert hardware['in'][0] in registry.allowed_values(registry.facet(hardware['facet']))
    # Validate the actual fenced JSON an agent reads, not just generator objects.
    import re
    for fenced in re.findall(r'```json\n(.*?)\n```', agent_copy.guide()[1], re.S):
        parse_spec(json.loads(fenced), facets=registry.facet)


def test_guide_changes_get_a_new_version():
    tiers = copy.deepcopy(agent_copy._tiers())
    tiers['credits']['weights']['decide.summary'] += 1
    assert agent_copy.guide(tiers)[0] != agent_copy.guide()[0]


def test_schema_compaction_preserves_every_original_rule():
    original = openapi.apply_agent_copy(openapi.build_spec())
    compacted = openapi.compact_schemas(copy.deepcopy(original))
    shared = {k: v for k, v in compacted['components']['schemas'].items() if k.startswith('Shared')}
    assert shared

    def expand(node):
        if isinstance(node, dict):
            if set(node) == {'$ref'} and node['$ref'].split('/')[-1] in shared:
                return expand(shared[node['$ref'].split('/')[-1]])
            return {k: expand(v) for k, v in node.items()}
        if isinstance(node, list):
            return [expand(v) for v in node]
        return node

    for key in shared:
        compacted['components']['schemas'].pop(key)
    assert expand(compacted) == original


def test_openapi_size_and_all_response_header_descriptions():
    text = (ROOT / 'api/worker/openapi.yaml').read_text()
    # MODEL-291 baseline 249,369 bytes; resulting file 217,392 bytes.
    # MODEL-293 adds the bounded representation (DecideRequest, ProjectedResult,
    # BoundedDecision, ModelEvidence, BoundedExplanation, BoundedRefused): about
    # 9 KB, already with copied properties pointing at their sources. 226,428 bytes.
    # MODEL-308 adds the typed aggregate coverage block, about 1.8 KB.
    # MODEL-316 adds rank's deprecation block and decide's relax_task_tokens,
    # about 1.3 KB and 300 tokens.
    assert len(text.encode()) <= 233_000
    assert tokens(text) <= 58_300
    spec = yaml.safe_load(text)
    assert agent_copy.GUIDE_URL in spec['info']['description']
    for path, operations in spec['paths'].items():
        if path.startswith('/v1/'):
            for operation in operations.values():
                for response in operation['responses'].values():
                    assert {'Link', 'x-modelspec-guide-version'} <= response['headers'].keys()


@pytest.mark.parametrize('path,method,body', [
    ('/v1/rank', 'POST', 'invalid JSON'), ('/v1/decide', 'POST', 'invalid JSON'),
    ('/v1/rank', 'OPTIONS', None), ('/v1/rank', 'DELETE', None),
    ('/v1/unknown', 'GET', None), ('/v1/human-status', 'GET', None),
])
def test_real_worker_responses_link_the_guide(entry, path, method, body):  # noqa: F811
    worker = entry.Default()
    worker.env = _entry_env(X402_ENABLED='false')
    response = asyncio.run(worker.fetch(_Req(path, body, method, {
        'origin': 'https://modelspec.dev', 'accept-encoding': 'br'})))
    headers = {k.lower(): v for k, v in response.headers.items()}
    assert headers['link'] == '<https://modelspec.dev/agents.md>; rel="describedby"'
    assert headers['x-modelspec-guide-version'] == agent_copy.guide()[0]
    assert 'Link' in headers['access-control-expose-headers']


def test_compact_and_control_prompts_and_http_tools():
    full = (ROOT / 'api/worker/openapi.yaml').read_text()
    for interface in ('mcp', 'http'):
        compact = agent_context(interface)
        assert agent_copy.copy()['context_guide'] in compact
        assert agent_copy.guide()[1].partition('\n## Worked Specs\n')[0] in compact
        assert full not in compact
        assert 'https://modelspec.dev/openapi.yaml' in compact
        assert tokens(compact) <= 4100
        assert full in agent_context(interface, control_full_spec=True)
    tools = capture_tools()['tools']
    assert agent_tools(tools, 'mcp') == tools
    http = agent_tools(tools, 'http')
    assert {t['name'] for t in http} == {t['name'] for t in tools}
    assert all(t['input_schema'] == {'type': 'object', 'additionalProperties': True} for t in http)
    assert 'POST /v1/decide' in next(t['description'] for t in http if t['name'] == 'decide')
    assert tokens(json.dumps(http)) < 1000
    raw = {'task': 'unsupported requirement', 'where': []}
    # HTTP preserves unsupported fields for the server's recovery hints.
    assert HttpTools.prepare(None, 'decide', raw) == raw


def test_guide_survives_the_live_tree_copy():
    assert 'agents.md' in live.KEEP_FILES
    assert 'agents.md' in live.DISCOVERY


@pytest.mark.parametrize('interface,control', [('mcp', False), ('http', False), ('mcp', True), ('http', True)])
def test_harness_prompt_arms_replay_offline(monkeypatch, tmp_path, interface, control):
    import httpx
    from qa.agent_harness import main, load_scenarios

    def forbidden(*args, **kwargs):
        raise AssertionError('Prompt arm attempted network I/O')

    monkeypatch.setattr(httpx.Client, 'request', forbidden)
    args = ['--dry-run', '--interface', interface, '--agent', 'openai',
            '--scenario', load_scenarios()[0]['id'], '--output-dir', str(tmp_path),
            '--date', '2026-10-03']
    if control:
        args.append('--control-full-spec')
    assert main(args) == 0
    report = json.loads((tmp_path / '2026-10-03-agent-scenarios.json').read_text())
    assert report['metadata']['interface'] == interface
    assert report['metadata']['control_full_spec'] is control
    assert report['metadata']['guide_version'] == agent_copy.guide()[0]
    assert report['budget']['real_spend_usd'] == 0
