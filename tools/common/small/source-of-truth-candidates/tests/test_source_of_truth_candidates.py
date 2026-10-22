import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / 'script' / 'source_of_truth_candidates.py'
spec = importlib.util.spec_from_file_location('source_of_truth_candidates', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


# {責務: [SourceOfTruthCandidatesTests: 設計や仕様の保存先候補の分類と省略を検査する], フィールド: [root: 一時作業先], 処理: [1: 検査用文書を作る, 2: 分類と件数を照合する]}
class SourceOfTruthCandidatesTests(unittest.TestCase):
    # {責務: [setUp: 他のテストと混ざらない文書の保存先を作る], 処理: [1: 一時作業先を作り終了時の削除を予約する], 引数: [], 戻り値: []}
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    # {責務: [test_candidate_paths_group_by_role: 設計と仕様の候補を別々に返すことを確認する], 処理: [1: 二種類の文書を作る, 2: 分類と省略なしを照合する], 引数: [], 戻り値: []}
    def test_candidate_paths_group_by_role(self):
        (self.root / 'architecture.md').write_text('# A\n', encoding='utf-8')
        (self.root / 'specification.md').write_text('# S\n', encoding='utf-8')
        candidates, truncated, scanned = module.candidate_paths(self.root, 10)
        self.assertEqual(['architecture.md'], candidates['architecture'])
        self.assertEqual(['specification.md'], candidates['specification'])
        self.assertIs(False, truncated['architecture'])
        self.assertEqual(2, scanned)

    # {責務: [test_candidate_paths_report_role_truncation: 上限による候補の省略を分類ごとに返すことを確認する], 処理: [1: 上限より多い文書を作る, 2: 件数と省略ありを照合する], 引数: [], 戻り値: []}
    def test_candidate_paths_report_role_truncation(self):
        (self.root / 'architecture-a.md').write_text('', encoding='utf-8')
        (self.root / 'architecture-b.md').write_text('', encoding='utf-8')
        candidates, truncated, scanned = module.candidate_paths(self.root, 1)
        self.assertEqual(1, len(candidates['architecture']))
        self.assertIs(True, truncated['architecture'])
        self.assertEqual(2, scanned)


if __name__ == '__main__':
    unittest.main()
