"""公開入口と内部Pythonモジュールの明示一覧を実装と照合する。"""

import argparse
import ast
import json
import subprocess
from pathlib import Path, PurePosixPath


SKIP_DIRECTORIES = {"tests", "testdata", "fixtures", "dist", "bin", "node_modules", "__pycache__"}
FIELDS = {"schema_version", "coverage", "python", "internal_python", "shell", "go"}


# {責務: [unique_object: JSONの同じ項目名による上書きを拒否する], 処理: [1: 項目を順に保存する, 2: 重複があれば失敗にする], 引数: [pairs: JSONの項目], 戻り値: [1: 重複のない対応表]}
def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


# {責務: [has_main_guard: Pythonを直接起動する入口が宣言されているか判定する], 処理: [1: 構文を読み取る, 2: モジュール直下の起動条件を探す], 引数: [path: Pythonソース], 戻り値: [1: 起動条件がある場合は真]}
def has_main_guard(path):
    tree = ast.parse(path.read_text(encoding="utf-8-sig"))
    for statement in tree.body:
        if not isinstance(statement, ast.If):
            continue
        for node in ast.walk(statement.test):
            if not isinstance(node, ast.Compare) or len(node.ops) != 1 or not isinstance(node.ops[0], ast.Eq):
                continue
            left, right = node.left, node.comparators[0]
            for name, value in ((left, right), (right, left)):
                if isinstance(name, ast.Name) and name.id == "__name__" and isinstance(value, ast.Constant) and value.value == "__main__":
                    return True
    return False


# {責務: [discover: ソースの公開入口と内部モジュールを分類する], 処理: [1: 対象外の保存先を除く, 2: Pythonとシェルを列挙する, 3: Goの構文解析結果を統合する], 引数: [root: リポジトリ, go_entries: Goの構文解析結果], 戻り値: [1: 分類ごとの実装一覧]}
def discover(root, go_entries):
    result = {"python": [], "internal_python": [], "shell": [], "go": {}}
    for path in sorted((root / "tools").rglob("*")):
        relative = path.relative_to(root)
        if any(part in SKIP_DIRECTORIES or part.startswith(".") for part in relative.parts[:-1]):
            continue
        if path.suffix not in {".py", ".sh", ".bat", ".ps1"}:
            continue
        if path.is_symlink():
            raise ValueError(f"source symlink is not supported: {relative}")
        if not path.is_file():
            continue
        category = ("python" if has_main_guard(path) else "internal_python") if path.suffix == ".py" else "shell"
        result[category].append(relative.as_posix())
    if not isinstance(go_entries, list) or not go_entries:
        raise ValueError("Go scanner returned no entrypoints")
    for entry in go_entries:
        if set(entry) != {"path", "commands"} or entry["path"] in result["go"]:
            raise ValueError("invalid or duplicate Go scanner entry")
        result["go"][entry["path"]] = entry["commands"]
    return result


# {責務: [check_names: 重複や曖昧なソース位置を一覧へ登録させない], 処理: [1: 一覧と要素の型を確認する, 2: 重複と相対位置の表記を検証する], 引数: [names: 登録値, paths: ソース位置として扱うか], 戻り値: []}
def check_names(names, paths=True):
    if not isinstance(names, list) or any(not isinstance(name, str) or not name for name in names):
        raise ValueError("inventory entries must be nonempty strings in a list")
    if len(names) != len(set(names)):
        raise ValueError("duplicate inventory entry")
    if paths:
        for name in names:
            path = PurePosixPath(name)
            if not name.startswith("tools/") or "\\" in name or ".." in path.parts or path.as_posix() != name:
                raise ValueError(f"invalid inventory path: {name}")


# {責務: [validate: 明示一覧の欠落・余分な登録・分類違いを失敗にする], 処理: [1: 一覧の形式を検証する, 2: 実装からの探索結果と照合する, 3: 確認できた登録件数だけを返す], 引数: [manifest: 明示一覧, actual: 探索結果], 戻り値: [1: 登録の検査結果]}
def validate(manifest, actual):
    if (set(manifest) != FIELDS or type(manifest["schema_version"]) is not int or manifest["schema_version"] != 1
            or manifest["coverage"] != "inventory_only" or not isinstance(manifest["go"], dict)):
        raise ValueError("unsupported inventory schema or coverage claim")
    errors = []
    for category in ("python", "internal_python", "shell"):
        check_names(manifest[category])
        expected, found = set(manifest[category]), set(actual[category])
        if expected != found:
            errors.append(f"{category}: unregistered={sorted(found - expected)}, stale={sorted(expected - found)}")
    check_names(list(manifest["go"]))
    for path, commands in manifest["go"].items():
        check_names(commands, paths=False)
        if sorted(commands) != sorted(actual["go"].get(path, [])) or path not in actual["go"]:
            errors.append(f"Go entrypoint or commands changed: {path}")
    if set(actual["go"]) - set(manifest["go"]):
        errors.append(f"unregistered Go entrypoints: {sorted(set(actual['go']) - set(manifest['go']))}")
    if errors:
        raise ValueError("\n".join(errors))
    return {"status": "inventory_ok", "io_coverage": "not_checked", "python": len(actual["python"]),
            "internal_python": len(actual["internal_python"]), "shell": len(actual["shell"]),
            "go": len(actual["go"]), "go_commands": sum(len(names) for names in actual["go"].values())}


# {責務: [main: 探索専用バイナリと明示一覧を接続して登録検査を実行する], 処理: [1: Goの探索結果を取得する, 2: 明示一覧を読み取る, 3: 実装との照合結果を出力する], 引数: [], 戻り値: []}
def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--go-scanner", required=True, type=Path)
    args = parser.parse_args()
    root = args.repo.resolve()
    completed = subprocess.run([str(args.go_scanner.resolve()), str(root)], capture_output=True, text=True, check=True, timeout=60)
    actual = discover(root, json.loads(completed.stdout, object_pairs_hook=unique_object))
    manifest = json.loads((root / "release/ENTRYPOINTS.json").read_text(encoding="utf-8"), object_pairs_hook=unique_object)
    print(json.dumps(validate(manifest, actual)))


if __name__ == "__main__":
    main()
