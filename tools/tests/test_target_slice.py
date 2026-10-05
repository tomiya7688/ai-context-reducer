import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
SCRIPT = TOOLS / 'common/large/target-slice/script/target_slice.py'


class TargetSliceTests(unittest.TestCase):
    # test_match_limits_report_only_real_truncation はlimit未満・同数・超過を区別する。
    def test_match_limits_report_only_real_truncation(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'sample.txt'
            for lines, limit, expected_count, truncated in (
                (['hit'], 2, 1, False),
                (['hit', 'hit'], 2, 2, False),
                (['hit', 'hit', 'hit'], 2, 2, True),
            ):
                source.write_text('\n'.join(lines) + '\n', encoding='utf-8')
                result = self.run_slice(source, limit)
                self.assertEqual(result['match_count'], expected_count)
                self.assertEqual(result['matches_truncated'], truncated)

    # test_nonpositive_match_limit_means_unlimited は0以下の上限を無制限として扱う。
    def test_nonpositive_match_limit_means_unlimited(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'sample.txt'
            source.write_text('hit\nhit\nhit\n', encoding='utf-8')
            for limit in (0, -1):
                with self.subTest(limit=limit):
                    result = self.run_slice(source, limit)
                    self.assertEqual(result['match_count'], 3)
                    self.assertFalse(result['matches_truncated'])

    def run_slice(self, source, limit):
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), 'hit', '--max-matches', str(limit), '--before', '0', '--after', '0', str(source)],
            text=True,
            capture_output=True,
            check=True,
        )
        return json.loads(completed.stdout)


if __name__ == '__main__':
    unittest.main()
