import { chromium } from "@playwright/test";
import { readFile } from "node:fs/promises";
import { pathToFileURL } from "node:url";

const manifest = process.argv[2];
if (!manifest) throw new Error("usage: render-social-cards.mjs MANIFEST.json");

const jobs = JSON.parse(await readFile(manifest, "utf8"));
const browser = await chromium.launch({ headless: true });
try {
  const page = await browser.newPage({ viewport: { width: 1200, height: 630 } });
  for (const job of jobs) {
    await page.goto(pathToFileURL(job.source).href, { waitUntil: "load" });
    await page.evaluate(() => document.fonts.ready);
    await page.screenshot({ path: job.output, type: "png" });
  }
} finally {
  await browser.close();
}
