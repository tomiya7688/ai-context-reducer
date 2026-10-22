"""Regression checks for installation traps and filesystem monitoring."""

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from runtime_guard import INSTALL_COMMANDS, assert_no_install_attempts, assert_unchanged, prepare_install_guard, snapshot
from runtime_smoke import main


# {責務: [RuntimeGuardTests: 導入呼び出しと想定外の書き換えを検出する検査自体を検証する], フィールド: [root: 一時作業先, binary: 検査専用の実行ファイル], 処理: [1: 各試験専用の場所を作る, 2: 拒否と記録と変更検出を確かめる]}
class RuntimeGuardTests(unittest.TestCase):
    # {責務: [setUp: 試験ごとに監視用の場所と実行ファイルを取得する], 処理: [1: 一時作業先を作る, 2: 環境で指定された検査用実行ファイルを取得する], 引数: [], 戻り値: []}
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.binary = Path(os.environ["ACR_TEST_INSTALL_GUARD"]).resolve()

    # {責務: [test_every_installer_records_attempts: 導入に失敗しても呼び出した事実を記録することを確認する], 処理: [1: 全コマンドの事前確認を行う, 2: 各コマンドを呼んで終了コードと記録を確かめる], 引数: [], 戻り値: []}
    def test_every_installer_records_attempts(self):
        guards, log = self.root / "guards", self.root / "attempts.jsonl"
        env = prepare_install_guard(self.binary, guards, log, os.environ)
        assert_no_install_attempts(log)
        suffix = ".exe" if os.name == "nt" else ""
        for command in INSTALL_COMMANDS:
            result = subprocess.run([str(guards / (command + suffix)), "install", "fixture"],
                                    env=env, capture_output=True, timeout=10)
            self.assertEqual(97, result.returncode, command)
            with self.assertRaisesRegex(RuntimeError, "installation command attempted"):
                assert_no_install_attempts(log)
            self.assertIn(command, log.read_text(encoding="utf-8"))
            log.unlink()

    # {責務: [test_guard_cannot_succeed_without_log: 記録不能を成功と誤認しないことを確認する], 処理: [1: 存在しない親を記録先に指定する, 2: 異常終了を確かめる], 引数: [], 戻り値: []}
    def test_guard_cannot_succeed_without_log(self):
        env = dict(os.environ, ACR_INSTALL_GUARD_LOG=str(self.root / "missing/log"))
        result = subprocess.run([str(self.binary)], env=env, capture_output=True, timeout=10)
        self.assertEqual(98, result.returncode)

    # {責務: [test_file_and_empty_directory_changes_are_detected: 同じ大きさの書き換え・削除・追加を検出する], 処理: [1: 変更前を記録する, 2: 各種類の変更を加え検出を確かめる], 引数: [], 戻り値: []}
    def test_file_and_empty_directory_changes_are_detected(self):
        for change in ("rewrite", "delete", "new-file", "new-directory"):
            with self.subTest(change=change):
                target = self.root / change
                target.mkdir()
                source = target / ".config"
                source.write_text("before", encoding="utf-8")
                before = snapshot(target)
                assert_unchanged(target, before)
                if change == "rewrite":
                    source.write_text("after!", encoding="utf-8")
                elif change == "delete":
                    source.unlink()
                elif change == "new-file":
                    (target / "extra").write_text("", encoding="utf-8")
                else:
                    (target / "empty").mkdir()
                with self.assertRaisesRegex(RuntimeError, "unexpected filesystem changes"):
                    assert_unchanged(target, before)

    # {責務: [test_missing_guard_is_not_silently_skipped: 監視用実行ファイルがなくても合格しないことを確認する], 処理: [1: 存在しない実行ファイルを渡す, 2: 配置の失敗を確かめる], 引数: [], 戻り値: []}
    def test_missing_guard_is_not_silently_skipped(self):
        with self.assertRaises(OSError):
            prepare_install_guard(self.root / "missing", self.root / "guards", self.root / "log", os.environ)

    # {責務: [test_gate_rejects_swallowed_installer_failure: 呼び出し側が導入失敗を無視しても検査全体を失敗にする], 処理: [1: 正常終了を装う処理へ差し替える, 2: 監視下で導入コマンドを呼ぶ, 3: 最後の記録確認で拒否することを確かめる], 引数: [], 戻り値: []}
    def test_gate_rejects_swallowed_installer_failure(self):
        bundle = self.root / "bundle"
        bundle.mkdir()

        # {責務: [swallow_failure: 監視下だけで導入コマンドを呼び失敗を無視する], 処理: [1: 呼び出し記録先のある環境で実行する], 引数: [bundle: 配布先, full: 同梱版か, env: 隔離環境, work: 記録先, shell: 標準シェル, empty_path: 空の探索先か], 戻り値: []}
        def swallow_failure(bundle, full, env, work, shell, empty_path):
            if not empty_path:
                name = "npm.exe" if os.name == "nt" else "npm"
                subprocess.run([str(Path(env["PATH"]) / name), "install", "fixture"], env=env,
                               capture_output=True, timeout=10)

        argv = ["runtime_smoke.py", str(bundle), "--install-guard", str(self.binary)]
        with mock.patch.object(sys, "argv", argv), mock.patch("runtime_smoke.exercise", side_effect=swallow_failure):
            with self.assertRaisesRegex(RuntimeError, "installation command attempted"):
                main()


if __name__ == "__main__":
    unittest.main()
