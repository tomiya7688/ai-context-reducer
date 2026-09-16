import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / 'script' / 'policy_index.py'


class PolicyIndexCLITests(unittest.TestCase):
    def test_zero_limit_means_unlimited(self):
        with tempfile.TemporaryDirectory() as tmp:
            policy = Path(tmp) / 'policy.md'
            policy.write_text('# Rules\nMust test.\nShould document.\n', encoding='utf-8')
            result = subprocess.run(
                [sys.executable, str(SCRIPT), '--max-findings', '0', str(policy)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(2, payload['finding_count_total'])
            self.assertEqual(2, len(payload['findings']))
            self.assertFalse(payload['findings_truncated'])

    def test_missing_only_input_is_explicit_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / 'missing.md'
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(missing)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(2, result.returncode)
            payload = json.loads(result.stdout)
            self.assertEqual('input_unavailable', payload['status'])
            self.assertEqual([str(missing)], payload['missing_inputs'])


if __name__ == '__main__':
    unittest.main()
