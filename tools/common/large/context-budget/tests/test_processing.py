import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / 'script'
sys.path.insert(0, str(SCRIPT))

from processing import summarize


class ContextBudgetTest(unittest.TestCase):
    def test_summary_is_self_describing(self):
        result = summarize([(25, 100, 'a.py')], 10, 'fast', 1, False)
        self.assertEqual(result['tool'], 'context-budget')
        self.assertEqual(result['scanned_text_files'], 1)
        self.assertTrue(result['largest_context_candidates'][0]['token_estimate_is_approximate'])


if __name__ == '__main__':
    unittest.main()
