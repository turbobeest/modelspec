# Hardware-fit 2.0 response bytes

These four response bodies were captured from the unchanged implementation at
`b4a7074f` before MODEL-407 changed snapshot storage. Each uses the public,
synthetic fixtures in `tests/test_hardware_fit.py`.

The files preserve the Worker's `json.dumps(body, indent=2, default=str)` wire
format, including field order and the absence of a trailing newline. Only the
content-addressed `snapshot` field is replaced by
`snap_golden_hardware_fit_2_0`. Compact storage changes the signed content hash,
so that identity changes even when the response contract is identical.

`test_hardware_fit_2_0_response_bytes_match_before_memory_change` compares actual
keyed Worker responses to these bytes for measured, full estimate, lower-bound
estimate, and undetermined assessments. Do not regenerate these files when
changing snapshot storage.
