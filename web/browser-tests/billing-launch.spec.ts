import { expect, test, type Route } from "@playwright/test";
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { z } from "zod";

const replay = fileURLToPath(new URL("../../tests/replay_billing_launch.py", import.meta.url));
const outcomeSchema = z.array(z.object({
  status: z.number().int(),
  body: z.string(),
  headers: z.record(z.string(), z.string()),
  produced: z.number().int(),
}));

for (const humanGate of [false, true]) {
  const lookupTest = humanGate && process.env.VITE_HUMAN_GATE_ENABLED !== "true" ? test.skip : test;
  lookupTest(`billing launch completes a keyless lookup with human gate ${humanGate}`, async ({ page, baseURL }) => {
    const calls: { path: string; method: string; headers: Record<string, string>; body: string | null }[] = [];
    const statuses: number[] = [];
    let produced = 0;
    async function worker(route: Route, path: string) {
      const request = route.request();
      const headers = await request.allHeaders();
      expect(headers.authorization).toBeUndefined();
      expect(headers["x-api-key"]).toBeUndefined();
      if (path !== "/v1/vocabulary") expect(headers.origin).toBe("https://modelspec.dev");
      calls.push({ path, method: request.method(), headers, body: request.postData() });
      const outcomes = outcomeSchema.parse(JSON.parse(execFileSync(
        process.env.MODELSPEC_TEST_PYTHON ?? "python3", [replay],
        { input: JSON.stringify({ human_gate: humanGate, calls }), encoding: "utf8" },
      )));
      const outcome = outcomes.at(-1);
      if (!outcome) throw new Error("Worker replay returned no response");
      produced = outcome.produced;
      if (path === "/v1/decide" && request.method() === "POST") statuses.push(outcome.status);
      await route.fulfill({ status: outcome.status, body: outcome.body, headers: outcome.headers });
    }
    // Serve the built artifact at the real allowed origin, with no live calls.
    await page.route("https://modelspec.dev/**", async (route) => {
      if (!baseURL) throw new Error("built-page preview URL is required");
      const target = new URL(route.request().url());
      const response = await route.fetch({ url: new URL(target.pathname + target.search, baseURL).href });
      await route.fulfill({ response });
    });
    await page.route(/\/(?:api\/decision\/vocabulary\.json|v1\/vocabulary)(?:\?.*)?$/, (route) =>
      worker(route, "/v1/vocabulary"));
    await page.route("https://api.modelspec.dev/v1/**", (route) =>
      worker(route, new URL(route.request().url()).pathname));
    await page.route("https://challenges.cloudflare.com/**", (route) => route.fulfill({
      contentType: "application/javascript",
      body: `window.turnstile = {
        render(container, options) { options.callback("browser-test-token"); return "test-widget"; },
        remove() {}
      };`,
    }));
    await page.goto("https://modelspec.dev/decide.html");
    if (humanGate) {
      const lookup = page.getByRole("button", { name: "Look up this decision" });
      await expect(lookup).toBeEnabled();
      expect(statuses).toEqual([]);
      await lookup.click();
    }
    await expect(page.getByLabel("Facet board answer")).toBeVisible();
    await expect.poll(() => statuses.length).toBeGreaterThanOrEqual(3);
    expect(statuses.every((status) => status === 200)).toBe(true);
    expect(produced).toBe(statuses.length);
    const decisions = calls.filter((call) => call.path === "/v1/decide" && call.method === "POST");
    expect(new Set(decisions.map((call) => call.headers["x-modelspec-intent"])).size).toBe(1);
    expect(decisions[0].headers["x-modelspec-turnstile"]).toBe(humanGate ? "browser-test-token" : undefined);
  });
}
