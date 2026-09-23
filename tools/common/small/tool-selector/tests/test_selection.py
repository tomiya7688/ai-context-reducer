import importlib.util
import tempfile
import unittest
from collections import Counter
from pathlib import Path

MODULE = Path(__file__).parents[1] / 'script' / 'tool_selector.py'
spec = importlib.util.spec_from_file_location('tool_selector', MODULE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class ToolSelectorSelectionTests(unittest.TestCase):
    # Large Python repoでtool候補とlanguage group候補が現行schemaへ分離されることを検証する。
    def test_recommend_for_large_python_repo(self):
        recommended, conditional, groups, conditional_groups = mod.recommend(
            'large',
            Counter({'python': 100}).most_common(),
            ['rule_heavy'],
            docs=5,
            tests=10,
            has_git=True,
        )
        recommended_paths = [row['tool_path'] for row in recommended]
        conditional_paths = [row['tool_path'] for row in conditional]
        conditional_group_paths = [row['tool_group_path'] for row in conditional_groups]

        self.assertIn('common/large/context-budget', recommended_paths)
        self.assertIn('python/large', conditional_group_paths)
        self.assertIn('common/medium/policy-index', conditional_paths)
        self.assertTrue(groups)

    # 実repo scanからtest数とGit向けrouting候補を組み立てるcontractを検証する。
    def test_build_selection(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / '.git').mkdir()
            (root / 'tests').mkdir()
            (root / 'main.py').write_text('print(1)', encoding='utf-8')
            (root / 'tests' / 'test_main.py').write_text('def test_x(): pass', encoding='utf-8')
            (root / 'README.md').write_text('# Docs', encoding='utf-8')
            result = mod.build_selection(root)

        self.assertEqual('ok', result['status'])
        self.assertEqual(1, result['test_file_count'])
        recommended_paths = [row['tool_path'] for row in result['recommended_tools']]
        self.assertIn('common/medium/compact-diff', recommended_paths)


if __name__ == '__main__':
    unittest.main()
