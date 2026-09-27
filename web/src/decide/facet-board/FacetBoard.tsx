import { useMemo, useState } from "react";
import type { Spec } from "../engine/types";
import type { Vocabulary, VocabFacet } from "../vocabulary";
import {
  boardToSpec, defaultFacetOp, defaultFacetValue, groupFacets, readEstate,
  supportsPreference, writeEstate,
} from "./model";
import type { BoardSelections, Estate, FacetMode, FacetSelection } from "./model";

const numberText = (value: unknown) => typeof value === "number" ? String(value) : "0";

function ValueControl({ facet, choice, onChange }: {
  facet: VocabFacet;
  choice: FacetSelection;
  onChange: (next: FacetSelection) => void;
}) {
  const value = choice.value ?? defaultFacetValue(facet);
  const op = choice.op ?? defaultFacetOp(facet);
  if (facet.value_type === "boolean") return (
    <label className="facet-value">Required value
      <select value={String(value)} onChange={(event) => onChange({ ...choice, value: event.target.value === "true" })}>
        <option value="true">Yes</option><option value="false">No</option>
      </select>
    </label>
  );
  if (facet.value_type === "number" || facet.value_type === "date") return (
    <div className="facet-value inline">
      <label>Operator <select value={op} onChange={(event) => onChange({ ...choice, op: event.target.value as FacetSelection["op"] })}>
        {facet.operators.filter((item) => ["<=", ">=", "=", "!="].includes(item)).map((item) => <option key={item}>{item}</option>)}
      </select></label>
      <label>Threshold <input type={facet.value_type === "date" ? "date" : "number"} value={facet.value_type === "number" ? numberText(value) : String(value)} onChange={(event) => onChange({ ...choice, value: facet.value_type === "number" ? Number(event.target.value) : event.target.value })} /></label>
      {facet.unit && <span>{facet.unit.replaceAll("_", " ")}</span>}
    </div>
  );
  const selected = Array.isArray(value) ? value.map(String) : [String(value)];
  return <fieldset className="facet-values"><legend>Values</legend>{facet.values?.map((item) => {
    const checked = selected.includes(String(item.value));
    return <label key={String(item.value)}><input type="checkbox" checked={checked} onChange={() => {
      const values = checked ? selected.filter((v) => v !== String(item.value)) : [...selected, String(item.value)];
      onChange({ ...choice, op: "in", value: values });
    }} />{item.label ?? String(item.value)}</label>;
  })}</fieldset>;
}

function FacetRow({ facet, choice, onChange }: { facet: VocabFacet; choice: FacetSelection; onChange: (next: FacetSelection) => void }) {
  const unavailable = facet.known === 0;
  const preference = supportsPreference(facet.id);
  const setMode = (mode: FacetMode) => onChange({
    ...choice, mode,
    op: choice.op ?? defaultFacetOp(facet), value: choice.value ?? defaultFacetValue(facet),
    weight: choice.weight ?? 0.5,
  });
  const must = choice.mode === "must" || choice.mode === "both";
  const prefer = choice.mode === "prefer" || choice.mode === "both";
  return <div className={`facet-row ${choice.mode === "off" ? "facet-off" : ""}`} data-facet={facet.id}>
    <div className="facet-copy"><strong>{facet.label}</strong><small>{facet.definition}</small>{choice.mode === "off" && facet.values?.[0] && <small>Set to Must with {facet.values[0].label ?? String(facet.values[0].value)}: {facet.values[0].count} survive</small>}{choice.reason && <small className="template-reason">Why: {choice.reason}</small>}</div>
    <span className="facet-known">{facet.known}/{facet.of}</span>
    <div className="facet-controls">
      <div className="facet-state" role="radiogroup" aria-label={`State for ${facet.label}`}>
        <label><input type="radio" name={`state-${facet.id}`} checked={choice.mode === "off"} onChange={() => setMode("off")} />Doesn't matter</label>
        <label><input type="radio" name={`state-${facet.id}`} disabled={unavailable} checked={must && !prefer} onChange={() => setMode("must")} />Must</label>
        <label title={!preference ? "coming (MODEL-172)" : undefined}><input type="radio" name={`state-${facet.id}`} disabled={unavailable || !preference} checked={prefer && !must} onChange={() => setMode("prefer")} />Prefer</label>
      </div>
      {!preference && !unavailable && <small>Prefer coming (MODEL-172)</small>}
      {unavailable && <small>Not yet tracked; Must and Prefer are unavailable.</small>}
      {(must || prefer) && !unavailable && <div className="facet-settings">
        {must && <ValueControl facet={facet} choice={choice} onChange={onChange} />}
        {prefer && <label>Weight <input aria-label={`Weight for ${facet.label}`} type="range" min="0.05" max="1" step="0.05" value={choice.weight ?? 0.5} onChange={(event) => onChange({ ...choice, weight: Number(event.target.value) })} />{(choice.weight ?? 0.5).toFixed(2)}</label>}
        {prefer && ["number", "date"].includes(facet.value_type) && <label><input type="checkbox" checked={choice.mode === "both"} onChange={(event) => setMode(event.target.checked ? "both" : "prefer")} />and never worse than…</label>}
      </div>}
      {facet.id.startsWith("capability.") && <details className="benchmarks"><summary>Benchmarks</summary><p>Benchmark switches: coming (MODEL-171)</p></details>}
    </div>
  </div>;
}

function EstateStrip({ vocabulary, estate, onChange }: { vocabulary: Vocabulary; estate: Estate; onChange: (estate: Estate) => void }) {
  const update = (next: Estate) => { onChange(next); writeEstate(next); };
  return <section className="estate-strip" aria-label="My estate"><span className="eyebrow">My estate</span>
    <div>{estate.providers.map((provider) => <button key={provider} onClick={() => update({ ...estate, providers: estate.providers.filter((item) => item !== provider) })}>{vocabulary.providers[provider] ?? provider} ×</button>)}
      <label>+ provider <select aria-label="Add provider" value="" onChange={(event) => event.target.value && update({ ...estate, providers: [...new Set([...estate.providers, event.target.value])] })}><option value="">Choose…</option>{Object.entries(vocabulary.providers).filter(([id]) => !estate.providers.includes(id)).map(([id, label]) => <option key={id} value={id}>{label}</option>)}</select></label>
    </div><div><button onClick={() => update({ ...estate, plans: [...estate.plans, "Plan"] })}>+ plan</button> <small>coming (MODEL-173)</small> <button onClick={() => update({ ...estate, hardware: [...estate.hardware, "Device"] })}>+ hardware</button> <small>coming (MODEL-174)</small></div>
  </section>;
}

export function FacetBoard({ vocabulary, spec, onSpec, estate, onEstate }: { vocabulary: Vocabulary; spec: Spec; onSpec: (spec: Spec) => void; estate: Estate; onEstate: (estate: Estate) => void }) {
  const [selections, setSelections] = useState<BoardSelections>({});
  const [templatesOpen, setTemplatesOpen] = useState(true);
  const grouped = useMemo(() => groupFacets(vocabulary), [vocabulary]);
  const update = (id: string, next: FacetSelection) => {
    const all = { ...selections, [id]: next };
    setSelections(all); onSpec(boardToSpec(spec, vocabulary, all));
  };
  const applyTemplate = (template: NonNullable<Vocabulary["templates"]>[number]) => {
    const all = Object.fromEntries(template.facets.map(({ id, ...choice }) => [id, { ...choice }]));
    setSelections(all); setTemplatesOpen(false); onSpec(boardToSpec(spec, vocabulary, all));
  };
  return <div className="facet-board">
    <div className="board-intro"><div><span className="eyebrow">Model decision engine</span><h1>Set what matters. Watch the field narrow.</h1><p>Every facet is here. Must is a gate. Prefer changes ranking and never excludes. Nothing is guessed from your words.</p></div>{vocabulary.templates?.length ? <button aria-expanded={templatesOpen} onClick={() => setTemplatesOpen(!templatesOpen)}>ⓘ Templates</button> : null}</div>
    {templatesOpen && vocabulary.templates?.length ? <section className="board-templates"><span className="eyebrow">Start from a template</span><div>{vocabulary.templates.map((template) => <button key={template.id} onClick={() => applyTemplate(template)}><strong>{template.name}</strong><span>{template.description}</span></button>)}</div></section> : null}
    <EstateStrip vocabulary={vocabulary} estate={estate} onChange={onEstate} />
    <section className="facet-list" aria-label="Facets"><header><span className="eyebrow">Facets</span><button onClick={() => { setSelections({}); onSpec(boardToSpec(spec, vocabulary, {})); }}>Reset all</button></header>
      {grouped.groups.map((group) => <details key={group.name} open><summary>{group.name}</summary>{group.facets.map((facet) => <FacetRow key={facet.id} facet={facet} choice={selections[facet.id] ?? { mode: "off" }} onChange={(choice) => update(facet.id, choice)} />)}</details>)}
      {!!grouped.untracked.length && <details className="untracked"><summary>Not yet tracked · {grouped.untracked.length}</summary><p>No model in this snapshot has a value. Must and Prefer are disabled; a null beats a guess.</p>{grouped.untracked.map((facet) => <FacetRow key={facet.id} facet={facet} choice={{ mode: "off" }} onChange={() => undefined} />)}</details>}
    </section>
  </div>;
}

export { readEstate };
