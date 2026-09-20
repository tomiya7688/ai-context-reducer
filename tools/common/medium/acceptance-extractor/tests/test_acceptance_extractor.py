import importlib.util
from pathlib import Path
import unittest

SCRIPT = Path(__file__).parents[1] / 'script' / 'acceptance_extractor.py'
spec = importlib.util.spec_from_file_location('acceptance_extractor', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class AcceptanceExtractorTests(unittest.TestCase):
    # test_section_stops_at_next_heading は対象機能の契約と回帰条件が維持されることを確認する。
    def test_section_stops_at_next_heading(self):
        lines = ['# Goal', 'first', 'second', '# Acceptance', 'done']
        values, truncated = module.section(lines, 0, 40)
        self.assertEqual(['first', 'second'], values)
        self.assertFalse(truncated)

    # test_section_reports_truncation は対象機能の契約と回帰条件が維持されることを確認する。
    def test_section_reports_truncation(self):
        lines = ['# Goal', 'one', 'two', 'three']
        values, truncated = module.section(lines, 0, 2)
        self.assertEqual(['one', 'two'], values)
        self.assertTrue(truncated)

    # test_zero_limit_is_explicitly_truncated_when_content_exists は対象機能の契約と回帰条件が維持されることを確認する。
    def test_zero_limit_is_explicitly_truncated_when_content_exists(self):
        values, truncated = module.section(['# Goal', 'one'], 0, 0)
        self.assertEqual([], values)
        self.assertTrue(truncated)

    # test_heading_terms_use_word_boundaries は対象機能の契約と回帰条件が維持されることを確認する。
    def test_heading_terms_use_word_boundaries(self):
        sections, _ = module.extract_sections(['# Goalkeeper notes', 'not a goal'], 40)
        self.assertEqual([], sections['goal'])
        sections, _ = module.extract_sections(['# Goal', 'ship it'], 40)
        self.assertEqual(['ship it'], sections['goal'])


if __name__ == '__main__':
    unittest.main()
