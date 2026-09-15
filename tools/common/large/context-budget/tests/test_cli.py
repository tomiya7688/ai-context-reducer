import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / 'script' / 'context_budget.py'


class ContextBudgetCliTest(unittest.TestCase):
    def test_missing_root_is_explicit(self):
        with tempfile.TemporaryDirectory() as raw:
            missing = Path(raw) / 'missing'
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(missing)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual('input_missing', payload['status'])

    def test_file_root_is_not_reported_as_empty_repository(self):
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / 'file.txt'
            path.write_text('text', encoding='utf-8')
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(path)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual('input_not_directory', payload['status'])


if __name__ == '__main__':
    unittest.main()
