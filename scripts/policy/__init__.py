"""Policy determinations: the licence readings, and the rule that applies them.

MODEL-78. What lives here is the *method* — which licence says what, and how a
card is matched to a licence. What the method produces is enrichment and is not
in this repository; `schema/enrichment.py` says where the records live and why.

That split is the one `api/ranking/engine.py` already makes: the method is
public so it can be checked, the determinations are the product. A reader can
audit every claim in `licences.py` against the cited URL — and
`verify_quotes.py` does exactly that, on demand — without this project handing
over the corpus-wide answer.
"""
