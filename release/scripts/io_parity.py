"""固定入力と期待値をPython版・バイナリ版へ共通に適用する。"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path, PurePosixPath

from entrypoint_inventory import unique_object
from runtime_guard import assert_unchanged, snapshot


# {責務: [relative_path: 固定入力の保存先を作業先の内側に限定する], 処理: [1: 相対表記を検証する, 2: 正規化した位置を返す], 引数: [name: 入力の相対位置, allow_root: 作業先自体を許すか], 戻り値: [1: 相対位置]}
def relative_path(name, allow_root=False):
    if not isinstance(name, str) or not name or "\\" in name or ":" in name:
        raise ValueError(f"invalid fixture path: {name}")
    path = PurePosixPath(name)
    if path.is_absolute() or ".." in path.parts or path.as_posix() != name or (name == "." and not allow_root):
        raise ValueError(f"invalid fixture path: {name}")
    return path


# {責務: [validate_suite: 入力と期待値の形式および公開入口への対応を確認する], 処理: [1: 形式と重複を検査する, 2: 公開入口一覧と照合する, 3: 全事例の入力を検証する], 引数: [suite: 検査定義, inventory: 公開入口一覧], 戻り値: []}
def validate_suite(suite, inventory):
    if set(suite) != {"schema_version", "python_entry", "go_entry", "command", "fixtures", "cases"} or type(suite["schema_version"]) is not int or suite["schema_version"] != 1:
        raise ValueError("unsupported I/O suite schema")
    if suite["python_entry"] not in inventory["python"] or suite["command"] not in inventory["go"].get(suite["go_entry"], []):
        raise ValueError("I/O suite refers to an unregistered entrypoint")
    if not isinstance(suite["fixtures"], dict) or not suite["fixtures"] or not isinstance(suite["cases"], list) or not suite["cases"]:
        raise ValueError("fixtures and cases must not be empty")
    for files in suite["fixtures"].values():
        if not isinstance(files, dict):
            raise ValueError("fixture must map paths to text")
        for name, content in files.items():
            relative_path(name)
            if not isinstance(content, str):
                raise ValueError("fixture content must be text")
    seen = set()
    for case in suite["cases"]:
        if not isinstance(case, dict) or set(case) != {"id", "fixture", "root", "args", "exit_code", "stderr", "json"}:
            raise ValueError("invalid I/O case fields")
        if not isinstance(case["id"], str) or not case["id"] or case["id"] in seen:
            raise ValueError("invalid or duplicate I/O case id")
        seen.add(case["id"])
        relative_path(case["root"], allow_root=True)
        if case["fixture"] not in suite["fixtures"] or not isinstance(case["args"], list) or any(not isinstance(arg, str) for arg in case["args"]):
            raise ValueError("invalid fixture reference or arguments")
        if type(case["exit_code"]) is not int or not isinstance(case["stderr"], str) or not isinstance(case["json"], dict) or not case["json"].get("status"):
            raise ValueError("exit code, stderr and JSON status expectations are required")


# {責務: [project_expected: 契約で指定した項目を型ごとに照合する], 処理: [1: 必要な項目の存在を確かめる, 2: 入れ子と値を比較する], 引数: [actual: 実際のJSON, expected: 明示した期待値, location: 診断用の位置], 戻り値: [1: 照合済みの項目]}
def project_expected(actual, expected, location="$"):
    if type(actual) is not type(expected):
        raise ValueError(f"{location}: JSON type mismatch")
    if isinstance(expected, dict):
        if not set(expected).issubset(actual):
            raise ValueError(f"{location}: missing JSON fields")
        # 空の辞書は、言語別集計が存在しないという期待値にも使う。
        if not expected and actual:
            raise ValueError(f"{location}: expected an empty object")
        return {key: project_expected(actual[key], value, f"{location}.{key}") for key, value in expected.items()}
    if actual != expected:
        raise ValueError(f"{location}: expected {expected!r}, got {actual!r}")
    return actual


# {責務: [run_suite: 同じ入力と期待値で各実装の応答と入力保護を確認する], 処理: [1: 固定入力と空の探索先を作る, 2: 指定した実装を実行する, 3: 終了状態・JSON・書き換え・実装間の一致を照合する], 引数: [suite: 検査定義, commands: 実装名と起動引数], 戻り値: [1: 実行した組み合わせの件数]}
def run_suite(suite, commands):
    if not commands:
        raise ValueError("at least one execution route is required")
    count = 0
    for case in suite["cases"]:
        previous = None
        for route, command in commands.items():
            with tempfile.TemporaryDirectory() as temporary:
                work = Path(temporary)
                project = work / "project"
                project.mkdir()
                for name, content in suite["fixtures"][case["fixture"]].items():
                    path = project / relative_path(name)
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(content.encode("utf-8"))
                empty_path = work / "empty-path"
                empty_path.mkdir()
                root = project / relative_path(case["root"], allow_root=True)
                env = dict(os.environ, PATH=str(empty_path), PYTHONDONTWRITEBYTECODE="1")
                before = snapshot(work)
                result = subprocess.run([*command, *case["args"], str(root)], input="", capture_output=True,
                                        text=True, encoding="utf-8", env=env, cwd=work, timeout=30)
                label = f"{case['id']}/{route}"
                if result.returncode != case["exit_code"] or result.stderr != case["stderr"]:
                    raise ValueError(f"{label}: exit/stderr mismatch: {result.returncode}: {result.stderr}")
                payload = json.loads(result.stdout, object_pairs_hook=unique_object)
                if not isinstance(payload, dict) or payload.get("project_root") != str(root.resolve()):
                    raise ValueError(f"{label}: unexpected project_root")
                projected = project_expected(payload, case["json"], label)
                assert_unchanged(work, before)
                if previous is not None and projected != previous:
                    raise ValueError(f"{label}: implementation parity mismatch")
                previous = projected
                count += 1
    return count


# {責務: [main: 検査定義を指定経路へ接続して部分的な検査結果を報告する], 処理: [1: 定義と公開入口を照合する, 2: 指定した経路だけを起動する, 3: 未検査範囲を明示する], 引数: [], 戻り値: []}
def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--suite", default="release/fixtures/repo-stats.json")
    parser.add_argument("--binary", type=Path)
    parser.add_argument("--python", action="store_true", help="Also execute the source Python entrypoint")
    args = parser.parse_args()
    repo = args.repo.resolve()
    suite = json.loads((repo / relative_path(args.suite)).read_text(encoding="utf-8"), object_pairs_hook=unique_object)
    inventory = json.loads((repo / "release/ENTRYPOINTS.json").read_text(encoding="utf-8"), object_pairs_hook=unique_object)
    validate_suite(suite, inventory)
    commands = {}
    if args.python:
        commands["python"] = [sys.executable, str(repo / suite["python_entry"])]
    if args.binary:
        commands["binary"] = [str(args.binary.resolve()), suite["command"]]
    count = run_suite(suite, commands)
    print(json.dumps({"status": "ok", "coverage": "partial", "cases": len(suite["cases"]),
                      "executions": count, "routes": list(commands), "python_entry": suite["python_entry"],
                      "go_entry": suite["go_entry"], "command": suite["command"]}))


if __name__ == "__main__":
    main()
