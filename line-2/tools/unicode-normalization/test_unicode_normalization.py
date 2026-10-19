import hashlib
import random
import unicodedata
import unittest

from unicode_normalization import DEMO, MAX_BYTES, _normalize, review


def unescape(text):
    return text.encode("ascii").decode("unicode_escape")


class UnicodeNormalizationTests(unittest.TestCase):
    def assert_reconstructs(self, original):
        data = original.encode("utf-8")
        result = review(data)
        self.assertEqual(result["source_sha256"], hashlib.sha256(data).hexdigest())
        for form in ("NFC", "NFKC"):
            rebuilt = []
            position = 0
            for detail in result["details"]:
                start, end = detail["source_byte_range"]
                self.assertGreaterEqual(start, position)
                self.assertEqual(unescape(detail["original"]), data[start:end].decode())
                self.assertEqual(detail["character_index"], len(data[:start].decode()))
                self.assertEqual(detail["source_span_sha256"], hashlib.sha256(data[start:end]).hexdigest())
                rebuilt.append(data[position:start].decode())
                rebuilt.append(unescape(detail[form.lower()]))
                position = end
            rebuilt.append(data[position:].decode())
            self.assertEqual("".join(rebuilt), unicodedata.normalize(form, original))
        return result

    def test_hangul_jamo_compose_across_class_zero_boundary(self):
        original = "각"
        result = self.assert_reconstructs("x" + original + " y")
        self.assertEqual(result["finding_count"], 1)
        detail = result["details"][0]
        self.assertEqual(unescape(detail["original"]), original)
        self.assertEqual(unescape(detail["nfc"]), "각")
        self.assertEqual(detail["source_byte_range"], [1, 10])

    def test_reported_bengali_and_tamil_regressions(self):
        for original, expected in (("\u09c7\u09be", "\u09cb"),
                                   ("\u0bc6\u0bbe", "\u0bca")):
            with self.subTest(sequence=original):
                result = self.assert_reconstructs("é " + original + "!")
                self.assertEqual(result["finding_count"], 1)
                detail = result["details"][0]
                self.assertEqual(unescape(detail["nfc"]), expected)
                self.assertEqual(detail["source_byte_range"], [3, 9])
                self.assertEqual(detail["character_index"], 2)

    def test_three_part_kannada_composition(self):
        # Looking only at adjacent pairs misses the final length mark.
        result = self.assert_reconstructs("\u0cc6\u0cc2\u0cd5")
        self.assertEqual(result["finding_count"], 1)
        detail = result["details"][0]
        self.assertEqual(unescape(detail["nfc"]), "\u0ccb")
        self.assertEqual(detail["source_byte_range"], [0, 9])

    def test_kirat_rai_non_mark_trailer_when_available(self):
        original = "\U00016d63\U00016d67\U00016d67"
        expected = "\U00016d6a"
        if unicodedata.normalize("NFC", original) != expected:
            self.skipTest("runtime predates Kirat Rai composition data")
        self.assertEqual(unicodedata.category("\U00016d67"), "Lo")
        result = self.assert_reconstructs(original)
        self.assertEqual(result["finding_count"], 1)
        self.assertEqual(unescape(result["details"][0]["nfc"]), expected)

    def test_intervening_nonstarter_blocks_class_zero_composition(self):
        original = "\u09c7\u0301\u09be"
        self.assertEqual(unicodedata.normalize("NFC", original), original)
        self.assertEqual(self.assert_reconstructs(original)["finding_count"], 0)

    def test_compatibility_jamo(self):
        original = "\u3131\u314f"
        detail = self.assert_reconstructs(original)["details"][0]
        self.assertEqual(unescape(detail["nfc"]), original)
        self.assertEqual(unescape(detail["nfkc"]), "가")

    def test_combining_run_is_one_finding_with_exact_bytes(self):
        result = self.assert_reconstructs("é A\u030a\u0301")
        self.assertEqual(result["finding_count"], 1)
        self.assertEqual(result["details"][0]["source_byte_range"], [3, 8])

    def test_leading_nonstarters_reorder(self):
        result = self.assert_reconstructs("\u0315\u0300x")
        self.assertEqual(result["finding_count"], 1)
        self.assertEqual(unescape(result["details"][0]["nfc"]), "\u0300\u0315")

    def test_conservative_group_can_include_unchanged_neighbor(self):
        result = self.assert_reconstructs("Ａ\u09be")
        self.assertEqual(result["finding_count"], 1)
        self.assertEqual(result["details"][0]["source_byte_range"], [0, 6])

    def test_cap_counts_all_and_bounds_details(self):
        result = review(("Ａ \u09c7\u09be " * 20).encode(), max_details=1)
        self.assertEqual((result["finding_count"], result["retained_details"], result["omitted_details"]), (40, 1, 39))
        empty = review(DEMO.encode(), max_details=0)
        self.assertEqual((empty["finding_count"], empty["details"]), (6, []))

    def test_long_combining_run(self):
        result = review(("A" + "\u0301" * 10000).encode(), max_details=0)
        self.assertEqual(result["finding_count"], 1)
        self.assertEqual(result["details"], [])

    def test_long_disordered_run_matches_standard_normalization(self):
        # The large-span path must preserve canonical ordering, stable ties,
        # blocked composition, compatibility expansion, and starter boundaries.
        for original in ("A" + "\u0315\u0300\u0301\u0323" * 700,
                         "\u0315\u0300" * 700,
                         "Ａ\u030a\u0323\u09be\u0345\u0300" * 300):
            for form in ("NFC", "NFKC"):
                with self.subTest(form=form, length=len(original)):
                    self.assertEqual(_normalize(form, original), unicodedata.normalize(form, original))

    def test_runtime_canonical_class_zero_decompositions(self):
        checked = 0
        for cp in range(0x110000):
            original = chr(cp)
            decomposition = unicodedata.decomposition(original)
            if not decomposition or decomposition.startswith("<"):
                continue
            sequence = "".join(chr(int(part, 16)) for part in decomposition.split())
            if len(sequence) < 2 or unicodedata.combining(sequence[-1]) != 0:
                continue
            if unicodedata.normalize("NFC", sequence) != original:
                continue
            checked += 1
            for candidate in {sequence, unicodedata.normalize("NFD", original)}:
                result = self.assert_reconstructs("é " + candidate + "!")
                self.assertGreater(result["finding_count"], 0, f"U+{cp:04X}")
        self.assertGreater(checked, 20)

    def test_mixed_sequences_reconstruct_both_forms(self):
        rng = random.Random(724)
        alphabet = ["a", "Ａ", "é", "\u0301", "\u0315", "\u0323", "\u0345",
                    "\u09c7", "\u09be", "\u0cc6", "\u0cc2", "\u0cd5",
                    "\u1100", "\u1161", "\u11a8", "\u3131", "\u314f", "\ufdfa", " "]
        for _ in range(300):
            self.assert_reconstructs("".join(rng.choices(alphabet, k=30)))

    def test_input_and_detail_limits(self):
        for invalid in ("not bytes", b"\xff", b"A" * (MAX_BYTES + 1)):
            with self.assertRaises((UnicodeError, ValueError)):
                review(invalid)
        for invalid_cap in (-1, 1001, 1.5, "1"):
            with self.assertRaises(ValueError):
                review(b"test", invalid_cap)
        self.assertEqual(review(b"")["finding_count"], 0)
        self.assertEqual(review(b"ASCII text")["finding_count"], 0)


if __name__ == "__main__":
    unittest.main()
