"""公開入口の未割り当てと、実行されない事例の登録を検出する。"""

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from io_coverage import TOOLBOX, execute_suites, load_coverage, load_json, public_surfaces


# {責務: [CoverageTests: 既知の残件を増減させたときの検出を確認する], フィールド: [repo: 検査用リポジトリ, inventory: 公開入口, suite: 実行事例, pending: 既知の残件], 処理: [1: 小さい登録を用意する, 2: 誤った追加・削除を照合する]}
class CoverageTests(unittest.TestCase):
    # {責務: [setUp: 2入口へ1事例を割り当てた固定入力を作る], 処理: [1: 一時先を作る, 2: 明示した公開入口と残件を保存する], 引数: [], 戻り値: []}
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.repo = Path(temporary.name).resolve()
        self.inventory = {
            "python": ["tools/stats.py", "tools/next.py"],
            "shell": ["tools/run.sh"],
            "go": {TOOLBOX: ["stats", "next"]},
        }
        self.suite = {
            "schema_version": 1,
            "python_entry": "tools/stats.py",
            "go_entry": TOOLBOX,
            "command": "stats",
            "fixtures": {"empty": {}},
            "cases": [
                {
                    "id": "empty",
                    "fixture": "empty",
                    "root": ".",
                    "args": [],
                    "exit_code": 0,
                    "stderr": "",
                    "json": {"status": "ok"},
                }
            ],
        }
        self.pending = [
            "python:tools/next.py",
            "shell:tools/run.sh",
            f"go:{TOOLBOX}",
            f"go-command:{TOOLBOX}:next",
        ]
        self.save()

    # {責務: [write: 検査定義を所定の相対位置へ保存する], 処理: [1: 親を作る, 2: JSONとして保存する], 引数: [name: 相対位置, value: 定義], 戻り値: []}
    def write(self, name, value):
        path = self.repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value), encoding="utf-8")

    # {責務: [save: 公開入口と既知の残件と最初の事例を保存する], 処理: [1: 三つの定義を保存する], 引数: [], 戻り値: []}
    def save(self):
        self.write("release/ENTRYPOINTS.json", self.inventory)
        self.write(
            "release/IO_PENDING.json", {"schema_version": 1, "issue": 33, "pending": self.pending}
        )
        self.write("release/fixtures/stats.json", self.suite)

    # {責務: [test_partial_assignment_is_not_complete_or_executed: 登録を実行済みや全体合格と誤表示しない], 処理: [1: 明示した6公開面を照合する, 2: 2割当と4残件を確認する], 引数: [], 戻り値: []}
    def test_partial_assignment_is_not_complete_or_executed(self):
        report, suites = load_coverage(self.repo)
        self.assertEqual(
            ("partial", 6, 2, 4, 1),
            (
                report["coverage"],
                report["public_surfaces"],
                report["assigned_surfaces"],
                report["pending_surfaces"],
                report["case_count"],
            ),
        )
        self.assertEqual(["release/fixtures/stats.json"], report["suite_files"])
        self.assertEqual(1, len(suites))

    # {責務: [test_new_entrypoint_or_alias_cannot_hide_in_old_pending: 新しい未割り当てを既知の残件で隠せないことを確認する], 処理: [1: 公開入口と別名を順に増やす, 2: 未割り当てとして拒否する], 引数: [], 戻り値: []}
    def test_new_entrypoint_or_alias_cannot_hide_in_old_pending(self):
        for field in ("python", "go"):
            inventory = copy.deepcopy(self.inventory)
            if field == "python":
                inventory[field].append("tools/new.py")
            else:
                inventory[field][TOOLBOX].append("alias")
            self.write("release/ENTRYPOINTS.json", inventory)
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "unassigned"):
                load_coverage(self.repo)

    # {責務: [test_stale_duplicate_and_already_assigned_pending_fail: 削除済みや検査済みの入口を残件に残せないことを確認する], 処理: [1: 三種類の不正な残件を保存する, 2: それぞれを拒否する], 引数: [], 戻り値: []}
    def test_stale_duplicate_and_already_assigned_pending_fail(self):
        for additions in (
            ["python:tools/deleted.py"],
            [self.pending[0]],
            ["python:tools/stats.py"],
        ):
            self.write(
                "release/IO_PENDING.json",
                {"schema_version": 1, "issue": 33, "pending": self.pending + additions},
            )
            with self.subTest(additions=additions), self.assertRaises(ValueError):
                load_coverage(self.repo)

    # {責務: [test_all_suite_files_are_counted_and_executed: 新しく登録した事例がCIの実行対象から漏れないことを確認する], 処理: [1: 別入口の事例を追加する, 2: 古い残件を除く, 3: 二事例が比較器へ渡ることを確認する], 引数: [], 戻り値: []}
    def test_all_suite_files_are_counted_and_executed(self):
        second = copy.deepcopy(self.suite)
        second.update(python_entry="tools/next.py", command="next")
        self.write("release/fixtures/next.json", second)
        with self.assertRaisesRegex(ValueError, "already_assigned"):
            load_coverage(self.repo)
        self.pending = ["shell:tools/run.sh"]
        self.save()
        report, suites = load_coverage(self.repo)
        self.assertEqual(
            (5, 1, 2),
            (report["assigned_surfaces"], report["pending_surfaces"], report["case_count"]),
        )
        with patch("io_coverage.run_suite", return_value=2) as run:
            self.assertEqual(4, execute_suites(self.repo, suites, True, self.repo / "acr-toolbox"))
        self.assertEqual(2, run.call_count)
        self.assertEqual(
            {
                ("next", (sys.executable, str(self.repo / "tools/next.py"))),
                ("stats", (sys.executable, str(self.repo / "tools/stats.py"))),
            },
            {
                (call.args[0]["command"], tuple(call.args[1]["python"]))
                for call in run.call_args_list
            },
        )
        self.assertEqual(
            {"next", "stats"}, {call.args[1]["binary"][1] for call in run.call_args_list}
        )

    # {責務: [test_multiple_suites_for_one_surface_are_all_executed: 同じ入口の追加事例で被覆件数を水増しせず全事例を実行する], 処理: [1: 別名の定義を追加する, 2: 割り当て件数と実行件数を分けて確認する], 引数: [], 戻り値: []}
    def test_multiple_suites_for_one_surface_are_all_executed(self):
        second = copy.deepcopy(self.suite)
        second["cases"].append(dict(second["cases"][0], id="another-empty"))
        self.write("release/fixtures/stats-more.json", second)
        report, suites = load_coverage(self.repo)
        self.assertEqual(2, report["assigned_surfaces"])
        self.assertEqual(3, report["case_count"])
        with patch("io_coverage.run_suite", return_value=1) as run:
            self.assertEqual(2, execute_suites(self.repo, suites, python=True))
        self.assertEqual(2, run.call_count)

    # {責務: [test_python_entry_link_is_rejected_before_execution: 登録された入口からリポジトリ外を実行しない], 処理: [1: 入口をリンクと模擬する, 2: 比較器を呼ぶ前に拒否する], 引数: [], 戻り値: []}
    def test_python_entry_link_is_rejected_before_execution(self):
        with patch.object(Path, "is_symlink", return_value=True):
            with patch("io_coverage.run_suite") as run:
                with self.assertRaisesRegex(ValueError, "Python entry"):
                    execute_suites(self.repo, [("stats", self.suite)], python=True)
                run.assert_not_called()

    # {責務: [test_later_outside_entry_blocks_all_execution: 後続の不正な入口も全事例の実行前に拒否する], 処理: [1: 正常と外部入口の順で渡す, 2: 比較器が一度も呼ばれないことを確認する], 引数: [], 戻り値: []}
    def test_later_outside_entry_blocks_all_execution(self):
        for outside in ("../outside.py", str(self.repo.parent / "outside.py")):
            second = dict(self.suite, python_entry=outside)
            with self.subTest(outside=outside), patch("io_coverage.run_suite") as run:
                with self.assertRaisesRegex(ValueError, "Python entry"):
                    execute_suites(
                        self.repo, [("stats", self.suite), ("outside", second)], python=True
                    )
                run.assert_not_called()

    # {責務: [test_cli_execution_modes_and_diagnostics: CLIの実行経路と失敗時の残件を正しく報告する], 処理: [1: 小さい実入口を用意する, 2: 引数不足と厳密な拒否を確認する, 3: 許可付きで実行する], 引数: [], 戻り値: []}
    def test_cli_execution_modes_and_diagnostics(self):
        entry = self.repo / "tools/stats.py"
        entry.parent.mkdir(parents=True)
        entry.write_text(
            "import json, sys\nfrom pathlib import Path\n"
            'print(json.dumps({"status": "ok", "project_root": str(Path(sys.argv[-1]).resolve())}))\n',
            encoding="utf-8",
        )
        script = Path(__file__).with_name("io_coverage.py")
        for flags, code in (
            (["--run"], 2),
            (["--python"], 2),
            (["--run", "--python"], 1),
            (["--allow-pending", "--run", "--python"], 0),
        ):
            with self.subTest(flags=flags):
                result = subprocess.run(
                    [sys.executable, str(script), "--repo", str(self.repo), *flags],
                    capture_output=True,
                    text=True,
                    check=False,
                    timeout=30,
                )
                self.assertEqual(code, result.returncode, result.stderr)
                if code == 2:
                    self.assertIn("must be supplied together", result.stderr)
                    continue
                report = json.loads(result.stdout)
                if code == 1:
                    self.assertEqual(0, report["executions"])
                    self.assertEqual([], report["executed_routes"])
                    self.assertEqual(sorted(self.pending), report["pending"])
                else:
                    self.assertEqual(1, report["executions"])
                    self.assertEqual(["python"], report["executed_routes"])
                    self.assertNotIn("pending", report)

    # {責務: [test_empty_invalid_and_unsupported_suites_fail: 実行できない事例を登録件数に数えない], 処理: [1: 事例を不正にする, 2: 空の定義一覧も拒否する], 引数: [], 戻り値: []}
    def test_empty_invalid_and_unsupported_suites_fail(self):
        for cases in ([], [self.suite["cases"][0]] * 2):
            suite = copy.deepcopy(self.suite)
            suite["cases"] = cases
            self.write("release/fixtures/stats.json", suite)
            with self.subTest(cases=cases), self.assertRaises(ValueError):
                load_coverage(self.repo)
        self.save()
        self.write("release/fixtures/extra.json", {"invalid": True})
        with self.assertRaises(ValueError):
            load_coverage(self.repo)
        (self.repo / "release/fixtures/extra.json").unlink()
        (self.repo / "release/fixtures/stats.json").unlink()
        with self.assertRaisesRegex(ValueError, "no I/O suites"):
            load_coverage(self.repo)

    # {責務: [test_linked_definitions_fail_without_reading: 定義のリンクから別の保存先を読ませない], 処理: [1: 残件定義をリンクと模擬する, 2: 読み取り前に拒否する], 引数: [], 戻り値: []}
    def test_linked_definitions_fail_without_reading(self):
        original = Path.is_symlink
        with patch.object(
            Path, "is_symlink", lambda path: path.name == "IO_PENDING.json" or original(path)
        ):
            with self.assertRaisesRegex(ValueError, "symlink"):
                load_coverage(self.repo)

    # {責務: [test_strict_cli_blocks_pending_and_complete_cli_passes: 段階的CIと公開前の終了コードを区別する], 処理: [1: 残件ありの厳密・許可付き実行を比較する, 2: 全割り当て後の成功を確認する], 引数: [], 戻り値: []}
    def test_strict_cli_blocks_pending_and_complete_cli_passes(self):
        script = Path(__file__).with_name("io_coverage.py")
        for flags, code in (([], 1), (["--allow-pending"], 0)):
            result = subprocess.run(
                [sys.executable, str(script), "--repo", str(self.repo), *flags],
                capture_output=True,
                text=True,
                check=False,
                timeout=30,
            )
            self.assertEqual(code, result.returncode, result.stderr)
            self.assertEqual(0, json.loads(result.stdout)["executions"])
        self.inventory = {"python": ["tools/stats.py"], "shell": [], "go": {TOOLBOX: ["stats"]}}
        self.pending = []
        self.save()
        report, _ = load_coverage(self.repo)
        self.assertEqual(
            ("complete", 3, 0),
            (report["coverage"], report["assigned_surfaces"], report["pending_surfaces"]),
        )
        result = subprocess.run(
            [sys.executable, str(script), "--repo", str(self.repo)],
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
        self.assertEqual(0, result.returncode, result.stderr)

    # {責務: [test_schema_and_missing_execution_routes_fail: 曖昧な残件と未実行を拒否する], 処理: [1: 真偽値の版番号を拒否する, 2: 経路を指定しない実行を拒否する], 引数: [], 戻り値: []}
    def test_schema_and_missing_execution_routes_fail(self):
        self.write(
            "release/IO_PENDING.json",
            {"schema_version": True, "issue": 33, "pending": self.pending},
        )
        with self.assertRaises(ValueError):
            load_coverage(self.repo)
        with self.assertRaises(ValueError):
            execute_suites(self.repo, [("stats", self.suite)])

    # {責務: [test_unsupported_binary_route_fails: 未対応の単独入口をtoolboxで検査済みにしない], 処理: [1: 登録上は存在する別入口を用意する, 2: 起動経路の不一致を拒否する], 引数: [], 戻り値: []}
    def test_unsupported_binary_route_fails(self):
        path = "tools/standalone/main.go"
        self.inventory["go"][path] = ["stats"]
        self.suite["go_entry"] = path
        self.save()
        with self.assertRaisesRegex(ValueError, "unsupported binary execution route"):
            load_coverage(self.repo)

    # {責務: [test_outside_definition_is_not_read: 別の保存先の定義を読み取る前に拒否する], 処理: [1: リポジトリ外の位置を渡す, 2: 読み取り処理が呼ばれないことを確認する], 引数: [], 戻り値: []}
    def test_outside_definition_is_not_read(self):
        with patch.object(Path, "read_text", side_effect=AssertionError("must not read")):
            with self.assertRaisesRegex(ValueError, "outside repository"):
                load_json(self.repo, self.repo.parent / "outside.json")

    # {責務: [test_internal_modules_are_not_public_surfaces: 内部モジュールを公開入口の件数に含めない], 処理: [1: 内部モジュールの登録を追加する, 2: 公開面の集合が変わらないことを確認する], 引数: [], 戻り値: []}
    def test_internal_modules_are_not_public_surfaces(self):
        before = public_surfaces(self.inventory)
        self.inventory["internal_python"] = ["tools/internal.py"]
        self.assertEqual(before, public_surfaces(self.inventory))


if __name__ == "__main__":
    unittest.main()
