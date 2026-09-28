import { chromium } from "@playwright/test";
import { readFile, writeFile } from "node:fs/promises";
import { pathToFileURL } from "node:url";

const manifest = process.argv[2];
const reportPath = process.argv[3];
if (!manifest) throw new Error("usage: render-social-cards.mjs MANIFEST.json");

const jobs = JSON.parse(await readFile(manifest, "utf8"));
const browser = await chromium.launch({ headless: true });
try {
  const page = await browser.newPage({ viewport: { width: 1200, height: 630 } });
  const reports = [];
  for (const job of jobs) {
    await page.goto(pathToFileURL(job.source).href, { waitUntil: "load" });
    await page.evaluate(() => document.fonts.ready);
    reports.push(await page.evaluate(() => {
      const box = (selector) => {
        const element = document.querySelector(selector);
        if (!element) return null;
        const bounds = element.getBoundingClientRect();
        return {
          left: bounds.left,
          top: bounds.top,
          right: bounds.right,
          bottom: bounds.bottom,
          width: bounds.width,
          height: bounds.height,
        };
      };
      const frame = { left: 0, top: 0, right: innerWidth, bottom: innerHeight };
      const blocks = [...document.querySelectorAll("[data-content-block]")].map((element) => {
        const box = element.getBoundingClientRect();
        return {
          tag: element.tagName.toLowerCase(),
          className: element.className,
          left: box.left,
          top: box.top,
          right: box.right,
          bottom: box.bottom,
          scrollWidth: element.scrollWidth,
          clientWidth: element.clientWidth,
          scrollHeight: element.scrollHeight,
          clientHeight: element.clientHeight,
        };
      });
      const text = [...document.querySelectorAll("[data-content-block], [data-content-block] *")]
        .filter((element) => [...element.childNodes].some((node) => node.nodeType === Node.TEXT_NODE && node.textContent.trim()))
        .map((element) => ({
          tag: element.tagName.toLowerCase(),
          className: element.className?.baseVal ?? element.className,
          scrollWidth: element.scrollWidth,
          clientWidth: element.clientWidth,
          scrollHeight: element.scrollHeight,
          clientHeight: element.clientHeight,
        }));
      const details = {
        plot: box(".plot"),
        yAxis: box("[data-y-axis]"),
        yAxisLabel: box("[data-y-axis-label]"),
        cheapestPoint: box("[data-cheapest-point]"),
        cheapestCallout: box("[data-cheapest-callout]"),
        plottedCircles: [...document.querySelectorAll("[data-plot-point]")].map((element) => {
          const bounds = element.getBoundingClientRect();
          const style = getComputedStyle(element);
          return {
            left: bounds.left,
            top: bounds.top,
            right: bounds.right,
            bottom: bounds.bottom,
            width: bounds.width,
            height: bounds.height,
            tied: element.dataset.tied === "true",
            visible: style.display !== "none" && style.visibility !== "hidden"
              && Number(style.opacity) > 0 && bounds.width > 0 && bounds.height > 0,
          };
        }),
      };
      return { frame, blocks, text, details };
    }));
    await page.screenshot({ path: job.output, type: "png" });
  }
  if (reportPath) await writeFile(reportPath, JSON.stringify(reports));
} finally {
  await browser.close();
}
