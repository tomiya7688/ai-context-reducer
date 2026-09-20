import sys
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[1] / 'script'
sys.path.insert(0, str(SCRIPT_DIR))

from processing import normalized_stem, route_candidates


class ChangeRouterProcessingTests(unittest.TestCase):
    # test_test_name_normalization は対象機能の契約と回帰条件が維持されることを確認する。
    def test_test_name_normalization(self):
        self.assertEqual(normalized_stem('tests/test_widget.py'), 'widget')
        self.assertEqual(normalized_stem('widget_test.go'), 'widget')

    # test_route_fields_are_self_describing は対象機能の契約と回帰条件が維持されることを確認する。
    def test_route_fields_are_self_describing(self):
        index = [
            {'path': 'tests/test_widget.py', 'name': 'test_widget.py', 'is_test': True, 'is_doc': False},
            {'path': 'docs/widget.md', 'name': 'widget.md', 'is_test': False, 'is_doc': True},
        ]
        result = route_candidates('src/widget.py', index, 8)

        self.assertEqual(result['changed_file'], 'src/widget.py')
        self.assertEqual(result['candidate_tests'], ['tests/test_widget.py'])
        self.assertFalse(result['candidate_tests_truncated'])
        self.assertEqual(result['candidate_docs'], ['docs/widget.md'])
        self.assertFalse(result['candidate_docs_truncated'])
        self.assertNotIn('changed', result)
        self.assertNotIn('tests', result)
        self.assertNotIn('docs', result)

    # test_per_kind_limit_reports_real_truncation は対象機能の契約と回帰条件が維持されることを確認する。
    def test_per_kind_limit_reports_real_truncation(self):
        index = [
            {'path': 'tests/test_widget.py', 'name': 'test_widget.py', 'is_test': True, 'is_doc': False},
            {'path': 'tests/widget_test.py', 'name': 'widget_test.py', 'is_test': True, 'is_doc': False},
        ]
        limited = route_candidates('src/widget.py', index, 1)
        self.assertEqual(1, len(limited['candidate_tests']))
        self.assertTrue(limited['candidate_tests_truncated'])

        unlimited = route_candidates('src/widget.py', index, 0)
        self.assertEqual(2, len(unlimited['candidate_tests']))
        self.assertFalse(unlimited['candidate_tests_truncated'])


if __name__ == '__main__':
    unittest.main()
