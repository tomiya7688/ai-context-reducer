import importlib.util
from pathlib import Path
import unittest

MODULE = Path(__file__).parents[1] / 'script' / 'compact_log.py'
spec = importlib.util.spec_from_file_location('compact_log', MODULE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class CompactLogTests(unittest.TestCase):
    def test_findings_and_tail_are_bounded(self):
        result = mod.compact_log('ok\nwarning one\nerror two\nlast', max_findings=1, tail=2)
        self.assertEqual(4, result['line_count'])
        self.assertEqual(2, result['finding_count'])
        self.assertTrue(result['findings_truncated'])
        self.assertEqual(1, len(result['findings']))
        self.assertEqual([3, 4], [row['line'] for row in result['tail']])


if __name__ == '__main__':
    unittest.main()
