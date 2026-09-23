import importlib.util
import tempfile
import unittest
from pathlib import Path

MODULE = Path(__file__).parents[1] / 'script' / 'file_role_map.py'
spec = importlib.util.spec_from_file_location('file_role_map', MODULE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class FileRoleMapProcessingTests(unittest.TestCase):
    # 代表pathがsource/test/docs/configurationへ正しく分類されることを検証する。
    def test_role_classification(self):
        self.assertEqual('source', mod.role(Path('src/main.py')))
        self.assertEqual('tests', mod.role(Path('tests/test_main.py')))
        self.assertEqual('documentation', mod.role(Path('docs/guide.md')))
        self.assertEqual('configuration', mod.role(Path('config/app.toml')))

    # role mapがscan件数とrole別件数を同じcontractで返すことを検証する。
    def test_build_role_map(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / 'src').mkdir()
            (root / 'src' / 'a.py').write_text('x = 1', encoding='utf-8')
            (root / 'README.md').write_text('doc', encoding='utf-8')
            result = mod.build_role_map(root, 0, 2)

        self.assertEqual('ok', result['status'])
        self.assertEqual(2, result['files_scanned'])
        self.assertEqual(1, result['roles']['source']['file_count'])
        self.assertEqual(1, result['roles']['documentation']['file_count'])


if __name__ == '__main__':
    unittest.main()
