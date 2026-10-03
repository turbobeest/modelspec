import type { VocabRefinement, VocabTemplate, Vocabulary } from "../vocabulary";

/** The applied template, and the subcategory (a refinement ID) it was applied with. */
export interface ActiveTemplate {
  id: string;
  refinement: string | null;
}

export type TemplateCategory = NonNullable<Vocabulary["template_categories"]>[number];
export type TemplateTier = NonNullable<Vocabulary["template_tiers"]>[number];

export interface TemplateRow {
  category: TemplateCategory;
  /** One cell per tier of its table, in tier order; null where the category has no available template for that tier. */
  cells: (VocabTemplate | null)[];
  /** Refinements a tier of this category can prefer, with measured evidence. */
  subcategories: VocabRefinement[];
}

export interface TemplateGrid {
  /** One table per kind, with only the tiers and categories that have an available template. */
  kinds: { kind: TemplateCategory["kind"]; label: string; tiers: TemplateTier[]; rows: TemplateRow[] }[];
}

const KIND_LABELS: Record<TemplateCategory["kind"], string> = {
  use: "By use",
  constraint: "By constraint",
};

/** The templates a visitor can apply on this snapshot. The board offers no others (MODEL-277). */
export const availableTemplates = (vocabulary: Vocabulary): VocabTemplate[] =>
  (vocabulary.templates ?? []).filter((template) => template.available);

/**
 * The category-by-tier grid, entirely from the vocabulary, holding only
 * available templates: a category with none is not a row, and a tier with none
 * in a table is not a column. Null when the vocabulary predates categories
 * (contract 2.8) and the page lists templates flat.
 */
export function templateGrid(vocabulary: Vocabulary): TemplateGrid | null {
  const categories = vocabulary.template_categories;
  const tiers = vocabulary.template_tiers;
  const all = vocabulary.templates ?? [];
  if (!categories?.length || !tiers?.length || all.some((row) => !row.category || !row.tier)) return null;
  const templates = availableTemplates(vocabulary);
  const kinds = (["use", "constraint"] as const).map((kind) => {
    const members = categories
      .filter((category) => category.kind === kind)
      .map((category) => ({ category, templates: templates.filter((row) => row.category === category.id) }))
      .filter((row) => row.templates.length > 0);
    const shown = tiers.filter((tier) => members.some((row) => row.templates.some((template) => template.tier === tier.id)));
    const rows = members.map(({ category, templates: own }): TemplateRow => {
      const domains = new Set(all.filter((row) => row.category === category.id).flatMap((row) => row.needs.domains));
      return {
        category,
        cells: shown.map((tier) => own.find((row) => row.tier === tier.id) ?? null),
        subcategories: (vocabulary.refinements ?? []).filter((refinement) =>
          domains.has(refinement.parent_domain) &&
          (refinement.evidence_state === "live" || refinement.evidence_state === "thin"),
        ),
      };
    });
    return { kind, label: KIND_LABELS[kind], tiers: shown, rows };
  });
  return { kinds: kinds.filter((group) => group.rows.length > 0) };
}

/** "Coding › Rust · Budget", or the template's own name when it has no category. */
export function activeTemplateLabel(vocabulary: Vocabulary, active: ActiveTemplate | null): string | null {
  if (!active) return null;
  const template = vocabulary.templates?.find((row) => row.id === active.id);
  if (!template) return null;
  const category = vocabulary.template_categories?.find((row) => row.id === template.category);
  const tier = vocabulary.template_tiers?.find((row) => row.id === template.tier);
  if (!category || !tier) return template.name;
  const refinement = active.refinement
    ? vocabulary.refinements?.find((row) => row.id === active.refinement && template.needs.domains.includes(row.parent_domain))
    : undefined;
  return `${category.name}${refinement ? ` › ${refinement.name}` : ""} · ${tier.name}`;
}

/** A refinement can only be preferred beside a template that weights its parent domain. */
export function refinementFor(template: VocabTemplate, refinement: VocabRefinement | undefined): VocabRefinement | null {
  return refinement && Object.keys(template.weights).includes(refinement.parent_domain) ? refinement : null;
}
