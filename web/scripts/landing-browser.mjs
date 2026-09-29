import assert from "node:assert/strict";
import fs from "node:fs";
import http from "node:http";
import path from "node:path";
import { chromium } from "playwright";

const [livePath, holdingPath, methodPath, assembledPath] = process.argv.slice(2);
const root = new URL("../../", import.meta.url);
const cssPath = new URL("pipeline/landing_assets/landing.css", root).pathname;
const scriptPath = new URL("pipeline/landing_assets/landing.js", root).pathname;
const live = fs.readFileSync(livePath, "utf8");
const holding = fs.readFileSync(holdingPath, "utf8");
const method = fs.readFileSync(methodPath, "utf8");
const assembledRoot = path.resolve(assembledPath);
const results = {};
const browser = await chromium.launch({ headless: true });
const server = http.createServer((request, response) => {
  const pathname = new URL(request.url ?? "/", "http://localhost").pathname;
  const relative = pathname === "/decide/"
    ? "decide/index.html"
    : pathname.replace(/^\//, "");
  const staticFile = path.resolve(assembledPath, relative);
  if (relative && staticFile.startsWith(assembledRoot + path.sep) && fs.existsSync(staticFile)) {
    const types = { ".css": "text/css", ".html": "text/html", ".js": "text/javascript" };
    response.setHeader("content-type", types[path.extname(staticFile)] ?? "application/octet-stream");
    response.end(fs.readFileSync(staticFile));
    return;
  }
  response.setHeader("content-type", "text/html; charset=utf-8");
  response.end(live);
});
await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
const address = server.address();
assert.notEqual(address, null);
assert.equal(typeof address, "object");
const origin = `http://127.0.0.1:${address.port}`;

function recordBrowserFailures(page) {
  const failures = [];
  page.on("console", (message) => {
    if (message.type() === "error") failures.push(`console: ${message.text()}`);
  });
  page.on("pageerror", (error) => failures.push(`page: ${error.message}`));
  page.on("requestfailed", (request) =>
    failures.push(`request: ${request.url()} (${request.failure()?.errorText})`),
  );
  page.on("response", (response) => {
    if (response.status() >= 400) failures.push(`HTTP ${response.status()}: ${response.url()}`);
  });
  return failures;
}

async function assertRankedBoard(page) {
  await page.getByRole("heading", { name: "Set what matters. Watch the field narrow." }).waitFor();
  assert.equal(await page.locator("textarea").count(), 0);
  await page.locator(".board-ranked-answer li").first().waitFor();
}

// MODEL-213: one lockup scale, 48px mark on desktop and 38px below 900px, never past the edge.
async function assertLockup(page, width) {
  const lockup = await page.evaluate(() => {
    const element = document.querySelector("header .lockup, .global-header .lockup");
    const mark = element?.querySelector(".mark")?.getBoundingClientRect();
    const box = element?.getBoundingClientRect();
    return { mark: mark?.width, right: box?.right, client: document.documentElement.clientWidth };
  });
  assert.equal(lockup.mark, width >= 900 ? 48 : 38, `lockup at ${width}px: ${JSON.stringify(lockup)}`);
  assert.equal(lockup.right <= lockup.client, true, `lockup overflows at ${width}px: ${JSON.stringify(lockup)}`);
}

async function load(page, html) {
  await page.setContent(html);
  await page.addStyleTag({ path: cssPath });
  await page.addScriptTag({ path: scriptPath });
}

try {
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await context.newPage();
  await load(page, live);

  const plotText = await page.locator("#plot").textContent();
  assert.match(plotText, /cost per coding task \(12K tokens in, 3K out\)/);
  await assert.doesNotReject(() =>
    page.locator(".receipt").getByText("4,321 tasks · 12K in / 3K out").waitFor(),
  );

  async function submit(id) {
    await page.locator("#model-pick").selectOption(id);
    await page.locator("#pick-form button").click();
    return page.locator("#pick-result").textContent();
  }
  const tied = await submit("synthetic-tie");
  assert.match(tied, /Synthetic Tie is in the tie/);
  assert.match(tied, /\$0\.200 per task/);
  assert.match(tied, /At 4,321 tasks/);
  assert.match(tied, /costs \$432 more than.*Synthetic Cheapest/);
  const untied = await submit("synthetic-outsider");
  assert.match(untied, /Synthetic Outsider is not in the tie/);
  assert.match(untied, /\$0\.500 per task/);
  assert.match(untied, /costs \$1,728 more than.*Synthetic Cheapest/);
  results.altered_data = true;
  results.challenge = true;

  assert.equal(await page.locator(".sticky").evaluate((el) => getComputedStyle(el).display), "none");
  await assertLockup(page, 1440);
  const hero = await page.evaluate(() => {
    const box = (selector) => document.querySelector(selector).getBoundingClientRect();
    const size = (selector) => parseFloat(getComputedStyle(document.querySelector(selector)).fontSize);
    const copy = box(".hero-copy");
    const plot = box("#plot");
    return {
      copyRight: copy.right, copyTop: copy.top, copyBottom: copy.bottom,
      plotLeft: plot.left, plotTop: plot.top, plotWidth: plot.width,
      h1: size(".hero h1"), tie: size(".receipt h2"),
      scroll: document.documentElement.scrollWidth,
    };
  });
  // MODEL-229: the graph sits beside the copy, larger than its old 680px
  // column, and neither headline outgrows the smaller type.
  assert.equal(hero.plotLeft >= hero.copyRight, true, JSON.stringify(hero));
  assert.equal(hero.plotTop < hero.copyBottom && hero.plotTop >= hero.copyTop - 100, true, JSON.stringify(hero));
  assert.equal(hero.plotWidth > 680, true, JSON.stringify(hero));
  assert.equal(hero.h1 <= 56 && hero.tie <= 56, true, JSON.stringify(hero));
  assert.equal(hero.scroll <= 1440, true, JSON.stringify(hero));
  await page.setViewportSize({ width: 390, height: 844 });
  await assertLockup(page, 390);
  const overflow = await page.evaluate(() => ({
    client: document.documentElement.clientWidth,
    scroll: document.documentElement.scrollWidth,
    bodyClient: document.body.clientWidth,
    bodyScroll: document.body.scrollWidth,
    bodyOverflow: getComputedStyle(document.body).overflowX,
    widest: [...document.querySelectorAll("body *")]
      .map((element) => ({ tag: element.tagName, className: element.className?.baseVal ?? element.className, right: element.getBoundingClientRect().right }))
      .filter(({ right }) => right > document.documentElement.clientWidth)
      .sort((a, b) => b.right - a.right)
      .slice(0, 5),
  }));
  assert.equal(overflow.scroll <= overflow.client, true, JSON.stringify(overflow));
  assert.notEqual(await page.locator(".sticky").evaluate((el) => getComputedStyle(el).display), "none");
  assert.equal(await page.locator(".sticky").isVisible(), true);
  results.responsive = true;
  await context.close();

  const methodContext = await browser.newContext({ viewport: { width: 390, height: 844 } });
  const methodPage = await methodContext.newPage();
  await methodPage.setContent(method);
  await methodPage.addStyleTag({ path: cssPath });
  await methodPage.addStyleTag({ path: new URL("pipeline/landing_assets/method.css", root).pathname });
  const methodWidth = await methodPage.evaluate(() => document.documentElement.scrollWidth);
  assert.equal(methodWidth <= 390, true, `method scrollWidth=${methodWidth}`);
  await assertLockup(methodPage, 390);
  results.method_responsive = true;
  await methodContext.close();

  const reduced = await browser.newContext({
    viewport: { width: 1440, height: 900 },
    reducedMotion: "reduce",
  });
  const reducedPage = await reduced.newPage();
  await load(reducedPage, live);
  assert.equal(await reducedPage.locator(".chips [data-active]").count(), 3);
  const reducedCaption = await reducedPage.locator("#plot-caption").textContent();
  await reducedPage.waitForTimeout(2850);
  assert.equal(await reducedPage.locator(".chips [data-active]").count(), 3);
  assert.equal(await reducedPage.locator("#plot-caption").textContent(), reducedCaption);
  await reduced.close();

  const animated = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const animatedPage = await animated.newPage();
  await load(animatedPage, live);
  assert.equal(await animatedPage.locator(".chips [data-active]").count(), 0);
  await animatedPage.waitForTimeout(2850);
  assert.equal(await animatedPage.locator(".chips [data-active]").count(), 1);
  results.motion = true;
  await animated.close();

  const holdingContext = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const holdingPage = await holdingContext.newPage();
  await load(holdingPage, holding);
  assert.equal(await holdingPage.locator('a[href="/"]').count(), 0);
  assert.equal(await holdingPage.getByText("Board opening soon").first().isVisible(), true);
  results.holding = true;
  await holdingContext.close();

  const forwarding = await browser.newContext();
  const forwardingPage = await forwarding.newPage();
  await forwardingPage.goto(`${origin}/?estate=saved&utm_source=old#s=shared`);
  await forwardingPage.waitForURL(`${origin}/decide/?estate=saved&utm_source=old#s=shared`);
  assert.equal(new URL(forwardingPage.url()).pathname, "/decide/");
  const campaignPage = await forwarding.newPage();
  await campaignPage.goto(`${origin}/?utm_source=launch`);
  assert.equal(new URL(campaignPage.url()).pathname, "/");
  results.forwarding = true;
  await forwarding.close();

  const vocabularyFixture = fs.readFileSync(new URL("../src/decide/__fixtures__/vocabulary.json", import.meta.url), "utf8");
  const decisionFixture = fs.readFileSync(new URL("../src/decide/__fixtures__/live-empty-board-full.json", import.meta.url), "utf8");
  async function serveAssembled(context, { scripts = true } = {}) {
    await context.route("https://modelspec.dev/**", (route) => {
      const pathname = new URL(route.request().url()).pathname;
      const relative = pathname === "/decide/" ? "decide/index.html" : pathname.replace(/^\//, "");
      const staticFile = path.resolve(assembledPath, relative);
      if (!scripts && relative.endsWith(".js")) return route.abort();
      if (!staticFile.startsWith(assembledRoot + path.sep) || !fs.existsSync(staticFile))
        return route.fulfill({ status: 404, body: "not found" });
      const types = { ".css": "text/css", ".html": "text/html", ".js": "text/javascript" };
      return route.fulfill({ status: 200, contentType: types[path.extname(staticFile)] ?? "application/octet-stream", body: fs.readFileSync(staticFile) });
    });
    await context.route("**/api/decision/vocabulary.json", (route) => route.fulfill({ status: 200, contentType: "application/json", body: vocabularyFixture }));
    await context.route("**/v1/decide", (route) => route.fulfill({ status: 200, contentType: "application/json", body: decisionFixture }));
  }

  // Before the app's script runs, the page is already dark: no light flash, whatever the OS prefers.
  const unhydrated = await browser.newContext({ colorScheme: "light" });
  await serveAssembled(unhydrated, { scripts: false });
  const firstPaint = await unhydrated.newPage();
  await firstPaint.goto("https://modelspec.dev/decide/?demo=1");
  assert.deepEqual(await firstPaint.evaluate(() => ({
    theme: document.documentElement.dataset.decideTheme,
    background: getComputedStyle(document.documentElement).backgroundColor,
  })), { theme: "dark", background: "rgb(11, 20, 38)" });
  results.decide_dark_before_paint = true;
  await unhydrated.close();

  const assembled = await browser.newContext({ colorScheme: "light", viewport: { width: 1440, height: 900 } });
  await serveAssembled(assembled);
  const decidePage = await assembled.newPage();
  const decideFailures = recordBrowserFailures(decidePage);
  await decidePage.goto("https://modelspec.dev/decide/?demo=1");
  await assertRankedBoard(decidePage);
  assert.deepEqual(decideFailures, []);
  assert.equal(await decidePage.locator(".decide-app").getAttribute("data-theme"), "dark");
  await decidePage.getByRole("button", { name: "Light mode" }).waitFor();
  await assertLockup(decidePage, 1440);
  results.assembled_decide = true;

  await decidePage.setViewportSize({ width: 390, height: 844 });
  async function assertDecideFitsViewport(theme) {
    assert.equal(await decidePage.locator(".decide-app").getAttribute("data-theme"), theme);
    await assertLockup(decidePage, 390);
    const overflow = await decidePage.evaluate(() => ({
      clientWidth: document.documentElement.clientWidth,
      scrollWidth: document.documentElement.scrollWidth,
      offenders: [...document.querySelectorAll("body *")]
        .map((element) => {
          const rect = element.getBoundingClientRect();
          return { tag: element.tagName, className: element.className?.baseVal ?? element.className, left: rect.left, right: rect.right, width: rect.width };
        })
        .filter(({ left, right }) => left < 0 || Math.abs(right - document.documentElement.scrollWidth) < 1)
        .sort((left, right) => right.right - left.right)
        .slice(0, 30),
    }));
    assert.equal(
      overflow.scrollWidth <= 390,
      true,
      `${theme} decide overflow: ${JSON.stringify(overflow)}`,
    );
  }
  await assertDecideFitsViewport("dark");
  await decidePage.getByRole("button", { name: "Light mode" }).click();
  await assertDecideFitsViewport("light");
  results.assembled_decide_mobile = true;

  await decidePage.reload();
  await assertRankedBoard(decidePage);
  assert.equal(await decidePage.locator(".decide-app").getAttribute("data-theme"), "light");
  await decidePage.getByRole("button", { name: "Dark mode" }).click();
  await decidePage.reload();
  await assertRankedBoard(decidePage);
  assert.equal(await decidePage.locator(".decide-app").getAttribute("data-theme"), "dark");
  results.decide_theme_persists = true;

  const state = btoa(encodeURIComponent(JSON.stringify({
    tokIn: 40000,
    tokOut: 4000,
    bench: "CodeBench Pro",
    w: { cap: 0.6, cost: 0.3, speed: 0.1 },
    conds: [{ f: "type", v: "llm" }, { f: "active" }],
  })));
  const oldRootPage = await assembled.newPage();
  const forwardedFailures = recordBrowserFailures(oldRootPage);
  await oldRootPage.goto(`${origin}/?demo=1#s=${state}`);
  await oldRootPage.waitForURL(`${origin}/decide/?demo=1#s=${state}`);
  assert.equal(new URL(oldRootPage.url()).hash, `#s=${state}`);
  await assertRankedBoard(oldRootPage);
  assert.deepEqual(forwardedFailures, []);
  results.forwarded_state_ranks = true;
  await assembled.close();
} finally {
  server.close();
  await browser.close();
}

process.stdout.write(JSON.stringify(results));
