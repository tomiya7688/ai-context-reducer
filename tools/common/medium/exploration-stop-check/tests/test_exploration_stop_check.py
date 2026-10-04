import importlib.util
from pathlib import Path
import unittest

MODULE = Path(__file__).parents[1] / 'script' / 'exploration_stop_check.py'
spec = importlib.util.spec_from_file_location('exploration_stop_check', MODULE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class ExplorationStopCheckTests(unittest.TestCase):
    # test_ready_when_required_context_is_present は必須contextが揃うと探索を終了可能と判定することを確認します。
    def test_ready_when_required_context_is_present(self):
        result = mod.evaluate('Goal Required Acceptance source tests')
        self.assertTrue(result['stop_broad_exploration'])
        self.assertEqual([], result['missing_required_checks'])

    # test_missing_required_context_is_reported は不足しているcontext名を結果に含めることを確認します。
    def test_missing_required_context_is_reported(self):
        result = mod.evaluate('Goal source')
        self.assertFalse(result['stop_broad_exploration'])
        self.assertIn('required', result['missing_required_checks'])
        self.assertIn('tests', result['missing_required_checks'])

    # test_keyword_substrings_do_not_satisfy_checks はkeyword部分一致を必須条件の充足に数えないことを確認します。
    def test_keyword_substrings_do_not_satisfy_checks(self):
        result = mod.evaluate('Goal Required Acceptance source latest')
        self.assertFalse(result['checks']['tests'])
        self.assertIn('tests', result['missing_required_checks'])

    # test_japanese_terms_remain_supported は日本語の必須語でも語境界判定が使えることを確認します。
    def test_japanese_terms_remain_supported(self):
        result = mod.evaluate('目的 要件 完了条件 対象ファイル 検証')
        self.assertTrue(result['stop_broad_exploration'])


if __name__ == '__main__':
    unittest.main()
