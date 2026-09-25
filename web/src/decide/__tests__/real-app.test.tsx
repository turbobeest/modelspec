import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import fixtureJson from "../__fixtures__/full-decision.json";
import App from "../App";
import { decisionSchema } from "../adapter";
import { json, routeFetch, sentSpecs, smallVocabulary } from "./vocab-fixtures";
import { VOCABULARY_URL } from "../vocabulary";

const fixture = decisionSchema.parse(fixtureJson);

beforeEach(() => history.replaceState(null, "", "/"));
afterEach(() => vi.unstubAllGlobals());

it("runs the designed App on a full hosted decision without fictional labels", async () => {
  const fetch = routeFetch({
    decide: (init) => {
      const spec = JSON.parse(String(init?.body));
      return json(
        spec.explain === "none"
          ? { ...fixture, explain: "none", results: fixture.results.slice(0, 2) }
          : fixture,
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
    "Gamma Max 0902",
  );
  expect(document.body).toHaveTextContent("lab/alpha");
  expect(document.body).not.toHaveTextContent(/Gamma Max 902|\bAlpha\b/);
  expect(screen.queryByText(/fictional/i)).not.toBeInTheDocument();

  const sent = sentSpecs(fetch).find((body) => body.explain === "full");
  expect(sent).not.toHaveProperty("task");
  expect(sent.where).toContain("model.class = text-generator");
  expect(sent.where).toContain("model.context_window >= 200000");
  // The benchmark comes from the vocabulary, never a fixed name.
  expect(sent.where).toContain("quality >= 68 @independent");
  expect(sent.capabilities).toEqual({ software_engineering: "required" });
  expect(sent.task_tokens).toEqual({ input: 40000, output: 4000 });
  expect(Object.keys(sent.optimize.weights).sort()).toEqual([
    "-offering.cost_per_task",
    "quality",
  ]);
  expect(sent.explain).toBe("full");

  fireEvent.click(screen.getByRole("button", { name: "Share or act" }));
  const dialog = screen.getByRole("dialog");
  fireEvent.click(within(dialog).getByRole("tab", { name: "API call" }));
  expect(dialog).toHaveTextContent("https://api.modelspec.dev/v1/decide");
  expect(dialog).not.toHaveTextContent(/fictional/i);
  expect(dialog).not.toHaveTextContent('"task"');
});

it("switches the ranking benchmark in one click from the rank-by control", async () => {
  const vocabulary = {
    ...smallVocabulary,
    benchmarks: [
      ...smallVocabulary.benchmarks,
      { ...smallVocabulary.benchmarks[0], id: "quality_pro", name: "Quality Pro", models: 3 },
    ],
  };
  const fetch = routeFetch({ vocabulary: () => json(vocabulary), decide: () => json(fixture) });
  vi.stubGlobal("fetch", fetch);
  render(<App />);
  await screen.findByText("Coding agent on a budget");
  fireEvent.change(screen.getByLabelText("Describe your task"), {
    target: { value: "Refactor a large Rust codebase, precision matters" },
  });
  fireEvent.click(screen.getByRole("button", { name: /Find models/ }));
  await screen.findByRole("region", { name: "Trade-off canvas" });
  expect(
    screen.getByText(/rank on Quality Bench, the direct benchmark with the most verified lineup models \(4\); also direct: Quality Pro \(3\)/),
  ).toBeInTheDocument();

  const control = screen.getByRole("group", { name: "Benchmark to rank on" });
  expect(within(control).getByRole("button", { name: /Quality Bench 4 models/ })).toHaveAttribute(
    "aria-pressed",
    "true",
  );
  fireEvent.click(within(control).getByRole("button", { name: /Quality Pro 3 models/ }));

  await waitFor(() => {
    const full = sentSpecs(fetch).filter((body) => body.explain === "full");
    const last = full[full.length - 1];
    expect(Object.keys(last.optimize.weights)).toContain("quality_pro");
    expect(last.where).toContain("quality_pro >= 68 @independent");
    expect(last.where.some((c: string) => c.startsWith("quality >="))).toBe(false);
  });
});

it("shows no stale designed result after a hosted error", async () => {
  let calls = 0;
  const fetch = routeFetch({
    decide: () =>
      calls++ === 0
        ? json(fixture)
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
  vi.stubGlobal("fetch", routeFetch({ decide: () => json(fixture) }));
  render(<App />);
  await screen.findByText("Coding agent on a budget");
  fireEvent.click(screen.getByText("start from constraints"));
  const detail = await screen.findByRole("region", { name: "Why this model" });
  expect(within(detail).getAllByText("not available in this snapshot").length).toBeGreaterThan(0);
});

it("renders the full decision as four models without machine condition syntax", async () => {
  vi.stubGlobal("fetch", routeFetch({ decide: () => json(fixture) }));
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
      return json(fixture);
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
      return json(fixture);
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
