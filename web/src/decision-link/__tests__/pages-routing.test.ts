import { readFile } from "node:fs/promises";
import { expect, it } from "vitest";

it("the decision shell prevents referrers and indexing before loading its script", async () => {
  const shell = await readFile("decision.html", "utf8");
  expect(shell).toContain('name="referrer" content="no-referrer"');
  expect(shell).toContain('name="robots" content="noindex, nofollow, noarchive"');
  expect(shell).not.toMatch(/token=|og:|canonical|cloudflareinsights|analytics/);
});
