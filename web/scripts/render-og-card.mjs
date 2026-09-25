// Renders brand/og-card-2a.png: the light lockup from brand/2a on the decide
// page's light background, 1200x630. The PNG is committed; run this again only
// when the lockup changes. `node web/scripts/render-og-card.mjs`
import { chromium } from "@playwright/test";
import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";

const brand = new URL("../../brand/", import.meta.url);
const background = "#faf9f8"; // --bg, light theme, web/src/decide/decide.css
const lockup = (
  await readFile(new URL("2a/modelspec-lockup-light.svg", brand), "utf8")
)
  .replace(/<metadata>[\s\S]*?<\/metadata>/, "")
  // The lockup's own white plate would show as a box on the page background.
  .replace(/<rect width="200" height="48" fill="#FFFFFF"><\/rect>/, "")
  .replace(/width="800" height="192"/, 'width="960" height="230"');

// The wordmark ends well short of the lockup's right edge, so the margin
// centres the ink rather than the box.
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1200, height: 630 } });
await page.setContent(
  `<!doctype html><html><body style="margin:0;width:1200px;height:630px;` +
    `display:grid;place-items:center;background:${background}">` +
    `<div style="margin-left:210px">${lockup}</div></body></html>`,
);
await page.screenshot({
  path: fileURLToPath(new URL("og-card-2a.png", brand)),
  type: "png",
});
await browser.close();
