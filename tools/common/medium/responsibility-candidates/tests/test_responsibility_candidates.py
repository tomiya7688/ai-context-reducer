import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / 'script' / 'responsibility_candidates.py'
spec = importlib.util.spec_from_file_location('responsibility_candidates', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ResponsibilityCandidatesTests(unittest.TestCase):
    def test_exact_scan_cap_is_not_truncated(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'a.py').write_text('', encoding='utf-8')
            (root / 'b.go').write_text('', encoding='utf-8')
            rows, scanned, truncated, stat_errors, walk_errors = module.scan_candidates(root, 2)
            self.assertEqual(2, len(rows))
            self.assertEqual(2, scanned)
            self.assertFalse(truncated)
            self.assertEqual(0, stat_errors)
            self.assertEqual(0, walk_errors)

    def test_additional_code_file_marks_explicit_scan_truncation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'a.py').write_text('', encoding='utf-8')
            (root / 'b.go').write_text('', encoding='utf-8')
            rows, scanned, truncated, _, _ = module.scan_candidates(root, 1)
            self.assertEqual(1, len(rows))
            self.assertEqual(1, scanned)
            self.assertTrue(truncated)

    def test_default_scan_is_unlimited(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for index in range(3):
                (root / f'f{index}.py').write_text('', encoding='utf-8')
            rows, scanned, truncated, _, _ = module.scan_candidates(root, 0)
            self.assertEqual(3, len(rows))
            self.assertEqual(3, scanned)
            self.assertFalse(truncated)


if __name__ == '__main__':
    unittest.main()
