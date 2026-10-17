"""What ModelSpec is, said once (MODEL-252).

Every public surface that describes ModelSpec reads these strings: the landing
page's title, meta and og descriptions and lead, the first paragraph of
/method/, the /about/ facts page, the opening of llms.txt and its Markdown
twins, the MCP card and the Organization JSON-LD. A surface that writes its own
description is drift, and answer engines read two descriptions as two entities.
Jamie froze the sentence on 2026-10-01; changing it is a positioning decision,
not a copy edit.

The neutrality commitment is not restated here. It lives in
``api.ranking.engine.neutrality_commitment()`` and ``docs/legal/``, held
together by ``tests/test_legal.py``; claims link to it.
"""

from __future__ import annotations

from dataclasses import dataclass

NAME = "ModelSpec"
SITE = "https://modelspec.dev"
REPOSITORY = "https://github.com/turbobeest/modelspec"
MCP_ENDPOINT = "https://api.modelspec.dev/mcp"
API_DECIDE = "https://api.modelspec.dev/v1/decide"
BOARD = f"{SITE}/decide/"

ONE_SENTENCE = (
    "ModelSpec is an analysis of alternatives for AI models: it decides which "
    "models fit a job from your requirements, sourced benchmarks and real cost, "
    "and shows its work."
)

#: For surfaces with a length limit: the `<title>` (search engines cut near 60
#: characters) and the MCP card (`description` is at most 100 by schema).
TITLE = "ModelSpec — an analysis of alternatives for AI models"
SHORT = "An analysis of alternatives for AI models: which models fit a job, and why."

#: First paragraph of any page an answer engine could confuse with these.
DISAMBIGUATION = (
    "ModelSpec at modelspec.dev is not OpenAI's Model Spec, the CNCF ModelPack "
    "model-spec, or the Python package named modelspec."
)

#: Names an engine may use for us. The first is canonical.
ALIASES = (NAME, "modelspec.dev", "Model Spec")

#: The Organization's JSON-LD `sameAs`, before any social profile. The site is
#: the node's own `url`, and the MCP server is its own node, so neither is here.
SAME_AS = (REPOSITORY,)


@dataclass(frozen=True)
class Claim:
    id: str
    statement: str
    proof: str


#: Machine calls require this phrase. Pages render the registry sentences.
MACHINE_KEY = "with a key"


#: What ModelSpec may say about itself. Each is true over HTTP today; each
#: proof is where a reader checks it. Nothing here mentions payment rails that
#: are switched off (x402 is off until Jamie turns it on).
CLAIMS = (
    Claim("evidence-not-payment",
          "The decision comes from your requirements, every admitted benchmark and real cost. "
          "Nobody pays to rank higher.",
          f"{SITE}/legal/neutrality/"),
    Claim("ties-declared",
          "When the evidence can't separate models, ModelSpec says so: it returns the tie "
          'as kind: "tied" with tie_breakers. It does not return the cheapest model as the answer.',
          f"{SITE}/method/#ties"),
    Claim("reproducible",
          "The same spec on the same snapshot returns the same answer, with a decision ID and "
          "a signed snapshot.",
          f"{SITE}/method/#reproducible"),
    Claim("per-job-not-per-request",
          "ModelSpec decides per job or role. It does not route or proxy requests: a router "
          "can choose among the models it recommends.",
          f"{SITE}/method/"),
    Claim("access",
          "People decide free on the board. Machines use the hosted API and the MCP server "
          f"{MACHINE_KEY}.",
          f"{SITE}/pricing/"),
)


@dataclass(frozen=True)
class Call:
    id: str
    statement: str
    href: str


#: How a person or a machine calls ModelSpec. The hrefs are the live endpoints.
CALLS = (
    Call("board", "People decide on the board.", BOARD),
    Call("api", f"Machines call the hosted API {MACHINE_KEY}.", API_DECIDE),
    Call("mcp", f"Machines call the MCP server {MACHINE_KEY}.", MCP_ENDPOINT),
)

#: Visible headings on /about/. The page prints these and nothing else of its own.
ABOUT_HEADING = "About ModelSpec"
CLAIMS_HEADING = "Claims"
CALL_HEADING = "How to call it"
COST_HEADING = "What it costs"
NEUTRALITY_LINK = "The neutrality commitment"
NEUTRALITY_PATH = "/legal/neutrality/"

#: Credit weights and published prices. `{n}` and `{unit}` come from tiers.json.
COST_ANSWERS = (
    ("decide.summary", "A decision costs {n} {unit}."),
    ("decide.full", "A fully explained decision costs {n} {unit}."),
    ("rank", "A ranking costs {n} {unit}."),
    ("policy-check", "A licence and data-residency check costs {n} {unit}."),
)
PRICE_LINE = "{name} costs ${usd}{when} for {credits} credits."


def cost_statements(tiers: dict) -> tuple[str, ...]:
    """Answer weights and the prices on sale. Legacy rows are not sold."""
    weights = tiers["credits"]["weights"]
    lines = []
    for key, template in COST_ANSWERS:
        count = int(weights[key])
        lines.append(template.format(n=count, unit="credit" if count == 1 else "credits"))
    for row in tiers["billing"]["prices"].values():
        if row.get("legacy") or not row.get("credits"):
            continue
        when = " a month" if row.get("interval") == "month" else ""
        lines.append(PRICE_LINE.format(
            name=row["name"], usd=row["usd"], credits=f"{int(row['credits']):,}", when=when))
    return tuple(lines)


def linked(text: str, links: dict[str, str]) -> str:
    """``text`` as HTML with each phrase in ``links`` wrapped in an anchor.

    The visible text stays the registry string byte for byte, so a page can link
    the sentence's parts without rewording it. Every phrase must occur exactly
    once, or the sentence changed underneath the page and the build stops.
    """
    import html

    out = html.escape(text, quote=False)
    for phrase, href in links.items():
        escaped = html.escape(phrase, quote=False)
        if out.count(escaped) != 1:
            raise ValueError(f"{phrase!r} must occur exactly once in {text!r}")
        out = out.replace(escaped, f'<a href="{href}">{escaped}</a>')
    return out


#: The one-liners live on 2026-10-01, before this registry. None may return.
SUPERSEDED = (
    "justifies the model decision and shows its work",
    "Decide which AI model your job needs",
    "a decision engine for AI models",
    "decides which AI model a job needs",
    "Decide which model fits a task",
)
