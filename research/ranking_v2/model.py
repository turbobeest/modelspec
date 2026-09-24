"""A hierarchical, benchmark-agnostic capability model. Pure Python.

Every model m has a general ability g_m and one deviation s_{m,d} per domain d.
A benchmark (an *item*) is tagged with one or two domains T_b and measures

    theta_{m,b} = g_m + mean_{d in T_b} s_{m,d}

through its own link:

* bounded percentages (3PL IRT on the aggregate score)
      E[y] = c_b + (1 - c_b) * sigmoid(lambda_b * theta_{m,b} + beta_b + delta_k)
      Var[y] = tau_b^2 + y(1-y)/N_b                     (probability scale)
* ratings and log-durations (Arena Elo, METR minutes), standardised per item
      E[y] = lambda_b * theta_{m,b} + beta_b + delta_k
      Var[y] = se^2 + tau_b^2

`c_b` is the page's random baseline, `N_b` its dataset size, `delta_k` a learned
offset per source kind (provider self-report, unsourced flat block), `tau_b` a
learned residual noise per item. Priors: g ~ N(0, 1), s_d ~ N(0, sigma_d^2) with
sigma_d learned (empirical Bayes), lambda_b ~ N(family mean, .), beta_b weak.

A benchmark's weight is not configured anywhere. It falls out of lambda_b
(discrimination), tau_b (how well it agrees with everything else), N_b, the
slope of the link at the model's ability (saturation) and the evidence's age.
Missing data needs no imputation: the likelihood simply has no term for it, and
a domain with no evidence falls back to its prior with its prior's width.

Fitting is MAP by alternating damped Gauss-Newton with backtracking (models,
items, source offsets), in two stages: first with empirical-Bayes updates of
tau_b, kappa_k and sigma_d, then with every variance frozen so the objective is
fixed and the iteration converges. Each sweep also solves exactly for the two
directions the likelihood cannot see (the location and scale of the abilities),
which is what makes the convergence fast. Uncertainty is the Laplace
approximation per model, conditional on item parameters, whose own uncertainty
is propagated into each row's variance.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Iterable

from research.ranking_v2.domains import DOMAINS
from research.ranking_v2.evidence import Obs, days_between

# ── configuration (every number here is a proposal, see the design doc) ─────

#: Items enter the fit only with this many anchored models (models that also
#: have >= 2 observations on other items). Below it the item waits for overlap.
MIN_OVERLAP = 3
#: With fewer anchored models than this, lambda is held near its family mean.
FREE_DISCRIMINATION = 8
#: Precision half-life of static evidence, and of live readings that are not
#: from the newest snapshot, in days. Floors keep old evidence from vanishing.
HALF_LIFE_STATIC, FLOOR_STATIC = 365.0, 0.25
HALF_LIFE_LIVE, FLOOR_LIVE = 90.0, 0.10
#: Design effect for subtask families measured in one run (MMLU subjects, the
#: Arena text categories): n correlated items count as n / (1 + rho (n - 1)).
FAMILY_RHO = 0.7
#: Subtask families that get a testlet factor instead: one extra dimension per
#: (model, family), shared by that family's items only. MMLU's 57 subjects are
#: one run; their shared deviation is a property of that run, not of the
#: model's knowledge, and a testlet keeps it out of g and the domains.
TESTLET_FAMILIES = frozenset({"mmlu", "multipl_e", "mteb", "flores"})
#: Extra probability-scale noise by source kind (on top of tau_b).
SOURCE_NOISE = {"independent_evaluator": 0.0, "benchmark_author": 0.0,
                "provider_self_report": 0.015, "flat_unsourced": 0.03}
OFFSET_KINDS = ("provider_self_report", "flat_unsourced")
#: Sweeps during which hyperparameters (tau, kappa, sigma) and the scale are
#: re-estimated; after them the objective is fixed and the fit runs to tolerance.
EB_SWEEPS = 30
#: Prior on an item's residual noise tau (probability scale) and its weight in
#: models: the item's own residuals outweigh it only past ~10 models.
TAU_PRIOR_PCT, TAU_PRIOR_N = 0.04, 10.0


def sigmoid(x: float) -> float:
    if x >= 0:
        return 1.0 / (1.0 + math.exp(-x))
    e = math.exp(x)
    return e / (1.0 + e)


def logit(p: float) -> float:
    p = min(max(p, 1e-4), 1 - 1e-4)
    return math.log(p / (1 - p))


# ── small dense linear algebra ───────────────────────────────────────────────


def cholesky(a: list[list[float]]) -> list[list[float]]:
    n = len(a)
    L = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1):
            s = a[i][j] - sum(L[i][k] * L[j][k] for k in range(j))
            if i == j:
                L[i][i] = math.sqrt(max(s, 1e-12))
            else:
                L[i][j] = s / L[j][j]
    return L


def chol_solve(L: list[list[float]], b: list[float]) -> list[float]:
    n = len(b)
    y = [0.0] * n
    for i in range(n):
        y[i] = (b[i] - sum(L[i][k] * y[k] for k in range(i))) / L[i][i]
    x = [0.0] * n
    for i in reversed(range(n)):
        x[i] = (y[i] - sum(L[k][i] * x[k] for k in range(i + 1, n))) / L[i][i]
    return x


def chol_inverse(L: list[list[float]]) -> list[list[float]]:
    n = len(L)
    cols = [chol_solve(L, [1.0 if r == c else 0.0 for r in range(n)]) for c in range(n)]
    return [[cols[c][r] for c in range(n)] for r in range(n)]


# ── the fitted objects ───────────────────────────────────────────────────────


@dataclass
class Item:
    id: str
    link: str
    tags: tuple[str, ...]
    c: float = 0.0            # lower asymptote (random baseline), pct only
    N: float = 300.0          # binomial size, pct only
    center: float = 0.0       # standardisation, lin/log only
    scale: float = 1.0
    lam: float = 1.0
    beta: float = 0.0
    tau2: float = 0.0
    #: Posterior (co)variance of (lambda, beta), propagated into every row's
    #: variance so a thinly observed item cannot pin a model tightly.
    vll: float = 0.0
    vbb: float = 0.0
    vlb: float = 0.0
    family: str = ""
    lam_prior: float = 1.0
    lam_prior_sd: float = 0.5
    n_models: int = 0
    n_anchor: int = 0
    status: str = "free"      # free | borrowed | awaiting_overlap | single_model
    testlet: str = ""         # subtask family with its own per-model factor


@dataclass
class Row:
    """One observation, prepared for the likelihood."""
    obs: Obs
    item: Item
    y: float                  # pct: proportion; lin/log: standardised
    meas_var: float           # known part of the variance (se, binomial, source)
    weight: float             # recency * design effect
    a: dict[str, float]       # loading pattern over g and domains
    #: Shared, learned extra variance by (source kind, link): how far a
    #: provider's own number or an unsourced flat value scatters around what
    #: independent evidence predicts, beyond the item's own noise.
    kind_var: dict = field(default_factory=dict)
    #: Set when stage 2 of the fit freezes every variance, so the objective the
    #: blocks descend is fixed and the iteration converges.
    fixed_var: float | None = None

    @property
    def kind_key(self) -> tuple[str, str]:
        return (self.obs.source_kind, "pct" if self.item.link == "pct" else "lin")


@dataclass
class ModelFit:
    model_id: str
    dims: list[str]                        # "g" plus the domains it has evidence in
    v: list[float]
    cov: list[list[float]] = field(default_factory=list)
    rows: list[Row] = field(default_factory=list)

    def value(self, dim: str) -> float:
        return self.v[self.dims.index(dim)] if dim in self.dims else 0.0


@dataclass
class Fit:
    as_of: str
    items: dict[str, Item]
    models: dict[str, ModelFit]
    sigma: dict[str, float]
    offsets: dict[str, float]
    offset_se: dict[str, float]
    history: list[float] = field(default_factory=list)
    kind_var: dict = field(default_factory=dict)

    # ── use-case scores ──
    def score(self, model_id: str, mix: dict[str, float]) -> tuple[float, float]:
        """Posterior mean and sd of U = g + sum_d pi_d s_d."""
        mf = self.models.get(model_id)
        w = {d: p for d, p in mix.items() if p}
        if mf is None:
            var = 1.0 + sum((p * self.sigma.get(d, 0.5)) ** 2 for d, p in w.items())
            return 0.0, math.sqrt(var)
        vec = [1.0 if dim == "g" else w.get(dim, 0.0) for dim in mf.dims]
        mean = sum(a * b for a, b in zip(vec, mf.v))
        var = sum(vec[i] * mf.cov[i][j] * vec[j]
                  for i in range(len(vec)) for j in range(len(vec)))
        # Domains with no evidence contribute their prior variance, not zero.
        var += sum((p * self.sigma.get(d, 0.5)) ** 2 for d, p in w.items() if d not in mf.dims)
        return mean, math.sqrt(max(var, 0.0))

    def predict_sd(self, model_id: str, item_id: str) -> float | None:
        """Predictive sd of one new observation on the raw scale (pp, Elo, log-min)."""
        it = self.items.get(item_id)
        mf = self.models.get(model_id)
        if it is None or mf is None or it.status not in ("free", "borrowed") or not mf.cov:
            return None
        a = {"g": 1.0}
        for d in it.tags:
            a[d] = a.get(d, 0.0) + 1.0 / len(it.tags)
        if it.testlet:
            a["fam:" + it.testlet] = 1.0
        idx = {d: i for i, d in enumerate(mf.dims)}
        var_theta = sum(ca * cb * mf.cov[idx[da]][idx[db]]
                        for da, ca in a.items() for db, cb in a.items() if da in idx and db in idx)
        var_theta += sum(c * c * self.sigma.get(d, 0.5) ** 2 for d, c in a.items() if d not in idx)
        theta = sum(c * mf.value(d) for d, c in a.items())
        eta = it.lam * theta + it.beta
        mu, slope = _mean_and_slope(it, eta)
        var = (slope * it.lam) ** 2 * var_theta + slope ** 2 * (
            theta * theta * it.vll + it.vbb + 2 * theta * it.vlb) + it.tau2
        if it.link == "pct":
            var += max(mu * (1 - mu), 1e-4) / it.N
            return 100.0 * math.sqrt(var)
        return it.scale * math.sqrt(var)

    def predict(self, model_id: str, item_id: str, source_kind: str = "") -> float | None:
        """Expected raw value of one (model, item) cell, as `source_kind` would
        report it, or None if the item is not in the fit."""
        it = self.items.get(item_id)
        mf = self.models.get(model_id)
        if it is None or it.status not in ("free", "borrowed"):
            return None
        theta = 0.0
        if mf is not None:
            theta = mf.value("g") + sum(mf.value(d) for d in it.tags) / len(it.tags)
            if it.testlet:
                theta += mf.value("fam:" + it.testlet)
        eta = it.lam * theta + it.beta + self.offsets.get(source_kind, 0.0)
        if it.link == "pct":
            return 100.0 * (it.c + (1 - it.c) * sigmoid(eta))
        raw = it.center + it.scale * eta
        return math.exp(raw) if it.link == "log" else raw


# ── preparation ──────────────────────────────────────────────────────────────


def _recency(o: Obs, as_of: str) -> float:
    age = max(0, days_between(o.date, as_of))
    if o.live:
        # The newest snapshot of a live board is current by definition.
        if "(aligned)" not in o.version:
            return 1.0
        return max(FLOOR_LIVE, 0.5 ** (age / HALF_LIFE_LIVE))
    return max(FLOOR_STATIC, 0.5 ** (age / HALF_LIFE_STATIC))


def _loading(tags: tuple[str, ...]) -> dict[str, float]:
    a = {"g": 1.0}
    for d in tags:
        a[d] = a.get(d, 0.0) + 1.0 / len(tags)
    return a


def prepare(obs: list[Obs], pages: dict[str, dict], as_of: str) -> tuple[dict[str, Item], list[Row]]:
    by_item: dict[str, list[Obs]] = {}
    for o in obs:
        by_item.setdefault(o.item, []).append(o)
    per_model: dict[str, int] = {}
    for o in obs:
        per_model[o.model_id] = per_model.get(o.model_id, 0) + 1

    items: dict[str, Item] = {}
    for iid, os_ in by_item.items():
        first = os_[0]
        page = pages.get(iid.replace("flat:", ""), {})
        metric = page.get("metric") or {}
        it = Item(iid, first.link, first.tags)
        lineage = page.get("lineage") or {}
        it.family = str(lineage.get("family") or "") or (
            "arena" if first.live or iid.startswith("flat:arena") else iid)
        if it.link == "pct":
            base = metric.get("random_baseline")
            it.c = min(0.5, float(base) / 100.0) if isinstance(base, (int, float)) and base > 0 else 0.0
            size = (page.get("dataset") or {}).get("size")
            # Pages sometimes give a task count (MTEB: 12) rather than an item
            # count; below 100 the binomial term would drown the signal.
            it.N = float(min(max(size, 100), 3000)) if isinstance(size, (int, float)) and size else 300.0
        else:
            vals = [math.log(o.value) if o.link == "log" else o.value for o in os_]
            it.center = sum(vals) / len(vals)
            sd = math.sqrt(sum((v - it.center) ** 2 for v in vals) / max(1, len(vals) - 1))
            it.scale = sd if sd > 1e-6 else 1.0
        models = {o.model_id for o in os_}
        it.n_models = len(models)
        it.n_anchor = sum(1 for m in models if per_model[m] - sum(
            1 for o in os_ if o.model_id == m) >= 2)
        items[iid] = it

    # Family priors: an item with little overlap borrows its discrimination.
    for it in items.values():
        if it.n_models < 2:
            it.status = "single_model"
        elif it.n_anchor < MIN_OVERLAP:
            it.status = "awaiting_overlap"
        elif it.n_anchor < FREE_DISCRIMINATION:
            it.status = "borrowed"
            it.lam_prior_sd = 0.2
        else:
            it.status = "free"

    rows: list[Row] = []
    kind_var = {(k, link): (SOURCE_NOISE[k] if link == "pct" else 3 * SOURCE_NOISE[k]) ** 2
                for k in SOURCE_NOISE for link in ("pct", "lin")}
    fam_count: dict[tuple[str, str, str], int] = {}
    for o in obs:
        if o.family:
            k = (o.model_id, o.family, o.source_kind)
            fam_count[k] = fam_count.get(k, 0) + 1
    for o in obs:
        it = items[o.item]
        if it.status not in ("free", "borrowed"):
            continue
        n = fam_count.get((o.model_id, o.family, o.source_kind), 1) if o.family else 1
        a = _loading(it.tags)
        if o.family in TESTLET_FAMILIES:
            it.testlet = o.family
            design = 1.0
            if n >= 2:
                a["fam:" + o.family] = 1.0
        else:
            design = 1.0 / (1.0 + FAMILY_RHO * (n - 1))
        w = _recency(o, as_of) * design
        if it.link == "pct":
            y = o.value / 100.0
            meas = 0.0
        else:
            raw = math.log(o.value) if it.link == "log" else o.value
            y = (raw - it.center) / it.scale
            se = (o.se / it.scale) if o.se else 0.0
            if o.link == "log" and o.se is None:
                se = 0.0
            meas = se * se
        rows.append(Row(o, it, y, meas, w, a, kind_var))
    return items, rows


# ── the fit ──────────────────────────────────────────────────────────────────


def _mean_and_slope(it: Item, eta: float) -> tuple[float, float]:
    if it.link == "pct":
        s = sigmoid(eta)
        return it.c + (1 - it.c) * s, (1 - it.c) * s * (1 - s)
    return eta, 1.0


def _row_var(r: Row, mu: float, slope: float | None = None, th: float = 0.0) -> float:
    if r.fixed_var is not None:
        return r.fixed_var
    it = r.item
    var = it.tau2 + r.meas_var + r.kind_var.get(r.kind_key, 0.0)
    if it.link == "pct":
        var += max(mu * (1 - mu), 1e-4) / it.N
    if slope is not None:
        var += slope * slope * (th * th * it.vll + it.vbb + 2 * th * it.vlb)
    return var


class Fitter:
    def __init__(self, obs: list[Obs], pages: dict[str, dict], as_of: str,
                 domains: Iterable[str] = DOMAINS, use_domains: bool = True,
                 offsets: bool = True):
        self.as_of = as_of
        self.items, self.rows = prepare(obs, pages, as_of)
        self.use_domains = use_domains
        self.fit_offsets = offsets
        self.fixed = False
        self.sigma = {d: 0.5 for d in domains}
        self.sigma.update({"fam:" + f: 0.5 for f in TESTLET_FAMILIES})
        self.offsets = {k: 0.0 for k in OFFSET_KINDS}
        self.offset_se = {k: 0.0 for k in OFFSET_KINDS}
        self.by_model: dict[str, list[Row]] = {}
        self.by_item: dict[str, list[Row]] = {}
        for r in self.rows:
            if not use_domains:
                r.a = {"g": 1.0}
            self.by_model.setdefault(r.obs.model_id, []).append(r)
            self.by_item.setdefault(r.item.id, []).append(r)
        self.models: dict[str, ModelFit] = {}
        for mid, rows in self.by_model.items():
            dims = ["g"] + sorted({d for r in rows for d in r.a if d != "g"})
            self.models[mid] = ModelFit(mid, dims, [0.0] * len(dims), rows=rows)
        for it in self.items.values():
            it.tau2 = 0.02 ** 2 if it.link == "pct" else 0.3 ** 2
        self._init()

    # ── helpers ──
    def _theta(self, r: Row, mf: ModelFit) -> float:
        return sum(coef * mf.v[mf.dims.index(d)] for d, coef in r.a.items())

    def _eta(self, r: Row, mf: ModelFit) -> float:
        return r.item.lam * self._theta(r, mf) + r.item.beta + self.offsets.get(r.obs.source_kind, 0.0)

    def _prior_prec(self, dim: str) -> float:
        return 1.0 if dim == "g" else 1.0 / (self.sigma.get(dim, 0.5) ** 2)

    def _init(self) -> None:
        # Item-standardised scores give a starting g; items start centred.
        for it in self.items.values():
            rs = self.by_item.get(it.id, [])
            if not rs:
                continue
            if it.link == "pct":
                zs = [logit((r.y - it.c) / (1 - it.c)) for r in rs]
            else:
                zs = [r.y for r in rs]
            mu = sum(zs) / len(zs)
            sd = math.sqrt(sum((z - mu) ** 2 for z in zs) / max(1, len(zs) - 1)) or 1.0
            it.beta = mu
            it.lam = max(0.3, min(2.5, sd)) if it.link == "pct" else 0.8
            for r, z in zip(rs, zs):
                r._z0 = (z - mu) / sd  # type: ignore[attr-defined]
        for mid, mf in self.models.items():
            zs = [getattr(r, "_z0", 0.0) for r in mf.rows]
            mf.v[0] = sum(zs) / (len(zs) + 1.0)

    def objective(self) -> float:
        total = 0.0
        for mf in self.models.values():
            for r in mf.rows:
                mu, _ = _mean_and_slope(r.item, self._eta(r, mf))
                var = _row_var(r, mu)
                total += 0.5 * r.weight * ((r.y - mu) ** 2 / var + math.log(var))
            total += 0.5 * sum(self._prior_prec(d) * x * x for d, x in zip(mf.dims, mf.v))
        for it in self.items.values():
            total += 0.5 * ((it.lam - it.lam_prior) / it.lam_prior_sd) ** 2
        return total

    # ── block updates ──
    def _model_step(self, mf: ModelFit, final: bool = False) -> None:
        k = len(mf.dims)
        idx = {d: i for i, d in enumerate(mf.dims)}

        def local_obj(v: list[float]) -> float:
            tot = 0.5 * sum(self._prior_prec(d) * x * x for d, x in zip(mf.dims, v))
            for r in mf.rows:
                th = sum(coef * v[idx[d]] for d, coef in r.a.items())
                eta = r.item.lam * th + r.item.beta + self.offsets.get(r.obs.source_kind, 0.0)
                mu, slope = _mean_and_slope(r.item, eta)
                tot += 0.5 * r.weight * (r.y - mu) ** 2 / _row_var(r, mu, slope, th)
            return tot

        for _ in range(2):
            H = [[0.0] * k for _ in range(k)]
            grad = [0.0] * k
            for r in mf.rows:
                th = self._theta(r, mf)
                eta = r.item.lam * th + r.item.beta + self.offsets.get(r.obs.source_kind, 0.0)
                mu, slope = _mean_and_slope(r.item, eta)
                w = r.weight / _row_var(r, mu, slope, th)
                jd = slope * r.item.lam
                J = [0.0] * k
                for d, coef in r.a.items():
                    J[idx[d]] = jd * coef
                res = r.y - mu
                for i in range(k):
                    if J[i] == 0.0:
                        continue
                    grad[i] += w * J[i] * res
                    for j in range(i + 1):
                        H[i][j] += w * J[i] * J[j]
            for i, d in enumerate(mf.dims):
                H[i][i] += self._prior_prec(d)
                grad[i] -= self._prior_prec(d) * mf.v[i]
            for i in range(k):
                for j in range(i):
                    H[j][i] = H[i][j]
            L = cholesky(H)
            step = chol_solve(L, grad)
            before = local_obj(mf.v)
            t = 1.0
            for _ in range(6):
                trial = [x + t * s for x, s in zip(mf.v, step)]
                if local_obj(trial) <= before + 1e-12:
                    mf.v = trial
                    break
                t *= 0.5
            if final:
                mf.cov = chol_inverse(cholesky(H))

    def _item_step(self, it: Item) -> None:
        rs = self.by_item.get(it.id, [])
        if not rs:
            return
        for _ in range(2):
            H = [[0.0, 0.0], [0.0, 0.0]]
            g = [0.0, 0.0]
            for r in rs:
                mf = self.models[r.obs.model_id]
                th = self._theta(r, mf)
                eta = it.lam * th + it.beta + self.offsets.get(r.obs.source_kind, 0.0)
                mu, slope = _mean_and_slope(it, eta)
                w = r.weight / _row_var(r, mu)
                J = (slope * th, slope)
                res = r.y - mu
                for i in range(2):
                    g[i] += w * J[i] * res
                    for j in range(2):
                        H[i][j] += w * J[i] * J[j]
            plam = 1.0 / it.lam_prior_sd ** 2
            pbeta = 1.0 / 9.0
            H[0][0] += plam
            H[1][1] += pbeta
            g[0] -= plam * (it.lam - it.lam_prior)
            g[1] -= pbeta * it.beta
            det = H[0][0] * H[1][1] - H[0][1] * H[1][0]
            if det <= 1e-12:
                return
            d_lam = (H[1][1] * g[0] - H[0][1] * g[1]) / det
            d_beta = (H[0][0] * g[1] - H[1][0] * g[0]) / det
            before = self._item_obj(it, rs)
            lam0, beta0, t = it.lam, it.beta, 1.0
            for _ in range(6):
                it.lam = min(6.0, max(0.05, lam0 + t * d_lam))
                it.beta = beta0 + t * d_beta
                if self._item_obj(it, rs) <= before + 1e-12:
                    break
                t *= 0.5
            else:
                it.lam, it.beta = lam0, beta0
            if self.fixed:
                continue
            it.vll, it.vbb, it.vlb = H[1][1] / det, H[0][0] / det, -H[0][1] / det

    def _item_obj(self, it: Item, rs: list[Row]) -> float:
        tot = 0.5 * ((it.lam - it.lam_prior) / it.lam_prior_sd) ** 2 + 0.5 * it.beta ** 2 / 9.0
        for r in rs:
            mf = self.models[r.obs.model_id]
            mu, _ = _mean_and_slope(it, self._eta(r, mf))
            tot += 0.5 * r.weight * (r.y - mu) ** 2 / _row_var(r, mu)
        return tot

    def _freeze(self) -> None:
        """Stage 2: fix every row's variance at its current value."""
        for mf in self.models.values():
            for r in mf.rows:
                th = self._theta(r, mf)
                mu, slope = _mean_and_slope(r.item, self._eta(r, mf))
                r.fixed_var = _row_var(r, mu, slope, th)
        self.fixed = True

    def _standardise(self) -> None:
        """Publish on a fixed unit: g has mean 0 and sd 1 over the models with
        three or more observations. A gauge change: no prediction moves."""
        gs = [mf.v[0] for mf in self.models.values() if len(mf.rows) >= 3]
        if len(gs) < 5:
            return
        mean = sum(gs) / len(gs)
        sd = math.sqrt(sum((x - mean) ** 2 for x in gs) / len(gs)) or 1.0
        for it in self.items.values():
            it.beta += it.lam * mean
            it.lam *= sd
            # (lambda, beta) covariance under lambda' = sd lambda, beta' = beta + mean lambda
            vll, vbb, vlb = it.vll, it.vbb, it.vlb
            it.vll = sd * sd * vll
            it.vbb = vbb + 2 * mean * vlb + mean * mean * vll
            it.vlb = sd * (vlb + mean * vll)
        for mf in self.models.values():
            mf.v[0] -= mean
            mf.v = [x / sd for x in mf.v]
            mf.cov = [[c / (sd * sd) for c in row] for row in mf.cov]
        self.sigma = {d: s / sd for d, s in self.sigma.items()}
        self.scale_sd = sd

    def _offset_step(self) -> None:
        for kind in OFFSET_KINDS:
            h, g = 1.0 / 0.25, -self.offsets[kind] / 0.25
            for r in self.rows:
                if r.obs.source_kind != kind:
                    continue
                mf = self.models[r.obs.model_id]
                mu, slope = _mean_and_slope(r.item, self._eta(r, mf))
                w = r.weight / _row_var(r, mu)
                h += w * slope * slope
                g += w * slope * (r.y - mu)
            self.offsets[kind] += g / h
            self.offset_se[kind] = math.sqrt(1.0 / h)

    def _noise_step(self) -> None:
        for it in self.items.values():
            rs = self.by_item.get(it.id, [])
            if not rs:
                continue
            # A model-by-benchmark interaction of a few points is normal
            # between frontier benchmarks; an item seen on seven models cannot
            # show it is smaller, so the prior carries ten models' weight.
            prior, nu = (TAU_PRIOR_PCT ** 2, TAU_PRIOR_N) if it.link == "pct" else (0.3 ** 2, TAU_PRIOR_N)
            num, den = nu * prior, nu
            for r in rs:
                mf = self.models[r.obs.model_id]
                mu, _ = _mean_and_slope(it, self._eta(r, mf))
                known = _row_var(r, mu) - it.tau2
                num += r.weight * max(0.0, (r.y - mu) ** 2 - known)
                den += r.weight
            floor = 0.01 ** 2 if it.link == "pct" else 0.05 ** 2
            it.tau2 = max(floor, num / den)
        # Extra scatter of provider self-reports and flat values, learned the
        # same way from their residuals, shrunk toward the configured prior.
        if not self.rows:
            return
        kv = self.rows[0].kind_var
        acc: dict[tuple[str, str], list[float]] = {}
        for r in self.rows:
            key = r.kind_key
            if key[0] not in OFFSET_KINDS:
                continue
            mf = self.models[r.obs.model_id]
            mu, _ = _mean_and_slope(r.item, self._eta(r, mf))
            known = _row_var(r, mu) - kv.get(key, 0.0)
            a = acc.setdefault(key, [0.0, 0.0])
            a[0] += r.weight * ((r.y - mu) ** 2 - known)
            a[1] += r.weight
        for key, (num, den) in acc.items():
            base = (SOURCE_NOISE[key[0]] if key[1] == "pct" else 3 * SOURCE_NOISE[key[0]]) ** 2
            kv[key] = max(base, (num + 5 * base) / (den + 5))

    def _sigma_step(self) -> None:
        for d in self.sigma:
            num, den = 5 * 0.5 ** 2, 5.0
            for mf in self.models.values():
                if d in mf.dims:
                    i = mf.dims.index(d)
                    post = mf.cov[i][i] if mf.cov else 0.0
                    num += mf.v[i] ** 2 + post
                    den += 1
            self.sigma[d] = min(1.2, max(0.15, math.sqrt(num / den)))

    def _gauge_step(self) -> None:
        """Move along the two directions the likelihood cannot see.

        Shifting every g by a (and each beta by -lambda a), or scaling every
        ability by c (and each lambda by 1/c), leaves every prediction
        unchanged; only the priors notice. Block updates crawl along such flat
        directions, so each is solved exactly here, as its own 1-D problem.
        """
        ms = list(self.models.values())
        its = [it for it in self.items.values() if self.by_item.get(it.id)]
        if not ms or not its:
            return
        # Location: minimise sum (g + a)^2 / 2 + sum (beta - lambda a)^2 / 18.
        num = -sum(mf.v[0] for mf in ms) + sum(it.lam * it.beta for it in its) / 9.0
        den = len(ms) + sum(it.lam ** 2 for it in its) / 9.0
        a = num / den
        for mf in ms:
            mf.v[0] += a
        for it in its:
            it.beta -= it.lam * a
        # Scale: minimise c^2 A / 2 + sum (lambda / c - prior)^2 / (2 sd^2).
        A = 0.0
        for mf in ms:
            for d, x in zip(mf.dims, mf.v):
                A += self._prior_prec(d) * x * x

        def obj(c: float) -> float:
            return 0.5 * c * c * A + sum(0.5 * ((it.lam / c - it.lam_prior) / it.lam_prior_sd) ** 2
                                         for it in its)
        lo, hi = 0.5, 2.0
        for _ in range(40):  # golden section; the objective is unimodal in c
            m1, m2 = lo + 0.382 * (hi - lo), lo + 0.618 * (hi - lo)
            if obj(m1) < obj(m2):
                hi = m2
            else:
                lo = m1
        c = 0.5 * (lo + hi)
        if abs(c - 1.0) < 1e-9:
            return
        for mf in ms:
            mf.v = [x * c for x in mf.v]
        for it in its:
            it.lam = it.lam / c

    def run(self, sweeps: int = 300, tol: float = 1e-3, verbose: bool = False) -> Fit:
        """Two stages. Stage 1 (`EB_SWEEPS`): alternate the blocks and update the
        hyperparameters (tau, kappa, sigma) and the scale. Stage 2: hold the
        hyperparameters fixed and iterate the blocks on the now fixed objective
        until no model's parameters move by more than `tol`."""
        history: list[float] = []
        self.fixed = False
        for sweep in range(sweeps):
            if sweep == EB_SWEEPS:
                self._freeze()
            before = {m: list(mf.v) for m, mf in self.models.items()}
            for mf in self.models.values():
                self._model_step(mf)
            for it in self.items.values():
                self._item_step(it)
            if self.fit_offsets and not self.fixed:
                self._offset_step()
            if sweep < EB_SWEEPS:
                if sweep >= 2:
                    self._noise_step()
                if sweep % 3 == 2:
                    for mf in self.models.values():
                        self._model_step(mf, final=True)
                    if self.use_domains:
                        self._sigma_step()
            self._gauge_step()
            history.append(self.objective())
            moved = max((abs(x - y) for m, mf in self.models.items()
                         for x, y in zip(mf.v, before[m])), default=0.0)
            if verbose:
                print(f"sweep {sweep}: objective {history[-1]:.2f}, max move {moved:.2e}", flush=True)
            if sweep >= EB_SWEEPS and moved < tol:
                break
        self.sweeps_run = len(history)
        for mf in self.models.values():
            self._model_step(mf, final=True)
        self._standardise()
        return Fit(self.as_of, self.items, self.models, dict(self.sigma),
                   dict(self.offsets), dict(self.offset_se), history,
                   dict(self.rows[0].kind_var) if self.rows else {})


def fit(obs: list[Obs], pages: dict[str, dict], as_of: str, **kw) -> Fit:
    sweeps = kw.pop("sweeps", 300)
    verbose = kw.pop("verbose", False)
    return Fitter(obs, pages, as_of, **kw).run(sweeps=sweeps, verbose=verbose)


# ── explanation ──────────────────────────────────────────────────────────────


def explain(fit_: Fit, model_id: str, mix: dict[str, float], top: int = 5) -> list[dict]:
    """Which measurements drove U for this model, with sources and dates.

    Linearised at the MAP, the estimate is a precision-weighted combination of
    what each observation implies on its own:

        v = Cov * sum_i a_i * p_i * implied_i,   p_i = w_i (slope_i lambda_i)^2 / var_i

    so U = w' v = sum_i omega_i * implied_i with omega_i = w' Cov a_i p_i. Each
    row reports the raw value and citation, the ability it implies on its own
    domain blend, its weight share and its contribution to U.
    """
    mf = fit_.models.get(model_id)
    if mf is None:
        return []
    idx = {d: i for i, d in enumerate(mf.dims)}
    wvec = [1.0 if d == "g" else mix.get(d, 0.0) for d in mf.dims]
    wcov = [sum(wvec[i] * mf.cov[i][j] for i in range(len(wvec))) for j in range(len(wvec))]
    out = []
    for r in mf.rows:
        it = r.item
        th = sum(coef * mf.v[idx[d]] for d, coef in r.a.items())
        eta = it.lam * th + it.beta + fit_.offsets.get(r.obs.source_kind, 0.0)
        mu, slope = _mean_and_slope(it, eta)
        var = _row_var(r, mu, slope, th)
        d_eta = slope * it.lam
        if d_eta <= 1e-9:
            continue
        implied = th + (r.y - mu) / d_eta
        prec = r.weight * d_eta ** 2 / var
        omega = sum(wcov[idx[d]] * coef for d, coef in r.a.items()) * prec
        out.append({**r.obs.cite(), "tags": list(it.tags), "implied_ability": implied,
                    "implied_sd": 1.0 / math.sqrt(prec) if prec > 0 else float("inf"),
                    "weight": omega, "contribution": omega * implied,
                    "saturation_slope": slope if it.link == "pct" else None,
                    "recency_weight": r.weight})
    total = sum(abs(x["weight"]) for x in out) or 1.0
    for x in out:
        x["weight_share"] = x["weight"] / total
    out.sort(key=lambda x: -abs(x["weight"]))
    return out[:top]


def item_information(fit_: Fit, item_id: str, theta: float) -> float:
    """Fisher information an item carries about ability `theta` (per observation)."""
    it = fit_.items[item_id]
    eta = it.lam * theta + it.beta
    mu, slope = _mean_and_slope(it, eta)
    var = it.tau2 + (max(mu * (1 - mu), 1e-4) / it.N if it.link == "pct" else 0.0)
    return (slope * it.lam) ** 2 / var


def mask_cells(obs: list[Obs], frac: float, seed: int) -> tuple[list[Obs], list[Obs]]:
    """Hold out a random `frac` of (model, item) cells, keeping every model and
    item that would otherwise vanish entirely in the training set."""
    rng = random.Random(seed)
    cells: dict[tuple[str, str], list[Obs]] = {}
    for o in obs:
        cells.setdefault((o.model_id, o.item), []).append(o)
    keys = sorted(cells)
    rng.shuffle(keys)
    per_model: dict[str, int] = {}
    per_item: dict[str, int] = {}
    for m, i in keys:
        per_model[m] = per_model.get(m, 0) + 1
        per_item[i] = per_item.get(i, 0) + 1
    target = int(frac * len(keys))
    test: set[tuple[str, str]] = set()
    for m, i in keys:
        if len(test) >= target:
            break
        if per_model[m] <= 2 or per_item[i] <= 3:
            continue
        test.add((m, i))
        per_model[m] -= 1
        per_item[i] -= 1
    train = [o for k, os_ in cells.items() if k not in test for o in os_]
    held = [o for k, os_ in cells.items() if k in test for o in os_]
    return train, held
