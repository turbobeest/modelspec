import assert from "node:assert/strict";
import { chromium } from "playwright";

const origin = process.env.PROTO_ORIGIN ?? "http://127.0.0.1:5197";
const browser = await chromium.launch();
try {
  for (const variant of ["a", "b", "c"]) {
    const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
    await page.route("**/*", (route) => new URL(route.request().url()).origin === origin
      ? route.continue() : route.abort());
    await page.goto(`${origin}/prototypes/proto-${variant}.html`);
    assert.equal(await page.getByRole("heading", { name: "Which AI model fits your job?", exact: true }).count(), 1,
      `Variant ${variant.toUpperCase()} must offer the first-visit decision page`);
    await page.close();
  }
  console.log("PASS: all three prototype entries open on mobile");
} finally {
  await browser.close();
}
