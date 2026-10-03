import contextlib
import importlib
import io
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT_DIR = Path(__file__).resolve().parents[1] / 'script'
sys.path.insert(0, str(SCRIPT_DIR))

from processing import compact_remote_delta
import commander
remote_delta = importlib.import_module('remote_delta')


class CompactRemoteDeltaTests(unittest.TestCase):
    # test_compact_result_is_self_describing は対象機能の契約と回帰条件が維持されることを確認する。
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

    # test_changed_files_are_bounded_without_losing_truncation_signal は対象機能の契約と回帰条件が維持されることを確認する。
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

    # test_failure_status_keeps_unknown_values_explicit は対象機能の契約と回帰条件が維持されることを確認する。
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

    # test_build_remote_delta_distinguishes_environment_ref_and_query_failures はGit failure種別の契約を固定する。
    def test_build_remote_delta_distinguishes_environment_ref_and_query_failures(self):
        root = Path('.')
        with patch.object(commander, 'git_result', return_value=(False, '', 'git_unavailable')):
            result = commander.build_remote_delta(root, 'HEAD', 'origin/main', 40)
        self.assertEqual(result['status'], 'git_unavailable')

        with patch.object(commander, 'git_result', return_value=(False, '', 'git_query_failed')):
            result = commander.build_remote_delta(root, 'HEAD', 'origin/main', 40)
        self.assertEqual(result['status'], 'git_unavailable_or_not_repository')

        with patch.object(commander, 'git_result', side_effect=[
            (True, 'true', ''), (True, '', ''), (False, '', 'git_query_failed'),
            (False, '', 'remote_unavailable'),
        ]):
            result = commander.build_remote_delta(root, 'HEAD', 'origin/missing', 40)
        self.assertEqual(result['status'], 'remote_unavailable')

        with patch.object(commander, 'git_result', side_effect=[
            (True, 'true', ''), (True, '', ''), (False, '', 'git_query_failed'),
            (False, '', 'git_query_failed'),
        ]):
            result = commander.build_remote_delta(root, 'HEAD', 'origin/main', 40)
        self.assertEqual(result['status'], 'git_query_failed')

        with patch.object(commander, 'git_result', side_effect=[
            (True, 'true', ''), (True, '', ''), (True, 'abc123', ''),
            (False, '', 'git_query_failed'), (True, '0', ''), (True, '', ''),
            (True, '', ''), (True, '', ''),
        ]):
            result = commander.build_remote_delta(root, 'missing-base', 'origin/main', 40)
        self.assertEqual(result['status'], 'git_query_failed')

    # test_cli_exit_code_matches_query_status はfailure statusをshell成功として返さない。
    def test_cli_exit_code_matches_query_status(self):
        for status, expected_code in (('git_query_failed', 2), ('remote_unavailable', 0)):
            with self.subTest(status=status):
                result = {'tool': 'remote-delta', 'status': status}
                with patch.object(remote_delta, 'build_remote_delta', return_value=result), \
                        patch.object(sys, 'argv', ['remote-delta']), \
                        contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(remote_delta.main(), expected_code)


if __name__ == '__main__':
    unittest.main()
