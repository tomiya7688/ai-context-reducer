import sys
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[1] / 'script'
sys.path.insert(0, str(SCRIPT_DIR))

from processing import compact_remote_delta


class CompactRemoteDeltaTests(unittest.TestCase):
    def test_compact_result_is_self_describing(self):
        result = compact_remote_delta({
            'status': 'ok',
            'base': 'HEAD',
            'remote': 'origin/main',
            'dirty': False,
            'ahead': 1,
            'behind': 2,
            'diff_stat': '2 files changed',
            'changed_files': ['a.py', 'b.py'],
            'remote_commits': ['abc123 update'],
        }, max_files=40)

        self.assertEqual(result['tool'], 'remote-delta')
        self.assertEqual(result['status'], 'ok')
        self.assertEqual(result['changed_files'], ['a.py', 'b.py'])
        self.assertFalse(result['changed_files_truncated'])
        self.assertNotIn('summary', result)

    def test_changed_files_are_bounded_without_losing_truncation_signal(self):
        result = compact_remote_delta({
            'status': 'ok',
            'base': 'HEAD',
            'remote': 'origin/main',
            'dirty': False,
            'changed_files': ['a.py', 'b.py', 'c.py'],
        }, max_files=2)

        self.assertEqual(result['changed_files'], ['a.py', 'b.py'])
        self.assertTrue(result['changed_files_truncated'])

    def test_failure_status_keeps_unknown_values_explicit(self):
        result = compact_remote_delta({
            'status': 'git_unavailable_or_not_repository',
            'base': 'HEAD',
            'remote': 'origin/main',
            'dirty': None,
        }, max_files=40)

        self.assertIsNone(result['dirty'])
        self.assertIsNone(result['ahead'])
        self.assertIsNone(result['behind'])
        self.assertEqual(result['changed_files'], [])


if __name__ == '__main__':
    unittest.main()
