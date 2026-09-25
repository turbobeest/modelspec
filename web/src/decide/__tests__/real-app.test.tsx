import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import fixtureJson from "../__fixtures__/full-decision.json";
import App from "../App";
import { DECIDE_ENDPOINT, decisionSchema } from "../adapter";

const fixture = decisionSchema.parse(fixtureJson);

beforeEach(() => history.replaceState(null, "", "/"));
afterEach(() => vi.unstubAllGlobals());

it("runs the designed App on a full hosted decision without fictional labels", async () => {
  const fetch = vi.fn().mockImplementation((_url, init?: RequestInit) => {
    const spec = JSON.parse(String(init?.body));
    const answer =
      spec.explain === "none"
        ? { ...fixture, explain: "none", results: fixture.results.slice(0, 2) }
        : fixture;
    return Promise.resolve(
      new Response(JSON.stringify(answer), {
        status: 200,
        headers: { "content-type": "application/json" },
      }),
    );
  });
  vi.stubGlobal("fetch", fetch);
  render(<App />);

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

  const fullCall = fetch.mock.calls.find(([, init]) => {
    const body = JSON.parse(String((init as RequestInit).body));
    return body.explain === "full";
  });
  expect(fullCall?.[0]).toBe(DECIDE_ENDPOINT);
  const sent = JSON.parse(String((fullCall?.[1] as RequestInit).body));
  expect(sent).not.toHaveProperty("task");
  expect(sent.where).toContain("model.class = text-generator");
  expect(sent.where).toContain("model.context_window >= 200000");
  expect(sent.explain).toBe("full");

  fireEvent.click(screen.getByRole("button", { name: "Share or act" }));
  const dialog = screen.getByRole("dialog");
  fireEvent.click(within(dialog).getByRole("tab", { name: "API call" }));
  expect(dialog).toHaveTextContent("https://api.modelspec.dev/v1/decide");
  expect(dialog).not.toHaveTextContent(/fictional/i);
  expect(dialog).not.toHaveTextContent('"task"');
});

it("shows no stale designed result after a hosted error", async () => {
  const fetch = vi
    .fn()
    .mockResolvedValueOnce(
      new Response(JSON.stringify(fixture), {
        status: 200,
        headers: { "content-type": "application/json" },
      }),
    )
    .mockResolvedValueOnce(
      new Response(
        JSON.stringify({
          error: { code: "snapshot_unavailable", message: "Try again" },
        }),
        { status: 503, headers: { "content-type": "application/json" } },
      ),
    );
  vi.stubGlobal("fetch", fetch);
  render(<App />);

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
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue(
      new Response(JSON.stringify(fixture), {
        status: 200,
        headers: { "content-type": "application/json" },
      }),
    ),
  );
  render(<App />);
  fireEvent.click(screen.getByText("start from constraints"));
  const table = await screen.findByRole("region", { name: "Decision table" });
  expect(within(table).getAllByText("not available in this snapshot").length).toBeGreaterThan(0);
});
