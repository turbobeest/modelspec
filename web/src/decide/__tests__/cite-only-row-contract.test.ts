import { expect, it } from "vitest";
import rawDecision from "../__fixtures__/live-assistant-balanced-full.json";
import { decisionSchema } from "../adapter/contract";

const warning = "cite_only_not_machine_verified";
const offering = { model: "lab/cited", provider: null, region: null, tier: null };
const elimination = { model: offering.model, offering, condition: "too small", value: 1,
  warnings: [warning] };

it("accepts citation warnings on may-qualify, eliminated and grouped offering rows", () => {
  const result = decisionSchema.parse({
    ...rawDecision,
    may_qualify: [{ model: offering.model, offering, unknown: ["model.context_window"],
      warnings: [warning] }],
    eliminated: { ...rawDecision.eliminated, models: [elimination], model_groups: [{
      model: offering.model,
      model_elimination: elimination,
      offerings: [{ offering, condition: "too small", value: 1, warnings: [warning] }],
    }] },
    by_model: [{ model: offering.model, status: "may_qualify", rank: null, cost_per_task: null,
      offerings: [{ offering, status: "may_qualify", rank: null, cost_per_task: null,
        unknown: ["model.context_window"], reason: null, warnings: [warning] }] }],
  });
  expect(result.may_qualify[0]).toHaveProperty("warnings", [warning]);
  expect(result.eliminated.models[0]).toHaveProperty("warnings", [warning]);
  expect(result.eliminated.model_groups[0]?.model_elimination).toHaveProperty("warnings", [warning]);
  expect(result.eliminated.model_groups[0]?.offerings[0]).toHaveProperty("warnings", [warning]);
  expect(result.by_model[0]?.offerings[0]).toHaveProperty("warnings", [warning]);
});

it.each(["best", "rest", "thin"])("accepts citation warnings on %s band rows", (name) => {
  const row = { model: offering.model, offering, score: 1, score_interval: [1, 1],
    p_best: null, p_beats_leader: null, cost_per_task: null, estimates: [], warnings: [warning] };
  const result = decisionSchema.parse({
    ...rawDecision,
    bands: { basis: "test", band_probability: 0.25, thin_interval_width: 2.8,
      leader: name === "best" ? offering.model : null, best: [], rest: [], thin: [], [name]: [row] },
  });
  expect(result.bands).toHaveProperty(name, [row]);
});
