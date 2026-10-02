import contextlib
import importlib.util
import io
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT = Path(__file__).parents[1] / 'script' / 'compact_diff.py'
spec = importlib.util.spec_from_file_location('compact_diff', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class CompactDiffTests(unittest.TestCase):
    # test_main_preserves_clean_empty_diff は成功した空差分だけをnoneとして出力する。
    def test_main_preserves_clean_empty_diff(self):
        with patch.object(module, 'run_git', side_effect=[
            (True, 'true', ''), (True, '', ''), (True, '', ''),
            (True, '', ''), (True, '', ''),
        ]), patch.object(sys, 'argv', ['compact-diff']), contextlib.redirect_stdout(io.StringIO()) as output:
            module.main()
        self.assertEqual(module.json.loads(output.getvalue())['status'], 'ok')

    # test_main_returns_distinct_failures はGit環境・repository・query failureをexit 2にする。
    def test_main_returns_distinct_failures(self):
        cases = [
            ('git_unavailable', [(False, '', 'git_unavailable')]),
            ('git_unavailable_or_not_repository', [(False, '', 'git_query_failed')]),
            ('git_query_failed', [
                (True, 'true', ''), (True, '', ''), (False, '', 'git_query_failed'),
                (True, '', ''), (True, '', ''),
            ]),
        ]
        for expected, results in cases:
            with self.subTest(status=expected):
                output = io.StringIO()
                with patch.object(module, 'run_git', side_effect=results), \
                        patch.object(sys, 'argv', ['compact-diff']), \
                        contextlib.redirect_stdout(output), self.assertRaises(SystemExit) as raised:
                    module.main()
                self.assertEqual(raised.exception.code, 2)
                self.assertEqual(module.json.loads(output.getvalue())['status'], expected)


if __name__ == '__main__':
    unittest.main()
