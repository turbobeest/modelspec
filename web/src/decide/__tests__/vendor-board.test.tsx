import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import anyJson from "../__fixtures__/plans-any-full.json";
import vendorCodingJson from "../__fixtures__/plans-vendor-coding-full.json";
import { DesignedApp } from "../App";
import type { Vocabulary } from "../vocabulary";
import { planVocabulary } from "./plan-vocabulary";
import { json, routeFetch } from "./vocab-fixtures";

// MODEL-205: a subscription-only vendor. Cursor sells plans, never pay-per-use,
// so the board offers Cursor Pro as a plan, never as an account, and a Cursor
// Pro holder in a coding tool reaches the lab models it covers through the plan.
const CURSOR_PRO = "cursor/subscription/pro";

const vocabulary: Vocabulary = {
  ...planVocabulary,
  vendors: { cursor: "Cursor" },
  estate: {
    ...planVocabulary.estate,
    plans: [
      ...planVocabulary.estate.plans,
      { id: CURSOR_PRO, provider: "cursor", name: "Cursor Pro",
        price: { amount: 20, currency: "USD", period: "monthly" },
        surfaces: ["coding_tool:cursor", "coding_tool:cursor-agent"] },
    ],
  },
};

function engine() {
  return routeFetch({
    vocabulary: () => json(vocabulary),
    decide: (init) => json(JSON.parse(String(init?.body)).access === "coding_tool" ? vendorCodingJson : anyJson),
  });
}

const accessRadio = (label: string) =>
  within(screen.getByRole("radiogroup", { name: "How will you use it?" }))
    .getByRole("radio", { name: new RegExp(`^${label}`) });

beforeEach(() => {
  history.replaceState(null, "", "/decide/");
  localStorage.clear();
});
afterEach(() => vi.unstubAllGlobals());

it("offers Cursor Pro as a plan sold by Cursor, and never Cursor as a pay-per-use account", async () => {
  vi.stubGlobal("fetch", engine());
  render(<DesignedApp />);
  await screen.findByLabelText("Facet board answer");

  const plans = screen.getByLabelText("Add plan");
  const cursor = within(plans).getByRole("group", { name: "Cursor" });
  expect(within(cursor).getByRole("option", { name: "Cursor Pro" })).toHaveValue(CURSOR_PRO);
  const accounts = within(screen.getByLabelText("Add provider")).getAllByRole("option");
  expect(accounts.map((option) => option.textContent)).not.toContain("Cursor");
});

it("in a coding tool, a Cursor Pro holder reaches Claude Opus through the plan, not a Cursor offering", async () => {
  localStorage.setItem("modelspec-estate-v1", JSON.stringify({ providers: [], plans: [CURSOR_PRO], hardware: [] }));
  vi.stubGlobal("fetch", engine());
  render(<DesignedApp />);
  await screen.findByLabelText("Facet board answer");
  fireEvent.click(accessRadio("In a coding tool"));

  await waitFor(() => expect(screen.getAllByText("Cursor Pro · monthly plan").length).toBeGreaterThan(0));
  expect(screen.getByRole("button", { name: "Remove Cursor Pro" })).toBeInTheDocument();
  const answer = screen.getByLabelText("Facet board answer").closest<HTMLElement>(".board-answer")!;
  const names = [...answer.querySelectorAll(".route-name")].map((name) => name.textContent);
  expect(names).toContain("Cursor Pro · monthly plan");
  expect(names.some((name) => /^Cursor · pay per use/.test(name ?? ""))).toBe(false);
  expect(screen.getAllByText("Cursor Pro · monthly plan")[0]).toHaveAccessibleDescription(
    "A flat fee each month. Works in Cursor and Cursor Agent; not your own software.",
  );
  const held = await waitFor(() => {
    const section = [...document.querySelectorAll(".answer-lists > section")]
      .find((item) => item.querySelector("strong")?.textContent === "With what you have");
    expect(section).toBeDefined();
    return section as HTMLElement;
  });
  const opus = within(held).getByRole("list", { name: "Routes to Claude Opus 5.5" });
  expect(within(opus).getAllByRole("listitem").map((item) => item.querySelector(".route-name")?.textContent))
    .toEqual(["Cursor Pro · monthly plan"]);
  expect(opus).toHaveTextContent("included in your plan");
});
