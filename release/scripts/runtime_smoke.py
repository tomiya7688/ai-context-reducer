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


# {責務: [run_json: 同梱バイナリの終了状態とJSONを検証する], 引数: [args: コマンド, env: 隔離環境, cwd: 作業先], 戻り値: [data: JSON]}
def run_json(args, env, cwd):
    result = subprocess.run(args, env=env, cwd=cwd, capture_output=True, text=True, timeout=30)
    if result.returncode != 0 or result.stderr.strip():
        raise RuntimeError(f"packaged command failed: {args[0]} code={result.returncode}: {result.stderr}")
    return json.loads(result.stdout)


# {責務: [gui_smoke: 同梱GUI経由で本物のCLIと拒否条件を確認する], 引数: [bundle: 配布先, project: fixture, env: 隔離環境, work: 記録先], 戻り値: [なし]}
def gui_smoke(bundle, project, env, work):
    suffix = ".exe" if os.name == "nt" else ""
    binary = bundle / "gui" / ("acr-hub" + suffix)
    # The GUI must be in the archive; never inject a build-directory binary.
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


# {責務: [main: 空PATHと隔離ホームで配布物だけを実行する], 戻り値: [なし]}
def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--full", action="store_true")
    args = parser.parse_args()
    bundle = args.bundle.resolve()
    shell = os.environ.get("COMSPEC") if os.name == "nt" else shutil.which("sh")
    with tempfile.TemporaryDirectory(prefix="acr-no-runtime-") as folder:
        work = Path(folder)
        project, home, empty = [work / name for name in ("project", "home", "empty-path")]
        for path in (project, home, empty):
            path.mkdir()
        (project / "README.md").write_text("# Fixture\n", encoding="utf-8")
        (project / "sample.py").write_text("def example():\n    return 1\n", encoding="utf-8")
        env = dict(os.environ, PATH=str(empty), HOME=str(home), USERPROFILE=str(home),
                   XDG_CONFIG_HOME=str(home), GOTOOLCHAIN="local", GOTELEMETRY="off")
        suffix = ".exe" if os.name == "nt" else ""
        binary = str(bundle / ("acr-toolbox" + suffix))
        for command in ("version", "env", "language-env"):
            run_json([binary, command], env, project)
        for command in ("analyze", "stats", "language-setup"):
            run_json([binary, command, str(project)], env, project)
        if args.full:
            name = "analyze.bat" if os.name == "nt" else "analyze.sh"
            command = [shell, "/d", "/c", str(bundle / name), str(project)] if os.name == "nt" else [shell, str(bundle / name), str(project)]
            run_json(command, env, project)
            name = "setup.bat" if os.name == "nt" else "setup.sh"
            command = [shell, "/d", "/c", str(bundle / name), str(project)] if os.name == "nt" else [shell, str(bundle / name), str(project)]
            result = subprocess.run(command, env=env, cwd=project, capture_output=True, text=True, timeout=30)
            if result.returncode != 0 or result.stderr.strip():
                raise RuntimeError(f"packaged setup failed: {result.returncode}: {result.stderr}")
            decoder, remaining, reports = json.JSONDecoder(), result.stdout.strip(), []
            while remaining:
                report, end = decoder.raw_decode(remaining)
                reports.append(report)
                remaining = remaining[end:].strip()
            if len(reports) != 5:
                raise RuntimeError("packaged setup omitted an operation")
            gui_smoke(bundle, project, env, work)
        if list(home.rglob("*")):
            raise RuntimeError("distribution modified the isolated user home")
        print(f"No-runtime {'Full Bundle' if args.full else 'CLI'} smoke passed")


if __name__ == "__main__":
    main()
