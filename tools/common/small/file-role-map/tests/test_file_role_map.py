import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / 'script' / 'file_role_map.py'
spec = importlib.util.spec_from_file_location('file_role_map', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class FileRoleMapTests(unittest.TestCase):
    # test_role_classification は対象機能の契約と回帰条件が維持されることを確認する。
    def test_role_classification(self):
        self.assertEqual(module.role(Path('src/main.py')), 'source')
        self.assertEqual(module.role(Path('tests/test_main.py')), 'tests')
        self.assertEqual(module.role(Path('tests/acceptance.md')), 'tests')
        self.assertEqual(module.role(Path('docs/guide.md')), 'documentation')
        self.assertEqual(module.role(Path('config/app.toml')), 'configuration')

    # test_build_role_map_limits_examples は対象機能の契約と回帰条件が維持されることを確認する。
    def test_build_role_map_limits_examples(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / 'a.py').write_text('', encoding='utf-8')
            (root / 'b.py').write_text('', encoding='utf-8')
            result = module.build_role_map(root, 0, 1)
            source = result['roles']['source']
            self.assertEqual(source['file_count'], 2)
            self.assertEqual(len(source['example_paths']), 1)
            self.assertFalse(result['scan_truncated'])


if __name__ == '__main__':
    unittest.main()
