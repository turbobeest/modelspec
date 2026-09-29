"""The daily coverage report (MODEL-215): measure every target, state every breach.

Each check is a pure function over data already read: a premier build audit,
the models.dev payload, and the latest workflow runs. ``measure`` reads them.
A check that could not read its input reports ``error``, and a check that
measured nothing reports ``error`` too: an empty check is never a met target.

Targets and thresholds: ``scripts/slo/targets.yaml``. Prose:
``docs/method/coverage-slo.md``.
"""

from __future__ import annotations

import json
import subprocess
from collections import defaultdict
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any, Literal

import yaml

TARGETS_PATH = Path(__file__).with_name("targets.yaml")
REPO = "turbobeest/modelspec"
PRICE_PREFIX = "offering.price."
SPEED_FACETS = ("offering.speed.throughput", "offering.speed.time_to_first_token")

Status = Literal["met", "breach", "error", "not_in_force"]


# ── configuration ──────────────────────────────────────────────────────────


@dataclass(frozen=True)
class Target:
    id: str
    title: str
    in_force: bool
    params: Mapping[str, Any]


@dataclass(frozen=True)
class WatchedWorkflow:
    file: str
    max_age_hours: float | None
    skipped_ok: bool


@dataclass(frozen=True)
class Config:
    report_url: str
    notify: tuple[str, ...]
    escalate_after_hours: float
    issue_label: str
    targets: tuple[Target, ...]
    domain_map: Mapping[str, tuple[str, ...]]
    workflows: tuple[WatchedWorkflow, ...]

    def target(self, target_id: str) -> Target:
        for t in self.targets:
            if t.id == target_id:
                return t
        raise KeyError(target_id)


def load_config(path: Path = TARGETS_PATH) -> Config:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    targets = []
    for raw in data["targets"]:
        raw = dict(raw)
        targets.append(Target(id=raw.pop("id"), title=raw.pop("title"),
                              in_force=bool(raw.pop("in_force")), params=raw))
    return Config(
        report_url=str(data["report_url"]),
        notify=tuple(data.get("notify") or ()),
        escalate_after_hours=float(data["escalate_after_hours"]),
        issue_label=str(data["issue_label"]),
        targets=tuple(targets),
        domain_map={k: tuple(v) for k, v in data["domain_map"].items()},
        workflows=tuple(
            WatchedWorkflow(file=w["file"], max_age_hours=w.get("max_age_hours"),
                            skipped_ok=bool(w.get("skipped_ok", True)))
            for w in data["workflows"]
        ),
    )


# ── results ────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class Finding:
    subject: str
    detail: str


@dataclass(frozen=True)
class Result:
    target: str
    title: str
    status: Status
    measured: int
    findings: tuple[Finding, ...]
    errors: tuple[str, ...] = ()


@dataclass(frozen=True)
class Check:
    """What one check saw: how many things it measured, and what failed."""

    measured: int = 0
    findings: tuple[Finding, ...] = ()
    errors: tuple[str, ...] = ()


def settle(target: Target, check: Check) -> Result:
    """A target's status. Only a check that measured something and found nothing is met."""
    findings = tuple(sorted(set(check.findings), key=lambda f: (f.subject, f.detail)))
    errors = tuple(check.errors)
    if not target.in_force:
        status: Status = "not_in_force"
    elif errors:
        status = "error"
    elif check.measured == 0:
        status = "error"
        errors = ("nothing was measured, so the target cannot be called met",)
    elif findings:
        status = "breach"
    else:
        status = "met"
    return Result(target.id, target.title, status, check.measured, findings, errors)


@dataclass(frozen=True)
class Report:
    as_of: date
    generated_at: datetime
    commit: str | None
    snapshot_id: str | None
    results: tuple[Result, ...]
    run_url: str | None = None

    @property
    def status(self) -> Literal["met", "breach"]:
        """``met`` only when every in-force target was measured and met."""
        return "met" if all(r.status in ("met", "not_in_force") for r in self.results) \
            else "breach"

    def to_json(self) -> dict[str, Any]:
        return {
            "format": "modelspec.coverage-report",
            "format_version": 1,
            "as_of": self.as_of.isoformat(),
            "generated_at": self.generated_at.isoformat(timespec="seconds"),
            "commit": self.commit,
            "snapshot_id": self.snapshot_id,
            "run_url": self.run_url,
            "status": self.status,
            "counts": {s: sum(r.status == s for r in self.results)
                       for s in ("met", "breach", "error", "not_in_force")},
            "targets": [
                {"id": r.target, "title": r.title, "status": r.status, "measured": r.measured,
                 "errors": list(r.errors),
                 "findings": [{"subject": f.subject, "detail": f.detail} for f in r.findings]}
                for r in self.results
            ],
        }


# ── the lineup, as a premier build sees it ─────────────────────────────────


@dataclass(frozen=True)
class Lineup:
    """The active premier models, their offerings, and the domains they claim."""

    models: tuple[str, ...]
    offerings: Mapping[str, tuple[str, ...]]
    claims: Mapping[str, tuple[str, ...]]

    def subjects(self) -> set[str]:
        return set(self.models) | {o for os in self.offerings.values() for o in os}


def lineup_of(content: Mapping[str, Any], premier: Mapping[str, Any]) -> Lineup:
    models, offerings = [], defaultdict(list)
    for c in content["lineup"]["candidates"]:
        if c["kind"] == "model":
            models.append(c["id"])
        else:
            offerings[c["model"]].append(c["id"])
    claims = {
        str(m["model_id"]): tuple(sorted({str(cl["domain"]) for cl in m.get("clauses") or ()
                                          if cl.get("domain")}))
        for m in premier.get("models") or ()
    }
    return Lineup(tuple(sorted(models)), {m: tuple(sorted(o)) for m, o in offerings.items()},
                  claims)


def _verified_on(record: Mapping[str, Any]) -> date | None:
    verification = record.get("verification") or {}
    try:
        return date.fromisoformat(str(verification.get("date")))
    except ValueError:
        return None


def _age(as_of: date, day: date | None) -> str:
    return "undated" if day is None else f"{(as_of - day).days} days ago ({day.isoformat()})"


# ── checks over the snapshot ───────────────────────────────────────────────


def check_domain_evidence(lineup: Lineup, evidence: Mapping[str, Sequence[Any]],
                          benchmark_domains: Mapping[str, Iterable[Sequence[str]]],
                          domain_map: Mapping[str, Sequence[str]]) -> Check:
    """Each claimed premier domain needs one admitted row on a benchmark tagged for it."""
    tagged: dict[str, set[str]] = defaultdict(set)
    for bid, tags in benchmark_domains.items():
        for domain_id, _directness in tags:
            tagged[str(domain_id)].add(bid)
    findings, errors, measured = [], [], 0
    for mid in lineup.models:
        have = {e.benchmark_id for e in evidence.get(mid, ())}
        for claim in lineup.claims.get(mid, ()):
            if claim not in domain_map:
                errors.append(f"premier domain {claim!r} has no entry in domain_map")
                continue
            measured += 1
            wanted = set().union(*(tagged[d] for d in domain_map[claim]))
            if not have & wanted:
                findings.append(Finding(mid, f"no verified evidence in {claim} "
                                             f"({', '.join(domain_map[claim])})"))
    return Check(measured, tuple(findings), tuple(sorted(set(errors))))


def check_live_reading_age(lineup: Lineup, evidence: Mapping[str, Sequence[Any]],
                           record: Callable[[str], Mapping[str, Any]], as_of: date,
                           max_age_days: int) -> Check:
    """Days since ModelSpec last read each live board row, per model and benchmark.

    A live reading is a row with ``date_type: evaluated``. Its evidence date is
    the board's run or observation date, which a re-read does not move; the
    reading's age is its winning verification's date.
    """
    findings, measured = [], 0
    for mid in lineup.models:
        newest: dict[str, date | None] = {}
        for e in evidence.get(mid, ()):
            if e.date_type != "evaluated":
                continue
            read = _verified_on(record(e.record_id)) if e.record_id else None
            current = newest.get(e.benchmark_id)
            if e.benchmark_id not in newest or (
                    read is not None and (current is None or read > current)):
                newest[e.benchmark_id] = read
        for bid, day in sorted(newest.items()):
            measured += 1
            if day is None or (as_of - day).days > max_age_days:
                findings.append(Finding(mid, f"{bid}: last read {_age(as_of, day)}"))
    return Check(measured, tuple(findings))


def check_thin_evidence(lineup: Lineup, evidence: Mapping[str, Sequence[Any]],
                        min_benchmarks: int) -> Check:
    findings = []
    for mid in lineup.models:
        n = len({e.benchmark_id for e in evidence.get(mid, ())})
        if n < min_benchmarks:
            findings.append(Finding(mid, f"admitted evidence on {n} benchmark(s), "
                                         f"fewer than {min_benchmarks}"))
    return Check(len(lineup.models), tuple(findings))


def check_facts_verified(lineup: Lineup, authored: Mapping[str, Sequence[str]],
                         rejected: Mapping[tuple[str, str], str],
                         gaps: Iterable[Any]) -> Check:
    """Every stated fact on a lineup subject was admitted.

    A fact stated as ``unknown`` is honest and not a breach; a guaranteed facet
    with no fact at all is (the completeness gate's gap).
    """
    subjects = lineup.subjects()
    found: dict[tuple[str, str], str] = {}
    for (sid, facet), reason in rejected.items():
        if sid in subjects and reason != "unknown":
            found[(sid, facet)] = reason
    for g in gaps:
        if g.subject in subjects and (g.subject, g.facet) not in found:
            found[(g.subject, g.facet)] = g.reason
    considered = {(s, f) for s in subjects for f in authored.get(s, ())} | set(found)
    return Check(len(considered), tuple(Finding(sid, f"{facet}: {reason}")
                                 for (sid, facet), reason in found.items()))


def check_fact_age(subjects: Iterable[str], fact_records: Mapping[str, Mapping[str, str]],
                   record: Callable[[str], Mapping[str, Any]], as_of: date, max_age_days: int,
                   facet_filter: Callable[[str], bool], label: str) -> Check:
    """The oldest winning verification of each subject's matching facts."""
    findings, measured = [], 0
    for sid in sorted(subjects):
        days = [(_verified_on(record(rid)), facet)
                for facet, rid in (fact_records.get(sid) or {}).items() if facet_filter(facet)]
        if not days:
            continue
        measured += 1
        stale = [(d, f) for d, f in days if d is None or (as_of - d).days > max_age_days]
        if stale:
            oldest = min((d for d, _ in stale if d is not None), default=None)
            findings.append(Finding(sid, f"{len(stale)} of {len(days)} {label} fact(s) last "
                                         f"re-read over {max_age_days} days ago; oldest "
                                         f"{_age(as_of, oldest)}"))
    return Check(measured, tuple(findings))


def check_plans(subscriptions: Sequence[Mapping[str, Any]],
                fact_records: Mapping[str, Mapping[str, str]],
                record: Callable[[str], Mapping[str, Any]],
                rejected: Mapping[tuple[str, str], str], as_of: date,
                max_age_days: int) -> Check:
    ids = [str(s["id"]) for s in subscriptions]
    age = check_fact_age(ids, fact_records, record, as_of, max_age_days,
                         lambda _facet: True, "plan")
    unverified = tuple(Finding(sid, f"{facet}: {reason}")
                       for (sid, facet), reason in rejected.items()
                       if "/subscription/" in sid and reason != "unknown")
    return Check(max(age.measured, len(ids)), age.findings + unverified)


def check_speed(lineup: Lineup, fact_records: Mapping[str, Mapping[str, str]],
                record: Callable[[str], Mapping[str, Any]],
                rejected: Mapping[tuple[str, str], str], as_of: date,
                max_age_days: int) -> Check:
    """Each lineup offering needs a ModelSpec speed measurement ending in the window."""
    findings, measured = [], 0
    for offerings in lineup.offerings.values():
        for oid in offerings:
            measured += 1
            for facet in SPEED_FACETS:
                rid = (fact_records.get(oid) or {}).get(facet)
                measurement = record(rid).get("measurement") if rid else None
                if not measurement:
                    why = rejected.get((oid, facet))
                    findings.append(Finding(oid, f"{facet}: no ModelSpec measurement"
                                                 + (f" ({why})" if why else "")))
                    continue
                end = datetime.fromisoformat(
                    str(measurement["window"]["end"]).replace("Z", "+00:00")).date()
                if (as_of - end).days > max_age_days:
                    findings.append(Finding(oid, f"{facet}: measured {_age(as_of, end)}"))
    return Check(measured, tuple(findings))


# ── checks over the release feeds ──────────────────────────────────────────


def check_new_model_cards(api_data: Mapping[str, Any] | None, fetch_error: str | None,
                          models_dir: Path, as_of: date, grace_days: int,
                          window_days: int) -> tuple[Check, tuple[str, ...]]:
    """Listings on a tracked lab's models.dev page, released in the window, with no card.

    A listing is held when the seeder would skip it (a known identity or the
    seeder's own path), when a card with the same file slug exists under any
    lab, or when a card shares its name and release day or its Hugging Face
    repo. Returns the check and the tracked pages absent from the payload.
    """
    if api_data is None:
        return Check(errors=(f"models.dev could not be read: {fetch_error}",)), ()
    from scripts import seed_models_dev as seeder

    known = seeder.load_known_identities()
    identities = seeder.load_catalogue_identities(models_dir)
    slugs = {p.stem for p in models_dir.glob("*/*.md")}
    oldest, newest = as_of - timedelta(days=window_days), as_of - timedelta(days=grace_days)
    findings, absent, measured = [], [], 0
    for pid, cfg in seeder.PROVIDER_MAP.items():
        page = api_data.get(pid)
        if not isinstance(page, Mapping):
            absent.append(pid)
            continue
        measured += 1
        for key, raw in (page.get("models") or {}).items():
            try:
                released = date.fromisoformat(seeder.release_day(raw.get("release_date")))
            except ValueError:
                continue
            if not oldest <= released <= newest:
                continue
            file_slug = seeder.slugify(raw.get("id", key))
            md_id = seeder.models_dev_identity(pid, raw, key)
            held = file_slug in slugs or seeder.already_held(
                models_dev_id=md_id, seeder_id=f"{cfg['slug']}/{file_slug}",
                file_path=models_dir / cfg["slug"] / f"{file_slug}.md",
                models_dir=models_dir, known=known, new_only=True,
            ) or seeder.catalogue_duplicate_warning(
                display_name=str(raw.get("name") or ""), release_date=raw.get("release_date"),
                listing=raw, identities=identities,
                proposed_model_id=f"{cfg['slug']}/{file_slug}",
            )
            if not held:
                findings.append(Finding(md_id, f"{raw.get('name') or key}, released "
                                               f"{released.isoformat()}, has no card"))
    return Check(measured, tuple(findings)), tuple(absent)


def check_lab_feeds(lineup: Lineup, absent_pages: Sequence[str]) -> Check:
    from scripts import seed_models_dev as seeder

    tracked = {cfg["slug"]: pid for pid, cfg in seeder.PROVIDER_MAP.items()}
    labs: dict[str, list[str]] = defaultdict(list)
    for mid in lineup.models:
        labs[mid.split("/", 1)[0]].append(mid)
    findings = []
    for lab, models in sorted(labs.items()):
        if lab not in tracked:
            findings.append(Finding(lab, f"no release feed tracks this lab; lineup models: "
                                         f"{', '.join(sorted(models))}"))
        elif tracked[lab] in absent_pages:
            findings.append(Finding(lab, f"models.dev has no {tracked[lab]!r} page"))
    return Check(len(labs), tuple(findings))


# ── checks over the workflows ──────────────────────────────────────────────


def _when(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def check_workflows(runs: Mapping[str, Sequence[Mapping[str, Any]] | str],
                    watched: Sequence[WatchedWorkflow], now: datetime) -> Check:
    """The latest completed, not-cancelled run of each watched workflow on main."""
    findings, errors, measured = [], [], 0
    for w in watched:
        got = runs.get(w.file)
        if got is None or isinstance(got, str):
            errors.append(f"{w.file}: runs could not be read: {got or 'not fetched'}")
            continue
        measured += 1
        done = sorted((r for r in got if r.get("status") == "completed"
                       and r.get("conclusion") != "cancelled"),
                      key=lambda r: r["created_at"], reverse=True)
        if not done:
            if not any(r.get("status") in ("queued", "in_progress") for r in got):
                findings.append(Finding(w.file, "no completed run on main"))
            continue
        latest = done[0]
        conclusion = latest.get("conclusion")
        where = f"{latest['created_at']} {latest.get('html_url', '')}".strip()
        if conclusion == "skipped" and not w.skipped_ok:
            findings.append(Finding(w.file, f"latest run skipped every job (pipeline "
                                            f"switched off): {where}"))
        elif conclusion not in ("success", "skipped"):
            streak = next((i for i, r in enumerate(done) if r.get("conclusion") == "success"),
                          len(done))
            findings.append(Finding(w.file, f"latest run concluded {conclusion}; "
                                            f"{streak} failing run(s) in a row: {where}"))
        if w.max_age_hours is not None:
            hours = (now - _when(latest["created_at"])).total_seconds() / 3600
            if hours > w.max_age_hours:
                findings.append(Finding(w.file, f"latest completed run is {hours:.0f} h old, "
                                                f"limit {w.max_age_hours:.0f} h"))
    return Check(measured, tuple(findings), tuple(errors))


# ── reading the inputs ─────────────────────────────────────────────────────


#: ``gh`` with arguments and optional stdin, returning stdout; a failure raises.
Gh = Callable[..., str]


def gh_cli(args: Sequence[str], stdin: str | None = None) -> str:
    done = subprocess.run(["gh", *args], check=True, capture_output=True, text=True,
                          input=stdin)
    return done.stdout


def fetch_runs(watched: Sequence[WatchedWorkflow], gh: Gh = gh_cli,
               repo: str = REPO) -> dict[str, Sequence[Mapping[str, Any]] | str]:
    """One REST call per workflow: its ten newest runs on main."""
    out: dict[str, Sequence[Mapping[str, Any]] | str] = {}
    for w in watched:
        try:
            body = gh(["api", f"repos/{repo}/actions/workflows/{w.file}/runs"
                              "?branch=main&per_page=10&exclude_pull_requests=true"])
            out[w.file] = json.loads(body)["workflow_runs"]
        except (subprocess.CalledProcessError, ValueError, KeyError) as exc:
            stderr = getattr(exc, "stderr", "") or ""
            out[w.file] = f"{type(exc).__name__}: {stderr.strip() or exc}"
    return out


def fetch_models_dev() -> tuple[dict | None, str | None]:
    from scripts import seed_models_dev as seeder

    try:
        return seeder.fetch_models_dev(), None
    except seeder.SourceError as exc:
        return None, str(exc)


@dataclass
class Inputs:
    """Everything ``measure`` reads, so a test can supply each one."""

    audit: Any
    premier: Mapping[str, Any]
    authored: Mapping[str, Sequence[str]]
    models_dev: tuple[Mapping[str, Any] | None, str | None]
    runs: Mapping[str, Sequence[Mapping[str, Any]] | str]
    models_dir: Path
    extra_findings: Mapping[str, Sequence[Finding]] = field(default_factory=dict)


def authored_facts(snapshot_inputs: Any) -> dict[str, list[str]]:
    """Subject -> the facets its records state, whatever their verification."""
    out: dict[str, list[str]] = defaultdict(list)
    for m in snapshot_inputs.models:
        out[str(m["id"])].extend(str(f["facet"]) for f in m.get("facts") or ())
    for o in snapshot_inputs.offerings:
        oid = f"{o['provider']}/{o['model']}/{o['region']}/{o['tier']}"
        out[oid].extend(str(f["facet"]) for f in o.get("facts") or ())
    return out


def read_repo(root: Path, as_of: date, *, gh: Gh = gh_cli,
              models_dev: tuple[dict | None, str | None] | None = None) -> Inputs:
    """Build the premier audit from the checkout and read the two network inputs."""
    from decision.excluded import excluded_sources
    from decision.snapshot import audit_build, collect_repo, default_registry, load_premier

    premier_path = root / "premier" / "slice-1.yaml"
    snapshot_inputs = collect_repo(root)
    audit = audit_build(snapshot_inputs, registry=default_registry(),
                        premier=load_premier(premier_path), as_of=as_of,
                        guard=excluded_sources())
    return Inputs(
        audit=audit,
        premier=yaml.safe_load(premier_path.read_text(encoding="utf-8")),
        authored=authored_facts(snapshot_inputs),
        models_dev=models_dev if models_dev is not None else fetch_models_dev(),
        runs=fetch_runs(load_config().workflows, gh),
        models_dir=root / "models",
    )


# ── the report ─────────────────────────────────────────────────────────────


def measure(inputs: Inputs, config: Config, *, as_of: date, now: datetime,
            commit: str | None = None, run_url: str | None = None) -> Report:
    from decision.snapshot import load_built_snapshot

    audit = inputs.audit
    content = audit.snapshot.content
    index = load_built_snapshot(audit.snapshot)
    lineup = lineup_of(content, inputs.premier)
    evidence: dict[str, list[Any]] = defaultdict(list)
    lineup_models = set(lineup.models)
    for mid, row in index.corpus_evidence():
        if mid in lineup_models:
            evidence[mid].append(row)
    fact_records = content.get("fact_records") or {}
    record = index.record
    t = config.target

    new_cards, absent = check_new_model_cards(
        inputs.models_dev[0], inputs.models_dev[1], inputs.models_dir, as_of,
        int(t("new-model-cards").params["grace_days"]),
        int(t("new-model-cards").params["window_days"]))
    offerings = [o for os in lineup.offerings.values() for o in os]
    checks: dict[str, Check] = {
        "new-model-cards": new_cards,
        "lab-release-feeds": check_lab_feeds(lineup, absent),
        "lineup-domain-evidence": check_domain_evidence(
            lineup, evidence, content.get("benchmark_domains") or {}, config.domain_map),
        "live-reading-age": check_live_reading_age(
            lineup, evidence, record, as_of, int(t("live-reading-age").params["max_age_days"])),
        "thin-evidence": check_thin_evidence(
            lineup, evidence, int(t("thin-evidence").params["min_benchmarks"])),
        "lineup-facts-verified": check_facts_verified(
            lineup, inputs.authored, audit.rejected, audit.gaps),
        "offering-price-age": check_fact_age(
            offerings, fact_records, record, as_of,
            int(t("offering-price-age").params["max_age_days"]),
            lambda facet: facet.startswith(PRICE_PREFIX), "price"),
        "plan-age": check_plans(
            content.get("subscriptions") or [], fact_records, record, audit.rejected, as_of,
            int(t("plan-age").params["max_age_days"])),
        "premier-speed-age": check_speed(
            lineup, fact_records, record, audit.rejected, as_of,
            int(t("premier-speed-age").params["max_age_days"])),
        "workflow-health": check_workflows(inputs.runs, config.workflows, now),
    }
    missing = {x.id for x in config.targets} ^ set(checks)
    if missing:
        raise ValueError(f"targets and checks disagree: {sorted(missing)}")
    results = []
    for target in config.targets:
        check = checks[target.id]
        staged = tuple(inputs.extra_findings.get(target.id, ()))
        if staged:
            check = Check(check.measured or len(staged), check.findings + staged, check.errors)
        results.append(settle(target, check))
    return Report(as_of=as_of, generated_at=now, commit=commit,
                  snapshot_id=audit.snapshot.snapshot_id, results=tuple(results),
                  run_url=run_url)


def report_from_json(data: Mapping[str, Any]) -> Report:
    """Read back ``Report.to_json``, for the alert step."""
    return Report(
        as_of=date.fromisoformat(data["as_of"]),
        generated_at=datetime.fromisoformat(data["generated_at"]),
        commit=data.get("commit"),
        snapshot_id=data.get("snapshot_id"),
        run_url=data.get("run_url"),
        results=tuple(
            Result(t["id"], t["title"], t["status"], int(t["measured"]),
                   tuple(Finding(f["subject"], f["detail"]) for f in t["findings"]),
                   tuple(t["errors"]))
            for t in data["targets"]
        ),
    )


def now_utc() -> datetime:
    return datetime.now(UTC).replace(microsecond=0)
