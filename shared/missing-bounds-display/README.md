# Missing Bounds Display

Read incomplete paired binary benchmark evidence as outward-rounded percentage
points without dropping cases or confusing sample possibilities with confidence
bounds. Joins Line 1's Missing Bounds to Line 4's Round Flint. Python 3.10+,
standard library only, no installation. Copy this entire folder to use offline.

One command from the repository root:

```sh
python3 -B shared/missing-bounds-display/missing_bounds_display.py demo
```

Tried: the synthetic example retains 120 planned cases, both candidates and 30
missing cells. The improved candidate has 90 complete pairs and 30 incomplete
pairs. Its sample identification interval displays [25.00, 50.00] percentage
points; its population confidence interval displays [6.27, 61.64] percentage
points. The unchanged candidate displays [-16.71, 4.15] confidence bounds. Neither
clears the predeclared +10-point improvement or ±10-point equivalence criterion.
These are synthetic outcomes, not measurements of real system performance.

The upper confidence endpoint rounds **up** to 61.64, rather than to the nearest
61.63. Decimal display cannot shrink the uncertainty. Sample identification and
population confidence intervals have separate named fields and both retain the
original exact rational endpoints inside `analysis`. The sample bounds describe
possible completed sample means; they are not population confidence intervals.

For your own data, pipe UTF-8 CSV on stdin with header `case,baseline` followed
by 1–16 candidate names, 1–512 unique planned case rows, and literal `0`, `1` or
`?` cells. `?` means unknown, never a failure or a pass. Blank cells and NA fail.
Include every planned row and candidate, even when entirely missing. Keep an
independently retained lowercase SHA-256 of the original input bytes. Replace
`RETAINED_SHA256` below with that digest:

```sh
python3 -B shared/missing-bounds-display/missing_bounds_display.py analyze --expected-input-sha256 RETAINED_SHA256 < results.csv
```

Options: `--places 0..6` (default 2), `--alpha 0.05`, `--margin 0.10`.
Choose sample size, protocol, pass rule, family, alpha, margin and precision
before observing results. Alpha is 0.000001–0.2; margin is 0–1, an absolute rate
difference. `0.10` means ten percentage points, not a relative ten percent gain.
Both allow at most nine decimal places. Input is capped at 2 MiB. Labels remain
unchanged, including Unicode; the CLI emits ASCII-escaped JSON. No data file is
opened by the wrapper; its only evidence input is stdin. Exit 0 means a complete
analysis, even when inconclusive. Exit 2 means invalid input or pin, with empty
stdout. No environment, configuration, network, wallet, key or transaction access.

`analysis` is exactly the original Missing Bounds result, including missing-cell
counts, all candidates, rational endpoints, strict criteria and assumptions.
The displayed endpoints use floor/ceiling after multiplication by 100, through
the unchanged Round Flint engine. Errors are display minus exact in percentage
points. Displayed comparisons use the exact unrounded margin. Rounding may lose
a criterion but cannot gain one; equality with a strict boundary fails. False
criteria are inconclusive, not proof of the opposite.

For latent iid complete case vectors under the stated fixed-sample protocol,
Missing Bounds encloses every completion, including outcome-dependent masking;
no missing-at-random assumption is required. It does not support omitted planned
rows, correlated cases, optional stopping, selected candidate families, inaccurate
observed outcomes or selective publication. A timeout defined prospectively as
failure is `0`; a genuinely unknown outcome is `?`. The tool cannot choose that
policy or detect absent rows. Coverage is repeated-sampling coverage, not a
posterior probability. Pins prove identity, not honesty or representative data.

Check with:

```sh
python3 -B -m unittest discover -s shared/missing-bounds-display -v
```

Ten integration tests cover original-analysis equality, retained wholly missing
rows/columns, every completion of a small incomplete family, complete-data
agreement, 200 seeded independent Fraction rounding oracles, strict boundaries,
precision, input/pin errors, Unicode byte identity, snapshot hashes and copied-
folder CLI operation with empty stdout on errors. Local tests do not certify the
sampling model or input truth. Four unchanged engine files are ordinary files
with source paths and SHA-256 hashes in `provenance.json`. Earlier shared crafts
are unchanged.
