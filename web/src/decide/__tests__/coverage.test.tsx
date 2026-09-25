import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import fixtureJson from "../__fixtures__/full-decision.json";
import App from "../App";
import { decisionSchema } from "../adapter/contract";
import { registerProviders, renderContractCondition } from "../adapter/condition-label";
import { encodeSpec } from "../state/spec";
import { mapDecisionToViewModel } from "../adapter/view-model";
import { lineupCoverage } from "../vocabulary/coverage";
import { EMPTY_DECISIONS, EMPTY_SPECS } from "./empty-specs";
import { json, realVocabulary, routeFetch, sentSpecs } from "./vocab-fixtures";

const answered = decisionSchema.parse(fixtureJson);

describe("what the verified lineup covers, when a decision is empty", () => {
  it("says there are no speech models yet, from the counts (Q20)", () => {
    const c = lineupCoverage(EMPTY_DECISIONS.q20, EMPTY_SPECS.q20, realVocabulary)!;
    expect(c.needed).toEqual([
      "Type: transcriber — the lineup has no speech recognition models yet",
    ]);
    expect(c.covers).toContain("32 models as of 2026-09-25, 29 with verified evidence");
    expect(c.covers).toContain("25 text generators");
    expect(c.covers).toContain("4 embedding models");
    expect(c.covers).toContain("No speech recognition models yet.");
    expect(c.relax).toEqual([{ index: 0, label: "Type: transcriber" }]);
  });

  it("says hardware fit is not recorded, and how many may qualify (Q17)", () => {
    const c = lineupCoverage(EMPTY_DECISIONS.q17, EMPTY_SPECS.q17, realVocabulary)!;
    expect(c.needed).toEqual([
      "Fits hardware: nvidia rtx 4090 — not recorded for any of the 32 models yet; " +
        "6 models may qualify once it is recorded",
    ]);
    expect(c.covers).toContain("25 text generators with verified software engineering evidence");
    expect(c.relax.map((r) => r.index)).toEqual([3]);
  });

  it("gives the closest value the lineup has for a limit nothing meets (Q10)", () => {
    const c = lineupCoverage(EMPTY_DECISIONS.q10, EMPTY_SPECS.q10, realVocabulary)!;
    const closest = Math.min(
      ...EMPTY_DECISIONS.q10.eliminated.models
        .filter((m) => m.condition === "offering.price.input <= 0.2")
        .map((m) => Number(m.value)),
    );
    expect(c.needed[0]).toMatch(/^Input price: at most \$0\.2 \/ 1M tokens — none of the \d+ remaining models; the closest is /);
    expect(c.needed[0]).toContain(`$${closest} / 1M tokens`);
    expect(c.needed[0]).toContain("1 model may qualify");
    // The engine's relaxation, whatever it is, is offered as returned.
    expect(c.relax).toEqual([{ index: 0, label: "Type: text generator" }]);
  });

  it("is not shown for an answered decision, or without published coverage", () => {
    expect(lineupCoverage(answered, EMPTY_SPECS.q10, realVocabulary)).toBeNull();
    expect(
      lineupCoverage(EMPTY_DECISIONS.q20, EMPTY_SPECS.q20, { ...realVocabulary, coverage: null }),
    ).toBeNull();
  });
});

describe("provider display names", () => {
  it("names the provider as the registry does wherever an offering appears", () => {
    const view = mapDecisionToViewModel(EMPTY_DECISIONS.q17, EMPTY_SPECS.q17, {
      axis: "task$",
      dismissed: [],
      providers: realVocabulary.providers,
    });
    const shown = view.explanation.may.flatMap((row) => row.m.offerings.map((o) => o.provider));
    expect(shown).toContain("Z.ai API");
    expect(shown).not.toContain("zai");
  });

  it("names providers in condition labels", () => {
    registerProviders(realVocabulary.providers);
    expect(renderContractCondition("offering.provider in {anthropic, zai}")).toBe(
      "Provider: Anthropic API or Z.ai API",
    );
  });
});

describe("the empty-result panel on the page", () => {
  beforeEach(() => history.replaceState(null, "", "/"));
  afterEach(() => vi.unstubAllGlobals());

  it("shows the panel above may-qualify and relaxes in one click (Q20)", async () => {
    const fetch = routeFetch({
      vocabulary: () => json(realVocabulary),
      decide: (init) =>
        JSON.parse(String(init?.body)).where.includes("model.class = transcriber")
          ? json(EMPTY_DECISIONS.q20)
          : json(answered),
    });
    vi.stubGlobal("fetch", fetch);
    history.replaceState(null, "", "/" + encodeSpec(EMPTY_SPECS.q20, "task$"));
    render(<App />);

    const panel = await screen.findByRole("region", { name: "Lineup coverage" });
    expect(panel).toHaveTextContent("What this question needed");
    expect(panel).toHaveTextContent("the lineup has no speech recognition models yet");
    expect(panel).toHaveTextContent("32 models as of 2026-09-25");
    expect(panel).not.toHaveTextContent(/sorry|unfortunately|apolog/i);
    const canvas = screen.getByRole("region", { name: "Trade-off canvas" });
    expect(panel.compareDocumentPosition(canvas) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();

    fireEvent.click(within(panel).getByRole("button", { name: /Type: transcriber/ }));
    await waitFor(() => {
      const last = sentSpecs(fetch).at(-1);
      expect(last.where).not.toContain("model.class = transcriber");
      expect(last.where).toContain("model.lifecycle = active");
    });
    await waitFor(() =>
      expect(screen.queryByRole("region", { name: "Lineup coverage" })).not.toBeInTheDocument(),
    );
  });
});
