from __future__ import annotations

import importlib.util
import unittest
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / 'script' / 'repo_stats.py'
spec = importlib.util.spec_from_file_location('repo_stats', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)



# {責務: [RepoStatsTests: 依存先の除外、集計値、読み込み上限を確認する], フィールド: [root: 検査専用の一時作業先], 処理: [1: 固定入力の結果を期待値と照合する]}
class RepoStatsTests(unittest.TestCase):
    # {責務: [setUp: 各テストで独立した入力を作れる場所を用意する], 処理: [1: 一時作業先を作り終了時の削除を予約する], 引数: [], 戻り値: []}
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    # {責務: [test_portable_stats_are_self_describing_and_prune_dependencies: 依存ファイルを除外した言語別の件数と行数を確認する], 処理: [1: 固定入力を用意する, 2: 出力を明示した期待値と照合する], 引数: [], 戻り値: []}
    def test_portable_stats_are_self_describing_and_prune_dependencies(self):
        tmp_path = self.root
        (tmp_path / 'src').mkdir()
        (tmp_path / 'src' / 'main.py').write_text('a = 1\nprint(a)\n', encoding='utf-8', newline='\n')
        (tmp_path / 'node_modules').mkdir()
        (tmp_path / 'node_modules' / 'ignored.py').write_text('print(2)\n', encoding='utf-8')

        result = module.build_stats(tmp_path, 0, 'portable')

        assert result['tool'] == 'repo-stats'
        assert result['status'] == 'ok'
        assert result['backend'] == 'portable'
        assert result['recognized_files_seen'] == 1
        assert result['analyzed_file_count'] == 1
        assert result['analyzed_line_count'] == 2
        assert result['languages']['Python'] == {
            'file_count': 1,
            'line_count': 2,
            'byte_count': len('a = 1\nprint(a)\n'.encode()),
            'code_count': None,
            'comment_count': None,
            'blank_count': None,
            'complexity': None,
        }

    # {責務: [test_explicit_file_size_cap_is_visible: 大きさの上限で読まなかったファイルを明示することを確認する], 処理: [1: 固定入力を用意する, 2: 出力を明示した期待値と照合する], 引数: [], 戻り値: []}
    def test_explicit_file_size_cap_is_visible(self):
        tmp_path = self.root
        (tmp_path / 'big.py').write_text('1234567890\n', encoding='utf-8')
        result = module.build_stats(tmp_path, 3, 'portable')
        assert result['recognized_files_seen'] == 1
        assert result['analyzed_file_count'] == 0
        assert result['oversized_file_count'] == 1
        assert result['max_file_bytes'] == 3

    # {責務: [test_parse_scc_stats_compacts_language_summary: sccの出力から言語別の集計だけを残すことを確認する], 処理: [1: 固定入力を用意する, 2: 出力を明示した期待値と照合する], 引数: [], 戻り値: []}
    def test_parse_scc_stats_compacts_language_summary(self):
        parsed = module.parse_scc_stats([
            {
                'Name': 'Go', 'Count': 2, 'Lines': 100, 'Bytes': 5000,
                'Code': 70, 'Comment': 20, 'Blank': 10, 'Complexity': 9,
                'Files': [{'Location': 'do-not-forward.go'}],
            },
            {
                'Name': 'Python', 'Count': 1, 'Lines': 20, 'Bytes': 800,
                'Code': 15, 'Comment': 2, 'Blank': 3, 'Complexity': 1,
            },
        ])
        assert parsed['recognized_files_seen'] == 3
        assert parsed['analyzed_line_count'] == 120
        assert parsed['languages'] == {
            'Go': {
                'file_count': 2, 'line_count': 100, 'byte_count': 5000,
                'code_count': 70, 'comment_count': 20, 'blank_count': 10, 'complexity': 9,
            },
            'Python': {
                'file_count': 1, 'line_count': 20, 'byte_count': 800,
                'code_count': 15, 'comment_count': 2, 'blank_count': 3, 'complexity': 1,
            },
        }


if __name__ == '__main__':
    unittest.main()
