// One action asks its plot question once. The full explanation replaces the
// summary while the plot is still in flight; that must not abort the plot and
// send it again under the same intent (MODEL-292 follow-up: a second, identical
// plot request spent the visitor's per-intent allowance and failed the
// visit-gate browser test whenever the full answer landed first).
import { render, screen, waitFor } from "@testing-library/react";
import { afterEach, expect, it, vi } from "vitest";
import liveEmptyBoardJson from "../__fixtures__/live-empty-board-full.json";
import { DesignedApp } from "../App";
import { DECIDE_ENDPOINT } from "../adapter/hosted";
import { json, realVocabulary, routeFetch } from "./vocab-fixtures";

afterEach(() => {
  vi.unstubAllGlobals();
});

it("keeps an in-flight plot when the full explanation lands first, and sends it once", async () => {
  const held: (() => void)[] = [];
  const fetch = routeFetch({
    vocabulary: () => json(realVocabulary),
    // The first request (the summary) answers at once; every later one waits
    // until the test releases it, in the order the test chooses.
    decide: () => held.length === 0 && fetch.mock.calls.filter(([url]) => url === DECIDE_ENDPOINT).length === 1
      ? json(liveEmptyBoardJson)
      : new Promise<Response>((resolve) => held.push(() => resolve(json(liveEmptyBoardJson)))),
  });
  vi.stubGlobal("fetch", fetch);
  render(<DesignedApp />);
  const decides = () => fetch.mock.calls.filter(([url]) => url === DECIDE_ENDPOINT);
  // Summary, then the full explanation and the plot, both held.
  await waitFor(() => expect(decides()).toHaveLength(3));
  const bodies = decides().map(([, init]) => String((init as RequestInit).body));
  const plot = bodies.findIndex((body, index) => index > 0 && body !== bodies[1]);
  expect(plot).toBe(2);
  // Answer the full explanation first; the plot is still waiting.
  held[0]();
  await screen.findByLabelText("Facet board answer");
  await new Promise((resolve) => setTimeout(resolve, 50));
  held[1]();
  await new Promise((resolve) => setTimeout(resolve, 50));
  const sent = decides().map(([, init]) => String((init as RequestInit).body));
  expect(sent).toHaveLength(3);
  expect(sent.filter((body) => body === bodies[plot])).toHaveLength(1);
  const signal = (decides()[plot][1] as RequestInit).signal;
  expect(signal?.aborted).toBe(false);
});
