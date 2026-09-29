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

const energyFacet = {
  id: "offering.energy_per_task",
  label: "Energy per task",
  definition: "Energy used for one task.",
  subject: "offering" as const,
  value_type: "number" as const,
  unit: "watt_hours",
  unit_definition: null,
  operators: ["<=", ">="] as ("<=" | ">=")[],
  objective: true,
  preference: {
    kind: "continuous" as const,
    directions: ["max", "min"] as ["max", "min"],
    threshold: "where" as const,
  },
  risk: "capability" as const,
  computed_by: null,
  known: 3,
  of: 4,
  range: { min: 1, max: 8 },
};

const energyVocabulary: Vocabulary = {
  ...smallVocabulary,
  facets: [...smallVocabulary.facets, energyFacet],
};

function decisionWithCoordinates() {
  return decisionSchema.parse({
    ...fixtureJson,
    contract_version: "1.10",
    results: fixtureJson.results.map((result, index) => ({
      ...result,
      contributions: [
        ...result.contributions,
        {
          ...result.contributions[0],
          dimension: "offering.energy_per_task",
          raw_value: index + 1,
          unit: "watt_hours",
        },
        {
          ...result.contributions[0],
          dimension: "model.max_output_tokens",
          raw_value: 64_000 + index * 16_000,
          unit: "tokens",
        },
      ],
    })),
    top: fixtureJson.top.map((candidate, index) => ({
      ...candidate,
      facts: [
        ...candidate.facts,
        {
          facet: "offering.energy_per_task",
          value: index + 1,
          unit: "watt_hours",
          record_id: `energy-${index}`,
        },
        {
          facet: "model.max_output_tokens",
          value: 64_000 + index * 16_000,
          unit: "tokens",
          record_id: `output-${index}`,
        },
        {
          facet: "model.release_date",
          value: `2026-0${index + 1}-15`,
          unit: null,
          record_id: `release-${index}`,
        },
      ],
    })),
  });
}

function decisionWithEstimate(domain: string, omitModel?: string) {
  const coordinates = decisionWithCoordinates();
  return decisionSchema.parse({
    ...coordinates,
    results: coordinates.results.map((result, index) => ({
      ...result,
      estimates:
        result.offering.model === omitModel
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
}

it("takes every numeric and date axis from the vocabulary and explains unavailable axes", () => {
  const vocabulary: Vocabulary = {
    ...realVocabulary,
    facets: [
      ...realVocabulary.facets,
      energyFacet,
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

it("fetches and renders an arbitrary covered facet for an excluded model", async () => {
  history.replaceState(null, "", "/decide/");
  const ranking = decisionSchema.parse({
    ...fixtureJson,
    results: fixtureJson.results.filter(
      (result) => result.offering.model !== "lab/alpha",
    ),
  });
  const coordinates = decisionWithCoordinates();
  const fetch = routeFetch({
    vocabulary: () => json(energyVocabulary),
    decide: (init) => {
      const request = JSON.parse(String(init?.body)) as DecisionSpec;
      return json(
        request.explain === "full" &&
          "weights" in request.optimize &&
          Object.hasOwn(request.optimize.weights, "offering.energy_per_task")
          ? coordinates
          : ranking,
      );
    },
  });
  vi.stubGlobal("fetch", fetch);
  render(<DesignedApp />);

  const canvas = await screen.findByRole("region", { name: "Trade-off canvas" });
  fireEvent.change(within(canvas).getByLabelText("X axis"), {
    target: { value: "facet:offering.energy_per_task" },
  });

  expect(
    await within(canvas).findByRole("button", {
      name: /lab\/alpha, Excluded, Energy per task 4 watt hours/,
    }),
  ).toHaveClass("excluded");
  expect(
    sentSpecs(fetch).some(
      (request) =>
        request.where?.length === 0 &&
        request.explain === "full" &&
        "weights" in request.optimize &&
        Object.hasOwn(request.optimize.weights, "offering.energy_per_task"),
    ),
  ).toBe(true);

  const plot = canvas.querySelector<HTMLElement>(".plot");
  if (!plot) throw new Error("canvas plot is missing");
  vi.spyOn(plot, "getBoundingClientRect").mockReturnValue({
    x: 0,
    y: 0,
    left: 0,
    top: 0,
    right: 100,
    bottom: 100,
    width: 100,
    height: 100,
    toJSON: () => ({}),
  });
  const xHandle = within(canvas).getByRole("slider", {
    name: "Energy per task Must threshold",
  });
  const yHandle = within(canvas).getByRole("slider", {
    name: "Maximum output tokens Must threshold",
  });
  xHandle.setPointerCapture = vi.fn();
  yHandle.setPointerCapture = vi.fn();
  fireEvent.pointerDown(xHandle, { pointerId: 1, clientX: 20 });
  fireEvent.pointerMove(plot, { pointerId: 1, clientX: 30 });
  fireEvent.pointerUp(plot, { pointerId: 1 });
  fireEvent.pointerDown(yHandle, { pointerId: 2, clientY: 80 });
  fireEvent.pointerMove(plot, { pointerId: 2, clientY: 70 });
  fireEvent.pointerUp(plot, { pointerId: 2 });

  await waitFor(() => {
    const requests = sentSpecs(fetch);
    expect(
      requests.some((request) =>
        request.where?.some((condition: string) =>
          condition.startsWith("offering.energy_per_task >= "),
        ),
      ),
    ).toBe(true);
    expect(
      requests.some((request) =>
        request.where?.some((condition: string) =>
          condition.startsWith("model.max_output_tokens >= "),
        ),
      ),
    ).toBe(true);
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
  const ranking = decisionWithEstimate("software_engineering");
  const plot = decisionWithEstimate("maths", "lab/alpha");
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
  const nearMiss = decision.explanation.rows[2];
  decision.nearMisses = [
    {
      row: nearMiss,
      ci: 0,
      cond: { f: "ctx", min: 300_000 },
      why: "Context window is below the Must floor",
      relaxed: null,
      off: nearMiss.best,
    },
  ];
  decision.explanation.rows[0].status = -1;
  decision.explanation.rows[1].status = 0;

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
  expect(canvas.querySelector(".point.may")).not.toBeNull();
  expect(within(canvas).getByText("Fails a Must · remains visible")).toBeInTheDocument();
  expect(within(canvas).getByText("May qualify · missing Must data")).toBeInTheDocument();
  expect(within(canvas).getByText("Gamma Max 0902 · near miss")).toHaveClass(
    "point-label",
  );
  expect(within(canvas).getByText(/Not plotted: no data/)).toHaveTextContent("lab/alpha");
  fireEvent.keyDown(within(canvas).getByRole("slider", { name: "Software engineering capability Must threshold" }), {
    key: "ArrowRight",
  });
  expect(onMust).toHaveBeenCalledWith(
    expect.objectContaining({ id: "capability:software_engineering", mustOp: ">=" }),
    expect.any(Number),
  );
});

it("renders a date against a capability without optimizing the date", () => {
  const options = canvasAxisOptions(smallVocabulary);
  const release = options.find((option) => option.id === "facet:model.release_date");
  const capability = options.find(
    (option) => option.id === "capability:software_engineering",
  );
  const fallback = options.find(
    (option) => option.id === "facet:model.context_window",
  );
  if (!release || !capability || !fallback)
    throw new Error("fixture is missing the date/capability axes");

  const request = canvasPlotSpec(
    {
      spec_version: 1,
      optimize: { min: "offering.price.input" },
      explain: "summary",
    },
    release,
    capability,
    fallback,
  );
  expect(request.optimize).toEqual({ weights: { software_engineering: 1 } });
  expect(request.explain).toBe("full");

  const ranking = decisionWithEstimate("software_engineering");
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
  render(
    <FreeAxisCanvas
      decision={decision}
      rankingDecision={ranking}
      plotDecision={ranking}
      vocabulary={smallVocabulary}
      axes={{
        x: "facet:model.release_date",
        y: "capability:software_engineering",
      }}
      onAxes={vi.fn()}
      onMust={vi.fn()}
      selections={{}}
      selected={null}
      onSelect={vi.fn()}
      compact={false}
    />,
  );

  const canvas = screen.getByRole("region", { name: "Trade-off canvas" });
  expect(
    within(canvas).getByRole("button", {
      name: /Delta 4.7, Qualifies, Release date 2026-01-15, Software engineering capability 40 capability score/,
    }),
  ).toBeInTheDocument();
  expect(canvas.querySelectorAll(".axis-interval.y")).toHaveLength(4);
  expect(canvas.querySelectorAll(".point-label").length).toBeGreaterThan(0);
  expect(within(canvas).getByText("Delta 4.7")).toHaveClass("point-label");
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
    explain: "full",
    limit: 500,
  });
});
