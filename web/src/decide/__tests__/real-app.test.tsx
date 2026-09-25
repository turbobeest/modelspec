import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import fixtureJson from "../__fixtures__/full-decision.json";
import App from "../App";
import { decisionSchema } from "../adapter";
import { json, routeFetch, sentSpecs } from "./vocab-fixtures";

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
  expect(
    screen.getByRole("region", { name: "Why this model" }),
  ).toHaveTextContent("Delta");
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
  expect(screen.getAllByText("Type: text generator").length).toBeGreaterThan(0);
  expect(screen.getAllByText("Has a provider").length).toBeGreaterThan(0);
  expect(screen.getByText("No model is one condition away.")).toBeInTheDocument();
  expect(screen.queryByText("model.class = text-generator")).not.toBeInTheDocument();
  expect(screen.queryByText("known(offering.provider)")).not.toBeInTheDocument();
});
