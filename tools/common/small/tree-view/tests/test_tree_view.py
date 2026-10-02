import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT = Path(__file__).parents[1] / 'script' / 'tree_view.py'
spec = importlib.util.spec_from_file_location('tree_view', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class TreeViewTests(unittest.TestCase):
    # test_build_tree_is_bounded は対象機能の契約と回帰条件が維持されることを確認する。
    def test_build_tree_is_bounded(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'a.txt').write_text('a', encoding='utf-8')
            (root / 'b.txt').write_text('b', encoding='utf-8')
            (root / 'dir').mkdir()
            (root / 'dir' / 'c.txt').write_text('c', encoding='utf-8')
            result = module.build_tree(root, 3, 2)
            self.assertEqual(result['tool'], 'tree-view')
            self.assertEqual(result['status'], 'ok')
            self.assertEqual(result['entries_scanned'], 2)
            self.assertTrue(result['entries_truncated'])

    # test_build_tree_marks_entry_kind は対象機能の契約と回帰条件が維持されることを確認する。
    def test_build_tree_marks_entry_kind(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'dir').mkdir()
            result = module.build_tree(root, 1, 0)
            self.assertEqual(result['entries'][0]['kind'], 'directory')

    # test_build_tree_marks_read_failure_warns は部分走査のread errorをclean成功として返さない。
    def test_build_tree_marks_read_failure_warns(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with patch.object(Path, 'iterdir', side_effect=PermissionError('denied')):
                result = module.build_tree(root, 3, 0)
            self.assertEqual(result['status'], 'ok_with_warnings')
            self.assertEqual(result['read_error_paths'], ['.'])

    # test_cli_rejects_missing_and_file_roots はroot取得失敗を正常な空treeとして返さない。
    def test_cli_rejects_missing_and_file_roots(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            file = root / 'root.txt'
            file.write_text('x', encoding='utf-8')
            missing = root / 'missing'
            for target, status in ((missing, 'input_missing'), (file, 'input_not_directory')):
                completed = subprocess.run([sys.executable, str(SCRIPT), str(target)], capture_output=True, text=True)
                self.assertEqual(completed.returncode, 2)
                self.assertEqual(json.loads(completed.stdout)['status'], status)


if __name__ == '__main__':
    unittest.main()
