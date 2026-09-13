import sys
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[1] / 'script'
sys.path.insert(0, str(SCRIPT_DIR))

from processing import render_context_pack


class RenderContextPackTests(unittest.TestCase):
    def test_clean_state_is_not_reported_as_unavailable(self):
        text = render_context_pack(
            {'goal': 'g', 'required': '', 'acceptance': '', 'deferred': ''},
            {
                'changed': [],
                'status': [],
                'changed_truncated': False,
                'status_truncated': False,
                'git_available': True,
            },
        )

        self.assertIn('none detected', text)
        self.assertIn('clean', text)
        self.assertNotIn('Git unavailable', text)

    def test_git_failure_is_explicit(self):
        text = render_context_pack(
            {'goal': 'g', 'required': '', 'acceptance': '', 'deferred': ''},
            {
                'changed': [],
                'status': [],
                'changed_truncated': False,
                'status_truncated': False,
                'git_available': False,
            },
        )

        self.assertIn('Git unavailable', text)

    def test_truncation_is_explicit(self):
        text = render_context_pack(
            {'goal': 'g', 'required': '', 'acceptance': '', 'deferred': ''},
            {
                'changed': ['a.py'],
                'status': ['M a.py'],
                'changed_truncated': True,
                'status_truncated': True,
                'git_available': True,
            },
        )

        self.assertGreaterEqual(text.count('truncated'), 2)


if __name__ == '__main__':
    unittest.main()
