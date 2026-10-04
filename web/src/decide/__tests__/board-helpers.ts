import { fireEvent, screen } from "@testing-library/react";

// MODEL-277: the template card and every facet group start collapsed. These
// open them the way a visitor does, by clicking their buttons.

const templateBar = () => screen.getByRole("button", { name: /^(All \d+ templates|Hide templates)$/ });

/** Opens the template card if it is collapsed, and returns the named template cell. */
export function templateCell(name: RegExp): HTMLElement {
  if (templateBar().getAttribute("aria-expanded") !== "true") fireEvent.click(templateBar());
  return screen.getByRole("button", { name });
}

/** Waits for the board to load, then returns the named template cell. */
export async function findTemplateCell(name: RegExp): Promise<HTMLElement> {
  await screen.findByRole("button", { name: /^(All \d+ templates|Hide templates)$/ });
  return templateCell(name);
}

/** Expands the named facet group if it is collapsed. */
export function openGroup(name: string): void {
  const summary = screen.getByRole("button", { name: new RegExp(`^${name}`) });
  if (summary.getAttribute("aria-expanded") !== "true") fireEvent.click(summary);
}

/** Expands "What it's good at" and returns the named capability's facet row. */
export function capabilityRow(label: string): HTMLElement {
  openGroup("What it's good at");
  return screen.getByText(label).closest<HTMLElement>(".facet-row")!;
}
