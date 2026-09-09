import json, math, os, pathlib, random, re, collections
import yaml
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = pathlib.Path(os.environ["OUT"])
BUILD = ROOT / "build"
# Resolve the cards from this file's location so the generator works in CI and
# in any checkout, not only from one developer's home directory. MODELSPEC_CARDS
# overrides it when the cards live elsewhere.
CARDS = pathlib.Path(
    os.environ.get("MODELSPEC_CARDS") or pathlib.Path(__file__).resolve().parents[3] / "models"
)

HUES = {
 "coding": "#22d3ee", "math": "#fbbf24", "reasoning": "#a78bfa", "knowledge": "#60a5fa",
 "multimodal": "#f472b6", "safety": "#34d399", "embeddings": "#2dd4bf", "agentic": "#fb923c",
 "domain": "#a3e635", "preference": "#fb7185", "translation": "#38bdf8", "long context": "#818cf8",
}
GENRE_RULES = [
 ("coding", r"^(humaneval|live_code_bench|aider_polyglot|terminal_bench|swe_bench|multipl_e)"),
 ("math", r"^(math_500|aime_|usamo_|gsm8k|mgsm)"),
 ("embeddings", r"^(mteb|beir|miracl)"),
 ("preference", r"^(arena_elo|alpaca_eval|mt_bench|wildbench)"),
 ("translation", r"^flores"),
 ("long context", r"^graphwalks"),
 ("agentic", r"^(tau_bench|osworld|browsecomp|screenspot|deepsearchqa)"),
 ("multimodal", r"^(mmmu|mathvista|chartqa|docvqa|ai2d|ocrbench|realworldqa|zerobench|charxiv|medxpertqa_multimodal|lab_bench_figqa)"),
 ("safety", r"^(toxigen|bbq|helm_safety|truthfulqa)"),
 ("domain", r"^(medqa|medmcqa|pubmedqa|healthbench|legalbench|finbench|frontierscience|ipho)"),
 ("knowledge", r"^(mmlu|mmmlu|hellaswag|winogrande|arc_challenge)"),
 ("reasoning", r"^(gpqa|hle|arc_agi|bbh|musr|ifeval|artificial_analysis)"),
]
def genre(k):
    for g, rx in GENRE_RULES:
        if re.match(rx, k): return g
    return "reasoning"

# ---------- data from the cards ----------
keys = collections.Counter(); models_scored = 0; entries = 0
swe = []
for c in CARDS.rglob("*.md"):
    txt = c.read_text(errors="ignore")
    m = re.match(r"---\n(.*?)\n---", txt, re.S)
    if not m: continue
    try: fm = yaml.safe_load(m.group(1)) or {}
    except Exception: continue
    b = fm.get("benchmarks") or {}
    sc = b.get("scores") or {}
    if isinstance(sc, dict):
        vals = {k: v for k, v in sc.items() if v is not None}
        if vals:
            models_scored += 1; entries += len(vals); keys.update(vals.keys())
            v = vals.get("swe_bench_verified")
            if isinstance(v, (int, float)):
                name = (fm.get("identity") or {}).get("display_name") or fm.get("display_name") or fm.get("name") or c.stem
                prov = (fm.get("identity") or {}).get("provider") or fm.get("provider") or c.parent.name
                swe.append((float(v), str(name), str(prov), str(b.get("benchmark_as_of") or "")))
swe.sort(reverse=True)
_seen = set(); _dedup = []
for row in swe:
    base = re.sub(r"\s*\((latest|preview)\)$", "", row[1], flags=re.I).strip().lower()
    if base in _seen: continue
    _seen.add(base); _dedup.append(row)
swe = _dedup
by_genre = collections.Counter(genre(k) for k in keys)
STATS = {"benchmarks": len(keys), "models": models_scored, "scores": entries}
print("stats", STATS, "| swe_bench_verified models:", len(swe), "| genres:", dict(by_genre))

# ---------- logo geometry ----------
rng = random.Random(7)
def tabletop(x0, x1, y0, y1, cols, rows, jitter=6):
    nodes = []
    for i in range(cols):
        for j in range(rows):
            x = x0 + (x1 - x0) * i / (cols - 1) + rng.uniform(-jitter, jitter)
            y = y0 + (y1 - y0) * j / (rows - 1) + rng.uniform(-jitter, jitter)
            nodes.append((x, y, i, j))
    edges = []
    for (x, y, i, j) in nodes:
        nxt = [n for n in nodes if n[2] == i + 1]
        for n in rng.sample(nxt, min(2, len(nxt))): edges.append(((x, y), (n[0], n[1])))
        if rng.random() < 0.35:
            far = [n for n in nodes if n[2] == i + 2]
            if far: n = rng.choice(far); edges.append(((x, y), (n[0], n[1])))
    return nodes, edges
def leg(x, y0, y1, n, jitter=4):
    nodes = [(x + rng.uniform(-jitter, jitter), y0 + (y1 - y0) * k / (n - 1), -1, k) for k in range(n)]
    edges = [((nodes[k][0], nodes[k][1]), (nodes[k + 1][0], nodes[k + 1][1])) for k in range(n - 1)]
    foot = [((nodes[-1][0], nodes[-1][1]), (nodes[-1][0] - 26, y1 + 18)), ((nodes[-1][0], nodes[-1][1]), (nodes[-1][0] + 26, y1 + 18))]
    return nodes, edges, foot
HUE_LIST = list(HUES.values())
def node_color(i, j): return HUE_LIST[(i * 3 + j * 5) % len(HUE_LIST)]

def logo_svg(with_text=True):
    W, H = 1200, 520
    top_nodes, top_edges = tabletop(150, 1050, 132, 214, 11, 3)
    L1, E1, F1 = leg(238, 250, 452, 4); L2, E2, F2 = leg(962, 250, 452, 4)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-labelledby="bg-title"><title id="bg-title">benchgraph</title>']
    out.append('<rect class="slab" x="128" y="112" width="944" height="124" rx="18" fill="#e5e7eb" fill-opacity="0.045"/>')
    out.append('<g class="edges" fill="none" stroke="#e5e7eb" stroke-opacity="0.28" stroke-width="2" stroke-linecap="round">')
    for (a, b) in top_edges:
        out.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}"/>')
    out.append('</g><g class="edges" fill="none" stroke="#e5e7eb" stroke-opacity="0.55" stroke-width="5" stroke-linecap="round">')
    for (a, b) in E1 + E2 + F1 + F2:
        out.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}"/>')
    out.append('</g><g class="nodes">')
    for (x, y, i, j) in top_nodes:
        r = 9 if (i + j) % 4 else 12
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{node_color(i, j)}"/>')
    for (x, y, i, j) in L1 + L2:
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="11" fill="#e5e7eb" fill-opacity="0.95"/>')
    out.append('</g>')
    if with_text:
        out.append('<text x="600" y="382" text-anchor="middle" font-family="Space Grotesk, ui-sans-serif, system-ui, sans-serif" font-weight="700" font-size="96" letter-spacing="-3.5" fill="#f3f4f6">benchgraph</text>')
    out.append('</svg>')
    return "\n".join(out), (top_nodes, top_edges, L1, E1, F1, L2, E2, F2)

def icon_svg():
    W = 512
    rng.seed(11)
    top_nodes, top_edges = tabletop(96, 416, 178, 232, 5, 2, jitter=3)
    L1, E1, F1 = leg(136, 262, 392, 3, jitter=2); L2, E2, F2 = leg(376, 262, 392, 3, jitter=2)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {W}" width="{W}" height="{W}"><rect width="{W}" height="{W}" rx="96" fill="#000"/>']
    out.append('<g fill="none" stroke="#e5e7eb" stroke-opacity="0.35" stroke-width="6" stroke-linecap="round">')
    for (a, b) in top_edges + E1 + E2 + F1 + F2:
        out.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}"/>')
    out.append('</g>')
    for (x, y, i, j) in top_nodes:
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{22 if (i + j) % 3 else 28}" fill="{node_color(i, j)}"/>')
    for (x, y, i, j) in L1 + L2:
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="18" fill="#e5e7eb"/>')
    out.append('</svg>')
    return "\n".join(out), (top_nodes, top_edges, L1, E1, F1, L2, E2, F2)

LOGO_SVG, LOGO_GEOM = logo_svg(True)
ICON_SVG, ICON_GEOM = icon_svg()

# ---------- PNG rendering with Pillow ----------
def render(geom, size, scale, offset=(0, 0), bg=None, text=None, node_r=(9, 12), leg_r=11, edge_w=2, foot_w=5, supersample=3, slab=(128, 112, 944, 124)):
    S = supersample
    W, H = size
    img = Image.new("RGBA", (W * S, H * S), bg or (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    top_nodes, top_edges, L1, E1, F1, L2, E2, F2 = geom
    def P(p): return ((p[0] * scale + offset[0]) * S, (p[1] * scale + offset[1]) * S)
    if slab:
        (sx, sy, sw, sh) = slab
        d.rounded_rectangle([P((sx, sy)), P((sx + sw, sy + sh))], radius=int(18 * scale * S), fill=(229, 231, 235, 12))
    for (a, b) in top_edges:
        d.line([P(a), P(b)], fill=(229, 231, 235, 72), width=int(edge_w * scale * S))
    for (a, b) in E1 + E2 + F1 + F2:
        d.line([P(a), P(b)], fill=(229, 231, 235, 140), width=int(foot_w * scale * S))
    def hexrgb(h): return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))
    for (x, y, i, j) in top_nodes:
        r = (node_r[0] if (i + j) % 4 else node_r[1]) * scale * S
        cx, cy = P((x, y)); d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=hexrgb(node_color(i, j)) + (255,))
    for (x, y, i, j) in L1 + L2:
        r = leg_r * scale * S; cx, cy = P((x, y)); d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(229, 231, 235, 235))
    if text:
        s, (tx, ty), size_px, fill = text
        font = ImageFont.truetype(str(BUILD / "SpaceGrotesk-VF.ttf"), int(size_px * scale * S))
        try: font.set_variation_by_name("Bold")
        except Exception: pass
        d.text(((tx * scale + offset[0]) * S, (ty * scale + offset[1]) * S), s, font=font, fill=fill, anchor="ms")
    return img.resize((W, H), Image.LANCZOS)

# logo.png (transparent, for social/README)
logo_png = render(LOGO_GEOM, (1200, 520), 1.0, text=("benchgraph", (600, 380), 96, (243, 244, 246, 255)))
logo_png.save(ROOT / "logo.png", optimize=True)
# icon 512 + favicon 64
icon = render(ICON_GEOM, (512, 512), 1.0, bg=(0, 0, 0, 255), node_r=(22, 28), leg_r=20, edge_w=6, foot_w=9, slab=(80, 160, 352, 92))
mask = Image.new("L", (512, 512), 0); ImageDraw.Draw(mask).rounded_rectangle([0, 0, 511, 511], radius=96, fill=255)
icon.putalpha(mask); icon.save(ROOT / "icon-512.png", optimize=True)
icon.resize((64, 64), Image.LANCZOS).save(ROOT / "favicon-64.png", optimize=True)
icon.resize((180, 180), Image.LANCZOS).save(ROOT / "apple-touch-icon.png", optimize=True)
# OG card 1200x630
og = Image.new("RGBA", (1200, 630), (0, 0, 0, 255))
lg = render(LOGO_GEOM, (1200, 520), 0.78, offset=(132, 40), text=("benchgraph", (600, 380), 96, (243, 244, 246, 255)))
og.alpha_composite(lg, (0, 0))
d = ImageDraw.Draw(og)
f2 = ImageFont.truetype(str(BUILD / "SpaceGrotesk-VF.ttf"), 34)
try: f2.set_variation_by_name("Medium")
except Exception: pass
d.text((600, 530), "Every AI benchmark, as a graph you can read.", font=f2, fill=(154, 163, 178, 255), anchor="ms")
d.text((600, 578), "benchgraph.dev", font=f2, fill=(245, 179, 66, 255), anchor="ms")
og.convert("RGB").save(ROOT / "og-card.png", optimize=True)
print("assets written")

# ---------- family map SVG ----------
def family_map():
    W, H = 1100, 430
    genres = [g for g, _ in GENRE_RULES]
    genres = sorted(genres, key=lambda g: -by_genre[g])
    cols = 6; cw = W / cols; rh = H / 2
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%" role="img" aria-label="Benchmark families in the graph, one node per benchmark, sized by count">']
    r2 = random.Random(3)
    for idx, g in enumerate(genres):
        n = by_genre[g]; cx = cw * (idx % cols) + cw / 2; cy = rh * (idx // cols) + rh / 2 - 22
        hue = HUES[g]
        pts = []
        for k in range(n):
            a = k * 2.399963; rad = (8 + 8.2 * math.sqrt(k)) if n > 20 else (10 + 11 * math.sqrt(k))
            pts.append((cx + rad * math.cos(a), cy + rad * math.sin(a)))
        out.append(f'<g stroke="{hue}" stroke-opacity="0.25" stroke-width="1">')
        for k in range(1, len(pts)):
            p, q = pts[k], pts[max(0, k - r2.randint(1, min(4, k)))]
            out.append(f'<line x1="{p[0]:.1f}" y1="{p[1]:.1f}" x2="{q[0]:.1f}" y2="{q[1]:.1f}"/>')
        out.append('</g>')
        for k, (x, y) in enumerate(pts):
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{(4.2 if n > 20 else 5) if k else 8}" fill="{hue}"/>')
        out.append(f'<text x="{cx:.1f}" y="{cy + 100:.1f}" text-anchor="middle" font-size="15" fill="#f3f4f6">{g}</text>')
        out.append(f'<text x="{cx:.1f}" y="{cy + 120:.1f}" text-anchor="middle" font-size="13" fill="#9aa3b2">{n} benchmark{"s" if n != 1 else ""}</text>')
    out.append('</svg>')
    return "\n".join(out)
FAMILY_SVG = family_map()

# ---------- HTML ----------
def nice(k): 
    return {"gpqa_diamond": "GPQA Diamond", "swe_bench_verified": "SWE-bench Verified"}.get(k, k)
swe_rows = "\n".join(f'<tr><td>{n}</td><td class="mute">{p}</td><td class="num">{v:.1f}</td><td class="mute">{d or "undated"}</td></tr>' for v, n, p, d in swe[:6])
tpl = (BUILD / "index.tpl.html").read_text()
html = (tpl.replace("{{LOGO_SVG}}", LOGO_SVG).replace("{{FAMILY_SVG}}", FAMILY_SVG)
        .replace("{{N_BENCH}}", f"{STATS['benchmarks']}").replace("{{N_MODELS}}", f"{STATS['models']}").replace("{{N_SCORES}}", f"{STATS['scores']:,}")
        .replace("{{SWE_ROWS}}", swe_rows).replace("{{SWE_COUNT}}", str(len(swe))))
(ROOT / "index.html").write_text(html)
(ROOT / "logo.svg").write_text(LOGO_SVG)
(ROOT / "icon.svg").write_text(ICON_SVG)
print("html written", len(html), "bytes")
