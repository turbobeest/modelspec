import assert from "node:assert/strict";
import { mkdir, writeFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { chromium } from "playwright";

const origin = "http://127.0.0.1:5197";
const output = new URL("../../.scratch/proto/variant-c/", import.meta.url);
await mkdir(output, { recursive: true });
const browser = await chromium.launch();
const report = { pages: [], interactions: [] };

async function audit(page, variant, theme, width, phase = "initial") {
  await page.evaluate(() => window.scrollTo(0, 0));
  const checks = await page.evaluate(() => {
    const rgba = (value) => {
      const parts = value.match(/[\d.]+/g)?.map(Number) ?? [];
      return [parts[0] ?? 0, parts[1] ?? 0, parts[2] ?? 0, parts[3] ?? 1];
    };
    const over = (front, back) => [0, 1, 2].map((i) => front[i] * front[3] + back[i] * (1 - front[3])).concat(1);
    const luminance = (color) => color.slice(0, 3).map((n) => {
      const c = n / 255;
      return c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
    }).reduce((sum, n, i) => sum + n * [0.2126, 0.7152, 0.0722][i], 0);
    const violations = [];
    const gradients = [];
    let checked = 0;
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    while (walker.nextNode()) {
      const node = walker.currentNode;
      const text = node.textContent.trim();
      const element = node.parentElement;
      if (!element || !text || ["SCRIPT", "STYLE"].includes(element.tagName) || !element.checkVisibility({ checkOpacity: true, checkVisibilityCSS: true })) continue;
      const range = document.createRange();
      range.selectNode(node);
      const rect = range.getBoundingClientRect();
      if (!rect.width || !rect.height || rect.right < 0 || rect.bottom < 0) continue;
      const ancestors = [];
      let ancestor = element;
      let clipped = false;
      while (ancestor) {
        const style = getComputedStyle(ancestor);
        if (style.clip !== "auto" || style.clipPath !== "none") clipped = true;
        ancestors.unshift(ancestor);
        ancestor = ancestor.parentElement;
      }
      if (clipped) continue;
      let background = [255, 255, 255, 1];
      let hasGradient = false;
      for (const parent of ancestors) {
        const style = getComputedStyle(parent);
        background = over(rgba(style.backgroundColor), background);
        if (style.backgroundImage !== "none") hasGradient = true;
      }
      const style = getComputedStyle(element);
      const foreground = over(rgba(style.color), background);
      const light = luminance(foreground);
      const dark = luminance(background);
      const ratio = (Math.max(light, dark) + 0.05) / (Math.min(light, dark) + 0.05);
      checked++;
      const detail = { text: text.slice(0, 100), tag: element.tagName, class: element.className, ratio: Number(ratio.toFixed(3)), color: style.color, background, size: style.fontSize };
      if (hasGradient) gradients.push(detail);
      if (ratio < 4.5) violations.push(detail);
    }
    const overflow = [...document.querySelectorAll("body *")].filter((element) => {
      if (!element.checkVisibility()) return false;
      const rect = element.getBoundingClientRect();
      return rect.width > 0 && (rect.right > innerWidth + 1 || rect.left < -1);
    }).slice(0, 15).map((element) => ({ tag: element.tagName, class: element.className, text: element.textContent.trim().slice(0, 80), left: element.getBoundingClientRect().left, right: element.getBoundingClientRect().right }));
    return { checked, violations, gradients, scrollWidth: document.documentElement.scrollWidth, innerWidth, overflow };
  });
  report.pages.push({ variant, theme, width, phase, ...checks });
}

try {
  for (const width of [390, 1440]) {
    for (const theme of ["dark", "light"]) {
      for (const variant of ["a", "b", "c"]) {
        const page = await browser.newPage({ viewport: { width, height: width === 390 ? 844 : 900 } });
        await page.route("**/*", (route) => new URL(route.request().url()).origin === origin ? route.continue() : route.abort());
        await page.goto(`${origin}/prototypes/proto-${variant}.html?theme=${theme}`);
        if (variant !== "b") await page.locator(variant === "c" ? ".board-ranked-answer" : ".proto-shortlist").waitFor();
        await audit(page, variant, theme, width);
        if (theme === "light") await page.screenshot({ path: fileURLToPath(new URL(`${variant}-${width === 390 ? "mobile" : "desktop"}-light-fold.png`, output)) });
        if (variant === "b") {
          await page.getByRole("button", { name: /Everyday help/ }).click();
          await audit(page, variant, theme, width, "priority");
          await page.getByRole("button", { name: /Balance cost and quality/ }).click();
          await audit(page, variant, theme, width, "limit");
          await page.getByRole("button", { name: /Show my options/ }).click();
          await page.locator(".proto-shortlist").waitFor();
          await audit(page, variant, theme, width, "answer");
        }
        await page.close();
      }
    }
  }

  const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
  const requests = [];
  await page.route("**/*", (route) => new URL(route.request().url()).origin === origin ? route.continue() : route.abort());
  page.on("request", (request) => {
    if (request.url().endsWith("/v1/decide") && request.method() === "POST") requests.push(request.postDataJSON());
  });
  await page.goto(`${origin}/prototypes/proto-c.html?theme=dark`);
  await page.locator(".board-ranked-answer").waitFor();
  for (const selector of [".proto-c-refine", ".proto-c-evidence", ".proto-expander:last-child"]) {
    const details = page.locator(selector);
    const summary = details.locator(":scope > summary");
    await summary.focus();
    await page.keyboard.press("Enter");
    assert.equal(await details.evaluate((element) => element.open), true);
    await page.keyboard.press("Space");
    assert.equal(await details.evaluate((element) => element.open), false);
    report.interactions.push(`${await summary.innerText()}: Enter opens; Space closes`);
  }
  const theme = page.locator(".proto-header > button");
  await theme.focus();
  await page.keyboard.press("Enter");
  assert.equal(await page.locator(".proto").getAttribute("data-theme"), "light");
  await page.keyboard.press("Space");
  assert.equal(await page.locator(".proto").getAttribute("data-theme"), "dark");
  report.interactions.push("Theme: Enter selects light; Space selects dark");

  const before = await page.locator(".proto-c-answer").innerText();
  const previousLink = await page.getByRole("link", { name: "See the full evidence", exact: true }).getAttribute("href");
  await page.locator(".proto-c-refine > summary").focus();
  await page.keyboard.press("Enter");
  const cost = page.locator('[data-facet="offering.cost_per_task"]');
  await cost.getByRole("checkbox").focus();
  await page.keyboard.press("Space");
  const threshold = cost.getByRole("spinbutton");
  await threshold.fill("0.05");
  await threshold.press("Tab");
  await page.locator(".board-ranked-answer").waitFor();
  const after = await page.locator(".proto-c-answer").innerText();
  const link = await page.getByRole("link", { name: "See the full evidence", exact: true }).getAttribute("href");
  assert.notEqual(link, previousLink);
  assert.notEqual(after, before);
  const state = JSON.parse(decodeURIComponent(Buffer.from(link.split("#s=")[1], "base64").toString("utf8")));
  assert.equal(state.board.selections["offering.cost_per_task"].value, 0.05);
  assert.equal(state.board.selections["offering.cost_per_task"].mode, "both");
  assert(requests.at(-1).where.some((condition) => condition.includes("offering.cost_per_task <= 0.05")));
  report.interactions.push({ facet: "Cost per task", threshold: 0.05, outgoingSpec: requests.at(-1), carriedSelection: state.board.selections["offering.cost_per_task"], changedAnswer: after.slice(0, 400) });
  for (const themeName of ["dark", "light"]) {
    if (themeName === "light") await theme.click();
    await audit(page, "c", themeName, 390, "refine-open");
    await page.locator(".proto-c-refine > summary").click();
    await page.locator(".proto-c-evidence > summary").click();
    await audit(page, "c", themeName, 390, "evidence-open");
    await page.locator(".proto-c-evidence > summary").click();
    await page.locator(".proto-expander:last-child > summary").click();
    await audit(page, "c", themeName, 390, "agent-open");
    await page.locator(".proto-expander:last-child > summary").click();
    await page.locator(".proto-c-refine > summary").click();
  }
  await page.close();
  await writeFile(new URL("audit.json", output), JSON.stringify(report, null, 2));
  console.log(JSON.stringify({ pageStates: report.pages.length, contrastViolations: report.pages.flatMap((item) => item.violations.map((violation) => ({ variant: item.variant, theme: item.theme, width: item.width, phase: item.phase, ...violation }))), overflows: report.pages.filter((item) => item.scrollWidth > item.innerWidth).map((item) => ({ variant: item.variant, theme: item.theme, width: item.width, phase: item.phase, scrollWidth: item.scrollWidth, overflow: item.overflow })), interactions: report.interactions }, null, 2));
  assert.equal(report.pages.flatMap((item) => item.violations).length, 0, "Every checked text node must have at least 4.5:1 contrast");
  assert.equal(report.pages.filter((item) => item.scrollWidth > item.innerWidth).length, 0, "Page content must not overflow horizontally");
} finally {
  await browser.close();
}
