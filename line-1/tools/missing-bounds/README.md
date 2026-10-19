# Missing Bounds

Keep unfinished benchmark cases in the evidence. This standard-library Python
3.10+ tool gives conservative simultaneous confidence bounds for paired binary
candidate-minus-baseline pass-rate differences when some outcomes are unknown.
It never silently discards a case or treats a missing result as a failure.
Copy this whole folder for standalone offline use; no installation is needed.

One command from the repository root:

```sh
python3 -B line-1/tools/missing-bounds/missing_bounds.py --demo
```

When tried, the **synthetic** 120-case, two-candidate example retained all cases
and 30 missing cells. The improved candidate had 90 complete pairs and a sample
mean identification interval [0.25, 0.50]; its population confidence interval
was approximately [0.0627, 0.6163]. The unchanged candidate had 110 complete
pairs and a confidence interval approximately [-0.1671, 0.0414]. Neither
established improvement beyond +0.10 or equivalence within ±0.10. In the
predecessor's unmasked synthetic example those respective criteria were met.
This illustrates information loss, not measurements of real systems.
`example-result.json` retains actual CLI output with exact rational endpoints.

## Your incomplete results

Use UTF-8 CSV with header `case,baseline` followed by 1–16 distinct candidate
names. Outcomes must be literal `0`, `1` or `?`; blank, NA and null are errors.
Include every **planned** case even if all its outcomes are `?`, and keep every
planned candidate column even if entirely unknown. The program cannot detect
unlisted cases or missing candidate columns. Sample size is the row count,
not the complete-pair count. A missing baseline affects every paired comparison.

```csv
case,baseline,system-a,system-b
request-a,0,1,?
request-b,?,1,0
request-c,?,?,?
```

Retain the original bytes' SHA-256 independently at handoff, then replace these
uppercase tokens with your actual workspace-relative path and retained digest:

```sh
python3 -B line-1/tools/missing-bounds/missing_bounds.py --input RESULTS.csv --expected-input-sha256 RETAINED_SHA256 --alpha 0.05 --margin 0.10
```

Alpha accepts plain decimals 0.000001–0.2; margin accepts 0–1 (an absolute
pass-rate difference, so 0.10 is ten percentage points), at most nine fractional
places. Choose both prospectively. Limits: 1–512 cases, 1–16 candidates, 2 MiB
CSV. IDs are unique, 1–200 characters, without edge whitespace or Unicode
category-C characters. BOM, CRLF, quoted Unicode IDs and commas are supported;
labels are preserved. Blank rows, duplicate/reserved headers, bad outcomes and
incomplete field counts fail. The file must resolve to a regular file inside
the current working directory; escaping symlinks fail. Reads are bounded.

The CLI only reads that supplied input and prints ASCII-escaped JSON to stdout;
it changes no file. Exit 0 means analysis completed, including inconclusive
results. Exit 2 means invalid input/options/pin, with no partial JSON. Safe
rendering of JSON labels in another format remains the consumer's job. A pin
establishes byte identity, not honest measurement or prospective planning.

## Method and interpretation

For each visible pair enumerate its possible latent differences `candidate -
baseline`. For example `(?,1)` permits {0,+1}, `(1,?)` permits {-1,0}, and
`(?,?)` permits {-1,0,+1}. Sum the smallest/largest possible differences and
divide by **all n planned rows** for sample identification bounds. These are
possible completed sample means, not confidence intervals or estimated effects.
No single observed effect is imputed.

Separately count minimum/maximum possible candidate-only passes (`w_min`,
`w_max`) and baseline-only passes (`l_min`, `l_max`). Using Paired Bounds'
unchanged exact binomial engine and tail budget `alpha/(4m)`, return:

```
[L(n,w_min) - U(n,l_max), U(n,w_max) - L(n,l_min)]
```

Binomial endpoints are monotone in count. Therefore this interval encloses the
complete-data interval for **every binary completion**. Indeed the lower and
upper extremes are each attainable for one candidate: choose each unknown pair
to minimize or maximize its difference. Extremes for different candidates need
not be jointly attainable; the conservative simultaneous enclosure remains
valid. The full candidate family shares Bonferroni's 4m tail budget. Outward
2^-32 grid arithmetic uses integers/Fractions; there is no floating point or
simulation. Distinct count calculations are cached, keeping work bounded.

For latent independent identically distributed complete case vectors, the
predecessor's simultaneous coverage event implies this report's coverage event.
Consequently coverage is at least 1-alpha even when masking depends on observed
outcomes. **No missing-at-random assumption is required.** This does not permit
optional stopping, outcome-selected sample sizes/families, omitted rows,
correlated cases, inaccurate observed outcomes or selective publication. Fix
the final sample size, sampling protocol, pass rule, family, alpha and margin
before seeing outcomes. Curated examples alone are not population samples.
The program does not implement sequential or cluster inference.

The confidence interval describes the latent complete-outcome target. If a
system's timeout is defined prospectively as an actual failure, record `0`;
if an outcome is truly unknown, record `?`. Changing the pass rule after seeing
results changes the question and is unsupported. This tool does not determine
which interpretation fits your workload.

A candidate clears +margin only if the lower endpoint is strictly above it;
baseline clears +margin if the upper endpoint is strictly below -margin.
Equivalence requires the whole interval strictly inside (-margin,+margin).
Equality fails each strict comparison. A false field is inconclusive, never
proof of the opposite. Complete inputs reproduce Paired Bounds exactly;
masking additional cells can only widen intervals and cannot gain a criterion.
Entirely missing inputs produce [-1,+1] and keep the complete family and rows.
Coverage is repeated-sampling coverage under assumptions, not a posterior
probability. Statistical intervals do not certify measurement truth or utility.

## Checks and reuse

```sh
python3 -B -m unittest discover -s line-1/tools/missing-bounds -v
```

All 12 local tests passed: all nine visible pair states; every two-row missing
pattern against enumeration of all completions; exact predecessor agreement;
50 seeded masking checks; retained all-missing cases/families; baseline swap;
family/alpha monotonicity; input validation; Unicode/BOM/CRLF; synthetic claim
loss; the 512-case/16-candidate cap; and copied-folder CLI/pins/escaping symlink
rejection/input immutability. The unchanged predecessor's 11 tests also passed,
including independent binomial formulas and small-model exact coverage checks.
These are local checks, not independent certification.

`bounds_engine.py` is an unchanged ordinary-file snapshot of Paired Bounds,
pinned in `provenance.json`; only its validation helpers, file reader, exact
binomial bounds and fraction serializer are used. The new parser accepts `?`.
There is no runtime dependency on a sibling folder. No network, environment,
wallet, key, signing, sending, payment, chain or deployment is needed; this
statistical tool has no currency requirement.
