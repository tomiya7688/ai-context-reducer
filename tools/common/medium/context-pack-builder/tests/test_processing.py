import sys
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[1] / 'script'
sys.path.insert(0, str(SCRIPT_DIR))

from commander import build_context_pack
from processing import render_context_pack


class RenderContextPackTests(unittest.TestCase):
    def test_clean_state_is_not_reported_as_unavailable(self):
        text = render_context_pack(
            {'goal': 'g', 'required': '', 'acceptance': '', 'deferred': ''},
            {
                'changed': [],
                'status': [],
                'changed_query_ok': True,
                'status_query_ok': True,
                'changed_error_kind': None,
                'status_error_kind': None,
                'changed_truncated': False,
                'status_truncated': False,
            },
        )

        self.assertIn('none detected', text)
        self.assertIn('clean', text)
        self.assertNotIn('Git unavailable', text)

    def test_git_unavailable_is_explicit(self):
        text = render_context_pack(
            {'goal': 'g', 'required': '', 'acceptance': '', 'deferred': ''},
            {
                'changed': [],
                'status': [],
                'changed_query_ok': False,
                'status_query_ok': False,
                'changed_error_kind': 'git_unavailable',
                'status_error_kind': 'git_unavailable',
                'changed_truncated': False,
                'status_truncated': False,
            },
        )

        self.assertIn('Git unavailable', text)
        self.assertNotIn('- clean', text)
        self.assertNotIn('none detected', text)

    def test_git_query_failure_is_not_clean_state(self):
        text = render_context_pack(
            {'goal': 'g', 'required': '', 'acceptance': '', 'deferred': ''},
            {
                'changed': [],
                'status': [],
                'changed_query_ok': False,
                'status_query_ok': False,
                'changed_error_kind': 'git_query_failed',
                'status_error_kind': 'git_query_failed',
                'changed_truncated': False,
                'status_truncated': False,
            },
        )

        self.assertIn('git diff query failed', text)
        self.assertIn('git status query failed', text)
        self.assertNotIn('- clean', text)

    def test_truncation_is_explicit(self):
        text = render_context_pack(
            {'goal': 'g', 'required': '', 'acceptance': '', 'deferred': ''},
            {
                'changed': ['a.py'],
                'status': ['M a.py'],
                'changed_query_ok': True,
                'status_query_ok': True,
                'changed_error_kind': None,
                'status_error_kind': None,
                'changed_truncated': True,
                'status_truncated': True,
            },
        )

        self.assertGreaterEqual(text.count('truncated'), 2)

    def test_negative_limit_is_normalized_to_zero(self):
        class FakeResult(dict):
            pass

        import commander
        original = commander.git_lines
        try:
            commander.git_lines = lambda root, args: FakeResult(ok=True, lines=['a.py'], error_kind=None)
            text = build_context_pack(Path('.'), {'goal': 'g', 'required': '', 'acceptance': '', 'deferred': ''}, -1)
        finally:
            commander.git_lines = original

        self.assertNotIn('  - a.py\n', text)
        self.assertGreaterEqual(text.count('truncated'), 2)


if __name__ == '__main__':
    unittest.main()
