// MODEL-294: every facet the test vocabulary offers, set to Must and then to
// Prefer on a live board, must leave the answer drawable. The decision stays
// the production answer whose mixed capability intervals blanked the page;
// each click re-maps it against the new spec at once, so the sweep needs no
// round trip per facet. The whole-board render after each click needs a longer
// budget than one interaction on a loaded parallel runner.
import { fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import inputPricePreferJson from "../__fixtures__/live-input-price-prefer-full.json";
import { DesignedApp } from "../App";
import { groupFacets } from "../facet-board/model";
import { json, realVocabulary, routeFetch } from "./vocab-fixtures";

beforeEach(() => history.replaceState(null, "", "/decide/"));
afterEach(() => {
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

// Selectors, not role queries: role queries over the whole board cost seconds here.
const FAILURE = '[role="alert"][aria-label="The answer could not be shown"]';
function setGroupOpen(name: string, open: boolean) {
  const summary = [...document.querySelectorAll<HTMLElement>("button[aria-expanded]")]
    .find((button) => button.textContent?.startsWith(name));
  if (!summary) throw new Error(`no ${name} group on the board`);
  if ((summary.getAttribute("aria-expanded") === "true") !== open) fireEvent.click(summary);
}

it("draws the answer for Must and then Prefer on every facet", { timeout: 60_000 }, async () => {
  const errors: unknown[][] = [];
  vi.spyOn(console, "error").mockImplementation((...args) => void errors.push(args));
  vi.stubGlobal("fetch", routeFetch({
    vocabulary: () => json(realVocabulary),
    decide: () => json(inputPricePreferJson),
  }));
  render(<DesignedApp />);
  await screen.findByRole("region", { name: "Why this model" });

  const { groups } = groupFacets(realVocabulary);
  const preferred: string[] = [];
  for (const group of groups) {
    setGroupOpen(group.name, true);
    for (const facet of group.facets) {
      const row = document.querySelector<HTMLElement>(`.facet-row[data-facet="${facet.id}"]`);
      if (!row) throw new Error(`${facet.id} is not on the board`);
      for (const mode of ["Must", "Prefer", "Doesn't matter"]) {
        const control = within(row).queryByLabelText(mode);
        if (!control) continue;
        fireEvent.click(control);
        if (mode === "Prefer") preferred.push(facet.id);
        expect(document.querySelector(FAILURE), `${mode} on ${facet.id}`).toBeNull();
        expect(errors, `${mode} on ${facet.id}`).toEqual([]);
      }
    }
    setGroupOpen(group.name, false);
  }
  expect(preferred).toEqual(expect.arrayContaining(["offering.price.input", "offering.cost_per_task"]));
});
