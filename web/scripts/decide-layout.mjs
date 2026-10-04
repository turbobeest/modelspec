// Measures /decide's layout contract (MODEL-325) on a clean first visit and
// after a template click, and saves the screenshots.
//
// Usage, with `npm run dev -- --host 127.0.0.1` running in web/:
//   node scripts/decide-layout.mjs [--base http://127.0.0.1:5173] [--out test-results/decide-layout]
// Exits 1 when any check fails.

import { mkdirSync, writeFileSync } from "node:fs";
import { parseArgs } from "node:util";
import { chromium, devices } from "@playwright/test";
import { check, counterView, measure, openDecide, routeFixtures, routeNarrowedDecision, stickyChartView } from "./decide-layout-measure.mjs";

const { values } = parseArgs({ options: {
  base: { type: "string", default: "http://127.0.0.1:5173" },
  out: { type: "string", default: "test-results/decide-layout" },
} });
mkdirSync(values.out, { recursive: true });

const VIEWPORTS = [
  { name: "desktop-1236", viewport: { width: 1236, height: 800 } },
  { name: "desktop-1440", viewport: { width: 1440, height: 800 } },
  { name: "phone-390", ...devices["iPhone 14"], viewport: { width: 390, height: 844 } },
];

const browser = await chromium.launch();
const report = {};
let failed = 0;
for (const { name, ...options } of VIEWPORTS) {
  const context = await browser.newContext({ ...options, reducedMotion: "reduce" });
  const page = await context.newPage();
  await routeFixtures(page);
  await openDecide(page, values.base);
  await page.screenshot({ path: `${values.out}/${name}-first-screen.png` });
  await page.screenshot({ path: `${values.out}/${name}-full.png`, fullPage: true });
  const { width, height } = options.viewport;
  await page.screenshot({ path: `${values.out}/${name}-first-two-screens.png`, fullPage: true, clip: { x: 0, y: 0, width, height: 2 * height } });
  const layout = await measure(page);
  const rows = check(layout);

  if (name.startsWith("desktop")) {
    const sticky = await stickyChartView(page);
    rows.push({
      check: "chart clears the sticky header",
      pass: sticky.chartTop >= sticky.headerBottom + 16 - 0.5,
      detail: `chart top ${Math.round(sticky.chartTop * 10) / 10} ≥ header bottom ${Math.round(sticky.headerBottom * 10) / 10} + 16`,
    });
    await page.evaluate(() => scrollTo(0, 0));
  }

  if (name === "desktop-1236") {
    const before = await counterView(page);
    await routeNarrowedDecision(page);
    const answered = page.waitForResponse((response) => response.url().endsWith("/v1/decide"));
    const want = ["15", "3", "14", "—"];
    await page.locator(".template-shortcut").nth(1).click();
    await answered;
    await page.waitForFunction((expected) => {
      const got = [...document.querySelectorAll(".narrowing-number")].map((node) => node.textContent);
      return got.length === expected.length && got.every((value, index) => value === expected[index]);
    }, want);
    const after = await counterView(page);
    const scrollY = await page.evaluate(() => scrollY);
    await page.screenshot({ path: `${values.out}/${name}-after-template-click.png` });
    const numbers = (await page.locator(".narrowing-number").allTextContents()).join("/");
    rows.push({
      check: "template click changes the first screen",
      pass: numbers === want.join("/") && after !== null && after.bottom <= 800 && scrollY === 0,
      detail: `${before.summary} → ${numbers}; counter bottom ${after === null ? "missing" : Math.round(after.bottom)} ≤ 800; scrollY ${scrollY}`,
    });
  }
  report[name] = { rows, layout };
  console.log(`\n${name} (${options.viewport.width}×${options.viewport.height})`);
  for (const row of rows) {
    if (!row.pass) failed += 1;
    console.log(`  ${row.pass ? "PASS" : "FAIL"}  ${row.check.padEnd(40)} ${row.detail}`);
  }
  await context.close();
}
await browser.close();
writeFileSync(`${values.out}/report.json`, JSON.stringify(report, null, 2));
console.log(`\n${failed ? `${failed} check(s) failed` : "all checks pass"}; screenshots and report.json in ${values.out}`);
process.exit(failed ? 1 : 0);
