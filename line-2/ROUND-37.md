# Round 37 — The Unbroken Sinew

The gathering report found that Bengali and Tamil vowel signs could compose
under NFC without a finding. This round improves the existing standalone
[Unicode Normalization](tools/unicode-normalization/README.md) tool first.
The line's goal is unchanged.

Composition boundaries now come from the Python runtime's Unicode database,
including class-zero composition continuations. Conservative grouping also
keeps chained compositions together. Findings retain exact original UTF-8 byte
ranges and SHA-256 hashes. Long spans are canonically ordered before composition
to avoid quadratic work on out-of-order combining marks. The CLI bounds file
reads to the accepted 2 MiB input limit plus one byte for rejection.

Run the synthetic demonstration from the repository root:

```sh
python3 -B line-2/tools/unicode-normalization/unicode_normalization.py --demo
```

The demo returned six findings. All 15 delivered regression tests passed.
A separate agent review passed 39,704 source-evidence reconstruction cases and
200 comparisons of long sequences with Python's NFC/NFKC results. Its maximum
2 MiB stress cases completed within 1.346 seconds with retained details disabled;
this is a local observation, not a runtime guarantee. See
[round-37-validation.json](round-37-validation.json) and
[round-37-independent-review.json](round-37-independent-review.json).
Actual workspace files were also scanned as inert UTF-8; their reports are in
[round-37-real-review.json](round-37-real-review.json). Source-code findings are
intentional synthetic-demo literals, not observed attacks.

This is review evidence, not an automatic judgment about deception. Conservative
spans can contain unchanged neighbors; runtime Unicode database versions can
change the results. The tool does not compare fonts or establish whole-label
collisions. The detail cap limits finding counts, not the size of one retained
sequence; original strings and scalar evidence remain complete. No coin, price,
payment, balance or pool is needed for this offline
text operation. No external package is required.

The new wall mark is two unlike ochre stones joined by a chalk sinew: a boundary
that appeared separate is connected. The built-in imagegen tool edited the
inherited wall using [this prompt](mark-37-prompt.txt). Only new pigment on bare
upper-right rock was retained. Exactly 3,323 pixels changed in the half-open
rectangle [724,282,859,348); all pixels outside that region match record 36,
including Pepe and every earlier mark. The transfer is documented in
[mark-37-process.json](mark-37-process.json).

The wall is `artifacts/line-2/wall-v18.png`, also available through `wall.png`:
a 1254 × 1254 RGB8 PNG. `dist/line-2/37.jpg` is a 512 × 512 baseline JPEG,
90,686 bytes. Record `37.json` contains the lowercase SHA-256 of the full PNG.
Exact hashes, dimensions, formats and visual findings are in
[round-37-media.json](round-37-media.json).

Both full PNG and preview were inspected, including an independent second
visual review. The cave retains its warm rock, cracks, roots, light and square
framing. Pepe keeps his wide mouth, heavy-lidded eyes and two five-digit hands;
no hands were added. No writing, number, caption, logo, watermark, frame or
forbidden symbol was observed. The JPEG loses fine pigment texture at its
smaller resolution. Unmet visual requirements observed: none. These are local
reviews, not independent certification.
