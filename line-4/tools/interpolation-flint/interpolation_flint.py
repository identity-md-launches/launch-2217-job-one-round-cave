#!/usr/bin/env python3
"""Bounded exact piecewise-linear interpolation with explicit dimensions."""
import argparse
from bisect import bisect_right
import json
import sys

from engine import Parser, Quantity, UnitError, dimensions, exact_decimal

MAX_BYTES = 65536


def parse(text, target=False):
    if not isinstance(text, str):
        raise ValueError('quantities and units must be expression strings')
    return Parser(text, target=target).parse()


def bound(value, dims):
    return Parser.bounded(Quantity(value, dims), 0).value


def calculate(request):
    required = {'schema', 'points', 'at', 'to'}
    if not isinstance(request, dict) or not required <= request.keys() or request.keys() - required - {'expect', 'extrapolate'}:
        raise ValueError('request requires schema, points, at, to; optional expect, extrapolate')
    if request['schema'] != 'interpolation-flint/1':
        raise ValueError('unsupported schema')
    allow = request.get('extrapolate', False)
    if type(allow) is not bool:
        raise ValueError('extrapolate must be boolean')
    points = request['points']
    if not isinstance(points, list) or not 2 <= len(points) <= 128:
        raise ValueError('points must contain 2..128 entries')
    parsed = []
    for point in points:
        if not isinstance(point, dict) or set(point) != {'x', 'y'}:
            raise ValueError('each point requires exactly x and y')
        x, y = parse(point['x']), parse(point['y'])
        if parsed:
            if x.dims != parsed[0][0].dims or y.dims != parsed[0][1].dims:
                raise ValueError('all x dimensions and all y dimensions must agree')
            if x.value <= parsed[-1][0].value:
                raise ValueError('x coordinates must be strictly increasing; duplicates are invalid')
        parsed.append((x, y))
    query, target = parse(request['at']), parse(request['to'], target=True)
    xd, yd = parsed[0][0].dims, parsed[0][1].dims
    if query.dims != xd:
        raise ValueError('query dimensions do not match x')
    if target.dims != yd or target.value <= 0:
        raise ValueError('target must have y dimensions and a positive scale')
    outside = query.value < parsed[0][0].value or query.value > parsed[-1][0].value
    if outside and not allow:
        raise ValueError('query outside table; explicit extrapolate=true required')
    i = max(0, min(len(parsed) - 2, bisect_right([x.value for x, _ in parsed], query.value) - 1))
    (x0, y0), (x1, y1) = parsed[i:i+2]
    dx = bound(x1.value - x0.value, xd)
    dy = bound(y1.value - y0.value, yd)
    offset = bound(query.value - x0.value, xd)
    weight = bound(offset / dx, (0, 0, 0, 0))
    increment = bound(weight * dy, yd)
    value = bound(y0.value + increment, yd)
    slope_dims = tuple(a - b for a, b in zip(yd, xd))
    slope = bound(dy / dx, slope_dims)
    shown = bound(value / target.value, yd)
    result = {'schema': 'interpolation-flint-result/1',
              'method': 'piecewise-linear', 'extrapolated': outside,
              'segment': {'left_index': i, 'right_index': i + 1,
                          'left': points[i], 'right': points[i + 1],
                          'right_weight': str(weight),
                          'slope_base_value': str(slope),
                          'slope_base_unit': dimensions(slope_dims)},
              'at': request['at'], 'value': exact_decimal(shown), 'unit': request['to'],
              'base_value': exact_decimal(value), 'base_unit': dimensions(yd),
              'passes': True}
    if 'expect' in request:
        expected = parse(request['expect'])
        if expected.dims != yd:
            raise ValueError('expected dimensions do not match y')
        difference = bound(value - expected.value, yd)
        result['check'] = {'expression': request['expect'], 'matches': difference == 0,
                           'difference_base_value': exact_decimal(difference)}
        result['passes'] = difference == 0
    return result


def reject(value):
    raise ValueError('JSON numeric values are unsupported; use expression strings')


def unique(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError('duplicate JSON key: ' + key)
        obj[key] = value
    return obj


def load(raw):
    if len(raw) > MAX_BYTES:
        raise ValueError('input exceeds 65536 bytes')
    text = raw.decode('utf-8')
    depth = 0
    quoted = escaped = False
    for char in text:
        if quoted:
            if escaped:
                escaped = False
            elif char == '\\':
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '"':
            quoted = True
        elif char in '[{':
            depth += 1
            if depth > 4:
                raise ValueError('JSON nesting exceeds four levels')
        elif char in ']}':
            depth -= 1
    return json.loads(text, object_pairs_hook=unique, parse_int=reject,
                      parse_float=reject, parse_constant=reject)


def example():
    return {'schema': 'interpolation-flint/1',
            'points': [{'x': '0 g', 'y': '0 mm'}, {'x': '500 g', 'y': '2 mm'},
                       {'x': '1 kg', 'y': '5 mm'}],
            'at': '750 g', 'to': 'mm', 'expect': '3.5 mm'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['run', 'demo'])
    args = parser.parse_args(argv)
    try:
        request = example() if args.command == 'demo' else load(sys.stdin.buffer.read(MAX_BYTES + 1))
        result = calculate(request)
    except (ValueError, TypeError, UnicodeError, UnitError, OverflowError) as exc:
        print('interpolation-flint: ' + str(exc), file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0 if result['passes'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
