import { z } from "zod";

const facetId = z.string().regex(/^-?[a-z][a-z0-9_-]*(\.[a-z0-9_-]+)*$/);
const modelId = z.string().regex(/^[a-z0-9][a-z0-9._-]*\/[a-z0-9][a-z0-9._-]*$/);
const nullableString = z.string().nullable();
const scalar = z.union([z.string(), z.number().finite(), z.boolean()]);

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
    requested_domain: nullableString.optional(),
    record_id: nullableString.optional(),
    benchmark: z.string(),
    version: nullableString,
    sub_category: nullableString,
    value: z.number().finite(),
    unit: nullableString,
    n: z.number().int().positive().nullable(),
    interval: z
      .tuple([z.number().finite(), z.number().finite()])
      .nullable()
      .optional()
      .default(null),
    quality_flags: z
      .array(z.enum(["deprecated", "contamination_warning"]))
      .optional()
      .default([]),
    measured_by: z.enum([
      "independent",
      "provider_self_report",
      "benchmark_author",
      "modelspec",
      "outcome_protocol",
    ]),
    effort: nullableString,
    harness: nullableString,
    harness_unregistered: z.boolean().optional().default(false),
    date: z.iso.date(),
    date_type: z.enum(["published", "observed"]),
    source: z.url(),
    source_snapshot: nullableString,
    directness: z.enum(["direct", "proxy"]),
    loading: z.number().finite().nullable().optional(),
    estimate_weight: z.number().min(0).max(1).nullable().optional(),
    recency_weight: z.number().min(0).max(1).nullable().optional(),
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
    raw_value: z.number().finite().nullable().optional(),
    unit: nullableString.optional(),
    records: z.array(z.string()).optional(),
    dimension: facetId,
    weight: z.number().finite().nullable(),
    value: z.number().finite().nullable(),
    normalisation: nullableString,
    evidence: z.array(evidenceItemSchema),
    formula: nullableString.optional(),
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
    near_misses: z
      .array(
        z
          .object({
            values: z.array(scalar),
            offering: offeringRefSchema,
            condition: z.string(),
            facet: nullableString,
            value: scalar.nullable(),
            distance: z.number().finite().nullable(),
            unit: nullableString,
            records: z.array(z.string()),
            formula: nullableString.optional(),
          })
          .strict(),
      )
      .optional()
      .default([]),
    top: z
      .array(
        z
          .object({
            offering: offeringRefSchema,
            facts: z.array(
              z
                .object({
                  facet: z.string(),
                  value: z.union([scalar, z.array(scalar)]).nullable(),
                  unit: nullableString,
                  record_id: nullableString,
                  records: z.array(z.string()).optional(),
                  formula: nullableString.optional(),
                  // 1.4: the fact's sources, as IDs into the decision's `sources`.
                  source_ids: z.array(z.string()).optional().default([]),
                })
                .strict(),
            ),
            contributions: z.array(contributionSchema),
            evidence: z.array(
              z
                .object({
                  domain: facetId,
                  items: z.array(evidenceItemSchema),
                })
                .strict(),
            ),
          })
          .strict(),
      )
      .optional()
      .default([]),
    chart: nullableString.optional().default(null),
    number_origins: z
      .array(
        z
          .object({
            path: z.string(),
            basis: z.string(),
            records: z.array(z.string()),
            // Always empty from 1.4, which names sources by `source_ids`.
            sources: z.array(z.url()),
            source_ids: z.array(z.string()).optional().default([]),
          })
          .strict(),
      )
      .optional()
      .default([]),
    // 1.4: every source the origins and shown facts cite, once each.
    sources: z
      .array(
        z
          .object({
            id: z.string(),
            url: z.url(),
            title: nullableString,
            date: z.iso.date().nullable(),
          })
          .strict(),
      )
      .optional()
      .default([]),
    contract_version: z.enum([
      "1.1",
      "1.2",
      "1.3",
      "1.4",
      "1.5",
      "1.6",
      "1.7",
      "1.8",
    ]),
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
              models_before: z.number().int().nonnegative().optional().default(0),
              models_after: z.number().int().nonnegative().optional().default(0),
              offerings_before: z.number().int().nonnegative().optional().default(0),
              offerings_after: z.number().int().nonnegative().optional().default(0),
              models_may_qualify: z.number().int().nonnegative().optional().default(0),
              offerings_may_qualify: z.number().int().nonnegative().optional().default(0),
            })
            .strict(),
        ),
        models: z.array(
          z
            .object({
              values: z.array(scalar).optional().default([]),
              offering: offeringRefSchema.nullable().optional().default(null),
              unit: nullableString.optional().default(null),
              records: z.array(z.string()).optional().default([]),
              model: modelId,
              condition: z.string(),
              value: scalar.nullable(),
              formula: nullableString.optional(),
            })
            .strict(),
        ),
        model_groups: z
          .array(
            z
              .object({
                model: modelId,
                model_elimination: z
                  .object({
                    values: z.array(scalar).optional().default([]),
                    offering: offeringRefSchema.nullable().optional().default(null),
                    unit: nullableString.optional().default(null),
                    records: z.array(z.string()).optional().default([]),
                    model: modelId,
                    condition: z.string(),
                    value: scalar.nullable(),
                    formula: nullableString.optional(),
                  })
                  .strict()
                  .nullable(),
                offerings: z.array(
                  z
                    .object({
                      values: z.array(scalar).optional().default([]),
                      offering: offeringRefSchema,
                      unit: nullableString.optional().default(null),
                      records: z.array(z.string()).optional().default([]),
                      condition: z.string(),
                      value: scalar.nullable(),
                      formula: nullableString.optional(),
                    })
                    .strict(),
                ),
              })
              .strict(),
          )
          .optional()
          .default([]),
      })
      .strict(),
    constraint_costs: z.array(
      z
        .object({
          units: z.record(z.string(), nullableString).optional().default({}),
          records: z.array(z.string()).optional().default([]),
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
    // 1.5: the smallest change to each numeric cap or floor that admits a model.
    relax_to: z
      .array(
        z
          .object({
            condition: z.string(),
            relaxed: z.string(),
            facet: facetId,
            value: z.number().finite(),
            unit: z.string().nullable(),
            admits: z.number().int().positive(),
          })
          .strict(),
      )
      .optional()
      .default([]),
    warnings: z.array(z.string().regex(/^[a-z0-9_]+$/)),
    out_of_lineup: z.number().int().nonnegative().optional().default(0),
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
    task_tokens: z
      .object({
        input: z.number().int().nonnegative(),
        output: z.number().int().nonnegative(),
      })
      .strict()
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
export type Contribution = z.infer<typeof contributionSchema>;
