import { useId } from "react";
import { money } from "../adapter";
import type { AdapterDecision } from "../adapter";
import type { Row } from "../engine/reference";
import { payee } from "./routes";

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

function deciding(key: TieBreakerKey, row: Row | undefined): string | null {
  if (key === "cheapest") return row?.cost == null ? null : `${money(row.cost)} per task`;
  if (key === "fastest") return row?.tps == null ? null : `${Math.round(row.tps)} tokens/s`;
  if (key === "open_weights") return "the only open-weights model in the group";
  return null;
}

export function TieAwareAnswer({ answer, decision }: { answer: Answer; decision: AdapterDecision }) {
  const headingId = useId();
  const rows = decision.explanation.feasible;
  const byModel = new Map(rows.map((row) => [rowModel(row), row]));
  const nameOf = (model: string) => byModel.get(model)?.m.name ?? model;

  if (answer.kind === "separated") {
    return <section className="board-tie-answer" aria-labelledby={headingId}>
      <h2 id={headingId}>Clear winner: {nameOf(answer.leader)}</h2>
      <p>No other model's score interval overlaps its.</p>
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
    <h2 id={headingId}>These {members.length} fit. The evidence can't separate them.</h2>
    <p className="board-tie-note">Listed alphabetically, in no order of merit.</p>
    <ul className="board-tie-group">
      {members.map(({ model, row }) => {
        const pickedBy = picks.filter((pick) => pick.model === model).map((pick) => pick.label);
        return <li key={model}>
          <strong>{nameOf(model)}</strong>
          {row && <small>{row.m.labName} · via {payee(row.best.o.provider)}</small>}
          {pickedBy.length > 0 && <span className="board-tie-pick">picked by {pickedBy.join(", ")}</span>}
        </li>;
      })}
    </ul>
    {picks.length > 0
      ? <>
        <h3>What breaks the tie</h3>
        <ul className="board-tie-breakers">
          {picks.map(({ key, label, model }) => {
            const value = deciding(key, byModel.get(model));
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
