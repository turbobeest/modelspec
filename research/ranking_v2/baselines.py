"""Baselines for the held-out test: benchmark mean, model mean, low-rank ALS.

The low-rank model is the "observational scaling laws" / PCA family: transform
each item to an unbounded scale (logit for percentages, log for minutes, raw
for Elo), standardise per item, and factorise the sparse matrix Z ~ U V' with
ridge penalties by alternating least squares. It learns its loadings freely,
with no domain structure, which is exactly what makes it the right contrast for
the tagged bifactor model.
"""

from __future__ import annotations

import math
import random

from research.ranking_v2.evidence import Obs
from research.ranking_v2.model import chol_solve, cholesky, logit, sigmoid


def _fwd(o: Obs) -> float:
    if o.link == "pct":
        return logit(o.value / 100.0)
    if o.link == "log":
        return math.log(o.value)
    return o.value


def _inv(link: str, z: float) -> float:
    if link == "pct":
        return 100.0 * sigmoid(z)
    if link == "log":
        return math.exp(z)
    return z


class Standardiser:
    def __init__(self, train: list[Obs]):
        vals: dict[str, list[float]] = {}
        raw: dict[str, list[float]] = {}
        self.link: dict[str, str] = {}
        for o in train:
            vals.setdefault(o.item, []).append(_fwd(o))
            raw.setdefault(o.item, []).append(o.value)
            self.link[o.item] = o.link
        self.mu, self.sd, self.raw_mean, self.raw_sd = {}, {}, {}, {}
        for k, v in vals.items():
            m = sum(v) / len(v)
            s = math.sqrt(sum((x - m) ** 2 for x in v) / max(1, len(v) - 1)) or 1.0
            self.mu[k], self.sd[k] = m, s
            rv = raw[k]
            rm = sum(rv) / len(rv)
            self.raw_mean[k] = rm
            self.raw_sd[k] = math.sqrt(sum((x - rm) ** 2 for x in rv) / max(1, len(rv) - 1)) or 1.0

    def z(self, o: Obs) -> float:
        return (_fwd(o) - self.mu[o.item]) / self.sd[o.item]

    def back(self, item: str, z: float) -> float:
        return _inv(self.link[item], self.mu[item] + self.sd[item] * z)


def item_mean(train: list[Obs]):
    st = Standardiser(train)
    return lambda m, i: st.raw_mean.get(i)


def model_mean(train: list[Obs]):
    """The model's average standardised score on other items, mapped back."""
    st = Standardiser(train)
    zs: dict[str, list[float]] = {}
    for o in train:
        zs.setdefault(o.model_id, []).append(st.z(o))
    zbar = {m: sum(v) / (len(v) + 1.0) for m, v in zs.items()}  # shrunk toward 0

    def pred(m: str, i: str):
        if i not in st.mu:
            return None
        return st.back(i, zbar.get(m, 0.0))
    return pred


def lowrank(train: list[Obs], k: int, ridge: float = 1.0, iters: int = 40, seed: int = 0):
    st = Standardiser(train)
    rng = random.Random(seed)
    cells: dict[tuple[str, str], float] = {}
    for o in train:
        cells[(o.model_id, o.item)] = st.z(o)
    models = sorted({m for m, _ in cells})
    items = sorted({i for _, i in cells})
    U = {m: [rng.gauss(0, 0.1) for _ in range(k)] for m in models}
    V = {i: [rng.gauss(0, 0.1) + (1.0 if j == 0 else 0.0) for j in range(k)] for i in items}
    by_m: dict[str, list[tuple[str, float]]] = {}
    by_i: dict[str, list[tuple[str, float]]] = {}
    for (m, i), z in cells.items():
        by_m.setdefault(m, []).append((i, z))
        by_i.setdefault(i, []).append((m, z))

    def solve(pairs, other):
        A = [[ridge if r == c else 0.0 for c in range(k)] for r in range(k)]
        b = [0.0] * k
        for key, z in pairs:
            x = other[key]
            for r in range(k):
                b[r] += x[r] * z
                for c in range(k):
                    A[r][c] += x[r] * x[c]
        return chol_solve(cholesky(A), b)

    for _ in range(iters):
        for m in models:
            U[m] = solve(by_m[m], V)
        for i in items:
            V[i] = solve(by_i[i], U)

    def pred(m: str, i: str):
        if i not in V:
            return None
        u = U.get(m, [0.0] * k)
        return st.back(i, sum(a * b for a, b in zip(u, V[i])))
    return pred
