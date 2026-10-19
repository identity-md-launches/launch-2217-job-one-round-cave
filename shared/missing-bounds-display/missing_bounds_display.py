#!/usr/bin/env python3
"""Display incomplete benchmark evidence without hiding missingness or shrinking bounds."""
import argparse
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent

def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / 'engines' / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

# Round Flint imports its own unchanged arithmetic engine by this name.
# Loading it explicitly makes the folder portable without searching other lines.
engine = load('missing_display_arithmetic', 'engine.py')
previous_engine = sys.modules.get('engine')
sys.modules['engine'] = engine
try:
    rounding = load('missing_display_rounding', 'round_flint.py')
finally:
    if previous_engine is None:
        del sys.modules['engine']
    else:
        sys.modules['engine'] = previous_engine
bounds = load('missing_display_binomial', 'bounds_engine.py')
previous_bounds_engine = sys.modules.get('bounds_engine')
sys.modules['bounds_engine'] = bounds
try:
    missing = load('missing_display_inference', 'missing_bounds.py')
finally:
    if previous_bounds_engine is None:
        del sys.modules['bounds_engine']
    else:
        sys.modules['bounds_engine'] = previous_bounds_engine


def rational(obj):
    return Fraction(int(obj['numerator']), int(obj['denominator']))


def display_interval(lower, upper, places=2):
    """Arguments are exact pass-rate differences, display is percentage points."""
    if type(places) is not int or not 0 <= places <= 6:
        raise ValueError('places must be an integer from 0 to 6')
    if not isinstance(lower, Fraction) or not isinstance(upper, Fraction) or lower > upper:
        raise ValueError('ordered Fraction endpoints required')
    def endpoint(value, mode):
        expression = f'({value.numerator}) / ({value.denominator}) * 100'
        return rounding.calculate(expression, '1', places, mode)
    lo, hi = endpoint(lower, 'floor'), endpoint(upper, 'ceiling')
    return {'lower': lo['rounded'], 'upper': hi['rounded'],
            'lower_rounding_error': lo['error'], 'upper_rounding_error': hi['error']}


def criteria(lower, upper, margin):
    return {'candidate_exceeds_positive_margin': lower > margin,
            'baseline_exceeds_positive_margin': upper < -margin,
            'entire_interval_strictly_inside_equivalence_margin': lower > -margin and upper < margin}


def summarize(raw, pin, alpha=Fraction(1, 20), margin=Fraction(1, 10), places=2):
    # Pin original CSV bytes, not parsed labels or a reserialized table.
    if not isinstance(raw, bytes) or len(raw) > bounds.MAX_BYTES:
        raise ValueError('CSV must be bytes, at most 2 MiB')
    if not isinstance(pin, str) or not re.fullmatch('[0-9a-f]{64}', pin):
        raise ValueError('a retained lowercase 64-hex input SHA-256 is required')
    if hashlib.sha256(raw).hexdigest() != pin:
        raise ValueError('input SHA-256 mismatch')
    display_interval(Fraction(0), Fraction(0), places)
    analysis = missing.analyze(raw, alpha, margin)
    rows = []
    for candidate in analysis['candidates']:
        low, high = map(rational, candidate['candidate_minus_baseline_bounds'])
        shown = display_interval(low, high, places)
        original = criteria(low, high, margin)
        # The displayed endpoints are still exact rationals. Strict comparisons
        # against the unrounded margin can only weaken the original criteria.
        conservative = criteria(Fraction(shown['lower']) / 100,
                                Fraction(shown['upper']) / 100, margin)
        if any(conservative[k] and not original[k] for k in original):
            raise ValueError('display unexpectedly strengthened an exact criterion')
        sample_low, sample_high = map(rational, candidate['sample_difference_identification_bounds'])
        rows.append({'candidate': candidate['name'],
                     'complete_pairs': candidate['complete_pairs'],
                     'incomplete_pairs': candidate['incomplete_pairs'],
                     'sample_identification_percentage_points': display_interval(sample_low, sample_high, places),
                     'population_confidence_percentage_points': shown,
                     'exact_criteria': original, 'displayed_interval_criteria': conservative,
                     'criteria_lost_to_display_precision': [k for k in original if original[k] and not conservative[k]]})
    return {'schema': 'missing-bounds-display/1', 'input_sha256': pin,
            'analysis': analysis, 'display': {'unit': 'percentage points', 'places': places,
                'lower_mode': 'floor', 'upper_mode': 'ceiling',
                'margin_percentage_points': str(margin * 100),
                'rounding_error_means': 'display minus exact, in percentage points'},
            'candidates': rows,
            'limits': [
                'Original rational intervals and decisions are retained unchanged; displayed intervals are enlarged outward.',
                'Coverage requires latent complete case vectors to be independent identically distributed draws, with fixed planned rows and full candidate family.',
                'Every planned row is retained; ? is unknown, never imputed as pass or failure. Unlisted cases cannot be detected.',
                'Sample identification intervals describe possible completed sample means, not population confidence bounds.',
                'No missing-at-random assumption is needed; every binary completion is enclosed. This does not repair selective omission, optional stopping or inaccurate observations.',
                'Coverage is repeated-sampling, not a posterior probability; rounding adds no measurement evidence.',
                'The practical margin is an absolute rate difference: 0.1 means ten percentage points, not a relative percent improvement.',
                'Displayed comparisons use the exact unrounded margin and may be inconclusive when the original criterion passes.',
                'A false criterion does not establish its opposite; do not choose precision, margin or family after inspecting outcomes.',
                'Input pins prove byte identity, not honest execution, representative sampling or prospective choices.',
            ]}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['demo', 'analyze'])
    parser.add_argument('--expected-input-sha256')
    parser.add_argument('--alpha', default='0.05')
    parser.add_argument('--margin', default='0.10')
    parser.add_argument('--places', type=int, default=2)
    args = parser.parse_args(argv)
    try:
        alpha = bounds.decimal(args.alpha, 'alpha', Fraction(1, 1000000), Fraction(1, 5))
        margin = bounds.decimal(args.margin, 'margin', Fraction(0), Fraction(1))
        if args.command == 'demo':
            if args.expected_input_sha256 is not None:
                raise ValueError('demo does not accept an input pin')
            raw = missing.demo_csv()
            pin = hashlib.sha256(raw).hexdigest()
        else:
            if args.expected_input_sha256 is None:
                raise ValueError('analyze requires --expected-input-sha256')
            raw = sys.stdin.buffer.read(bounds.MAX_BYTES + 1)
            pin = args.expected_input_sha256
        result = summarize(raw, pin, alpha, margin, args.places)
        result['data_kind'] = 'synthetic_demonstration' if args.command == 'demo' else 'user_supplied_benchmark'
        rendered = json.dumps(result, ensure_ascii=True, allow_nan=False, indent=2) + '\n'
    except (ValueError, TypeError, OSError, OverflowError) as exc:
        parser.exit(2, 'missing-bounds-display: ' + ascii(str(exc))[:240] + '\n')
    sys.stdout.write(rendered)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
