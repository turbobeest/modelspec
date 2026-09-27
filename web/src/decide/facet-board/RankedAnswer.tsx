import { useMemo, useState } from "react";
import { money } from "../adapter";
import type { AdapterDecision, Spec } from "../adapter";
import type { Vocabulary } from "../vocabulary";
import { boardHasPreference } from "./model";

const COLLAPSED_COUNT = 8;

export function RankedAnswer({
  decision,
  spec,
  vocabulary,
}: {
  decision: AdapterDecision;
  spec: Spec;
  vocabulary: Vocabulary;
}) {
  const [expanded, setExpanded] = useState(false);
  const ranked = boardHasPreference(spec);
  const rows = ranked
    ? decision.explanation.feasible
    : [...decision.explanation.feasible].sort((left, right) =>
        left.m.name.localeCompare(right.m.name),
      );
  const visible = expanded ? rows : rows.slice(0, COLLAPSED_COUNT);
  const capability = vocabulary.domains.find((domain) =>
    Object.keys(spec.boardWeights ?? {}).includes(domain.id),
  );
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
    {!ranked && <p className="board-unranked">Not ranked — set a Prefer to rank these</p>}
    {ranked && inseparable.length > 0 && <p className="board-inseparable">
      The evidence can't separate {inseparable.map((row) => row.m.name).join(", ")}.
    </p>}
    {capability && <div className="board-ranked-columns" aria-hidden="true">
      <span />
      <span />
      <small>{capability.name}, estimated · 80% interval</small>
    </div>}
    <ol>
      {visible.map((row) => {
        const value = row.cap ?? extent.min;
        const radius = row.capR?.ci ?? 0;
        const left = 100 * (value - radius - extent.min) / extent.span;
        const width = Math.max(2, 100 * (radius * 2) / extent.span);
        return <li className={capability ? "" : "without-capability"} key={`${row.m.lab}/${row.m.id}`}>
          <div className="board-ranked-copy">
            <strong>{row.m.name}</strong>
            <small>{row.m.labName} · via {row.best.o.provider}</small>
          </div>
          <div className="board-ranked-cost"><small>Cost per task</small><span>{money(row.cost)}</span></div>
          {capability && <div className="board-capability">
            <span className="board-interval-track" aria-label={`${row.m.name} capability interval`}>
              <i style={{ left: `${Math.max(0, left)}%`, width: `${Math.min(100 - Math.max(0, left), width)}%` }} />
              <b style={{ left: `${Math.max(0, Math.min(100, 100 * (value - extent.min) / extent.span))}%` }} />
            </span>
            <small>{row.cap === null ? "unknown" : `${row.cap.toFixed(2)} capability score`}</small>
          </div>}
        </li>;
      })}
    </ol>
    {rows.length > COLLAPSED_COUNT && <button className="text-button board-show-all" onClick={() => setExpanded((current) => !current)}>
      {expanded ? "Show fewer" : `Show all ${rows.length}`}
    </button>}
    {rows.length === 0 && <small>No model qualifies yet.</small>}
  </section>;
}
