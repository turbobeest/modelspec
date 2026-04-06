"""ModelSpec Ranking Engine — 4-stage pipeline for model downselection.

Stages:
  1. Filter — eliminate models that don't meet hard constraints
  2. Score  — compute weighted composite scores per use-case profile
  3. Rank   — sort by score, break ties
  4. Explain — generate human-readable reasons
"""

from .engine import RankingEngine, USE_CASE_PROFILES

__all__ = ["RankingEngine", "USE_CASE_PROFILES"]
