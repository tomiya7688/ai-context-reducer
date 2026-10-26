"""公開入口と共通入出力事例を照合し、既知の未割り当てだけを段階的に許可する。"""

import argparse
import json
import sys
from pathlib import Path

from entrypoint_inventory import check_names, unique_object
from io_parity import run_suite, validate_suite

TOOLBOX = "tools/common/native/acr-toolbox/main.go"


# {責務: [load_json: リポジトリ外やリンク先の定義を読み込まない], 処理: [1: 保存位置を検証する, 2: 重複項目を拒否して読む], 引数: [repo: リポジトリ, path: 定義の位置], 戻り値: [1: JSONの値]}
def load_json(repo, path):
    if path.is_symlink() or not path.resolve().is_relative_to(repo):
        raise ValueError(f"definition is outside repository or a symlink: {path}")
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)


# {責務: [public_surfaces: 公開入口とGoの各コマンドへ照合用の識別子を与える], 処理: [1: 登録の重複と位置を検証する, 2: 内部モジュールを除いて列挙する], 引数: [inventory: 公開入口一覧], 戻り値: [1: 公開面の識別子集合]}
def public_surfaces(inventory):
    surfaces = set()
    for kind in ("python", "shell"):
        check_names(inventory[kind])
        surfaces.update(f"{kind}:{path}" for path in inventory[kind])
    check_names(list(inventory["go"]))
    for path, commands in inventory["go"].items():
        check_names(commands, paths=False)
        surfaces.add(f"go:{path}")
        surfaces.update(f"go-command:{path}:{command}" for command in commands)
    return surfaces


# {責務: [load_coverage: 公開入口を事例ありと既知の未割り当てへ分ける], 処理: [1: 定義を読み検証する, 2: 実行できる事例を全件集める, 3: 新規の欠落・古い例外・重複を拒否する], 引数: [repo: リポジトリ], 戻り値: [1: 割り当て報告, 2: 全ての事例定義]}
def load_coverage(repo):
    repo = repo.resolve()
    inventory = load_json(repo, repo / "release/ENTRYPOINTS.json")
    baseline = load_json(repo, repo / "release/IO_PENDING.json")
    if (
        not isinstance(baseline, dict)
        or set(baseline) != {"schema_version", "issue", "pending"}
        or type(baseline["schema_version"]) is not int
        or baseline["schema_version"] != 1
        or type(baseline["issue"]) is not int
        or baseline["issue"] <= 0
    ):
        raise ValueError("unsupported pending baseline schema")
    names = baseline["pending"]
    if (
        not isinstance(names, list)
        or any(not isinstance(name, str) or not name for name in names)
        or len(names) != len(set(names))
    ):
        raise ValueError("pending entries must be unique nonempty strings")
    public = public_surfaces(inventory)
    pending, assigned, suites = set(names), set(), []
    directory = repo / "release/fixtures"
    if directory.is_symlink() or not directory.resolve().is_relative_to(repo):
        raise ValueError("suite directory must stay inside repository")
    for path in sorted(directory.glob("*.json")):
        suite = load_json(repo, path)
        validate_suite(suite, inventory)
        # 共通の起動口がまだない単独バイナリを、toolboxで検査済みにはしない。
        if suite["go_entry"] != TOOLBOX:
            raise ValueError(f"unsupported binary execution route: {path}")
        assigned.update(
            (
                f"python:{suite['python_entry']}",
                f"go-command:{suite['go_entry']}:{suite['command']}",
            )
        )
        suites.append((path.relative_to(repo).as_posix(), suite))
    if not suites:
        raise ValueError("no I/O suites found")
    # コマンドを持つGo入口は、列挙された全コマンドの割り当てがある場合だけ集約する。
    for path, commands in inventory["go"].items():
        if commands and all(f"go-command:{path}:{command}" in assigned for command in commands):
            assigned.add(f"go:{path}")
    missing, stale, overlap = public - assigned - pending, pending - public, pending & assigned
    if missing or stale or overlap:
        raise ValueError(
            f"I/O assignments changed: unassigned={sorted(missing)}, "
            f"stale_pending={sorted(stale)}, already_assigned={sorted(overlap)}"
        )
    return {
        "coverage": "partial" if pending else "complete",
        "public_surfaces": len(public),
        "assigned_surfaces": len(assigned),
        "pending_surfaces": len(pending),
        "pending_issue": baseline["issue"],
        "pending": sorted(pending),
        "suite_files": [name for name, _ in suites],
        "case_count": sum(len(suite["cases"]) for _, suite in suites),
    }, suites


# {責務: [execute_suites: 割り当てとして数えた全ての定義を指定した経路で実行する], 処理: [1: 各定義の入口を起動引数へ変換する, 2: 共通比較器で全件を検査する], 引数: [repo: リポジトリ, suites: 検証済み定義, python: Python版も起動するか, binary: 同梱toolboxの位置], 戻り値: [1: 実行件数]}
def execute_suites(repo, suites, python=False, binary=None):
    if not python and binary is None:
        raise ValueError("at least one execution route is required")
    count = 0
    for _, suite in suites:
        commands = {}
        if python:
            entry = repo / suite["python_entry"]
            if entry.is_symlink() or not entry.resolve().is_relative_to(repo.resolve()):
                raise ValueError(f"Python entry must stay inside repository: {entry}")
            commands["python"] = [sys.executable, str(entry)]
        if binary is not None:
            commands["binary"] = [str(binary.resolve()), suite["command"]]
        count += run_suite(suite, commands)
    return count


# {責務: [main: 通常の段階的検査と公開前の厳密な検査を区別する], 処理: [1: 割り当てを照合する, 2: 指定された場合だけ事例を実行する, 3: 未割り当てがあれば既定では失敗する], 引数: [], 戻り値: [1: 合格なら0、未割り当てが残れば1]}
def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--allow-pending", action="store_true")
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--python", action="store_true")
    parser.add_argument("--binary", type=Path)
    args = parser.parse_args()
    if args.run != bool(args.python or args.binary):
        parser.error("--run and at least one of --python/--binary must be supplied together")
    repo = args.repo.resolve()
    report, suites = load_coverage(repo)
    incomplete = report["pending_surfaces"] > 0 and not args.allow_pending
    report["status"] = "incomplete" if incomplete else "ok"
    report["executions"] = 0
    report["executed_routes"] = []
    if args.run and not incomplete:
        report["executions"] = execute_suites(repo, suites, args.python, args.binary)
        report["executed_routes"] = [
            route
            for route, enabled in (("python", args.python), ("binary", args.binary))
            if enabled
        ]
        # 成功した実行では残件一覧を省く。未実行の失敗では診断を残す。
        del report["pending"]
    print(json.dumps(report))
    return 1 if incomplete else 0


if __name__ == "__main__":
    sys.exit(main())
