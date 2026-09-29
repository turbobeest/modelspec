import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import fixtureJson from "../__fixtures__/full-decision.json";
import liveBudgetCodingJson from "../__fixtures__/live-budget-coding-full.json";
import liveEmptyBoardJson from "../__fixtures__/live-empty-board-full.json";
import liveSwePreferJson from "../__fixtures__/live-swe-prefer-full.json";
import refinementVocabularyJson from "../__fixtures__/vocabulary-refinements.json";
import App, { DesignedApp } from "../App";
import { decisionSchema } from "../adapter";
import {
  json,
  realVocabulary,
  routeFetch,
  sentSpecs,
  rankingCalls,
  rankingSpecs,
  smallVocabulary,
} from "./vocab-fixtures";
import { VOCABULARY_URL, realBaseSpec, vocabularySchema } from "../vocabulary";
import { decodeBoardState, encodeBoardSpec } from "../facet-board/model";
import { LEGACY_PERMALINKS } from "../__fixtures__/legacy-permalinks";

const fixture = decisionSchema.parse(fixtureJson);
const liveBudgetCoding = decisionSchema.parse(liveBudgetCodingJson);
const liveEmptyBoard = decisionSchema.parse(liveEmptyBoardJson);
const liveSwePrefer = decisionSchema.parse(liveSwePreferJson);
const refinementVocabulary = vocabularySchema.parse(refinementVocabularyJson);

it("sanitizes every unavailable selection in an old namespaced board permalink", async () => {
  const unavailableFacet = refinementVocabulary.facets.find((facet) => facet.id === "model.context_window")!;
  const vocabulary = {
    ...refinementVocabulary,
    facets: refinementVocabulary.facets.map((facet) =>
      facet.id === unavailableFacet.id ? { ...facet, known: 0 } : facet,
    ),
    refinements: refinementVocabulary.refinements?.filter((row) => row.id !== "python"),
  };
  const base = { ...realBaseSpec(vocabulary), domain: "retired_domain", conds: [] };
  const permalink = encodeBoardSpec(base, "task$", {
    selections: {
      [unavailableFacet.id]: { mode: "must", op: ">=", value: 200000 },
      "capability.retired_domain": { mode: "prefer", weight: 0.7 },
      "refinement.python": { mode: "prefer", weight: 0.3, weightKey: "software_engineering.python" },
    },
    mustOrder: [unavailableFacet.id],
    estate: { providers: [], plans: [], hardware: [] },
  });
  const fetch = routeFetch({
    vocabulary: () => json(vocabulary),
    decide: (init) => json(decisionFor(init)),
  });
  vi.stubGlobal("fetch", fetch);
  history.replaceState(null, "", `/decide/${permalink}`);

  render(<App />);

  const note = await screen.findByRole("note", { name: "Notes from your old decision link" });
  expect(note).toHaveTextContent(unavailableFacet.label);
  expect(note).toHaveTextContent("retired domain capability");
  expect(note).toHaveTextContent("python refinement");
  expect(note).not.toHaveTextContent("capability.retired_domain");
  expect(note).not.toHaveTextContent("refinement.python");
  await waitFor(() => expect(sentSpecs(fetch).length).toBeGreaterThan(0));
  const request = sentSpecs(fetch).at(-1)!;
  expect(request.where).not.toContain("model.context_window >= 200000");
  expect(request.optimize.weights).not.toHaveProperty("retired_domain");
  expect(request.optimize.weights).not.toHaveProperty("software_engineering.python");
  expect(request.capabilities?.retired_domain).toBeUndefined();
});

it("opens a composer-era permalink as a populated board with migration notes", async () => {
  vi.stubGlobal("fetch", routeFetch({ decide: (init) => json(decisionFor(init)) }));
  history.replaceState(null, "", `/decide/?theme=dark&layout=table${LEGACY_PERMALINKS.budgetCoding}`);
  render(<App />);
  await screen.findByRole("heading", { name: "Set what matters. Watch the field narrow." });
  expect(screen.queryByLabelText("Describe your task")).not.toBeInTheDocument();
  expect(screen.getByRole("button", { name: "Table first" })).toHaveAttribute("aria-pressed", "true");
  expect(screen.getByRole("button", { name: "Light mode" })).toBeInTheDocument();
  expect(await screen.findByRole("note", { name: "Notes from your old decision link" })).toHaveTextContent(
    "The board does not interpret free text.",
  );
  fireEvent.click(screen.getByRole("button", { name: /^Size of work/ }));
  const context = document.querySelector<HTMLElement>('[data-facet="model.context_window"]');
  if (!context) throw new Error("legacy context facet did not render");
  expect(within(context).getByLabelText("Must")).toBeChecked();
  expect(within(context).getByLabelText("Threshold")).toHaveValue(200000);
});

it("applies visible legacy controls and drops the unsupported parts named in the migration note", async () => {
  const fetch = routeFetch({ decide: (init) => json(decisionFor(init)) });
  vi.stubGlobal("fetch", fetch);
  history.replaceState(null, "", `/decide/${LEGACY_PERMALINKS.unsupportedParts}`);

  render(<App />);

  const note = await screen.findByRole("note", { name: "Notes from your old decision link" });
  expect(note).toHaveTextContent("single-benchmark floor, so it's not applied");
  expect(note).toHaveTextContent("soft(0.2)");
  await waitFor(() => expect(rankingSpecs(fetch).length).toBeGreaterThan(0));
  const request = rankingSpecs(fetch).at(-1)!;
  expect(request.where).toContain("offering.region in {EU}");
  expect(request.where).not.toContain("swe_bench_pro >= 50 @independent");
  expect(request.where.every((condition: string) => !condition.includes("soft("))).toBe(true);
});

it("migrates a composer-era permalink navigated to after vocabulary loads", async () => {
  const fetch = routeFetch({ decide: (init) => json(decisionFor(init)) });
  vi.stubGlobal("fetch", fetch);
  render(<App />);
  await screen.findByRole("heading", { name: "Set what matters. Watch the field narrow." });
  const requestsBeforeNavigation = sentSpecs(fetch).length;

  history.pushState(null, "", `/decide/${LEGACY_PERMALINKS.unsupportedParts}`);
  window.dispatchEvent(new HashChangeEvent("hashchange"));

  const note = await screen.findByRole("note", { name: "Notes from your old decision link" });
  expect(note).toHaveTextContent("single-benchmark floor, so it's not applied");
  expect(note).toHaveTextContent("soft(0.2)");
  await waitFor(() => {
    const navigatedRequests = sentSpecs(fetch).slice(requestsBeforeNavigation);
    expect(navigatedRequests.some((request) => request.where.includes("offering.region in {EU}"))).toBe(true);
    expect(navigatedRequests.every((request) => !request.where.includes("swe_bench_pro >= 50 @independent"))).toBe(true);
    expect(navigatedRequests.every((request) => request.where.every((condition: string) => !condition.includes("soft(")))).toBe(true);
  });
});

/** Keep the legacy full fixture consistent with the objective a UI test sends. */
function decisionFor(init: RequestInit | undefined, decision = fixture) {
  const sent = JSON.parse(String(init?.body ?? "{}"));
  const weights = sent.optimize?.weights ?? {};
  const domain = smallVocabulary.domains.find((row) => row.id in weights)?.id;
  if (!domain) return decision;
  return {
    ...decision,
    results: decision.results.map((result, index) => {
      const value = 2 - index * 0.2;
      const driver = {
        ...result.evidence[0].items[0],
        requested_domain: domain,
        loading: 1,
        estimate_weight: 1,
        recency_weight: 1,
      };
      return {
        ...result,
        estimates: [{ domain, value, interval: [value - 0.4, value + 0.4], harness: null, effort: null }],
        p_best: index === 0 ? 0.5 : 0.1,
        top3_stability: index < 3 ? 0.8 : 0.2,
        contributions: [
          ...result.contributions,
          {
            raw_value: value,
            unit: "capability_score",
            records: [driver.record_id],
            dimension: domain,
            weight: weights[domain],
            value: 1 - index * 0.2,
            normalisation: "feasible min-max; max",
            evidence: [driver],
            formula: "monotone domain evidence estimate",
          },
        ],
      };
    }),
  };
}

beforeEach(() => history.replaceState(null, "", "/decide/"));
afterEach(() => vi.unstubAllGlobals());

it("folds invalid refinement weights into the parent without losing board state", async () => {
  let unsupportedRequests = 0;
  const fetch = routeFetch({
    vocabulary: () => json(refinementVocabulary),
    decide: (init) => {
      const sent = JSON.parse(String(init?.body));
      if ("software_engineering/python" in sent.optimize.weights) {
        unsupportedRequests += 1;
        return json({ error: { code: "invalid_spec", message: "Refinement weights are not rankable yet.", issues: [] } }, 400);
      }
      return json(decisionFor(init));
    },
  });
  vi.stubGlobal("fetch", fetch);
  const app = render(<DesignedApp />);
  await screen.findByLabelText("Facet board answer");
  const software = screen.getByText("Software engineering").closest<HTMLElement>(".facet-row")!;
  fireEvent.click(within(software).getByLabelText("Prefer"));
  fireEvent.click(within(software).getByRole("button", { name: "Refine" }));
  const python = within(software).getByText("Python").closest<HTMLElement>(".refinement-row")!;
  fireEvent.click(within(python).getByLabelText("Prefer"));

  fireEvent.change(screen.getByLabelText("Add provider"), {
    target: { value: Object.keys(refinementVocabulary.providers)[0] },
  });
  fireEvent.click(screen.getByRole("button", { name: "Share or act" }));
  const beforeFallbackShare = screen.getByRole("dialog");
  const beforeFallbackPermalink = within(beforeFallbackShare)
    .getByRole("tabpanel", { name: "Permalink" }).querySelector("pre")?.textContent;
  expect(decodeBoardState(new URL(beforeFallbackPermalink!).hash)?.selections["refinement.python"])
    .toEqual({ mode: "prefer", weight: 0.25 });
  fireEvent.click(within(beforeFallbackShare).getByRole("button", { name: "Close Share or act" }));

  expect(await within(python).findByText("Ranked by general software engineering: Python isn't ranked separately today.")).toBeInTheDocument();
  await waitFor(() => expect(screen.queryByText("Checking…")).not.toBeInTheDocument());
  const requests = sentSpecs(fetch);
  expect(requests.some((body) => body.optimize.weights["software_engineering/python"] > 0)).toBe(true);
  expect(requests.some((body) => body.optimize.weights.software_engineering === 0.5 && !("software_engineering/python" in body.optimize.weights))).toBe(true);
  expect(unsupportedRequests).toBe(1);
  expect(requests.filter((body) => body.where.some((condition: string) =>
    condition.startsWith("offering.provider in"),
  ))).toEqual([expect.objectContaining({
    optimize: { weights: { software_engineering: 0.5 } },
  })]);
  expect(within(python).getByLabelText("Prefer")).toBeChecked();
  fireEvent.click(screen.getByRole("button", { name: "Share or act" }));
  const share = screen.getByRole("dialog");
  const permalink = within(share).getByRole("tabpanel", { name: "Permalink" }).querySelector("pre")?.textContent;
  expect(permalink).toContain("#s=");
  expect(permalink).toContain(location.origin + location.pathname);
  expect(permalink).toBe(beforeFallbackPermalink);
  fireEvent.click(within(share).getByRole("tab", { name: "Spec YAML" }));
  expect(share).toHaveTextContent("refinement weights folded into their parent domains");
  expect(share).toHaveTextContent('optimize: {"weights":{"software_engineering":0.5}}');

  app.unmount();
  const shared = new URL(permalink!);
  history.replaceState(null, "", shared.pathname + shared.search + shared.hash);
  render(<DesignedApp />);
  await screen.findByLabelText("Facet board answer");
  const restoredSoftware = screen.getByText("Software engineering").closest<HTMLElement>(".facet-row")!;
  fireEvent.click(within(restoredSoftware).getByRole("button", { name: "Refine" }));
  const restoredPython = within(restoredSoftware).getByText("Python").closest<HTMLElement>(".refinement-row")!;
  expect(within(restoredPython).getByLabelText("Prefer")).toBeChecked();
});

it("does not retry an invalid spec that carried no refinement weights", async () => {
  let decisionRequests = 0;
  const fetch = routeFetch({
    vocabulary: () => json(refinementVocabulary),
    decide: () => {
      decisionRequests += 1;
      return json({ error: { code: "invalid_spec", message: "Invalid plain spec.", issues: [] } }, 400);
    },
  });
  vi.stubGlobal("fetch", fetch);
  render(<DesignedApp />);

  expect(await screen.findByText("Decision unavailable (invalid_spec).")).toBeInTheDocument();
  expect(decisionRequests).toBe(1);
});

it("does not retry the legacy refinement code on a spec that carried no refinement weights", async () => {
  let decisionRequests = 0;
  const fetch = routeFetch({
    vocabulary: () => json(refinementVocabulary),
    decide: () => {
      decisionRequests += 1;
      return json({ error: { code: "refinement_not_rankable_yet", message: "Refinements are not ranked yet.", issues: [] } }, 400);
    },
  });
  vi.stubGlobal("fetch", fetch);
  render(<DesignedApp />);

  expect(await screen.findByText("Decision unavailable (refinement_not_rankable_yet).")).toBeInTheDocument();
  expect(decisionRequests).toBe(1);
});

it("tries the refinement fold-back only once", async () => {
  let rejectedRefinement = false;
  const fetch = routeFetch({
    vocabulary: () => json(refinementVocabulary),
    decide: (init) => {
      const sent = JSON.parse(String(init?.body));
      if ("software_engineering/python" in sent.optimize.weights) rejectedRefinement = true;
      if (rejectedRefinement)
        return json({ error: { code: "invalid_spec", message: "Still invalid after folding.", issues: [] } }, 400);
      return json(decisionFor(init));
    },
  });
  vi.stubGlobal("fetch", fetch);
  render(<DesignedApp />);
  await screen.findByLabelText("Facet board answer");
  const software = screen.getByText("Software engineering").closest<HTMLElement>(".facet-row")!;
  fireEvent.click(within(software).getByLabelText("Prefer"));
  fireEvent.click(within(software).getByRole("button", { name: "Refine" }));
  const callsBeforeRefinement = sentSpecs(fetch).length;
  const python = within(software).getByText("Python").closest<HTMLElement>(".refinement-row")!;
  fireEvent.click(within(python).getByLabelText("Prefer"));

  expect(await screen.findByText("Decision unavailable (invalid_spec).")).toBeInTheDocument();
  const attempts = sentSpecs(fetch).slice(callsBeforeRefinement)
    .filter((body) => body.explain === "summary");
  expect(attempts).toHaveLength(2);
  expect(attempts[0].optimize.weights).toHaveProperty("software_engineering/python");
  expect(attempts[1].optimize.weights).not.toHaveProperty("software_engineering/python");
});

it("lets a newer board request win when an in-flight folded retry is aborted", async () => {
  let fallbackStarted: (() => void) | undefined;
  const fallbackInFlight = new Promise<void>((resolve) => { fallbackStarted = resolve; });
  let rejectedRefinement = false;
  const fetch = routeFetch({
    vocabulary: () => json(refinementVocabulary),
    decide: (init) => {
      const sent = JSON.parse(String(init?.body));
      if ("software_engineering/python" in sent.optimize.weights) {
        rejectedRefinement = true;
        return json({ error: { code: "invalid_spec", message: "Refinement weights are not rankable yet.", issues: [] } }, 400);
      }
      if (rejectedRefinement && sent.optimize.weights.software_engineering === 0.5) {
        fallbackStarted?.();
        return new Promise<Response>((_resolve, reject) => {
          init?.signal?.addEventListener("abort", () => reject(new DOMException("Aborted", "AbortError")), { once: true });
        });
      }
      return json(decisionFor(init));
    },
  });
  vi.stubGlobal("fetch", fetch);
  render(<DesignedApp />);
  await screen.findByLabelText("Facet board answer");
  const software = screen.getByText("Software engineering").closest<HTMLElement>(".facet-row")!;
  fireEvent.click(within(software).getByLabelText("Prefer"));
  fireEvent.click(within(software).getByRole("button", { name: "Refine" }));
  const python = within(software).getByText("Python").closest<HTMLElement>(".refinement-row")!;
  fireEvent.click(within(python).getByLabelText("Prefer"));
  await fallbackInFlight;

  fireEvent.change(within(software).getByLabelText("Weight for Software engineering"), {
    target: { value: "0.6" },
  });

  await waitFor(() => expect(screen.getByLabelText("Facet board answer")).toBeInTheDocument());
  expect(screen.queryByText("The decision service could not be reached.")).not.toBeInTheDocument();
  await waitFor(() => expect(sentSpecs(fetch).some((body) =>
    body.optimize.weights.software_engineering === 0.6,
  )).toBe(true));
});

it("runs the designed App on a full hosted decision without fictional labels", async () => {
  const fetch = routeFetch({
    decide: (init) => {
      const spec = JSON.parse(String(init?.body));
      const decision = decisionFor(init);
      return json(
        spec.explain === "none"
          ? { ...decision, explain: "none", results: decision.results.slice(0, 2) }
          : decision,
      );
    },
  });
  vi.stubGlobal("fetch", fetch);
  render(<App />);

  await screen.findByText("Coding agent on a budget");
  fireEvent.click(screen.getByText("Coding agent on a budget"));
  expect(
    await screen.findByRole("region", { name: "Trade-off canvas" }),
  ).toBeInTheDocument();
  const why = screen.getByRole("region", { name: "Why this model" });
  // Names come from the cards in the vocabulary, never from the slug.
  expect(why).toHaveTextContent("Delta 4.7");
  expect(why).toHaveTextContent("Lab Inc.");
  expect(screen.getByRole("region", { name: "Trade-off canvas" })).toHaveTextContent(
    "Beta-5.2",
  );
  expect(document.body).toHaveTextContent("lab/alpha");
  expect(document.body).not.toHaveTextContent(/Gamma Max 902|\bAlpha\b/);
  expect(screen.queryByText(/fictional/i)).not.toBeInTheDocument();

  await waitFor(() => expect(rankingSpecs(fetch).filter((body) => body.explain === "full").length).toBeGreaterThan(1));
  const sent = rankingSpecs(fetch).filter((body) => body.explain === "full").at(-1);
  if (!sent) throw new Error("template decision did not send a full request");
  expect(sent).not.toHaveProperty("task");
  expect(sent.where).toContain("model.class = text-generator");
  expect(sent.where).toContain("model.context_window >= 200000");
  // The learned domain estimate is the default; benchmark floors are explicit only.
  expect(sent.where.some((condition: string) => condition.startsWith("quality >="))).toBe(false);
  expect(sent.capabilities).toEqual({ software_engineering: "required" });
  expect(sent.task_tokens).toEqual({ input: 40000, output: 4000 });
  expect(Object.keys(sent.optimize.weights).sort()).toEqual([
    "-offering.cost_per_task",
    "software_engineering",
  ]);
  expect(sent.explain).toBe("full");

  fireEvent.click(screen.getByRole("button", { name: "Share or act" }));
  const dialog = screen.getByRole("dialog");
  fireEvent.click(within(dialog).getByRole("tab", { name: "API call" }));
  expect(dialog).toHaveTextContent("https://api.modelspec.dev/v1/decide");
  expect(dialog).not.toHaveTextContent(/fictional/i);
  expect(dialog).not.toHaveTextContent('"task"');
  fireEvent.click(within(dialog).getByRole("tab", { name: "CLI" }));
  expect(dialog).toHaveTextContent(
    "pipx install modelspec-dev modelspec snapshot fetch modelspec decide spec.yaml --explain full --json",
  );
});

it("keeps ticket IDs and future promises out of every applied template surface", async () => {
  const allTemplatesVocabulary = {
    ...realVocabulary,
    templates: realVocabulary.templates?.map((template) => ({
      ...template,
      available: true,
      unavailable_reason: null,
    })),
  };
  const fetch = routeFetch({
    vocabulary: () => json(allTemplatesVocabulary),
    decide: (init) => json(decisionFor(init)),
  });
  vi.stubGlobal("fetch", fetch);
  render(<App />);
  await screen.findByText("Coding agent on a budget");

  for (const template of allTemplatesVocabulary.templates ?? []) {
    fireEvent.click(screen.getByRole("button", { name: new RegExp(template.name) }));
    const canvas = await screen.findByRole("region", { name: "Trade-off canvas" });
    const point = canvas.querySelector<HTMLButtonElement>(".point");
    if (point) {
      fireEvent.pointerEnter(point);
      expect(within(canvas).getByRole("tooltip")).not.toHaveTextContent(/MODEL-\d+|\bcoming\b/i);
      fireEvent.click(point);
    }
    expect(screen.getByRole("region", { name: "Why this model" })).not.toHaveTextContent(/MODEL-\d+|\bcoming\b/i);
    expect(screen.getByLabelText("Facet board answer").closest(".board-answer")).not.toHaveTextContent(/MODEL-\d+|\bcoming\b/i);
    expect(document.querySelector(".facet-board")).not.toHaveTextContent(/MODEL-\d+|\bcoming\b/i);
    fireEvent.click(screen.getByRole("button", { name: "ⓘ Templates" }));
  }
});

function plotCostAgainstCapability(canvas: HTMLElement) {
  fireEvent.change(within(canvas).getByLabelText("X axis"), {
    target: { value: "facet:offering.cost_per_task" },
  });
  fireEvent.change(within(canvas).getByLabelText("Y axis"), {
    target: { value: "capability:software_engineering" },
  });
}

it("does not render the Next-questions panel in the facet-board preview", async () => {
  const fetch = routeFetch({ decide: (init) => {
    const decision = decisionFor(init);
    return json({
      ...decision,
      contract_version: "1.6",
      eliminated: {
        ...decision.eliminated,
        funnel: decision.eliminated.funnel.map((step) => ({
          ...step,
          models_before: step.before,
          models_after: step.after,
          offerings_before: step.before,
          offerings_after: step.after,
          models_may_qualify: step.may_qualify,
          offerings_may_qualify: step.may_qualify,
        })),
        model_groups: [],
      },
    });
  } });
  vi.stubGlobal("fetch", fetch);
  render(<DesignedApp />);
  await screen.findByRole("region", { name: "Trade-off canvas" });
  expect(screen.queryByText("Next questions, most narrowing first")).not.toBeInTheDocument();
  expect(screen.getByText("Narrowing, in the order you set conditions")).toBeInTheDocument();
  const narrowing = screen.getByText("Narrowing, in the order you set conditions").closest<HTMLElement>(".narrowing")!;
  const engineStep = within(narrowing).getByText("Added by the engine: Has a provider");
  expect(engineStep).toHaveAttribute("title", "This condition was added by the decision engine.");
  expect(engineStep.closest("li")).toHaveTextContent("−4");
  expect(screen.queryByRole("button", { name: "Run decision" })).not.toBeInTheDocument();
  const answer = screen.getByLabelText("Facet board answer").closest<HTMLElement>(".board-answer")!;
  expect(within(answer).queryByText(/Best overall|Best value|#1 of/)).not.toBeInTheDocument();
  expect(within(answer).getByText("Delta 4.7")).toBeInTheDocument();
  expect(within(answer).getAllByText("Lab Inc. · via cloud").length).toBeGreaterThan(0);
  expect(within(answer).queryByText("cloud/lab/delta/global/standard · cloud")).not.toBeInTheDocument();
  expect(within(answer).queryByLabelText("Delta 4.7 capability interval")).not.toBeInTheDocument();
  expect(within(answer).getByText(/qualify — set a Prefer to rank them/)).toBeInTheDocument();
  expect(screen.getByLabelText("Why this model")).toHaveTextContent("Select a model to inspect");
  const canvas = screen.getByRole("region", { name: "Trade-off canvas" });
  plotCostAgainstCapability(canvas);
  await waitFor(() => expect(canvas.querySelector(".point")).not.toBeNull());
  const point = canvas.querySelector<HTMLButtonElement>(".point");
  if (!point) throw new Error("unranked canvas did not render a model point");
  fireEvent.pointerEnter(point);
  expect(within(canvas).getByRole("tooltip")).not.toHaveTextContent(/#\d/);
  fireEvent.pointerLeave(point);
  fireEvent.focus(point);
  expect(within(canvas).getByRole("tooltip")).not.toHaveTextContent(/#\d/);
  fireEvent.click(point);
  const why = screen.getByRole("region", { name: "Why this model" });
  expect(why).not.toHaveTextContent(/#\d/);
  expect(within(why).queryByText("Tipping point")).not.toBeInTheDocument();
  const whyNot = within(why).getByLabelText("Why not");
  const comparison = within(whyNot).getAllByRole("option").find((option) => option.getAttribute("value"));
  if (!comparison) throw new Error("Why not has no model option");
  fireEvent.change(whyNot, { target: { value: comparison.getAttribute("value") } });
  expect(why).not.toHaveTextContent(/#\d/);
  const modelNames = within(answer).getAllByRole("listitem").map((item) =>
    item.querySelector("strong")?.textContent ?? "",
  );
  expect(modelNames).toEqual([...modelNames].sort((left, right) => left.localeCompare(right)));
  expect(within(narrowing).getByText("Qualifying models")).toBeInTheDocument();
  expect(within(narrowing).queryByText(/Ranking on/)).not.toBeInTheDocument();
  expect(sentSpecs(fetch).every((body) => body.where.length === 0)).toBe(true);
  expect(sentSpecs(fetch).every((body) => Object.keys(body.optimize.weights).length > 0)).toBe(true);

  fireEvent.click(screen.getByRole("button", { name: "Share or act" }));
  const share = screen.getByRole("dialog");
  fireEvent.click(within(share).getByRole("tab", { name: "Spec YAML" }));
  expect(share).toHaveTextContent("# unranked: no Prefer set");
  // The shared spec keeps the objective so it runs as-is; the comment says it does not rank.
  expect(share).toHaveTextContent("it does not rank");
  // An empty board's YAML must parse to a valid spec: where is [], not null.
  expect(share).toHaveTextContent("where: []");
  expect(share).toHaveTextContent("optimize:");
  fireEvent.click(within(share).getByRole("button", { name: "Close Share or act" }));

  fireEvent.click(screen.getByRole("button", { name: /Size of workall Doesn't matter/ }));
  const context = screen.getByText("Context window").closest<HTMLElement>(".facet-row")!;
  fireEvent.click(within(context).getByLabelText("Must"));
  await waitFor(() => expect(sentSpecs(fetch).some((body) =>
    body.where.includes("model.context_window >= 529096"),
  )).toBe(true));
  expect(within(answer).getByText(/qualify — set a Prefer to rank them/)).toBeInTheDocument();
  expect(sentSpecs(fetch).every((body) => Object.keys(body.optimize.weights).length > 0)).toBe(true);
});

it("renders the qualifying models from the live empty-board decision alphabetically", async () => {
  const fetch = routeFetch({
    vocabulary: () => json(realVocabulary),
    decide: () => json(liveEmptyBoard),
  });
  vi.stubGlobal("fetch", fetch);
  render(<DesignedApp />);

  const answer = (await screen.findByLabelText("Facet board answer"))
    .closest<HTMLElement>(".board-answer")!;
  fireEvent.click(within(answer).getByRole("button", { name: "Show all 22" }));
  const rankedAnswer = answer.querySelector<HTMLElement>(".board-ranked-answer")!;
  const modelNames = within(rankedAnswer).getAllByRole("listitem").map((item) =>
    item.querySelector("strong")?.textContent ?? "",
  );

  expect(modelNames).toHaveLength(22);
  expect(modelNames).toEqual([...modelNames].sort((left, right) => left.localeCompare(right)));
  expect(within(answer).queryByText(/no capability data|no evidence for/i)).not.toBeInTheDocument();
  const tableRows = screen.getByLabelText("Decision table").querySelectorAll("tbody tr");
  expect(within(screen.getByLabelText("Decision table")).queryByRole("columnheader", { name: /#/ }))
    .not.toBeInTheDocument();
  expect(tableRows[0]?.querySelector("td")).toHaveTextContent("Claude Fable 5");
  const providers = [...tableRows].map((row) => row.children[1]?.textContent ?? "");
  const firstUnavailable = providers.indexOf("Provider not available");
  expect(firstUnavailable).toBeGreaterThan(0);
  expect(providers.slice(firstUnavailable).every((provider) => provider === "Provider not available"))
    .toBe(true);

  const capability = screen.getByText("Software engineering").closest<HTMLElement>(".facet-row")!;
  fireEvent.click(within(capability).getByLabelText("Prefer"));
  expect(await within(screen.getByLabelText("Decision table")).findByRole("columnheader", { name: /#/ }))
    .toBeInTheDocument();

  const canvas = screen.getByRole("region", { name: "Trade-off canvas" });
  const collapsed = within(canvas).queryByText(/\d+ not plotted/);
  if (collapsed) {
    expect(collapsed).toHaveTextContent("show");
    fireEvent.click(within(collapsed).getByRole("button", { name: "show" }));
    expect(within(canvas).getByText(/Not plotted:/)).toBeInTheDocument();
  }
});

it("plots and tabulates domain estimates while the board is unranked", async () => {
  const fetch = routeFetch({
    vocabulary: () => json(realVocabulary),
    decide: () => json(liveSwePrefer),
  });
  vi.stubGlobal("fetch", fetch);
  render(<DesignedApp />);

  const canvas = await screen.findByRole("region", { name: "Trade-off canvas" });
  plotCostAgainstCapability(canvas);
  await waitFor(() => expect(canvas.querySelectorAll(".point")).toHaveLength(10));
  const first = liveSwePrefer.results[0].estimates?.[0];
  if (!first) throw new Error("live capability fixture has no estimate");
  const modelName = realVocabulary.models[liveSwePrefer.results[0].offering.model]?.display_name ??
    liveSwePrefer.results[0].offering.model;
  const modelRow = [...screen.getByLabelText("Decision table").querySelectorAll("tbody tr")]
    .find((row) => row.textContent?.includes(modelName));
  expect(modelRow).toHaveTextContent(first.value.toFixed(2));
  expect(modelRow).toHaveTextContent("±");
  expect(modelRow?.children[3]).not.toHaveTextContent("not available in this snapshot");
});

it("keeps capability-unknown models outside the ranked board answer", async () => {
  const fetch = routeFetch({
    vocabulary: () => json(realVocabulary),
    decide: (init) => "software_engineering" in JSON.parse(String(init?.body ?? "{}"))
      .optimize.weights
      ? json(liveSwePrefer)
      : json(liveEmptyBoard),
  });
  vi.stubGlobal("fetch", fetch);
  render(<DesignedApp />);
  await screen.findByLabelText("Facet board answer");

  const capability = screen.getByText("Software engineering").closest<HTMLElement>(".facet-row")!;
  fireEvent.click(within(capability).getByLabelText("Prefer"));

  const mayHeading = await screen.findByRole("heading", {
    name: "May qualify — no Software engineering evidence (7)",
  });
  const rankedAnswer = mayHeading.closest<HTMLElement>(".board-ranked-answer")!;
  fireEvent.click(within(rankedAnswer).getByRole("button", { name: "Show all 25" }));

  const rankedNames = [...rankedAnswer.querySelectorAll(":scope > ol > li strong")]
    .map((node) => node.textContent);
  expect(rankedNames).toEqual([...new Set(liveSwePrefer.results.map((result) => result.offering.model))].map((model) =>
    realVocabulary.models[model]?.display_name ?? model.split("/").at(-1)
  ));
  expect(rankedAnswer.querySelectorAll(":scope > ol .board-interval-track")).toHaveLength(25);
  expect(within(rankedAnswer).getAllByText("also via Vertex AI (Google Cloud)").length).toBeGreaterThan(0);

  const mayGroup = mayHeading.closest<HTMLElement>(".board-may-qualify")!;
  expect(within(mayGroup).getAllByRole("listitem")).toHaveLength(7);
  expect(mayGroup.querySelector(".board-interval-track")).toBeNull();
  expect(mayGroup.querySelector(".board-capability")).toBeNull();

  const table = screen.getByRole("region", { name: "Decision table" });
  for (const candidate of liveSwePrefer.may_qualify) {
    const name = realVocabulary.models[candidate.model]?.display_name ?? candidate.model.split("/").at(-1)!;
    const row = within(table).getByRole("button", { name }).closest("tr")!;
    expect(row.cells[0]).toBeEmptyDOMElement();
  }
});

it("lists only qualifying providers as alternatives on the board", async () => {
  const model = "anthropic/claude-opus-5-5";
  const decision = decisionSchema.parse({
    ...liveBudgetCoding,
    eliminated: {
      ...liveBudgetCoding.eliminated,
      model_groups: [
        ...liveBudgetCoding.eliminated.model_groups,
        {
          model,
          model_elimination: null,
          offerings: [{
            values: [],
            offering: {
              model,
              provider: "azure-ai-foundry",
              region: "global",
              tier: "standard",
            },
            unit: "usd_per_task",
            records: [],
            condition: "offering.cost_per_task <= 0.25",
            value: 1,
            formula: null,
          }],
        },
      ],
    },
  });
  const fetch = routeFetch({
    vocabulary: () => json(realVocabulary),
    decide: () => json(decision),
  });
  vi.stubGlobal("fetch", fetch);
  render(<DesignedApp />);
  await screen.findByLabelText("Facet board answer");
  fireEvent.click(screen.getByRole("button", { name: /Coding agent on a budget/ }));

  const answer = screen.getByLabelText("Facet board answer")
    .closest<HTMLElement>(".board-answer")!;
  fireEvent.click(within(answer).getByRole("button", { name: "Show all 15" }));
  const modelRow = within(answer).getByText("Claude Opus 5.5").closest("li")!;
  expect(within(modelRow).getByText(/also via/)).toHaveTextContent(
    "Vertex AI (Google Cloud)",
  );
  expect(within(modelRow).queryByText(/Azure AI Foundry/)).not.toBeInTheDocument();
});

it("shows model-grained funnel and board counts from the live budget decision", async () => {
  const fetch = routeFetch({
    vocabulary: () => json(realVocabulary),
    decide: () => json(liveBudgetCoding),
  });
  vi.stubGlobal("fetch", fetch);
  render(<DesignedApp />);
  await screen.findByLabelText("Facet board answer");
  fireEvent.click(screen.getByRole("button", { name: /Coding agent on a budget/ }));

  const narrowing = screen.getByText("Narrowing, in the order you set conditions")
    .closest<HTMLElement>(".narrowing")!;
  const funnelRows = within(narrowing).getAllByRole("listitem");
  const stepCounts = funnelRows.slice(1, -1).map((row) =>
    Number(row.querySelector(".count")?.textContent),
  );
  const expectedStepCounts = liveBudgetCoding.eliminated.funnel.map(
    (step) => step.models_after,
  );
  expect(stepCounts).toEqual(expectedStepCounts);

  const qualifyingModels = new Set(
    liveBudgetCoding.results.map((result) => result.offering.model),
  ).size;
  const may = liveBudgetCoding.may_qualify.length;
  const lastMust = liveBudgetCoding.eliminated.funnel.at(-1)!;
  expect(qualifyingModels + may).toBe(
    lastMust.models_after + lastMust.models_may_qualify,
  );
  const lastMustRow = funnelRows.at(-2)!;
  expect(lastMustRow.querySelector(".count")).toHaveTextContent(
    String(lastMust.models_after),
  );
  expect(lastMustRow).toHaveTextContent(`${lastMust.models_may_qualify} may`);
  expect(within(narrowing).getByText(
    `${qualifyingModels} qualify · ${may} may qualify · 14 excluded`,
  )).toBeInTheDocument();
  const ranking = within(narrowing).getByText(/Ranking on .*Software engineering 0.60/)
    .closest("li")!;
  expect(ranking.querySelector(".count")).toHaveTextContent(String(qualifyingModels));
  expect(ranking).toHaveTextContent(`+ ${may} may qualify`);
  expect(screen.getByText(`${qualifyingModels} fit · ${may} may`)).toBeInTheDocument();
});

it("never requests the estate twice for the same settled key", async () => {
  const fetch = routeFetch({ decide: (init) => json(decisionFor(init)) });
  vi.stubGlobal("fetch", fetch);
  render(<DesignedApp />);
  await screen.findByRole("region", { name: "Trade-off canvas" });

  fireEvent.change(screen.getByLabelText("Add provider"), {
    target: { value: Object.keys(smallVocabulary.providers)[0] },
  });
  await waitFor(() => expect(document.querySelector(
    ".answer-lists > section:first-child .board-ranked-answer",
  )).toBeInTheDocument());
  expect(screen.getAllByText(/models qualify · .* may qualify/).length).toBe(2);
  await new Promise((resolve) => setTimeout(resolve, 350));
  const estateRequests = sentSpecs(fetch).filter((body) =>
    body.where.some((condition: string) => condition.startsWith("offering.provider in")),
  );
  expect(estateRequests).toHaveLength(1);
  expect(estateRequests[0].explain).toBe("summary");
  expect(estateRequests[0].optimize.weights).toEqual({ "-offering.cost_per_task": 1 });
  await new Promise((resolve) => setTimeout(resolve, 350));
  expect(sentSpecs(fetch).filter((body) =>
    body.where.some((condition: string) => condition.startsWith("offering.provider in")),
  )).toHaveLength(1);
});

it("reissues an estate request aborted by a vocabulary replacement", async () => {
  const fresh = { ...smallVocabulary, snapshot: "snap_after_estate_started" };
  let vocabularyLoads = 0;
  let estateRequests = 0;
  let replaceVocabulary: (() => void) | undefined;
  const changed = (requested: string | null) =>
    json(
      {
        contract_version: "1.4",
        endpoint: "decide",
        snapshot: fresh.snapshot,
        error: {
          code: "snapshot_changed",
          message: "reload the vocabulary and retry",
          requested,
          current: fresh.snapshot,
        },
      },
      409,
    );
  const fetch = routeFetch({
    vocabulary: () => json(vocabularyLoads++ === 0 ? smallVocabulary : fresh),
    decide: (init) => {
      const body = JSON.parse(String(init?.body));
      const snapshot = new Headers(init?.headers).get("x-modelspec-snapshot");
      const isEstate = body.where.some((condition: string) =>
        condition.startsWith("offering.provider in"),
      );
      if (isEstate) {
        estateRequests += 1;
        if (estateRequests === 1)
          return new Promise<Response>((_resolve, reject) => {
            init?.signal?.addEventListener(
              "abort",
              () => reject(new DOMException("Aborted", "AbortError")),
              { once: true },
            );
          });
        return json(decisionFor(init));
      }
      if (body.explain === "full" && snapshot !== fresh.snapshot)
        return new Promise<Response>((resolve) => {
          replaceVocabulary = () => resolve(changed(snapshot));
        });
      return json(decisionFor(init));
    },
  });
  vi.stubGlobal("fetch", fetch);
  render(<DesignedApp />);
  await screen.findByRole("region", { name: "Trade-off canvas" });

  fireEvent.change(screen.getByLabelText("Add provider"), {
    target: { value: Object.keys(smallVocabulary.providers)[0] },
  });
  await waitFor(() => expect(estateRequests).toBe(1));
  if (!replaceVocabulary) throw new Error("full request did not wait for vocabulary replacement");
  replaceVocabulary();

  await waitFor(() => expect(estateRequests).toBe(2));
  await waitFor(() => expect(screen.queryByText("Checking…")).not.toBeInTheDocument());
  expect(vocabularyLoads).toBe(2);
});

it("reissues an estate request aborted by a newer main decision", async () => {
  let estateRequests = 0;
  const zeroQualify = {
    ...fixture,
    results: [],
    may_qualify: fixture.results.slice(0, 3).map(({ offering }) => ({
      model: offering.model,
      offering,
      unknown: ["model.weights_openness"],
    })),
    top: [],
  };
  const fetch = routeFetch({
    decide: (init) => {
      const body = JSON.parse(String(init?.body));
      const isEstate = body.where.some((condition: string) =>
        condition.startsWith("offering.provider in"),
      );
      if (!isEstate) return json(decisionFor(init));
      estateRequests += 1;
      if (estateRequests >= 2) return json(zeroQualify);
      return new Promise<Response>((_resolve, reject) => {
        init?.signal?.addEventListener(
          "abort",
          () => reject(new DOMException("Aborted", "AbortError")),
          { once: true },
        );
      });
    },
  });
  vi.stubGlobal("fetch", fetch);
  render(<DesignedApp />);
  await screen.findByRole("region", { name: "Trade-off canvas" });

  fireEvent.change(screen.getByLabelText("Add provider"), {
    target: { value: Object.keys(smallVocabulary.providers)[0] },
  });
  await waitFor(() => expect(estateRequests).toBe(1));
  fireEvent.click(screen.getByRole("button", { name: /Coding agent on a budget/ }));

  expect(await screen.findByText("0 models qualify · 3 may qualify")).toBeInTheDocument();
  expect(estateRequests).toBe(2);
  expect(screen.queryByText("Checking…")).not.toBeInTheDocument();
});

it("shows a retry when the estate request fails", async () => {
  const fetch = routeFetch({
    decide: (init) => {
      const body = JSON.parse(String(init?.body));
      return body.where.some((condition: string) => condition.startsWith("offering.provider in"))
        ? json({ error: { code: "snapshot_unavailable", message: "Try again" } }, 503)
        : json(decisionFor(init));
    },
  });
  vi.stubGlobal("fetch", fetch);
  render(<DesignedApp />);
  await screen.findByRole("region", { name: "Trade-off canvas" });
  fireEvent.change(screen.getByLabelText("Add provider"), {
    target: { value: Object.keys(smallVocabulary.providers)[0] },
  });
  expect(await screen.findByText("Couldn't load:")).toBeInTheDocument();
  expect(screen.getByRole("button", { name: "retry" })).toBeInTheDocument();
  expect(screen.queryByText("Checking…")).not.toBeInTheDocument();
});

it("labels capability intervals with their ranking basis and units", async () => {
  const fetch = routeFetch({ decide: (init) => json(decisionFor(init)) });
  vi.stubGlobal("fetch", fetch);
  render(<DesignedApp />);
  await screen.findByRole("region", { name: "Trade-off canvas" });

  const capability = screen.getByText("Software engineering").closest<HTMLElement>(".facet-row")!;
  fireEvent.click(within(capability).getByLabelText("Prefer"));

  expect(await screen.findByText("Software engineering, estimated · 80% interval")).toBeInTheDocument();
  expect(screen.queryByText("Not ranked — set a Prefer to rank these")).not.toBeInTheDocument();
  expect(screen.getByText(/Ranking on Software engineering 0.50/)).toBeInTheDocument();
  expect((await screen.findAllByText(/above the lineup median|near the median|below the median/)).length)
    .toBeGreaterThan(0);
  expect(screen.queryByText(/capability score$/)).not.toBeInTheDocument();
  expect(screen.getAllByLabelText("Delta 4.7 capability interval").length).toBeGreaterThan(0);
});

it("shows no stale designed result after a hosted error", async () => {
  let calls = 0;
  const fetch = routeFetch({
    decide: (init) =>
      calls++ === 0
        ? json(decisionFor(init))
        : json({ error: { code: "snapshot_unavailable", message: "Try again" } }, 503),
  });
  vi.stubGlobal("fetch", fetch);
  render(<App />);
  await screen.findByText("Coding agent on a budget");
  expect(
    await screen.findByRole("region", { name: "Trade-off canvas" }),
  ).toBeInTheDocument();
  fireEvent.click(screen.getByText("Coding agent on a budget"));

  await waitFor(() => expect(screen.getByRole("alert")).toHaveTextContent("Try again"));
  expect(
    screen.queryByRole("region", { name: "Trade-off canvas" }),
  ).not.toBeInTheDocument();
});

it("treats the legacy demo flag as the public board", async () => {
  const fetch = routeFetch({ decide: (init) => json(decisionFor(init)) });
  vi.stubGlobal("fetch", fetch);
  history.replaceState(null, "", "/decide/?demo=1");
  render(<App />);
  expect(await screen.findByRole("heading", { name: "Set what matters. Watch the field narrow." })).toBeInTheDocument();
  expect(screen.queryByLabelText("Describe your task")).not.toBeInTheDocument();
  expect(fetch).toHaveBeenCalled();
});

it("renders unavailable snapshot facets instead of hiding them", async () => {
  vi.stubGlobal("fetch", routeFetch({ decide: (init) => json(decisionFor(init)) }));
  render(<App />);
  await screen.findByText("Coding agent on a budget");
  const table = await screen.findByRole("region", { name: "Decision table" });
  fireEvent.click(within(table).getAllByRole("button", { name: "Delta 4.7" })[0]);
  const detail = await screen.findByRole("region", { name: "Why this model" });
  expect(within(detail).getAllByText("not available in this snapshot").length).toBeGreaterThan(0);
});

it("renders capability intervals, probability of best and top-three stability", async () => {
  const estimated = {
    ...fixture,
    contract_version: "1.6",
    results: fixture.results.map((result, index) => {
      const driver = {
        ...result.evidence[0].items[0],
        loading: 1,
        estimate_weight: 0.72,
        recency_weight: 0.94,
      };
      const value = 2 - index * 0.2;
      return {
        ...result,
        estimates: [
          {
            domain: "software_engineering",
            value,
            interval: [value - 0.4, value + 0.4],
            harness: null,
            effort: null,
          },
        ],
        p_best: index === 0 ? 0.62 : 0.12,
        top3_stability: index === 0 ? 0.91 : 0.5,
        contributions: [
          ...result.contributions,
          {
            raw_value: value,
            unit: "capability_score",
            records: [driver.record_id],
            dimension: "software_engineering",
            weight: 0.6,
            value: 1 - index * 0.2,
            normalisation: "feasible min-max; max",
            evidence: [driver],
            formula: "monotone domain evidence estimate",
          },
        ],
        warnings:
          index === 0 ? ["not_separable", "proxy_evidence_only"] : ["not_separable"],
      };
    }),
  };
  vi.stubGlobal("fetch", routeFetch({ decide: () => json(estimated) }));
  render(<App />);
  await screen.findByText("Coding agent on a budget");

  const table = await screen.findByRole("region", { name: "Decision table" });
  fireEvent.click(within(table).getAllByRole("button", { name: "Delta 4.7" })[0]);
  const detail = await screen.findByRole("region", { name: "Why this model" });
  expect(detail).toHaveTextContent("P(best) 62%");
  expect(detail).toHaveTextContent("Top-3 stability 91%");
  expect(detail).toHaveTextContent("Not separable: intervals overlap.");
  expect(detail).toHaveTextContent("Proxy evidence only.");
});

it("renders the full decision as four models without machine condition syntax", async () => {
  vi.stubGlobal("fetch", routeFetch({ decide: (init) => json(decisionFor(init)) }));
  render(<App />);
  await screen.findByText("Coding agent on a budget");

  const table = await screen.findByRole("region", { name: "Decision table" });
  expect(within(table).getAllByRole("row")).toHaveLength(5);
  expect(screen.getByText("4 models · 8 offerings")).toBeInTheDocument();
  fireEvent.click(within(table).getAllByRole("button", { name: "Delta 4.7" })[0]);
  expect(screen.getAllByText("Type: Text generator").length).toBeGreaterThan(0);
  expect(screen.getAllByText("Has a provider").length).toBeGreaterThan(0);
  expect(screen.getByText("No model is one condition away.")).toBeInTheDocument();
  expect(screen.queryByText("model.class = text-generator")).not.toBeInTheDocument();
  expect(screen.queryByText("known(offering.provider)")).not.toBeInTheDocument();
});

it("on a 409 to the summary, reloads once, retries the summary, then asks for full on the new snapshot", async () => {
  const fresh = { ...smallVocabulary, snapshot: "snap_after_deploy" };
  let vocabularyLoads = 0;
  const fetch = routeFetch({
    vocabulary: () => json(vocabularyLoads++ === 0 ? smallVocabulary : fresh),
    decide: (init) => {
      const sent = new Headers(init?.headers).get("x-modelspec-snapshot");
      if (sent !== fresh.snapshot)
        return json(
          {
            contract_version: "1.4",
            endpoint: "decide",
            snapshot: fresh.snapshot,
            error: {
              code: "snapshot_changed",
              message: "reload the vocabulary and retry",
              requested: sent,
              current: fresh.snapshot,
            },
          },
          409,
        );
      return json(decisionFor(init));
    },
  });
  vi.stubGlobal("fetch", fetch);
  render(<App />);
  await screen.findByText("Coding agent on a budget");

  expect(
    await screen.findByRole("region", { name: "Trade-off canvas" }),
  ).toBeInTheDocument();
  expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  const sent = (explain: string) =>
    rankingCalls(fetch)
      .filter(([, init]) => JSON.parse(String(init?.body)).explain === explain)
      .map(([, init]) => new Headers(init?.headers).get("x-modelspec-snapshot"));
  await waitFor(() => expect(sent("full")).toEqual([fresh.snapshot]));
  expect(sent("summary")).toEqual([smallVocabulary.snapshot, fresh.snapshot]);
  // Probes follow the reloaded vocabulary; none of them reloads it again.
  await waitFor(() => expect(sent("none").length).toBeGreaterThan(0));
  expect(new Set(sent("none"))).toEqual(new Set([fresh.snapshot]));
  expect(vocabularyLoads).toBe(2);
});

it("after the summary reloaded, a 409 to the full request keeps the summary and reloads no more", async () => {
  const fresh = { ...smallVocabulary, snapshot: "snap_after_deploy" };
  let vocabularyLoads = 0;
  const changed = (requested: string | null) =>
    json(
      {
        contract_version: "1.4",
        endpoint: "decide",
        snapshot: "snap_newer",
        error: {
          code: "snapshot_changed",
          message: "reload the vocabulary and retry",
          requested,
          current: "snap_newer",
        },
      },
      409,
    );
  const fetch = routeFetch({
    vocabulary: () => json(vocabularyLoads++ === 0 ? smallVocabulary : fresh),
    decide: (init) => {
      const sent = new Headers(init?.headers).get("x-modelspec-snapshot");
      const explain = JSON.parse(String(init?.body)).explain;
      const ranking = Object.hasOwn(
        JSON.parse(String(init?.body)).optimize.weights ?? {},
        "-offering.cost_per_task",
      );
      if ((explain === "full" && ranking) || sent !== fresh.snapshot) return changed(sent);
      return json(decisionFor(init));
    },
  });
  vi.stubGlobal("fetch", fetch);
  render(<App />);
  await screen.findByText("Coding agent on a budget");

  expect(
    await screen.findByRole("region", { name: "Trade-off canvas" }),
  ).toBeInTheDocument();
  await waitFor(() =>
    expect(rankingSpecs(fetch).filter((spec) => spec.explain === "full")).toHaveLength(1),
  );
  expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  expect(vocabularyLoads).toBe(2);
});

it("keeps the reloaded board vocabulary visible when a retried summary fails", async () => {
  const fresh = {
    ...smallVocabulary,
    snapshot: "snap_retry_fails",
    domains: smallVocabulary.domains.map((domain, index) => index === 0
      ? { ...domain, name: "Fresh vocabulary marker" }
      : domain),
  };
  let vocabularyLoads = 0;
  let decisionRequests = 0;
  const fetch = routeFetch({
    vocabulary: () => json(vocabularyLoads++ === 0 ? smallVocabulary : fresh),
    decide: () => {
      decisionRequests += 1;
      return decisionRequests === 1
        ? json({ error: { code: "snapshot_changed", message: "reload the vocabulary and retry" } }, 409)
        : json({ error: { code: "retry_failed", message: "retry failed" } }, 500);
    },
  });
  vi.stubGlobal("fetch", fetch);
  render(<App />);
  await screen.findByText("Coding agent on a budget");

  expect(await screen.findByRole("alert")).toHaveTextContent("retry failed");
  expect(screen.getByText("Fresh vocabulary marker")).toBeInTheDocument();
  expect(vocabularyLoads).toBe(2);
  expect(decisionRequests).toBe(2);
});

it("folds a rejected refinement with the vocabulary installed after a snapshot change", async () => {
  const fresh = {
    ...refinementVocabulary,
    snapshot: "snap_after_deploy",
    refinements: refinementVocabulary.refinements?.map((row) => row.id === "python"
      ? { ...row, parent_domain: "engineering_stem" }
      : row),
  };
  let vocabularyLoads = 0;
  const fetch = routeFetch({
    vocabulary: () => json(vocabularyLoads++ === 0 ? refinementVocabulary : fresh),
    decide: (init) => {
      const snapshot = new Headers(init?.headers).get("x-modelspec-snapshot");
      const sent = JSON.parse(String(init?.body));
      if (snapshot === refinementVocabulary.snapshot && "software_engineering/python" in sent.optimize.weights)
        return json({ error: { code: "snapshot_changed", message: "reload the vocabulary and retry" } }, 409);
      if ("software_engineering/python" in sent.optimize.weights)
        return json({ error: { code: "invalid_spec", message: "Refinement weights are not rankable yet.", issues: [] } }, 400);
      return json(decisionFor(init));
    },
  });
  vi.stubGlobal("fetch", fetch);
  render(<DesignedApp />);
  await screen.findByLabelText("Facet board answer");
  const software = screen.getByText("Software engineering").closest<HTMLElement>(".facet-row")!;
  fireEvent.click(within(software).getByLabelText("Prefer"));
  await waitFor(() => expect(sentSpecs(fetch).some((spec) =>
    spec.explain === "summary" && spec.optimize.weights.software_engineering === 0.5,
  )).toBe(true));
  fireEvent.click(within(software).getByRole("button", { name: "Refine" }));
  const callsBeforeRefinement = fetch.mock.calls.length;
  fireEvent.click(within(within(software).getByText("Python").closest<HTMLElement>(".refinement-row")!).getByLabelText("Prefer"));

  const refinementSummaries = () => fetch.mock.calls.slice(callsBeforeRefinement).filter(([url, init]) =>
    url !== VOCABULARY_URL && JSON.parse(String(init?.body)).explain === "summary" && (() => {
      const weights = JSON.parse(String(init?.body)).optimize.weights;
      return "software_engineering/python" in weights || "engineering_stem" in weights;
    })(),
  );
  await waitFor(() => expect(refinementSummaries()).toHaveLength(3));
  const summaries = refinementSummaries();
  expect(summaries.map(([, init]) => ({
    snapshot: new Headers(init?.headers).get("x-modelspec-snapshot"),
    weights: JSON.parse(String(init?.body)).optimize.weights,
  }))).toEqual([
    { snapshot: refinementVocabulary.snapshot, weights: { software_engineering: 0.25, "software_engineering/python": 0.25 } },
    { snapshot: fresh.snapshot, weights: { software_engineering: 0.25, "software_engineering/python": 0.25 } },
    { snapshot: fresh.snapshot, weights: { software_engineering: 0.25, engineering_stem: 0.25 } },
  ]);
  expect(JSON.parse(String(summaries[1][1]?.body)).optimize.weights)
    .toHaveProperty("software_engineering/python");
  expect(JSON.parse(String(summaries[2][1]?.body)).optimize.weights)
    .toEqual({ software_engineering: 0.25, engineering_stem: 0.25 });
  expect(vocabularyLoads).toBe(2);
});
