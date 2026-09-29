// MODEL-205: the page loads a vocabulary carrying `vendors` the way it loads
// the live one. The fixture is `build_vocabulary`'s own output, pinned by
// tests/test_decide_page_fixtures.py, so a schema that refused the new key
// (as #361's strict parse refused a new field) fails here, not on /decide.
import { afterEach, expect, it, vi } from "vitest";
import vendorVocabulary from "../__fixtures__/vocabulary-vendors.json";
import { loadVocabulary } from "../vocabulary";

afterEach(() => vi.unstubAllGlobals());

it("parses the engine's vocabulary with its vendors and a vendor's plan", async () => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify(vendorVocabulary))));

  const vocabulary = await loadVocabulary();

  expect(vocabulary.vendors).toMatchObject({ cursor: "Cursor", "github-copilot": "GitHub Copilot" });
  expect(vocabulary.providers).not.toHaveProperty("cursor");
  expect(vocabulary.estate.providers).not.toContain("cursor");
  expect(vocabulary.estate.plans).toContainEqual(expect.objectContaining({
    id: "cursor/subscription/pro", provider: "cursor", name: "Cursor Pro",
    surfaces: ["coding_tool:cursor", "coding_tool:cursor-agent"],
  }));
});
