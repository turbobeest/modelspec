import { expect, it } from "vitest";
import { decisionSummary, defaultDecideRequest } from "../src/server";
import { asToolResult } from "../src/origin";
// Generated from the public catalogue. Pytest also measures fresh answers from the real Worker.
import fixture from "./fixtures/decide-budget.json";

it("keeps real public Worker answers within MCP and drill-down budgets", () => {
  expect(defaultDecideRequest({
    spec_version: 1,
    capabilities: { software_engineering: "required" },
    optimize: { max: "software_engineering" },
  })).toEqual(fixture.request);
  for (const [index, body] of [fixture.default, fixture.drill_down].entries()) {
    const result = asToolResult({ origin: "https://api.modelspec.dev/v1/decide", status: 200, body });
    // The tool sends the origin envelope plus the short summary as a second text block.
    const bytes = Buffer.byteLength(result.content[0].text, "utf8")
      + Buffer.byteLength(decisionSummary(body), "utf8");
    expect(bytes / 4).toBeLessThanOrEqual(index === 0 ? 3000 : 2000);
  }
});
