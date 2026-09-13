import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / 'script' / 'tree_view.py'
spec = importlib.util.spec_from_file_location('tree_view', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class TreeViewTests(unittest.TestCase):
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

    def test_build_tree_marks_entry_kind(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'dir').mkdir()
            result = module.build_tree(root, 1, 0)
            self.assertEqual(result['entries'][0]['kind'], 'directory')


if __name__ == '__main__':
    unittest.main()
