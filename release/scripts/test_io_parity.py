"""入出力比較器が誤った応答・入力改変・不正な検査定義を拒否するか確認する。"""

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from io_parity import project_expected, relative_path, run_suite, validate_suite


# {責務: [IOParityTests: 比較器自体の見逃しを固定入力で検出する], フィールド: [suite: 最小の検査定義, inventory: 対応する公開入口], 処理: [1: 正常応答を実行する, 2: 失敗する応答と定義を照合する]}
class IOParityTests(unittest.TestCase):
    # {責務: [setUp: 実装出力に依存しない小さい契約を用意する], 処理: [1: 明示した入口と期待値を組み立てる], 引数: [], 戻り値: []}
    def setUp(self):
        self.suite = {"schema_version": 1, "python_entry": "tools/example.py", "go_entry": "tools/main.go",
                      "command": "stats", "fixtures": {"empty": {}}, "cases": [
                          {"id": "empty", "fixture": "empty", "root": ".", "args": [],
                           "exit_code": 0, "stderr": "", "json": {"tool": "repo-stats", "status": "ok"}}]}
        self.inventory = {"python": ["tools/example.py"], "go": {"tools/main.go": ["stats"]}}

    # {責務: [command: 制御した応答を返す子プロセスの引数を作る], 処理: [1: 正しい応答を基本に追加処理を接続する], 引数: [extra: 応答後に実行する処理], 戻り値: [1: 起動引数]}
    def command(self, extra=""):
        source = ("import json,sys; from pathlib import Path; "
                  "print(json.dumps({'tool':'repo-stats','status':'ok','project_root':sys.argv[-1]})); " + extra)
        return [sys.executable, "-c", source]

    # {責務: [test_real_fixture_is_registered: 配布用定義の全事例と公開入口の対応を確認する], 処理: [1: 実際の定義を読む, 2: 六事例が登録済み入口を指すことを検証する], 引数: [], 戻り値: []}
    def test_real_fixture_is_registered(self):
        repo = Path(__file__).resolve().parents[2]
        suite = json.loads((repo / "release/fixtures/repo-stats.json").read_text(encoding="utf-8"))
        inventory = json.loads((repo / "release/ENTRYPOINTS.json").read_text(encoding="utf-8"))
        validate_suite(suite, inventory)
        self.assertEqual(6, len(suite["cases"]))

    # {責務: [test_success_and_empty_routes: 正常な二経路の実行数と経路なしの拒否を確認する], 処理: [1: 二つの子プロセスを比較する, 2: 未実行を成功にしない], 引数: [], 戻り値: []}
    def test_success_and_empty_routes(self):
        self.assertEqual(2, run_suite(self.suite, {"first": self.command(), "second": self.command()}))
        with self.assertRaises(ValueError):
            run_suite(self.suite, {})

    # {責務: [test_work_directory_is_canonical_before_launch: 一時先の別表記を入力先の違いと誤認しない], 処理: [1: 同じ一時先を指す別表記を用意する, 2: 子プロセスへ実体の絶対位置が渡ることを確認する], 引数: [], 戻り値: []}
    def test_work_directory_is_canonical_before_launch(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "actual"
            target.mkdir()
            alias = str(target / ".." / "actual")
            with patch("io_parity.tempfile.TemporaryDirectory") as directory:
                directory.return_value.__enter__.return_value = alias
                self.assertEqual(1, run_suite(self.suite, {"canonical": self.command()}))

    # {責務: [test_wrong_exit_stderr_json_and_root_fail: 各応答項目の違いを検出する], 処理: [1: 制御した不正応答を順に返す, 2: 正常として通らないことを確認する], 引数: [], 戻り値: []}
    def test_wrong_exit_stderr_json_and_root_fail(self):
        commands = [
            self.command("sys.exit(2)"), self.command("sys.stderr.write('unexpected')"),
            [sys.executable, "-c", "print('not JSON')"],
            [sys.executable, "-c", "print('{}')"],
            [sys.executable, "-c", "print('[]')"],
            [sys.executable, "-c", "print('{\"status\":\"ok\",\"status\":\"ok\"}')"],
        ]
        for command in commands:
            with self.subTest(command=command), self.assertRaises(ValueError):
                run_suite(self.suite, {"broken": command})

    # {責務: [test_input_changes_and_timeouts_fail: 書き換えと応答停止を拒否する], 処理: [1: 子プロセスに入力先へ追加させる, 2: 時間切れを模擬して失敗を確かめる], 引数: [], 戻り値: []}
    def test_input_changes_and_timeouts_fail(self):
        with self.assertRaises(RuntimeError):
            run_suite(self.suite, {"writer": self.command("Path('project/unexpected').write_text('changed')")})
        with patch("io_parity.subprocess.run", side_effect=subprocess.TimeoutExpired("fixture", 30)):
            with self.assertRaises(subprocess.TimeoutExpired):
                run_suite(self.suite, {"timeout": self.command()})

    # {責務: [test_expected_fields_and_types_are_strict: 欠落・型違い・値違い・空集計の違いを検出する], 処理: [1: 正しい部分比較を確認する, 2: 誤った値を順に拒否する], 引数: [], 戻り値: []}
    def test_expected_fields_and_types_are_strict(self):
        self.assertEqual({"n": 1}, project_expected({"n": 1, "other": 2}, {"n": 1}))
        for actual, expected in [({}, {"n": 1}), ({"n": True}, {"n": 1}),
                                 ({"n": 2}, {"n": 1}), ({"languages": {"Python": {}}}, {"languages": {}})]:
            with self.subTest(actual=actual), self.assertRaises(ValueError):
                project_expected(actual, expected)

    # {責務: [test_unsafe_paths_and_incomplete_suites_fail: 作業先外への保存と未登録入口と空の定義を拒否する], 処理: [1: 不正な位置を検査する, 2: 期待値や入口の対応を壊して検査する], 引数: [], 戻り値: []}
    def test_unsafe_paths_and_incomplete_suites_fail(self):
        for name in ("../escape", "/absolute", "C:/outside", "nested\\file", ".", "a/../b", "a//b"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                relative_path(name)
        variations = [
            {"cases": []}, {"python_entry": "tools/unregistered.py"}, {"command": "unknown"},
            {"cases": self.suite["cases"] * 2}, {"fixtures": {"empty": {"../escape": "bad"}}},
            {"schema_version": True},
        ]
        for variation in variations:
            suite = copy.deepcopy(self.suite)
            suite.update(variation)
            with self.subTest(variation=variation), self.assertRaises(ValueError):
                validate_suite(suite, self.inventory)
        for key, value in [("exit_code", True), ("json", {}), ("stderr", None), ("root", "../escape")]:
            suite = copy.deepcopy(self.suite)
            suite["cases"][0][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                validate_suite(suite, self.inventory)


if __name__ == "__main__":
    unittest.main()
