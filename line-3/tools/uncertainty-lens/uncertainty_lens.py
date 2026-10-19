#!/usr/bin/env python3
"""Summarize definite order and overlap among bounded timestamp intervals."""

import argparse
import json
import math
import sys


MAX_INPUT_BYTES = 256 * 1024
MAX_EVENTS = 128
MAX_PAIRS = MAX_EVENTS * (MAX_EVENTS - 1) // 2


def _endpoint(value):
    # bool is a subclass of int, and NaN silently defeats every ordering test.
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    return not isinstance(value, float) or math.isfinite(value)


def analyze(events):
    if not isinstance(events, list):
        raise ValueError("input must be a JSON array of events")
    if len(events) > MAX_EVENTS:
        raise ValueError(f"too many events (limit {MAX_EVENTS}; at most {MAX_PAIRS} pairs)")
    clean = []
    seen = set()
    for item in events:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str) or not item["id"]:
            raise ValueError("each event needs a nonempty string id")
        if item["id"] in seen:
            raise ValueError(f"duplicate event id: {item['id']!r}")
        seen.add(item["id"])
        start, end = item.get("start"), item.get("end")
        if not _endpoint(start) or not _endpoint(end) or end < start:
            raise ValueError("each event needs finite nonboolean numeric start <= end")
        clean.append({"id": item["id"], "start": start, "end": end})
    ordered, uncertain = [], []
    for i, left in enumerate(clean):
        for right in clean[i + 1:]:
            if left["end"] <= right["start"]:
                ordered.append({"before": left["id"], "after": right["id"]})
            elif right["end"] <= left["start"]:
                ordered.append({"before": right["id"], "after": left["id"]})
            else:
                uncertain.append({"events": [left["id"], right["id"]], "reason": "intervals overlap"})
    return {"events": len(clean), "definite_orders": ordered, "uncertain_pairs": uncertain}


def _read_bounded(path):
    if path in (None, "-"):
        raw = sys.stdin.buffer.read(MAX_INPUT_BYTES + 1)
    else:
        with open(path, "rb") as source:
            raw = source.read(MAX_INPUT_BYTES + 1)
    if len(raw) > MAX_INPUT_BYTES:
        raise ValueError(f"input exceeds {MAX_INPUT_BYTES} bytes")
    return raw.decode("utf-8")


def _reject_constant(value):
    raise ValueError(f"nonfinite JSON number: {value}")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("path", nargs="?", help="JSON array file or - for stdin")
    args = ap.parse_args()
    try:
        events = json.loads(_read_bounded(args.path), parse_constant=_reject_constant)
        result = analyze(events)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        raise SystemExit(f"error: {exc}")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
