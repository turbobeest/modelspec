import { useId } from "react";
import { money } from "../adapter";
import type { AdapterDecision } from "../adapter";
import type { BandEntry, BlendTerm } from "../adapter/contract";
import type { Row } from "../engine/reference";
import { payee } from "./routes";
import { leadingModels } from "./leading";

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

/** A probability as the page says it: whole percent, never a false 0% or 100%. */
function percent(value: number): string {
  if (value > 0 && value < 0.005) return "under 1%";
  if (value < 1 && value > 0.995) return "over 99%";
  return `${Math.round(value * 100)}%`;
}

function listed(names: string[]): string {
  if (names.length < 2) return names.join("");
  return `${names.slice(0, -1).join(", ")} and ${names.at(-1)}`;
}

const isCost = (dimension: string) => dimension.replace(/^-/, "") === "offering.cost_per_task";

function measured(entry: BandEntry): string {
  if (entry.estimates.length === 0) return "no capability estimate";
  const { benchmarks, direct_benchmarks: direct } = entry.estimates.reduce((fewest, estimate) =>
    estimate.direct_benchmarks < fewest.direct_benchmarks ? estimate : fewest);
  const text = `measured on ${benchmarks} benchmark${benchmarks === 1 ? "" : "s"}`;
  if (direct === benchmarks) return text;
  if (direct === 0) return `${text}, ${benchmarks === 1 ? "not" : "none of them"} directly`;
  return `${text}, ${direct} directly`;
}

function estimateText(entry: BandEntry): string | null {
  const [first] = entry.estimates;
  if (!first) return null;
  const [low, high] = first.interval;
  return `estimate ${first.value.toFixed(2)} (80% interval ${low.toFixed(2)} to ${high.toFixed(2)})`;
}

/** "On your 60/40 mix of software engineering and cost per task". */
function mixSentence(blend: BlendTerm[], dimensionName: (key: string) => string): string | null {
  if (blend.length < 2) return null;
  const shares = blend.map((term) => Math.round(term.share * 100)).join("/");
  return `On your ${shares} mix of ${listed(blend.map((term) => dimensionName(term.dimension).toLocaleLowerCase()))}`;
}

function termSentence(term: BlendTerm, nameOf: (model: string) => string, dimensionName: (key: string) => string): string {
  const name = capitalise(dimensionName(term.dimension).toLocaleLowerCase());
  if (term.leaders.length === 0) return `${name} alone: no model has enough evidence to lead.`;
  if (!term.estimated) {
    const leaders = listed(term.leaders.map(nameOf));
    if (isCost(term.dimension)) {
      const price = term.value === null ? "" : ` (${money(term.value)} per task)`;
      return `${name} alone: cheapest is ${leaders}${price}.`;
    }
    return `${name} alone: ${leaders} lead${term.leaders.length === 1 ? "s" : ""}.`;
  }
  const leader = nameOf(term.leaders[0]);
  let text = `${name} alone: ${leader} leads`;
  if (term.p_best !== null) text += `, ${percent(term.p_best)} likely the strongest of the well-measured models`;
  if (term.runner_up !== null && term.p_runner_up !== null)
    text += `; ${nameOf(term.runner_up)} is ahead of it with probability ${percent(term.p_runner_up)}`;
  return `${text}.`;
}

export function TieAwareAnswer({
  answer,
  decision,
  dimensionName = (key) => key.replace(/^-/, ""),
}: {
  answer: Answer | null | undefined;
  decision: AdapterDecision;
  dimensionName?: (key: string) => string;
}) {
  const headingId = useId();
  const rows = decision.explanation.feasible;
  const byModel = new Map(rows.map((row) => [rowModel(row), row]));
  const nameOf = (model: string) => byModel.get(model)?.m.name ?? model;
  const bands = decision.bands;
  const blend = decision.blend ?? [];
  const mix = mixSentence(blend, dimensionName);

  const picks = answer?.kind === "tied"
    ? TIE_BREAKERS.flatMap(({ key, label }) => {
      const model = answer.tie_breakers[key];
      return model === null ? [] : [{ key, label, model }];
    })
    : [];
  const banded = new Map(bands?.best.map((entry) => [entry.model, entry]) ?? []);
  const leading = (leadingModels(decision) ?? []).map((model): Pick<BandEntry, "model" | "p_best" | "p_beats_leader" | "cost_per_task"> =>
    banded.get(model) ?? { model, p_best: null, p_beats_leader: null, cost_per_task: null });
  const heading = leading.length === 0
    ? "No model has enough evidence to lead yet"
    : leading.length === 1
      ? `Best for your weights: ${nameOf(leading[0].model)}`
      : `Best for your weights: these ${leading.length}. The evidence can't separate them.`;
  const ordered = leading.some((entry) => entry.p_best !== null);

  return <section className="board-tie-answer" aria-labelledby={headingId}>
    {mix && <p className="board-blend">{mix}.</p>}
    <h2 id={headingId}>{heading}</h2>
    {leading.length === 1 && bands && <p className="board-tie-note">
      Every other model with enough evidence is behind it with probability over {percent(1 - bands.band_probability)}.
    </p>}
    {leading.length > 1 && <p className="board-tie-note">
      {ordered ? "Ordered by chance of being best." : "In score order; the order is not evidence that one is better."}
    </p>}
    {leading.length > 1 && <ol className="board-tie-group">
      {leading.map((entry) => {
        const row = byModel.get(entry.model);
        const pickedBy = picks.filter((pick) => pick.model === entry.model).map((pick) => pick.label);
        return <li key={entry.model}>
          <strong>{nameOf(entry.model)}</strong>
          {row && <small>{row.m.labName} · via {payee(row.best.o.provider)}</small>}
          {entry.p_best !== null && <small>{percent(entry.p_best)} chance of being best</small>}
          {entry.p_beats_leader !== null && <small>{percent(entry.p_beats_leader)} likely to score at least as well as {nameOf(bands?.leader ?? entry.model)}</small>}
          {pickedBy.length > 0 && <span className="board-tie-pick">picked by {pickedBy.join(", ")}</span>}
        </li>;
      })}
    </ol>}
    {answer?.kind === "tied" && (picks.length > 0
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
      : <p>No tie-breaker separates them either.</p>)}
    {blend.length > 1 && <>
      <h3>Each part of the mix alone</h3>
      <ul className="board-blend-terms">
        {blend.map((term) => <li key={term.dimension}>{termSentence(term, nameOf, dimensionName)}</li>)}
      </ul>
    </>}
    {bands && bands.rest.length > 0 && <>
      <h3>The rest, in order</h3>
      <ol className="board-band-rest">
        {bands.rest.map((entry) => <li key={entry.model}>
          <strong>{nameOf(entry.model)}</strong>
          {estimateText(entry) && <small>{estimateText(entry)}</small>}
          {entry.cost_per_task !== null && <small>{money(entry.cost_per_task)} per task</small>}
          {entry.p_beats_leader !== null && bands.leader && <small>{percent(entry.p_beats_leader)} likely to score at least as well as {nameOf(bands.leader)}</small>}
        </li>)}
      </ol>
    </>}
    {bands && bands.thin.length > 0 && <>
      <h3>Not enough evidence yet</h3>
      <ul className="board-band-thin">
        {bands.thin.map((entry) => <li key={entry.model}>
          <strong>{nameOf(entry.model)}</strong>
          <small>{measured(entry)}</small>
          {estimateText(entry) && <small>{estimateText(entry)}</small>}
        </li>)}
      </ul>
    </>}
  </section>;
}
