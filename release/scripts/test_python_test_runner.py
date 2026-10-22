"""テスト未実行を成功にしない実行器の回帰試験。"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


RUNNER = Path(__file__).with_name("run_python_tests.py")
PASSING = "import unittest\nclass Tests(unittest.TestCase):\n    def test_pass(self):\n        self.assertEqual(1, 1)\n"


# {責務: [PythonTestRunnerTests: 未収集・失敗・全件省略とプロセス間の混入を検査する], フィールド: [root: 試験用のリポジトリ], 処理: [1: 各種テストファイルを作る, 2: 本物の実行器の終了コードと報告を照合する]}
class PythonTestRunnerTests(unittest.TestCase):
    # {責務: [setUp: 検査用のリポジトリを用意する], 処理: [1: 一時作業先を作り終了時の削除を予約する], 引数: [], 戻り値: []}
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    # {責務: [write_test: 試験内容を指定した場所へ保存する], 処理: [1: 必要な親を作る, 2: テスト本文を保存する], 引数: [name: ツール名, source: テスト本文, nested: tests内の配置先], 戻り値: [1: 保存先]}
    def write_test(self, name, source, nested=""):
        path = self.root / "tools" / name / "tests" / nested / "test_case.py"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(source, encoding="utf-8")
        return path

    # {責務: [invoke: 作成した試験群へ実行器を適用する], 処理: [1: 新しいプロセスで実行する, 2: 終了コードとJSONを返す], 引数: [optimize: 呼び出し元に設定する最適化の値], 戻り値: [1: 終了コード, 2: 全体の報告]}
    def invoke(self, optimize="0"):
        result = subprocess.run([sys.executable, str(RUNNER), "--root", str(self.root)],
                                capture_output=True, text=True, timeout=30,
                                env=dict(os.environ, PYTHONOPTIMIZE=optimize))
        self.assertTrue(result.stdout.strip(), result.stderr)
        return result.returncode, json.loads(result.stdout)

    # {責務: [test_collected_test_runs_without_main_block: 直接実行用の末尾がなくてもテストを実行する], 処理: [1: 一件の試験を作る, 2: 発見・実行件数と成功を照合する], 引数: [], 戻り値: []}
    def test_collected_test_runs_without_main_block(self):
        self.write_test("one", PASSING)
        code, report = self.invoke()
        self.assertEqual(0, code)
        self.assertEqual({"status": "ok", "files_discovered": 1, "files_executed": 1,
                          "tests_executed": 1, "tests_skipped": 0}, report)

    # {責務: [test_empty_or_uncollected_tests_fail: ファイルもテストもない場合に成功させない], 処理: [1: 空の対象を調べる, 2: 収集されない関数と空ファイルを順に調べる], 引数: [], 戻り値: []}
    def test_empty_or_uncollected_tests_fail(self):
        code, report = self.invoke()
        self.assertEqual(1, code)
        self.assertEqual(0, report["files_executed"])
        for source in ("", "def test_uncollected():\n    assert False\n"):
            with self.subTest(source=source):
                self.write_test("one", source)
                code, report = self.invoke()
                self.assertEqual(1, code)
                self.assertEqual(0, report["tests_executed"])

    # {責務: [test_failures_import_errors_and_all_skipped_fail: 失敗・読み込み異常・全件省略を拒否する], 処理: [1: 各異常を起こす試験を作る, 2: 最適化指定があっても異常終了することを確認する], 引数: [], 戻り値: []}
    def test_failures_import_errors_and_all_skipped_fail(self):
        sources = (
            PASSING.replace("self.assertEqual(1, 1)", "assert False"),
            "raise RuntimeError('import failed')\n",
            PASSING.replace("class Tests", "@unittest.skip('fixture')\nclass Tests"),
        )
        for source in sources:
            with self.subTest(source=source):
                self.write_test("one", source)
                code, report = self.invoke(optimize="2")
                self.assertEqual(1, code)
                self.assertEqual("incomplete", report["status"])

    # {責務: [test_same_named_modules_are_isolated_and_nested_tests_run: 同名の内部モジュールが他の試験へ混ざらず入れ子も実行されることを確認する], 処理: [1: 同名で異なる値の依存先を作る, 2: 両方の試験が成功することを照合する], 引数: [], 戻り値: []}
    def test_same_named_modules_are_isolated_and_nested_tests_run(self):
        for name in ("first", "second"):
            source = PASSING.replace("import unittest", "import unittest\nimport processing")
            source = source.replace("self.assertEqual(1, 1)", f"self.assertEqual(processing.VALUE, '{name}')")
            path = self.write_test(name, source, "nested" if name == "second" else "")
            path.with_name("processing.py").write_text(f"VALUE = '{name}'\n", encoding="utf-8")
        code, report = self.invoke()
        self.assertEqual(0, code)
        self.assertEqual(2, report["files_executed"])
        self.assertEqual(2, report["tests_executed"])

    # {責務: [test_collected_but_not_executed_suite_fails: 収集件数だけを返す試験群を成功させない], 処理: [1: 実行しない試験群を作る, 2: 実行件数の不足で拒否することを確認する], 引数: [], 戻り値: []}
    def test_collected_but_not_executed_suite_fails(self):
        source = PASSING + "\nclass EmptyRun(unittest.TestSuite):\n    def run(self, result, debug=False):\n        return result\ndef load_tests(loader, tests, pattern):\n    return EmptyRun([Tests('test_pass')])\n"
        self.write_test("one", source)
        code, report = self.invoke()
        self.assertEqual(1, code)
        self.assertEqual(0, report["tests_executed"])

    # {責務: [test_uncollected_function_beside_class_fails: クラスの成功で未収集の関数が隠れないことを確認する], 処理: [1: 成功するクラスと未収集の関数を同居させる, 2: 全体が異常終了することを照合する], 引数: [], 戻り値: []}
    def test_uncollected_function_beside_class_fails(self):
        self.write_test("one", PASSING + "\ndef test_hidden():\n    assert False\n")
        code, report = self.invoke()
        self.assertEqual(1, code)
        self.assertEqual("incomplete", report["status"])

    # {責務: [test_failure_does_not_hide_later_test_files: 先頭が失敗しても後続を実行し全体は失敗にする], 処理: [1: 失敗と成功の試験を別々に作る, 2: 両方の実行件数と全体の失敗を照合する], 引数: [], 戻り値: []}
    def test_failure_does_not_hide_later_test_files(self):
        self.write_test("first", PASSING.replace("self.assertEqual(1, 1)", "self.fail('fixture')"))
        self.write_test("second", PASSING)
        code, report = self.invoke()
        self.assertEqual(1, code)
        self.assertEqual(2, report["files_executed"])
        self.assertEqual(2, report["tests_executed"])


if __name__ == "__main__":
    unittest.main()
