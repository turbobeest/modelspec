import { useMemo, useState } from "react";
import type { ReactNode } from "react";
import type { Spec } from "../engine/types";
import type { Vocabulary, VocabFacet } from "../vocabulary";
import {
  boardToSpec, defaultFacetOp, defaultFacetValue, facetGroup, GROUP_ORDER,
  groupFacets, readEstate, supportsPreference, templateToBoard, writeEstate,
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
  const [infoOpen, setInfoOpen] = useState(false);
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
    <div className="facet-copy"><span className="facet-label"><strong>{facet.label}</strong><button className="facet-info" aria-label={`About ${facet.label}`} aria-expanded={infoOpen} onClick={() => setInfoOpen(!infoOpen)}>i</button></span>{infoOpen && <small className="facet-definition">{facet.definition}</small>}{choice.mode === "off" && facet.values?.[0] && <small>If Must: {facet.values[0].count} survive</small>}{choice.reason && <small className="template-reason">Why: {choice.reason}</small>}</div>
    <span className="facet-known">{facet.known}/{facet.of}</span>
    <div className="facet-controls">
      <div className="facet-state" role="radiogroup" aria-label={`State for ${facet.label}`}>
        <label><input type="radio" name={`state-${facet.id}`} checked={choice.mode === "off"} onChange={() => setMode("off")} />Doesn't matter</label>
        <label><input type="radio" name={`state-${facet.id}`} disabled={unavailable} checked={must && !prefer} onChange={() => setMode("must")} />Must</label>
        <label title={!preference ? "coming (MODEL-172)" : undefined}><input type="radio" name={`state-${facet.id}`} disabled={unavailable || !preference} checked={prefer} onChange={() => setMode("prefer")} />Prefer</label>
      </div>
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

export function FacetBoard({ vocabulary, spec, onSpec, selections, onSelections, estate, onEstate, answer, fit = 0, may = 0 }: { vocabulary: Vocabulary; spec: Spec; onSpec: (spec: Spec) => void; selections?: BoardSelections; onSelections?: (selections: BoardSelections) => void; estate: Estate; onEstate: (estate: Estate) => void; answer?: ReactNode; fit?: number; may?: number }) {
  const [localSelections, setLocalSelections] = useState<BoardSelections>({});
  const selected = selections ?? localSelections;
  const setSelected = (next: BoardSelections) => {
    if (onSelections) onSelections(next);
    else setLocalSelections(next);
  };
  const [templatesOpen, setTemplatesOpen] = useState(true);
  const [expandedGroups, setExpandedGroups] = useState<Record<string, boolean>>(() => {
    const active = new Set(Object.entries(selections ?? {}).flatMap(([id, choice]) => choice.mode === "off" ? [] : [facetGroup(id)]));
    return Object.fromEntries(GROUP_ORDER.map((name) => [name, name === "What it's good at" || active.has(name)]));
  });
  const grouped = useMemo(() => groupFacets(vocabulary), [vocabulary]);
  const update = (id: string, next: FacetSelection) => {
    const all = { ...selected, [id]: next };
    if (next.mode !== "off") setExpandedGroups((current) => ({ ...current, [grouped.groups.find((group) => group.facets.some((facet) => facet.id === id))?.name ?? "Other"]: true }));
    setSelected(all); onSpec(boardToSpec(spec, vocabulary, all));
  };
  const applyTemplate = (template: NonNullable<Vocabulary["templates"]>[number]) => {
    const converted = templateToBoard(template, vocabulary);
    const all = converted.selections;
    const activeGroups = grouped.groups.filter((group) => group.facets.some((facet) => ["must", "prefer", "both"].includes(all[facet.id]?.mode)));
    setExpandedGroups((current) => Object.fromEntries(grouped.groups.map((group) => [group.name, group.name === "What it's good at" || activeGroups.some((active) => active.name === group.name) || current[group.name] === true])));
    const templateSpec = converted.taskTokens
      ? { ...spec, tokIn: converted.taskTokens.input, tokOut: converted.taskTokens.output }
      : spec;
    setSelected(all); setTemplatesOpen(false); onSpec(boardToSpec(templateSpec, vocabulary, all));
  };
  return <div className="facet-board">
    <div className="board-intro"><div><span className="eyebrow">Model decision engine</span><h1>Set what matters. Watch the field narrow.</h1><p>Every facet is here. Must is a gate. Prefer changes ranking and never excludes. Nothing is guessed from your words.</p></div>{vocabulary.templates?.length ? <button aria-expanded={templatesOpen} onClick={() => setTemplatesOpen(!templatesOpen)}>ⓘ Templates</button> : null}</div>
    {templatesOpen && vocabulary.templates?.length ? <section className="board-templates"><span className="eyebrow">Start from a template</span><div>{vocabulary.templates.filter((template) => template.available).map((template) => <button key={template.id} onClick={() => applyTemplate(template)}><strong>{template.name}</strong><span>{template.purpose}</span></button>)}</div>{vocabulary.templates.filter((template) => !template.available).map((template) => <p className="template-unavailable" key={template.id}>Not available on today's data: {template.name} — {template.unavailable_reason}</p>)}</section> : null}
    <EstateStrip vocabulary={vocabulary} estate={estate} onChange={onEstate} />
    <a className="mobile-answer-bar" href="#facet-board-answer">{fit} fit · {may} may <span>View answer ↓</span></a>
    <div className="board-workspace">
      <section className="facet-list" aria-label="Facets"><header><span><span className="eyebrow">Facets</span><small>{Object.values(selected).filter((choice) => choice.mode !== "off").length} set</small></span><button onClick={() => { setSelected({}); setExpandedGroups({ "What it's good at": true }); onSpec(boardToSpec(spec, vocabulary, {})); }}>Reset all</button></header>
        <div className="facet-columns" aria-hidden="true"><span>Facet</span><span>Known</span><span>State</span></div>
        {grouped.groups.map((group) => {
          const active = group.facets.filter((facet) => selected[facet.id]?.mode && selected[facet.id]?.mode !== "off");
          const survival = active.flatMap((facet) => facet.values?.map((value) => value.count) ?? []).filter((count): count is number => typeof count === "number");
          const open = expandedGroups[group.name] === true;
          return <section className="facet-group" key={group.name}><button className="facet-group-summary" aria-expanded={open} onClick={() => setExpandedGroups((current) => ({ ...current, [group.name]: !open }))}><span>{group.name}</span><small>{active.length ? `${active.length} set` : "all Doesn't matter"}{survival.length ? ` · → ${Math.min(...survival)} survive` : " · no change"}</small><b aria-hidden="true">{open ? "−" : "+"}</b></button>{open && <div>{group.facets.map((facet) => <FacetRow key={facet.id} facet={facet} choice={selected[facet.id] ?? { mode: "off" }} onChange={(choice) => update(facet.id, choice)} />)}{group.facets.some((facet) => facet.known > 0 && !supportsPreference(facet.id)) && <p className="group-coming">Prefer on these facets: coming (MODEL-172)</p>}</div>}</section>;
        })}
        {!!grouped.untracked.length && <section className="facet-group untracked"><button className="facet-group-summary" aria-expanded={expandedGroups.untracked === true} onClick={() => setExpandedGroups((current) => ({ ...current, untracked: !current.untracked }))}><span>Not yet tracked</span><small>{grouped.untracked.length} facets · no values</small><b aria-hidden="true">{expandedGroups.untracked ? "−" : "+"}</b></button>{expandedGroups.untracked && <div><p>No model in this snapshot has a value. Must and Prefer are disabled; a null beats a guess.</p>{grouped.untracked.map((facet) => <FacetRow key={facet.id} facet={facet} choice={{ mode: "off" }} onChange={() => undefined} />)}</div>}</section>}
      </section>
      {answer && <aside className="board-answer" id="facet-board-answer">{answer}</aside>}
    </div>
  </div>;
}

export { readEstate };
