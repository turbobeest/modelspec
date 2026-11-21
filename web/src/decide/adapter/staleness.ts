/** Stale label for a verified price (MODEL-521). Display only: never a ranking input.
 * Mirrors decision/staleness.py: a price or subscription fact is stale after 45 days.
 * `today` is passed in by the caller; nothing here reads a clock. */
export const PRICE_STALE_DAYS = 45;

const DAY_MS = 86_400_000;

function utcDay(value: string): number | null {
  const stamp = Date.parse(`${value.slice(0, 10)}T00:00:00Z`);
  return Number.isNaN(stamp) ? null : stamp;
}

/** "Last checked <date>, may be out of date", or null when fresh, undated or unparsable. */
export function priceStaleLabel(verifiedAt: string | null | undefined, today: Date): string | null {
  if (!verifiedAt) return null;
  const day = utcDay(verifiedAt);
  if (day === null) return null;
  const now = Date.UTC(today.getUTCFullYear(), today.getUTCMonth(), today.getUTCDate());
  return (now - day) / DAY_MS > PRICE_STALE_DAYS
    ? `Last checked ${verifiedAt.slice(0, 10)}, may be out of date`
    : null;
}
