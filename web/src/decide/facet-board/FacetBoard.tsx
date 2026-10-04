import { useMemo, useState } from "react";
import type { ReactNode } from "react";
import type { Spec } from "../engine/types";
import type { Vocabulary, VocabFacet, VocabRefinement, VocabTemplate } from "../vocabulary";
import type { CanvasAxes } from "../components/FreeAxisCanvas";
import { TemplatePicker } from "./TemplatePicker";
import type { ActiveTemplate } from "./templates";
import { templateCanvasAxes } from "./templates";
import {
  allocateBoardWeights, boardToSpec, defaultFacetOp, defaultFacetValue, facetGroup, GROUP_ORDER,
  groupFacets, nextMustOrder, readEstate, refinementSelectionId, supportsPreference,
  sanitizeBoardState, templateToBoard, writeEstate,
} from "./model";
import type { BoardSelections, Estate, FacetMode, FacetSelection } from "./model";
import { ACCESS_ANSWERS, deviceName, payee, planName } from "./routes";
import { bestMargin, isBestValue } from "../adapter/view-model";
import { handoffData } from "../handoff-data";
import type { AccessAnswer } from "./routes";

const numberText = (value: unknown) => typeof value === "number" ? String(value) : "";

function ValueControl({ facet, choice, onChange }: {
  facet: VocabFacet;
  choice: FacetSelection;
  onChange: (next: FacetSelection) => void;
}) {
  const value = choice.value;
  const op = choice.op ?? defaultFacetOp(facet);
  if (isBestValue(value)) return (
    <p className="facet-value">Within {bestMargin(value.best)} of the best eligible model</p>
  );
  if (facet.value_type === "boolean") return (
    <label className="facet-value">Required value
      <select value={value === undefined ? "" : String(value)} onChange={(event) => onChange({ ...choice, value: event.target.value === "" ? undefined : event.target.value === "true" })}>
        <option value="">Choose value</option>
        <option value="true">Yes</option><option value="false">No</option>
      </select>
    </label>
  );
  if (facet.value_type === "number" || facet.value_type === "date") return (
    <div className="facet-value inline">
      <label>Operator <select value={op} onChange={(event) => onChange({ ...choice, op: event.target.value as FacetSelection["op"] })}>
        {facet.operators.filter((item) => ["<=", ">=", "=", "!="].includes(item)).map((item) => <option key={item}>{item}</option>)}
      </select></label>
      <label>Threshold <input type={facet.value_type === "date" ? "date" : "number"} value={facet.value_type === "number" ? numberText(value ?? defaultFacetValue(facet)) : String(value ?? defaultFacetValue(facet))} onChange={(event) => onChange({ ...choice, value: event.target.value === "" ? undefined : facet.value_type === "number" ? Number(event.target.value) : event.target.value })} /></label>
      {facet.unit && <span>{facet.unit.replaceAll("_", " ")}</span>}
    </div>
  );
  const selected = value === undefined ? [] : Array.isArray(value) ? value.map(String) : [String(value)];
  const listed = new Set(facet.values?.filter((value) => value.has_data !== false).map((item) => String(item.value)) ?? []);
  const legacyValues = selected.filter((item) => !listed.has(item));
  return <fieldset className="facet-values"><legend>{selected.length ? "Values" : "Choose value(s)"}</legend>{legacyValues.map((item) => <label key={`legacy-${item}`}><input type="checkbox" checked readOnly />{item} (from older link)</label>)}{facet.values?.filter((value) => value.has_data !== false).map((item) => {
    const checked = selected.includes(String(item.value));
    return <label key={String(item.value)}><input type="checkbox" checked={checked} onChange={() => {
      const values = checked ? selected.filter((v) => v !== String(item.value)) : [...selected, String(item.value)];
      if (values.length === 0) onChange({ ...choice, value: undefined });
      else if (facet.value_type === "set" || values.length > 1) onChange({ ...choice, op: "in", value: values });
      else onChange({ ...choice, op: "=", value: values[0] });
    }} />{item.label ?? String(item.value)}{typeof item.count === "number" ? ` (${item.count})` : ""}</label>;
  })}</fieldset>;
}

const KIND_LABELS = { language: "Language", task: "Task", mode: "Mode", material: "Material" } as const;
const EVIDENCE_LABELS = { live: "Live", thin: "Thin", not_measured: "Not yet measured", no_benchmark: "No benchmark" } as const;
const EVIDENCE_ORDER = { live: 0, thin: 1, not_measured: 2, no_benchmark: 3 } as const;

function RefinementRow({ row, choice, parent, allocation, fallback, onChange }: { row: VocabRefinement; choice: FacetSelection; parent: FacetSelection; allocation?: { weight: number; max: number }; fallback: boolean; onChange: (next: FacetSelection) => void }) {
  const [infoOpen, setInfoOpen] = useState(false);
  const disabled = row.evidence_state === "not_measured" || row.evidence_state === "no_benchmark";
  const proxyOnly = row.benchmarks.length > 0 && row.benchmarks.every((benchmark) => benchmark.directness === "proxy");
  const parentWeight = parent.mode === "prefer" || parent.mode === "both" ? parent.weight ?? 0.5 : null;
  const weight = allocation?.weight ?? choice.weight ?? (parentWeight === null ? 0.5 : parentWeight / 2);
  const max = allocation?.max ?? parentWeight ?? 1;
  const reason = row.evidence_state === "not_measured" ? "Benchmarks exist; no scores for these models yet"
    : row.evidence_state === "no_benchmark" ? "No public benchmark measures this yet"
    : row.evidence_state === "thin" ? proxyOnly ? "proxy evidence only" : "Order may rest on 1–2 models"
    : null;
  const preferReasonId = reason ? `refinement-${row.id}-prefer-reason` : undefined;
  return <div className={`refinement-row ${disabled ? "refinement-unavailable" : ""}`} data-refinement={row.id} data-mode={choice.mode === "prefer" ? "prefer" : "off"}>
    <div className="refinement-heading"><span><strong>{row.name}</strong><button className="facet-info" aria-label={`About ${row.name}`} aria-expanded={infoOpen} onClick={() => setInfoOpen(!infoOpen)}>i</button></span><span className={`refinement-badge evidence-${row.evidence_state}`}>{EVIDENCE_LABELS[row.evidence_state]}</span><small>measured on {row.measured_models} of {row.of_models}</small></div>
    {infoOpen && <div className="refinement-definition"><p>{row.definition}</p>{row.benchmarks.length > 0 && <ul>{row.benchmarks.map((benchmark) => <li key={`${benchmark.id}-${benchmark.directness}`}><code>{benchmark.id}</code> · {benchmark.directness}</li>)}</ul>}</div>}
    <div className="facet-state refinement-state" role="radiogroup" aria-label={`State for ${row.name}`}><label className="state-off"><input type="radio" name={`state-refinement-${row.id}`} checked={choice.mode !== "prefer"} onChange={() => onChange({ ...choice, mode: "off" })} />Doesn't matter</label><label className="state-prefer"><input type="radio" name={`state-refinement-${row.id}`} disabled={disabled} aria-describedby={disabled ? preferReasonId : undefined} checked={choice.mode === "prefer"} onChange={() => onChange({ ...choice, mode: "prefer", weight })} />Prefer</label></div>
    {reason && <small id={preferReasonId} className="refinement-reason">{reason}</small>}
    {fallback && choice.mode === "prefer" && <small className="refinement-fallback">Ranked by general {row.parent_domain.replaceAll("_", " ")}: {row.name} isn't ranked separately today.</small>}
    {choice.mode === "prefer" && !disabled && <label className="refinement-weight">{row.name} weight <input aria-label={`Weight for ${row.name}`} type="range" min="0.05" max={max} step="0.05" value={weight} onChange={(event) => onChange({ ...choice, mode: "prefer", weight: Number(event.target.value) })} />{weight.toFixed(2)}</label>}
  </div>;
}

function Refinements({ rows, selections, parent, fallbackKeys, onChange }: { rows: VocabRefinement[]; selections: BoardSelections; parent: FacetSelection; fallbackKeys: ReadonlySet<string>; onChange: (id: string, next: FacetSelection) => void }) {
  const [open, setOpen] = useState(false);
  const active = rows.filter((row) => selections[refinementSelectionId(row.id)]?.mode === "prefer");
  const parentWeight = parent.mode === "prefer" || parent.mode === "both" ? parent.weight ?? 0.5 : null;
  const allocation = allocateBoardWeights({ refinements: rows }, selections);
  const general = parentWeight === null ? null : allocation.general[rows[0]?.parent_domain ?? ""] ?? parentWeight;
  return <section className="refinements"><button className="refine-toggle" aria-expanded={open} onClick={() => setOpen(!open)}>Refine</button>
    {general !== null && active.length > 0 && <div className="refinement-carve"><span>general {general.toFixed(1)}{active.map((row) => ` · ${row.name} ${allocation.refinements[refinementSelectionId(row.id)].weight.toFixed(1)}`).join("")}</span><label>General remainder <input aria-label="General remainder" type="range" min="0" max={parentWeight ?? 1} step="0.05" value={general} readOnly /></label></div>}
    {open && (["language", "task", "mode", "material"] as const).map((kind) => { const grouped = rows.filter((row) => row.kind === kind).sort((left, right) => EVIDENCE_ORDER[left.evidence_state] - EVIDENCE_ORDER[right.evidence_state] || left.name.localeCompare(right.name)); return grouped.length > 0 && <section className="refinement-group" key={kind}><h4>{KIND_LABELS[kind]}</h4>{grouped.map((row) => <RefinementRow key={row.id} row={row} choice={selections[refinementSelectionId(row.id)] ?? { mode: "off" }} parent={parent} allocation={allocation.refinements[refinementSelectionId(row.id)]} fallback={fallbackKeys.has(row.weight_key)} onChange={(next) => onChange(refinementSelectionId(row.id), next)} />)}</section>; })}
  </section>;
}

function FacetRow({ facet, choice, refinements = [], selections = {}, fallbackKeys = new Set(), onChange, onRefinementChange = () => undefined }: { facet: VocabFacet; choice: FacetSelection; refinements?: VocabRefinement[]; selections?: BoardSelections; fallbackKeys?: ReadonlySet<string>; onChange: (next: FacetSelection) => void; onRefinementChange?: (id: string, next: FacetSelection) => void }) {
  const [infoOpen, setInfoOpen] = useState(false);
  const unavailable = facet.known === 0;
  const preference = supportsPreference(facet);
  const setMode = (mode: FacetMode) => {
    const needsDefault = facet.value_type === "number" || facet.value_type === "date" ||
      (facet.preference?.kind === "value" && (mode === "prefer" || mode === "both"));
    onChange({
      ...choice, mode,
      op: choice.op ?? defaultFacetOp(facet),
      ...(choice.value !== undefined
        ? { value: choice.value }
        : needsDefault ? { value: defaultFacetValue(facet) } : {}),
      weight: choice.weight ?? 0.5,
    });
  };
  const must = choice.mode === "must" || choice.mode === "both";
  const prefer = choice.mode === "prefer" || choice.mode === "both";
  return <div className={`facet-row ${choice.mode === "off" ? "facet-off" : ""}`} data-facet={facet.id} data-mode={choice.mode}>
    <div className="facet-copy"><span className="facet-label"><strong>{facet.label}</strong><button className="facet-info" aria-label={`About ${facet.label}`} aria-expanded={infoOpen} onClick={() => setInfoOpen(!infoOpen)}>i</button></span>{infoOpen && <small className="facet-definition">{facet.definition}</small>}{choice.mode === "off" && typeof facet.values?.[0]?.count === "number" && <small>If Must: {facet.values[0].count} survive</small>}{choice.reason && <small className="template-reason">Why: {choice.reason}</small>}</div>
    {facet.known !== undefined && <span className="facet-known">{facet.known}/{facet.of}</span>}
    <div className="facet-controls">
      <div className="facet-state" role="radiogroup" aria-label={`State for ${facet.label}`}>
        <label className="state-off"><input type="radio" name={`state-${facet.id}`} checked={choice.mode === "off"} onChange={() => setMode("off")} />Doesn't matter</label>
        <label className="state-must"><input type="radio" name={`state-${facet.id}`} disabled={unavailable} checked={must && !prefer} onChange={() => setMode("must")} />Must</label>
        {preference && <label className="state-prefer"><input type="radio" name={`state-${facet.id}`} disabled={unavailable} checked={prefer} onChange={() => setMode("prefer")} />Prefer</label>}
      </div>
      {unavailable && <small>Not yet tracked; Must and Prefer are unavailable.</small>}
      {(must || prefer) && !unavailable && <div className="facet-settings">
        {(must || (prefer && facet.preference?.kind === "value")) &&
          <ValueControl facet={facet} choice={choice} onChange={onChange} />}
        {prefer && <label>Weight <input aria-label={`Weight for ${facet.label}`} type="range" min="0.05" max="1" step="0.05" value={choice.weight ?? 0.5} onChange={(event) => onChange({ ...choice, weight: Number(event.target.value) })} />{(choice.weight ?? 0.5).toFixed(2)}</label>}
        {prefer && ["number", "date"].includes(facet.value_type) && <label><input type="checkbox" checked={choice.mode === "both"} onChange={(event) => setMode(event.target.checked ? "both" : "prefer")} />and never worse than…</label>}
      </div>}
      {facet.id.startsWith("capability.") && choice.mode !== "off" && refinements.length > 0 && <Refinements rows={refinements} selections={selections} parent={choice} fallbackKeys={fallbackKeys} onChange={onRefinementChange} />}
    </div>
  </div>;
}

function AccessQuestion({ access, onAccess }: { access: AccessAnswer; onAccess: (access: AccessAnswer) => void }) {
  return <section className="access-question" aria-labelledby="access-question-heading">
    <h2 id="access-question-heading" className="eyebrow">How will you use it?</h2>
    <div role="radiogroup" aria-labelledby="access-question-heading">
      {ACCESS_ANSWERS.map((answer) => <label key={answer.id} className={answer.id === access ? "access-on" : ""}>
        <input type="radio" name="access" value={answer.id} checked={answer.id === access} onChange={() => onAccess(answer.id)} />
        <span><strong>{answer.label}</strong><small>{answer.hint}</small></span>
      </label>)}
    </div>
  </section>;
}

function EstateStrip({ vocabulary, estate, onChange }: { vocabulary: Vocabulary; estate: Estate; onChange: (estate: Estate) => void }) {
  const update = (next: Estate) => { onChange(next); writeEstate(next); };
  const plans = vocabulary.estate.plans;
  const planLabel = (id: string) => planName(plans.find((plan) => plan.id === id)?.name ?? id);
  const providerName = (id: string) => payee(vocabulary.providers[id] ?? id);
  const sellerName = (id: string) => payee(vocabulary.providers[id] ?? vocabulary.vendors[id] ?? id);
  const chip = (label: string, remove: () => void) =>
    <button key={label} className="estate-chip" aria-label={`Remove ${label}`} onClick={remove}>{label} <span aria-hidden="true">×</span></button>;
  const planGroups = [...new Set(plans.filter((plan) => !estate.plans.includes(plan.id)).map((plan) => plan.provider))];
  const devices = vocabulary.estate.devices.filter((id) => !estate.hardware.includes(id));
  return <section className="estate-strip" aria-label="What I already have"><span className="eyebrow">What I already have</span>
    <div>
      {estate.plans.map((id) => chip(planLabel(id), () => update({ ...estate, plans: estate.plans.filter((item) => item !== id) })))}
      {estate.providers.map((id) => chip(`${providerName(id)} account`, () => update({ ...estate, providers: estate.providers.filter((item) => item !== id) })))}
      {estate.hardware.map((id) => chip(deviceName(id), () => update({ ...estate, hardware: estate.hardware.filter((item) => item !== id) })))}
      {plans.length > 0 && <label>+ plan <select aria-label="Add plan" value="" onChange={(event) => event.target.value && update({ ...estate, plans: [...new Set([...estate.plans, event.target.value])] })}><option value="">Choose…</option>{planGroups.map((provider) => <optgroup key={provider} label={sellerName(provider)}>{plans.filter((plan) => plan.provider === provider && !estate.plans.includes(plan.id)).map((plan) => <option key={plan.id} value={plan.id}>{planName(plan.name)}</option>)}</optgroup>)}</select></label>}
      <label>+ pay-per-use account <select aria-label="Add provider" value="" onChange={(event) => event.target.value && update({ ...estate, providers: [...new Set([...estate.providers, event.target.value])] })}><option value="">Choose…</option>{Object.entries(vocabulary.providers).filter(([id]) => !estate.providers.includes(id)).map(([id, label]) => <option key={id} value={id}>{payee(label)}</option>)}</select></label>
      {vocabulary.estate.devices.length > 0 && <label>+ device <select aria-label="Add device" value="" onChange={(event) => event.target.value && update({ ...estate, hardware: [...new Set([...estate.hardware, event.target.value])] })}><option value="">Choose…</option>{devices.map((id) => <option key={id} value={id}>{deviceName(id)}</option>)}</select></label>}
    </div>
    <small className="estate-privacy">Kept in this link and this browser. Sent with each question, never stored.</small>
  </section>;
}

export function FacetBoard({ vocabulary, spec, onSpec, selections, onSelections, mustOrder, onMustOrder, estate, onEstate, access = "any", onAccess, answer, narrowing, verification, fit = 0, may = 0, notes = [], onNotes, refinementFallbackKeys = new Set(), onCanvasAxes, activeTemplate: controlledTemplate, onTemplate }: { vocabulary: Vocabulary; spec: Spec; onSpec: (spec: Spec) => void; selections?: BoardSelections; onSelections?: (selections: BoardSelections) => void; mustOrder?: string[]; onMustOrder?: (mustOrder: string[]) => void; estate: Estate; onEstate: (estate: Estate) => void; access?: AccessAnswer; onAccess?: (access: AccessAnswer) => void; answer?: ReactNode; narrowing?: ReactNode; verification?: ReactNode; fit?: number; may?: number; notes?: string[]; onNotes?: (notes: string[]) => void; refinementFallbackKeys?: ReadonlySet<string>; onCanvasAxes?: (axes: CanvasAxes) => void; activeTemplate?: ActiveTemplate | null; onTemplate?: (template: ActiveTemplate | null) => void }) {
  const [localSelections, setLocalSelections] = useState<BoardSelections>({});
  const [localMustOrder, setLocalMustOrder] = useState<string[]>([]);
  const selected = selections ?? localSelections;
  const orderedMusts = mustOrder ?? localMustOrder;
  const setSelected = (next: BoardSelections) => {
    if (onSelections) onSelections(next);
    else setLocalSelections(next);
  };
  const [templatesOpen, setTemplatesOpen] = useState(false);
  const [localTemplate, setLocalTemplate] = useState<ActiveTemplate | null>(null);
  const activeTemplate = controlledTemplate === undefined ? localTemplate : controlledTemplate;
  const [expandedGroups, setExpandedGroups] = useState<Record<string, boolean>>(() => {
    const active = new Set(Object.entries(selections ?? {}).flatMap(([id, choice]) => choice.mode === "off" ? [] : [facetGroup(id)]));
    return Object.fromEntries(GROUP_ORDER.map((name) => [name, active.has(name)]));
  });
  const grouped = useMemo(() => groupFacets(vocabulary), [vocabulary]);
  const activeRefinementCount = (parentIds?: ReadonlySet<string>) => (vocabulary.refinements ?? []).filter((refinement) => {
    const parentId = `capability.${refinement.parent_domain}`;
    return (!parentIds || parentIds.has(parentId))
      && selected[parentId]?.mode !== undefined
      && selected[parentId]?.mode !== "off"
      && selected[refinementSelectionId(refinement.id)]?.mode === "prefer";
  }).length;
  const activeSelectionCount = Object.entries(selected).filter(([id, choice]) =>
    !id.startsWith("refinement.") && choice.mode !== "off"
  ).length + activeRefinementCount();
  const update = (id: string, next: FacetSelection) => {
    const all = allocateBoardWeights(vocabulary, { ...selected, [id]: next }).selections;
    const nextOrder = nextMustOrder(orderedMusts, selected, id, next);
    const sanitized = sanitizeBoardState({ selections: all, mustOrder: nextOrder, estate }, vocabulary, notes);
    if (next.mode !== "off") setExpandedGroups((current) => ({ ...current, [grouped.groups.find((group) => group.facets.some((facet) => facet.id === id))?.name ?? "Other"]: true }));
    if (onMustOrder) onMustOrder(sanitized.mustOrder); else setLocalMustOrder(sanitized.mustOrder);
    setSelected(sanitized.selections); onNotes?.(sanitized.notes);
    onSpec(boardToSpec(spec, vocabulary, sanitized.selections, sanitized.mustOrder));
  };
  const applyTemplate = (template: VocabTemplate, refinement: VocabRefinement | null = null) => {
    const converted = templateToBoard(template, vocabulary);
    // A subcategory is a Prefer on one refinement, sharing its parent domain's weight.
    const selections = refinement
      ? allocateBoardWeights(vocabulary, {
          ...converted.selections,
          [refinementSelectionId(refinement.id)]: { mode: "prefer", reason: `Subcategory: ${refinement.name}.` },
        }).selections
      : converted.selections;
    const sanitized = sanitizeBoardState({ selections, mustOrder: converted.mustOrder, estate }, vocabulary);
    const all = sanitized.selections;
    const activeGroups = grouped.groups.filter((group) => group.facets.some((facet) => ["must", "prefer", "both"].includes(all[facet.id]?.mode)));
    setExpandedGroups((current) => Object.fromEntries(grouped.groups.map((group) => [group.name, activeGroups.some((active) => active.name === group.name) || current[group.name] === true])));
    const taskTokens = converted.taskTokens ?? vocabulary.default_task_tokens;
    const templateSpec = { ...spec, tokIn: taskTokens.input, tokOut: taskTokens.output };
    if (onMustOrder) onMustOrder(sanitized.mustOrder); else setLocalMustOrder(sanitized.mustOrder);
    setSelected(all); onNotes?.(sanitized.notes); setTemplatesOpen(false);
    const active = { id: template.id, refinement: refinement?.id ?? null };
    setLocalTemplate(active);
    onTemplate?.(active);
    const canvas = templateCanvasAxes(template, vocabulary);
    if (canvas) onCanvasAxes?.(canvas);
    onSpec(boardToSpec(templateSpec, vocabulary, all, sanitized.mustOrder));
  };
  const resetAll = () => {
    const empty = sanitizeBoardState({ selections: {}, mustOrder: [], estate }, vocabulary);
    setSelected(empty.selections);
    if (onMustOrder) onMustOrder([]); else setLocalMustOrder([]);
    onNotes?.([]);
    setExpandedGroups({});
    setLocalTemplate(null); onTemplate?.(null); setTemplatesOpen(false);
    onSpec(boardToSpec(spec, vocabulary, empty.selections, []));
  };
  return <div className="facet-board">
    <TemplatePicker vocabulary={vocabulary} active={activeTemplate} open={templatesOpen} onOpen={setTemplatesOpen} onApply={applyTemplate} onClear={resetAll} />
    {narrowing}
    {notes.length > 0 && <section className="legacy-notes" role="note" aria-label="Notes from your old decision link"><strong>Some settings from this older link are not editable on the board.</strong><ul>{notes.map((note) => <li key={note}>{note}</li>)}</ul></section>}
    {onAccess && <AccessQuestion access={access} onAccess={onAccess} />}
    <EstateStrip vocabulary={vocabulary} estate={estate} onChange={onEstate} />
    <a className="mobile-answer-bar" href="#facet-board-answer">{fit} fit · {may} may <span>View answer ↓</span></a>
    <div className="board-workspace">
      <section className="facet-list" aria-label="Facets"><header><span><span className="eyebrow">Facets</span><small>{activeSelectionCount} set</small></span><button onClick={resetAll}>Reset all</button></header>
        <div className="facet-columns" aria-hidden="true"><span>Facet</span><span>Known</span><span>State</span></div>
        {grouped.groups.map((group) => {
          const active = group.facets.filter((facet) => selected[facet.id]?.mode && selected[facet.id]?.mode !== "off");
          const activeCount = active.length + activeRefinementCount(new Set(group.facets.map((facet) => facet.id)));
          const survival = active.flatMap((facet) => facet.values?.filter((value) => value.has_data !== false).map((value) => value.count) ?? []).filter((count): count is number => typeof count === "number");
          const open = expandedGroups[group.name] === true;
          return <section className="facet-group" key={group.name}><button className="facet-group-summary" aria-expanded={open} onClick={() => setExpandedGroups((current) => ({ ...current, [group.name]: !open }))}><span>{group.name}</span><small>{activeCount ? `${activeCount} set` : "all Doesn't matter"}{survival.length ? ` · → ${Math.min(...survival)} survive` : " · no change"}</small><b aria-hidden="true">{open ? "−" : "+"}</b></button>{open && <div>{group.facets.map((facet) => <FacetRow key={facet.id} facet={facet} choice={selected[facet.id] ?? { mode: "off" }} refinements={(vocabulary.refinements ?? []).filter((row) => facet.id === `capability.${row.parent_domain}`)} selections={selected} fallbackKeys={refinementFallbackKeys} onChange={(choice) => update(facet.id, choice)} onRefinementChange={update} />)}</div>}</section>;
        })}
        {!!grouped.untracked.length && <section className="facet-group untracked"><button className="facet-group-summary" aria-expanded={expandedGroups.untracked === true} onClick={() => setExpandedGroups((current) => ({ ...current, untracked: !current.untracked }))}><span>Not yet tracked</span><small>{grouped.untracked.length} facets · no values</small><b aria-hidden="true">{expandedGroups.untracked ? "−" : "+"}</b></button>{expandedGroups.untracked && <div><p>No model in this snapshot has a value. Must and Prefer are disabled; a null beats a guess.</p>{grouped.untracked.map((facet) => <FacetRow key={facet.id} facet={facet} choice={{ mode: "off" }} onChange={() => undefined} />)}</div>}</section>}
      </section>
      {answer && <aside className="board-answer" id="facet-board-answer">{verification}{answer}</aside>}
    </div>
  </div>;
}

export { readEstate, writeEstate };

/** The board's heading. App renders it before the vocabulary loads, so the
 * page's largest paint does not wait on a fetch (MODEL-218). */
const noPaidPlacement = handoffData.neutrality.text.replace(/^./, (first) => first.toUpperCase());

export function BoardIntro() {
  return <div className="board-intro"><div>
    <span className="eyebrow">Free for people · {noPaidPlacement}</span>
    <h1>Which AI model fits your job?</h1>
    <p>Set what must be true and what you'd prefer. Every model that misses a must is shown out, with the reason, and you see what each one costs. Free for people.</p>
    <p>Then hand it to your agents: the same question, answered the same way, in about a tenth of a second.</p>
    <p className="board-intro-rules">'Must' is a gate; 'Prefer' changes the ranking and never excludes.</p>
    <p className="board-intro-note">About 0.1 s: the median time to first byte for an agent's API decision, measured from Boston on 2026-10-01.</p>
  </div></div>;
}
