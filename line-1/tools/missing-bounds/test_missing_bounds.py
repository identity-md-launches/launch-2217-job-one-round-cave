"""Exact completion oracles, masking monotonicity and standalone interface checks."""
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
from fractions import Fraction as F
import missing_bounds as m


def q(x):
    return F(int(x['numerator']), int(x['denominator']))


def ends(c):
    return tuple(map(q, c['candidate_minus_baseline_bounds']))


def csv_bytes(rows, names=('a',)):
    return ('case,baseline,'+','.join(names)+'\n'+''.join(
        f'c{i},'+','.join('?' if x is None else str(x) for x in row)+'\n'
        for i, row in enumerate(rows))).encode()


class MissingTests(unittest.TestCase):
    def test_all_nine_visible_pairs(self):
        for b, c in itertools.product((0, 1, None), repeat=2):
            raw = csv_bytes([(b,c)])
            out = m.analyze(raw)['candidates'][0]
            completions = [(bb,cc) for bb,cc in itertools.product((0,1), repeat=2)
                           if (b is None or b == bb) and (c is None or c == cc)]
            differences = [cc-bb for bb,cc in completions]
            self.assertEqual(list(map(q,out['sample_difference_identification_bounds'])),
                             [min(differences),max(differences)])
            self.assertEqual(out['candidate_only_pass_count_range'],
                             [int(all(d==1 for d in differences)),int(1 in differences)])
            self.assertEqual(out['baseline_only_pass_count_range'],
                             [int(all(d==-1 for d in differences)),int(-1 in differences)])

    def test_exhaustive_completion_envelope(self):
        # Every 2-row missing pattern, every possible latent completion; exact endpoints.
        choices = list(itertools.product((0,1,None),repeat=2))
        for rows in itertools.product(choices,repeat=2):
            report = m.analyze(csv_bytes(rows))['candidates'][0]
            lo, hi = ends(report)
            possible = []
            for row in rows:
                possible.append([pair for pair in itertools.product((0,1),repeat=2)
                                 if all(x is None or x==y for x,y in zip(row,pair))])
            intervals = [ends(m.engine.analyze(csv_bytes(full))['candidates'][0])
                         for full in itertools.product(*possible)]
            self.assertEqual(lo,min(x[0] for x in intervals))
            self.assertEqual(hi,max(x[1] for x in intervals))

    def test_complete_data_exactly_matches_predecessor(self):
        rng = random.Random(3601)
        for _ in range(30):
            rows = [tuple(rng.randrange(2) for _ in range(4)) for _ in range(rng.randrange(1,20))]
            raw = csv_bytes(rows,('a','b','c'))
            actual, old = m.analyze(raw), m.engine.analyze(raw)
            for new, prior in zip(actual['candidates'],old['candidates']):
                for field in ('candidate_minus_baseline_bounds','candidate_exceeds_positive_margin',
                              'baseline_exceeds_positive_margin','entire_interval_strictly_inside_equivalence_margin'):
                    self.assertEqual(new[field],prior[field])
            self.assertEqual(actual['missing_cells'],0)

    def test_masking_only_widens_and_cannot_gain_criteria(self):
        rng = random.Random(3602)
        for _ in range(50):
            rows = [tuple(rng.randrange(2) for _ in range(3)) for _ in range(12)]
            masked = [tuple(None if rng.randrange(3)==0 else x for x in row) for row in rows]
            before = m.analyze(csv_bytes(rows,('a','b')))
            after = m.analyze(csv_bytes(masked,('a','b')))
            for old,new in zip(before['candidates'],after['candidates']):
                self.assertLessEqual(ends(new)[0],ends(old)[0])
                self.assertGreaterEqual(ends(new)[1],ends(old)[1])
                for field in ('candidate_exceeds_positive_margin','baseline_exceeds_positive_margin',
                              'entire_interval_strictly_inside_equivalence_margin'):
                    self.assertFalse(new[field] and not old[field])

    def test_all_missing_keeps_rows_and_family(self):
        result = m.analyze(csv_bytes([(None,None,None)]*25,('a','b')))
        self.assertEqual(result['planned_cases_retained'],25)
        self.assertEqual(result['missing_cells'],75)
        self.assertEqual(result['candidate_count'],2)
        for c in result['candidates']:
            self.assertEqual(ends(c),(F(-1),F(1)))
            self.assertEqual(c['incomplete_pairs'],25)
            self.assertFalse(c['entire_interval_strictly_inside_equivalence_margin'])

    def test_baseline_swap_and_exact_sample_bounds(self):
        rows = [(None,1),(1,None),(0,0),(None,None),(0,1)]
        c = m.analyze(csv_bytes(rows))['candidates'][0]
        swapped = m.analyze(csv_bytes([(b,a) for a,b in rows]))['candidates'][0]
        lo,hi=ends(c)
        self.assertEqual(ends(swapped),(-hi,-lo))
        self.assertEqual(list(map(q,c['sample_difference_identification_bounds'])),[F(-1,5),F(3,5)])

    def test_family_and_alpha_only_widen(self):
        raw=csv_bytes([(0,1)]*25)
        original=ends(m.analyze(raw)['candidates'][0])
        family=ends(m.analyze(csv_bytes([(0,1,None)]*25,('a','b')))['candidates'][0])
        alpha=ends(m.analyze(raw,F(1,100))['candidates'][0])
        for low,high in (family,alpha):
            self.assertLessEqual(low,original[0]); self.assertGreaterEqual(high,original[1])

    def test_invalid_csv_and_scalars(self):
        for raw in (b'',b'case,baseline,a\n',b'case,baseline,a\nx,,1\n',
                    b'case,baseline,a\nx,NA,1\n',b'case,baseline,a\nx,?,?\nx,0,1\n',
                    b'case,baseline,a\nx,?,true\n',b'case,baseline,a\n\n',
                    b'case,baseline,a,a\nx,0,?,1\n',b'case,baseline,a\n x,?,1\n',
                    b'case,baseline,a\nx,0,1,?\n',b'case,baseline,a\nx,0,1\n\xff',
                    csv_bytes([(None,None)]*513),b'x'*(m.engine.MAX_BYTES+1)):
            with self.subTest(raw=raw[:30]),self.assertRaises(m.InputError): m.analyze(raw)
        for a,d in [(0.05,F(1,10)),(F(0),F(1,10)),(F(1,20),0.1)]:
            with self.assertRaises(m.InputError): m.analyze(m.demo_csv(),a,d)

    def test_unicode_bom_crlf_and_input_pin(self):
        raw='\ufeffcase,baseline,"系统,a"\r\n"é,一",?,1\r\n'.encode()
        out=m.analyze(raw)
        self.assertEqual(out['candidates'][0]['name'],'系统,a')
        self.assertEqual(out['input_sha256'],hashlib.sha256(raw).hexdigest())

    def test_demo_loses_complete_data_claims(self):
        before=m.engine.analyze(m.engine.demo_csv())
        after=m.analyze(m.demo_csv())
        self.assertTrue(before['candidates'][0]['candidate_exceeds_positive_margin'])
        self.assertTrue(before['candidates'][1]['entire_interval_strictly_inside_equivalence_margin'])
        self.assertFalse(after['candidates'][0]['candidate_exceeds_positive_margin'])
        self.assertFalse(after['candidates'][1]['entire_interval_strictly_inside_equivalence_margin'])

    def test_maximum_shape(self):
        raw=csv_bytes([(None,)*17]*512,tuple('a'+str(i) for i in range(16)))
        out=m.analyze(raw)
        self.assertEqual(out['missing_cells'],8704)
        self.assertTrue(all(ends(c)==(-1,1) for c in out['candidates']))

    def test_copied_folder_cli_validation_and_immutability(self):
        scratch=Path.cwd()/'test'/'scratch'
        scratch.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as temp:
            folder=Path(temp)
            for name in ('missing_bounds.py','bounds_engine.py'):
                shutil.copyfile(Path(m.__file__).parent/name,folder/name)
            raw=m.demo_csv(); (folder/'data.csv').write_bytes(raw)
            pin=hashlib.sha256(raw).hexdigest()
            def run(*args):
                return subprocess.run([sys.executable,'-B','missing_bounds.py',*args],cwd=folder,
                                      capture_output=True,text=True,timeout=30)
            demo=run('--demo')
            self.assertEqual(demo.returncode,0,demo.stderr)
            self.assertEqual(json.loads(demo.stdout)['missing_cells'],30)
            good=run('--input','data.csv','--expected-input-sha256',pin)
            self.assertEqual(good.returncode,0,good.stderr)
            for args in [('--input','data.csv'),('--input','data.csv','--expected-input-sha256','0'*64),
                         ('--demo','--alpha','NaN'),('--demo','--margin',' 0.1'),
                         ('--demo','--expected-input-sha256',pin)]:
                result=run(*args)
                self.assertEqual(result.returncode,2)
                self.assertEqual(result.stdout,'')
            outside=folder.parent/'missing-bounds-outside.csv'
            outside.write_bytes(raw)
            try:
                (folder/'escape.csv').symlink_to(outside)
                bad=run('--input','escape.csv','--expected-input-sha256',pin)
                self.assertEqual(bad.returncode,2)
                self.assertEqual(bad.stdout,'')
            finally: outside.unlink()
            self.assertEqual((folder/'data.csv').read_bytes(),raw)


if __name__=='__main__': unittest.main()
