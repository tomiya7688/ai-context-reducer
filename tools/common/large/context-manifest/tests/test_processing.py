import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / 'script'
sys.path.insert(0, str(SCRIPT))

from processing import build_manifest, priority


class ContextManifestTests(unittest.TestCase):
    def test_priority_routes_high_source_tests_docs_then_other(self):
        self.assertEqual('P0', priority(Path('README.md')))
        self.assertEqual('P1', priority(Path('src/app.py')))
        self.assertEqual('P2', priority(Path('tests/test_app.py')))
        self.assertEqual('P3', priority(Path('docs/guide.md')))
        self.assertEqual('P4', priority(Path('assets/logo.svg')))

    def test_manifest_is_bounded_and_reports_warnings(self):
        entries = [
            {'path': Path('src/app.py'), 'bytes': 20},
            {'path': Path('README.md'), 'bytes': 10},
            {'path': Path('tests/test_app.py'), 'bytes': 30},
        ]
        result = build_manifest(entries, 2, stat_error_count=1, walk_error_count=2)
        self.assertEqual('ok_with_warnings', result['status'])
        self.assertEqual(3, result['total_files'])
        self.assertEqual(2, result['returned_files'])
        self.assertTrue(result['files_truncated'])
        self.assertEqual('README.md', result['files'][0]['path'])
        self.assertEqual(1, result['stat_error_count'])
        self.assertEqual(2, result['walk_error_count'])

    def test_zero_limit_returns_no_rows_but_preserves_total(self):
        result = build_manifest([{'path': Path('a.py'), 'bytes': 1}], 0)
        self.assertEqual(1, result['total_files'])
        self.assertEqual(0, result['returned_files'])
        self.assertTrue(result['files_truncated'])
        self.assertEqual([], result['files'])


if __name__ == '__main__':
    unittest.main()
