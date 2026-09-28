// The site serves vocabulary.json with max-age=14400. After a deploy (or a
// 409 snapshot_changed) the page must revalidate, never read a cached copy.
import { afterEach, describe, expect, it, vi } from "vitest";
import { loadVocabulary } from "../vocabulary";

describe("loadVocabulary", () => {
  afterEach(() => vi.unstubAllGlobals());

  it("revalidates instead of trusting the browser cache", async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response("{}", { status: 500 }));
    vi.stubGlobal("fetch", fetchMock);
    await loadVocabulary().catch(() => undefined);
    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(fetchMock.mock.calls[0][1]).toMatchObject({ cache: "no-cache" });
  });
});
