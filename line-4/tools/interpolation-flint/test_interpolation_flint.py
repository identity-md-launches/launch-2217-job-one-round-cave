import copy
from fractions import Fraction
import json
from pathlib import Path
import random
import subprocess
import sys
import unittest

import interpolation_flint as flint
from engine import UnitError


class InterpolationTests(unittest.TestCase):
    def test_demo_and_dimensions(self):
        result = flint.calculate(flint.example())
        self.assertEqual(result['value'], '3.5')
        self.assertEqual(result['segment']['right_weight'], '1/2')
        self.assertEqual(result['segment']['slope_base_value'], '3/500')
        self.assertEqual(result['segment']['slope_base_unit'], 'm*kg^-1')
        self.assertTrue(result['passes'])

    def test_seeded_fraction_oracle(self):
        rng = random.Random(735)
        for _ in range(400):
            xs = sorted(rng.sample(range(-100, 101), rng.randint(2, 8)))
            ys = [rng.randint(-1000, 1000) for x in xs]
            k = rng.randrange(len(xs) - 1)
            weight = Fraction(rng.randrange(101), 100)
            query = xs[k] + weight * (xs[k+1] - xs[k])
            expected = ys[k] + weight * (ys[k+1] - ys[k])
            request = {'schema': 'interpolation-flint/1',
                       'points': [{'x': str(x*1000) + ' ms', 'y': str(y*100) + ' cm'}
                                  for x, y in zip(xs, ys)],
                       'at': '(' + str(query) + ') * s', 'to': 'm'}
            result = flint.calculate(request)
            self.assertEqual(Fraction(result['value']), expected)
            self.assertFalse(result['extrapolated'])

    def test_knots_and_segment_policy(self):
        for value, expected, index in [('0 g', '0', 0), ('500 g', '2', 1), ('1 kg', '5', 1)]:
            request = flint.example()
            request.pop('expect')
            request['at'] = value
            result = flint.calculate(request)
            self.assertEqual(result['value'], expected)
            self.assertEqual(result['segment']['left_index'], index)
            self.assertFalse(result['extrapolated'])

    def test_extrapolation_requires_explicit_boolean(self):
        for query, expected in [('-250 g', '-1'), ('1250 g', '6.5')]:
            request = flint.example()
            request.pop('expect')
            request['at'] = query
            with self.assertRaises(ValueError):
                flint.calculate(request)
            request['extrapolate'] = True
            result = flint.calculate(request)
            self.assertEqual(result['value'], expected)
            self.assertTrue(result['extrapolated'])
        for value in [1, 0, 'true', None, [], {}]:
            request = flint.example()
            request['extrapolate'] = value
            with self.assertRaises(ValueError):
                flint.calculate(request)

    def test_decreasing_flat_and_nonterminating(self):
        request = {'schema': 'interpolation-flint/1', 'points': [
            {'x': '0 s', 'y': '3 m'}, {'x': '3 s', 'y': '2 m'}], 'at': '1 s', 'to': 'm'}
        result = flint.calculate(request)
        self.assertEqual(result['value'], '8/3')
        self.assertEqual(result['segment']['slope_base_value'], '-1/3')
        request['points'][1]['y'] = '300 cm'
        self.assertEqual(flint.calculate(request)['value'], '3')

    def test_dimensionless_and_derived(self):
        request = {'schema': 'interpolation-flint/1', 'points': [
            {'x': '0', 'y': '1 m/s'}, {'x': '2', 'y': '3 m/s'}],
            'at': '1', 'to': 'km/h', 'expect': '7.2 km/h'}
        self.assertTrue(flint.calculate(request)['passes'])

    def test_dimensions_rejected_even_at_exact_knot(self):
        for key, value in [('at', '750 s'), ('to', 'kg'), ('expect', '3.5 s')]:
            request = flint.example()
            request[key] = value
            with self.assertRaises(ValueError):
                flint.calculate(request)
        for axis in ['x', 'y']:
            request = flint.example()
            request['at'] = '0 g'
            request['points'][-1][axis] = '0 s'
            with self.assertRaises(ValueError):
                flint.calculate(request)

    def test_duplicate_or_unsorted_x(self):
        for x in ['500 g', '0.5 kg', '100 g']:
            request = flint.example()
            request['points'][-1]['x'] = x
            with self.assertRaises(ValueError):
                flint.calculate(request)

    def test_strict_shape(self):
        bad = [None, [], {}, {'schema': 'other'}]
        for key, value in [('schema', 'wrong'), ('points', []), ('points', [{}]),
                           ('at', True), ('to', None), ('extra', 'x')]:
            request = flint.example()
            request[key] = value
            bad.append(request)
        request = flint.example()
        request['points'][0]['extra'] = 'x'
        bad.append(request)
        for request in bad:
            with self.assertRaises((ValueError, UnitError)):
                flint.calculate(request)

    def test_units_and_limits(self):
        for target in ['0 mm', '-mm', 'mm + mm', 'unknown', 'degC']:
            request = flint.example()
            request['to'] = target
            with self.assertRaises((ValueError, UnitError)):
                flint.calculate(request)
        request = flint.example()
        request['points'] *= 65
        with self.assertRaises(ValueError):
            flint.calculate(request)
        for expression in ['1e10000 kg', '(' * 40 + '1' + ')' * 40, '1' * 4097]:
            request = flint.example()
            request['at'] = expression
            with self.assertRaises(UnitError):
                flint.calculate(request)

    def test_claim_and_no_mutation(self):
        request = flint.example()
        original = copy.deepcopy(request)
        flint.calculate(request)
        self.assertEqual(request, original)
        request['expect'] = '4 mm'
        result = flint.calculate(request)
        self.assertFalse(result['passes'])
        self.assertEqual(result['check']['difference_base_value'], '-0.0005')

    def test_json_limits_and_duplicate_keys(self):
        for raw in [b'{"at":"a","at":"b"}', b'[' * 5 + b']' * 5,
                    b' ' * 65537, b'\xff', b'{"at":NaN}', b'{"at":1.0}',
                    b'{"at":1}', b'{"at":Infinity}', b'no json']:
            with self.assertRaises((ValueError, UnicodeError)):
                flint.load(raw)
        self.assertEqual(flint.load(json.dumps(flint.example()).encode()), flint.example())

    def test_cli_status_streams(self):
        script = str(Path(__file__).with_name('interpolation_flint.py'))
        for change, expected_exit in [({}, 0), ({'expect': '4 mm'}, 1), ({'to': 'kg'}, 2)]:
            request = flint.example()
            request.update(change)
            run = subprocess.run([sys.executable, '-B', script, 'run'],
                                 input=json.dumps(request).encode(), capture_output=True, timeout=10)
            self.assertEqual(run.returncode, expected_exit, run.stderr)
            if expected_exit == 2:
                self.assertEqual(run.stdout, b'')
                self.assertIn(b'interpolation-flint:', run.stderr)
            else:
                self.assertEqual(run.stderr, b'')
                self.assertEqual(json.loads(run.stdout)['passes'], expected_exit == 0)
        run = subprocess.run([sys.executable, '-B', script, 'demo'], capture_output=True, timeout=10)
        self.assertEqual(run.returncode, 0, run.stderr)


if __name__ == '__main__':
    unittest.main()
