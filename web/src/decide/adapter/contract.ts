import { z } from "zod";

const facetId = z.string().regex(/^-?[a-z][a-z0-9_-]*(\.[a-z0-9_-]+)*$/);
const objectiveId = z.string().regex(/^-?[a-z][a-z0-9_-]*(\.[a-z0-9_-]+)*(\/[a-z][a-z0-9_-]*)?$/);
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

// 2.4 (MODEL-190): a refinement estimate nested in its parent domain.
const refinementEstimateSchema = z
  .object({
    key: z.string().regex(/^[a-z][a-z0-9_]*\/[a-z][a-z0-9_]*$/),
    domain: facetId,
    refinement: facetId,
    value: z.number().finite(),
    interval: z.tuple([z.number().finite(), z.number().finite()]),
    evidence_count: z.number().int().nonnegative(),
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
    preferred_value: scalar.nullable().optional(),
    preference_status: z
      .enum(["satisfied", "not_satisfied", "unknown"])
      .nullable()
      .optional(),
    refinement: facetId.nullish(),
  })
  .strict();

// 2.6 (MODEL-200): a subscription plan that reaches a result on the spec's
// `access`. Each part the plan page does not publish is null.
const planPriceSchema = z
  .object({
    amount: z.number().nonnegative(),
    currency: z.literal("USD"),
    period: z.enum(["monthly", "annual"]),
  })
  .strict();

export const planCoverageSchema = z
  .object({
    family: nullableString.optional(),
    quote: nullableString.optional(),
    resolves_to: z.array(modelId).optional().default([]),
    rule: z.string(),
  })
  .strict();

const planAllowanceSchema = z
  .object({
    relative_to: nullableString.optional(),
    multiplier: z.number().nonnegative().nullable().optional(),
    window: nullableString.optional(),
    tokens: z.number().nonnegative().nullable().optional(),
  })
  .strict();

const planRouteSchema = z
  .object({
    plan: z.string(),
    name: z.string(),
    surface: z.string(),
    price: planPriceSchema.nullable().optional(),
    price_monthly_usd: z.number().nonnegative().nullable().optional(),
    coverage: planCoverageSchema,
    allowance: planAllowanceSchema.optional(),
    break_even_tasks_per_month: z.number().nonnegative().nullable().optional(),
    basis: z.string(),
  })
  .strict();

const resultSchema = z
  .object({
    rank: z.number().int().positive(),
    // 2.5 flat fields. Older saved decisions predate them.
    model: modelId.optional(),
    model_rank: z.number().int().positive().nullable().optional(),
    cost_per_task: z.number().nullable().optional(),
    offering: offeringRefSchema,
    harness: nullableString,
    effort: nullableString,
    evidence: z.array(
      z.object({ domain: facetId, items: z.array(evidenceItemSchema) }).strict(),
    ),
    estimates: z.array(estimateSchema).nullable(),
    refinement_estimates: z.array(refinementEstimateSchema).nullish(),
    p_best: z.number().min(0).max(1).nullable(),
    top3_stability: z.number().min(0).max(1).nullable(),
    soft_penalty: z.number().nonnegative(),
    contributions: z.array(contributionSchema),
    warnings: z.array(z.string().regex(/^[a-z0-9_]+$/)),
    // 2.6: absent without `access`.
    plans: z.array(planRouteSchema).optional(),
  })
  .strict();

const modelRowStatus = z.enum(["ranked", "may_qualify", "eliminated"]);

const modelOfferingSchema = z
  .object({
    offering: offeringRefSchema,
    status: modelRowStatus,
    rank: z.number().int().positive().nullable(),
    cost_per_task: z.number().nullable(),
    unknown: z.array(facetId),
    reason: z.string().nullable(),
  })
  .strict();

const modelRowSchema = z
  .object({
    model: modelId,
    status: modelRowStatus,
    rank: z.number().int().positive().nullable(),
    cost_per_task: z.number().nullable(),
    offerings: z.array(modelOfferingSchema),
  })
  .strict();

const tieBreakersSchema = z
  .object({
    cheapest: modelId.nullable(),
    open_weights: modelId.nullable(),
    most_independently_measured: modelId.nullable(),
    fastest: modelId.nullable(),
  })
  .strict();

const answerSchema = z.discriminatedUnion("kind", [
  z
    .object({
      kind: z.literal("separated"),
      members: z.array(modelId).length(1),
      leader: modelId,
      basis: z.string(),
      tie_breakers: tieBreakersSchema,
      deterministic_order: z.array(modelId).length(1),
    })
    .strict(),
  z
    .object({
      kind: z.literal("tied"),
      members: z.array(modelId).min(2),
      basis: z.string(),
      tie_breakers: tieBreakersSchema,
      deterministic_order: z.array(modelId).min(2),
    })
    .strict(),
]);

// 2.7 (MODEL-206): the ranked models in three bands, and the named blend.
const bandEntrySchema = z
  .object({
    model: modelId,
    offering: offeringRefSchema,
    score: z.number(),
    score_interval: z.tuple([z.number(), z.number()]),
    p_best: z.number().min(0).max(1).nullable(),
    p_beats_leader: z.number().min(0).max(1).nullable(),
    cost_per_task: z.number().nullable(),
    estimates: z.array(
      z
        .object({
          dimension: z.string(),
          value: z.number(),
          interval: z.tuple([z.number(), z.number()]),
          benchmarks: z.number().int().nonnegative(),
          direct_benchmarks: z.number().int().nonnegative(),
        })
        .strict(),
    ),
  })
  .strict();

const bandsSchema = z
  .object({
    basis: z.string(),
    band_probability: z.number(),
    thin_interval_width: z.number(),
    leader: modelId.nullable(),
    best: z.array(bandEntrySchema),
    rest: z.array(bandEntrySchema),
    thin: z.array(bandEntrySchema),
  })
  .strict();

const blendTermSchema = z
  .object({
    dimension: z.string(),
    weight: z.number(),
    share: z.number().min(0).max(1),
    estimated: z.boolean(),
    leaders: z.array(modelId),
    value: z.number().nullable(),
    p_best: z.number().min(0).max(1).nullable(),
    runner_up: modelId.nullable(),
    p_runner_up: z.number().min(0).max(1).nullable(),
    order: z.array(modelId),
    thin: z.array(modelId),
  })
  .strict();

const accessKind = z.enum(["chat_app", "coding_tool", "own_software", "own_hardware"]);

const truncatedSchema = z
  .object({
    offerings: z.number().int().nonnegative(),
    models: z.number().int().nonnegative(),
  })
  .strict();

const mayQualifySchema = z
  .object({
    model: modelId,
    offering: offeringRefSchema.nullable(),
    unknown: z.array(facetId),
  })
  .strict();

const decisionStatus = z.enum(["answered", "partial", "no_feasible"]);

// 2.3 (MODEL-179): the same question answered from what the caller holds.
// 2.6 (MODEL-200): a plan mark carries its coverage; `warnings` is new.
const estateHoldSchema = z
  .object({ kind: z.enum(["provider", "plan", "device"]), id: z.string() })
  .strict();

const estateMarkSchema = z
  .object({
    via: estateHoldSchema,
    cost_basis: z.enum(["list_price", "plan_included", "owned_hardware"]),
    marginal_cost_per_task_usd: z.number().nonnegative().nullable().optional(),
    coverage: planCoverageSchema.nullable().optional(),
  })
  .strict();

export const withEstateSchema = z
  .object({
    status: decisionStatus,
    answer: answerSchema.nullable().optional(),
    results: z
      .array(
        z
          .object({
            rank: z.number().int().positive(),
            offering: offeringRefSchema,
            estate: estateMarkSchema,
            soft_penalty: z.number().nonnegative().optional().default(0),
            warnings: z.array(z.string().regex(/^[a-z0-9_]+$/)).optional().default([]),
          })
          .strict(),
      )
      .optional()
      .default([]),
    may_qualify: z.array(mayQualifySchema).optional().default([]),
    truncated: truncatedSchema.optional().default({ offerings: 0, models: 0 }),
    gap: z
      .object({
        same_answer: z.boolean(),
        unreachable_models: z.array(modelId).optional().default([]),
        summary: z.string(),
      })
      .strict(),
    gain: z
      .array(
        z
          .object({
            add: estateHoldSchema,
            status: decisionStatus,
            leader: modelId.nullable().optional(),
            answer: answerSchema.nullable().optional(),
          })
          .strict(),
      )
      .optional()
      .default([]),
    warnings: z.array(z.string().regex(/^[a-z0-9_]+$/)).optional().default([]),
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
    // MODEL-179 estate answer, present when the spec sent an `estate`.
    with_estate: withEstateSchema.nullish(),
    benchmark_exclusions: z
      .object({
        benchmarks: z.array(facetId),
        estimate_changes: z.array(
          z
            .object({
              model: modelId,
              domain: facetId,
              before: estimateSchema.nullable(),
              after: estimateSchema.nullable(),
              removed_drivers: z.array(evidenceItemSchema),
            })
            .strict(),
        ),
      })
      .strict()
      .nullish(),
    contract_version: z.enum([
      "1.1",
      "1.2",
      "1.3",
      "1.4",
      "1.5",
      "1.6",
      "1.7",
      "1.8",
      "1.9",
      "1.10",
      "1.11",
      "1.12",
      "2.0",
      "2.1",
      "2.2",
      "2.3",
      "2.4",
      "2.5",
      "2.6",
      "2.7",
      "2.8",
      "2.9",
    ]),
    decision_id: z.string().regex(/^dec_[0-9A-Za-z]{8,}$/),
    snapshot: z.string().regex(/^snap_[A-Za-z0-9:._-]+$/),
    signature_verified: z.boolean().optional().default(false),
    spec_hash: z.string().regex(/^sha256:[0-9a-f]{64}$/),
    explain: z.enum(["none", "summary", "full"]),
    status: decisionStatus,
    // Older saved decisions predate 2.1. New responses always send the block,
    // while the adapter keeps those local fixtures readable.
    answer: answerSchema.nullable().optional(),
    // 2.7 (MODEL-206): absent for a lexicographic or Pareto objective, and
    // in decisions saved before 2.7.
    bands: bandsSchema.nullish(),
    blend: z.array(blendTermSchema).optional().default([]),
    results: z.array(resultSchema),
    // Older saved decisions predate 2.5; the page then groups by model itself.
    by_model: z.array(modelRowSchema).optional().default([]),
    may_qualify: z.array(mayQualifySchema),
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
    truncated: truncatedSchema
      .optional()
      .default({ offerings: 0, models: 0 }),
    constraint_costs: z.array(
      z
        .object({
          units: z.record(z.string(), nullableString).optional().default({}),
          records: z.array(z.string()).optional().default([]),
          condition: z.string(),
          admits: z.number().int().nonnegative(),
          gain: z.record(facetId, z.number().finite()),
          refinement_gains: z
            .array(
              z
                .object({ dimension: facetId, refinement: facetId, gain: z.number().finite() })
                .strict(),
            )
            .optional(),
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
          refinement: facetId.nullish(),
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
  z.object({
    weights: z.record(
      objectiveId,
      z.union([
        z.number().positive(),
        z.object({ prefer: scalar, weight: z.number().positive() }).strict(),
      ]),
    ),
  }).strict(),
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
    exclude_benchmarks: z.array(facetId).optional(),
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
    // 2.6 (MODEL-200): how the caller will use the model, as an object or the bare kind.
    access: z
      .union([
        accessKind,
        z
          .object({
            kind: accessKind,
            harness: z.string().regex(/^[a-z0-9][a-z0-9-]*$/).nullable().optional(),
          })
          .strict(),
      ])
      .nullable()
      .optional(),
    // 2.3 (MODEL-179): what the caller holds. Sent for one decision, never stored.
    estate: z
      .object({
        providers: z.array(z.string().min(1).max(120)).max(64).optional(),
        plans: z.array(z.string().min(1).max(120)).max(64).optional(),
        devices: z.array(z.string().min(1).max(120)).max(64).optional(),
        exhausted: z.array(z.string().min(1).max(120)).max(64).optional(),
      })
      .strict()
      .nullable()
      .optional(),
  })
  .strict();

export type OfferingRef = z.infer<typeof offeringRefSchema>;
export type EvidenceItem = z.infer<typeof evidenceItemSchema>;
export type Result = z.infer<typeof resultSchema>;
export type ModelRow = z.infer<typeof modelRowSchema>;
export type Decision = z.infer<typeof decisionSchema>;
export type Bands = z.infer<typeof bandsSchema>;
export type BandEntry = z.infer<typeof bandEntrySchema>;
export type BlendTerm = z.infer<typeof blendTermSchema>;
export type DecisionSpec = z.infer<typeof decisionSpecSchema>;
export type Contribution = z.infer<typeof contributionSchema>;
export type PlanRoute = z.infer<typeof planRouteSchema>;
export type PlanCoverage = z.infer<typeof planCoverageSchema>;
export type WithEstate = z.infer<typeof withEstateSchema>;
export type EstateResult = WithEstate["results"][number];
export type EstateMark = EstateResult["estate"];
export type AccessKind = z.infer<typeof accessKind>;
export type MayQualify = z.infer<typeof mayQualifySchema>;
