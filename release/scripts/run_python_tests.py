"""Pythonの各テストファイルを別プロセスで収集し、実行件数を検証する。"""

import argparse
import ast
import io
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path


# {責務: [run_file: 一つのテストファイルを収集し実行結果と件数を返す], 処理: [1: unittestで収集する, 2: 収集できたテストを実行する, 3: 失敗・未実行・全件省略を識別する], 引数: [path: 対象ファイル], 戻り値: [1: 状態と件数の報告]}
def run_file(path):
    tree = ast.parse(path.read_text(encoding="utf-8-sig"))
    functions = [node.name for node in tree.body
                 if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_")]
    if functions:
        return {"file": str(path), "collected": 0, "executed": 0, "skipped": 0,
                "status": "unsupported_test_functions", "functions": functions}
    loader = unittest.TestLoader()
    suite = loader.discover(str(path.parent), pattern=path.name)
    collected = suite.countTestCases()
    report = {"file": str(path), "collected": collected, "executed": 0, "skipped": 0, "status": "no_tests"}
    if collected == 0:
        return report
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, buffer=True).run(suite)
    report.update(executed=result.testsRun, skipped=len(result.skipped),
                  failures=len(result.failures), errors=len(result.errors))
    if not result.wasSuccessful():
        report["status"] = "failed"
        sys.stderr.write(stream.getvalue())
    elif result.testsRun == 0 or result.testsRun != collected:
        report["status"] = "incomplete"
    elif result.testsRun == len(result.skipped):
        report["status"] = "all_skipped"
    else:
        report["status"] = "ok"
    return report


# {責務: [run_all: 全テストファイルを別プロセスで検査し結果を集計する], 処理: [1: tests内の対象ファイルを列挙する, 2: 一つずつ隔離して実行する, 3: 実行漏れや異常終了を失敗にする], 引数: [root: リポジトリの位置], 戻り値: [1: 全体の状態と件数]}
def run_all(root):
    files = sorted(path for path in (root / "tools").rglob("test_*.py") if "tests" in path.relative_to(root / "tools").parts[:-1])
    reports = []
    for path in files:
        # 同名のテストやprocessingなどの読み込み済みモジュールが他のツールへ混ざるのを防ぐ。
        command = [sys.executable, str(Path(__file__).resolve()), "--root", str(root), "--test-file", str(path)]
        result = subprocess.run(command, cwd=root, env=dict(os.environ, PYTHONOPTIMIZE="0"),
                                capture_output=True, text=True, timeout=180)
        if result.stderr:
            sys.stderr.write(result.stderr)
        try:
            report = json.loads(result.stdout)
        except ValueError:
            raise RuntimeError(f"test process did not return a report: {path}: {result.stdout[:1000]}") from None
        if result.returncode != 0 and report["status"] == "ok":
            report["status"] = "process_failed"
        reports.append(report)
        print(f"{path.relative_to(root).as_posix()}: {report['status']}, executed={report['executed']}, skipped={report['skipped']}", file=sys.stderr)
    complete = bool(files) and len(reports) == len(files) and all(report["status"] == "ok" for report in reports)
    return {"status": "ok" if complete else "incomplete", "files_discovered": len(files),
            "files_executed": len(reports), "tests_executed": sum(report["executed"] for report in reports),
            "tests_skipped": sum(report["skipped"] for report in reports)}


# {責務: [main: 一件の検査と全件検査を選び終了コードを確定する], 処理: [1: 入力を解析する, 2: 対象を検証して実行する, 3: JSONと終了コードで結果を返す], 引数: [], 戻り値: [1: 正常なら0、それ以外は1]}
def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--test-file", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    if args.test_file:
        path = args.test_file.resolve()
        if (not path.is_relative_to(root / "tools") or "tests" not in path.relative_to(root / "tools").parts[:-1]
                or not path.name.startswith("test_") or path.suffix != ".py" or not path.is_file()):
            parser.error("test file must be tools/**/tests/test_*.py")
        report = run_file(path)
    else:
        report = run_all(root)
    print(json.dumps(report))
    return 0 if report["status"] == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
