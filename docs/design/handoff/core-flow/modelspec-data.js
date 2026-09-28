// ModelSpec sample catalogue + decision engine. ALL DATA IS FICTIONAL.
export const TODAY = '2026-09-24';
export const TYPES = { llm: 'LLM', embed: 'Embedding', rerank: 'Reranker', vision: 'Vision', speech: 'Speech', decision: 'Decision model' };
export const BENCH = {
  'CodeBench Pro': { unit: '% resolved', pct: true, d: 1, hi: true, types: ['llm'] },
  'TermTasks 4': { unit: '% tasks passed', pct: true, d: 1, hi: true, types: ['llm'] },
  'ReasonHard': { unit: '% accuracy', pct: true, d: 1, hi: true, types: ['llm'] },
  'RetrievalEval v2': { unit: 'nDCG@10', d: 3, hi: true, types: ['embed', 'rerank'] },
  'ChartRead': { unit: '% accuracy', pct: true, d: 1, hi: true, types: ['vision'] },
  'VoxWER': { unit: '% word error rate', pct: true, d: 1, hi: false, types: ['speech'] },
  'IntentRoute': { unit: 'macro-F1', d: 2, hi: true, types: ['decision'] },
};
export const LABS = {
  halden: { name: 'Halden Labs', origin: 'US', cloud: 'Halden Cloud', regions: ['us-east', 'eu-west'] },
  norrow: { name: 'Norrow', origin: 'EU', cloud: 'Norrow Platform', regions: ['eu-west'] },
  kestrel: { name: 'Kestrel AI', origin: 'US', cloud: 'Kestrel API', regions: ['us-east', 'us-west'] },
  quillon: { name: 'Quillon', origin: 'UK', cloud: 'Quillon Cloud', regions: ['uk-south'] },
  meridian: { name: 'Meridian Compute', origin: 'SG', cloud: 'Meridian Cloud', regions: ['ap-southeast'] },
  oban: { name: 'Oban Research', origin: 'CA', cloud: 'Oban API', regions: ['ca-central', 'us-east'] },
};
export const HOSTS = {
  stratus: { name: 'Stratus', regions: ['us-east', 'eu-west'], pm: 1.1, ttft: 80, tpsm: 0.95, ret: 0 },
  fernway: { name: 'Fernway', regions: ['eu-west', 'eu-central'], pm: 1.2, ttft: 120, tpsm: 0.9, ret: 0 },
  pylon: { name: 'Pylon', regions: ['us-west', 'ap-southeast'], pm: 1.3, ttftm: 0.6, tpsm: 1.8, ret: 30 },
  arcgrid: { name: 'Arcgrid', regions: ['us-east'], pm: 0.8, ttft: 300, tpsm: 0.8, ret: 'contract' },
};
const EVAL = 'Harbor Evals';
const r = (b, v, ci, by, date, effort = 'default', harness = 'standard') => ({ b, v, ci, by, date, effort, harness });

const RAW = [
  ['halden-atlas-3', 'Atlas 3', 'halden', 'llm', { open: false, lic: 'Proprietary', commercial: true, ctx: 1000000, rel: '2026-05-14', in: 3, out: 15, ttft: 900, tps: 85, hosts: ['stratus', 'arcgrid'],
    bench: [r('CodeBench Pro', 66.1, null, 'lab', '2026-05-14', 'high', 'Halden agent harness'), r('CodeBench Pro', 62.4, 1.8, 'indep', '2026-06-20'), r('TermTasks 4', 48.2, 2.5, 'indep', '2026-06-22'), r('ReasonHard', 71.0, null, 'lab', '2026-05-14')] }],
  ['halden-atlas-3-mini', 'Atlas 3 Mini', 'halden', 'llm', { open: false, lic: 'Proprietary', commercial: true, ctx: 400000, rel: '2026-05-14', in: 0.4, out: 1.6, ttft: 350, tps: 190, hosts: ['stratus', 'pylon', 'arcgrid'],
    bench: [r('CodeBench Pro', 52.0, null, 'lab', '2026-05-14'), r('CodeBench Pro', 49.8, 2.0, 'indep', '2026-06-20'), r('TermTasks 4', 35.1, 2.8, 'indep', '2026-06-22'), r('ReasonHard', 58.3, null, 'lab', '2026-05-14')] }],
  ['halden-atlas-2-5', 'Atlas 2.5', 'halden', 'llm', { open: false, lic: 'Proprietary', commercial: true, ctx: 200000, rel: '2025-09-02', status: 'retired', retiredOn: '2026-03-31', in: 2.5, out: 10, ttft: 1100, tps: 60, hosts: ['stratus'],
    bench: [r('CodeBench Pro', 51.2, 2.1, 'indep', '2025-10-11'), r('ReasonHard', 60.4, 1.9, 'indep', '2025-10-11')] }],
  ['halden-embed-3', 'Halden Embed 3', 'halden', 'embed', { open: false, lic: 'Proprietary', commercial: true, ctx: 32000, rel: '2026-02-03', in: 0.13, out: null, ttft: 120, tps: null, hosts: ['stratus'],
    bench: [r('RetrievalEval v2', 0.655, null, 'lab', '2026-02-03'), r('RetrievalEval v2', 0.641, 0.008, 'indep', '2026-03-01')] }],
  ['norrow-fjord-l', 'Fjord L', 'norrow', 'llm', { open: true, lic: 'Apache-2.0', commercial: true, ctx: 256000, rel: '2026-04-08', in: 0.9, out: 2.7, ttft: 600, tps: 110, hosts: ['fernway', 'stratus', 'pylon'],
    bench: [r('CodeBench Pro', 57.0, null, 'lab', '2026-04-08'), r('CodeBench Pro', 55.1, 2.0, 'indep', '2026-05-02'), r('TermTasks 4', 40.2, 2.9, 'indep', '2026-05-04'), r('ReasonHard', 64.0, null, 'lab', '2026-04-08')] }],
  ['norrow-fjord-s', 'Fjord S', 'norrow', 'llm', { open: true, lic: 'Apache-2.0', commercial: true, ctx: 128000, rel: '2026-04-08', in: 0.15, out: 0.45, ttft: 220, tps: 280, hosts: ['fernway', 'pylon'],
    bench: [r('CodeBench Pro', 38.4, 2.4, 'indep', '2026-05-02'), r('ReasonHard', 47.0, 2.2, 'indep', '2026-05-02')] }],
  ['norrow-fjord-code', 'Fjord Code', 'norrow', 'llm', { open: true, lic: 'Norrow Community Licence', commercial: true, ctx: 256000, rel: '2026-07-01', in: 0.6, out: 1.8, ttft: 480, tps: 140, hosts: ['fernway', 'stratus', 'arcgrid'],
    bench: [r('CodeBench Pro', 60.5, null, 'lab', '2026-07-01'), r('CodeBench Pro', 57.9, 2.2, 'indep', '2026-07-19'), r('TermTasks 4', 43.0, null, 'lab', '2026-07-01')] }],
  ['norrow-fjord-embed', 'Fjord Embed', 'norrow', 'embed', { open: true, lic: 'Apache-2.0', commercial: true, ctx: 32000, rel: '2026-04-08', in: 0.05, out: null, ttft: 140, tps: null, hosts: ['fernway'],
    bench: [r('RetrievalEval v2', 0.618, 0.009, 'indep', '2026-05-02')] }],
  ['norrow-gate-1', 'Gate-1', 'norrow', 'decision', { open: true, lic: 'Apache-2.0', commercial: true, ctx: 32000, rel: '2026-06-10', in: 0.05, out: 0.2, ttft: 150, tps: 400, hosts: ['fernway'],
    bench: [r('IntentRoute', 0.88, null, 'lab', '2026-06-10')] }],
  ['kestrel-talon-2', 'Talon 2', 'kestrel', 'llm', { open: false, lic: 'Proprietary', commercial: true, ctx: 500000, rel: '2026-06-03', in: 0.7, out: 2.8, ttft: 700, tps: 120, hosts: ['stratus', 'pylon'],
    bench: [r('CodeBench Pro', 61.0, null, 'lab', '2026-06-03', 'high'), r('CodeBench Pro', 57.4, 2.1, 'indep', '2026-06-28'), r('TermTasks 4', 44.6, 2.6, 'indep', '2026-06-29'), r('ReasonHard', 69.0, null, 'lab', '2026-06-03')] }],
  ['kestrel-talon-2-flash', 'Talon 2 Flash', 'kestrel', 'llm', { open: false, lic: 'Proprietary', commercial: true, ctx: 500000, rel: '2026-06-03', in: 0.25, out: 1.0, ttft: 250, tps: 320, hosts: ['stratus', 'pylon'],
    bench: [r('CodeBench Pro', 44.0, 2.3, 'indep', '2026-06-28'), r('TermTasks 4', 31.0, 2.9, 'indep', '2026-06-29')] }],
  ['kestrel-talon-2-deep', 'Talon 2 Deep', 'kestrel', 'llm', { open: false, lic: 'Proprietary', commercial: true, ctx: 500000, rel: '2026-06-03', in: 5, out: 25, ttft: 1800, tps: 55, hosts: ['stratus'],
    bench: [r('CodeBench Pro', 67.2, null, 'lab', '2026-06-03', 'high'), r('CodeBench Pro', 63.1, 1.9, 'indep', '2026-06-28', 'high'), r('ReasonHard', 76.5, 1.5, 'indep', '2026-06-29', 'high')] }],
  ['kestrel-wren-7b', 'Wren 7B', 'kestrel', 'llm', { open: true, lic: 'MIT', commercial: true, ctx: 32000, rel: '2026-03-12', in: 0.05, out: 0.2, ttft: 150, tps: 400, hosts: ['pylon', 'arcgrid'],
    bench: [r('CodeBench Pro', 21.3, null, 'lab', '2026-03-12'), r('ReasonHard', 30.0, null, 'lab', '2026-03-12')] }],
  ['kestrel-rerank-2', 'Rerank 2', 'kestrel', 'rerank', { open: false, lic: 'Proprietary', commercial: true, ctx: 32000, rel: '2026-01-20', in: 0.05, out: null, ttft: 180, tps: null, hosts: ['stratus'],
    bench: [r('RetrievalEval v2', 0.702, 0.007, 'indep', '2026-02-14', 'default', 'rerank top-100 from BM25')] }],
  ['quillon-q-prime', 'Q-Prime', 'quillon', 'llm', { open: false, lic: 'Proprietary', commercial: true, ctx: 2000000, rel: '2026-04-22', in: 15, out: 75, ttft: 2500, tps: 35, hosts: ['stratus'],
    bench: [r('CodeBench Pro', 68.0, null, 'lab', '2026-04-22', 'high'), r('CodeBench Pro', 65.8, 1.6, 'indep', '2026-05-15'), r('TermTasks 4', 52.3, 2.4, 'indep', '2026-05-16'), r('ReasonHard', 79.1, 1.4, 'indep', '2026-05-16')] }],
  ['quillon-q-swift', 'Q-Swift', 'quillon', 'llm', { open: false, lic: 'Proprietary', commercial: true, ctx: 200000, rel: '2026-04-22', in: 0.8, out: 3.2, ttft: 400, tps: 160, hosts: ['stratus'], fpRegions: null, hostRegions: ['us-east'],
    bench: [r('CodeBench Pro', 50.5, 2.2, 'indep', '2026-05-15'), r('TermTasks 4', 38.0, null, 'lab', '2026-04-22')] }],
  ['quillon-q-edge-3b', 'Q-Edge 3B', 'quillon', 'llm', { open: true, lic: 'Quillon Open Licence (non-commercial)', commercial: false, ctx: 32000, rel: '2026-02-11', in: 0.06, out: 0.24, ttft: 160, tps: 380, hosts: ['pylon'],
    bench: [r('CodeBench Pro', 18.2, 2.5, 'indep', '2026-03-05')] }],
  ['meridian-tide-4', 'Tide 4', 'meridian', 'llm', { open: true, lic: 'Tide Licence v2', commercial: true, ctx: 256000, rel: '2026-05-30', in: 0.35, out: 1.2, ttft: 800, tps: 90, hosts: ['pylon', 'stratus', 'arcgrid'], fpRet: null,
    bench: [r('CodeBench Pro', 53.0, 2.6, 'indep', '2026-06-25'), r('TermTasks 4', 37.5, 3.0, 'indep', '2026-06-26'), r('ReasonHard', 62.0, null, 'lab', '2026-05-30')] }],
  ['meridian-tide-4-reason', 'Tide 4 Reason', 'meridian', 'llm', { open: true, lic: 'Tide Licence v2', commercial: true, ctx: 128000, rel: '2026-05-30', in: 0.7, out: 2.8, ttft: 2100, tps: 45, hosts: ['pylon'],
    bench: [r('CodeBench Pro', 56.2, 2.4, 'indep', '2026-06-25', 'high'), r('ReasonHard', 74.0, 1.8, 'indep', '2026-06-26', 'high')] }],
  ['meridian-tide-4-mini', 'Tide 4 Mini', 'meridian', 'llm', { open: true, lic: 'Tide Licence v2', commercial: true, ctx: 64000, rel: '2026-05-30', in: 0.08, out: 0.3, ttft: 200, tps: 300, hosts: ['pylon'],
    bench: [r('CodeBench Pro', 30.2, 2.7, 'indep', '2026-06-25')] }],
  ['meridian-anchor-embed', 'Anchor Embed', 'meridian', 'embed', { open: true, lic: 'Tide Licence v2', commercial: true, ctx: 32000, rel: '2026-03-18', in: 0.06, out: null, ttft: 160, tps: null, hosts: [], fpRegions: null,
    bench: [r('RetrievalEval v2', 0.598, 0.010, 'indep', '2026-04-10')] }],
  ['meridian-lens-2', 'Lens 2', 'meridian', 'vision', { open: false, lic: 'Proprietary', commercial: true, ctx: 128000, rel: '2026-07-14', in: 1.2, out: 4.8, ttft: 650, tps: 95, hosts: ['stratus'],
    bench: [r('ChartRead', 84.0, null, 'lab', '2026-07-14'), r('ChartRead', 81.2, 1.5, 'indep', '2026-08-02')] }],
  ['oban-cairn-1', 'Cairn 1', 'oban', 'llm', { open: false, lic: 'Proprietary', commercial: true, ctx: 1000000, rel: '2026-09-22', provisional: true, in: 1.0, out: 4.0, ttft: null, tps: null, hosts: [],
    bench: [r('CodeBench Pro', 64.0, null, 'lab', '2026-09-22', 'high', 'Oban agent harness'), r('TermTasks 4', 51.0, null, 'lab', '2026-09-22', 'high'), r('ReasonHard', 76.0, null, 'lab', '2026-09-22', 'high')] }],
  ['oban-birch', 'Birch', 'oban', 'llm', { open: false, lic: 'Proprietary', commercial: true, ctx: 128000, rel: '2026-01-28', in: 0.3, out: 1.2, ttft: 300, tps: 210, hosts: ['stratus'],
    bench: [r('CodeBench Pro', 41.7, 2.3, 'indep', '2026-02-20'), r('ReasonHard', 55.0, 2.1, 'indep', '2026-02-20')] }],
  ['oban-echo', 'Echo', 'oban', 'speech', { open: false, lic: 'Proprietary', commercial: true, ctx: null, rel: '2026-04-30', in: 0.5, out: 2.0, ttft: 300, tps: null, hosts: [],
    bench: [r('VoxWER', 5.8, 0.3, 'indep', '2026-05-21')] }],
];

const rp = x => Number(x.toPrecision(2));
const slug = s => s.toLowerCase().replace(/[^a-z0-9]+/g, '-');
export function buildCatalogue() {
  const models = RAW.map(([id, name, lab, type, o]) => {
    const L = LABS[lab];
    const m = { id, name, lab, labName: L.name, origin: L.origin, type, status: 'active', ...o };
    m.bench = m.bench.map(x => ({ ...x, who: x.by === 'indep' ? EVAL : L.name, src: x.by === 'indep' ? `https://harbor-evals.example/${slug(x.b)}/${id}` : `https://${lab}.example/research/${id}` }));
    const offs = [{ id: id + '@fp', provider: L.cloud, first: true, regions: m.fpRegions === undefined ? L.regions : m.fpRegions, in: m.in, out: m.out, ttft: m.ttft, tps: m.tps, ret: m.fpRet === undefined ? 30 : m.fpRet }];
    (m.hosts || []).forEach(h => {
      const H = HOSTS[h];
      offs.push({ id: id + '@' + h, provider: H.name, regions: m.hostRegions || H.regions, in: rp(m.in * H.pm), out: m.out == null ? null : rp(m.out * H.pm),
        ttft: m.ttft == null ? null : Math.round(H.ttftm ? m.ttft * H.ttftm : m.ttft + H.ttft), tps: m.tps == null ? null : Math.round(m.tps * H.tpsm), ret: H.ret });
    });
    m.offerings = offs;
    return m;
  });
  const byId = Object.fromEntries(models.map(m => [m.id, m]));
  return { models, byId, offerings: models.reduce((a, m) => a + m.offerings.length, 0), labs: Object.keys(LABS).length };
}

// ---------- formatting
export const fmtB = (b, v) => v == null ? '—' : v.toFixed(BENCH[b].d) + (BENCH[b].pct ? '%' : '');
export const fmtCI = (b, r) => r.ci == null ? '' : '± ' + r.ci.toFixed(BENCH[b].d);
export const money = k => k == null ? 'unknown' : k < 0.01 ? '$' + k.toFixed(4) : k < 1 ? '$' + k.toFixed(3) : '$' + k.toFixed(2);
export const per1M = p => p == null ? '—' : '$' + (p < 1 ? p.toFixed(2) : p.toFixed(2));
export const tok = n => n == null ? 'unknown' : n >= 1e6 ? (n / 1e6) + 'M' : Math.round(n / 1000) + 'K';
export const num = n => n == null ? '—' : n.toLocaleString('en-US');
export const daysAgo = d => Math.round((new Date(TODAY) - new Date(d)) / 864e5);

// ---------- conditions
const P = { s: 1 }, un = why => ({ s: 0, why }), fl = why => ({ s: -1, why });
const regionIn = (r, v) => v === 'EU' ? /^eu-/.test(r) : v === 'US' ? /^us-/.test(r) : v === 'UK' ? /^uk-/.test(r) : false;
export const offCost = (o, spec) => o.in == null ? null : (o.in * spec.tokIn + (o.out || 0) * spec.tokOut) / 1e6;
export function benchVal(m, b, indepOnly) {
  const rs = m.bench.filter(x => x.b === b);
  const ind = rs.find(x => x.by === 'indep');
  if (ind) return ind;
  return indepOnly ? null : (rs[0] || null);
}
const cmpB = (b, v, floor) => BENCH[b].hi ? v >= floor : v <= floor;

export function condLabel(c, D) {
  switch (c.f) {
    case 'type': return 'Type: ' + TYPES[c.v];
    case 'active': return 'Offered now';
    case 'ctx': return 'Context ≥ ' + tok(c.min) + ' tokens';
    case 'open': return c.v === false ? 'Open weights: exclude' : 'Open weights: require';
    case 'commercial': return 'Licence allows commercial use';
    case 'bench': return `${c.b} ${BENCH[c.b].hi ? '≥' : '≤'} ${fmtB(c.b, c.min)}${c.indep ? ' · independent' : ''}`;
    case 'task$': return '≤ ' + money(c.max) + ' per task';
    case 'in$': return 'Input ≤ ' + per1M(c.max) + ' / 1M tokens';
    case 'resid': return 'Data residency: ' + c.v;
    case 'ret0': return 'Data retention: 0 days';
    case 'ttft': return 'First token ≤ ' + num(c.max) + ' ms';
    case 'tps': return 'Throughput ≥ ' + num(c.min) + ' tokens/s';
    case 'origin': return 'Origin: exclude ' + c.ex.join(', ');
    case 'rel': return `≥ ${D.byId[c.ref].name} on ${c.b}, and cheaper`;
  }
  return c.f;
}

function testCond(c, m, o, spec, D) {
  switch (c.f) {
    case 'type': return m.type === c.v ? P : fl(`${TYPES[m.type]}, not ${TYPES[c.v]}`);
    case 'active': return m.status === 'retired' ? fl(`retired ${m.retiredOn}, in the live archive`) : P;
    case 'ctx': return m.ctx == null ? un('context length not published') : m.ctx >= c.min ? P : fl(`context ${tok(m.ctx)}, you need ${tok(c.min)}`);
    case 'open': return m.open === (c.v !== false) ? P : fl(m.open ? 'open weights, which you excluded' : 'closed weights');
    case 'commercial': return m.commercial == null ? un('licence terms unclear') : m.commercial ? P : fl(`${m.lic} forbids commercial use`);
    case 'bench': {
      const x = benchVal(m, c.b, c.indep);
      if (!x) { const any = benchVal(m, c.b, false); return any ? un(`no independent ${c.b} yet; lab reports ${fmtB(c.b, any.v)}`) : un(`no ${c.b} result`); }
      return cmpB(c.b, x.v, c.min) ? P : fl(`${c.b} ${fmtB(c.b, x.v)}, your floor is ${fmtB(c.b, c.min)}`);
    }
    case 'task$': { const k = offCost(o, spec); return k == null ? un('price not published') : k <= c.max ? P : fl(`${money(k)} per task, your cap is ${money(c.max)}`); }
    case 'in$': return o.in == null ? un('price not published') : o.in <= c.max ? P : fl(`input ${per1M(o.in)}/1M, your cap is ${per1M(c.max)}`);
    case 'resid': return o.regions == null ? un(`${c.v} data residency not stated`) : o.regions.some(x => regionIn(x, c.v)) ? P : fl(`served from ${o.regions.join(', ')}; no ${c.v} region`);
    case 'ret0': return o.ret == null ? un('retention terms not published') : o.ret === 0 ? P : o.ret === 'contract' ? fl('0-day retention needs an enterprise contract') : fl(`retains data ${o.ret} days`);
    case 'ttft': return o.ttft == null ? un('time to first token not yet measured') : o.ttft <= c.max ? P : fl(`first token ${num(o.ttft)} ms, your cap is ${num(c.max)} ms`);
    case 'tps': return o.tps == null ? un('throughput not yet measured') : o.tps >= c.min ? P : fl(`${o.tps} tokens/s, you need ${c.min}`);
    case 'origin': return c.ex.includes(m.origin) ? fl(`origin ${m.origin}, which you excluded`) : P;
    case 'rel': {
      const X = D.byId[c.ref]; if (X.id === m.id) return fl('this is the reference model');
      const xb = benchVal(X, c.b, false), mb = benchVal(m, c.b, false);
      if (!mb) return un(`no ${c.b} result`);
      const xc = Math.min(...X.offerings.map(q => offCost(q, spec)).filter(v => v != null)), mc = offCost(o, spec);
      if (!cmpB(c.b, mb.v, xb.v)) return fl(`${c.b} ${fmtB(c.b, mb.v)}, below ${X.name}'s ${fmtB(c.b, xb.v)}`);
      if (mc == null) return un('price not published');
      return mc < xc ? P : fl(`${money(mc)} per task, not cheaper than ${X.name} (${money(xc)})`);
    }
  }
  return P;
}

export function relaxValue(c, m, o, spec) {
  const up = (v, s) => Math.ceil(v / s) * s, dn = (v, s) => Math.floor(v / s) * s;
  switch (c.f) {
    case 'ctx': return m.ctx != null ? { ...c, min: m.ctx } : null;
    case 'bench': { const x = benchVal(m, c.b, c.indep); return x ? { ...c, min: BENCH[c.b].hi ? dn(x.v, BENCH[c.b].d === 3 ? 0.005 : 0.5) : up(x.v, 0.5) } : null; }
    case 'task$': { const k = offCost(o, spec); return k != null ? { ...c, max: Math.ceil(k * 1000) / 1000 } : null; }
    case 'in$': return { ...c, max: o.in };
    case 'ttft': return o.ttft != null ? { ...c, max: up(o.ttft, 50) } : null;
    case 'tps': return o.tps != null ? { ...c, min: dn(o.tps, 5) } : null;
  }
  return null;
}

// ---------- evaluation
export function evaluate(D, spec, opt = {}) {
  const conds = spec.conds;
  const w = spec.w, B = spec.bench;
  const speedFirst = w.speed > w.cost;
  const rows = D.models.map(m => {
    const offs = m.offerings.map(o => {
      const t = conds.map(c => testCond(c, m, o, spec, D));
      const fails = [], unks = [], softs = [];
      t.forEach((x, i) => { if (x.s === -1) (conds[i].soft ? softs : fails).push(i); else if (x.s === 0) unks.push(i); });
      return { o, t, fails, unks, softs, s: fails.length ? -1 : unks.length ? 0 : 1, cost: offCost(o, spec) };
    });
    const status = Math.max(...offs.map(x => x.s));
    const pool = offs.filter(x => x.s === status);
    pool.sort((a, b) => a.fails.length - b.fails.length || a.softs.length - b.softs.length || (speedFirst ? (b.o.tps || 0) - (a.o.tps || 0) : (a.cost ?? 1e9) - (b.cost ?? 1e9)));
    const best = pool[0];
    // step at which the model drops out (prefix evaluation)
    let dropAt = -1, mayFrom = -1;
    for (let i = 0; i < conds.length && dropAt < 0; i++) {
      const alive = offs.some(x => x.t.slice(0, i + 1).every((q, j) => q.s !== -1 || conds[j].soft));
      if (!alive) dropAt = i;
    }
    const capR = benchVal(m, B, false);
    return { m, offs, status, best, dropAt, capR, cap: capR ? capR.v : null, cost: best.cost, tps: best.o.tps, labOnly: capR && capR.by === 'lab' };
  });
  const typeCond = conds.findIndex(c => c.f === 'type');
  const inScope = rows.filter(x => typeCond < 0 || x.dropAt !== typeCond);
  let feasible = rows.filter(x => x.status === 1);
  const unranked = feasible.filter(x => x.cap == null);
  feasible = feasible.filter(x => x.cap != null);
  const may = rows.filter(x => x.status === 0).concat(unranked.map(x => ({ ...x, unrankedWhy: `no ${B} result to rank on` })));
  const excluded = rows.filter(x => x.status === -1);
  rank(feasible, w, B);

  // funnel
  const funnel = [{ label: 'Sample catalogue', n: D.models.length, may: 0 }];
  conds.forEach((c, i) => {
    const alive = rows.filter(x => x.dropAt < 0 || x.dropAt > i);
    const mayN = alive.filter(x => !x.offs.some(o => o.t.slice(0, i + 1).every((q, j) => q.s === 1 || (q.s === -1 && conds[j].soft)))).length;
    funnel.push({ label: condLabel(c, D), n: alive.length, may: mayN, idx: i });
  });

  const out = { rows, inScope, feasible, may, excluded, funnel };
  if (opt.lite) return out;

  // frontier (cost low, cap high)
  const hiB = BENCH[B].hi;
  const byCost = feasible.filter(x => x.cost != null).slice().sort((a, b) => a.cost - b.cost || (hiB ? b.cap - a.cap : a.cap - b.cap));
  let bestCap = hiB ? -Infinity : Infinity; const frontier = [];
  byCost.forEach(x => { if (hiB ? x.cap > bestCap : x.cap < bestCap) { frontier.push(x.m.id); bestCap = x.cap; } });
  out.frontier = frontier;

  // shortlist
  const top = feasible[0];
  const value = feasible.filter(x => x.cost > 0).slice().sort((a, b) => (b.cap / b.cost) - (a.cap / a.cost))[0];
  const bar = spec.bar ?? (conds.find(c => c.f === 'bench' && c.b === B)?.min) ?? null;
  const clears = feasible.filter(x => bar == null || cmpB(B, x.cap, bar)).sort((a, b) => a.cost - b.cost)[0];
  const open = feasible.find(x => x.m.open);
  out.shortlist = { top, value, clears, open, bar };
  // not separable
  const insep = r0 => !r0 ? [] : feasible.filter(x => x !== r0 && x.capR.ci != null && r0.capR.ci != null && Math.abs(x.cap - r0.cap) < Math.hypot(x.capR.ci, r0.capR.ci) && x.cost / r0.cost < 2 && r0.cost / x.cost < 2);
  out.insep = insep;

  // near misses
  out.nearMisses = excluded.filter(x => x.dropAt !== typeCond && conds[x.dropAt]?.f !== 'active').map(x => {
    const cand = x.offs.filter(o => o.fails.length === 1).sort((a, b) => (a.cost ?? 1e9) - (b.cost ?? 1e9))[0];
    if (!cand) return null;
    const ci = cand.fails[0], c = conds[ci];
    return { row: x, ci, cond: c, why: cand.t[ci].why, relaxed: relaxValue(c, x.m, cand.o, spec), off: cand };
  }).filter(Boolean).sort((a, b) => (hiB ? (b.row.cap ?? 0) - (a.row.cap ?? 0) : 0));

  // constraint cost
  const maxCap = arr => arr.length ? (hiB ? Math.max(...arr.map(x => x.cap)) : Math.min(...arr.map(x => x.cap))) : null;
  const nowMax = maxCap(feasible);
  out.costs = conds.map((c, i) => {
    if (c.f === 'type' || c.f === 'active') return null;
    const alt = evaluate(D, { ...spec, conds: conds.filter((_, j) => j !== i) }, { lite: true });
    const altMax = maxCap(alt.feasible);
    const bestAlt = alt.feasible.slice().sort((a, b) => hiB ? b.cap - a.cap : a.cap - b.cap)[0];
    return { i, c, label: condLabel(c, D), pts: altMax == null || nowMax == null ? null : Math.abs(altMax - nowMax), unlocks: alt.feasible.length - feasible.length, bestAlt };
  }).filter(Boolean);

  // tipping point on cost weight
  if (top) {
    const others = w.cap + w.speed || 1;
    const topAt = wc => { const ww = { cost: wc, cap: (1 - wc) * (w.cap / others), speed: (1 - wc) * (w.speed / others) }; const f = feasible.slice(); rank(f, ww, B, true); return f[0]; };
    let lo = null, hi = null;
    for (let k = Math.round(w.cost * 100); k <= 100; k++) { const t = topAt(k / 100); if (t.m.id !== top.m.id) { hi = { at: k / 100, who: t }; break; } }
    for (let k = Math.round(w.cost * 100); k >= 0; k--) { const t = topAt(k / 100); if (t.m.id !== top.m.id) { lo = { at: k / 100, who: t }; break; } }
    out.tip = { lo, hi };
  }
  return out;
}

function rank(arr, w, B, quiet) {
  if (!arr.length) return;
  const hiB = BENCH[B].hi;
  const caps = arr.map(x => x.cap), lc = arr.map(x => Math.log(Math.max(x.cost ?? 1, 1e-6))), sp = arr.map(x => x.tps).filter(v => v != null);
  const n = (v, a, b) => b - a < 1e-9 ? 1 : (v - a) / (b - a);
  const cMin = Math.min(...caps), cMax = Math.max(...caps), kMin = Math.min(...lc), kMax = Math.max(...lc), sMin = Math.min(...sp), sMax = Math.max(...sp);
  arr.forEach((x, i) => {
    const nc = hiB ? n(x.cap, cMin, cMax) : 1 - n(x.cap, cMin, cMax);
    const nk = 1 - n(lc[i], kMin, kMax);
    const ns = x.tps == null ? 0 : n(x.tps, sMin, sMax);
    const parts = { cap: w.cap * nc, cost: w.cost * nk, speed: w.speed * ns };
    const sc = parts.cap + parts.cost + parts.speed;
    if (quiet) x._q = sc; else { x.score = sc; x.parts = parts; x.norm = { cap: nc, cost: nk, speed: ns }; }
  });
  arr.sort((a, b) => quiet ? b._q - a._q : b.score - a.score);
  if (!quiet) arr.forEach((x, i) => x.rank = i + 1);
}

// ---------- clarifying questions (ordered by how much they'd narrow)
export function suggestions(D, spec, dismissed) {
  const has = f => spec.conds.some(c => c.f === f);
  const type = spec.conds.find(c => c.f === 'type')?.v || 'llm';
  const Q = [];
  if (!has('task$')) Q.push({ id: 'task$', q: 'What can you spend per task?', opts: [0.02, 0.05, 0.1].map(v => ({ label: '≤ ' + money(v), c: { f: 'task$', max: v } })) });
  if (!has('resid')) Q.push({ id: 'resid', q: 'Must data be processed in the EU?', opts: [{ label: 'Yes, EU only', c: { f: 'resid', v: 'EU' } }] });
  if (!has('open')) Q.push({ id: 'open', q: 'Do you need open weights?', opts: [{ label: 'Yes', c: { f: 'open', v: true } }] });
  if (!has('ret0')) Q.push({ id: 'ret0', q: 'Do you need 0-day data retention?', opts: [{ label: 'Yes', c: { f: 'ret0' } }] });
  if (type === 'llm' && !has('ttft')) Q.push({ id: 'ttft', q: 'How soon must the first token arrive?', opts: [500, 1000].map(v => ({ label: '≤ ' + num(v) + ' ms', c: { f: 'ttft', max: v } })) });
  if (!has('commercial')) Q.push({ id: 'commercial', q: 'Is this for commercial use?', opts: [{ label: 'Yes', c: { f: 'commercial' } }] });
  const base = evaluate(D, spec, { lite: true });
  const baseN = base.feasible.length + base.may.length;
  return Q.filter(q => !dismissed.includes(q.id)).map(q => {
    q.opts.forEach(o => { const e = evaluate(D, { ...spec, conds: spec.conds.concat(o.c) }, { lite: true }); o.n = e.feasible.length; o.may = e.may.length; o.removes = baseN - (o.n + o.may); });
    q.gain = Math.max(...q.opts.map(o => o.removes));
    return q;
  }).sort((a, b) => b.gain - a.gain);
}

// ---------- plain-language parse (deterministic keyword classifier stand-in)
export function parseTask(text) {
  const t = (text || '').toLowerCase();
  const trace = [];
  const hit = (re, note) => { const m = t.match(re); if (m) trace.push({ word: m[0], note }); return !!m; };
  let type = 'llm', bench = 'CodeBench Pro';
  if (hit(/rerank\w*/, 'type: reranker')) { type = 'rerank'; bench = 'RetrievalEval v2'; }
  else if (hit(/embed\w*|retrieval|semantic search|\brag\b/, 'type: embedding')) { type = 'embed'; bench = 'RetrievalEval v2'; }
  else if (hit(/transcri\w*|speech|audio/, 'type: speech')) { type = 'speech'; bench = 'VoxWER'; }
  else if (hit(/chart\w*|image\w*|vision|screenshot\w*/, 'type: vision')) { type = 'vision'; bench = 'ChartRead'; }
  else if (hit(/terminal|shell|devops|cli\b/, 'rank on TermTasks 4')) bench = 'TermTasks 4';
  else if (hit(/math\w*|reason\w*|proof\w*/, 'rank on ReasonHard')) bench = 'ReasonHard';
  else hit(/refactor\w*|rust|code\w*|bug\w*|repo\w*|test\w*|typescript|python/, 'rank on CodeBench Pro');
  const conds = [{ f: 'type', v: type, from: true }, { f: 'active', from: true }];
  const w = { cap: 0.6, cost: 0.3, speed: 0.1 };
  if (hit(/large|codebase|monorepo|long/, 'context ≥ 200K')) conds.push({ f: 'ctx', min: 200000, from: true });
  if (hit(/precision|precise|accura\w*|correct\w*|matters/, `${bench} floor, measured independently`)) { conds.push({ f: 'bench', b: bench, min: bench === 'CodeBench Pro' ? 50 : bench === 'RetrievalEval v2' ? 0.6 : 50, indep: true, from: true }); w.cap = 0.7; w.cost = 0.2; w.speed = 0.1; }
  if (hit(/cheap\w*|budget|low.cost/, 'weight cost higher')) { w.cap = 0.5; w.cost = 0.4; w.speed = 0.1; }
  if (hit(/fast|latency|real.time|interactive/, 'first token ≤ 1,000 ms')) { conds.push({ f: 'ttft', max: 1000, from: true }); w.speed = 0.3; w.cap = 0.5; w.cost = 0.2; }
  if (hit(/\beu\b|gdpr|europe\w*/, 'EU data residency')) conds.push({ f: 'resid', v: 'EU', from: true });
  if (hit(/private|on.prem\w*|local|self.host\w*/, 'open weights, 0-day retention')) { conds.push({ f: 'open', v: true, from: true }); }
  if (hit(/commercial/, 'commercial licence')) conds.push({ f: 'commercial', from: true });
  return { conds, w, bench, trace };
}

export const TEMPLATES = [
  { id: 'budget-agent', name: 'Coding agent on a budget', task: 'Coding agent that fixes failing tests in a TypeScript monorepo', spec: { tokIn: 60000, tokOut: 6000, bench: 'CodeBench Pro', w: { cap: 0.5, cost: 0.4, speed: 0.1 }, conds: [{ f: 'type', v: 'llm' }, { f: 'active' }, { f: 'ctx', min: 128000 }, { f: 'task$', max: 0.1 }, { f: 'bench', b: 'CodeBench Pro', min: 45, indep: true }] } },
  { id: 'private', name: 'Private and on-prem', task: 'Internal assistant we run on our own servers', spec: { tokIn: 20000, tokOut: 2000, bench: 'CodeBench Pro', w: { cap: 0.6, cost: 0.2, speed: 0.2 }, conds: [{ f: 'type', v: 'llm' }, { f: 'active' }, { f: 'open', v: true }, { f: 'commercial' }, { f: 'ctx', min: 128000 }] } },
  { id: 'embed', name: 'Cheapest good embedding', task: 'Embed 10,000 documents of about 800 tokens for retrieval', spec: { tokIn: 8000000, tokOut: 0, bench: 'RetrievalEval v2', w: { cap: 0.3, cost: 0.7, speed: 0 }, conds: [{ f: 'type', v: 'embed' }, { f: 'active' }, { f: 'bench', b: 'RetrievalEval v2', min: 0.6, indep: true }] } },
];

export const FACETS = [
  { k: 'context length window tokens', label: 'Context length', hint: 'minimum, tokens', c: { f: 'ctx', min: 200000 } },
  { k: 'open weights licence self host', label: 'Open weights', hint: 'require or exclude', c: { f: 'open', v: true } },
  { k: 'licence license commercial use', label: 'Licence allows commercial use', hint: 'yes / no / unknown', c: { f: 'commercial' } },
  { k: 'price per task budget cost dollars', label: 'Price per task', hint: '$ per task, from your token counts', c: { f: 'task$', max: 0.1 } },
  { k: 'input price per million tokens cost', label: 'Input price', hint: '$ per 1M input tokens', c: { f: 'in$', max: 1 } },
  { k: 'data residency region eu gdpr location', label: 'Data residency: EU', hint: 'offering serves an EU region', c: { f: 'resid', v: 'EU' } },
  { k: 'data residency region us location', label: 'Data residency: US', hint: 'offering serves a US region', c: { f: 'resid', v: 'US' } },
  { k: 'data retention zero privacy logging', label: 'Data retention: 0 days', hint: 'provider terms', c: { f: 'ret0' } },
  { k: 'benchmark floor codebench pro score coding', label: 'CodeBench Pro floor', hint: '% resolved, independent', c: { f: 'bench', b: 'CodeBench Pro', min: 50, indep: true } },
  { k: 'benchmark termtasks terminal', label: 'TermTasks 4 floor', hint: '% tasks passed', c: { f: 'bench', b: 'TermTasks 4', min: 40, indep: true } },
  { k: 'benchmark reasonhard reasoning math', label: 'ReasonHard floor', hint: '% accuracy', c: { f: 'bench', b: 'ReasonHard', min: 60, indep: true } },
  { k: 'latency time to first token ttft speed', label: 'Time to first token', hint: 'maximum, ms', c: { f: 'ttft', max: 1000 } },
  { k: 'throughput speed tokens per second', label: 'Output throughput', hint: 'minimum, tokens/s', c: { f: 'tps', min: 100 } },
  { k: 'origin jurisdiction country lab', label: 'Origin jurisdiction', hint: 'exclude SG', c: { f: 'origin', ex: ['SG'] } },
  { k: 'relative compare better cheaper than talon', label: 'At least as good as Talon 2, and cheaper', hint: 'relative, on CodeBench Pro', c: { f: 'rel', ref: 'kestrel-talon-2', b: 'CodeBench Pro' } },
];
