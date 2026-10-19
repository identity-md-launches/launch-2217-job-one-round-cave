# Uncertainty Lens

Uncertainty Lens turns a small JSON array of timestamp intervals into a reproducible summary of definite pairwise order and unresolved overlaps. It is a local, read-only incident-evidence helper using only Python's standard library. It never runs the services described by the events.

From the repository root, run this one command:

```sh
printf '%s\n' '[{"id":"ingest","start":1,"end":3},{"id":"alert","start":3,"end":4},{"id":"retry","start":2,"end":5}]' | python3 -B line-3/tools/uncertainty-lens/uncertainty_lens.py
```

Tried locally: it reported `ingest` before `alert`, and the two pairs involving `retry` as uncertain. Six focused tests passed, including CLI rejection of nonfinite JSON numbers and oversized input. No real incident or measured clock error is claimed.

Input is a JSON array of objects with a unique, nonempty string `id` and finite, nonboolean numeric `start` and `end`, with `start <= end`. Intervals are half-open: an end exactly equal to another start gives definite order. Overlap does not establish simultaneity or causality. Extra object fields are ignored. The CLI accepts stdin by default or a JSON file path. It reads at most 256 KiB and accepts at most 128 events, bounding the report to 8,128 pairs. Malformed input, duplicate IDs, booleans, NaN and infinities fail with an error instead of producing an order claim.
