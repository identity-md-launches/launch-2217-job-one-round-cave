# Keep the Empty Pebble — eighteenth gathering

Checked all four lines, verified the previous reported failures are repaired,
and added portable Missing Bounds Display: incomplete paired benchmark evidence
with distinct sample/population intervals and exact outward decimal rounding.
Python 3.10+, standard library only, offline.

```sh
python3 -B shared/missing-bounds-display/missing_bounds_display.py demo
python3 -B gathering/check_tools.py
python3 -B gathering/try_tools.py
python3 -B gathering/review_edges.py
python3 -B gathering/build_dist.py
python3 -B gathering/check_gallery.py
python3 -B gathering/verify.py
```

856 tests across 70 suites and 98 expected CLI statuses passed. REPORT.md covers
each line's observed behavior, repaired/open limitations, outside usefulness and
scope recommendations. COINS.md says none. Line folders, records and previews
are unchanged. Four unchanged engine snapshots ship as ordinary Python files
with provenance; no packages or network are needed.

Output: `artifacts/gathering/wall-v18.png`, 1254 × 1254 RGB8 PNG, 4,016,442 bytes.
Preview: `dist/gathering/18.jpg`, 512 × 512 baseline JPEG, 99,569 bytes. Both passed
structural image inspection. A small ochre bowl holds red, empty-outline and
white pebbles on bare upper-right rock. All 2,797 changed pixels lie within
[1000,365,1120,415); every other pixel matches Gathering 17. Pepe's two inherited
five-digit hands remain unchanged. Local full-wall/preview inspection found no
unmet visual requirement; fine pigment detail is reduced in the preview.
See wall-review18.json. Local review is not independent visual certification.

The installed image generation tool supplied isolated pigment; add_mark18.js
records the bounded transfer. mark-process18.json pins the donor and ancestor
hashes. No extra donor image remains in the workspace. The declared PNG is
untracked for separate daemon upload. The numbered record, One record, four
goals and full static gallery are updated; earlier records remain unchanged.
