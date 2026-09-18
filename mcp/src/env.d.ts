interface Env {
  EXPORT_ORIGIN: string;
  RANK_API_ORIGIN: string;
  /** Service binding to the rank Worker (modelspec-rank). Absent in unit tests. */
  RANK?: Fetcher;
  BUILD_COMMIT: string;
}
