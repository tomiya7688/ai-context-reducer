import importlib.util
import unittest
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / 'script' / 'repo_profile.py'
spec = importlib.util.spec_from_file_location('repo_profile', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)



# {責務: [RepoProfileTests: 言語別の件数と集計の省略を確認する], フィールド: [root: 検査専用の一時作業先], 処理: [1: 固定入力の結果を期待値と照合する]}
class RepoProfileTests(unittest.TestCase):
    # {責務: [setUp: 各テストで独立した入力を作れる場所を用意する], 処理: [1: 一時作業先を作り終了時の削除を予約する], 引数: [], 戻り値: []}
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    # {責務: [test_build_profile_separates_language_and_other_files: ソースと説明文書の件数を分けて集計することを確認する], 処理: [1: 固定入力を用意する, 2: 出力を明示した期待値と照合する], 引数: [], 戻り値: []}
    def test_build_profile_separates_language_and_other_files(self):
        tmp_path = self.root
        (tmp_path / 'main.py').write_text('print(1)\n', encoding='utf-8')
        (tmp_path / 'README.md').write_text('# Demo\n', encoding='utf-8')
        result = module.build_profile(tmp_path, 0)
        assert result['tool'] == 'repo-profile'
        assert result['status'] == 'ok'
        assert result['backend'] == 'portable'
        assert result['files_scanned'] == 2
        assert result['language_file_counts'] == {'Python': 1}
        assert result['recognized_source_files_scanned'] == 1
        assert result['non_language_files_scanned'] == 1
        assert result['scan_truncated'] is False
        assert result['language_metrics'][0]['lines'] is None

    # {責務: [test_build_profile_marks_only_real_truncation_unknown: 未集計の候補が残る場合だけ集計不足を示すことを確認する], 処理: [1: 固定入力を用意する, 2: 出力を明示した期待値と照合する], 引数: [], 戻り値: []}
    def test_build_profile_marks_only_real_truncation_unknown(self):
        tmp_path = self.root
        (tmp_path / 'a.py').write_text('', encoding='utf-8')
        exact = module.build_profile(tmp_path, 1)
        assert exact['scan_truncated'] is False
        assert exact['project_size_class'] == 'small'

        (tmp_path / 'b.py').write_text('', encoding='utf-8')
        truncated = module.build_profile(tmp_path, 1)
        assert truncated['scan_truncated'] is True
        assert truncated['project_size_class'] == 'large_or_unknown_due_to_scan_limit'

    # {責務: [test_parse_scc_payload_keeps_compact_language_metrics: sccの出力からファイルごとの詳細を除き言語別指標を残すことを確認する], 処理: [1: 固定入力を用意する, 2: 出力を明示した期待値と照合する], 引数: [], 戻り値: []}
    def test_parse_scc_payload_keeps_compact_language_metrics(self):
        counts, metrics = module.parse_scc_payload([
            {
                'Name': 'Go',
                'Count': 3,
                'Lines': 120,
                'Code': 90,
                'Comment': 20,
                'Blank': 10,
                'Complexity': 7,
                'Files': [{'Location': 'should-not-be-forwarded.go'}],
            },
            {
                'Name': 'Python',
                'Count': 1,
                'Lines': 30,
                'Code': 20,
                'Comment': 5,
                'Blank': 5,
                'Complexity': 2,
            },
        ])
        assert counts == {'Go': 3, 'Python': 1}
        assert metrics == [
            {'language': 'Go', 'files': 3, 'lines': 120, 'code': 90, 'comment': 20, 'blank': 10, 'complexity': 7},
            {'language': 'Python', 'files': 1, 'lines': 30, 'code': 20, 'comment': 5, 'blank': 5, 'complexity': 2},
        ]


if __name__ == '__main__':
    unittest.main()
