from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / 'script' / 'text_search.py'


class TextSearchTests(unittest.TestCase):
    def run_tool(self, *args: str) -> tuple[int, dict]:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            text=True,
            capture_output=True,
            check=False,
        )
        return result.returncode, json.loads(result.stdout)

    def test_portable_search_is_json_and_prunes_dependency_dirs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'src').mkdir()
            (root / 'src' / 'a.txt').write_text('alpha\nneedle here\nomega\n', encoding='utf-8')
            (root / 'node_modules').mkdir()
            (root / 'node_modules' / 'hidden.txt').write_text('needle hidden\n', encoding='utf-8')

            code, payload = self.run_tool('needle', str(root), '--backend', 'portable')

            self.assertEqual(code, 0)
            self.assertEqual(payload['tool'], 'text-search')
            self.assertEqual(payload['status'], 'ok')
            self.assertEqual(payload['backend'], 'portable')
            self.assertEqual(payload['matches'], [{'path': 'src/a.txt', 'line': 2, 'text': 'needle here'}])
            self.assertFalse(payload['matches_truncated'])

    def test_limit_reports_real_truncation_and_context_is_structured(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'a.txt').write_text('before\nneedle one\nafter\nneedle two\n', encoding='utf-8')

            code, payload = self.run_tool(
                'needle', str(root), '--backend', 'portable', '--max-results', '1', '--context', '1'
            )

            self.assertEqual(code, 0)
            self.assertTrue(payload['matches_truncated'])
            match = payload['matches'][0]
            self.assertEqual(match['line'], 2)
            self.assertEqual(match['before'], [{'line': 1, 'text': 'before'}])
            self.assertEqual(match['after'], [{'line': 3, 'text': 'after'}])

    def test_invalid_regex_and_missing_root_are_not_empty_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, payload = self.run_tool('(', tmp, '--backend', 'portable')
            self.assertEqual(code, 2)
            self.assertEqual(payload['status'], 'invalid_pattern')

        code, payload = self.run_tool('needle', '/definitely/missing/acr-text-search', '--backend', 'portable')
        self.assertEqual(code, 2)
        self.assertEqual(payload['status'], 'input_missing')


if __name__ == '__main__':
    unittest.main()
