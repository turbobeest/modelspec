import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, expect, it, vi } from "vitest";
import fixtureJson from "../__fixtures__/full-decision.json";
import { decisionSchema } from "../adapter";
import type { DecisionSpec, Spec } from "../adapter";
import { mapDecisionToViewModel } from "../adapter/view-model";
import { FreeAxisCanvas } from "../components/FreeAxisCanvas";
import {
  capabilityPlotSpec,
  canvasAxisOptions,
  canvasPlotSpec,
} from "../components/canvas-axis";
import { baseSpec } from "../state/spec";
import { DesignedApp } from "../App";
import { decodeBoardState } from "../facet-board/model";
import type { Vocabulary } from "../vocabulary";
import {
  json,
  realVocabulary,
  routeFetch,
  sentSpecs,
  smallVocabulary,
} from "./vocab-fixtures";

afterEach(() => vi.unstubAllGlobals());

it("takes every numeric and date axis from the vocabulary and explains unavailable axes", () => {
  const vocabulary: Vocabulary = {
    ...realVocabulary,
    facets: [
      ...realVocabulary.facets,
      {
        id: "offering.energy_per_task",
        label: "Energy per task",
        definition: "Energy used for one task.",
        subject: "offering",
        value_type: "number",
        unit: "watt_hours",
        unit_definition: null,
        operators: ["<=", ">="],
        objective: true,
        risk: "capability",
        computed_by: null,
        known: 3,
        of: 4,
        range: { min: 1, max: 8 },
      },
    ],
  };

  const options = canvasAxisOptions(vocabulary);

  expect(options.map((option) => option.id)).toContain("facet:offering.energy_per_task");
  expect(options.map((option) => option.id)).toContain("facet:model.release_date");
  expect(options.map((option) => option.id)).toContain("capability:software_engineering");
  expect(options.find((option) => option.id === "facet:model.parameters_total")).toMatchObject({
    disabled: true,
    disabledReason: "No models have a recorded value in this snapshot",
  });
});

it("sends a separate preferred-capability request without changing the board ranking request", async () => {
  history.replaceState(null, "", "/decide/");
  const fetch = routeFetch({ decide: () => json(fixtureJson) });
  vi.stubGlobal("fetch", fetch);
  render(<DesignedApp />);

  const canvas = await screen.findByRole(
    "region",
    { name: "Trade-off canvas" },
    { timeout: 5_000 },
  );
  const rankingRequest = sentSpecs(fetch).find(
    (request) =>
      "weights" in request.optimize &&
      Object.hasOwn(request.optimize.weights, "-offering.cost_per_task"),
  );
  expect(rankingRequest).toBeDefined();
  fireEvent.change(within(canvas).getByLabelText("Y axis"), {
    target: { value: "capability:software_engineering" },
  });

  await waitFor(() => {
    expect(
      sentSpecs(fetch).some(
        (request) =>
          request.capabilities?.software_engineering === "preferred" &&
          request.where?.length === 0 &&
          "weights" in request.optimize &&
          Object.hasOwn(request.optimize.weights, "software_engineering"),
      ),
    ).toBe(true);
  });
  expect(sentSpecs(fetch)).toContainEqual(rankingRequest);

  fireEvent.keyDown(
    screen.getByRole("slider", {
      name: "Software engineering capability Must threshold",
    }),
    { key: "ArrowUp" },
  );
  await waitFor(() =>
    expect(
      sentSpecs(fetch).some((request) =>
        request.where?.some((condition: string) =>
          condition.startsWith("software_engineering >= "),
        ),
      ),
    ).toBe(true),
  );
  expect(decodeBoardState(location.hash)?.canvas?.y).toBe(
    "capability:software_engineering",
  );
  fireEvent.click(screen.getByRole("button", { name: "Share or act" }));
  const share = screen.getByRole("dialog", { name: "Share or act on this decision" });
  fireEvent.click(within(share).getByRole("tab", { name: "Spec YAML" }));
  expect(within(share).getByRole("tabpanel", { name: "Spec YAML" })).toHaveTextContent(
    "# canvas y: capability:software_engineering",
  );
});

it("draws capability intervals on either axis and leaves no-data models at the margin", () => {
  const maths = realVocabulary.domains.find((domain) => domain.id === "maths");
  if (!maths) throw new Error("fixture has no maths domain");
  const vocabulary: Vocabulary = {
    ...smallVocabulary,
    domains: [...smallVocabulary.domains, maths],
  };
  const withEstimate = (domain: string, omitLast = false) =>
    decisionSchema.parse({
      ...fixtureJson,
      contract_version: "1.10",
      results: fixtureJson.results.map((result, index) => ({
        ...result,
        estimates:
          omitLast && result.offering.model === "lab/alpha"
            ? []
            : [
                {
                  domain,
                  value: 40 + index * 10,
                  interval: [35 + index * 10, 47 + index * 10],
                  harness: null,
                  effort: null,
                },
              ],
      })),
    });
  const ranking = withEstimate("software_engineering");
  const plot = withEstimate("maths", true);
  const spec: Spec = {
    ...baseSpec,
    bench: "quality",
    domain: "software_engineering",
    basis: "estimate",
    boardWeights: { software_engineering: 1 },
  };
  const decision = mapDecisionToViewModel(ranking, spec, {
    axis: "task$",
    dismissed: [],
    benchmarks: {
      quality: { unit: "%", pct: true, d: 2, hi: true, types: [] },
    },
    models: smallVocabulary.models,
    providers: smallVocabulary.providers,
  });
  decision.explanation.rows[0].status = -1;

  const onMust = vi.fn();
  render(
    <FreeAxisCanvas
      decision={decision}
      rankingDecision={ranking}
      plotDecision={plot}
      vocabulary={vocabulary}
      axes={{
        x: "capability:software_engineering",
        y: "capability:maths",
      }}
      onAxes={vi.fn()}
      onMust={onMust}
      selections={{}}
      selected={null}
      onSelect={vi.fn()}
      compact={false}
    />,
  );

  const canvas = screen.getByRole("region", { name: "Trade-off canvas" });
  expect(canvas.querySelectorAll(".axis-interval.x")).toHaveLength(3);
  expect(canvas.querySelectorAll(".axis-interval.y")).toHaveLength(3);
  expect(canvas.querySelector(".point.excluded")).not.toBeNull();
  expect(within(canvas).getByText("Fails a Must · remains visible")).toBeInTheDocument();
  expect(within(canvas).getByText(/Not plotted: no data/)).toHaveTextContent("lab/alpha");
  fireEvent.keyDown(within(canvas).getByRole("slider", { name: "Software engineering capability Must threshold" }), {
    key: "ArrowRight",
  });
  expect(onMust).toHaveBeenCalledWith(
    expect.objectContaining({ id: "capability:software_engineering", mustOp: ">=" }),
    expect.any(Number),
  );
});

it("asks for an unranked y-domain as preferred without changing the ranking spec", () => {
  const ranking: DecisionSpec = {
    spec_version: 1,
    capabilities: { software_engineering: "required" },
    where: ["model.class = text-generator"],
    optimize: { weights: { software_engineering: 0.7, "-offering.cost_per_task": 0.3 } },
    explain: "full",
  };

  const plot = capabilityPlotSpec(ranking, "maths");

  expect(ranking.capabilities).toEqual({ software_engineering: "required" });
  expect(plot).toMatchObject({
    capabilities: { software_engineering: "required", maths: "preferred" },
    where: ranking.where,
    optimize: ranking.optimize,
  });
  expect(capabilityPlotSpec(ranking, "software_engineering")).toBeNull();

  const options = canvasAxisOptions(realVocabulary);
  const price = options.find((option) => option.id === "facet:offering.price.output");
  const maths = options.find((option) => option.id === "capability:maths");
  if (!price || !maths) throw new Error("fixture is missing canvas axes");
  expect(canvasPlotSpec(ranking, price, maths)).toMatchObject({
    capabilities: { maths: "preferred" },
    where: [],
    optimize: {
      weights: { "-offering.price.output": 0.5, maths: 0.5 },
    },
    explain: "summary",
    limit: 500,
  });
});
