// The first load after a deploy meets a cold Worker (MODEL-153). The page asks
// for the summary alone, and only then for the full explanation and the
// next-question probes; whatever goes wrong with the main decision ends in a
// message with Retry, within 20 seconds at most, and a failed probe costs only
// its own count.
import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import summaryJson from "../__fixtures__/compact-summary.json";
import fixtureJson from "../__fixtures__/full-decision.json";
import App, { DECISION_WATCHDOG_MS } from "../App";
import { decisionSchema } from "../adapter";
import { json, routeFetch, smallVocabulary } from "./vocab-fixtures";

const fixture = decisionSchema.parse(fixtureJson);
const TASK = "Refactor a large Rust codebase, precision matters";

beforeEach(() => history.replaceState(null, "", "/"));
afterEach(() => {
  vi.unstubAllGlobals();
  vi.useRealTimers();
});

const explainOf = (init: RequestInit | undefined) => JSON.parse(String(init?.body)).explain;
const posts = (fetch: ReturnType<typeof routeFetch>) =>
  fetch.mock.calls
    .filter(([, init]) => (init as RequestInit | undefined)?.method === "POST")
    .map(([, init]) => explainOf(init as RequestInit));

async function findModels() {
  render(<App />);
  await screen.findByText("Coding agent on a budget");
  fireEvent.change(screen.getByLabelText("Describe your task"), { target: { value: TASK } });
  fireEvent.click(screen.getByRole("button", { name: /Find models/ }));
}

const noSkeleton = () =>
  expect(document.querySelector('[aria-busy="true"]')).not.toBeInTheDocument();

function held() {
  let release: () => void = () => {};
  const gate = new Promise<void>((resolve) => (release = resolve));
  return { gate, release: () => release() };
}

it("sends the full explanation and the probes only after the summary answers", async () => {
  const summary = held();
  const fetch = routeFetch({
    decide: async (init) => {
      if (explainOf(init) === "summary") {
        await summary.gate;
        return json(summaryJson);
      }
      return json(explainOf(init) === "full" ? fixture : summaryJson);
    },
  });
  vi.stubGlobal("fetch", fetch);
  await findModels();

  await waitFor(() => expect(posts(fetch)).toEqual(["summary"]));
  await new Promise((resolve) => setTimeout(resolve, 800));
  expect(posts(fetch)).toEqual(["summary"]);

  summary.release();
  await waitFor(() => expect(posts(fetch)).toContain("none"));
  expect(posts(fetch).slice(0, 2)).toEqual(["summary", "full"]);
});

it("an edit sends no probe until the edited spec's summary answers", async () => {
  let hold: ReturnType<typeof held> | null = null;
  const fetch = routeFetch({
    decide: async (init) => {
      if (explainOf(init) === "summary" && hold) {
        await hold.gate;
      }
      return json(explainOf(init) === "full" ? fixture : summaryJson);
    },
  });
  vi.stubGlobal("fetch", fetch);
  await findModels();
  expect(await screen.findByRole("region", { name: "Trade-off canvas" })).toBeInTheDocument();
  await waitFor(() => expect(screen.queryByText("checking…")).not.toBeInTheDocument());

  hold = held();
  const before = posts(fetch).length;
  fireEvent.click(screen.getAllByRole("button", { name: /Remove condition:/ })[0]);
  await waitFor(() => expect(posts(fetch).slice(before)).toEqual(["summary"]));
  await new Promise((resolve) => setTimeout(resolve, 800));
  expect(posts(fetch).slice(before)).toEqual(["summary"]);

  hold.release();
  await waitFor(() => expect(posts(fetch).slice(before)).toContain("none"));
});

// Browsers reject with a DOMException, which is an Error there (not in jsdom).
const strayAbort = () => Object.assign(new Error("The operation was aborted."), { name: "AbortError" });
const hang = () => new Promise<Response>(() => {});

it.each<[string, () => Response | Promise<Response>]>([
  ["a fetch that rejects with TypeError (how a CORS-less 1102 surfaces)", () => {
    throw new TypeError("Failed to fetch");
  }],
  ["a non-JSON 503 (the 1102 page itself)", () => new Response("error code: 1102", { status: 503 })],
  ["a 500", () => json({ error: { code: "internal", message: "boom" } }, 500)],
  ["a 403", () => json({ error: { code: "forbidden", message: "no" } }, 403)],
  ["a 400 without issues", () => json({ error: { code: "invalid_request", message: "bad body" } }, 400)],
  ["an AbortError the page did not ask for", () => {
    throw strayAbort();
  }],
])("ends %s in a message with Retry", async (_name, failure) => {
  let calls = 0;
  vi.stubGlobal(
    "fetch",
    routeFetch({ decide: () => (calls++ === 0 ? failure() : json(fixture)) }),
  );
  await findModels();

  const alert = await screen.findByRole("alert");
  noSkeleton();
  fireEvent.click(within(alert).getByRole("button", { name: "Retry" }));
  expect(await screen.findByRole("region", { name: "Trade-off canvas" })).toBeInTheDocument();
});

it.each<[string, (init: RequestInit | undefined) => Response | Promise<Response>]>([
  ["a request that never answers", hang],
  [
    "a response whose body never finishes",
    () =>
      ({
        ok: true,
        status: 200,
        headers: new Headers(),
        json: hang,
        text: hang,
      }) as unknown as Response,
  ],
])("shows Retry within 20 seconds for %s", async (_name, stuck) => {
  vi.useFakeTimers({ shouldAdvanceTime: true });
  vi.stubGlobal("fetch", routeFetch({ decide: stuck }));
  await findModels();
  await vi.advanceTimersByTimeAsync(DECISION_WATCHDOG_MS + 500);
  const alert = await screen.findByRole("alert");
  expect(alert).toHaveTextContent("The decision service is taking too long.");
  expect(alert).toHaveTextContent("did not answer within 20 seconds");
  expect(within(alert).getByRole("button", { name: "Retry" })).toBeInTheDocument();
  noSkeleton();
});

it("shows Retry when the vocabulary reload after a 409 never answers", async () => {
  vi.useFakeTimers({ shouldAdvanceTime: true });
  let vocabularies = 0;
  vi.stubGlobal(
    "fetch",
    routeFetch({
      vocabulary: () => (vocabularies++ === 0 ? json(smallVocabulary) : hang()),
      decide: () =>
        json(
          {
            error: {
              code: "snapshot_changed",
              message: "reload the vocabulary and retry",
              requested: smallVocabulary.snapshot,
              current: "snap_next",
            },
          },
          409,
        ),
    }),
  );
  await findModels();
  await vi.advanceTimersByTimeAsync(DECISION_WATCHDOG_MS + 500);
  const alert = await screen.findByRole("alert");
  expect(within(alert).getByRole("button", { name: "Retry" })).toBeInTheDocument();
  noSkeleton();
});

it.each<[string, () => Response | Promise<Response>]>([
  ["TypeError", () => {
    throw new TypeError("Failed to fetch");
  }],
  ["a 400", () => json({ error: { code: "invalid_spec", message: "no", issues: [] } }, 400)],
  ["a stray AbortError", () => {
    throw strayAbort();
  }],
])("a probe that fails with %s costs only its own count", async (_name, failure) => {
  let probes = 0;
  vi.stubGlobal(
    "fetch",
    routeFetch({
      decide: (init) => {
        const explain = explainOf(init);
        if (explain === "none" && probes++ === 0) return failure();
        return json(explain === "full" ? fixture : summaryJson);
      },
    }),
  );
  await findModels();
  expect(await screen.findByRole("region", { name: "Trade-off canvas" })).toBeInTheDocument();
  await waitFor(() => expect(screen.getByText("count unavailable")).toBeInTheDocument());
  expect(screen.queryByText("checking…")).not.toBeInTheDocument();
  expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  noSkeleton();
});

it("Find models before the vocabulary has loaded answers once it arrives", async () => {
  const vocabulary = held();
  const fetch = routeFetch({
    vocabulary: async () => {
      await vocabulary.gate;
      return json(smallVocabulary);
    },
    decide: (init) => json(explainOf(init) === "full" ? fixture : summaryJson),
  });
  vi.stubGlobal("fetch", fetch);
  render(<App />);
  fireEvent.change(screen.getByLabelText("Describe your task"), { target: { value: TASK } });
  fireEvent.click(screen.getByRole("button", { name: /Find models/ }));
  expect(await screen.findByText(/Loading what the current snapshot can answer/)).toBeInTheDocument();

  vocabulary.release();
  expect(await screen.findByRole("region", { name: "Trade-off canvas" })).toBeInTheDocument();
  expect(posts(fetch)[0]).toBe("summary");
});
