"""The public recipe for choosing models for an orchestrator's sub-tasks."""

from __future__ import annotations

import html
import json
from pathlib import Path

from decision.templates import template_by_id
from pipeline import agent_copy, brand, landing_chrome

PATH = "/orchestrators/"
TITLE = "Choose models for your orchestrator"
DESCRIPTION = "A system prompt and worked Spec for a frontier-model orchestrator that uses ModelSpec to choose models for each job or role."

SYSTEM_PROMPT = """Use ModelSpec when choosing models for a sub-task or role.
Orient once with `modelspec help agent --json` and read the agent guide.
Call decide once per job or role, rather than once per inference request.

Translate the user's requirements into a Spec. Put exclusion gates in where
and ranking preferences in optimize.weights. A '-' prefix on a numeric
weight key means less is better. Never invent gates, facet names, weights,
or numeric tradeoffs. Free-text task is rejected. Find an unknown facet with
`modelspec vocab --search 'software engineering' --json`.
Start from a registry template, for example
`modelspec decide --template coding-balanced --json`, only when its gates
and preferences match the user's requirements. Otherwise adapt its Spec.
Use `modelspec decide --spec role.json --json` for your saved Spec.
Size task_tokens for the user's workload and state any assumptions.

On the first answer, save decision_id, snapshot, the Spec, and the answer in
the orchestrator's job state. Set the Spec's snapshot to that returned ID
for reproducible retries. ModelSpec's CLI does not cache decisions for you.

Check status before reading ranks. For no_feasible, propose relaxing only
a constraint the user stated, one at a time, using the returned relax hints.
Say what changed and why. A retry does not verify a removed requirement.
For partial or coverage, report what is missing rather than choosing a winner.
A non-separable tie has no single winner. Preserve every answer.members
member and offer next_move when present. Do not promote one from memory.
may_qualify means unknown, not a pass. A null cost is unknown, never zero.
Cite only returned evidence. Present summary_for_user unchanged and retain
every must_mention item. Follow reading.do_not_claim and explanation.fetch.
An omitted row is not an elimination.

Use the recommended best band for an actionable answer. If the user has
authorized routing among tied members, preserve the tie in the report and
route within that band without claiming a single best model. Otherwise
offer the returned next steps before dispatching. Export a config with
`modelspec decide --spec role.json --emit-router-config json --out router.json`.
Check exported placeholders and resolve missing verified IDs before use.

When requirements change, update the Spec and decide again. When the snapshot
moves, compare the saved Spec with `modelspec compare --spec role.json --to snap_SAVED --json`.
Replace snap_SAVED with the retained snapshot ID from the saved answer.
If comparison_snapshot_unavailable is returned, follow next. For a fresh
decision, remove the old snapshot pin, decide on the current snapshot, and
pin the returned ID again. State that no historical comparison was available.
Save the new decision_id and snapshot before using the new band.

After acting, submit feedback with
`modelspec feedback dec_SAVED --rating reliable` only if that rating fits
the observed result. Replace dec_SAVED with the saved decision_id. Never
include prompts, credentials, or personal details in feedback.
If the CLI exits 5, stop and tell the human about the key problem. Use
`modelspec key` for access instructions. Do not bypass keyed access.
"""


def _code(text: str) -> str:
    return f"<pre><code>{html.escape(text)}</code></pre>"


def page() -> str:
    example = json.dumps(template_by_id("coding-balanced")["spec"], indent=2)
    commands = "\n".join((
        "modelspec decide --spec role.json --emit-router-config litellm --out router.yaml",
        "modelspec decide --spec role.json --emit-router-config openrouter --out guardrail.json",
        "modelspec decide --spec role.json --emit-router-config json --out router.json",
    ))
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<title>{TITLE} · ModelSpec</title><meta name="description" content="{DESCRIPTION}">'
        f'<link rel="canonical" href="https://modelspec.dev{PATH}">'
        f'{brand.head_links()}{brand.social_meta(TITLE, path=PATH)}'
        '<link rel="stylesheet" href="/landing-assets/landing.css">'
        '<link rel="stylesheet" href="/landing-assets/method.css">'
        '<link rel="stylesheet" href="/landing-assets/orchestrators.css">'
        f'{landing_chrome.lockup_style()}</head><body>'
        '<div class="axis" aria-hidden="true"></div>'
        f'<header class="site-head">{landing_chrome.lockup()}<nav>'
        '<a href="/method/">How it decides</a><a href="/agents.md">Agent guide</a>'
        '<a href="/pricing/">Pricing</a></nav></header>'
        '<main class="orchestrator-recipe"><p class="eyebrow">Orchestrator recipe</p>'
        f'<h1>{TITLE}</h1>'
        '<p>Give your frontier-model orchestrator a model-selection step for each sub-task or role. '
        'ModelSpec is not a per-request router. Call it once per job or role, save the '
        '<code>decision_id</code> and <code>snapshot</code> in your job state, then route among '
        'the recommended band. Re-decide when requirements change or the snapshot moves.</p>'
        '<p>Machine access is keyed. Only human lookup is free. Get access through '
        '<a href="/pricing/">pricing</a> or <code>modelspec key</code>. Install the '
        '<code>modelspec-dev</code> package using the <a href="/agents.md">agent guide</a>.</p>'
        '<section id="prompt"><h2>Add this to the orchestrator system prompt</h2>'
        '<p>Copy the block into the orchestrator instructions. The filenames and IDs are '
        'placeholders for your job state, not published decisions.</p>'
        f'{_code(SYSTEM_PROMPT)}</section>'
        '<section id="example"><h2>Work through a coding role</h2>'
        '<p>This Spec comes directly from the registry template <code>coding-balanced</code>. '
        'Its numeric gates and weights are template assumptions, not measured results or '
        'requirements to add silently. Use it only if the user accepts those assumptions. '
        'Otherwise keep only the requirements the user stated and adjust the preferences '
        'to match. Save the JSON as <code>role.json</code>.</p>'
        f'{_code(example)}'
        '<p>The first call can use the current snapshot. Run '
        '<code>modelspec decide --spec role.json --json</code>, then add the returned '
        '<code>snapshot</code> ID to the Spec. Save the answer alongside its '
        '<code>decision_id</code>. State the workload assumptions behind cost estimates.</p>'
        '<p>The following is illustrative control flow, not a captured decision or a model recommendation. '
        'Suppose the bounded answer has <code>status: partial</code>, '
        '<code>answer.kind: tied</code>, and <code>next_move.kind: decide_by_testing</code>. '
        'The orchestrator reports <code>summary_for_user</code> unchanged, retains every '
        '<code>must_mention</code> item, and offers the returned test steps for the returned '
        'candidates. It does not dispatch a supposed winner. Those fields decide the next '
        'action even if a result row has the highest rank.</p>'
        '<p>For this role, handle the bounded answer as follows:</p>'
        '<ol><li>Read <code>status</code> and <code>coverage</code>. If there is no feasible '
        'answer, report the blocker and propose a stated constraint to relax. If the answer '
        'is partial, report the missing evidence.</li>'
        '<li>Read <code>answer</code>, <code>summary_for_user</code>, and '
        '<code>must_mention</code>. If <code>answer.kind</code> is <code>tied</code>, '
        'report all members without selecting a winner. Offer <code>next_move</code> when '
        'present. Dispatch among tied members only under the user\'s routing authorization.</li>'
        '<li>For an actionable answer, retain <code>bands.best</code> as the allowed band. '
        'Keep unknown costs unknown. Follow <code>explanation.fetch</code> if the required '
        'evidence was omitted. Never infer exclusions from omitted rows.</li>'
        '<li>Export the band, check unresolved IDs, and record observed feedback after use. '
        'Re-decide for changed requirements. Use <code>modelspec compare --spec role.json '
        '--to snap_SAVED --json</code> to compare against the saved snapshot when retained '
        'snapshots are available. This deployment may return '
        '<code>comparison_snapshot_unavailable</code>. Follow its next steps and request a '
        'current decision without claiming a historical comparison. Remove the old '
        'snapshot pin for that fresh call, then pin the returned ID again.</li></ol></section>'
        '<section id="export"><h2>Export the recommended band</h2>'
        '<p>LiteLLM and OpenRouter are config-export targets. Choose the format your '
        'application consumes. These commands request a decision and export its best band. '
        'Use the saved Spec with its pinned snapshot. An export preserves membership, '
        'not proof of a unique winner. It does not run inference.</p>'
        f'{_code(commands)}'
        '<p>Missing verified provider IDs remain explicit placeholders. Resolve them before '
        'using a config. Do not substitute an ID from memory.</p></section>'
        '<section id="mcp"><h2>Use MCP instead of the CLI</h2>'
        '<p>For a tool-calling orchestrator, connect to '
        '<code>https://api.modelspec.dev/mcp</code> with an '
        '<code>Authorization: Bearer &lt;MODELSPEC_API_KEY&gt;</code> header. '
        'The Spec itself is the <code>decide</code> tool arguments. Do not wrap it in '
        '<code>spec</code> or <code>task</code>.</p>'
        f'<p>{html.escape(agent_copy.BOUNDED_MCP)}</p>'
        '<p>Print a client-specific setup snippet with '
        '<code>modelspec setup mcp --client generic</code>. Replace <code>generic</code> '
        'with a supported client from the <a href="/agents.md">agent guide</a>. '
        'Configure the key in that client\'s environment or secret settings. '
        'CLI authentication does not configure another client.</p></section></main>'
        f'{landing_chrome.footer()}</body></html>\n'
    )


def write(tree: Path) -> dict:
    destination = tree / "orchestrators/index.html"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(page(), encoding="utf-8")
    stylesheet = Path(__file__).parent / "landing_assets/orchestrators.css"
    (tree / "landing-assets/orchestrators.css").write_text(stylesheet.read_text(), encoding="utf-8")
    return {"sitemap_paths": [PATH]}
