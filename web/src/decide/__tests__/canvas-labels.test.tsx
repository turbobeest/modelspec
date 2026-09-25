// Every frontier, shortlist and selected point on the canvas carries its
// name; every other point is named while hovered or focused (MODEL-153).
import { fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import fixtureJson from "../__fixtures__/full-decision.json";
import App from "../App";
import type { Spec } from "../engine/types";
import { encodeSpec } from "../state/spec";
import { json, routeFetch, smallVocabulary } from "./vocab-fixtures";

beforeEach(() => history.replaceState(null, "", "/"));
afterEach(() => vi.unstubAllGlobals());

const SPEC: Spec = {
  task: "Quality per dollar",
  tokIn: 40000,
  tokOut: 4000,
  bench: "quality",
  w: { cap: 0.7, cost: 0.3, speed: 0 },
  conds: [{ f: "type", v: "llm" }, { f: "active" }],
};

/**
 * The fixture plus a dominated fifth model: as good as none, as dear as the
 * dearest, so it is on no frontier and no shortlist card.
 */
function withDominated() {
  const raw = structuredClone(fixtureJson);
  const rename = <T extends { offering: { model: string } }>(row: T, rank?: number): T => {
    const copy = structuredClone(row);
    copy.offering.model = "lab/epsilon";
    for (const group of (copy as unknown as { evidence: { items: { value: number }[] }[] }).evidence)
      for (const item of group.items) item.value = 50;
    return rank === undefined ? copy : { ...copy, rank };
  };
  const alpha = <T extends { offering: { model: string } }>(rows: T[]) =>
    rows.find((row) => row.offering.model === "lab/alpha")!;
  raw.results.push(rename(alpha(raw.results), raw.results.length + 1));
  raw.top.push(rename(alpha(raw.top)));
  return raw;
}

async function canvas() {
  vi.stubGlobal(
    "fetch",
    routeFetch({ vocabulary: () => json(smallVocabulary), decide: () => json(withDominated()) }),
  );
  history.replaceState(null, "", "/" + encodeSpec(SPEC, "task$"));
  render(<App />);
  return screen.findByRole("region", { name: "Trade-off canvas" });
}

const pointName = (point: Element) => point.getAttribute("aria-label")!.split(",")[0];
const labelled = (region: HTMLElement) =>
  [...region.querySelectorAll(".point-label")].map((l) => l.textContent!.split(" · ")[0]);

it("labels every frontier, shortlist and selected point", async () => {
  const region = await canvas();
  const shortlist = screen.getByText("Shortlist").closest("section")!;
  const named = new Set(
    [...shortlist.querySelectorAll(".model-name")].map((n) => n.textContent!),
  );
  const selected = region.querySelector(".point.selected");
  expect(selected).not.toBeNull();
  named.add(pointName(selected!));
  const onPlot = new Set([...region.querySelectorAll(".point")].map(pointName));
  const shown = new Set(labelled(region));
  for (const name of named) if (onPlot.has(name)) expect(shown, name).toContain(name);
});

it("names any other point while it is hovered or focused", async () => {
  const region = await canvas();
  const bare = [...region.querySelectorAll<HTMLElement>(".point")].filter(
    (p) => !labelled(region).includes(pointName(p)),
  );
  expect(bare.length).toBeGreaterThan(0);
  for (const point of bare) {
    fireEvent.focus(point);
    expect(labelled(region)).toContain(pointName(point));
    expect(within(region).getByRole("tooltip")).toHaveTextContent(pointName(point));
    fireEvent.blur(point);
    expect(labelled(region)).not.toContain(pointName(point));
  }
});
