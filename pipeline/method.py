"""Build the public methodology page from the landing page's data."""

from __future__ import annotations

import html
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from api.ranking.engine import neutrality_commitment
from decision.snapshot import SnapshotIntegrityError, load_public_keys, load_snapshot_bytes
from pipeline import brand, landing_chrome
from pipeline.landing import LandingData

PAGE_PATH = Path("method/index.html")
ASSET_PATH = Path("landing-assets/method.css")
KEYS_REL = Path("decision/snapshot_keys.json")
SNAPSHOT_REL = Path("api/decision/snapshot.json.gz")
GH = "https://github.com/turbobeest/modelspec/blob/main/"
GH_TREE = "https://github.com/turbobeest/modelspec/tree/main/"


def load_key_ids(root: Path) -> tuple[str, ...]:
    return tuple(load_public_keys(root / KEYS_REL))


@dataclass(frozen=True)
class SigningState:
    published_key_ids: tuple[str, ...]
    signed_key_id: str | None


def load_signing_state(tree: Path, root: Path) -> SigningState:
    """Report a signature only when the CLI's own verifier accepts the built snapshot."""
    public_keys = load_public_keys(root / KEYS_REL)
    key_ids = tuple(public_keys)
    snapshot = tree / SNAPSHOT_REL
    if not (public_keys and snapshot.is_file()):
        return SigningState(key_ids, None)
    try:
        loaded = load_snapshot_bytes(
            snapshot.read_bytes(), key=None, public_keys=public_keys, source=str(snapshot),
        )
    except SnapshotIntegrityError:
        return SigningState(key_ids, None)
    return SigningState(key_ids, loaded.signature_key_id if loaded.signature_verified else None)


def _sources(rows: tuple[tuple[str, str, str], ...]) -> str:
    links = ""
    for path, what, anchor in rows:
        href = (GH_TREE if path.endswith("/") else GH) + path.rstrip("/")
        href += f"#{anchor}" if anchor else ""
        links += (f'<li><a href="{href}"><code>{html.escape(path)}</code></a>'
                  f'<span>{what}</span></li>')
    return f'<div class="checks"><p>Check it</p><ul>{links}</ul></div>'


def _tie_plot(data: LandingData) -> str:
    models = sorted(data.models, key=lambda row: (-row.estimate, row.cost, row.id))[:8]
    low, high = min(row.low for row in models), max(row.high for row in models)
    span = high - low or 1
    sx = lambda value: 150 + (value - low) / span * 570
    rows = ""
    for index, model in enumerate(models):
        y = 58 + index * 40
        colour = ("#F2C94C" if model.id == data.leader_id else
                  "#3FB68B" if model.tied else "#5f6f8c")
        status = ("leader" if model.id == data.leader_id else
                  "tied" if model.tied else "thin" if model.thin else "apart")
        name = model.name if len(model.name) <= 19 else model.name[:17] + "…"
        rows += (f'<text x="138" y="{y + 5}" text-anchor="end">{html.escape(name)}</text>'
                 f'<line x1="{sx(model.low):.1f}" y1="{y}" x2="{sx(model.high):.1f}" '
                 f'y2="{y}" stroke="{colour}"/><circle cx="{sx(model.estimate):.1f}" '
                 f'cy="{y}" r="6" fill="{colour}"/><text class="status" x="730" '
                 f'y="{y + 5}" fill="{colour}">{status}</text>')
    others = len(data.tie) - 1
    label = (f"Estimated coding ability, with 80% ranges. {others} other "
             f"{'model' if others == 1 else 'models'} can't be told apart from the top estimate.")
    return (f'<svg class="tie-plot" viewBox="0 0 772 420" role="img" aria-label="{label}">'
            '<rect width="772" height="420" rx="6"/><line class="axis-y" x1="150" y1="24" x2="150" y2="370"/>'
            '<line class="axis-x" x1="150" y1="370" x2="752" y2="370"/>'
            + rows + '<text class="axis-label" x="450" y="400" text-anchor="middle">estimated ability in one domain, higher is better</text></svg>')


def _signing(signing: SigningState) -> str:
    if signing.signed_key_id:
        key_id = html.escape(signing.signed_key_id)
        return ('<div class="terminal"><span>reproduce a decision through the API</span><pre>'
                'POST https://api.modelspec.dev/v1/decide\n'
                '  "snapshot": "[SNAPSHOT ID]",\n  "spec_hash": "sha256:[SPEC HASH]",\n'
                '  "signature_verified": true</pre></div><div class="key">'
                f'<h3>Public signing key</h3><p>This snapshot is Ed25519-signed with published '
                f'key ID <code>{key_id}</code>. The signature was verified when this page was '
                'built. Use the hosted API to reproduce a decision against this snapshot.</p>'
                '<p>The content hash is checked separately.</p></div>')
    if signing.published_key_ids:
        ids = ", ".join(f"<code>{html.escape(key_id)}</code>"
                        for key_id in signing.published_key_ids)
        state = (f"<p>A public signing key is published (id {ids}); this snapshot is not "
                 "signed with it. Signing key being re-issued.</p>")
    else:
        state = "<p><strong>Signing key being re-issued.</strong></p>"
    return f'<div class="key"><h3>Public signing key</h3>{state}</div>'


def _section(section_id: str, number: str, title: str, lede: str,
             content: str, *, theme: str) -> str:
    return (f'<section id="{section_id}" class="method-section {theme}"><div class="intro">'
            f'<code>{number}</code><h2>{title}</h2><p>{lede}</p></div>'
            f'<div class="content">{content}</div></section>')


def page(data: LandingData, signing: SigningState) -> str:
    tied = len(data.tie) - 1
    claims = (
        ("#estimate", "Your model is a guess.", "The estimate"),
        ("#ties", f"The evidence can't tell {tied} of these {'model' if tied == 1 else 'models'} "
                  "apart from the top one.", "Ties"),
        ("#evidence", "Every number is one click from its source.", "Evidence"),
        ("#unknown", "Unknown means unknown.", "Unknowns"),
        ("#neutrality", "Nobody pays to rank higher.", "Neutrality"),
        ("#dont", "A different job from a router.", "What we don't do"),
    )
    claim_links = "".join(f'<a href="{href}"><b>{html.escape(claim)}</b><span>{where}</span></a>'
                          for href, claim, where in claims)
    commitment = neutrality_commitment()
    assertions = "".join(
        f'<li><code>{html.escape(key)}</code><b>false</b></li>'
        for key in commitment["assertions"]
    )
    evidence = ('<h3>Cards and benchmark pages</h3><p>Model cards hold the measurements, one '
                'record per result. Benchmark pages say what each benchmark measures, and which '
                'domains it counts toward.</p><h3>Who measured it</h3><p>Every measurement '
                'carries one of three labels. A lab\'s claim about its own model sits beside '
                'independent results, labelled, never mixed in unmarked.</p><div class="code-list">'
                '<code>benchmark_author</code><span>The benchmark\'s own authors.</span>'
                '<code>independent_evaluator</code><span>An evaluator outside the lab.</span>'
                '<code>provider_self_report</code><span>The lab or provider, about its own model.</span>'
                '</div><div class="callouts"><article><h3>Two keys before anything counts</h3>'
                '<p>A record enters the snapshot only when a second check agrees with the first, '
                'and that check was made by a deterministic tool or by a model from a different '
                'family.</p></article><article><h3>What never enters</h3><p>A value whose latest '
                'check isn\'t "verified", anything without a registered source URL, anything from '
                'an excluded source, or the old flat score block on each card.</p></article></div>'
                '<h3>Sources we exclude</h3><p>Two publishers whose terms don\'t permit our use '
                'were removed on 24 September 2026, with every value and benchmark they own. A '
                'test fails the build if either comes back, and the snapshot build scans its own '
                'output with the same rules.</p>' + _sources((
                    ("models/", "the model cards", ""),
                    ("benchmarks/", "benchmark pages and domain tags", ""),
                    ("schema/card.py", "source_kind: the three measurer labels", ""),
                    ("decision/model.py", "sources required; the two-key rule", ""),
                    ("tests/test_removed_sources.py", "keeps excluded sources out", ""))))
    basis = ('<h3>What <code>evidence_basis</code> means</h3><p>The rank export and the '
             '<code>/v1/rank</code> API label each row\'s inputs with '
             '<code>evidence_basis</code>. The label describes the inputs. It is not a verdict '
             'on the model.</p><div class="code-list">'
             '<code>none</code><span>No usable measurement contributed.</span>'
             '<code>unverified-legacy</code><span>Every input is an older card value.</span>'
             '<code>mixed</code><span>Reviewed and older values both contribute.</span>'
             '<code>partial-verified</code><span>Every input is reviewed, but some the profile asks for are missing.</span>'
             '<code>verified</code><span>Every weighted benchmark is present and reviewed.</span>'
             '</div>' + _sources((("pipeline/ranking.py", "_basis(): the evidence_basis labels", ""),)))
    evidence += basis
    rules = (("No benchmark names in the code", "The fit reads which domains a benchmark counts toward from that benchmark's own page, tagged direct or proxy."),
             ("Direct counts more than proxy", "A direct measurement loads at 1, a proxy at 0.35, so a proxy carries 0.1225 of a direct one's precision."),
             ("Old evidence counts less", "A measurement's precision halves every 365 days, down to a floor of a quarter."),
             ("Every estimate has a range", "A central 80% range: the estimate ± 1.2816 standard deviations."),
             ("No evidence, no estimate", "A model with nothing measured in a domain gets no estimate there."),
             ("A higher score never hurts", "The weights don't depend on the scores."))
    estimate = '<div class="rule-grid">' + "".join(
        f'<article><h3>{title}</h3><p>{text}</p></article>' for title, text in rules
    ) + '</div>' + _sources((
        ("decision/capability.py", "fit_capabilities(): the fit itself", ""),
        ("docs/design/capability-model.md", "why this model, and its rules", ""),
        ("docs/validation/capability-model.md", "the held-out test report", "")))
    tie_rules = ('<div class="rule-grid"><article><h3>Overlap with any other model</h3>'
                 '<p>A row is flagged <code>not_separable</code> when its range overlaps the '
                 'range of any other model in the domain being ranked, not only the leader\'s. '
                 'Two models can be told apart from the leader and still not from each other. '
                 'The board names the models the evidence cannot separate. The API keeps a stable transport order '
                 'so a list can travel. Read the flag before the rank.</p></article>'
                 '<article><h3>Inside a tie, choose on something else</h3><p>Ability cannot split '
                 'a tied group. Price, context, licence and the other facets you set can, and '
                 'the board shows them for every row.</p></article></div>')
    thin = sum(model.thin for model in data.models)
    ties = (f'<figure>{_tie_plot(data)}<figcaption>{tied} of the other '
            f'{len(data.models) - 1} models are at least 25% likely to score as well as '
            f'{html.escape(data.leader.name)}. That is the front-page figure, counted against '
            f'the top estimate only. {thin} more have too little evidence to count, however '
            f'high their estimate. Of the {tied + 1}, {html.escape(data.cheapest.name)} is '
            f'cheapest.</figcaption></figure>'
            + tie_rules
            + _sources((("decision/bands.py", "the tie: P(B ≥ leader) and the thin threshold", ""),
                        ("decision/engine.py", "where not_separable is set", ""),
                        ("decision/capability.py", "deterministic_probabilities()", ""),
                        ("docs/decision-contract.md", "p_best and top3_stability", "a-result"))))
    settings = (("Doesn't matter", "The default. The row stays on the board, greyed, so you can always see what you didn't choose."),
                ("Must", "A hard gate, with a threshold where the facet has one: context of at least 200K, a cost cap, a signed BAA. A model that fails is excluded, and stays on screen as excluded."),
                ("Prefer", "A weight. It orders the models that passed every Must. It never removes one."))
    must_prefer = '<div class="setting-grid">' + "".join(
        f'<article><h3>{title}</h3><p>{text}</p></article>' for title, text in settings
    ) + ('</div><p><b>For agents, in a spec.</b> Musts are the conditions under '
         '<code>where</code>. Prefers are the weights under <code>optimize</code>. A condition '
         'marked <code>soft(penalty)</code> is a preference too.</p>') + _sources((
             ("docs/design/briefs/2026-09-27-facet-board.md", "the three settings, and why", "principles"),
             ("decision/filter.py", "no condition adds a score", ""),
             ("docs/decision-contract.md", "soft conditions", "soft-conditions")))
    states = (("Known", "A value with a source, and a check that passed.", "Used."),
              ("Unknown, on ability or a spec such as context", "Nobody has published it, or it hasn't been collected yet.", "May qualify: listed beside the answer, not ranked, never scored as zero."),
              ("Unknown, on your data or the licence", "We can't confirm the provider's terms.", "Not treated as met. Shown as unverified, may qualify, so you can check it yourself."),
              ("Inapplicable", "The model's class can't have it. A model that writes no text has no output-token limit.", "Derived from the class, never typed on a card."))
    unknown = ('<table><thead><tr><th>The value is</th><th>Which means</th><th>What the answer '
               'does</th></tr></thead><tbody>' + "".join(
                   f'<tr><th>{a}</th><td>{b}</td><td>{c}</td></tr>' for a, b, c in states
               ) + '</tbody></table><aside><h3>Never inapplicable: how a model is built</h3>'
               '<p>A closed model still has layers and parameters. Nobody has published them. '
               'That is unknown, not meaningless, so architecture fields are never marked '
               'inapplicable.</p></aside>' + _sources((
                   ("decision/filter.py", "pass, fail and unknown", ""),
                   ("docs/decision-contract.md", "what an unknown does", "unknown-values"),
                   ("schema/applicability.py", "inapplicable, derived from the class", ""))))
    reproducible = ('<div class="rule-grid"><article><h3>The snapshot is fixed</h3><p>Every '
                    'admitted record, written as canonical JSON: sorted keys, no whitespace.</p>'
                    '</article><article><h3>The spec is hashed too</h3><p>Key order, whitespace '
                    'and compact or YAML spelling don\'t change the hash. Changing any field does.'
                    '</p></article><article><h3>The decision id comes from both</h3><p><code>dec_'
                    '</code> plus a hash of the spec hash and the snapshot id.</p></article>'
                    '<article><h3>Signing state at build</h3><p>This page reads the signature block '
                    'from the decision snapshot that the site publishes.</p></article></div>' + _signing(signing)
                    + _sources((("docs/decision-snapshot.md", "the file format, hash and id", "file-format"),
                                ("docs/decision-contract.md", "the canonical spec hash", "the-canonical-spec-hash"),
                                ("docs/snapshot-signing.md", "how snapshots are signed", ""),
                                ("decision/snapshot_keys.json", "the public snapshot signing keys", ""))))
    neutrality = (f'<blockquote>“{html.escape(str(commitment["pledge"]))}”<footer>The neutrality '
                  f'commitment, {html.escape(str(commitment["version"]))}</footer></blockquote>'
                  f'<ul class="assertions">{assertions}</ul>' + _sources((
                      ("docs/legal/neutrality.md", "the commitment, in full", ""),
                      ("api/ranking/engine.py", "neutrality_commitment()", ""))))
    flow = ((1, "Sources", "Model cards and benchmark pages. Each value has its URL, its date and who measured it.", "#evidence"),
            (2, "Two keys", "A second, independent check must agree before a value is used.", "#evidence"),
            (3, "Snapshot", "Everything admitted, frozen into one file and hashed.", "#reproducible"),
            (4, "Estimate", "Ability per domain, learned from every benchmark, with an 80% range.", "#estimate"),
            (5, "Your spec", "Must gates remove. Prefer weights order. Unknowns stay listed.", "#must-prefer"),
            (6, "Answer", "Ranked where the evidence separates models, and flagged where it can't.", "#ties"))
    sections = (
        _section("evidence", "1 · Where evidence comes from", "Every number starts as a sourced, checked record.", "A value with no source never reaches a decision. Neither does one that only its collector has checked.", evidence, theme="dark")
        + _section("estimate", "2 · The capability estimate", "Ability is estimated per domain, from every benchmark we hold.", "There is no fixed benchmark list and no hand-set weight. Every admitted benchmark with at least two model observations counts, and nobody picks favourites. One leaderboard is one reading, and readings disagree. The estimate uses all of them, and says how sure it is.", estimate, theme="light")
        + _section("ties", "3 · Ties", "Why the #1 is often a tie.", "Every estimate is a range. When another model is at least 25% likely to score as well as the top one, the evidence can't say which is better, so the page doesn't pretend to. A model whose range is too wide to tell is never counted in the tie.", '<pre>range         = estimate ± 1.2816 × sd\ntied          = P(B ≥ leader) ≥ 0.25, where\nP(B ≥ leader) = Φ((B − leader) / √(sd_B² + sd_leader²))\nthin          = range wider than 2.8: never tied\nnot_separable = max(A.low, B.low) ≤ min(A.high, B.high)\n                for any other model B</pre>' + ties, theme="dark")
        + _section("must-prefer", "4 · Must and Prefer", "Must is a gate. Prefer is a weight.", "Every facet on the board has three settings, and each does a different job. Conditions filter. They never add points.", must_prefer, theme="light")
        + _section("unknown", "5 · Unknown means unknown", "A missing fact is never a zero.", "Every condition has three answers: pass, fail and unknown. Unknown is its own answer, with its own rules. A null beats a guess.", unknown, theme="dark")
        + _section("reproducible", "6 · Reproducibility", "Same spec, same snapshot, same answer.", "A decision depends on two things you can name: the question and the evidence. Pin both, and anyone holding the same snapshot file gets the answer you got.", reproducible, theme="light")
        + _section("neutrality", "7 · Neutrality", "Nobody pays to rank higher.", "We charge the people and agents who ask for an answer. Never the models, labs or hosts the answer is about.", neutrality, theme="yellow"))
    donts = (("No text box on the board", "You set each criterion yourself. No parser and no AI reads your words and guesses what you meant."),
             ("No paid placement or referral fees", "No provider, host or gateway can buy inclusion, position or a mention."),
             ("No proxying your tokens", "We recommend and hand off. Your inference goes to the provider directly. Choosing per request, in your request path, is a router's job; ModelSpec decides what's worth routing to, outside that path."),
             ("No prompts kept", "A request carries a profile, not prompt text, so there is nothing to keep."),
             ("No guessed values", "A missing value stays missing. It is never filled in, and never counted as zero."),
             ("No fixed benchmark list", "Nobody chooses which benchmarks matter. Every admitted benchmark counts, weighted by the same rules."))
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>How ModelSpec decides</title><meta name="description" content="How ModelSpec turns sourced evidence into model decisions, ties and reproducible answers."><link rel="canonical" href="https://modelspec.dev/method/">{brand.head_links()}{brand.social_meta("How ModelSpec decides")}<link rel="stylesheet" href="/landing-assets/landing.css"><link rel="stylesheet" href="/landing-assets/method.css">{landing_chrome.lockup_style()}</head><body><div class="axis" aria-hidden="true"></div>{landing_chrome.method_header()}<main><section class="method-hero"><div><h1>How ModelSpec decides.</h1><p>The front page says ModelSpec justifies the model decision and shows its work. This is the work: the front page's main claims, taken apart in plain language and linked to the code, the document or the public data that makes it true. Check it rather than trust it.</p><p>Everything here describes the code on main. Where a figure is needed, the page shows how it is computed, or reads it from the live snapshot.</p></div><nav aria-label="The claims, and where each is answered">{claim_links}</nav></section><section class="flow"><h2>From a published score to your answer</h2><ol>{''.join(f'<li><a href="{href}"><code>{n}</code><b>{title}</b><span>{text}</span></a></li>' for n, title, text, href in flow)}</ol></section>{sections}<section id="dont" class="dont"><code>8 · What we don't do</code><h2>What we don't do, on purpose.</h2><div>{''.join(f'<article><h3>{title}</h3><p>{text}</p></article>' for title, text in donts)}</div></section><section class="public-data"><div><h2>Check it yourself.</h2><p>The decision snapshot and vocabulary read by decision answers are public, versioned and free to fetch. So is the code that reads them. The <code>/v1/policy-check</code> determinations are private.</p><a class="button" href="/decide/">Open the board</a></div><ul><li><a href="https://modelspec.dev/api/decision/snapshot.json.gz"><code>modelspec.dev/api/decision/snapshot.json.gz</code></a><span>The snapshot that decision answers read.</span></li><li><a href="https://modelspec.dev/api/decision/vocabulary.json"><code>modelspec.dev/api/decision/vocabulary.json</code></a><span>Every facet, benchmark and domain decision answers know.</span></li><li><a href="https://modelspec.dev/api/rank/profiles.json"><code>modelspec.dev/api/rank/profiles.json</code></a><span>The ranking floors and the neutrality commitment, as data.</span></li><li><a href="https://modelspec.dev/.well-known/modelspec-snapshot-keys.json"><code>modelspec.dev/.well-known/modelspec-snapshot-keys.json</code></a><span>The public keys used to verify signed snapshots.</span></li></ul></section></main>{landing_chrome.footer(detail="This page describes the code on main.")}</body></html>'''


def write(tree: Path, root: Path, data: LandingData) -> dict[str, Any]:
    out = Path(tree) / PAGE_PATH
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page(data, load_signing_state(Path(tree), Path(root))), encoding="utf-8")
    asset = Path(tree) / ASSET_PATH
    asset.parent.mkdir(parents=True, exist_ok=True)
    source = Path(__file__).parent / "landing_assets/method.css"
    asset.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    return {"path": "/method/", "sitemap_paths": ["/method/"]}
