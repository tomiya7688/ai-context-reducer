import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[1] / 'script'
sys.path.insert(0, str(SCRIPT_DIR))

from ignore_candidates import scan_candidates


class IgnoreCandidatesTests(unittest.TestCase):
    def test_candidate_directory_prunes_subtree(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            nested = root / 'node_modules' / 'pkg'
            nested.mkdir(parents=True)
            (nested / 'debug.log').write_text('x', encoding='utf-8')
            (root / 'src').mkdir()
            (root / 'src' / 'trace.log').write_text('x', encoding='utf-8')

            candidates, errors = scan_candidates(root)
            self.assertEqual(errors, 0)
            self.assertEqual(candidates, [
                {'path': 'node_modules', 'kind': 'directory', 'matched_rule': 'directory_name:node_modules'},
                {'path': 'src/trace.log', 'kind': 'file', 'matched_rule': 'file_extension:.log'},
            ])

    def test_cli_zero_limit_is_unlimited_and_missing_root_is_error(self):
        script = SCRIPT_DIR / 'ignore_candidates.py'
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'build').mkdir()
            (root / 'trace.log').write_text('x', encoding='utf-8')
            run = subprocess.run(
                [sys.executable, str(script), '--limit', '0', str(root)],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(run.returncode, 0, run.stderr)
            payload = json.loads(run.stdout)
            self.assertEqual(payload['candidate_count_total'], 2)
            self.assertFalse(payload['candidates_truncated'])
            self.assertTrue(payload['review_required_before_ignoring'])

            missing = subprocess.run(
                [sys.executable, str(script), str(root / 'missing')],
                capture_output=True, text=True, check=False,
            )
            self.assertNotEqual(missing.returncode, 0)
            self.assertEqual(json.loads(missing.stdout)['status'], 'input_missing')


if __name__ == '__main__':
    unittest.main()
