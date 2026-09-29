/**
 * The decide page is dark unless the link or the visitor chose light
 * (MODEL-213). `prefers-color-scheme` is deliberately not consulted: dark is
 * the product's look, and the toggle is how a visitor opts out. See
 * docs/design/lockup-and-theme.md.
 *
 * decide.html repeats this rule in an inline script so the first paint is
 * already themed; `__tests__/theme.test.tsx` holds the two to the same answers.
 */
export type Theme = "light" | "dark";

export const THEME_KEY = "modelspec-theme";

const isTheme = (value: string | null): value is Theme =>
  value === "light" || value === "dark";

/** `?theme=` wins for that link, then the visitor's stored choice, then dark. */
export function initialTheme(search: string, stored: string | null): Theme {
  const linked = new URLSearchParams(search).get("theme");
  if (isTheme(linked)) return linked;
  return isTheme(stored) ? stored : "dark";
}

export function storedTheme(): string | null {
  try {
    return localStorage.getItem(THEME_KEY);
  } catch {
    return null;
  }
}

export function storeTheme(theme: Theme): void {
  try {
    localStorage.setItem(THEME_KEY, theme);
  } catch {
    /* storage is optional; the choice then lasts for this visit */
  }
}
