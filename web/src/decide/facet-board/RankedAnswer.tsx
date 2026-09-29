import { useMemo, useState } from "react";
import { money } from "../adapter";
import type { AdapterDecision, Spec } from "../adapter";
import type { Vocabulary } from "../vocabulary";
import { boardHasPreference } from "./model";
import { TieAwareAnswer } from "./TieAwareAnswer";

const COLLAPSED_COUNT = 8;

function median(values: number[]): number | null {
  if (values.length === 0) return null;
  const ordered = values.slice().sort((left, right) => left - right);
  const middle = Math.floor(ordered.length / 2);
  return ordered.length % 2 === 0
    ? (ordered[middle - 1] + ordered[middle]) / 2
    : ordered[middle];
}

function medianPosition(value: number, radius: number, lineupMedian: number): string {
  if (value - radius <= lineupMedian && value + radius >= lineupMedian) return "near the median";
  return value > lineupMedian ? "above the lineup median" : "below the median";
}

function sentenceCase(name: string): string {
  return name.charAt(0).toLocaleLowerCase() + name.slice(1);
}

function domainName(vocabulary: Vocabulary, id: string): string | undefined {
  return vocabulary.domains.find((domain) => domain.id === id)?.name
    ?? vocabulary.coverage?.domains.find((domain) => domain.id === id)?.name;
}

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
  const capability = vocabulary.domains.find((domain) =>
    Object.keys(spec.boardWeights ?? {}).includes(domain.id),
  );
  const activeRefinements = (vocabulary.refinements ?? []).filter((refinement) =>
    Object.keys(spec.boardWeights ?? {}).includes(refinement.weight_key),
  );
  const rows = ranked
    ? decision.explanation.feasible
    : decision.explanation.feasible.slice().sort((left, right) =>
        left.m.name.localeCompare(right.m.name),
      );
  const visible = expanded ? rows : rows.slice(0, COLLAPSED_COUNT);
  const may = ranked && capability ? decision.explanation.may : [];
  const lineupMedian = useMemo(
    () => median(rows.flatMap((row) => row.cap === null ? [] : [row.cap])),
    [rows],
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
  const inseparable = decision.explanation.feasible.filter((row) =>
    warnedModels.has(`${row.m.lab}/${row.m.id}`) && decision.explanation.insep(row).length > 0,
  );

  return <section className="panel board-ranked-answer">
    {ranked && decision.answer && <TieAwareAnswer answer={decision.answer} decision={decision} capabilityName={capability?.name} />}
    {!ranked && <p className="board-unranked">{rows.length} qualify — set a Prefer to rank them</p>}
    {ranked && !decision.answer && inseparable.length > 0 && <p className="board-inseparable">
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
        const otherProviders = [...new Set(row.offs
          .filter((offering) => offering.o.id !== row.best.o.id)
          .map((offering) => offering.o.provider))];
        return <li className={capability ? "" : "without-capability"} key={`${row.m.lab}/${row.m.id}`}>
          <div className="board-ranked-copy">
            <strong>{row.m.name}</strong>
            <small>{row.m.labName} · via {row.best.o.provider}</small>
            {otherProviders.length > 0 && <small>also via {otherProviders.join(", ")}</small>}
            {activeRefinements.map((refinement) => {
              const result = decision.results.find((item) => item.offering.model === `${row.m.lab}/${row.m.id}`);
              const hasEvidence = result?.evidence.some((group) => group.items.some((item) => item.sub_category === refinement.id || refinement.benchmarks.some((benchmark) => benchmark.id === item.benchmark))) ?? false;
              const parentName = domainName(vocabulary, refinement.parent_domain);
              return !hasEvidence && parentName && <small key={refinement.id}>no {refinement.name} evidence — estimated from general {sentenceCase(parentName)}</small>;
            })}
          </div>
          <div className="board-ranked-cost"><small>Cost per task</small><span>{money(row.cost)}</span></div>
          {capability && <div className="board-capability">
            {row.cap === null
              ? <small>no evidence for {capability.name}</small>
              : <>
                <span className="board-interval-track" aria-label={`${row.m.name} capability interval`}>
                  <i style={{ left: `${Math.max(0, left)}%`, width: `${Math.min(100 - Math.max(0, left), width)}%` }} />
                  <b style={{ left: `${Math.max(0, Math.min(100, 100 * (value - extent.min) / extent.span))}%` }} />
                </span>
                <small>{lineupMedian === null ? "near the median" : medianPosition(row.cap, radius, lineupMedian)}</small>
              </>}
          </div>}
        </li>;
      })}
    </ol>
    {rows.length > COLLAPSED_COUNT && <button className="text-button board-show-all" onClick={() => setExpanded((current) => !current)}>
      {expanded ? "Show fewer" : `Show all ${rows.length}`}
    </button>}
    {may.length > 0 && <section className="board-may-qualify">
      <h3>May qualify — no {capability?.name} evidence ({may.length})</h3>
      <ul>
        {may.map((row) => <li key={row.best.o.id}>
          <div className="board-ranked-copy">
            <strong>{row.m.name}</strong>
            <small>{row.m.labName} · via {row.best.o.provider}</small>
          </div>
          <div className="board-ranked-cost"><small>Cost per task</small><span>{money(row.cost)}</span></div>
        </li>)}
      </ul>
    </section>}
    {rows.length === 0 && <small>No model qualifies yet.</small>}
  </section>;
}
