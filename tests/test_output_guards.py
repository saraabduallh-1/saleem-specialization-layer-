import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from output_guards import check_rewrite, contains_term

class TestGuards(unittest.TestCase):
    def test_diacritics_and_boundaries(self):
        self.assertTrue(contains_term("حدث فَرْطُ التكيّف هنا", "فرط التكيف"))
        self.assertFalse(contains_term("الهلوسات كثيرة", "هلوسة"))
        self.assertTrue(contains_term("هذه هلوسة بالفعل", "هلوسة"))
    def test_egyptian_drift(self):
        x = check_rewrite("وش المشكلة في المودل؟", "إيه المشكلة مع الموديل؟", style="saudi_colloquial")
        self.assertIn("possible_egyptian_dialect_drift", x.warnings)
    def test_no_false_alarm_if_in_source(self):
        self.assertTrue(check_rewrite("إيه المشكلة؟", "إيه المشكلة بالضبط؟", style="saudi_colloquial").passed)
    def test_missing_term(self):
        x = check_rewrite("النموذج يحفظ البيانات", "النموذج يتذكر البيانات", terms=["فرط التكيف"])
        self.assertFalse(x.checks["canonical_terms_present"])
    def test_newlines(self):
        x = check_rewrite("سطر أول\nسطر ثان", "سطر واحد", preserve_newlines=True)
        self.assertIn("newlines_lost", x.warnings)
    def test_not_a_semantic_validator(self):
        self.assertTrue(check_rewrite("النص", "نص مختلف").passed)

if __name__ == "__main__":
    unittest.main()
