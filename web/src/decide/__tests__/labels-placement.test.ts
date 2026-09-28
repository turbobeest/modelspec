import { describe, expect, it } from "vitest";
import { labelWidth, placeLabels } from "../components/labels";
import type { LabelInput, LabelPlacement } from "../components/labels";

const W = 892,
  H = 460;

function box(label: LabelInput, at: LabelPlacement) {
  const px = label.x * W,
    py = label.y * H + at.dy,
    w = labelWidth(label.text);
  return at.side === "right"
    ? { left: px + 12, right: px + 12 + w, top: py - 7, bottom: py + 7 }
    : { left: px - 12 - w, right: px - 12, top: py - 7, bottom: py + 7 };
}

function collisions(labels: LabelInput[], placed: LabelPlacement[]): string[] {
  const boxes = labels.map((label, i) => box(label, placed[i]));
  const out: string[] = [];
  boxes.forEach((a, i) =>
    boxes.slice(i + 1).forEach((b, j) => {
      if (a.left < b.right && b.left < a.right && a.top < b.bottom && b.top < a.bottom)
        out.push(`${labels[i].text} × ${labels[i + 1 + j].text}`);
    }),
  );
  return out;
}

describe("placing direct labels on the canvas", () => {
  it("resolves the live collision without moving a label beside another point", () => {
    // snap_898e29e1f0c39d6e, the default coding task, 2026-09-25: the
    // "Claude Fable 5" label stepped 30px down, beside Claude Fable 5.1.
    const labels: LabelInput[] = [
      { id: "opus-5", text: "Claude Opus 5", x: 0.7, y: 0.08 },
      { id: "fable-5", text: "Claude Fable 5", x: 0.935, y: 0.08 },
      { id: "sol", text: "GPT-5.6 Sol", x: 0.63, y: 0.27 },
    ];
    const markers = [...labels, { x: 0.935, y: 0.16 }, { x: 0.7, y: 0.6 }];
    const placed = placeLabels(labels, markers, W, H);
    expect(collisions(labels, placed)).toEqual([]);
    const fable = placed.find((p) => p.id === "fable-5")!;
    // Half the gap to the next point down: still nearer its own point.
    expect(Math.abs(fable.dy)).toBeLessThan((0.16 - 0.08) * H / 2);
  });

  it("flips to the left past 72% of the width", () => {
    const [p] = placeLabels([{ id: "a", text: "Model", x: 0.8, y: 0.5 }], [], W, H);
    expect(p).toEqual({ id: "a", side: "left", dy: 0 });
  });

  it("tries the other side before stepping away from the point", () => {
    const labels: LabelInput[] = [
      { id: "a", text: "First model", x: 0.4, y: 0.5 },
      { id: "b", text: "Second model", x: 0.45, y: 0.5 },
    ];
    const [, b] = placeLabels(labels, labels, W, H);
    expect(b.dy).toBe(0);
    expect(b.side).toBe("right");
    const [, a2] = placeLabels([...labels].reverse(), labels, W, H);
    expect(a2).toMatchObject({ side: "left", dy: 0 });
  });

  it("keeps labels off other markers when there is room", () => {
    const labels: LabelInput[] = [{ id: "a", text: "Model A", x: 0.3, y: 0.5 }];
    const markers = [labels[0], { x: 0.3 + 40 / W, y: 0.5 }];
    const [p] = placeLabels(labels, markers, W, H);
    expect(p).toMatchObject({ side: "left", dy: 0 });
  });

  it("places every label, and none leaves the plot", () => {
    const labels: LabelInput[] = Array.from({ length: 14 }, (_, i) => ({
      id: `m${i}`,
      text: `Model number ${i}`,
      x: 0.05 + (i % 7) * 0.14,
      y: 0.1 + Math.floor(i / 7) * 0.05,
    }));
    const placed = placeLabels(labels, labels, W, H);
    expect(placed.map((p) => p.id)).toEqual(labels.map((l) => l.id));
    expect(collisions(labels, placed)).toEqual([]);
    for (const [i, p] of placed.entries()) {
      const b = box(labels[i], p);
      expect(b.left).toBeGreaterThanOrEqual(0);
      expect(b.right).toBeLessThanOrEqual(W);
      expect(b.top).toBeGreaterThanOrEqual(0);
    }
  });
});
