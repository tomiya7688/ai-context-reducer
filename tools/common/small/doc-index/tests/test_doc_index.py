import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / 'script' / 'doc_index.py'
spec = importlib.util.spec_from_file_location('doc_index', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class DocIndexTests(unittest.TestCase):
    # test_build_index_reports_heading_truncation は対象機能の契約と回帰条件が維持されることを確認する。
    def test_build_index_reports_heading_truncation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'README.md').write_text('# A\n## B\n### C\n', encoding='utf-8')
            result = module.build_index(root, 0, 2)
            self.assertEqual(result['tool'], 'doc-index')
            self.assertEqual(result['status'], 'ok')
            self.assertEqual(result['markdown_files_scanned'], 1)
            self.assertEqual(result['documents'][0]['heading_count'], 3)
            self.assertEqual(len(result['documents'][0]['headings']), 2)
            self.assertTrue(result['documents'][0]['headings_truncated'])

    # test_build_index_reports_document_limit は対象機能の契約と回帰条件が維持されることを確認する。
    def test_build_index_reports_document_limit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'a.md').write_text('# A\n', encoding='utf-8')
            (root / 'b.md').write_text('# B\n', encoding='utf-8')
            result = module.build_index(root, 1, 0)
            self.assertEqual(len(result['documents']), 1)
            self.assertTrue(result['documents_truncated'])


if __name__ == '__main__':
    unittest.main()
