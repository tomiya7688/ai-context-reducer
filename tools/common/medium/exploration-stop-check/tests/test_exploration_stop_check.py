import importlib.util
from pathlib import Path
import unittest

MODULE = Path(__file__).parents[1] / 'script' / 'exploration_stop_check.py'
spec = importlib.util.spec_from_file_location('exploration_stop_check', MODULE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class ExplorationStopCheckTests(unittest.TestCase):
    # test_ready_when_required_context_is_present は対象機能の契約と回帰条件が維持されることを確認する。
    def test_ready_when_required_context_is_present(self):
        result = mod.evaluate('Goal Required Acceptance source tests')
        self.assertTrue(result['stop_broad_exploration'])
        self.assertEqual([], result['missing_required_checks'])

    # test_missing_required_context_is_reported は対象機能の契約と回帰条件が維持されることを確認する。
    def test_missing_required_context_is_reported(self):
        result = mod.evaluate('Goal source')
        self.assertFalse(result['stop_broad_exploration'])
        self.assertIn('required', result['missing_required_checks'])
        self.assertIn('tests', result['missing_required_checks'])

    # test_keyword_substrings_do_not_satisfy_checks は対象機能の契約と回帰条件が維持されることを確認する。
    def test_keyword_substrings_do_not_satisfy_checks(self):
        result = mod.evaluate('Goal Required Acceptance source latest')
        self.assertFalse(result['checks']['tests'])
        self.assertIn('tests', result['missing_required_checks'])

    # test_japanese_terms_remain_supported は対象機能の契約と回帰条件が維持されることを確認する。
    def test_japanese_terms_remain_supported(self):
        result = mod.evaluate('目的 要件 完了条件 対象ファイル 検証')
        self.assertTrue(result['stop_broad_exploration'])


if __name__ == '__main__':
    unittest.main()
