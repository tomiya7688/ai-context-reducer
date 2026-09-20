import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[1] / 'script'
sys.path.insert(0, str(SCRIPT_DIR))

from messenger import candidate_index, is_test_candidate


class ChangeRouterMessengerTests(unittest.TestCase):
    # test_test_candidate_avoids_substring_false_positive は対象機能の契約と回帰条件が維持されることを確認する。
    def test_test_candidate_avoids_substring_false_positive(self):
        self.assertFalse(is_test_candidate(Path('latest.py'), set()))
        self.assertFalse(is_test_candidate(Path('contest.py'), set()))
        self.assertTrue(is_test_candidate(Path('test_widget.py'), set()))
        self.assertTrue(is_test_candidate(Path('widget.test.js'), set()))
        self.assertTrue(is_test_candidate(Path('widget.py'), {'tests'}))

    # test_exact_index_cap_is_not_truncated は対象機能の契約と回帰条件が維持されることを確認する。
    def test_exact_index_cap_is_not_truncated(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'tests').mkdir()
            (root / 'tests' / 'test_a.py').write_text('', encoding='utf-8')
            (root / 'docs').mkdir()
            (root / 'docs' / 'a.md').write_text('', encoding='utf-8')

            rows, truncated, errors = candidate_index(root, 2)
            self.assertEqual(2, len(rows))
            self.assertFalse(truncated)
            self.assertEqual(0, errors)

    # test_additional_candidate_marks_truncation は対象機能の契約と回帰条件が維持されることを確認する。
    def test_additional_candidate_marks_truncation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'tests').mkdir()
            (root / 'tests' / 'test_a.py').write_text('', encoding='utf-8')
            (root / 'tests' / 'test_b.py').write_text('', encoding='utf-8')

            rows, truncated, errors = candidate_index(root, 1)
            self.assertEqual(1, len(rows))
            self.assertTrue(truncated)
            self.assertEqual(0, errors)


if __name__ == '__main__':
    unittest.main()
