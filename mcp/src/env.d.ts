interface Env {
  DATA_SPLIT_ENABLED?: string;
  EXPORT_ORIGIN: string;
  RANK_API_ORIGIN: string;
  /** Service binding to the rank Worker (modelspec-rank). Absent in unit tests. */
  RANK?: Fetcher;
  /** Legacy setting, ignored. Data tools always require a key. */
  MCP_REQUIRE_API_KEY?: string;
  BUILD_COMMIT: string;
}
