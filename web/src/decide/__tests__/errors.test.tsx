// Every failure the real page can meet ends in a message, never an endless
// skeleton (MODEL-153): a 400 beside the chip that caused it, a 503 as "no
// snapshot yet", a network failure or a timeout with Retry, and a missing
// vocabulary before any decision is asked for.
import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import summaryJson from "../__fixtures__/compact-summary.json";
import fixtureJson from "../__fixtures__/full-decision.json";
import App from "../App";
import { DECIDE_TIMEOUT_MS, DecideApiError, decisionSchema, hostedEngine } from "../adapter";
import { json, routeFetch } from "./vocab-fixtures";

const fixture = decisionSchema.parse(fixtureJson);
const TASK = "Refactor a large Rust codebase, precision matters";

beforeEach(() => history.replaceState(null, "", "/"));
afterEach(() => {
  vi.unstubAllGlobals();
  vi.useRealTimers();
});

async function findModels() {
  render(<App />);
  await screen.findByText("Coding agent on a budget");
  fireEvent.change(screen.getByLabelText("Describe your task"), { target: { value: TASK } });
  fireEvent.click(screen.getByRole("button", { name: /Find models/ }));
}

const noSkeleton = () =>
  expect(document.querySelector('[aria-busy="true"]')).not.toBeInTheDocument();

it("shows a 400's issues in plain language beside the chip that caused them", async () => {
  vi.stubGlobal(
    "fetch",
    routeFetch({
      decide: () =>
        json(
          {
            contract_version: "1.3",
            endpoint: "decide",
            snapshot: "snap_7bf37267f8f2b2eb",
            error: {
              code: "invalid_spec",
              message: "the request body is not a valid decision spec",
              issues: [
                {
                  path: "where[2]",
                  condition: "model.context_window >= 200000",
                  field: "model.context_window",
                  reason: "unknown facet 'model.context_window': not in registry/facets.yaml; did you mean 'model.context_windows'?",
                },
                {
                  path: "optimize.weights",
                  condition: null,
                  field: "quality",
                  reason: "unknown facet 'quality': not in the facet registry",
                },
              ],
            },
          },
          400,
        ),
    }),
  );
  await findModels();

  const alert = await screen.findByRole("alert");
  expect(alert).toHaveTextContent("The engine could not read part of this spec.");
  expect(alert).toHaveTextContent("marked beside the condition or control");
  const chip = screen
    .getByRole("button", { name: /Edit condition: Context: at least 200,000 tokens/ })
    .closest(".chip");
  expect(chip).toHaveClass("has-issue");
  const wrap = chip!.parentElement!;
  expect(within(wrap).getByRole("note")).toHaveTextContent(
    "The engine does not know “model.context_window”, so it cannot check this condition. Did you mean “model.context_windows”?",
  );
  // The other chips are not blamed.
  expect(document.querySelectorAll(".chip.has-issue")).toHaveLength(1);
  expect(screen.getByText(/The engine does not know “quality”/)).toBeInTheDocument();
  noSkeleton();
});

it("shows a 503 as no snapshot yet, with Retry", async () => {
  let calls = 0;
  vi.stubGlobal(
    "fetch",
    routeFetch({
      decide: () =>
        calls++ === 0
          ? json(
              {
                contract_version: "1.3",
                endpoint: "decide",
                snapshot: null,
                error: "no_snapshot",
                message: "the decision snapshot is not published yet",
              },
              503,
            )
          : json(fixture),
    }),
  );
  await findModels();

  const alert = await screen.findByRole("alert");
  expect(alert).toHaveTextContent("No snapshot yet.");
  expect(alert).toHaveTextContent("the decision snapshot is not published yet");
  noSkeleton();
  fireEvent.click(within(alert).getByRole("button", { name: "Retry" }));
  expect(await screen.findByRole("region", { name: "Trade-off canvas" })).toBeInTheDocument();
});

it("shows a network failure with Retry, and Retry recovers", async () => {
  let calls = 0;
  vi.stubGlobal(
    "fetch",
    routeFetch({
      decide: () => {
        // The summary, which the page asks for first, fails to connect.
        if (calls++ < 1) throw new TypeError("Failed to fetch");
        return json(fixture);
      },
    }),
  );
  await findModels();

  const alert = await screen.findByRole("alert");
  expect(alert).toHaveTextContent("Couldn't reach the decision service.");
  noSkeleton();
  fireEvent.click(within(alert).getByRole("button", { name: "Retry" }));
  expect(await screen.findByRole("region", { name: "Trade-off canvas" })).toBeInTheDocument();
});

const explainOf = (init: RequestInit | undefined) => JSON.parse(String(init?.body)).explain;

it("asks for the summary first, draws it, then enriches the Why panel with full", async () => {
  let release: () => void = () => {};
  const fullAnswered = new Promise<void>((resolve) => (release = resolve));
  const fetch = routeFetch({
    decide: async (init) => {
      if (explainOf(init) !== "full") return json(summaryJson);
      await fullAnswered;
      return json(fixture);
    },
  });
  vi.stubGlobal("fetch", fetch);
  await findModels();

  expect(await screen.findByRole("region", { name: "Trade-off canvas" })).toBeInTheDocument();
  const decides = () =>
    fetch.mock.calls.filter(([, init]) => init?.method === "POST").map(([, init]) => explainOf(init));
  expect(decides().slice(0, 2)).toEqual(["summary", "full"]);
  const why = screen.getByRole("region", { name: "Why this model" });
  expect(why).toHaveTextContent("Loading the detailed explanation");
  expect(why).not.toHaveTextContent("unavailable");

  release();
  await waitFor(() =>
    expect(screen.getByRole("region", { name: "Why this model" })).not.toHaveTextContent(
      "Loading the detailed explanation",
    ),
  );
  expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  // Enriching the explanation does not re-run the next-question probes.
  expect(decides().filter((explain) => explain === "summary")).toHaveLength(1);
});

it.each([
  ["a non-JSON 503 (Cloudflare 1102)", () => new Response("error code: 1102", { status: 503 })],
  [
    "a network failure (a limit page carries no CORS header)",
    () => {
      throw new TypeError("Failed to fetch");
    },
  ],
])("keeps the summary and marks details unavailable when full fails with %s", async (_name, limited) => {
  vi.stubGlobal(
    "fetch",
    routeFetch({ decide: (init) => (explainOf(init) === "full" ? limited() : json(summaryJson)) }),
  );
  await findModels();

  expect(await screen.findByRole("region", { name: "Trade-off canvas" })).toBeInTheDocument();
  const why = screen.getByRole("region", { name: "Why this model" });
  await waitFor(() => expect(why).toHaveTextContent("Detailed explanation unavailable for this request"));
  expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  noSkeleton();
});

it("reports a request that never answers instead of spinning", async () => {
  vi.useFakeTimers();
  vi.stubGlobal(
    "fetch",
    vi.fn().mockImplementation(
      (_url: string, init?: RequestInit) =>
        new Promise((_resolve, reject) =>
          init?.signal?.addEventListener("abort", () =>
            reject(new DOMException("Aborted", "AbortError")),
          ),
        ),
    ),
  );
  const pending = hostedEngine
    .decide({ spec_version: 1, optimize: { max: "quality" } })
    .catch((error: unknown) => error);
  await vi.advanceTimersByTimeAsync(DECIDE_TIMEOUT_MS + 1);
  const error = await pending;
  expect(error).toBeInstanceOf(DecideApiError);
  expect((error as DecideApiError).code).toBe("timeout");
});

it("reports a response whose body stalls, not only one that never starts", async () => {
  vi.useFakeTimers();
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: () => new Promise(() => {}),
    }),
  );
  const pending = hostedEngine
    .decide({ spec_version: 1, optimize: { max: "quality" } })
    .catch((error: unknown) => error);
  await vi.advanceTimersByTimeAsync(DECIDE_TIMEOUT_MS + 1);
  const error = await pending;
  expect(error).toBeInstanceOf(DecideApiError);
  expect((error as DecideApiError).code).toBe("timeout");
});

// The page's own 20-second watchdog, which fires before this 30-second one,
// is tested in burst.test.tsx.

it("says there is no snapshot yet when the vocabulary is not published", async () => {
  const fetch = routeFetch({
    vocabulary: () => new Response("Not found", { status: 404 }),
    decide: () => json(fixture),
  });
  vi.stubGlobal("fetch", fetch);
  render(<App />);
  const alert = await screen.findByRole("alert");
  expect(alert).toHaveTextContent("No snapshot yet.");
  noSkeleton();
  expect(screen.queryByText("Coding agent on a budget")).not.toBeInTheDocument();
  fireEvent.click(within(alert).getByRole("button", { name: "Retry" }));
  await waitFor(() => expect(fetch).toHaveBeenCalledTimes(2));
});
