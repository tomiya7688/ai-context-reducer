"""Run packaged CLI and GUI with no language runtimes or SDKs on PATH."""

import argparse
import json
import os
import re
import shutil
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

from runtime_guard import assert_no_install_attempts, assert_unchanged, prepare_install_guard, snapshot


# {責務: [run_json: 同梱バイナリの終了状態とJSONを検証する], 処理: [1: 隔離環境で実行する, 2: 終了コードと診断を確認してJSONを返す], 引数: [args: コマンド, env: 隔離環境, cwd: 作業先, expected_code: 期待する終了コード], 戻り値: [1: 解析したJSON]}
def run_json(args, env, cwd, expected_code=0):
    result = subprocess.run(args, env=env, cwd=cwd, capture_output=True, text=True, timeout=30)
    if result.returncode != expected_code or result.stderr.strip():
        raise RuntimeError(f"packaged command failed: {args[0]} code={result.returncode}: {result.stderr}")
    return json.loads(result.stdout)


# {責務: [gui_smoke: 同梱GUI経由で本物のCLIと拒否条件を確認する], 処理: [1: 同梱GUIを起動する, 2: 認証なしの拒否と認証後のCLI実行を確かめる, 3: 重い解析の確認要求を検査し終了する], 引数: [bundle: 配布先, project: 検査用の入力, env: 隔離環境, work: 記録先], 戻り値: []}
def gui_smoke(bundle, project, env, work):
    suffix = ".exe" if os.name == "nt" else ""
    binary = bundle / "gui" / ("acr-hub" + suffix)
    # 外部のビルド結果を渡すとGUIの同梱漏れを見逃すため、配布物内の実行ファイルだけを使う。
    with (work / "gui.log").open("w", encoding="utf-8") as log:
        process = subprocess.Popen([str(binary), "--bundle-root", str(bundle), "--no-open"],
                                   cwd=work, env=env, stdout=log, stderr=log,
                                   creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
        try:
            url = None
            for _ in range(100):
                text = (work / "gui.log").read_text(encoding="utf-8")
                match = re.search(r"AI Context Reducer Hub: (http://127\.0\.0\.1:\d+/)", text)
                if match:
                    url = match.group(1).rstrip("/")
                    break
                if process.poll() is not None:
                    raise RuntimeError(f"GUI exited before readiness: {text}")
                time.sleep(0.1)
            if not url:
                raise RuntimeError("GUI readiness timeout")
            opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
            with opener.open(url + "/api/health", timeout=10) as response:
                if json.load(response) != {"status": "ok"}:
                    raise RuntimeError("invalid GUI health")
            with opener.open(url + "/", timeout=10) as response:
                html = response.read().decode("utf-8")
            token = re.search(r'name="acr-session" content="([0-9a-f]+)"', html)
            if not token:
                raise RuntimeError("missing GUI session token")
            payload = json.dumps({"action_id": "project-overview", "project_root": str(project), "values": {}}).encode()
            request = urllib.request.Request(url + "/api/run", data=payload, headers={"Content-Type": "application/json"})
            try:
                opener.open(request, timeout=10).close()
            except urllib.error.HTTPError as error:
                if error.code != 403:
                    raise
            else:
                raise RuntimeError("GUI accepted an unauthenticated command")
            request.add_header("X-ACR-Session", token.group(1))
            with opener.open(request, timeout=15) as response:
                result = json.load(response)
            if result["result"]["state"] != "success":
                raise RuntimeError(f"GUI failed to execute packaged CLI: {result}")
            heavy = json.dumps({"action_id": "large-run", "project_root": str(project), "values": {}}).encode()
            request = urllib.request.Request(url + "/api/run", data=heavy,
                                             headers={"Content-Type": "application/json", "X-ACR-Session": token.group(1)})
            with opener.open(request, timeout=10) as response:
                result = json.load(response)
            if result["result"]["state"] != "confirmation_required":
                raise RuntimeError("GUI executed heavy analysis without confirmation")
        finally:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)


# {責務: [wrapper_command: 配布物のラッパーを標準シェルで起動する引数へ変換する], 処理: [1: OSに対応する拡張子と起動引数を選ぶ], 引数: [bundle: 配布先, name: ラッパー名, project: 調査対象, shell: 標準シェルの絶対位置], 戻り値: [1: 起動引数]}
def wrapper_command(bundle, name, project, shell):
    if os.name == "nt":
        return [shell, "/d", "/c", str(bundle / (name + ".bat")), str(project)]
    return [shell, str(bundle / (name + ".sh")), str(project)]


# {責務: [setup_smoke: 初期設定の出力を確認し想定外の書き込みを拒否する], 処理: [1: 専用の入力を用意する, 2: 五つの報告と生成物を検査する, 3: 元の入力が変わっていないことを確認する], 引数: [bundle: 配布先, project: 元の入力, env: 隔離環境, work: 記録先, shell: 標準シェル], 戻り値: []}
def setup_smoke(bundle, project, env, work, shell):
    target = work / "setup-project"
    shutil.copytree(project, target)
    before = snapshot(target)
    result = subprocess.run(wrapper_command(bundle, "setup", target, shell), env=env,
                            cwd=target, capture_output=True, text=True, timeout=30)
    if result.returncode != 0 or result.stderr.strip():
        raise RuntimeError(f"packaged setup failed: {result.returncode}: {result.stderr}")
    decoder, remaining, reports = json.JSONDecoder(), result.stdout.strip(), []
    while remaining:
        report, end = decoder.raw_decode(remaining)
        reports.append(report)
        remaining = remaining[end:].strip()
    if len(reports) != 5 or reports[-1].get("status") != "ok":
        raise RuntimeError("packaged setup omitted or failed an operation")
    after = snapshot(target)
    generated = {".acr", ".acr/language", ".acr/language/python_small_python_symbols.json"}
    if set(after) - set(before) != generated or any(after.get(key) != value for key, value in before.items()):
        raise RuntimeError("packaged setup wrote unexpected files or changed its input")
    output = json.loads((target / ".acr/language/python_small_python_symbols.json").read_text(encoding="utf-8"))
    if output.get("status") != "ok" or output.get("file_count") != 1:
        raise RuntimeError("packaged setup did not produce the native language analysis")


# {責務: [exercise: 配布物の基本機能と解析環境がない場合の応答を確認する], 処理: [1: 基本コマンドを実行する, 2: 外部検索手段がない場合の拒否と代替処理を確認する, 3: 同梱版ではラッパーとGUIも実行する], 引数: [bundle: 配布先, full: GUI同梱版か, env: 隔離環境, work: 記録先, shell: 標準シェル, empty_path: 実行環境の探索先が空か], 戻り値: []}
def exercise(bundle, full, env, work, shell, empty_path):
    project = work / "project"
    project.mkdir()
    (project / "README.md").write_text("# Fixture\n", encoding="utf-8")
    (project / "sample.py").write_text("def example():\n    return 1\n", encoding="utf-8")
    before = snapshot(project)
    binary = str(bundle / ("acr-toolbox.exe" if os.name == "nt" else "acr-toolbox"))
    for command in ("version", "env"):
        run_json([binary, command], env, project)
    languages = run_json([binary, "language-env"], env, project)
    if empty_path:
        expected = {"python", "csharp", "go", "c", "cpp", "gdscript"}
        if set(languages["languages"]) != expected or any(row["available"] or row["command"] for row in languages["languages"].values()):
            raise RuntimeError("language runtime availability report invalid with empty PATH")
    for command in ("analyze", "stats", "language-setup"):
        run_json([binary, command, str(project)], env, project)
    missing = run_json([binary, "find", "--backend", "fd", "*.py", str(project)], env, project, 2)
    if missing.get("status") != "external_backend_unavailable" or missing.get("backend") != "fd":
        raise RuntimeError("missing optional backend was not reported explicitly")
    fallback = run_json([binary, "find", "*.py", str(project)], env, project)
    if fallback.get("status") != "ok" or fallback.get("backend") != "portable" or not fallback.get("results"):
        raise RuntimeError("native search fallback unavailable")
    if full:
        run_json(wrapper_command(bundle, "analyze", project, shell), env, project)
        setup_smoke(bundle, project, env, work, shell)
        gui_smoke(bundle, project, env, work)
    assert_unchanged(project, before)


# {責務: [main: 空の探索先と導入コマンド監視下で配布物を検査する], 処理: [1: 配布物を別の場所へ複製する, 2: ホームと設定先を隔離して二種類の検査を実行する, 3: 呼び出し記録と書き換えを確認する], 引数: [], 戻り値: []}
def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--install-guard", required=True, type=Path)
    args = parser.parse_args()
    shell = os.environ.get("COMSPEC") if os.name == "nt" else shutil.which("sh")
    if args.full and not shell:
        parser.error("standard OS shell is required")
    with tempfile.TemporaryDirectory(prefix="acr-no-runtime-") as folder:
        work = Path(folder)
        bundle = work / "distribution"
        shutil.copytree(args.bundle.resolve(), bundle)
        original = snapshot(bundle)
        for phase in ("empty-path", "guarded-path"):
            case = work / phase
            case.mkdir()
            home, empty, temporary = [case / name for name in ("home", "empty", "tmp")]
            for path in (home, empty, temporary):
                path.mkdir()
            (home / "sentinel").write_text("must remain unchanged\n", encoding="utf-8")
            before = snapshot(home)
            env = dict(os.environ, PATH=str(empty), HOME=str(home), USERPROFILE=str(home),
                       XDG_CONFIG_HOME=str(home), XDG_CACHE_HOME=str(home), XDG_DATA_HOME=str(home),
                       XDG_STATE_HOME=str(home), APPDATA=str(home), LOCALAPPDATA=str(home),
                       TMPDIR=str(temporary), TMP=str(temporary), TEMP=str(temporary),
                       GOTOOLCHAIN="local", GOTELEMETRY="off")
            for key in ("PYTHONPATH", "PYTHONHOME", "GOROOT", "GOPATH", "NODE_PATH", "DOTNET_ROOT", "JAVA_HOME"):
                env.pop(key, None)
            for key in ("GOCACHE", "GOMODCACHE", "CARGO_HOME", "RUSTUP_HOME", "NPM_CONFIG_CACHE", "PIP_CACHE_DIR", "DOTNET_CLI_HOME", "NUGET_PACKAGES", "GRADLE_USER_HOME"):
                env[key] = str(home)
            log = case / "install-attempts.jsonl"
            if phase == "guarded-path":
                env = prepare_install_guard(args.install_guard.resolve(), case / "guards", log, env)
            try:
                exercise(bundle, args.full, env, case, shell, phase == "empty-path")
            finally:
                # 呼び出し側が失敗を握りつぶした場合も、導入コマンドの実行記録で検出する。
                assert_no_install_attempts(log)
                assert_unchanged(home, before)
                assert_unchanged(bundle, original)
        print(f"No-runtime {'Full Bundle' if args.full else 'CLI'} smoke and installation guard passed")


if __name__ == "__main__":
    main()
