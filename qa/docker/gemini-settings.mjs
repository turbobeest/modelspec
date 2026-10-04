// Ask the installed CLI's settings loader for method/enablement only.
import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const root = '/usr/local/lib/node_modules/@google/gemini-cli/bundle';
const pending = [path.join(root, 'gemini.js')], visited = new Set(), matches = [];
while (pending.length) {
  const file = fs.realpathSync(pending.pop());
  if (visited.has(file)) continue;
  visited.add(file);
  if (!file.startsWith(root + '/')) throw new Error('Settings module leaves package');
  const source = fs.readFileSync(file, 'utf8');
  if (/export\s*\{[^}]*\bloadSettings\b/s.test(source)) matches.push(file);
  for (const match of source.matchAll(/(?:\bfrom\s+|\bimport\s*\(?\s*)["'](\.\/[\w.-]+\.js)["']/g)) {
    const next = path.join(path.dirname(file), match[1]);
    if (fs.existsSync(next)) pending.push(next);
  }
}
if (matches.length !== 1) throw new Error('Settings export is ambiguous');
const { loadSettings, USER_SETTINGS_PATH } = await import(pathToFileURL(matches[0]).href);
const settings = loadSettings(process.cwd());
if (!Array.isArray(settings.errors) || settings.errors.length) process.exit(2);
const method = settings.merged.security?.auth?.selectedType ?? 'none';
const known = ['none', 'oauth-personal', 'gemini-api-key', 'vertex-ai', 'compute-default-credentials'];
console.log(JSON.stringify(process.argv[2] === 'auth' ? {
  selectedType: known.includes(method) ? method : 'unknown'
} : {
  skillsEnabled: settings.merged.skills?.enabled,
  hooksEnabled: settings.merged.hooksConfig?.enabled,
  hookEvents: Object.keys(settings.merged.hooks || {}),
  userSettingsPath: USER_SETTINGS_PATH
}));
