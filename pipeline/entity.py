"""What ModelSpec is, said once (MODEL-252).

Every public surface that describes ModelSpec reads these strings: the landing
page's title, meta and og descriptions and lead, the first paragraph of
/method/, the opening of llms.txt and its Markdown twins, the MCP card and the
Organization JSON-LD. A surface that writes its own description is drift, and
answer engines read two descriptions as two entities. Jamie froze the sentence
on 2026-10-01; changing it is a positioning decision, not a copy edit.

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


#: What ModelSpec may say about itself. Each is true over HTTP today; each
#: proof is where a reader checks it. Nothing here mentions payment rails that
#: are switched off (x402 is off until Jamie turns it on).
CLAIMS = (
    Claim("evidence-not-payment",
          "The decision comes from your requirements, every admitted benchmark and real cost. "
          "Nobody pays to rank higher.",
          f"{SITE}/legal/neutrality/"),
    Claim("ties-declared",
          "When the evidence can't separate models, ModelSpec says so: it returns the tie and "
          "names the cheapest, open-weights and best-measured member.",
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
          "People decide free on the board. Machines use the hosted API and the MCP server.",
          f"{SITE}/pricing/"),
)


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
