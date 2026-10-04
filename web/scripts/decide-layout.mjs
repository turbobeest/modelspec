// Measures /decide's layout contract (MODEL-325) on a clean first visit and
// after a template click, and saves the screenshots.
//
// Usage, with `npm run dev -- --host 127.0.0.1` running in web/:
//   node scripts/decide-layout.mjs [--base http://127.0.0.1:5173] [--out test-results/decide-layout]
// Exits 1 when any check fails.

import { mkdirSync, writeFileSync } from "node:fs";
import { parseArgs } from "node:util";
import { chromium, devices } from "@playwright/test";
import { check, counterView, measure, openDecide, routeFixtures } from "./decide-layout-measure.mjs";

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

  if (name === "desktop-1236") {
    const before = await counterView(page);
    const answered = page.waitForResponse((response) => response.url().endsWith("/v1/decide"));
    await page.locator(".template-shortcut").nth(1).click();
    await answered;
    await page.waitForFunction((text) => document.querySelector(".narrowing .panel")?.innerText !== text, before.text);
    const after = await counterView(page);
    await page.screenshot({ path: `${values.out}/${name}-after-template-click.png` });
    rows.push({
      check: "template click changes the first screen",
      pass: after.text !== before.text && after.bottom <= after.viewport && (await page.evaluate(() => scrollY)) === 0,
      detail: `${before.summary} → ${after.summary}; counter bottom ${Math.round(after.bottom)} ≤ ${after.viewport}`,
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
