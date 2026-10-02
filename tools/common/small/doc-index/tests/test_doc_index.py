import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

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

    # test_build_index_marks_read_failure_warns はdocument取得失敗をclean成功として返さない。
    def test_build_index_marks_read_failure_warns(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'README.md').write_text('# Guide\n', encoding='utf-8')
            with patch.object(Path, 'read_text', side_effect=PermissionError('denied')):
                result = module.build_index(root, 0, 0)
            self.assertEqual(result['status'], 'ok_with_warnings')
            self.assertEqual(result['read_error_paths'], ['README.md'])

    # test_cli_rejects_missing_and_file_roots はroot取得失敗を空indexとして正常扱いしない。
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
