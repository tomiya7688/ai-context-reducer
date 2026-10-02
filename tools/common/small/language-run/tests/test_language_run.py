import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / 'script' / 'language_run.py'
REPO_ROOT = Path(__file__).resolve().parents[5]


class LanguageRunRootTests(unittest.TestCase):
    # test_root_status_and_exit_code_match_native_contract はnative版と同じroot failure semanticsを保つ。
    def test_root_status_and_exit_code_match_native_contract(self):
        with tempfile.TemporaryDirectory(prefix='.tmp-language-run-test-', dir=REPO_ROOT) as tmp:
            base = Path(tmp)
            missing = base / 'missing'
            file = base / 'project.txt'
            file.write_text('not a directory', encoding='utf-8')
            empty = base / 'empty'
            empty.mkdir()
            for root, expected_status, expected_code in (
                (missing, 'input_missing', 2),
                (file, 'input_not_directory', 2),
                (empty, 'ok', 0),
            ):
                with self.subTest(root=root.name):
                    completed = subprocess.run(
                        [sys.executable, str(SCRIPT), str(root)], capture_output=True, text=True,
                    )
                    result = json.loads(completed.stdout)
                    self.assertEqual(completed.returncode, expected_code)
                    self.assertEqual(result['status'], expected_status)
                    if expected_status == 'ok':
                        self.assertEqual(result['failure_count'], 0)
                        self.assertEqual(result['results'], [])
                        self.assertFalse((empty / '.acr' / 'language').exists())


if __name__ == '__main__':
    unittest.main()
