import assert from "node:assert/strict";
import fs from "node:fs";
import http from "node:http";
import { chromium } from "playwright";

const [livePath, holdingPath] = process.argv.slice(2);
const root = new URL("../../", import.meta.url);
const cssPath = new URL("pipeline/landing_assets/landing.css", root).pathname;
const scriptPath = new URL("pipeline/landing_assets/landing.js", root).pathname;
const live = fs.readFileSync(livePath, "utf8");
const holding = fs.readFileSync(holdingPath, "utf8");
const results = {};
const browser = await chromium.launch({ headless: true });
const server = http.createServer((request, response) => {
  if (request.url?.startsWith("/decide/")) {
    response.end("<!doctype html><title>decide target</title>");
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
  await page.setViewportSize({ width: 390, height: 844 });
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
} finally {
  server.close();
  await browser.close();
}

process.stdout.write(JSON.stringify(results));
