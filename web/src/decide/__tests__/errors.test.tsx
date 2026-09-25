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
        // The full request and its one summary retry both fail to connect.
        if (calls++ < 2) throw new TypeError("Failed to fetch");
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

it.each([
  ["a non-JSON 503 (Cloudflare 1102)", () => new Response("error code: 1102", { status: 503 })],
  [
    "a network failure (a limit page carries no CORS header)",
    () => {
      throw new TypeError("Failed to fetch");
    },
  ],
])("retries %s once with summary and says the service hit a limit", async (_name, limited) => {
  const fetch = routeFetch({
    decide: (init) => (explainOf(init) === "full" ? limited() : json(summaryJson)),
  });
  vi.stubGlobal("fetch", fetch);
  await findModels();

  const notice = await screen.findByText(/The decision service hit a limit on this request/);
  expect(notice.closest('[role="status"]')).not.toBeNull();
  expect(screen.queryByText("Couldn't reach the decision service.")).not.toBeInTheDocument();
  expect(await screen.findByRole("region", { name: "Trade-off canvas" })).toBeInTheDocument();
  const why = screen.getByRole("region", { name: "Why this model" });
  expect(why).toHaveTextContent("Detailed explanation unavailable for this request");
  const decides = fetch.mock.calls.filter(([, init]) => init?.method === "POST");
  expect(decides.slice(0, 2).map(([, init]) => explainOf(init))).toEqual(["full", "summary"]);
  noSkeleton();
});

it("says the service hit a limit, not that it is unreachable, when the retry fails too", async () => {
  vi.stubGlobal(
    "fetch",
    routeFetch({
      decide: (init) => {
        if (explainOf(init) === "full") return new Response("error code: 1102", { status: 503 });
        throw new TypeError("Failed to fetch");
      },
    }),
  );
  await findModels();
  const alert = await screen.findByRole("alert");
  expect(alert).toHaveTextContent("The decision service hit a limit on this request.");
  expect(alert).not.toHaveTextContent("No snapshot yet");
  expect(within(alert).getByRole("button", { name: "Retry" })).toBeInTheDocument();
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

it("shows a timeout in the page with Retry", async () => {
  vi.useFakeTimers({ shouldAdvanceTime: true });
  vi.stubGlobal(
    "fetch",
    routeFetch({
      decide: (init) =>
        new Promise<Response>((_resolve, reject) =>
          init?.signal?.addEventListener("abort", () =>
            reject(new DOMException("Aborted", "AbortError")),
          ),
        ),
    }),
  );
  await findModels();
  await vi.advanceTimersByTimeAsync(DECIDE_TIMEOUT_MS + 1000);
  const alert = await screen.findByRole("alert");
  expect(alert).toHaveTextContent("The decision service is taking too long.");
  expect(alert).toHaveTextContent("did not answer within 30 seconds");
  expect(within(alert).getByRole("button", { name: "Retry" })).toBeInTheDocument();
  noSkeleton();
});

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
