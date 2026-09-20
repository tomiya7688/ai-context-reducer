import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

MODULE = Path(__file__).parents[1] / 'script' / 'syntax_health.py'
spec = importlib.util.spec_from_file_location('syntax_health', MODULE)
syntax_health = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(syntax_health)


class SyntaxHealthTests(unittest.TestCase):
    # test_summarize_returns_only_failing_files は対象機能の契約と回帰条件が維持されることを確認する。
    def test_summarize_returns_only_failing_files(self):
        payload = [
            {'path': 'ok.py', 'successful': True, 'error_count': 0, 'missing_count': 0},
            {'path': 'bad.py', 'successful': False, 'error_count': 2, 'missing_count': 1},
        ]
        result = syntax_health.summarize(payload, 80)
        self.assertEqual(result['files_seen'], 2)
        self.assertEqual(result['files_with_syntax_issues'], 1)
        self.assertEqual(result['syntax_issue_files'][0]['path'], 'bad.py')
        self.assertFalse(result['syntax_issue_files_truncated'])

    # test_limit_is_agent_visible_only は対象機能の契約と回帰条件が維持されることを確認する。
    def test_limit_is_agent_visible_only(self):
        payload = [
            {'file': 'b.py', 'errors': 1},
            {'file': 'a.py', 'errors': 1},
        ]
        result = syntax_health.summarize(payload, 1)
        self.assertEqual(result['files_with_syntax_issues'], 2)
        self.assertEqual(len(result['syntax_issue_files']), 1)
        self.assertTrue(result['syntax_issue_files_truncated'])


if __name__ == '__main__':
    unittest.main()
