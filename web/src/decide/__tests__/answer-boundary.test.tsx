// MODEL-294: one component's exception used to take the whole page down.
// The answer area sits behind an error boundary: the facets stay usable, and
// Reset returns to the default board.
import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import fixtureJson from "../__fixtures__/full-decision.json";
import { DesignedApp } from "../App";
import { capabilityRow } from "./board-helpers";
import { json, routeFetch, sentSpecs } from "./vocab-fixtures";

const broken = vi.hoisted(() => ({ why: false, rankedAnswer: false }));

vi.mock("../components/Why", async (importOriginal) => {
  const real = await importOriginal<typeof import("../components/Why")>();
  return {
    Why: (props: Parameters<typeof real.Why>[0]) => {
      if (broken.why) throw new TypeError("Why failed to render");
      return <real.Why {...props} />;
    },
  };
});
vi.mock("../facet-board/RankedAnswer", async (importOriginal) => {
  const real = await importOriginal<typeof import("../facet-board/RankedAnswer")>();
  return {
    ...real,
    RankedAnswer: (props: Parameters<typeof real.RankedAnswer>[0]) => {
      if (broken.rankedAnswer) throw new TypeError("RankedAnswer failed to render");
      return <real.RankedAnswer {...props} />;
    },
  };
});

const failure = () => screen.queryAllByRole("alert", { name: "The answer could not be shown" });

beforeEach(() => {
  history.replaceState(null, "", "/decide/");
  // React reports every caught render error on console.error; keep the run quiet.
  vi.spyOn(console, "error").mockImplementation(() => undefined);
});
afterEach(() => {
  broken.why = false;
  broken.rankedAnswer = false;
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

it("keeps the facets usable when the Why panel throws, and Reset returns to the default board", async () => {
  const fetch = routeFetch({ decide: () => json(fixtureJson) });
  vi.stubGlobal("fetch", fetch);
  render(<DesignedApp />);
  await screen.findByLabelText("Facet board answer");
  await screen.findByRole("region", { name: "Why this model" });

  broken.why = true;
  const software = capabilityRow("Software engineering");
  fireEvent.click(within(software).getByLabelText("Prefer"));

  expect(failure()).toHaveLength(1);
  expect(failure()[0]).toHaveTextContent("The answer could not be shown.");
  expect(screen.queryByRole("region", { name: "Why this model" })).not.toBeInTheDocument();
  // The rest of the page is still there and still answers clicks.
  const facets = () => screen.getByRole("region", { name: "Facets" });
  expect(facets()).toHaveTextContent("1 set");
  fireEvent.click(within(capabilityRow("Software engineering")).getByLabelText("Must"));
  expect(within(capabilityRow("Software engineering")).getByLabelText("Must")).toBeChecked();
  expect(failure()).toHaveLength(1);

  broken.why = false;
  const requestsBeforeReset = sentSpecs(fetch).length;
  fireEvent.click(within(failure()[0]).getByRole("button", { name: "Reset" }));

  expect(facets()).toHaveTextContent("0 set");
  expect(within(capabilityRow("Software engineering")).getByLabelText("Doesn't matter")).toBeChecked();
  await waitFor(() => expect(sentSpecs(fetch).length).toBeGreaterThan(requestsBeforeReset));
  expect(sentSpecs(fetch).at(-1)).toMatchObject({ where: [], optimize: { weights: { "-offering.cost_per_task": 1 } } });
  expect(await screen.findByRole("region", { name: "Why this model" })).toBeInTheDocument();
  expect(failure()).toHaveLength(0);
});

it("keeps the facets usable when the narrowing answer throws", async () => {
  vi.stubGlobal("fetch", routeFetch({ decide: () => json(fixtureJson) }));
  render(<DesignedApp />);
  await screen.findByLabelText("Facet board answer");

  broken.rankedAnswer = true;
  fireEvent.click(within(capabilityRow("Software engineering")).getByLabelText("Prefer"));

  expect(failure()).toHaveLength(1);
  expect(screen.getByRole("region", { name: "Facets" })).toHaveTextContent("1 set");
  // The table and Why below the board still render (the canvas sits inside the narrowing since #549).
  expect(screen.getByRole("region", { name: "Why this model" })).toBeInTheDocument();

  broken.rankedAnswer = false;
  fireEvent.click(within(failure()[0]).getByRole("button", { name: "Reset" }));
  expect(screen.getByRole("region", { name: "Facets" })).toHaveTextContent("0 set");
  await waitFor(() => expect(failure()).toHaveLength(0));
});
