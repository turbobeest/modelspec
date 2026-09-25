import { z } from "zod";

const facetId = z.string().regex(/^-?[a-z][a-z0-9_-]*(\.[a-z0-9_-]+)*$/);
const modelId = z.string().regex(/^[a-z0-9][a-z0-9._-]*\/[a-z0-9][a-z0-9._-]*$/);
const nullableString = z.string().nullable();

export const offeringRefSchema = z
  .object({
    model: modelId,
    provider: nullableString,
    region: nullableString,
    tier: nullableString,
  })
  .strict();

export const evidenceItemSchema = z
  .object({
    benchmark: z.string(),
    version: nullableString,
    sub_category: nullableString,
    value: z.number().finite(),
    unit: nullableString,
    n: z.number().int().positive().nullable(),
    measured_by: z.enum([
      "independent",
      "provider_self_report",
      "benchmark_author",
      "modelspec",
      "outcome_protocol",
    ]),
    effort: nullableString,
    harness: nullableString,
    date: z.iso.date(),
    date_type: z.enum(["published", "observed"]),
    source: z.url(),
    source_snapshot: nullableString,
    directness: z.enum(["direct", "proxy"]),
  })
  .strict();

const estimateSchema = z
  .object({
    domain: facetId,
    value: z.number().finite(),
    interval: z.tuple([z.number().finite(), z.number().finite()]),
    harness: nullableString,
    effort: nullableString,
  })
  .strict();

const contributionSchema = z
  .object({
    dimension: facetId,
    weight: z.number().finite().nullable(),
    value: z.number().finite().nullable(),
    normalisation: nullableString,
    evidence: z.array(evidenceItemSchema),
  })
  .strict();

const resultSchema = z
  .object({
    rank: z.number().int().positive(),
    offering: offeringRefSchema,
    harness: nullableString,
    effort: nullableString,
    evidence: z.array(
      z.object({ domain: facetId, items: z.array(evidenceItemSchema) }).strict(),
    ),
    estimates: z.array(estimateSchema).nullable(),
    p_best: z.number().min(0).max(1).nullable(),
    top3_stability: z.number().min(0).max(1).nullable(),
    soft_penalty: z.number().nonnegative(),
    contributions: z.array(contributionSchema),
    warnings: z.array(z.string().regex(/^[a-z0-9_]+$/)),
  })
  .strict();

export const decisionSchema = z
  .object({
    contract_version: z.literal("1.0"),
    decision_id: z.string().regex(/^dec_[0-9A-Za-z]{8,}$/),
    snapshot: z.string().regex(/^snap_[A-Za-z0-9:._-]+$/),
    spec_hash: z.string().regex(/^sha256:[0-9a-f]{64}$/),
    explain: z.enum(["none", "summary", "full"]),
    status: z.enum(["answered", "partial", "no_feasible"]),
    results: z.array(resultSchema),
    may_qualify: z.array(
      z
        .object({
          model: modelId,
          offering: offeringRefSchema.nullable(),
          unknown: z.array(facetId),
        })
        .strict(),
    ),
    eliminated: z
      .object({
        funnel: z.array(
          z
            .object({
              condition: z.string(),
              before: z.number().int().nonnegative(),
              after: z.number().int().nonnegative(),
              may_qualify: z.number().int().nonnegative(),
            })
            .strict(),
        ),
        models: z.array(
          z
            .object({
              model: modelId,
              condition: z.string(),
              value: z.union([z.string(), z.number(), z.boolean()]).nullable(),
            })
            .strict(),
        ),
      })
      .strict(),
    constraint_costs: z.array(
      z
        .object({
          condition: z.string(),
          admits: z.number().int().nonnegative(),
          gain: z.record(facetId, z.number().finite()),
        })
        .strict(),
    ),
    tipping_points: z.array(
      z
        .object({
          description: z.string(),
          dimension: facetId.nullable(),
          threshold: z.number().finite().nullable(),
          new_top: modelId.nullable(),
        })
        .strict(),
    ),
    relax: z.array(z.string()),
    warnings: z.array(z.string().regex(/^[a-z0-9_]+$/)),
  })
  .strict();

const objectiveSchema = z.union([
  z.object({ max: facetId }).strict(),
  z.object({ min: facetId }).strict(),
  z.object({ weights: z.record(facetId, z.number().positive()) }).strict(),
  z.object({ pareto: z.array(facetId).min(2) }).strict(),
  z
    .object({
      lexicographic: z
        .array(
          z.union([
            z.object({ max: facetId, within: z.unknown().optional() }).strict(),
            z.object({ min: facetId, within: z.unknown().optional() }).strict(),
          ]),
        )
        .min(2),
    })
    .strict(),
]);

export const decisionSpecSchema = z
  .object({
    spec_version: z.literal(1),
    snapshot: z
      .union([z.literal("latest"), z.string().regex(/^snap_[A-Za-z0-9:._-]+$/)])
      .optional(),
    profile: z
      .union([
        z.string().regex(/^profile:[a-z0-9][a-z0-9-]*$/),
        z.record(z.string(), z.unknown()),
      ])
      .nullable()
      .optional(),
    task: z.string().nullable().optional(),
    task_type: z
      .enum([
        "new_feature",
        "bug_fix",
        "refactor",
        "test_writing",
        "docs",
        "migration",
        "performance",
        "security_fix",
        "review",
        "analysis",
        "data_transform",
        "config_infra",
      ])
      .nullable()
      .optional(),
    capabilities: z
      .record(facetId, z.enum(["required", "preferred"]))
      .nullable()
      .optional(),
    where: z
      .array(z.union([z.string(), z.record(z.string(), z.unknown())]))
      .optional(),
    optimize: objectiveSchema,
    unknowns: z.literal("default").optional(),
    explain: z.enum(["none", "summary", "full"]).optional(),
    limit: z.number().int().min(1).max(500).optional(),
    save_as: z
      .string()
      .regex(/^[a-z0-9][a-z0-9-]{0,63}$/)
      .nullable()
      .optional(),
  })
  .strict();

export type OfferingRef = z.infer<typeof offeringRefSchema>;
export type EvidenceItem = z.infer<typeof evidenceItemSchema>;
export type Result = z.infer<typeof resultSchema>;
export type Decision = z.infer<typeof decisionSchema>;
export type DecisionSpec = z.infer<typeof decisionSpecSchema>;
