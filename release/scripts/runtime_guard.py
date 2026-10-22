"""Release-only command traps and filesystem change detection."""

import hashlib
import json
import os
import shutil
import subprocess


INSTALL_COMMANDS = (
    "pip", "pip3", "npm", "npx", "yarn", "pnpm", "corepack", "go", "cargo", "rustup",
    "brew", "apt", "apt-get", "dpkg", "dnf", "yum", "apk", "pacman", "port",
    "winget", "choco", "scoop", "nuget", "gem", "bundle", "composer", "uv",
)


# {責務: [snapshot: 監視対象の内容と種類を変更検出用に記録する], 処理: [1: 隠しファイルと空ディレクトリを含めて列挙する, 2: ファイルの内容をハッシュ化する], 引数: [root: 監視対象], 戻り値: [1: 相対位置と内容の対応]}
def snapshot(root):
    result = {}
    for path in sorted(root.rglob("*")):
        name = path.relative_to(root).as_posix()
        if path.is_symlink():
            result[name] = ("link", os.readlink(path))
        elif path.is_dir():
            result[name] = ("directory",)
        else:
            with path.open("rb") as stream:
                result[name] = ("file", hashlib.file_digest(stream, "sha256").hexdigest(), path.stat().st_mode)
    return result


# {責務: [assert_unchanged: 追加・削除・書き換えを失敗として報告する], 処理: [1: 実行後の記録と比較する, 2: 変化した相対位置を示す], 引数: [root: 監視対象, before: 実行前の記録], 戻り値: []}
def assert_unchanged(root, before):
    after = snapshot(root)
    changed = sorted(name for name in before.keys() | after.keys() if before.get(name) != after.get(name))
    if changed:
        raise RuntimeError(f"unexpected filesystem changes in {root.name}: {changed}")


# {責務: [prepare_install_guard: 導入コマンド名で呼べる検査用実行ファイルを用意する], 処理: [1: 各コマンド名へ検査専用バイナリを配置する, 2: 全コマンドの拒否と記録を事前に検証する], 引数: [binary: 検査専用バイナリ, directory: 配置先, log: 呼び出し記録, env: 子プロセスの環境], 戻り値: [1: 検査用の子プロセス環境]}
def prepare_install_guard(binary, directory, log, env):
    directory.mkdir()
    guarded = dict(env, PATH=str(directory), ACR_INSTALL_GUARD_LOG=str(log))
    suffix = ".exe" if os.name == "nt" else ""
    for name in INSTALL_COMMANDS:
        target = directory / (name + suffix)
        try:
            os.link(binary, target)
        except OSError:
            shutil.copy2(binary, target)
        result = subprocess.run([str(target), "--acr-guard-self-test"], env=guarded,
                                cwd=directory, capture_output=True, timeout=10)
        if result.returncode != 97:
            raise RuntimeError(f"installation guard not executable: {name}")
    recorded = [json.loads(line)["command"] for line in log.read_text(encoding="utf-8").splitlines()]
    if recorded != [name + suffix for name in INSTALL_COMMANDS]:
        raise RuntimeError("installation guard failed its recording control")
    # 事前確認の記録は除き、以後は検査対象からの呼び出しだけを違反とする。
    log.unlink()
    return guarded


# {責務: [assert_no_install_attempts: 検査対象が導入コマンドを呼んだ事実を失敗にする], 処理: [1: 呼び出し記録の有無を調べる, 2: 記録があれば診断を返す], 引数: [log: 呼び出し記録], 戻り値: []}
def assert_no_install_attempts(log):
    if log.exists():
        raise RuntimeError(f"installation command attempted: {log.read_text(encoding='utf-8')[:2000]}")
