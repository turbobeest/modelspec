import { useState } from "react";
import {
  TYPES,
  fmtB,
  fmtCI,
  money,
  per1M,
  num,
  daysAgo,
  status,
  reason,
} from "../adapter";
import { useVocab } from "../vocabulary/context";
import type { AdapterDecision, Evidence, Row, Spec } from "../adapter";
import { setWeight } from "../state/spec";
export function Why({
  decision,
  spec,
  row,
  onSpec,
  onRelax,
  onProvenance,
}: {
  decision: AdapterDecision;
  spec: Spec;
  row: Row | null;
  onSpec: (s: Spec) => void;
  onRelax: (i: number) => void;
  onProvenance: (e: Evidence) => void;
}) {
  const vocab = useVocab(),
    { label } = vocab;
  const [whyNot, setWhyNot] = useState(""),
    e = decision.explanation,
    compare = e.rows.find((r) => r.m.id === whyNot);
  if (!row)
    return (
      <section className="panel why-panel" aria-label="Why this model">
        <p>Select a model to inspect its evidence and conditions.</p>
      </section>
    );
  const m = row.m,
    o = row.best.o,
    ranked = e.feasible.find((r) => r.m.id === m.id),
    insep = e.insep(ranked),
    bd = decision.benchmarks[spec.bench];
  const dims = [
    {
      key: "cap",
      name: vocab.benchName(spec.bench),
      value:
        fmtB(spec.bench, row.cap) +
        (row.capR ? " " + fmtCI(spec.bench, row.capR) : ""),
      range: e.feasible.map((r) => r.cap),
      fmt: (v: number) => fmtB(spec.bench, v),
    },
    {
      key: "cost",
      name: "$ per task",
      value: money(row.cost),
      range: e.feasible.flatMap((r) => (r.cost === null ? [] : [r.cost])),
      fmt: money,
    },
    {
      key: "speed",
      name: "Output throughput",
      value: row.tps === null ? "unknown" : row.tps + " tok/s",
      range: e.feasible.flatMap((r) => (r.tps === null ? [] : [r.tps])),
      fmt: (v: number) => v + " tok/s",
    },
  ] as const;
  return (
    <section className="panel why-panel" aria-label="Why this model">
      <div className="why-heading">
        <div>
          <div className="eyebrow">Why this model</div>
          <h2>{m.name}</h2>
          <p>
            {m.labName} ·{" "}
            {m.rel
              ? `released ${m.rel} (${daysAgo(m.rel)} days ago)`
              : "release date not available in this snapshot"}
          </p>
          <div className="inline">
            <span className="badge">
              {m.type ? (vocab.types[m.type] ?? TYPES[m.type]) : "Class not available in this snapshot"}
            </span>
            <span className="badge">
              {m.open === null
                ? "Weights not available in this snapshot"
                : m.open
                  ? "Open weights"
                  : "Closed weights"}
              {m.lic ? ` · ${m.lic}` : ""}
            </span>
            {m.provisional && <span className="badge warn">Provisional</span>}
            {m.status === "retired" && (
              <span className="badge bad">Retired</span>
            )}
          </div>
        </div>
        <div className="why-status">
          <strong
            className={
              status(row) === "May qualify"
                ? "warn"
                : row.status === 1
                  ? "good"
                  : ""
            }
          >
            {status(row)}
            {ranked ? ` · #${row.rank} of ${e.feasible.length}` : ""}
          </strong>
          <small>
            {reason(row) ||
              `Best offering: ${o.provider}, ${money(row.cost)} per task`}
          </small>
        </div>
      </div>
      {m.provisional && (
        <div className="provisional">
          {m.rel ? `Released ${daysAgo(m.rel)} days ago.` : "Release date not available."}{" "}
          {m.bench.filter((b) => b.by === "lab").length} lab-reported scores,{" "}
          {m.bench.filter((b) => b.by === "indep").length} independent. Speed
          not yet measured. Scheduled updates at +1, +7 and +30 days.
        </div>
      )}
      {m.status === "retired" && (
        <div className="retired">
          Retired {m.retiredOn}. Kept in the live archive so past decisions stay
          reproducible; excluded while “Offered now” is on.
        </div>
      )}
      {!!insep.length && (
        <div className="note">
          <strong>Evidence too thin to separate these.</strong>{" "}
          {insep
            .map(
              (r) =>
                `${r.m.name}: ${fmtB(spec.bench, r.cap)} ${fmtCI(spec.bench, r.capR)}`,
            )
            .join("; ")}{" "}
          vs {m.name}: {fmtB(spec.bench, row.cap)}{" "}
          {row.capR && fmtCI(spec.bench, row.capR)}. The order between them is
          decided by cost and speed.
        </div>
      )}
      <div className="why-columns">
        <div>
          <div className="eyebrow">Why it ranks here</div>
          {ranked ? (
            dims
              .filter((d) => vocab.weightKeys.includes(d.key))
              .map((d) => (
              <div className="contribution" key={d.key}>
                <div>
                  <strong>{d.name}</strong>
                  <span>{d.value}</span>
                </div>
                <div
                  className="contribution-track"
                  aria-label={`${d.name} weight ${spec.w[d.key]}, earns ${Math.round(ranked.norm[d.key] * 100)} percent of it`}
                >
                  <span
                    className="weight-outline"
                    style={{ width: spec.w[d.key] * 100 + "%" }}
                  />
                  <span
                    className="earned"
                    style={{ width: ranked.parts[d.key] * 100 + "%" }}
                  />
                </div>
                <small>
                  {d.key === "cap"
                    ? (row.labOnly ? "Lab-reported" : "Independent") + " · "
                    : ""}
                  {d.range.length
                    ? "qualifying field " +
                      d.fmt(Math.min(...d.range)) +
                      " to " +
                      d.fmt(Math.max(...d.range))
                    : "unknown, so it earns nothing here"}
                  {d.key === "cost"
                    ? vocab.vocabulary
                      ? ", compared linearly between the cheapest and the dearest"
                      : ", compared on a log scale"
                    : ""}
                </small>
                {d.key === "cost" && o.costFormula && (
                  <small className="formula">{o.costFormula}</small>
                )}
              </div>
            ))
          ) : (
            <p>
              Not ranked.{" "}
              {status(row) === "May qualify"
                ? "Models that may qualify are not ranked until the unknowns are resolved."
                : "Excluded models are not ranked."}
            </p>
          )}
          <p className="muted">
            The outline is the weight you set; the fill is the share it earns.
            Conditions filter. They never add points.
          </p>
          {e.tip && e.shortlist.top && (
            <div className="tipping">
              <div className="eyebrow">Tipping point</div>
              <p>
                {e.shortlist.top.m.name} stays #1 while the $ per task weight is
                between {(e.tip.lo?.at ?? 0).toFixed(2)} and{" "}
                {(e.tip.hi?.at ?? 1).toFixed(2)}.
                {e.tip.hi &&
                  ` Above ${e.tip.hi.at.toFixed(2)}, ${e.tip.hi.who.m.name} takes #1.`}
                {e.tip.lo &&
                  ` Below ${e.tip.lo.at.toFixed(2)}, ${e.tip.lo.who.m.name} does.`}
              </p>
              <div className="tip-track">
                <span
                  style={{
                    left: (e.tip.lo?.at ?? 0) * 100 + "%",
                    width:
                      ((e.tip.hi?.at ?? 1) - (e.tip.lo?.at ?? 0)) * 100 + "%",
                  }}
                />
              </div>
              <input
                aria-label="Tipping point cost weight"
                type="range"
                min="0"
                max="1"
                step=".01"
                value={spec.w.cost}
                onChange={(ev) =>
                  onSpec({
                    ...spec,
                    w: setWeight(spec.w, "cost", Number(ev.target.value)),
                  })
                }
              />
              <small>$ per task weight · now {spec.w.cost.toFixed(2)}</small>
            </div>
          )}
        </div>
        <div>
          <div className="eyebrow">Evidence, with provenance</div>
          {m.bench
            .slice()
            .sort(
              (a, b) => a.b.localeCompare(b.b) || (a.by === "indep" ? -1 : 1),
            )
            .map((b, i) => (
              <div className="evidence-row" key={i}>
                <div>
                  <strong>{b.b}</strong>
                  <span>
                    {fmtB(b.b, b.v)}{" "}
                    {b.ci === null ? "no interval" : fmtCI(b.b, b)}
                  </span>
                </div>
                <small>
                  {decision.benchmarks[b.b]?.unit ?? "unit not recorded"} · effort{" "}
                  {b.effort} · {b.harness} · {b.date}
                </small>
                <button
                  className={"provenance " + (b.by === "lab" ? "note" : "")}
                  aria-label={`Provenance for ${b.b} ${fmtB(b.b, b.v)}`}
                  onClick={() => onProvenance(b)}
                >
                  {b.by === "lab" ? "Lab-reported" : "Independent"} ↗
                </button>
              </div>
            ))}
          <dl className="facts">
            <div>
              <dt>Context</dt>
              <dd>
                {m.ctx === null
                  ? "not available in this snapshot"
                  : num(m.ctx) + " tokens"}
              </dd>
            </div>
            <div>
              <dt>Licence</dt>
              <dd>
                {m.lic ?? "not available in this snapshot"}
                {m.commercial === false ? " (no commercial use)" : ""}
              </dd>
            </div>
            <div>
              <dt>Origin jurisdiction</dt>
              <dd>{m.origin ?? "not available in this snapshot"}</dd>
            </div>
            <div>
              <dt>Lifecycle</dt>
              <dd>{m.status ?? "not available in this snapshot"}</dd>
            </div>
            <div>
              <dt>Offerings</dt>
              <dd>{m.offerings.length} providers</dd>
            </div>
          </dl>
          <div className="eyebrow">What the lab didn't report</div>
          <p>
            {Object.keys(decision.benchmarks)
              .filter(
                (b) =>
                  (m.type === null || decision.benchmarks[b].types.includes(m.type)) &&
                  !m.bench.some((x) => x.b === b && x.by === "lab"),
              )
              .join(", ") ||
              `${m.labName} reported on every benchmark returned for this decision.`}
          </p>
        </div>
        <div>
          <div className="eyebrow">Condition checks · via {o.provider}</div>
          <ul className="checks">
            {spec.conds.map((c, i) => {
              const t = row.best.t[i],
                state =
                  t.s === 1
                    ? "pass"
                    : t.s === 0
                      ? "unknown"
                      : c.soft
                        ? "soft miss"
                        : "fail";
              return (
                <li key={i} aria-label={label(c) + ": " + state}>
                  <span
                    className={
                      t.s === 1 ? "good" : state === "fail" ? "bad" : "warn"
                    }
                  >
                    {t.s === 1 ? "✓" : t.s === 0 ? "?" : c.soft ? "~" : "✕"}
                  </span>
                  <div>
                    {label(c)}
                    {t.why && <small>{t.why}</small>}
                  </div>
                </li>
              );
            })}
          </ul>
          <div className="costs">
            <div className="eyebrow">What each condition costs you</div>
            {e.costs.map((c) => (
              <div key={c.i}>
                <div className="panel-heading">
                  <span>{c.label}</span>
                  <strong>
                    {c.pts === null
                      ? "unknown"
                      : c.pts === 0
                        ? "costs nothing"
                        : `−${c.pts.toFixed(bd.d)} ${bd.pct ? "pts" : bd.unit}`}
                  </strong>
                </div>
                <div className="cost-track">
                  <span
                    style={{
                      width:
                        ((c.pts || 0) /
                          Math.max(1e-9, ...e.costs.map((c) => c.pts || 0))) *
                          100 +
                        "%",
                    }}
                  />
                </div>
                <small>
                  {c.pts && c.bestAlt
                    ? `Without it, the best ${spec.bench} would be ${c.bestAlt.m.name} at ${fmtB(spec.bench, c.bestAlt.cap)}; ${c.unlocks} more would qualify`
                    : c.unlocks
                      ? `${c.unlocks} more would qualify without it`
                      : "Removing it changes nothing"}
                </small>
              </div>
            ))}
          </div>
          <div className="near-misses">
            <div className="eyebrow">Near misses</div>
            {decision.nearMisses.slice(0, 4).map((n, i) => (
              <div key={n.row.m.id}>
                <strong>{n.row.m.name}</strong>
                <small>{n.why}</small>
                <button onClick={() => onRelax(i)}>
                  {n.relaxed ? vocab.relaxLabel(n.relaxed) : "Drop condition"}
                </button>
              </div>
            ))}
            {!decision.nearMisses.length && (
              <small>No model is one condition away.</small>
            )}
          </div>
          <label className="why-not">
            Why not…
            <select
              aria-label="Why not"
              value={whyNot}
              onChange={(ev) => setWhyNot(ev.target.value)}
            >
              <option value="">Choose a model</option>
              {e.rows.map(({ m }) => (
                <option key={m.id} value={m.id}>
                  {m.name} · {m.labName}
                </option>
              ))}
            </select>
          </label>
          {compare && (
            <p>
              {compare.m.name}: {status(compare)}
              {compare.rank ? " · #" + compare.rank : ""}. {reason(compare)}{" "}
              {compare.rank &&
                `${vocab.benchName(spec.bench)}: ${fmtB(spec.bench, compare.cap)}; ${money(compare.cost)} per task; ${compare.tps ?? "unknown"} tok/s.`}
            </p>
          )}
        </div>
      </div>
      <div className="offerings">
        <div className="eyebrow">Offerings for {m.name}</div>
        <p className="formula">
          $/task = {num(spec.tokIn)} × {per1M(o.in)}/1M + {num(spec.tokOut)} ×{" "}
          {per1M(o.out)}/1M = {money(row.cost)}
        </p>
        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                {[
                  "Provider",
                  "Regions",
                  "In $/1M",
                  "Out $/1M",
                  "$ per task",
                  "First token",
                  "Tok/s",
                  "Retention",
                  "Against your conditions",
                ].map((t) => (
                  <th key={t}>{t}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {row.offs.map((off) => (
                <tr
                  key={off.o.id}
                  className={off === row.best ? "selected" : ""}
                >
                  <td>
                    {off.o.provider}
                    {off === row.best && <small>· used for ranking</small>}
                  </td>
                  <td>{off.o.regions?.join(", ") || "not stated"}</td>
                  <td>{per1M(off.o.in)}</td>
                  <td>{per1M(off.o.out)}</td>
                  <td>{money(off.cost)}</td>
                  <td>
                    {off.o.ttft === null ? "unknown" : off.o.ttft + " ms"}
                  </td>
                  <td>{off.o.tps ?? "unknown"}</td>
                  <td>
                    {off.o.ret === null
                      ? "not published"
                      : off.o.ret === "contract"
                        ? "0 d with enterprise contract"
                        : off.o.ret + " days"}
                  </td>
                  <td>
                    {off.s === 1
                      ? "Qualifies"
                      : off.s === 0
                        ? "May qualify"
                        : "Excluded"}
                    <small>
                      {off.t
                        .filter((t) => t.s !== 1)
                        .map((t) => t.why)
                        .join("; ")}
                    </small>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}
