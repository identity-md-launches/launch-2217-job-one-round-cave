import json
import subprocess
import sys
import unittest
from pathlib import Path

from uncertainty_lens import MAX_EVENTS, MAX_INPUT_BYTES, analyze


SCRIPT = Path(__file__).with_name("uncertainty_lens.py")


class LensTests(unittest.TestCase):
    def test_touching_is_ordered_and_overlap_is_uncertain(self):
        out = analyze([{"id": "a", "start": 0, "end": 2},
                       {"id": "b", "start": 2, "end": 4},
                       {"id": "c", "start": 1, "end": 3}])
        self.assertIn({"before": "a", "after": "b"}, out["definite_orders"])
        self.assertEqual(out["uncertain_pairs"], [
            {"events": ["a", "c"], "reason": "intervals overlap"},
            {"events": ["b", "c"], "reason": "intervals overlap"}])

    def test_bad_interval(self):
        with self.assertRaises(ValueError):
            analyze([{"id": "bad", "start": 2, "end": 1}])

    def test_nonfinite_boolean_and_duplicate_ids_rejected(self):
        for value in (float("nan"), float("inf"), -float("inf"), True, False):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "finite nonboolean"):
                analyze([{"id": "a", "start": value, "end": 2}])
            with self.subTest(end=value), self.assertRaisesRegex(ValueError, "finite nonboolean"):
                analyze([{"id": "a", "start": 0, "end": value}])
        with self.assertRaisesRegex(ValueError, "duplicate event id"):
            analyze([{"id": "same", "start": 0, "end": 1},
                     {"id": "same", "start": 1, "end": 2}])

    def test_array_and_event_limits(self):
        with self.assertRaisesRegex(ValueError, "JSON array"):
            analyze({"id": "a", "start": 1, "end": 2})
        events = [{"id": str(i), "start": i, "end": i + 1} for i in range(MAX_EVENTS)]
        out = analyze(events)
        self.assertEqual(len(out["definite_orders"]), MAX_EVENTS * (MAX_EVENTS - 1) // 2)
        with self.assertRaisesRegex(ValueError, "too many events"):
            analyze(events + [{"id": "extra", "start": 0, "end": 1}])

    def test_cli_rejects_nonfinite_json_and_oversize_input(self):
        for payload in (b'[{"id":"a","start":NaN,"end":2}]',
                        b'[{"id":"a","start":0,"end":Infinity}]',
                        b" " * (MAX_INPUT_BYTES + 1)):
            with self.subTest(payload=payload[:60]):
                proc = subprocess.run([sys.executable, "-B", str(SCRIPT), "-"],
                                      input=payload, capture_output=True, check=False)
                self.assertNotEqual(proc.returncode, 0)
                self.assertIn(b"error:", proc.stderr)

    def test_cli_demo_is_stable(self):
        payload = b'[{"id":"first","start":1,"end":2},{"id":"second","start":2,"end":3}]'
        proc = subprocess.run([sys.executable, "-B", str(SCRIPT), "-"],
                              input=payload, capture_output=True, check=True)
        self.assertEqual(json.loads(proc.stdout)["definite_orders"],
                         [{"before": "first", "after": "second"}])


if __name__ == "__main__":
    unittest.main()
