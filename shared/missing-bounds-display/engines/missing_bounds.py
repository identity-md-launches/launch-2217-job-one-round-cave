#!/usr/bin/env python3
"""Conservative paired-binary effect bounds without dropping missing outcomes."""
import argparse
import csv
import hashlib
import io
import json
import re
from fractions import Fraction as F
import bounds_engine as engine

InputError = engine.InputError


def parse_csv(raw):
    if not isinstance(raw, bytes) or len(raw) > engine.MAX_BYTES:
        raise InputError('CSV must be bytes, at most 2 MiB')
    try:
        reader = csv.reader(io.StringIO(raw.decode('utf-8-sig'), newline=''), strict=True)
        header = next(reader, [])
        if (not 3 <= len(header) <= engine.MAX_CANDIDATES + 2
                or header[:2] != ['case', 'baseline'] or len(set(header)) != len(header)
                or not all(engine.label(x) for x in header)):
            raise InputError('header: case,baseline followed by 1–16 unique valid candidate names')
        cases, rows = set(), []
        for row in reader:
            if len(row) != len(header) or not engine.label(row[0]):
                raise InputError(f'CSV line {reader.line_num}: invalid case or field count')
            if row[0] in cases or any(x not in ('0', '1', '?') for x in row[1:]):
                raise InputError(f'CSV line {reader.line_num}: duplicate case or invalid outcome; use 0, 1, ?')
            cases.add(row[0])
            rows.append(tuple(None if x == '?' else int(x) for x in row[1:]))
            if len(rows) > engine.MAX_CASES:
                raise InputError(f'at most {engine.MAX_CASES} planned cases are supported')
        if not rows:
            raise InputError('at least one planned case is required')
        return header[2:], rows
    except (UnicodeError, csv.Error) as exc:
        raise InputError('invalid UTF-8 or CSV') from exc


def possibilities(baseline, candidate):
    """All latent paired differences consistent with one visible pair."""
    return {c - b for b in ((0, 1) if baseline is None else (baseline,))
            for c in ((0, 1) if candidate is None else (candidate,))}


def analyze(raw, alpha=F(1, 20), margin=F(1, 10)):
    if (not isinstance(alpha, F) or not F(1, 1000000) <= alpha <= F(1, 5)
            or not isinstance(margin, F) or not 0 <= margin <= 1):
        raise InputError('invalid alpha or margin')
    names, rows = parse_csv(raw)
    n, m = len(rows), len(names)
    tail = alpha / (4 * m)
    cache = {}

    def bounds(k):
        if k not in cache:
            cache[k] = engine.binomial_bounds(n, k, tail)
        return cache[k]

    candidates = []
    for i, name in enumerate(names, 1):
        possible = [possibilities(row[0], row[i]) for row in rows]
        wmin = sum(s == {1} for s in possible)
        wmax = sum(1 in s for s in possible)
        lmin = sum(s == {-1} for s in possible)
        lmax = sum(-1 in s for s in possible)
        low = bounds(wmin)[0] - bounds(lmax)[1]
        high = bounds(wmax)[1] - bounds(lmin)[0]
        candidates.append({
            'name': name,
            'complete_pairs': sum(row[0] is not None and row[i] is not None for row in rows),
            'incomplete_pairs': sum(row[0] is None or row[i] is None for row in rows),
            'candidate_only_pass_count_range': [wmin, wmax],
            'baseline_only_pass_count_range': [lmin, lmax],
            'sample_difference_identification_bounds': [
                engine.fraction(F(sum(min(s) for s in possible), n)),
                engine.fraction(F(sum(max(s) for s in possible), n))],
            'candidate_minus_baseline_bounds': [engine.fraction(low), engine.fraction(high)],
            'candidate_exceeds_positive_margin': low > margin,
            'baseline_exceeds_positive_margin': high < -margin,
            'entire_interval_strictly_inside_equivalence_margin': low > -margin and high < margin,
        })
    return {
        'schema_version': 1, 'input_sha256': hashlib.sha256(raw).hexdigest(),
        'planned_cases_retained': n, 'candidate_count': m,
        'missing_cells': sum(x is None for row in rows for x in row),
        'familywise_alpha': engine.fraction(alpha),
        'simultaneous_coverage_at_least': engine.fraction(1-alpha),
        'practical_margin': engine.fraction(margin),
        'one_sided_tail_budget': engine.fraction(tail), 'outward_grid_bits': engine.BITS,
        'method': 'Envelope of complete-data Paired Bounds over every binary completion; exact outward binomial bounds',
        'candidates': candidates,
        'assumptions': [
            'Latent complete case vectors are independent identically distributed draws from the target population.',
            'Retain the fixed planned case set and full candidate family, including wholly missing rows and columns.',
            'Observed 0/1 outcomes are correct; ? means unknown, never an observed pass or fail.',
            'No missing-at-random assumption is needed: every binary completion is enclosed, even outcome-dependent masking.',
            'Fix final sample size, pass rule, family, alpha and margin before observing outcomes; no repeated looks or optional stopping.',
            'Unlisted or selectively omitted cases, correlated cases, selected families and incorrect observed labels invalidate coverage.',
            'Sample identification bounds describe possible completed sample means, not population confidence bounds.',
            'Non-establishment of a criterion is inconclusive; pins establish byte identity, not honesty or prospective choices.',
        ],
    }


def demo_csv():
    # Deliberately synthetic outage, not missingness observed in measured systems.
    lines = ['case,baseline,improved,unchanged']
    for i in range(120):
        baseline = str(int(i < 40))
        improved = str(int(i < 90))
        unchanged = baseline
        if 80 <= i < 100:
            improved = '?'
        if i >= 110:
            baseline = '?'
        lines.append(f'synthetic-{i+1:03},{baseline},{improved},{unchanged}')
    return ('\n'.join(lines)+'\n').encode()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument('--demo', action='store_true')
    source.add_argument('--input')
    parser.add_argument('--expected-input-sha256')
    parser.add_argument('--alpha', default='0.05')
    parser.add_argument('--margin', default='0.1')
    args = parser.parse_args(argv)
    try:
        alpha = engine.decimal(args.alpha, 'alpha', F(1, 1000000), F(1, 5))
        margin = engine.decimal(args.margin, 'margin', F(0), F(1))
        if args.demo:
            if args.expected_input_sha256 is not None:
                raise InputError('demo does not accept an input pin')
            raw = demo_csv()
        else:
            pin = args.expected_input_sha256
            if not pin or not re.fullmatch('[0-9a-f]{64}', pin):
                raise InputError('retained lowercase 64-hex --expected-input-sha256 required')
            raw = engine.load(args.input)
            if hashlib.sha256(raw).hexdigest() != pin:
                raise InputError('input SHA-256 mismatch')
        result = analyze(raw, alpha, margin)
        result['data_kind'] = 'synthetic_demonstration' if args.demo else 'user_supplied_benchmark'
    except (InputError, OSError, ValueError) as exc:
        parser.exit(2, f'error: {exc}\n')
    print(json.dumps(result, indent=2, ensure_ascii=True, allow_nan=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
