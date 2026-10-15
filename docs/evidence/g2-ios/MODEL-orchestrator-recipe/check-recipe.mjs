// Run from the repository root after pipeline.live builds dist-live.
import assert from 'node:assert/strict';
import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { resolve, extname } from 'node:path';
import { chromium } from '../../../../web/node_modules/playwright/index.mjs';

const tree = resolve(process.argv[2] ?? 'dist-live/modelspec');
const evidence = new URL('.', import.meta.url);
const server = createServer(async (request, response) => {
  let path = new URL(request.url, 'http://localhost').pathname;
  if (path.endsWith('/')) path += 'index.html';
  try {
    const body = await readFile(resolve(tree, '.' + path));
    const type = { '.html': 'text/html', '.css': 'text/css', '.svg': 'image/svg+xml',
      '.woff2': 'font/woff2' }[extname(path)] ?? 'application/octet-stream';
    response.writeHead(200, { 'Content-Type': type });
    response.end(body);
  } catch {
    response.writeHead(404);
    response.end();
  }
});
let browser;
try {
  await new Promise(done => server.listen(0, '127.0.0.1', done));
  browser = await chromium.launch();
  console.log(`Chromium ${browser.version()}; JavaScript disabled`);
  for (const width of [1440, 390, 320]) {
    const context = await browser.newContext({ javaScriptEnabled: false,
      viewport: { width, height: 1000 } });
    const page = await context.newPage();
    const response = await page.goto(`http://127.0.0.1:${server.address().port}/orchestrators/`);
    assert.equal(response.status(), 200);
    assert.equal(await page.locator('h1').textContent(), 'Choose models for your orchestrator');
    assert.match(await page.locator('#prompt pre').textContent(), /If the CLI exits 5/);
    const overflow = await page.locator('pre').evaluateAll(blocks =>
      blocks.some(block => block.scrollWidth > block.clientWidth + 1));
    assert.equal(overflow, false, `code overflow at ${width}px`);
    await page.screenshot({ path: new URL(`recipe-${width}.png`, evidence).pathname });
    console.log(`${width}px: 200, heading and system prompt readable, no code overflow`);
    await context.close();
  }
} finally {
  if (browser) await browser.close();
  await new Promise(done => server.close(done));
}
