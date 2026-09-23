import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / 'script' / 'source_of_truth_candidates.py'
spec = importlib.util.spec_from_file_location('source_of_truth_candidates', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class SourceOfTruthCandidatesTests(unittest.TestCase):
    # 0指定が候補数を切り捨てず、scan件数も正しく返すことを検証する。
    def test_zero_limit_means_unlimited(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'architecture.md').write_text('a', encoding='utf-8')
            (root / 'design.md').write_text('b', encoding='utf-8')
            candidates, truncated, scanned = module.candidate_paths(root, 0)
            self.assertEqual(candidates['architecture'], ['architecture.md', 'design.md'])
            self.assertFalse(truncated['architecture'])
            self.assertEqual(2, scanned)


if __name__ == '__main__':
    unittest.main()
