#!/usr/bin/env python3
"""Report Unicode sequences whose compatibility or canonical form changes."""
import argparse
import functools
import hashlib
import json
import pathlib
import sys
import unicodedata

MAX_BYTES = 2 * 1024 * 1024
MAX_DETAILS = 1000
DEMO = "owner=Ａdmin\nlabel=Kelvin\ncount=①\nbengali=\u09c7\u09be\ntamil=\u0bc6\u0bbe\nkannada=\u0cc6\u0cc2\u0cd5"


@functools.lru_cache(maxsize=1)
def _class_zero_trailers():
    """Find characters that can complete a canonical composition.

    Consult the active Unicode database instead of assuming only Hangul has
    class-zero composition. Explicit Jamo ranges cover Python databases that
    omit algorithmic Hangul decompositions from decomposition().
    """
    trailers = {chr(cp) for cp in range(0x1161, 0x1176)}
    trailers.update(chr(cp) for cp in range(0x11A8, 0x11C3))
    for cp in range(0x110000):
        character = chr(cp)
        decomposition = unicodedata.decomposition(character)
        if not decomposition or decomposition.startswith("<"):
            continue
        parts = decomposition.split()
        if len(parts) != 2:
            continue
        pair = "".join(chr(int(part, 16)) for part in parts)
        if (unicodedata.combining(pair[1]) == 0 and
                unicodedata.normalize("NFC", pair) == character):
            trailers.add(pair[1])
            trailers.update(unicodedata.normalize(form, pair[1])[0]
                            for form in ("NFD", "NFKD"))
    return frozenset(trailers)


@functools.lru_cache(maxsize=4096)
def _continues_sequence(current):
    """False only at a safe boundary for both NFC and NFKC.

    A decomposed nonstarter can reorder or compose with earlier characters.
    A class-zero composition trailer can compose with the accumulated starter,
    even when the immediately preceding original scalar cannot compose with it.
    Conservative grouping also preserves three-part Kannada compositions.
    """
    if current.isascii():
        return False
    for form in ("NFD", "NFKD"):
        first = unicodedata.normalize(form, current)[0]
        if unicodedata.combining(first) or first in _class_zero_trailers():
            return True
    return False


def _normalize(form, text):
    """Normalize without unbounded quadratic canonical-ordering work.

    Python's normalization can insertion-sort out-of-order combining marks.
    For long spans, decompose each scalar (bounded by the runtime database),
    then stably sort each nonstarter run before asking Python to compose it.
    Short spans use the standard implementation directly.
    """
    if len(text) <= 1024:
        return unicodedata.normalize(form, text)
    decomposition_form = "NFD" if form == "NFC" else "NFKD"
    ordered = []
    marks = []
    for character in text:
        for part in unicodedata.normalize(decomposition_form, character):
            if unicodedata.combining(part):
                marks.append(part)
            else:
                if marks:
                    ordered.extend(sorted(marks, key=unicodedata.combining))
                    marks.clear()
                ordered.append(part)
    ordered.extend(sorted(marks, key=unicodedata.combining))
    return unicodedata.normalize("NFC", "".join(ordered))


def escaped(text):
    return text.encode("unicode_escape").decode("ascii")


def scalar(c):
    return {"codepoint": f"U+{ord(c):04X}",
            "name": unicodedata.name(c, "UNNAMED"),
            "category": unicodedata.category(c)}


def review(data, max_details=100):
    if not isinstance(data, bytes) or len(data) > MAX_BYTES:
        raise ValueError("input must be UTF-8 bytes of at most 2 MiB")
    if not isinstance(max_details, int) or not 0 <= max_details <= MAX_DETAILS:
        raise ValueError("max_details must be an integer from 0 to 1000")
    text = data.decode("utf-8", "strict")
    findings = []
    finding_count = 0
    index = 0
    byte_position = 0
    while index < len(text):
        end = index + 1
        while end < len(text) and _continues_sequence(text[end]):
            end += 1
        original = text[index:end]
        nfc = _normalize("NFC", original)
        nfkc = _normalize("NFKC", original)
        original_bytes = original.encode("utf-8")
        after = byte_position + len(original_bytes)
        if nfc != original or nfkc != original:
            finding_count += 1
            if len(findings) < max_details:
                findings.append({
                    "character_index": index,
                    "source_byte_range": [byte_position, after],
                    "source_span_sha256": hashlib.sha256(original_bytes).hexdigest(),
                    "original": escaped(original),
                    "nfc": escaped(nfc),
                    "nfkc": escaped(nfkc),
                    "original_scalars": [scalar(c) for c in original],
                    "nfc_changed": nfc != original,
                    "nfkc_changed": nfkc != original,
                })
        byte_position = after
        index = end
    return {
        "schema_version": 1,
        "tool": "unicode-normalization/3",
        "source_sha256": hashlib.sha256(data).hexdigest(),
        "source_bytes": len(data),
        "unicode_version": unicodedata.unidata_version,
        "analysis_complete": True,
        "finding_count": finding_count,
        "detail_cap": max_details,
        "retained_details": len(findings),
        "omitted_details": finding_count - len(findings),
        "details": findings,
        "coverage": "UTF-8 text sequences whose NFC or NFKC form differs from the original.",
        "limitations": [
            "Normalization differences can be intentional and are not proof of deception.",
            "This is lexical review; it does not render text or compare fonts.",
            "Boundaries are conservative for NFC and NFKC; cited spans can include unchanged neighboring scalars.",
            "This is not a whole-label collision test; findings are normalization-sensitive sequences.",
            "Source ranges are zero-based UTF-8 byte offsets and output is escaped ASCII JSON.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--demo", action="store_true")
    group.add_argument("--file")
    parser.add_argument("--max-details", type=int, default=100)
    args = parser.parse_args()
    try:
        if args.demo:
            data = DEMO.encode("utf-8")
            source_kind = "synthetic-demo"
        else:
            path = pathlib.Path(args.file)
            root = pathlib.Path.cwd().resolve()
            resolved = path.resolve()
            if not resolved.is_relative_to(root) or not resolved.is_file():
                raise ValueError("file must be a regular file inside the current workspace")
            with resolved.open("rb") as selected:
                data = selected.read(MAX_BYTES + 1)
            source_kind = "selected-workspace-file"
        report = review(data, args.max_details)
        report["source_kind"] = source_kind
        print(json.dumps(report, ensure_ascii=True, sort_keys=True, indent=2))
        return 0
    except (OSError, UnicodeError, ValueError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=True), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
