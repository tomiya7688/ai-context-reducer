import sys
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[1] / 'script'
sys.path.insert(0, str(SCRIPT_DIR))

from processing import normalized_stem, route_candidates


class ChangeRouterProcessingTests(unittest.TestCase):
    def test_test_name_normalization(self):
        self.assertEqual(normalized_stem('tests/test_widget.py'), 'widget')
        self.assertEqual(normalized_stem('widget_test.go'), 'widget')

    def test_route_fields_are_self_describing(self):
        index = [
            {'path': 'tests/test_widget.py', 'name': 'test_widget.py', 'is_test': True, 'is_doc': False},
            {'path': 'docs/widget.md', 'name': 'widget.md', 'is_test': False, 'is_doc': True},
        ]
        result = route_candidates('src/widget.py', index, 8)

        self.assertEqual(result['changed_file'], 'src/widget.py')
        self.assertEqual(result['candidate_tests'], ['tests/test_widget.py'])
        self.assertEqual(result['candidate_docs'], ['docs/widget.md'])
        self.assertNotIn('changed', result)
        self.assertNotIn('tests', result)
        self.assertNotIn('docs', result)


if __name__ == '__main__':
    unittest.main()
