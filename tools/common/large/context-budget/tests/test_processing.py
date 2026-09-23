import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / 'script'
sys.path.insert(0, str(SCRIPT))

from processing import summarize


class ContextBudgetTest(unittest.TestCase):
    # test_fast_summary_is_self_describingで想定する境界条件と出力契約が回帰していないことを検証する。
    def test_fast_summary_is_self_describing(self):
        result = summarize([(25, 100, 'a.py')], 10, 'fast', 1, False)
        self.assertEqual(result['tool'], 'context-budget')
        self.assertEqual(result['status'], 'ok')
        self.assertEqual(result['scanned_text_files'], 1)
        self.assertTrue(result['token_estimate']['approximate'])
        self.assertEqual(result['token_estimate']['formula'], 'file_size_bytes_div_4')
        self.assertFalse(result['token_estimate']['reads_file_contents'])
        self.assertNotIn('token_estimate_is_approximate', result['largest_context_candidates'][0])

    # test_accurate_mode_is_still_an_estimateで想定する境界条件と出力契約が回帰していないことを検証する。
    def test_accurate_mode_is_still_an_estimate(self):
        result = summarize([(25, 100, 'a.py')], 10, 'accurate', 1, False)
        self.assertTrue(result['token_estimate']['approximate'])
        self.assertEqual(result['token_estimate']['formula'], 'decoded_text_characters_div_4')
        self.assertTrue(result['token_estimate']['reads_file_contents'])

    # test_estimation_failure_is_not_reported_as_clean_okで想定する境界条件と出力契約が回帰していないことを検証する。
    def test_estimation_failure_is_not_reported_as_clean_ok(self):
        result = summarize([], 10, 'accurate', 0, False, estimation_error_count=2)
        self.assertEqual(result['status'], 'ok_with_warnings')
        self.assertEqual(result['estimation_error_count'], 2)


if __name__ == '__main__':
    unittest.main()
