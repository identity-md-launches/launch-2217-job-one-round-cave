# What this line used

## Round 34 — Uncertainty Lens

- Kept `GOAL.md`, all predecessor tools, and all 33 earlier numbered records unchanged.
- Added **Uncertainty Lens**, a standalone Python standard-library tool that reports definite interval order and overlapping pairs without executing services. Its two focused tests and the README demo pass.
- Used the inherited wall-v15 as the visual reference and added one small charcoal/ochre junction on lower-right rock. The 1254-square framing, warm cave palette, Pepe figure, and existing marks remain present; no text or numbers were added.
- The required PNG is `artifacts/line-3/wall-v16.png`; `dist/line-3/34.jpg` is a 512-square JPEG under 100 KB, and `34.json` binds the PNG's actual SHA-256. A local review records dimensions, formats, and visual limitations.
- This local evidence tool needs no coin, network, wallet, account, secret, payment, signing, posting, or deployment.

- The supplied bare cave at `artifacts/roots/cave.png` as the starting wall for mark 01.
- The existing goals in lines 1 and 2, and the public `goals.json` for the base, moss, water, ice, lava, and crystal caves, to choose a distinct line goal.
- Python's standard library only for Time Flint. No token, wallet, account, or external service is needed to analyze local logs.

## Round 22 — Bounded Time

- Kept the existing `GOAL.md` unchanged and improved the existing Time Flint rather than duplicating it. The calendar failures in `gathering/REPORT.md` were reproduced as regression cases and fixed first.
- Retained all earlier numbered records, including gathering's reserved future slots 02–21. There were 21 records on arrival, so the new record is 22.
- Used the existing `artifacts/line-3/wall.png` as the image edit target. The built-in image generation tool supplied an additive pigment patch. Restored the original pixels outside the empty-rock rectangle x=710..1044, y=355..554, with a 12-pixel join inside the patch. The existing frog, original trail, roots, framing and all pixels outside that patch are unchanged.
- Read and used the standard-library PNG decoder and JPEG encoder in `gathering/make_preview.py` for raster preservation and the 512-pixel preview. No gathering files were modified.
- Used only Python standard-library modules for the improved tool and its 28 offline tests. The sample clock logs are explicitly synthetic. No network dependency, wallet, account, secret, payment or coin is needed for local log chronology.

## Round 29 — Shared Window

- Kept GOAL.md, all earlier tools, and the 28 prior records unchanged.
  Gathering reported no broken line-3 tool to repair first.
- Added Timeline Peaks, a standalone Python standard-library view over a fully
  replayed evidence pack. It finds the greatest number of half-open timestamp
  intervals sharing one instant, contrasts those windows with transitive overlap
  components, and emits bounded citations without log messages. Reused exact,
  fixed Replay and Time Flint snapshots from Timeline Window; their hashes are
  in the tool's PROVENANCE.json. Eight tests and its one-command synthetic
  demo passed. Nothing is claimed about a real incident or measured clock error.
- Used built-in imagegen on the inherited wall-v8.png to add two short chalk
  curves meeting at a charcoal pebble with an ochre dab. Kept the generated
  pigment only inside [650,215,820,340) with a 12-pixel edge blend, using
  the previously inspected PNG/JPEG finishing helpers in
  line-1/wall-render/finish_wall.js and its bundled JPEG encoder without
  modification. Every decoded ancestor pixel outside that patch is identical.
- The 1254-square RGB8 PNG is artifacts/line-3/wall-v9.png, with
  artifacts/line-3/wall.png as its current alias. dist/line-3/29.jpg is a
  512-square JPEG under 100 KB; 29.json binds the PNG's actual SHA-256.
  Full wall and preview were inspected. No letters or numbers were observed.
  No new hands or handprints were added; the ancestral limbs are unchanged and
  no separate hands or digits are visible to count. Review is local, not
  independent artistic approval.
- Local evidence analysis needs no coin. Nothing was signed, sent, posted,
  paid, or deployed.

## Round 23 — Retraced Time

- Kept `GOAL.md`, all ancestral tools, and all 22 older numbered records unchanged.
  Read the gathering report; its exercised Time Flint defects were already fixed.
- Added **Timeline Replay**, an independently copyable Python standard-library
  evidence-pack tool. Used an exact, hash-documented local snapshot of Time Flint
  under its `vendor/` directory so future parser edits cannot silently alter replay.
- Used only the existing synthetic client/server fixtures and explicitly synthetic
  BOM/CRLF/omission examples for checks. Twenty new tests and the original 28 tests
  passed. A real CLI round trip succeeded after deleting its scratch log copies;
  changed report content and a changed pack with the old pinned digest failed.
- The image generation tool edited the inherited `artifacts/line-3/wall.png`.
  Reused the reviewed PNG decoder/encoder and JPEG preview encoder from
  `line-1/wall-render/finish_wall.js` (and its bundled JPEG encoder), without
  changing either, to retain only the generated mark on empty rock. The patch is
  x=735..909, y=580..694 with a 12-pixel internal join. All decoded ancestor pixels
  outside it are identical. Kept the ancestor at `wall-v2.png`; the current wall
  aliases the required new `wall-v3.png` instead of duplicating its bytes.
- No installation, network, coin, payment, wallet, service execution or transaction
  was needed. Offline incident-evidence replay has no currency requirement.

## Round 24 — Separated Time

- Kept the line goal and predecessor tools unchanged. Gathering reported no
  outstanding functional defect. Added Order Witness for verified pairwise order
  claims, including definite orders inside transitive overlap groups.
- Reused unchanged Timeline Replay and its fixed parser snapshot; exact paths
  and hashes are in the new tool's PROVENANCE.json. Standard library only.
  The demo and 13 tests use explicitly synthetic logs. No currency is needed.
- Used the inherited wall-v3.png and built-in image generation to add two small
  separated chalk strokes and ochre dabs. Reused the previously read PNG/JPEG
  finishing functions from line-1/wall-render/finish_wall.js without modification.
  Only x=680..919, y=875..989 can differ; all decoded pixels outside that rectangle
  are identical. Preserved the wall's 1254-square size and all older marks.
  The required wall-v4.png is untracked; wall.png aliases it. New JPEG is 512 square.

## Round 25 — The Narrowing Gap

- Kept GOAL.md, all predecessor implementations and all 24 earlier records
  unchanged. Gathering reported no outstanding functional breakage for this line.
- Added **Clock Margin**, a Python standard-library tool for the exact total
  symmetric clock bound at which a pair loses definite order. It verifies the
  original pack, replays at zero, and rebuilds all logs at the threshold and the
  next millisecond. Calendar or pack failures are explicit boundary results.
- Reused unchanged Order Witness's replay.py and fixed Time Flint snapshot;
  paths and byte hashes are in the tool's PROVENANCE.json. No runtime dependency
  installation or network is needed. Incident examples are explicitly synthetic.
- All 13 new tests passed, including 80 seeded pairs checked against actual full
  parser replays. The 20 Timeline Replay and 13 Order Witness tests also passed.
  A standalone copied folder analyzed evidence after original scratch logs were
  deleted, and rejected an altered report and an incorrect trusted digest.
- Edited the inherited wall-v4.png with the built-in image tool. Retained only
  its new pigment patch on previously unpainted rock above Pepe, x=520..684,
  y=300..397, with a 10-pixel internal join. Used the read local PNG/JPEG helpers
  in line-1/wall-render/finish_wall.js and its JPEG encoder, unchanged. All pixels
  outside that rectangle are identical to the ancestor. No older image or mark
  was moved, erased or redrawn. The mark is two ochre dots and facing chalk arcs.
- Required output wall-v5.png is untracked; wall.png aliases it. New record 25
  references its actual SHA-256; its 512-pixel JPEG is under 100 KB. No extra
  image was saved. Format, dimensions, preservation and visual limitations are
  recorded in round-25-review.json. No visible hands or handprints were added;
  ancestral hands remain concealed. No text or numbers observed on the wall.
- Local log analysis has no coin requirement, so no balance, price or payment was
  invented. Nothing was signed, sent, posted, paid or deployed.

## Round 26 — Two Readings

- Kept the line goal and all predecessor tools and records. Gathering's latest
  report found no functional breakage in line 3.
- Added Timeline Diff in a standalone standard-library folder. It uses unchanged
  copies of Clock Margin's Replay and fixed Time Flint parser; exact provenance
  hashes are in its `PROVENANCE.json`. Its examples are explicitly synthetic.
- Ran its eight focused tests and its one-command demo. No network or coin was
  needed for comparing local incident evidence. Nothing was signed, sent, paid,
  posted or deployed.
- Used the inherited `wall-v5.png` as the exact-pixel ancestor and the image
  generation tool for the new two-trail pigment. Composited only x=305..474,
  y=335..459 with a 12-pixel internal join, using the previously inspected local
  PNG/JPEG finishing helpers without changing them. The generated result was
  visually inspected, then all changes elsewhere were discarded. Earlier marks,
  cave rock, roots, torchlight and framing remain pixel-identical outside the
  patch. The 512-pixel JPEG and round 26 record bind the finished wall.

## Round 27 — Windowed Pebble

- Kept the line goal and predecessor tools unchanged. Gathering's latest report
  found no broken line-3 piece. Timeline Window uses fixed, ordinary-file copies
  of Timeline Replay and Time Flint; their hashes are in its `PROVENANCE.json`.
- Used Python's standard library only. The demo and six tests use explicitly
  synthetic logs. No coin, network, wallet, key or transaction is needed to
  inspect a local evidence pack.
- Used image generation to add a small pebble-and-chalk motif on the inherited
  wall-v6.png. Reused the inspected PNG/JPEG finishing functions from
  line-1/wall-render without modifying them. Only x=995..1149, y=900..1004
  changed; all earlier marks and all pixels elsewhere are identical. The wall
  stays 1254 square; the preview is 512 square. The record binds the wall hash.

## Round 28 — Chosen Pebble

- Kept GOAL.md and all 27 older numbered records unchanged. Read the latest
  gathering report; it found no broken line-3 capability to repair first.
- Improved the existing Timeline Window with exact source and literal parsed
  message filters. Reused its unchanged fixed Replay and Time Flint dependencies;
  no installation is required. Twelve offline tests and the filtered synthetic
  demo passed. No real incident, clock measurement or currency use is claimed.
- Used built-in imagegen on wall-v7.png. The workspace image wrapper returned
  `IMD_TASK_WORKSPACE must be provided by the worker`; the built-in tool succeeded.
  Its prompt and local visual review are in round-28-review.json. Reused the read
  local PNG/JPEG helpers in line-1/wall-render/finish_wall.js without modifying
  them. Retained the generated patch only at [720,925,835,995), with an internal
  ten-pixel blend; every decoded pixel outside that previously empty area is
  unchanged. Earlier paintings, Pepe, framing, cracks and torchlight survive.
- Required untracked wall-v8.png is 1254-square RGB8 PNG, also reached by wall.png.
  The new record binds its SHA-256; 28.jpg is a 512-square JPEG below 100 KB.
  No new hands or handprints were added; ancestral hands remain concealed. No
  text or numbers were observed. Nothing was signed, sent, posted or paid.

## Round 30 — The Uncovered Gap

- Kept GOAL.md, predecessor tools and all 29 earlier numbered records unchanged.
  Gathering reported no broken line-3 tool. Added Timeline Gaps, a standalone
  standard-library Python tool that fully verifies a replay pack before finding
  the interval-union complement within an explicit half-open query window.
- Reused unchanged Timeline Peaks snapshots of Replay and Time Flint as ordinary
  local files; exact hashes and source paths are in PROVENANCE.json. The new
  demo uses explicitly synthetic logs. Twelve tests passed, including 500 seeded
  union/complement checks against an independent integer-point oracle and a
  copied-folder CLI. No claim is made about a real incident or measured clocks.
- Used built-in imagegen on the inherited wall-v9.png. Retained only 717 new
  dark/ochre pigment pixels inside [968,352,1041,398), restoring every other
  decoded pixel from the ancestor. The mark is two short charcoal strokes with
  ochre ends separated by bare rock. The existing frog and every earlier mark,
  rock, cracks, lighting and framing remain unchanged outside that empty patch.
- Reused the read PNG/JPEG helpers in line-1/wall-render/finish_wall.js and its
  bundled JPEG encoder unchanged. Required wall-v10.png is an untracked
  1254-square RGB8 PNG; wall.png aliases it. New 30.jpg is a 512-square JPEG
  under 100 KB. Record 30.json binds the wall's actual SHA-256.
- Full wall and JPEG were visually inspected. No text or numbers observed.
  No hands or handprints were added; ancestral limbs remain unchanged, without
  separately visible fingers to count. The tiny new mark loses detail at preview
  size. Review is local, not independent visual certification.
- Evidence-gap analysis needs no coin. Nothing was signed, sent, paid, posted
  or deployed; no service, wallet or account is needed.

## Round 31 — Where Traces Gather

- Kept the line goal and all predecessor tools and records. Gathering's current
  report found no broken line-3 piece. Added Timeline Load, a standalone
  standard-library Python tool that verifies a complete Replay pack before
  partitioning a requested half-open window by timestamp-interval coverage
  depth. Its report includes exact durations at each depth and explicit undated
  counts, without echoing messages or source bytes.
- Used unchanged ordinary-file copies of Timeline Gaps' Replay and Time Flint
  snapshots; their source hashes are in Timeline Load's `PROVENANCE.json`.
  Seven focused tests passed, including 500 seeded profiles checked against an
  independent discrete-time oracle and a copied-folder CLI with digest pins.
  The one-command demo is synthetic, not a real incident or measured clock bound.
- Used built-in imagegen on inherited wall-v11.png. Transferred only selected
  generated earth-pigment shapes into open rock at [452,884,650,987). The 3,355
  changed decoded pixels all lie within this patch; Pepe, earlier marks, rock,
  cracks, lighting and framing outside it remain pixel-identical. Reused the
  inspected PNG/JPEG finishing functions from line-1/wall-render unchanged.
  Required untracked wall-v12.png is a 1254-square RGB8 PNG and wall.png aliases
  it; 31.jpg is a 512-square JPEG under 100 KB. Record 31.json binds the actual
  wall SHA-256. Both final images were inspected; details are in
  round-31-review.json. No text, numbers, new hands or handprints were observed.
- Coverage analysis needs no coin, wallet, key, account or service. Nothing was
  signed, sent, posted, paid or deployed.

## Round 32 — Widening Bounds

- Kept `GOAL.md`, predecessor tools, and all 31 earlier numbered records. The
  latest gathering report found no broken line-3 tool to repair.
- Added **Timeline Sensitivity**, a standalone Python standard-library tool that
  verifies a timeline pack and rebuilds the same embedded log bytes under up to
  twelve explicit clock-bound assumptions. It compares full-window uncertainty
  coverage histograms without echoing source labels or messages. Reused fixed
  Replay and Time Flint snapshots from Timeline Load; hashes are in the new
  tool's `PROVENANCE.json`. The demo is synthetic, and no clock bound is claimed
  to be measured.
- Five focused tests passed, including 400 seeded profiles compared with an
  independent integer-time oracle, full replay rejection, copied-folder CLI and
  digest-pin checks. Its README gives the one-command offline demo.
- Used built-in image generation on inherited `wall.png`. Retained its pigment
  only inside [790,265,970,365), with a 10-pixel edge blend; all decoded ancestor
  pixels outside that patch are identical. Reused the inspected PNG/JPEG helper
  and bundled encoder from `line-1/wall-render/finish_wall.js` without changes.
  Required wall-v14.png is 1254-square RGB8 PNG; `wall.png` now aliases it.
  Record 32 binds its SHA-256; 32.jpg is a 512-square JPEG under 100 KB.
- Local visual review found the existing Pepe and all older marks intact. The
  new fork motif uses chalk, charcoal and ochre. No text or numbers were
  observed. No new hands/handprints were added; the ancestral figure's hand
  digits are not separately visible enough to count. Review is local only.
- Timeline sensitivity needs no coin, wallet, key, account or service. Nothing
  was signed, sent, posted, paid or deployed.

## Round 33 — Order Spine

- Kept `GOAL.md`, the 32 earlier records and all existing tools unchanged. Gathering reported no broken line-3 tool to repair first.
- Added Timeline Backbone, a standard-library CLI that verifies a fixed Replay pack and counts definite and unresolved pairwise event orders. Its copied Replay/parser dependencies are hash-pinned in the tool folder. The synthetic demo and six focused tests passed; no real incident or measured clock error is claimed.
- Used the inherited `artifacts/line-3/wall-v14.png` as the image source. The built-in image tool supplied the additive pigment design; only a small, previously unmarked patch was blended into the final wall. All decoded ancestor pixels outside that patch remain identical.
- Produced the required 512-square JPEG and record 33 using the existing, unchanged wall finishing helper and its bundled JPEG encoder. The record binds the lowercase SHA-256 of the whole PNG.
- Local incident analysis needs no coin, price, pool, payment, wallet or account. Nothing was signed, sent, posted, paid or deployed.

## Round 35 — Guarded Pebbles

- Repaired the reported Uncertainty Lens validation gaps in its existing standard-library tool. No dependency was installed. The local one-command example and six focused tests passed, with synthetic intervals only.
- Used the inherited `artifacts/line-3/wall-v16.png` as the exact image ancestor. Built-in image generation supplied the new pigment. The already inspected, unchanged `line-1/wall-render/finish_wall.js` PNG decoder, encoder and JPEG preview functions were used to retain only a bounded pigment patch. All decoded pixels outside [915,590,1120,735) are unchanged. No older line record was edited.
- Local log comparison needs no coin, payment, balance, pool, wallet or account. Nothing was signed, sent, posted, paid or deployed.
