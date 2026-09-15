import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / 'script' / 'tool_selector.py'
spec = importlib.util.spec_from_file_location('tool_selector', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def paths(rows, key):
    return [row[key] for row in rows]


class ToolSelectorTests(unittest.TestCase):
    def test_recommend_includes_git_tools_with_reasons(self):
        recommended, conditional, recommended_groups, conditional_groups = module.recommend(
            'small', [('python', 3)], [], docs=0, tests=0, has_git=True
        )
        self.assertIn('common/medium/compact-diff', paths(recommended, 'tool_path'))
        self.assertIn('common/medium/remote-delta', paths(conditional, 'tool_path'))
        self.assertIn('python/small', paths(recommended_groups, 'tool_group_path'))
        self.assertEqual(conditional_groups, [])
        self.assertTrue(all(row['reason'] for row in recommended + conditional))

    def test_build_selection_separates_language_and_other_files(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / '.git').mkdir()
            (root / 'main.py').write_text('print(1)\n', encoding='utf-8')
            (root / 'README.md').write_text('# demo\n', encoding='utf-8')
            result = module.build_selection(root)
            self.assertEqual(result['tool'], 'tool-selector')
            self.assertEqual(result['status'], 'ok')
            self.assertTrue(result['git_repository_detected'])
            self.assertEqual(result['language_file_counts'], {'python': 1})
            self.assertEqual(result['recognized_source_files_scanned'], 1)
            self.assertEqual(result['non_language_files_scanned'], 1)
            self.assertFalse(result['scan_truncated'])

    def test_project_type_detection_uses_relative_path_content(self):
        detected = set()
        module.detect_types_from_relative_path('src/parser/token_stream.py', detected)
        self.assertIn('compiler', detected)
        self.assertNotIn('simulation', detected)

    def test_large_rule_heavy_repo_gets_structure_tools(self):
        recommended, conditional, recommended_groups, conditional_groups = module.recommend(
            'large', [('python', 100)], ['rule_heavy'], docs=5, tests=10, has_git=True
        )
        self.assertIn('common/large/context-manifest', paths(recommended, 'tool_path'))
        self.assertIn('common/large/source-structure-index', paths(recommended, 'tool_path'))
        self.assertIn('common/medium/structural-search', paths(conditional, 'tool_path'))
        self.assertIn('common/medium/policy-index', paths(conditional, 'tool_path'))
        self.assertIn('python/small', paths(recommended_groups, 'tool_group_path'))
        self.assertIn('python/large', paths(conditional_groups, 'tool_group_path'))


if __name__ == '__main__':
    unittest.main()
