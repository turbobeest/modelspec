/// <reference types="node" />
import { expect, it } from "vitest";
import { readFileSync } from "node:fs";
const css = readFileSync("src/decide/decide.css", "utf8");
const luminance = (hex: string) => {
  const rgb =
    hex.match(/[a-f0-9]{2}/gi)?.map((h) => parseInt(h, 16) / 255) || [];
  return rgb
    .map((v) => (v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4))
    .reduce((sum, v, i) => sum + v * [0.2126, 0.7152, 0.0722][i], 0);
};
it.each(["light", "dark"])(
  "meets AA for every foreground/background token pair used for text in %s",
  (theme) => {
    const first = css.slice(
      css.indexOf(".decide-app {"),
      css.indexOf('.decide-app[data-theme="dark"]'),
    );
    const dark = css.slice(
      css.indexOf('.decide-app[data-theme="dark"]'),
      css.indexOf(".decide-app *"),
    );
    const tokens = Object.fromEntries(
      [
        ...(first + (theme === "dark" ? dark : "")).matchAll(
          /--([\w]+):\s*(#[a-f0-9]{6})/gi,
        ),
      ].map((m) => [m[1], m[2]]),
    );
    // Text on any ordinary panel, selected row, control, chip, or soft surface.
    const pairs = [
      ...["ink", "ink2", "muted"].flatMap((f) =>
        ["bg", "surface", "surface2", "accentSoft", "warnSoft", "badSoft"].map(
          (b) => [f, b],
        ),
      ),
      ["accentInk", "accent"],
      ["surface", "ink"],
      ["warn", "warnSoft"],
      ["bad", "badSoft"],
      ...["accentText", "good", "bad", "warn"].flatMap((f) =>
        ["surface", "accentSoft", "bg"].map((b) => [f, b]),
      ),
    ];
    for (const [foreground, background] of pairs) {
      expect(tokens[foreground], foreground).toBeDefined();
      expect(tokens[background], background).toBeDefined();
      const a = luminance(tokens[foreground]),
        b = luminance(tokens[background]);
      expect(
        (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05),
        `${foreground} on ${background}`,
      ).toBeGreaterThanOrEqual(4.5);
    }
  },
);
