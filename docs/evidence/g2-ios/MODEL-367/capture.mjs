// Run from the engine after npm ci in web; write only to a private receipt directory.
import { chromium } from '../../../../web/node_modules/playwright/index.mjs';
import { mkdir, writeFile } from 'node:fs/promises';
import { gzipSync } from 'node:zlib';
import { createHash } from 'node:crypto';

const [out, ...targets] = process.argv.slice(2);
if (!out || !targets.length) throw new Error('Usage: capture.mjs PRIVATE_DIRECTORY label=https://x.ai/path ...');
const pages = targets.map(target => {
  const split = target.indexOf('=');
  const name = target.slice(0, split);
  const url = target.slice(split + 1);
  if (!/^[a-z-]+$/.test(name) || new URL(url).origin !== 'https://x.ai') {
    throw new Error('Expected a plain label and an x.ai HTTPS URL');
  }
  return [name, url];
});
await mkdir(out, {recursive: true});
const browser = await chromium.launch({channel: 'chromium', headless: false});
const context = await browser.newContext({viewport: {width: 1440, height: 1100}});
const manifest = {
  started_at: new Date().toISOString(), browser: await browser.version(),
  channel: 'chromium', headless: false, viewport: {width: 1440, height: 1100}, pages: [],
};
try {
  for (const [name, url] of pages) {
    const page = await context.newPage();
    try {
      const response = await page.goto(url, {waitUntil: 'domcontentloaded', timeout: 30000});
      await page.waitForLoadState('networkidle', {timeout: 5000}).catch(() => {});
      const html = Buffer.from(await page.content());
      const file = `${name}.html.gz`;
      await writeFile(`${out}/${file}`, gzipSync(html), {flag: 'wx'});
      await writeFile(`${out}/${name}.txt`, await page.locator('body').innerText(), {flag: 'wx'});
      const entry = {
        name, url, final_url: page.url(), retrieved_at: new Date().toISOString(),
        status: response?.status(), content_type: response?.headers()['content-type'],
        user_agent: await page.evaluate(() => navigator.userAgent), file, bytes: html.length,
        sha256: createHash('sha256').update(html).digest('hex'), title: await page.title(),
      };
      manifest.pages.push(entry);
      if (['pricing', 'business'].includes(name)) {
        await page.screenshot({path: `${out}/${name}.png`, fullPage: true});
        const regions = await page.locator('section > div.border-t > div.hidden')
          .evaluateAll(els => els.map(el => el.outerHTML));
        await writeFile(`${out}/${name}-regions.json`, JSON.stringify(regions, null, 2) + '\n', {flag: 'wx'});
      }
      console.log(JSON.stringify(entry));
    } finally {
      await page.close();
      await writeFile(`${out}/retrieval.json`, JSON.stringify(manifest, null, 2) + '\n');
    }
  }
} finally {
  await browser.close();
}
