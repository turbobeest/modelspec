import assert from "node:assert/strict";
import { createRequire } from "node:module";
import { mkdirSync, writeFileSync } from "node:fs";
const require = createRequire(new URL("../package.json", import.meta.url));
const { chromium } = require("playwright");
const origin = "http://127.0.0.1:5197";
const output = new URL("../../.scratch/proto/data-path/", import.meta.url);
mkdirSync(output, { recursive: true });
const jobs = [
  ["assistant-balanced", "Everyday help"], ["coding-balanced", "Coding"],
  ["writing-balanced", "Writing"], ["long-documents", "Long documents"],
  ["high-volume", "High volume"], ["private-self-host", "Self-hosting"],
];
const budgets = [["budget", "Cheapest"], ["balanced", "Balanced"], ["best", "Best quality"]];
const limits = [["none", "No hard limit"], ["open", "Must be open weights"], ["cost", "At most $0.05 per task"], ["eu", "EU data residency"]];
function canonical(value) {
  if (Array.isArray(value)) return value.map(canonical);
  if (value && typeof value === "object") return Object.fromEntries(Object.entries(value).sort(([a], [b]) => a.localeCompare(b)).map(([k, v]) => [k, canonical(v)]));
  return value;
}
const key = (spec) => JSON.stringify(canonical(spec));
const results = [];
const browser = await chromium.launch();
const context = await browser.newContext();
await context.route("**/*", (route) => new URL(route.request().url()).origin === origin ? route.continue() : route.abort());
const unexpected = [];
context.on("request", (request) => { if (new URL(request.url()).origin !== origin) unexpected.push(request.url()); });

async function inspect(job, budget, limit = "none", variant = "a") {
  const page = await context.newPage();
  const exchanges = [];
  page.on("response", async (response) => {
    if (new URL(response.url()).pathname !== "/v1/decide") return;
    try { exchanges.push({ spec: response.request().postDataJSON(), response: await response.json(), status: response.status(), source: response.headers()["x-prototype-source"] }); } catch {}
  });
  let detail;
  const row = { variant, job: job[0], budget: budget[0], limit };
  try {
    await page.goto(`${origin}/prototypes/proto-${variant}.html`);
    const expected = await page.evaluate(async ({ job, budget, limit }) => {
      const data = await import("/prototypes/data.ts");
      const request = await import("/src/decide/adapter/request-spec.ts");
      const selection = data.choose(job, budget, limit);
      return {
        spec: request.prepareDecisionRequest(data.vocabulary, selection.spec, "full").decisionSpec,
        link: data.evidenceLink(selection),
        names: Object.fromEntries(Object.entries(data.vocabulary.models).map(([id, model]) => [id, model.display_name])),
      };
    }, { job: job[0], budget: budget[0], limit });
    row.request = expected.spec;
    if (variant === "a") {
      await page.getByRole("button", { name: new RegExp(`^${job[1]}`) }).click();
      await page.getByRole("button", { name: budget[1], exact: true }).click();
    } else {
      await page.getByRole("button", { name: new RegExp(`^${job[1]}`) }).click();
      const priority = budget[0] === "budget" ? "Spend less" : budget[0] === "balanced" ? "Balance cost and quality" : "Best quality";
      await page.getByRole("button", { name: new RegExp(`^${priority}`) }).click();
      await page.getByRole("button", { name: new RegExp(`^${limits.find(([id]) => id === limit)[1].replaceAll("$", "\\$")}`) }).click();
      await page.getByRole("button", { name: "Show my options" }).click();
    }
    await page.waitForFunction(() => !!document.querySelector(".proto-answer[data-decision-id]"), { timeout: 60000 });
    await page.waitForTimeout(100);
    const exchange = exchanges.findLast((item) => key(item.spec) === key(expected.spec));
    assert.ok(exchange, "Visible selection did not send its expected POST");
    assert.equal(exchange.status, 200);
    const actual = exchange.response;
    row.status = actual.status;
    row.kind = actual.answer?.kind;
    row.source = exchange.source;
    row.snapshot = actual.snapshot;
    row.decision = actual.decision_id;
    assert.equal(await page.locator(".proto-answer").getAttribute("data-decision-id"), actual.decision_id, "Visible answer is stale");
    const members = actual.answer?.deterministic_order ?? [];
    assert.deepEqual(await page.locator(".proto-shortlist li strong").allTextContents(), members.map((id) => expected.names[id] ?? id));
    if (actual.answer?.kind === "tied") {
      assert.equal(members.length, actual.answer.members.length);
      assert.deepEqual([...members].sort(), [...actual.answer.members].sort());
      assert.match(await page.locator(".proto-answer h2").innerText(), /too close to call/);
    }
    if (actual.status === "no_feasible") assert.match(await page.locator(".proto-answer h2").innerText(), /No confirmed match/);
    const visiblePrices = await page.locator(".proto-price").allTextContents();
    for (let i = 0; i < members.length; i++) {
      const id = members[i];
      const model = actual.by_model.find((item) => item.model === id);
      const band = actual.bands?.best.find((item) => item.model === id);
      const ranked = actual.results.find((item) => item.offering.model === id);
      const cost = model?.cost_per_task ?? band?.cost_per_task ?? ranked?.cost_per_task;
      assert.equal(visiblePrices[i], cost == null ? "Cost unknown" : `$${cost.toFixed(cost < .01 ? 4 : 3)}per task`);
      if (limit === "cost" && cost != null) assert.ok(cost <= .05, "Shortlisted price breaks chosen ceiling");
    }
    const link = await page.getByRole("link", { name: "See the full evidence" }).getAttribute("href");
    assert.equal(link, expected.link);
    const encoded = JSON.parse(decodeURIComponent(atob(link.split("#s=")[1])));
    assert.equal(encoded.tokIn, expected.spec.task_tokens.input);
    assert.equal(encoded.tokOut, expected.spec.task_tokens.output);
    if (job[0] === "high-volume") assert.deepEqual(expected.spec.task_tokens, { input: 2000, output: 500 });
    if (job[0] === "private-self-host") {
      assert.ok(expected.spec.where.includes("model.weights_openness = open_weights"));
      assert.ok(expected.spec.where.some((condition) => condition.startsWith("licence.commercial_use in")));
    }
    if (limit === "open") assert.ok(expected.spec.where.includes("model.weights_openness = open_weights"));
    if (limit === "cost") assert.ok(expected.spec.where.includes("offering.cost_per_task <= 0.05"));
    if (limit === "eu") {
      assert.ok(expected.spec.where.some((condition) => condition.startsWith("offering.region in")));
      assert.ok(expected.spec.where.includes("offering.data.trains_on_customer_data = false"));
    }
    detail = await context.newPage();
    const detailSpecs = [];
    detail.on("request", (request) => { if (new URL(request.url()).pathname === "/v1/decide") detailSpecs.push(request.postDataJSON()); });
    await detail.goto(origin + link);
    for (let attempt = 0; attempt < 60 && !detailSpecs.some((spec) => spec.explain === "full"); attempt++) await detail.waitForTimeout(500);
    const full = detailSpecs.find((spec) => spec.explain === "full");
    assert.ok(full, "Detailed page did not send a full explanation request");
    row.handoff = full;
    assert.deepEqual(full, expected.spec, "Evidence handoff changed the chosen request");
    row.pass = true;
  } catch (error) {
    row.pass = false;
    row.error = String(error);
    row.exchanges = exchanges.map(({ spec, status, response, source }) => ({ spec, status, source, decision: response.decision_id, error: response.error }));
  } finally {
    await detail?.close();
    await page.close();
  }
  results.push(row);
  writeFileSync(new URL("audit-results.json", output), JSON.stringify({ results, unexpected }, null, 2));
  console.log(JSON.stringify({ ...row, request: undefined, handoff: undefined, exchanges: undefined }));
}

try {
  for (const job of jobs) for (const budget of budgets) await inspect(job, budget);
  for (const [limit] of limits) await inspect(jobs[0], budgets[1], limit, "b");
  if (unexpected.length) console.log("Blocked external requests: " + JSON.stringify(unexpected));
  console.log(`${results.filter((row) => row.pass).length}/${results.length} paths passed`);
  assert.equal(results.filter((row) => row.pass).length, 22);
  assert.deepEqual(unexpected, []);
} finally { await browser.close(); }
