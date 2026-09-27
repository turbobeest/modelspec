import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import fixtureJson from "../__fixtures__/full-decision.json";
import App, { DesignedApp } from "../App";
import { decisionSchema } from "../adapter";
import { json, routeFetch, sentSpecs, smallVocabulary } from "./vocab-fixtures";
import { VOCABULARY_URL } from "../vocabulary";

const fixture = decisionSchema.parse(fixtureJson);

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

beforeEach(() => history.replaceState(null, "", "/"));
afterEach(() => vi.unstubAllGlobals());

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
  const task = screen.getByLabelText("Describe your task");
  fireEvent.change(task, {
    target: { value: "Refactor a large Rust codebase, precision matters" },
  });
  fireEvent.click(screen.getByRole("button", { name: /Find models/ }));

  expect(screen.getByText("Reading your task…")).toBeInTheDocument();
  expect(await screen.findByText("Read from your task:")).toBeInTheDocument();
  expect(
    await screen.findByRole("region", { name: "Trade-off canvas" }),
  ).toBeInTheDocument();
  expect(screen.getByText("Shortlist")).toBeInTheDocument();
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

  const sent = sentSpecs(fetch).find((body) => body.explain === "full");
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
    "modelspec snapshot fetch modelspec decide spec.yaml --json",
  );
});

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
  render(<DesignedApp demo={false} board />);
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
  expect(sentSpecs(fetch).every((body) => body.where.length === 0)).toBe(true);
});

it("labels capability intervals with their ranking basis and units", async () => {
  const fetch = routeFetch({ decide: (init) => json(decisionFor(init)) });
  vi.stubGlobal("fetch", fetch);
  render(<DesignedApp demo={false} board />);
  await screen.findByRole("region", { name: "Trade-off canvas" });

  const capability = screen.getByText("Software engineering").closest<HTMLElement>(".facet-row")!;
  fireEvent.click(within(capability).getByLabelText("Prefer"));

  expect(await screen.findByText("Software engineering, estimated · 80% interval")).toBeInTheDocument();
  expect(screen.getAllByText(/capability score$/).length).toBeGreaterThan(0);
  expect(screen.getByLabelText("Delta 4.7 capability interval")).toBeInTheDocument();
});

it("switches the ranking benchmark in one click from the rank-by control", async () => {
  const vocabulary = {
    ...smallVocabulary,
    benchmarks: [
      ...smallVocabulary.benchmarks,
      { ...smallVocabulary.benchmarks[0], id: "quality_pro", name: "Quality Pro", models: 3 },
    ],
  };
  const fetch = routeFetch({
    vocabulary: () => json(vocabulary),
    decide: (init) => json(decisionFor(init)),
  });
  vi.stubGlobal("fetch", fetch);
  render(<App />);
  await screen.findByText("Coding agent on a budget");
  fireEvent.change(screen.getByLabelText("Describe your task"), {
    target: { value: "Refactor a large Rust codebase, precision matters" },
  });
  fireEvent.click(screen.getByRole("button", { name: /Find models/ }));
  await screen.findByRole("region", { name: "Trade-off canvas" });
  expect(
    screen.getByText(/Software engineering capability: estimated from 1 benchmarks; Quality Bench is preselected for Measured by/),
  ).toBeInTheDocument();

  const control = screen.getByRole("group", { name: "Measurement basis" });
  expect(
    within(control).getByRole("button", { name: /Software engineering capability/ }),
  ).toHaveAttribute("aria-pressed", "true");
  expect(within(control).getByRole("button", { name: /Quality Bench 4 models/ })).toHaveAttribute(
    "aria-pressed",
    "false",
  );
  fireEvent.click(within(control).getByRole("button", { name: /Quality Pro 3 models/ }));

  await waitFor(() => {
    const full = sentSpecs(fetch).filter((body) => body.explain === "full");
    const last = full[full.length - 1];
    expect(Object.keys(last.optimize.weights)).toContain("quality_pro");
    expect(last.where.some((c: string) => c.startsWith("quality_pro >="))).toBe(false);
    expect(last.where.some((c: string) => c.startsWith("quality >="))).toBe(false);
  });
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
  fireEvent.click(screen.getByText("start from constraints"));
  expect(
    await screen.findByRole("region", { name: "Trade-off canvas" }),
  ).toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", { name: "Run decision" }));

  await waitFor(() => expect(screen.getByRole("alert")).toHaveTextContent("Try again"));
  expect(
    screen.queryByRole("region", { name: "Trade-off canvas" }),
  ).not.toBeInTheDocument();
});

it("keeps the fictional backend only behind demo=1", () => {
  const fetch = vi.fn();
  vi.stubGlobal("fetch", fetch);
  history.replaceState(null, "", "/?demo=1");
  render(<App />);
  expect(screen.getByText("Fictional sample data")).toBeInTheDocument();
  expect(fetch).not.toHaveBeenCalled();
});

it("renders unavailable snapshot facets instead of hiding them", async () => {
  vi.stubGlobal("fetch", routeFetch({ decide: (init) => json(decisionFor(init)) }));
  render(<App />);
  await screen.findByText("Coding agent on a budget");
  fireEvent.click(screen.getByText("start from constraints"));
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
  fireEvent.click(screen.getByText("start from constraints"));

  const detail = await screen.findByRole("region", { name: "Why this model" });
  expect(detail).toHaveTextContent("P(best) 62%");
  expect(detail).toHaveTextContent("Top-3 stability 91%");
  expect(detail).toHaveTextContent("Not separable: intervals overlap.");
  expect(detail).toHaveTextContent("Proxy evidence only.");
  expect(detail).toHaveTextContent("Top drivers");
  expect(detail).toHaveTextContent("Quality Bench · 72% influence · direct · 2026-08-01");
  expect(within(detail).getByRole("link", { name: "Source ↗" })).toHaveAttribute(
    "href",
    "https://board.example.org/results",
  );
});

it("renders the full decision as four models without machine condition syntax", async () => {
  vi.stubGlobal("fetch", routeFetch({ decide: (init) => json(decisionFor(init)) }));
  render(<App />);
  await screen.findByText("Coding agent on a budget");
  fireEvent.click(screen.getByText("start from constraints"));

  const table = await screen.findByRole("region", { name: "Decision table" });
  expect(within(table).getAllByRole("row")).toHaveLength(5);
  expect(screen.getByText("4 models · 8 offerings")).toBeInTheDocument();
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
  fireEvent.click(screen.getByText("start from constraints"));

  expect(
    await screen.findByRole("region", { name: "Trade-off canvas" }),
  ).toBeInTheDocument();
  expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  const sent = (explain: string) =>
    fetch.mock.calls
      .filter(
        ([url, init]) =>
          url !== VOCABULARY_URL && JSON.parse(String(init?.body)).explain === explain,
      )
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
      if (explain === "full" || sent !== fresh.snapshot) return changed(sent);
      return json(decisionFor(init));
    },
  });
  vi.stubGlobal("fetch", fetch);
  render(<App />);
  await screen.findByText("Coding agent on a budget");
  fireEvent.click(screen.getByText("start from constraints"));

  expect(
    await screen.findByRole("region", { name: "Trade-off canvas" }),
  ).toBeInTheDocument();
  await waitFor(() =>
    expect(sentSpecs(fetch).filter((spec) => spec.explain === "full")).toHaveLength(1),
  );
  expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  expect(vocabularyLoads).toBe(2);
});
