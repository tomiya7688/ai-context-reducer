import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[1] / 'script'
sys.path.insert(0, str(SCRIPT_DIR))

from messenger import iter_documents
from processing import collect_duplicates


class DocDuplicateHintsTests(unittest.TestCase):
    # test_dependency_documents_are_not_scanned は対象機能の契約と回帰条件が維持されることを確認する。
    def test_dependency_documents_are_not_scanned(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'docs').mkdir()
            (root / 'docs' / 'a.md').write_text('x', encoding='utf-8')
            (root / 'node_modules').mkdir()
            (root / 'node_modules' / 'README.md').write_text('x', encoding='utf-8')
            paths = [p.relative_to(root).as_posix() for p in iter_documents(root)]
            self.assertEqual(paths, ['docs/a.md'])

    # test_duplicate_groups_are_deterministic は対象機能の契約と回帰条件が維持されることを確認する。
    def test_duplicate_groups_are_deterministic(self):
        text = 'This line is deliberately long enough to be considered duplicate content.'
        groups = collect_duplicates([
            ('b.md', [text]),
            ('a.md', [text]),
        ], 20)
        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0]['occurrences'], [
            {'path': 'a.md', 'line': 1},
            {'path': 'b.md', 'line': 1},
        ])

    # test_cli_zero_limits_are_unlimited_and_missing_root_is_error は対象機能の契約と回帰条件が維持されることを確認する。
    def test_cli_zero_limits_are_unlimited_and_missing_root_is_error(self):
        script = SCRIPT_DIR / 'doc_duplicate_hints.py'
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            text = 'This repeated documentation line is intentionally longer than fifty characters.'
            (root / 'a.md').write_text(text + '\n', encoding='utf-8')
            (root / 'b.md').write_text(text + '\n', encoding='utf-8')
            run = subprocess.run(
                [sys.executable, str(script), '--max-groups', '0', '--max-occurrences-per-group', '0', str(root)],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(run.returncode, 0, run.stderr)
            payload = json.loads(run.stdout)
            self.assertEqual(payload['duplicate_group_count_total'], 1)
            self.assertFalse(payload['duplicate_groups_truncated'])
            self.assertFalse(payload['duplicate_groups'][0]['occurrences_truncated'])

            missing = subprocess.run(
                [sys.executable, str(script), str(root / 'missing')],
                capture_output=True, text=True, check=False,
            )
            self.assertNotEqual(missing.returncode, 0)
            self.assertEqual(json.loads(missing.stdout)['status'], 'input_missing')


if __name__ == '__main__':
    unittest.main()
