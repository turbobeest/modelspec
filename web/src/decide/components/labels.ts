// Where each direct label on the canvas goes (MODEL-153).
//
// The design: labels sit beside their point, flip to the left past 72% of the
// width, and step vertically in 15px when they would collide. On 2026-09-25 a
// label stepped two rows down beside a different point, and the point it named
// read as unlabelled. So a label first tries the other side, then steps up or
// down, never over another label or marker, and an offset label is drawn with
// a leader to its point.

/** A label to place; `x` and `y` are fractions of the plot, from its top left. */
export interface LabelInput {
  id: string;
  text: string;
  x: number;
  y: number;
}

export interface LabelPlacement {
  id: string;
  side: "left" | "right";
  /** Vertical offset from the point, in px. */
  dy: number;
}

/** 12px, weight 600: an upper bound on one character's width. */
const CHAR_PX = 7;
const GAP_PX = 12;
const STEP_PX = 15;
const HALF_HEIGHT_PX = 7; // within one 15px step
const MARKER_PX = 8;
const FLIP_AT = 0.72;
const STEPS = [0, -1, 1, -2, 2, -3, 3, -4, 4];

interface Box {
  left: number;
  right: number;
  top: number;
  bottom: number;
}

const overlaps = (a: Box, b: Box) =>
  a.left < b.right && b.left < a.right && a.top < b.bottom && b.top < a.bottom;

export function labelWidth(text: string): number {
  return text.length * CHAR_PX;
}

/**
 * Place labels in the order given (most important first). Every label gets a
 * place; when no free one exists it keeps its default side, unshifted.
 */
export function placeLabels(
  labels: readonly LabelInput[],
  markers: readonly { x: number; y: number }[],
  width: number,
  height: number,
): LabelPlacement[] {
  const taken: Box[] = [];
  const dots: Box[] = markers.map(({ x, y }) => ({
    left: x * width - MARKER_PX,
    right: x * width + MARKER_PX,
    top: y * height - MARKER_PX,
    bottom: y * height + MARKER_PX,
  }));
  return labels.map((label) => {
    const px = label.x * width,
      py = label.y * height,
      w = labelWidth(label.text);
    const preferred: LabelPlacement["side"] = label.x > FLIP_AT ? "left" : "right";
    const sides = [preferred, preferred === "left" ? "right" : "left"] as const;
    const box = (side: LabelPlacement["side"], dy: number): Box => ({
      left: side === "right" ? px + GAP_PX : px - GAP_PX - w,
      right: side === "right" ? px + GAP_PX + w : px - GAP_PX,
      top: py + dy - HALF_HEIGHT_PX,
      bottom: py + dy + HALF_HEIGHT_PX,
    });
    const own = (dot: Box) =>
      Math.abs((dot.left + dot.right) / 2 - px) < 0.5 &&
      Math.abs((dot.top + dot.bottom) / 2 - py) < 0.5;
    for (const step of STEPS)
      for (const side of sides) {
        const dy = step * STEP_PX,
          b = box(side, dy);
        const inside = b.left >= 0 && b.right <= width && b.top >= 0 && b.bottom <= height;
        if (
          inside &&
          !taken.some((t) => overlaps(t, b)) &&
          !dots.some((dot) => !own(dot) && overlaps(dot, b))
        ) {
          taken.push(b);
          return { id: label.id, side, dy };
        }
      }
    taken.push(box(preferred, 0));
    return { id: label.id, side: preferred, dy: 0 };
  });
}
