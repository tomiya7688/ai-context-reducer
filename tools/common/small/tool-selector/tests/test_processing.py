import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / 'script' / 'tool_selector.py'
spec = importlib.util.spec_from_file_location('tool_selector', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ToolSelectorProcessingTests(unittest.TestCase):
    # tool pathとlanguage group pathを別schemaで返す現行routing contractを検証する。
    def test_tool_paths_and_group_paths_are_separate(self):
        tools, conditional_tools, groups, conditional_groups = module.recommend(
            'medium', [('python', 10)], [], docs=1, tests=1, has_git=True
        )
        tool_paths = [row['tool_path'] for row in tools]
        conditional_paths = [row['tool_path'] for row in conditional_tools]
        group_paths = [row['tool_group_path'] for row in groups]
        conditional_group_paths = [row['tool_group_path'] for row in conditional_groups]

        self.assertIn('common/medium/compact-diff', tool_paths)
        self.assertIn('python/small', group_paths)
        self.assertNotIn('python/small', tool_paths)
        self.assertIn('python/medium', conditional_group_paths)
        self.assertTrue(all('/' in path for path in conditional_paths))


if __name__ == '__main__':
    unittest.main()
