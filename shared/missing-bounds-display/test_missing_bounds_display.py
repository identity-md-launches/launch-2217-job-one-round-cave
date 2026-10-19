"""Check missingness retention, outward display and portable offline execution."""
from fractions import Fraction as F
import hashlib
import itertools
import json
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile
import unittest

import missing_bounds_display as app


def summarize(raw, **options):
    return app.summarize(raw, hashlib.sha256(raw).hexdigest(), **options)


class MissingDisplayTests(unittest.TestCase):
    def test_original_analysis_retained_and_intervals_distinct(self):
        raw = app.missing.demo_csv()
        result = summarize(raw)
        self.assertEqual(result['analysis'], app.missing.analyze(raw))
        self.assertEqual(result['analysis']['planned_cases_retained'], 120)
        self.assertEqual(result['analysis']['missing_cells'], 30)
        improved, unchanged = result['candidates']
        self.assertEqual(improved['complete_pairs'], 90)
        self.assertEqual(improved['incomplete_pairs'], 30)
        sample = improved['sample_identification_percentage_points']
        self.assertEqual([sample['lower'], sample['upper']], ['25.00', '50.00'])
        confidence = improved['population_confidence_percentage_points']
        self.assertEqual([confidence['lower'], confidence['upper']], ['6.27', '61.64'])
        self.assertNotEqual(confidence, sample)
        self.assertFalse(any(improved['exact_criteria'].values()))
        self.assertEqual(unchanged['incomplete_pairs'], 10)

    def test_wholly_missing_rows_and_columns_are_retained(self):
        result = summarize(b'case,baseline,a,b\nx,?,?,?\ny,?,?,?\n')
        self.assertEqual(result['analysis']['planned_cases_retained'], 2)
        self.assertEqual(result['analysis']['candidate_count'], 2)
        self.assertEqual(result['analysis']['missing_cells'], 6)
        for row in result['candidates']:
            self.assertEqual(row['complete_pairs'], 0)
            self.assertEqual(row['incomplete_pairs'], 2)
            for key in ('sample_identification_percentage_points', 'population_confidence_percentage_points'):
                self.assertEqual([row[key]['lower'], row[key]['upper']], ['-100.00', '100.00'])
            self.assertFalse(any(row['exact_criteria'].values()))

    def test_display_contains_every_completion_of_small_incomplete_table(self):
        raw = b'case,baseline,a,b\nx,?,1,?\ny,1,?,0\n'
        report = summarize(raw)
        for values in itertools.product('01', repeat=3):
            completed = raw
            for value in values:
                completed = completed.replace(b'?', value.encode(), 1)
            complete_report = app.bounds.analyze(completed)
            for shown, exact in zip(report['candidates'], complete_report['candidates']):
                lo, hi = map(app.rational, exact['candidate_minus_baseline_bounds'])
                outer = shown['population_confidence_percentage_points']
                self.assertLessEqual(F(outer['lower']) / 100, lo)
                self.assertGreaterEqual(F(outer['upper']) / 100, hi)

    def test_complete_data_agrees_with_complete_engine(self):
        raw = b'case,baseline,a,b\nx,0,1,0\ny,1,0,1\nz,0,1,1\n'
        result = summarize(raw)
        previous = app.bounds.analyze(raw)
        self.assertEqual(result['analysis']['missing_cells'], 0)
        for new, old in zip(result['analysis']['candidates'], previous['candidates']):
            self.assertEqual(new['candidate_minus_baseline_bounds'], old['candidate_minus_baseline_bounds'])
            for key in app.criteria(F(0), F(1), F(1,10)):
                self.assertEqual(new[key], old[key])

    def test_outward_enclosure_independent_fraction_oracle(self):
        rng = random.Random(73718)
        for _ in range(200):
            low, high = sorted(F(rng.randint(-10000, 10000), rng.randint(1,10000)) for _ in range(2))
            places = rng.randrange(7)
            scale = 10 ** places
            shown = app.display_interval(low, high, places)
            self.assertEqual(F(shown['lower']), F((low * 100 * scale).__floor__(), scale))
            self.assertEqual(F(shown['upper']), F((high * 100 * scale).__ceil__(), scale))
            self.assertEqual(F(shown['lower_rounding_error']), F(shown['lower']) - low * 100)
            self.assertEqual(F(shown['upper_rounding_error']), F(shown['upper']) - high * 100)

    def test_strict_boundaries_and_precision_never_gains_criterion(self):
        margin = F(1,10)
        self.assertFalse(any(app.criteria(-margin, margin, margin).values()))
        # Outward rounding can lose an exact equivalence decision.
        lo, hi = F(-99,1000), F(99,1000)
        shown = app.display_interval(lo, hi, 0)
        self.assertTrue(app.criteria(lo, hi, margin)['entire_interval_strictly_inside_equivalence_margin'])
        self.assertFalse(app.criteria(F(shown['lower'])/100, F(shown['upper'])/100, margin)['entire_interval_strictly_inside_equivalence_margin'])
        for places in range(7):
            for row in summarize(app.missing.demo_csv(), places=places)['candidates']:
                for key, value in row['displayed_interval_criteria'].items():
                    self.assertFalse(value and not row['exact_criteria'][key])

    def test_bad_inputs_and_pins(self):
        raw = app.missing.demo_csv()
        for pin in (None, '', 'f'*64, hashlib.sha256(raw).hexdigest().upper()):
            with self.assertRaises(ValueError):
                app.summarize(raw, pin)
        for places in (-1, 7, True, 1.0):
            with self.assertRaises(ValueError):
                summarize(raw, places=places)
        for raw in (b'case,baseline,a\nx,,?\n', b'case,baseline,a\nx,NA,0\n',
                    b'case,baseline,a\nx,?,1\nx,0,1\n', b'\xff'):
            with self.assertRaises(ValueError): summarize(raw)

    def test_unicode_and_original_bytes_are_preserved(self):
        raw = '\ufeffcase,baseline,\u00e9,e\u0301\r\n\u03bb,?,1,?\r\n'.encode()
        result = summarize(raw)
        self.assertEqual([r['candidate'] for r in result['candidates']], ['\u00e9', 'e\u0301'])
        self.assertEqual(result['analysis']['candidate_count'], 2)
        self.assertEqual(result['analysis']['missing_cells'], 2)
        self.assertEqual(result['input_sha256'], hashlib.sha256(raw).hexdigest())

    def test_snapshot_provenance(self):
        here = Path(app.__file__).parent
        for row in json.loads((here/'provenance.json').read_text()):
            self.assertEqual(hashlib.sha256((here/row['copy']).read_bytes()).hexdigest(), row['sha256'])

    def test_copied_folder_cli_input_pins_escaping_and_no_partial_json(self):
        scratch = Path('test/scratch').resolve(); scratch.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as tmp:
            folder = Path(tmp)/'tool'
            shutil.copytree(Path(app.__file__).parent, folder, ignore=shutil.ignore_patterns('__pycache__'))
            command = [sys.executable, '-B', 'missing_bounds_display.py']
            def run(args, raw=None):
                return subprocess.run(command+args, cwd=folder, input=raw, capture_output=True, timeout=30)
            demo = run(['demo'])
            self.assertEqual(demo.returncode, 0, demo.stderr)
            self.assertEqual(json.loads(demo.stdout)['data_kind'], 'synthetic_demonstration')
            raw = 'case,baseline,\u00e9\nx,?,1\n'.encode()
            pin = hashlib.sha256(raw).hexdigest()
            good = run(['analyze', '--expected-input-sha256', pin], raw)
            self.assertEqual(good.returncode, 0, good.stderr)
            self.assertTrue(all(b < 128 for b in good.stdout))
            self.assertEqual(json.loads(good.stdout)['analysis'], app.missing.analyze(raw))
            for args, data in ((['analyze'], raw), (['analyze', '--expected-input-sha256', 'f'*64], raw),
                               (['demo','--places','7'],None), (['demo','--alpha','NaN'],None),
                               (['demo','--expected-input-sha256',pin],None),
                               (['analyze','--expected-input-sha256',pin],raw+b'\n')):
                bad = run(args, data)
                self.assertEqual(bad.returncode, 2, bad.stderr)
                self.assertEqual(bad.stdout, b'')


if __name__ == '__main__':
    unittest.main()
