# Superseded pilot runs

Runs here were made with an earlier harness request shape (MODEL-230, before
MODEL-243 fixed it) and are kept as raw data only. `window_runs` reads
`../runs/*.json.gz` and never this directory, so they are excluded from
aggregation: the aggregate guard refuses to mix runs whose settings differ.

A harness settings change starts a new window: move the old runs here first.
