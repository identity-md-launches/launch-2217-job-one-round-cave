# Unicode Normalization

Expose Unicode text whose canonical or compatibility-normalized form differs
from the original, with exact UTF-8 byte evidence. This helps a worker review
identifiers that change under a normalizing system. Python 3.10+ and the
standard library are sufficient; the tool has no network, dependency,
environment, sibling-import, or file-writing behavior.

Run this one command from the repository root:

```sh
python3 -B line-2/tools/unicode-normalization/unicode_normalization.py --demo
```

The demo reports six synthetic findings: a full-width ASCII letter, a Kelvin
sign, a circled digit, Bengali `U+09C7 U+09BE` → `U+09CB`, Tamil
`U+0BC6 U+0BBE` → `U+0BCA`, and the three-part Kannada sequence
`U+0CC6 U+0CC2 U+0CD5` → `U+0CCB`. The report labels the demo synthetic;
these are normalization differences, not evidence of attacks.

For a real, explicitly selected workspace file:

```sh
python3 -B line-2/tools/unicode-normalization/unicode_normalization.py --file path/to/text.txt
```

Each finding gives the original escaped text, NFC and NFKC forms, scalar names,
the original UTF-8 byte range, and a SHA-256 of that exact source span. Ranges
are zero-based and half-open: `[start, end)` refers to bytes in the unchanged
input. `character_index` counts Python Unicode scalars before that range.
The source hash binds the report to the entire original input. Counts cover
all input even when `--max-details 0` suppresses every detail; the default is
100 retained findings and the maximum is 1,000. This cap limits the number of
findings, not the length of an individual sequence: retained source and
normalized strings are complete, and one finding can span the entire input.

Version 3 fixes the class-zero composition gap reported after the earlier
Hangul repair. It derives possible composition continuations from the active
Python Unicode database, including algorithmic Hangul, rather than keeping a
script whitelist. Both canonical and compatibility-decomposed leading scalars
are checked. Conservative boundaries keep multi-part compositions together,
including Kannada and Unicode 16 Kirat Rai letters; testing only two adjacent
original scalars would miss some of these. A cited span may therefore include
unchanged neighboring scalars. Findings are normalization-sensitive sequences,
not grapheme clusters or minimum-sized replacements.

Inputs must be strict UTF-8 regular files inside the current workspace, at most
2 MiB. The CLI reads at most 2 MiB plus one rejection byte. Boundary decisions
use bounded caches and never repeatedly normalize growing prefixes. For spans
longer than 1,024 scalars, scalar-by-scalar decomposition and stable sorting of
nonstarter runs precede composition; this avoids quadratic canonical ordering
of an adversarial long run. The tool emits escaped ASCII JSON, reports the
active Unicode database version, and never rewrites the selected file.

Run the delivered regression checks:

```sh
python3 -B -m unittest discover -s line-2/tools/unicode-normalization -p 'test_*.py' -v
```

Observed locally with Unicode 16.0.0: the demo produced six findings and all
15 tests passed in 0.790 seconds. Tests include the Bengali/Tamil regressions,
three-part Kannada and Kirat Rai compositions, compatibility Jamo, intervening
marks that block composition, exact multibyte citations, detail caps, mixed
sequences, long disordered runs, and every composable canonical decomposition
ending in class zero in the runtime database. Replacing cited ranges with
their reported normalized forms reconstructs whole-input NFC and NFKC.

A separate review verified 39,704 reconstruction/evidence cases across the
runtime's decomposition mappings and seeded mixed strings, plus 200 long-form
normalization equivalence checks. A local 2 MiB out-of-order combining input
completed in 1.219 seconds with one finding and no retained details; 2 MiB
ASCII took 1.294 seconds, and a 2,097,150-byte class-zero continuation run took
0.850 seconds. These are observations on this machine, not timing guarantees.

Normalization can be intentional. Findings need human interpretation; the tool
does not render text, compare fonts, infer malicious intent, or detect whole-
label collisions. Results follow the runtime's Unicode database, so older
Python versions do not recognize scripts added in newer Unicode releases.
