import assert from "node:assert/strict";
import fs from "node:fs";
import http from "node:http";
import path from "node:path";
import { chromium } from "playwright";

const [directory, slug, screenshots] = process.argv.slice(2);
const root = path.resolve(directory);
const server = http.createServer((request, response) => {
  const pathname = new URL(request.url, "http://localhost").pathname;
  const file = path.resolve(root, `.${pathname}${pathname.endsWith("/") ? "index.html" : ""}`);
  if (!file.startsWith(root + path.sep) || !fs.existsSync(file) || !fs.statSync(file).isFile()) {
    response.writeHead(404);
    response.end();
    return;
  }
  const types = { ".html": "text/html", ".svg": "image/svg+xml", ".png": "image/png",
    ".woff2": "font/woff2", ".xml": "application/xml" };
  response.setHeader("content-type", types[path.extname(file)] ?? "application/octet-stream");
  response.end(fs.readFileSync(file));
});
await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
const address = server.address();
assert.ok(address && typeof address === "object");
const origin = `http://127.0.0.1:${address.port}`;
let browser;
try {
  browser = await chromium.launch({ headless: true });
  fs.mkdirSync(screenshots, { recursive: true });
  const results = {};
  for (const width of [390, 1440]) {
    const page = await browser.newPage({ viewport: { width, height: 1000 }, colorScheme: "light" });
    await page.route("**/*", (route) => route.request().url().startsWith(origin)
      ? route.continue() : route.abort());
    const failures = [];
    page.on("pageerror", (error) => failures.push(error.message));
    await page.goto(`${origin}/blog/${slug}/`, { waitUntil: "networkidle" });
    await page.evaluate(() => document.fonts.ready);
    results[width] = await page.evaluate(() => {
      const article = document.querySelector("article");
      const title = article.querySelector("h1");
      const titleRect = title.getBoundingClientRect();
      const graph = JSON.parse(document.querySelector('script[type="application/ld+json"]').textContent);
      const charts = [...article.querySelectorAll("img")];
      const notes = [...article.querySelectorAll('sup a[href^="#fn-"]')];
      return {
        title: title.textContent === "Alpha model release breakdown",
        dark: getComputedStyle(document.documentElement).colorScheme === "dark",
        chrome: document.querySelector("nav .lockup .wordmark").textContent === "ModelSpec",
        width: document.documentElement.scrollWidth <= document.documentElement.clientWidth,
        titleFits: titleRect.left >= 0 && titleRect.right <= window.innerWidth,
        tables: article.querySelectorAll("table").length >= 3,
        charts: charts.length === 3 && charts.every((image) => image.complete && image.naturalWidth > 0),
        notes: notes.length > 0 && notes.every((link) => document.querySelector(link.getAttribute("href"))),
        placeholders: !article.textContent.includes("{{"),
        article: graph["@graph"].some((node) => node["@type"] === "Article"),
        reproduce: [...article.querySelectorAll("h2")].some((h) => h.textContent === "Reproduce this"),
      };
    });
    results[width].noErrors = failures.length === 0;
    const card = await page.request.get(`${origin}/blog/${slug}/r1/og-card.png`);
    results[width].socialCard = card.ok() && card.headers()["content-type"] === "image/png";
    await page.screenshot({ path: path.join(screenshots, `blog-${width}-top.png`) });
    await page.screenshot({ path: path.join(screenshots, `blog-${width}.png`), fullPage: true });
    await page.close();
  }
  process.stdout.write(JSON.stringify(results));
} finally {
  if (browser) await browser.close();
  await new Promise((resolve) => server.close(resolve));
}
