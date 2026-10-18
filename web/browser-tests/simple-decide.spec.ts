import { expect, type Page, type Route } from "@playwright/test";
import { readFileSync, mkdirSync } from "node:fs";
import { test } from "./human-gate-fixtures";
import { decisionSchema, decisionSpecSchema, type Decision } from "../src/decide/adapter/contract";
import rawVocabulary from "../src/decide/__fixtures__/live-vocabulary.json" with { type: "json" };
import coveredVocabulary from "../src/decide/__fixtures__/vocabulary.json" with { type: "json" };
import { z } from "zod";

const read = (name: string): unknown => JSON.parse(readFileSync(new URL(`../src/decide/__fixtures__/${name}`, import.meta.url), "utf8"));
const vocabulary = { ...rawVocabulary, coverage: coveredVocabulary.coverage };
const fixture = decisionSchema.parse(read("live-assistant-balanced-full.json"));
const cors = { "access-control-allow-origin": "*", "access-control-allow-headers": "*", "access-control-allow-methods": "GET, POST, OPTIONS" };
const answer = (page: Page) => page.getByRole("region", { name: "Decision answer", exact: true });
const names = ["Claude Opus 5.5", "Gemini 3.7 Flash", "Gemini 3.8 Flash", "GPT-6 Sol", "Grok 4.7", "Qwen3.8 Max 0902"];
const evidence = new URL("../../docs/evidence/g2-ios/MODEL-404/gates/", import.meta.url);

async function reply(route: Route, body: unknown) {
  await route.fulfill({ status: route.request().method() === "OPTIONS" ? 204 : 200, headers: cors, contentType: "application/json", body: route.request().method() === "OPTIONS" ? undefined : JSON.stringify(body) });
}

test.beforeEach(async ({ page }) => {
  await page.route(/\/(?:api\/decision\/vocabulary\.json|v1\/vocabulary)(?:\?.*)?$/, (route) => reply(route, vocabulary));
  await page.route("**/v1/decide", (route) => reply(route, fixture));
});

test("opens with a labelled example and an alphabetical tie with equal emphasis", async ({ page }) => {
  await page.goto("/decide/");
  await expect(page.getByText("Example: Everyday help. Pick a job if this isn't yours.", { exact: true })).toBeVisible();
  await expect(answer(page).getByRole("heading", { level: 2 })).toHaveText("These 6 are too close to call.");
  await expect(page.getByRole("group", { name: "Choose your job" }).getByRole("button")).toHaveCount(6);
  await expect(answer(page).getByText("Listed alphabetically, not ranked.", { exact: true })).toBeVisible();
  const rows = answer(page).getByRole("list", { name: "Best matches" }).getByRole("listitem");
  await expect(rows.locator("strong")).toHaveText(names);
  await expect(answer(page)).not.toContainText(/chance of being best|your shortlist|your mix|winner|★/i);
  const styles = await rows.locator("strong").evaluateAll((nodes) => nodes.map((node) => {
    const style = getComputedStyle(node);
    return [style.fontSize, style.fontWeight, style.color, style.backgroundColor];
  }));
  expect(new Set(styles.map((style) => JSON.stringify(style))).size).toBe(1);
  await expect(page.getByText("Data as of 2026-09-25", { exact: true })).toBeVisible();
  await expect(page.locator("header")).not.toContainText("snap_");
  await expect(answer(page).getByText("ModelSpec is neutral: no referral fees, no paid placement.", { exact: true })).toBeVisible();
});

test("a keyboard job pick changes the request, focuses the verdict and carries the same question to evidence", async ({ page }) => {
  await page.goto("/decide/");
  await expect(answer(page)).toBeVisible();
  const changed = page.waitForRequest((request) => request.url().endsWith("/v1/decide") && request.method() === "POST" && JSON.stringify(request.postDataJSON()).includes("software_engineering"));
  const coding = page.getByRole("group", { name: "Choose your job" }).getByRole("button", { name: /^Coding/ });
  await coding.focus();
  await page.keyboard.press("Enter");
  const request = decisionSpecSchema.parse((await changed).postDataJSON());
  await expect(coding).toHaveAttribute("aria-pressed", "true");
  await expect(answer(page).getByRole("heading", { level: 2 })).toBeFocused();
  await expect(page.getByText("Example: Everyday help. Pick a job if this isn't yours.", { exact: true })).toHaveCount(0);
  const link = page.getByRole("link", { name: "See the full evidence", exact: true });
  await expect(link).toHaveAttribute("href", /^\/decide\/details\/#s=/);
  const sharedRequest = page.waitForRequest((item) => item.url().endsWith("/v1/decide") && item.method() === "POST" && item.postDataJSON().explain === "summary");
  await link.click();
  const details = decisionSpecSchema.parse((await sharedRequest).postDataJSON());
  expect({ ...details, explain: request.explain }).toEqual(request);
  await expect(page.getByLabel("Facet board answer")).toBeVisible();
});

for (const state of ["?template=coding-balanced&source=old", "?source=old#s=preserved-state"]) {
  test(`old board links retain query and hash: ${state}`, async ({ page }) => {
    await page.goto(`/decide/${state}`);
    await expect(page).toHaveURL(`http://127.0.0.1:${new URL(page.url()).port}/decide/details/${state}`);
    await expect(page.getByText("Example: Everyday help. Pick a job if this isn't yours.", { exact: true })).toHaveCount(0);
  });
}

test("limits are collapsed, EU and training are separate and route travels with the evidence", async ({ page }) => {
  const requests: ReturnType<typeof decisionSpecSchema.parse>[] = [];
  await page.route("**/v1/decide", async (route) => {
    if (route.request().method() === "POST") requests.push(decisionSpecSchema.parse(route.request().postDataJSON()));
    await reply(route, fixture);
  });
  await page.goto("/decide/");
  await expect(answer(page)).toBeVisible();
  await expect(page.getByLabel("EU residency", { exact: true })).not.toBeVisible();
  await page.getByRole("button", { name: "Change", exact: true }).click();
  await expect(page.getByText("We will only shortlist confirmed matches.", { exact: true })).toBeVisible();
  await page.getByLabel("EU residency", { exact: true }).check();
  await expect.poll(() => requests.at(-1)?.where).toContain("offering.region in {AT, BE, BG, HR, CY, CZ, DE, DK, EE, ES, FI, FR, GR, HU, IE, IT, LT, LU, LV, MT, NL, PL, PT, RO, SE, SI, SK}");
  expect(requests.at(-1)?.where).not.toContain("offering.data.trains_on_customer_data = false");
  await page.getByLabel("No customer-data training", { exact: true }).check();
  await expect.poll(() => requests.at(-1)?.where).toContain("offering.data.trains_on_customer_data = false");
  await page.getByRole("combobox", { name: "How will you use the model?", exact: true }).selectOption("own_software");
  await expect.poll(() => requests.at(-1)?.access).toBe("own_software");
  await expect(page.getByRole("link", { name: "See the full evidence", exact: true })).toHaveAttribute("href", /^\/decide\/details\/#s=/);
});

test("visible counts, costs and source dates change with the engine response", async ({ page }) => {
  const changed = structuredClone(fixture);
  if (!changed.answer || changed.answer.kind !== "tied") throw new Error("The fixture must contain a tie");
  changed.answer.members = changed.answer.members.slice(0, 2);
  changed.answer.deterministic_order = [...changed.answer.members].reverse();
  changed.by_model = changed.by_model.filter((row) => changed.answer?.members.includes(row.model) || row.status === "may_qualify").slice(0, 5);
  for (const row of changed.by_model) {
    if (row.status !== "ranked") continue;
    row.cost_per_task = 0.789;
    for (const offering of row.offerings) offering.cost_per_task = 0.789;
  }
  for (const result of changed.results) {
    result.cost_per_task = 0.789;
    for (const domain of result.evidence) for (const item of domain.items) item.date = "2026-08-19";
    for (const contribution of result.contributions) for (const item of contribution.evidence) item.date = "2026-08-19";
  }
  if (changed.bands) {
    changed.bands.best = changed.bands.best.filter((row) => changed.answer?.members.includes(row.model));
    for (const band of changed.bands.best) band.cost_per_task = 0.789;
  }
  await page.route("**/v1/decide", (route) => reply(route, decisionSchema.parse(changed)));
  await page.goto("/decide/");
  await expect(answer(page).getByRole("heading", { level: 2 })).toHaveText("These 2 are too close to call.");
  await expect(answer(page).getByRole("list", { name: "Best matches" }).getByRole("listitem")).toHaveCount(2);
  await expect(answer(page).getByText("$0.789 per task", { exact: true })).toHaveCount(2);
  await expect(answer(page)).toContainText("2 pass these limits. 3 more are missing a fact, so they stay possible.");
  await expect(answer(page)).toContainText("2026-08-19");
  await expect(answer(page)).not.toContainText("2026-09-23");
});

test("no-fit and undetermined answers keep uncertainty and a next action", async ({ page }) => {
  const noFit: Decision = { ...structuredClone(fixture), status: "no_feasible", answer: null, bands: null, results: [], by_model: [], relax: ["model.weights_openness = open_weights"] };
  await page.route("**/v1/decide", (route) => reply(route, noFit));
  await page.goto("/decide/");
  await page.getByRole("button", { name: "Change", exact: true }).click();
  await page.getByLabel("Open weights", { exact: true }).check();
  await expect(answer(page)).toContainText(/No (?:model|confirmed match)/);
  await expect(answer(page).getByRole("button", { name: /Remove.*Open weights/i })).toBeVisible();
  await expect(page.getByRole("link", { name: "See the full evidence", exact: true })).toBeVisible();
  await page.route("**/v1/decide", (route) => reply(route, { ...fixture, status: "partial", answer: null, bands: null }));
  await page.getByRole("group", { name: "Choose your job" }).getByRole("button", { name: /^Writing/ }).click();
  await expect(answer(page)).toContainText(/(?:cannot determine|No clear pick|undetermined)/i);
  await expect(answer(page).getByRole("list", { name: "Best matches" })).toHaveCount(0);
});

test("the example fits 390 by 844 with readable contrast, full ties and 44px controls in both themes", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/decide/");
  await expect(answer(page).getByRole("list", { name: "Best matches" }).getByRole("listitem")).toHaveCount(6);
  await page.evaluate(() => document.fonts.ready);
  for (const theme of ["dark", "light"]) {
    if (theme === "light") await page.getByRole("button", { name: "Light mode", exact: true }).click();
    const controls = page.getByRole("group", { name: "Choose your job" }).getByRole("button")
      .or(page.getByRole("group", { name: "What matters most?" }).getByRole("button"))
      .or(page.getByRole("link", { name: "ModelSpec home", exact: true }))
      .or(page.locator("header").getByRole("button", { name: /^(?:Light|Dark) mode$/ }))
      .or(page.getByRole("button", { name: "Change", exact: true }))
      .or(page.getByRole("link", { name: "See the full evidence", exact: true }));
    for (const control of await controls.all()) {
      const box = await control.boundingBox();
      expect(box).not.toBeNull();
      if (!box) continue;
      const name = await control.getAttribute("aria-label") ?? await control.innerText();
      expect(box.height, `${theme}: ${name} height`).toBeGreaterThanOrEqual(44);
      expect(box.width, `${theme}: ${name} width`).toBeGreaterThanOrEqual(44);
      expect(box.y + box.height).toBeLessThanOrEqual(844);
    }
    for (const item of await answer(page).getByRole("list", { name: "Best matches" }).getByRole("listitem").all()) {
      const box = await item.boundingBox();
      expect(box).not.toBeNull();
      if (box) expect(box.y + box.height).toBeLessThanOrEqual(844);
    }
    const cta = await page.getByRole("link", { name: "See the full evidence", exact: true }).boundingBox();
    expect(cta).not.toBeNull();
    if (cta) expect(cta.y + cta.height).toBeLessThanOrEqual(844);
    expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(390);
    const ratios = await page.locator("main").evaluate((root) => {
      const lum = (color: string) => {
        const rgb = color.match(/[\d.]+/g)?.slice(0, 3).map(Number);
        if (!rgb || rgb.length !== 3) throw new Error(`Unsupported color ${color}`);
        return rgb.map((value) => value / 255).map((value) => value <= 0.04045 ? value / 12.92 : ((value + 0.055) / 1.055) ** 2.4).reduce((sum, value, i) => sum + value * [0.2126, 0.7152, 0.0722][i], 0);
      };
      return [...root.querySelectorAll("h1,h2,p,button,a,strong,small,span")].filter((node) => node.getClientRects().length && node.textContent?.trim()).map((node) => {
        let background: Element | null = node;
        while (background && ["transparent", "rgba(0, 0, 0, 0)"].includes(getComputedStyle(background).backgroundColor)) background = background.parentElement;
        if (!background) throw new Error("No text background");
        const foreground = lum(getComputedStyle(node).color), behind = lum(getComputedStyle(background).backgroundColor);
        return { text: node.textContent?.slice(0, 70), ratio: (Math.max(foreground, behind) + 0.05) / (Math.min(foreground, behind) + 0.05) };
      });
    });
    for (const item of ratios) expect(item.ratio, `${theme}: ${item.text}`).toBeGreaterThanOrEqual(4.5);
  }
});

test.describe("simple page manual human gate", () => {
  test.use({ humanStatus: { enabled: true, remaining: 20 } });
  test.skip(process.env.VITE_HUMAN_GATE_ENABLED !== "true" && process.env.VITE_VISIT_GATE_ENABLED !== "true", "requires a gate-capable build");
  test("waits for verification and sends the existing manual credential", async ({ page }) => {
    const sent: string[] = [];
    await page.route("https://challenges.cloudflare.com/turnstile/**", (route) => route.fulfill({ contentType: "application/javascript", body: 'window.turnstile = { render(container, options) { options.callback("manual-fixture"); return "widget"; }, remove() {} };' }));
    await page.route("**/v1/decide", async (route) => {
      if (route.request().method() === "POST") sent.push(route.request().headers()["x-modelspec-turnstile"]);
      await reply(route, fixture);
    });
    await page.goto("/decide/");
    const lookup = page.getByRole("button", { name: "Look up this decision", exact: true });
    await expect(lookup).toBeEnabled();
    expect(sent).toEqual([]);
    await expect(answer(page).getByRole("list", { name: "Best matches" })).toHaveCount(0);
    await lookup.click();
    await expect(answer(page).getByRole("list", { name: "Best matches" })).toBeVisible();
    expect(sent.length).toBeGreaterThan(0);
    expect(sent.every((token) => token === "manual-fixture")).toBe(true);
    await page.getByRole("group", { name: "Choose your job" }).getByRole("button", { name: /^Coding/ }).click();
    await expect(answer(page).getByRole("list", { name: "Best matches" })).toHaveCount(0);
  });
});

test.describe("simple page managed visit gate", () => {
  test.use({ humanStatus: { enabled: true, mode: "visit", day_limit: 300, burst_limit: 30 } });
  test.skip(process.env.VITE_VISIT_GATE_ENABLED !== "true", "requires visit support");
  test("withholds data until verification, shares the token and renews a refused token", async ({ page }) => {
    let checks = 0, vocabularies = 0, refuse = false;
    const sent: { token: string; intent: string; body: unknown }[] = [];
    await page.route("https://challenges.cloudflare.com/turnstile/**", (route) => route.fulfill({ contentType: "application/javascript", body: 'window.turnstile = { render(container, options) { if (options.appearance !== "interaction-only") throw Error("wrong challenge"); const button = document.createElement("button"); button.textContent = "Verify fixture"; button.onclick = () => options.callback("single-use"); container.append(button); return "widget"; }, remove() { document.querySelectorAll(".visit-gate button").forEach(button => button.remove()); } };' }));
    await page.route("**/v1/visit-token", async (route) => {
      if (route.request().method() === "POST") { expect(route.request().headers()["x-modelspec-turnstile"]).toBe("single-use"); checks++; }
      await reply(route, { token: `visit-${checks}`, expires_at: Math.floor(Date.now() / 1000) + 1800 });
    });
    await page.route(/\/(?:api\/decision\/vocabulary\.json|v1\/vocabulary)(?:\?.*)?$/, async (route) => { if (route.request().method() !== "OPTIONS") vocabularies++; await reply(route, vocabulary); });
    await page.route("**/v1/decide", async (route) => {
      if (route.request().method() === "POST") {
        const headers = route.request().headers();
        sent.push({ token: headers["x-modelspec-visit-token"], intent: headers["x-modelspec-intent"], body: route.request().postDataJSON() });
        if (refuse) { refuse = false; await route.fulfill({ status: 401, headers: cors, contentType: "application/json", body: JSON.stringify({ error: { code: "visit_token_expired" } }) }); return; }
      }
      await reply(route, fixture);
    });
    await page.goto("/decide/");
    await expect(page.getByRole("button", { name: "Verify fixture", exact: true })).toBeVisible();
    expect(vocabularies).toBe(0);
    expect(sent).toEqual([]);
    await page.getByRole("button", { name: "Verify fixture", exact: true }).click();
    await expect(answer(page).getByRole("list", { name: "Best matches" })).toBeVisible();
    await expect.poll(() => sent.length).toBe(2);
    expect(sent.every((request) => request.token === "visit-1")).toBe(true);
    expect(new Set(sent.map((request) => request.intent)).size).toBe(1);
    await expect(page.getByRole("button", { name: "Look up this decision" })).toHaveCount(0);
    const start = sent.length;
    refuse = true;
    await page.getByRole("group", { name: "Choose your job" }).getByRole("button", { name: /^Coding/ }).click();
    await page.getByRole("button", { name: "Verify fixture", exact: true }).click();
    await expect(answer(page).getByRole("list", { name: "Best matches" })).toBeVisible();
    expect(checks).toBe(2);
    await expect.poll(() => sent.length).toBeGreaterThan(start + 1);
    expect(sent[start].intent).toBe(sent[start + 1].intent);
    expect(sent[start].body).toEqual(sent[start + 1].body);
    expect(sent[start + 1].token).toBe("visit-2");
  });
});

test("capture simple example, coding, tie, no-fit and detailed board", async ({ page }) => {
  test.skip(process.env.MODELSPEC_CAPTURE_SIMPLE !== "1", "opt-in reproducible evidence capture");
  mkdirSync(evidence, { recursive: true });
  await page.route(/\/(?:api\/decision\/vocabulary\.json|v1\/vocabulary)(?:\?.*)?$/, (route) => reply(route, rawVocabulary));
  const captureSchema = z.object({ spec: decisionSpecSchema, decision: decisionSchema });
  const coding = captureSchema.parse(JSON.parse(readFileSync(new URL(".generated/coding-decision.json", evidence), "utf8")));
  const noFit = captureSchema.parse(JSON.parse(readFileSync(new URL(".generated/no-fit-decision.json", evidence), "utf8")));
  await page.route("**/v1/decide", async (route) => {
    if (route.request().method() === "OPTIONS") return reply(route, {});
    const request = decisionSpecSchema.parse(route.request().postDataJSON());
    const recorded = request.where?.includes("model.weights_openness = open_weights")
      && request.where?.some((condition) => condition.startsWith("offering.cost_per_task")) ? noFit
      : JSON.stringify(request.optimize).includes("software_engineering") ? coding : null;
    if (recorded) {
      expect({ ...request, explain: "full" }).toEqual(recorded.spec);
      await reply(route, recorded.decision);
    } else await reply(route, fixture);
  });
  for (const viewport of [{ width: 1440, height: 1000 }, { width: 390, height: 844 }]) {
    const size = viewport.width === 390 ? "mobile" : "desktop";
    await page.setViewportSize(viewport);
    await page.goto("/decide/");
    await expect(answer(page).getByRole("list", { name: "Best matches" })).toBeVisible();
    await page.evaluate(() => document.fonts.ready);
    await page.screenshot({ path: new URL(`simple-${size}-example.png`, evidence).pathname, fullPage: size === "desktop" });
    if (size === "mobile") await page.screenshot({ path: new URL("simple-mobile-example-full.png", evidence).pathname, fullPage: true });
    await page.getByRole("group", { name: "Choose your job" }).getByRole("button", { name: /^Coding/ }).click();
    await expect(answer(page)).toHaveAttribute("data-decision-id", coding.decision.decision_id);
    await expect(answer(page).getByRole("heading", { level: 2 })).toBeFocused();
    await page.screenshot({ path: new URL(`simple-${size}-coding.png`, evidence).pathname, fullPage: size === "desktop" });
    await page.getByRole("group", { name: "Choose your job" }).getByRole("button", { name: /^Everyday help/ }).click();
    await expect(answer(page).getByRole("list", { name: "Best matches" }).getByRole("listitem")).toHaveCount(6);
    await page.screenshot({ path: new URL(`simple-${size}-tie.png`, evidence).pathname, fullPage: size === "desktop" });
    await page.getByRole("group", { name: "Choose your job" }).getByRole("button", { name: /^Self-hosting/ }).click();
    await page.getByRole("group", { name: "What matters most?" }).getByRole("button", { name: "Spend less", exact: true }).click();
    await expect(answer(page)).toHaveAttribute("data-decision-id", noFit.decision.decision_id);
    await expect(answer(page)).toContainText(/No (?:model|confirmed match)/);
    await page.screenshot({ path: new URL(`simple-${size}-no-fit.png`, evidence).pathname, fullPage: size === "desktop" });
    await page.goto("/decide/details/");
    await expect(page.getByLabel("Facet board answer")).toBeVisible();
    await page.screenshot({ path: new URL(`details-${size}.png`, evidence).pathname });
  }
});
