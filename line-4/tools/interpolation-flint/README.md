# Interpolation Flint

Check a piecewise-linear calibration or lookup calculation using exact rational
arithmetic and explicit dimensions. Python 3.10+ and the standard library only.
Copy this whole folder to run independently offline.

One command from the repository root shows it working:

```sh
python3 -B line-4/tools/interpolation-flint/interpolation_flint.py demo
```

Tried locally: the demo exits **0**, interpolating exactly **3.5 mm** at 750 g
between hypothetical observations of 2 mm at 500 g and 5 mm at 1 kg. Its exact
right weight is `1/2` and slope is `3/500 m*kg^-1`. These are illustrative
calibration inputs, not measured evidence. All **13 new tests** passed, including
400 seeded comparisons with an independent Fraction oracle, endpoint/segment
selection, mixed units, dimensions, strict input limits and CLI statuses.
All **117 inherited tests** passed. A standalone folder copy passed its demo
and all 13 tests. Local checks do not independently certify the model or inputs.

## Your table

Feed one JSON object on stdin:

```sh
printf '%s\n' '{"schema":"interpolation-flint/1","points":[{"x":"0 s","y":"1 m"},{"x":"3 s","y":"2 m"}],"at":"1 s","to":"m","expect":"(4/3) * m"}' | python3 -B line-4/tools/interpolation-flint/interpolation_flint.py run
```

This exits 0 and prints exact `4/3 m`. Required fields are `schema`, `points`,
`at`, `to`; optional fields are `expect` and boolean `extrapolate`. Each point
has exactly `x` and `y`, both expression strings. All x dimensions must agree,
all y dimensions must agree, and x values must be strictly increasing after
unit conversion. The table is never sorted or deduplicated silently. All points
are validated even when the query equals a knot. A zero retains its dimensions.

The query has x dimensions; the target and optional expected quantity have y
dimensions. For the enclosing adjacent points the result is exactly
`y0 + ((at - x0)/(x1 - x0)) * (y1 - y0)` with no rounding. Internal knots use
the segment to their right; the final knot uses the last segment. The output
identifies both zero-based point indices, their original expressions, exact
right weight, base-unit slope, result and optional claim difference.

Queries outside the table fail unless `"extrapolate":true` is explicitly
supplied. Permitted extrapolation uses the first/last segment and always sets
`extrapolated:true`; weights can then be outside `[0,1]`. Flat and descending y
values are supported. The target unit only changes display, not the calculation.

Exit **0** means a valid calculation and a passing claim (or no claim).
Exit **1** means the valid calculation disagrees with `expect`.
Exit **2** means invalid input or a resource limit. Invalid input produces no
partial stdout. The tool accepts no file paths, uses no network, reads no
environment/configuration or secrets, and writes only stdout/stderr.

## Grammar and bounds

Expressions use the unchanged Unit Flint engine: `+ - * / ^ **`, parentheses,
decimal/scientific numbers, and integer powers -12..12. Units: m, cm, mm, km,
in, ft, mi; kg, g, mg, t; s, ms, min, h, day; B, KiB, MiB, GiB; L, mL; N, J, W.
Dimensionless quantities use expressions such as `1`. Use explicit multiplication
around compound expressions: `(1/3) * s` is time, while `1/3 s` is inverse time.
`2 m^2` means `(2 m)^2`; use `2 * m^2` for two square metres. Target units use
the engine's unit-only grammar, with positive scale and no addition/subtraction.

CLI input is capped at 65,536 UTF-8 bytes and four JSON nesting levels, with
2..128 points. Duplicate keys, unknown fields, JSON numbers and nonfinite JSON
constants are rejected. Quantities must be strings; `extrapolate` must be a
boolean. Expressions allow at most 4096 characters, 256 tokens and 32 nesting
levels. Each parsed value and interpolation intermediate is capped at 2048
numerator/denominator bits; dimension exponents stay within -256..256. A valid
mathematical result can be refused if an intermediate exceeds these budgets.

## Limits and provenance

Linear interpolation is an explicit modeling assumption, not evidence that a
physical response is linear. This tool supplies no uncertainty model, error
bound, fitting, smoothing, interval propagation, currency/price conversion,
affine-temperature handling or measurements. It cannot establish sensor truth
or suitability of extrapolation. An exact result is exact for the supplied
piecewise-linear model only.

`engine.py` is a byte-identical ordinary-file copy of
`line-4/tools/unit-flint/unit_flint.py`. No packages or submodules are needed.

```sh
python3 -B -m unittest discover -s line-4/tools/interpolation-flint -v
```
