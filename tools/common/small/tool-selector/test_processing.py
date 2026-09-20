import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name('script') / 'tool_selector.py'
spec = importlib.util.spec_from_file_location('tool_selector', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ToolSelectorTests(unittest.TestCase):
    # test_tool_paths_and_group_paths_are_separate は対象機能の契約と回帰条件が維持されることを確認する。
    def test_tool_paths_and_group_paths_are_separate(self):
        tools, conditional_tools, groups, conditional_groups = module.recommend(
            'medium', [('python', 10)], [], docs=1, tests=1, has_git=True
        )
        self.assertIn('common/medium/compact-diff', tools)
        self.assertIn('python/small', groups)
        self.assertNotIn('python/small', tools)
        self.assertIn('python/medium', conditional_groups)
        self.assertTrue(all('/' in item for item in conditional_tools))


if __name__ == '__main__':
    unittest.main()
