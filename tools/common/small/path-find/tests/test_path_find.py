from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / 'script' / 'path_find.py'


class PathFindTests(unittest.TestCase):
    def run_tool(self, *args: str) -> tuple[int, dict]:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            text=True,
            capture_output=True,
            check=False,
        )
        return result.returncode, json.loads(result.stdout)

    def test_default_scan_is_unlimited_and_dependency_dirs_are_pruned(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            deep = root
            for index in range(24):
                deep = deep / f'd{index}'
            deep.mkdir(parents=True)
            (deep / 'target.txt').write_text('x', encoding='utf-8')
            (root / 'node_modules').mkdir()
            (root / 'node_modules' / 'target.txt').write_text('x', encoding='utf-8')

            code, payload = self.run_tool('target.txt', str(root), '--backend', 'portable')

            self.assertEqual(code, 0)
            self.assertEqual(payload['tool'], 'path-find')
            self.assertEqual(payload['backend'], 'portable')
            self.assertEqual(len(payload['results']), 1)
            self.assertTrue(payload['results'][0]['path'].endswith('target.txt'))
            self.assertFalse(payload['scan_truncated'])

    def test_result_limit_and_scan_limit_are_distinct(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in ('a.txt', 'b.txt', 'c.txt'):
                (root / name).write_text('x', encoding='utf-8')

            code, payload = self.run_tool('*.txt', str(root), '--backend', 'portable', '--max-results', '1')
            self.assertEqual(code, 0)
            self.assertTrue(payload['results_truncated'])
            self.assertFalse(payload['scan_truncated'])

            code, payload = self.run_tool('*', str(root), '--backend', 'portable', '--max-visited', '1', '--max-results', '0')
            self.assertEqual(code, 0)
            self.assertTrue(payload['scan_truncated'])
            self.assertEqual(payload['status'], 'partial')

    def test_missing_root_is_not_empty_success(self):
        code, payload = self.run_tool('*', '/definitely/missing/acr-path-find', '--backend', 'portable')
        self.assertEqual(code, 2)
        self.assertEqual(payload['status'], 'input_missing')


if __name__ == '__main__':
    unittest.main()
