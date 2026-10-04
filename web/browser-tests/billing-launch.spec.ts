import { expect, test as base, type Page, type Route } from "@playwright/test";
import { spawn } from "node:child_process";
import { createInterface } from "node:readline";
import { fileURLToPath } from "node:url";
import { readFileSync } from "node:fs";
import { z } from "zod";

const replay = fileURLToPath(new URL("../../tests/replay_billing_launch.py", import.meta.url));
const vocabulary = readFileSync(new URL("../src/decide/__fixtures__/live-vocabulary.json", import.meta.url), "utf8");
const api = "https://api.modelspec.dev";
const visitPage = process.env.VITE_VISIT_GATE_ENABLED === "true";
const outcomeSchema = z.array(z.object({
  status: z.number().int(),
  body: z.string(),
  headers: z.record(z.string(), z.string()),
  produced: z.number().int(),
  visit_objects: z.number().int(),
}));
type Call = { path: string; method: string; headers: Record<string, string>; body: string | null; now: number };
type Replay = (gate: boolean, calls: Call[]) => Promise<z.infer<typeof outcomeSchema>>;

const test = base.extend<{ replayWorker: Replay }>({
  replayWorker: async ({}, use) => {
    const workerProcess = spawn(process.env.MODELSPEC_TEST_PYTHON ?? process.env.MODELSPEC_PYTHON ?? "python3", [replay, "--serve"]);
    const lines = createInterface({ input: workerProcess.stdout });
    let stderr = "";
    workerProcess.stderr.on("data", (data: Buffer) => { stderr += data.toString(); });
    let pending = Promise.resolve();
    const send: Replay = (gate, calls) => {
      const result = pending.then(() => new Promise<z.infer<typeof outcomeSchema>>((resolve, reject) => {
        const failed = () => reject(new Error(`Worker replay stopped: ${stderr}`));
        workerProcess.once("exit", failed);
        lines.once("line", (line: string) => {
          workerProcess.off("exit", failed);
          try { resolve(outcomeSchema.parse(JSON.parse(line))); } catch (error) { reject(error); }
        });
        workerProcess.stdin.write(JSON.stringify({ visit_gate: gate, human_gate: false, calls }) + "\n");
      }));
      pending = result.then(() => undefined);
      return result;
    };
    try { await use(send); } finally {
      workerProcess.stdin.end();
      lines.close();
    }
  },
});

async function builtPage(page: Page, baseURL: string | undefined, gate: boolean, replayWorker: Replay, refuseVocabulary = false) {
  const calls: Call[] = [];
  const responses: z.infer<typeof outcomeSchema> = [];
  async function worker(route: Route, path: string) {
    const request = route.request();
    const headers = await request.allHeaders();
    expect(headers.authorization).toBeUndefined();
    expect(headers["x-api-key"]).toBeUndefined();
    calls.push({ path, method: request.method(), headers, body: request.postData(),
      now: await page.evaluate(() => Date.now() / 1000) });
    const outcomes = await replayWorker(gate, [...calls]);
    const outcome = outcomes.at(-1);
    if (!outcome) throw new Error("Worker replay returned no response");
    responses.push(outcome);
    await route.fulfill({ status: outcome.status, body: outcome.body, headers: outcome.headers });
  }
  // The built artifact runs at an allowed page origin; external services stay offline.
  await page.route("https://modelspec.dev/**", async (route) => {
    if (!baseURL) throw new Error("built-page preview URL is required");
    const target = new URL(route.request().url());
    const response = await route.fetch({ url: new URL(target.pathname + target.search, baseURL).href });
    await route.fulfill({ response });
  });
  await page.route("**/api/decision/vocabulary.json", (route) => refuseVocabulary
    ? worker(route, "/v1/vocabulary")
    : route.fulfill({ contentType: "application/json", body: vocabulary }));
  await page.route(`${api}/v1/**`, (route) => {
    const target = new URL(route.request().url());
    return worker(route, target.pathname + target.search);
  });
  await page.route("https://challenges.cloudflare.com/**", (route) => route.fulfill({
    contentType: "application/javascript",
    body: `let checks = 0; window.turnstile = {
      render(container, options) { options.callback("browser-test-token-" + ++checks); return "test-widget"; },
      remove() {}
    };`,
  }));
  await page.clock.install({ time: new Date("2026-10-04T12:00:00Z") });
  return { calls, responses };
}

test("billing launch keeps browser lookup free through the real visit gate", async ({ page, baseURL, replayWorker }) => {
  test.skip(!visitPage, "requires the visit-enabled page build");
  const { calls, responses } = await builtPage(page, baseURL, true, replayWorker);
  await page.goto("https://modelspec.dev/decide.html");
  await expect(page.getByLabel("Facet board answer")).toBeVisible({ timeout: 20_000 });
  await expect.poll(() => calls.filter((call) => call.path === "/v1/decide").length).toBe(3);
  await expect.poll(() => responses.at(-1)?.produced).toBe(3);
  const decisions = calls.filter((call) => call.path === "/v1/decide");
  expect(new Set(decisions.map((call) => call.headers["x-modelspec-intent"])).size).toBe(1);
  expect(decisions.every((call) => Boolean(call.headers["x-modelspec-visit-token"]))).toBe(true);
  for (const path of ["/v1/human-status", "/v1/visit-token"]) {
    const indices = calls.flatMap((call, index) => call.path === path ? [index] : []);
    expect(indices.length).toBeGreaterThanOrEqual(1);
    for (const index of indices) {
      expect(calls[index].headers.authorization).toBeUndefined();
      expect(calls[index].headers["x-api-key"]).toBeUndefined();
      expect(responses[index].status).toBe(200);
    }
  }
  expect(responses.every((response) => response.status === 200 || response.status === 204)).toBe(true);
  expect(responses.at(-1)?.headers["x-modelspec-decisions-remaining"]).toBe("299");
  await expect(page.getByText("Choose a plan or pack.")).toBeVisible();
  await expect(page.getByText("API keys open soon.")).toHaveCount(0);

  // The page uses static vocabulary. A hosted vocabulary request is also
  // admitted by the real token and its separate SQLite allowance.
  const admitted = [...responses].reverse().find((response) => response.headers["x-modelspec-visit-token"]);
  if (!admitted) throw new Error("no renewed visit credential");
  const token = admitted.headers["x-modelspec-visit-token"];
  await page.clock.fastForward(2000);
  const display = await page.evaluate(async ({ api, token }) => {
    const response = await fetch(`${api}/v1/vocabulary`, { headers: { "X-ModelSpec-Visit-Token": token } });
    return { status: response.status, token: response.headers.get("x-modelspec-visit-token"),
      expires: response.headers.get("x-modelspec-visit-expires"), body: await response.text() };
  }, { api, token });
  expect(display.status).toBe(200);
  const displayBody = z.object({ facets: z.array(z.unknown()) }).parse(JSON.parse(display.body));
  expect(displayBody.facets.length).toBeGreaterThan(0);
  expect(display.token).toBeTruthy();
  expect(display.token).not.toBe(token);
  expect(Number(display.expires)).toBeGreaterThan(Number(admitted.headers["x-modelspec-visit-expires"]));

  // The page expires its credential locally and performs another real exchange.
  await page.clock.fastForward(1801 * 1000);
  const capabilities = page.getByRole("button", { name: /What it.s good at/ });
  if (await capabilities.getAttribute("aria-expanded") !== "true") await capabilities.click();
  await page.locator('[data-facet="capability.software_engineering"]').getByLabel("Prefer", { exact: true }).check();
  await expect.poll(() => calls.filter((call) => call.path === "/v1/visit-token").length).toBe(2);
  await expect.poll(() => responses.at(-1)?.produced).toBeGreaterThan(3);
  await expect(page.getByLabel("Facet board answer")).toBeVisible();

  const direct = await page.evaluate(async (api) => {
    const response = await fetch(`${api}/v1/decide`, { method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ spec_version: 1, optimize: { min: "offering.cost_per_task" } }) });
    return { status: response.status, body: await response.text() };
  }, api);
  expect(direct.status).toBe(401);
  const directBody = z.object({ error: z.object({ code: z.string(), how_to_get_a_key: z.string() }) }).parse(JSON.parse(direct.body));
  expect(directBody.error.code).toBe("missing_api_key");
  expect(directBody.error.how_to_get_a_key).toBe("https://modelspec.dev/pricing");
});

test("billing launch shows the key pointer when the Worker visit gate is off", async ({ page, baseURL, replayWorker }) => {
  const { calls, responses } = await builtPage(page, baseURL, false, replayWorker);
  await page.goto("https://modelspec.dev/decide.html");
  const error = page.getByRole("alert");
  await expect(error).toContainText("requires an API key", { timeout: 20_000 });
  await expect(error).toContainText("https://modelspec.dev/pricing");
  await expect(page.getByLabel("Facet board answer")).toHaveCount(0);
  // A data-split build reads /v1/vocabulary first and stops at its 401.
  const refused = calls.flatMap((call, index) => ["/v1/decide", "/v1/vocabulary"].includes(call.path) ? [responses[index]] : []);
  expect(refused.length).toBeGreaterThan(0);
  expect(refused.every((response) => response.status === 401 && response.produced === 0)).toBe(true);
  expect(calls.some((call) => call.path === "/v1/visit-token")).toBe(false);
  await expect(page.getByRole("button", { name: "Look up this decision" })).toHaveCount(0);
});

test("billing launch shows the vocabulary key pointer when the Worker visit gate is off", async ({ page, baseURL, replayWorker }) => {
  const { calls, responses } = await builtPage(page, baseURL, false, replayWorker, true);
  await page.goto("https://modelspec.dev/decide.html");
  const error = page.getByRole("alert");
  await expect(error).toContainText("requires an API key", { timeout: 20_000 });
  await expect(error).toContainText("https://modelspec.dev/pricing");
  const index = calls.findIndex((call) => call.path === "/v1/vocabulary");
  expect(index).toBeGreaterThanOrEqual(0);
  expect(responses[index].status).toBe(401);
  expect(responses[index].produced).toBe(0);
});
