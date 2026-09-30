interface Env {
  EXPORT_ORIGIN: string;
  RANK_API_ORIGIN: string;
  /** Service binding to the rank Worker (modelspec-rank). Absent in unit tests. */
  RANK?: Fetcher;
  /** Only explicit "false" permits anonymous decision tools. Unset requires a key. */
  MCP_REQUIRE_API_KEY?: string;
  BUILD_COMMIT: string;
}
