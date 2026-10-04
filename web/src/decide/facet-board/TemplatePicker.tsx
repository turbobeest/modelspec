import { useId, useRef, useState } from "react";
import type { CSSProperties } from "react";
import type { VocabRefinement, VocabTemplate, Vocabulary } from "../vocabulary";
import { activeTemplateLabel, availableTemplates, fastTrackTemplates, refinementFor, templateGrid } from "./templates";
import type { ActiveTemplate, TemplateCategory, TemplateGrid, TemplateRow, TemplateTier } from "./templates";

const KIND_ORDER: VocabRefinement["kind"][] = ["language", "task", "mode", "material"];
const KIND_NAMES: Record<VocabRefinement["kind"], string> = {
  language: "Language", task: "Task", mode: "Mode", material: "Material",
};

function SubcategorySelect({ row, value, onChange }: { row: TemplateRow; value: string; onChange: (id: string) => void }) {
  if (row.subcategories.length === 0) return null;
  return (
    <label className="template-subcategory">
      <span>Subcategory</span>
      <select aria-label={`${row.category.name} subcategory`} value={value} onChange={(event) => onChange(event.target.value)}>
        <option value="">Any {row.category.name.toLowerCase()}</option>
        {KIND_ORDER.map((kind) => {
          const members = row.subcategories.filter((refinement) => refinement.kind === kind);
          return members.length ? (
            <optgroup key={kind} label={KIND_NAMES[kind]}>
              {members.map((refinement) => (
                <option key={refinement.id} value={refinement.id}>
                  {refinement.name}{refinement.evidence_state === "thin" ? " (thin evidence)" : ""}
                </option>
              ))}
            </optgroup>
          ) : null;
        })}
      </select>
    </label>
  );
}

function Cell({ template, category, tier, refinement, onApply }: {
  template: VocabTemplate | null;
  category: TemplateCategory;
  tier: TemplateTier;
  refinement: VocabRefinement | null;
  onApply: (template: VocabTemplate, refinement: VocabRefinement | null) => void;
}) {
  if (!template) return (
    <td className="template-empty"><span aria-hidden="true">—</span><span className="template-sr">No {tier.name} template</span></td>
  );
  const subject = `${category.name}${refinement ? ` › ${refinement.name}` : ""} · ${tier.name}`;
  return (
    <td>
      <button type="button" aria-label={`${subject}: ${template.tradeoff ?? template.purpose}`} title={template.purpose} onClick={() => onApply(template, refinement)}>
        <span className="template-tier-label">{tier.name}</span>
        <span>{template.tradeoff ?? template.purpose}</span>
      </button>
    </td>
  );
}

function Grid({ grid, onApply }: { grid: TemplateGrid; onApply: (template: VocabTemplate, refinement: VocabRefinement | null) => void }) {
  const [subcategory, setSubcategory] = useState<Record<string, string>>({});
  return <>
    {grid.kinds.map((group) => (
      <table className="template-grid" key={group.kind} style={{ "--tiers": group.tiers.length } as CSSProperties}>
        <caption>{group.label}</caption>
        <thead>
          <tr><th scope="col"><span className="template-sr">Category</span></th>{group.tiers.map((tier) => <th scope="col" key={tier.id}>{tier.name}</th>)}</tr>
        </thead>
        <tbody>
          {group.rows.map((row) => {
            const chosen = row.subcategories.find((refinement) => refinement.id === subcategory[row.category.id]);
            return (
              <tr key={row.category.id}>
                <th scope="row">
                  <strong>{row.category.name}</strong>
                  <SubcategorySelect row={row} value={chosen?.id ?? ""} onChange={(id) => setSubcategory((current) => ({ ...current, [row.category.id]: id }))} />
                </th>
                {row.cells.map((template, index) => (
                  <Cell
                    key={group.tiers[index].id}
                    template={template}
                    category={row.category}
                    tier={group.tiers[index]}
                    refinement={template ? refinementFor(template, chosen) : null}
                    onApply={onApply}
                  />
                ))}
              </tr>
            );
          })}
        </tbody>
      </table>
    ))}
  </>;
}

/** Templates from a vocabulary published before categories: one flat list. */
function FlatList({ templates, onApply }: { templates: VocabTemplate[]; onApply: (template: VocabTemplate, refinement: null) => void }) {
  return <div className="template-flat">{templates.map((template) =>
    <button type="button" key={template.id} onClick={() => onApply(template, null)}><strong>{template.name}</strong><span>{template.purpose}</span></button>)}</div>;
}

/**
 * Common jobs are one click away; the full category-by-tier list stays available.
 * Only templates this snapshot can answer are offered (MODEL-277).
 */
export function TemplatePicker({ vocabulary, active, open, onOpen, onApply, onClear }: {
  vocabulary: Vocabulary;
  active: ActiveTemplate | null;
  open: boolean;
  onOpen: (open: boolean) => void;
  onApply: (template: VocabTemplate, refinement: VocabRefinement | null) => void;
  onClear: () => void;
}) {
  const panel = useId();
  const bar = useRef<HTMLButtonElement>(null);
  const templates = availableTemplates(vocabulary);
  // A full-list cell unmounts on apply. Keep keyboard focus on the list control.
  const apply = (template: VocabTemplate, refinement: VocabRefinement | null) => {
    onApply(template, refinement);
    bar.current?.focus();
  };
  if (templates.length === 0) return null;
  const grid = templateGrid(vocabulary);
  const label = activeTemplateLabel(vocabulary, active);
  return (
    <section className="panel template-picker" aria-label="Templates">
      <div className="template-heading"><span className="eyebrow">Start from a template</span>
        {label && <div className="template-active"><span>Starting from: <strong>{label}</strong></span>
          <button type="button" className="text-button" onClick={() => { onClear(); bar.current?.focus(); }}>Clear</button>
        </div>}
        <button ref={bar} type="button" className="template-all" aria-expanded={open} aria-controls={panel} onClick={() => onOpen(!open)}>
          {open ? "Hide templates" : `All ${templates.length} templates`}
        </button>
      </div>
      <div className="template-shortcuts">{fastTrackTemplates(vocabulary).map((template) =>
        <button type="button" className="primary template-shortcut" key={template.id} aria-pressed={active?.id === template.id && active.refinement === null} onClick={() => onApply(template, null)}>
          <strong>{active?.id === template.id && active.refinement === null && <span className="template-check" aria-hidden="true">✓ </span>}{template.name}</strong><span>{template.tradeoff ?? template.purpose}</span>
        </button>)}</div>
      <div className="board-templates" id={panel} hidden={!open}>
        {open && (grid ? <Grid grid={grid} onApply={apply} /> : <FlatList templates={templates} onApply={apply} />)}
      </div>
    </section>
  );
}
