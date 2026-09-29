import { useId } from "react";
import { money } from "../adapter";
import type { AdapterDecision } from "../adapter";
import type { Row } from "../engine/reference";

type Answer = NonNullable<AdapterDecision["answer"]>;
type TieBreakerKey = keyof Answer["tie_breakers"];

const TIE_BREAKERS: { key: TieBreakerKey; label: string }[] = [
  { key: "cheapest", label: "cheapest" },
  { key: "fastest", label: "fastest" },
  { key: "open_weights", label: "open weights" },
  { key: "most_independently_measured", label: "most independently measured" },
];

const rowModel = (row: Row) => `${row.m.lab}/${row.m.id}`;
const capitalise = (text: string) => text.charAt(0).toLocaleUpperCase() + text.slice(1);

function independentMeasurements(decision: AdapterDecision, model: string): number {
  return decision.results
    .filter((result) => result.offering.model === model)
    .flatMap((result) => result.evidence.flatMap((group) => group.items))
    .filter((item) => item.measured_by === "independent").length;
}

function deciding(key: TieBreakerKey, row: Row | undefined, decision: AdapterDecision, model: string): string | null {
  if (key === "cheapest") return row?.cost == null ? null : `${money(row.cost)} per task`;
  if (key === "fastest") return row?.tps == null ? null : `${Math.round(row.tps)} tokens/s`;
  if (key === "open_weights") return "the only open-weights model in the group";
  const count = independentMeasurements(decision, model);
  return count > 0 ? `${count} independent ${count === 1 ? "measurement" : "measurements"}` : null;
}

export function TieAwareAnswer({
  answer,
  decision,
  capabilityName,
}: {
  answer: Answer;
  decision: AdapterDecision;
  capabilityName?: string;
}) {
  const headingId = useId();
  const rows = decision.explanation.feasible;
  const byModel = new Map(rows.map((row) => [rowModel(row), row]));
  const nameOf = (model: string) => byModel.get(model)?.m.name ?? model;

  if (answer.kind === "separated") {
    const leader = byModel.get(answer.leader);
    const next = rows
      .filter((row) => rowModel(row) !== answer.leader && row.cap !== null)
      .sort((left, right) => (right.cap ?? 0) - (left.cap ?? 0))[0];
    const interval = (row: Row) => {
      const radius = row.capR?.ci ?? 0;
      return `${row.cap!.toFixed(1)} (80% interval ${(row.cap! - radius).toFixed(1)}–${(row.cap! + radius).toFixed(1)})`;
    };
    return <section className="board-tie-answer" aria-labelledby={headingId}>
      <h3 id={headingId}>Clear winner: {nameOf(answer.leader)}</h3>
      <p>No other model's score interval overlaps its.</p>
      {leader?.cap != null && next && <p className="board-tie-gap">
        {capabilityName ? `${capitalise(capabilityName)}, estimated` : "Capability estimate"}: {interval(leader)}, against {interval(next)} for {next.m.name}, the next model.
      </p>}
    </section>;
  }

  const members = answer.members
    .map((model) => ({ model, row: byModel.get(model) }))
    .sort((left, right) => nameOf(left.model).localeCompare(nameOf(right.model)));
  const picks = TIE_BREAKERS.flatMap(({ key, label }) => {
    const model = answer.tie_breakers[key];
    return model === null ? [] : [{ key, label, model }];
  });

  return <section className="board-tie-answer" aria-labelledby={headingId}>
    <h3 id={headingId}>These {members.length} fit. The evidence can't separate them.</h3>
    <p className="board-tie-note">Listed alphabetically, in no order of merit.</p>
    <ul className="board-tie-group">
      {members.map(({ model, row }) => {
        const pickedBy = picks.filter((pick) => pick.model === model).map((pick) => pick.label);
        return <li key={model}>
          <strong>{nameOf(model)}</strong>
          {row && <small>{row.m.labName} · via {row.best.o.provider}</small>}
          {pickedBy.length > 0 && <span className="board-tie-pick">picked by {pickedBy.join(", ")}</span>}
        </li>;
      })}
    </ul>
    {picks.length > 0
      ? <>
        <h4>What breaks the tie</h4>
        <ul className="board-tie-breakers">
          {picks.map(({ key, label, model }) => {
            const value = deciding(key, byModel.get(model), decision, model);
            return <li key={key}>
              <span>{capitalise(label)}</span>
              <strong>{nameOf(model)}</strong>
              {value && <small>{value}</small>}
            </li>;
          })}
        </ul>
      </>
      : <p>No tie-breaker separates them either.</p>}
  </section>;
}
