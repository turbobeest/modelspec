"""The decision spec corpus (MODEL-203).

One list of specs, each with a one-line intent and what it must answer, run
through every surface that answers a decision spec: ``modelspec decide``, the
Worker's ``decide_service.decide``, the page's zod ``decisionSchema`` and the
built page in Chromium. ``cases.yaml`` holds the hand-written cases;
``corpus.py`` adds the ones the registry defines (every template, every facet
as Must and as Prefer, every domain) so a new template or facet is covered the
day it lands. See ``python -m tests.corpus --help``.
"""
