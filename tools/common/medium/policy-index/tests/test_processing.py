import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / 'script'
sys.path.insert(0, str(SCRIPT))

from processing import is_policy_line, policy_findings


class PolicyFindingsTest(unittest.TestCase):
    def test_rule_line_has_heading(self):
        findings = list(policy_findings(['# Rules', 'required: targeted tests', 'note']))
        self.assertEqual(findings[0][0], 2)
        self.assertEqual(findings[0][1], 'Rules')

    def test_english_rule_words_use_word_boundaries(self):
        self.assertTrue(is_policy_line('You must run targeted tests.'))
        self.assertTrue(is_policy_line('This should not be skipped.'))
        self.assertFalse(is_policy_line('Mustard belongs in the recipe.'))
        self.assertFalse(is_policy_line('Shoulder width is metadata.'))

    def test_japanese_rule_terms_are_detected(self):
        self.assertTrue(is_policy_line('変更後の検証は必須です。'))
        self.assertTrue(is_policy_line('生成物を直接編集してはならない。'))


if __name__ == '__main__':
    unittest.main()
