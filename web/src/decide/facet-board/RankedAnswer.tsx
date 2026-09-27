import { useMemo, useState } from "react";
import { fmtB, money } from "../adapter";
import type { AdapterDecision, Spec } from "../adapter";

const COLLAPSED_COUNT = 8;

export function RankedAnswer({ decision, spec }: { decision: AdapterDecision; spec: Spec }) {
  const [expanded, setExpanded] = useState(false);
  const rows = decision.explanation.feasible;
  const visible = expanded ? rows : rows.slice(0, COLLAPSED_COUNT);
  const extent = useMemo(() => {
    const values = rows.flatMap((row) => row.cap === null ? [] : [
      row.cap - (row.capR?.ci ?? 0),
      row.cap + (row.capR?.ci ?? 0),
    ]);
    const min = values.length ? Math.min(...values) : 0;
    const max = values.length ? Math.max(...values) : 1;
    return { min, span: Math.max(max - min, Number.EPSILON) };
  }, [rows]);
  const warnedModels = new Set(
    decision.results
      .filter((result) => result.warnings.includes("not_separable"))
      .map((result) => result.offering.model),
  );
  const inseparable = rows.filter((row) =>
    warnedModels.has(`${row.m.lab}/${row.m.id}`) && decision.explanation.insep(row).length > 0,
  );

  return <section className="panel board-ranked-answer">
    {inseparable.length > 0 && <p className="board-inseparable">
      The evidence can't separate {inseparable.map((row) => row.m.name).join(", ")}.
    </p>}
    <ol>
      {visible.map((row) => {
        const value = row.cap ?? extent.min;
        const radius = row.capR?.ci ?? 0;
        const left = 100 * (value - radius - extent.min) / extent.span;
        const width = Math.max(2, 100 * (radius * 2) / extent.span);
        return <li key={`${row.m.lab}/${row.m.id}`}>
          <div className="board-ranked-copy">
            <strong>{row.m.name}</strong>
            <small>{row.best.o.id} · {row.best.o.provider}</small>
          </div>
          <div className="board-ranked-cost"><small>Cost per task</small><span>{money(row.cost)}</span></div>
          <div className="board-capability">
            <span className="board-interval-track" aria-label={`${row.m.name} capability interval`}>
              <i style={{ left: `${Math.max(0, left)}%`, width: `${Math.min(100 - Math.max(0, left), width)}%` }} />
              <b style={{ left: `${Math.max(0, Math.min(100, 100 * (value - extent.min) / extent.span))}%` }} />
            </span>
            <small>{fmtB(spec.bench, row.cap)}</small>
          </div>
        </li>;
      })}
    </ol>
    {rows.length > COLLAPSED_COUNT && <button className="text-button board-show-all" onClick={() => setExpanded((current) => !current)}>
      {expanded ? "Show fewer" : `Show all ${rows.length}`}
    </button>}
    {rows.length === 0 && <small>No model qualifies yet.</small>}
  </section>;
}
