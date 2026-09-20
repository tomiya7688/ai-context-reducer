import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / 'script' / 'processing.py'
spec = importlib.util.spec_from_file_location('structural_search_processing', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class StructuralSearchProcessingTests(unittest.TestCase):
    # test_python_fallback_matches_single_node_metavariable は対象機能の契約と回帰条件が維持されることを確認する。
    def test_python_fallback_matches_single_node_metavariable(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / 'sample.py').write_text('print(value)\nother(value)\n', encoding='utf-8')
            result = module.python_ast_search(root, 'print($ARG)', 40)
            self.assertEqual(result['match_count'], 1)
            self.assertFalse(result['matches_truncated'])
            match = result['matches'][0]
            self.assertEqual(match['path'], 'sample.py')
            self.assertEqual(match['start_line_1_based'], 1)
            self.assertEqual(match['captures']['ARG']['text'], 'value')

    # test_repeated_metavariable_requires_same_structure は対象機能の契約と回帰条件が維持されることを確認する。
    def test_repeated_metavariable_requires_same_structure(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / 'sample.py').write_text('same(x, x)\nsame(x, y)\n', encoding='utf-8')
            result = module.python_ast_search(root, 'same($X, $X)', 40)
            self.assertEqual(result['match_count'], 1)
            self.assertEqual(result['matches'][0]['start_line_1_based'], 1)

    # test_fallback_reports_truncation_and_parse_errors は対象機能の契約と回帰条件が維持されることを確認する。
    def test_fallback_reports_truncation_and_parse_errors(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / 'a.py').write_text('print(1)\nprint(2)\n', encoding='utf-8')
            (root / 'broken.py').write_text('def broken(:\n', encoding='utf-8')
            result = module.python_ast_search(root, 'print($ARG)', 1)
            self.assertEqual(result['match_count'], 2)
            self.assertEqual(len(result['matches']), 1)
            self.assertTrue(result['matches_truncated'])
            self.assertEqual(result['parse_error_count'], 1)
            self.assertEqual(result['parse_error_paths'], ['broken.py'])

    # test_variadic_pattern_is_explicitly_unsupported_by_fallback は対象機能の契約と回帰条件が維持されることを確認する。
    def test_variadic_pattern_is_explicitly_unsupported_by_fallback(self):
        with tempfile.TemporaryDirectory() as raw:
            with self.assertRaises(module.PatternError):
                module.python_ast_search(Path(raw), 'call($$$ARGS)', 40)

    # test_ast_grep_normalization_converts_line_to_one_based_and_bounds_text は対象機能の契約と回帰条件が維持されることを確認する。
    def test_ast_grep_normalization_converts_line_to_one_based_and_bounds_text(self):
        rows = [{
            'file': 'src/a.js',
            'language': 'JavaScript',
            'text': 'x' * 300,
            'range': {
                'start': {'line': 2, 'column': 4},
                'end': {'line': 2, 'column': 8},
            },
            'metaVariables': {
                'single': {'A': {'text': 'value'}},
            },
        }]
        matches, truncated = module.normalize_ast_grep_matches(rows, 40)
        self.assertFalse(truncated)
        self.assertEqual(matches[0]['start_line_1_based'], 3)
        self.assertEqual(matches[0]['start_column_0_based'], 4)
        self.assertTrue(matches[0]['matched_text_truncated'])
        self.assertEqual(matches[0]['captures']['A']['text'], 'value')


if __name__ == '__main__':
    unittest.main()
