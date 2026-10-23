"""公開入口の追加・削除・分類変更を登録検査が検出するか確認する。"""

import copy
import json
import tempfile
import unittest
from pathlib import Path

from entrypoint_inventory import discover, has_main_guard, unique_object, validate


# {責務: [EntrypointInventoryTests: 実装と登録一覧の食い違いを検出する], フィールド: [root: 検査対象, go_entries: Go探索の固定結果, manifest: 明示した期待一覧], 処理: [1: 最小の配布元を作る, 2: 変更ごとの検出結果を照合する]}
class EntrypointInventoryTests(unittest.TestCase):
    # {責務: [setUp: 入口と内部モジュールを区別できる固定入力を用意する], 処理: [1: 一時作業先を作る, 2: ソースと期待一覧を明示する], 引数: [], 戻り値: []}
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.write("tools/app/entry.py", 'if __name__ == "__main__":\n    pass\n')
        self.write("tools/app/helper.py", '# if __name__ == "__main__":\ndef helper():\n    pass\n')
        self.write("tools/run.sh", "#!/bin/sh\n")
        self.write("tools/run.bat", "@echo off\n")
        self.go_entries = [{"path": "tools/app/main.go", "commands": ["one"]}]
        self.manifest = {"schema_version": 1, "coverage": "inventory_only",
                         "python": ["tools/app/entry.py"], "internal_python": ["tools/app/helper.py"],
                         "shell": ["tools/run.bat", "tools/run.sh"], "go": {"tools/app/main.go": ["one"]}}

    # {責務: [write: 検査用のソースを保存する], 処理: [1: 親を作る, 2: 本文を保存する], 引数: [name: 相対位置, source: 本文], 戻り値: [1: 保存先]}
    def write(self, name, source):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(source, encoding="utf-8")
        return path

    # {責務: [test_matching_inventory_does_not_claim_io_coverage: 登録一致だけを確認し入出力検査済みと表現しない], 処理: [1: 実装を探索する, 2: 登録件数と未検査の範囲を照合する], 引数: [], 戻り値: []}
    def test_matching_inventory_does_not_claim_io_coverage(self):
        report = validate(self.manifest, discover(self.root, self.go_entries))
        self.assertEqual({"status": "inventory_ok", "io_coverage": "not_checked", "python": 1,
                          "internal_python": 1, "shell": 2, "go": 1, "go_commands": 1}, report)

    # {責務: [test_new_python_helpers_and_wrappers_are_rejected: 新しい入口や内部ファイルの登録漏れを検出する], 処理: [1: 三種類のファイルを順に追加する, 2: 未登録として拒否されることを確認する], 引数: [], 戻り値: []}
    def test_new_python_helpers_and_wrappers_are_rejected(self):
        for name, source in (("new.py", 'if __name__ == "__main__": pass\n'), ("internal.py", "pass\n"),
                             ("new.sh", ""), ("new.cmd", ""), ("new.ps1", ""), ("bin/new.py", "pass\n")):
            with self.subTest(name=name):
                path = self.write("tools/app/" + name, source)
                try:
                    with self.assertRaisesRegex(ValueError, "unregistered"):
                        validate(self.manifest, discover(self.root, self.go_entries))
                finally:
                    path.unlink()

    # {責務: [test_python_encoding_and_syntax_diagnostics: 文字コード宣言を尊重し壊れたソースの位置を示す], 処理: [1: UTF以外の宣言付きソースを読む, 2: 構文不正と文字コード不正の位置を照合する], 引数: [], 戻り値: []}
    def test_python_encoding_and_syntax_diagnostics(self):
        path = self.root / "tools/app/entry.py"
        path.write_bytes(b'# coding: latin-1\n# \xe9\nif __name__ == "__main__": pass\n')
        self.assertTrue(has_main_guard(path))
        for source in (b"if (", b"# coding: utf-8\n# \xff\n"):
            path.write_bytes(source)
            with self.subTest(source=source), self.assertRaises(SyntaxError) as error:
                has_main_guard(path)
            self.assertEqual(str(path), error.exception.filename)

    # {責務: [test_removal_and_classification_change_are_rejected: 削除と内部モジュールの公開化を検出する], 処理: [1: 起動条件を変えて検査する, 2: ファイルを削除して検査する], 引数: [], 戻り値: []}
    def test_removal_and_classification_change_are_rejected(self):
        path = self.write("tools/app/helper.py", 'if __name__ == "__main__": pass\n')
        with self.assertRaisesRegex(ValueError, "unregistered"):
            validate(self.manifest, discover(self.root, self.go_entries))
        path.unlink()
        with self.assertRaisesRegex(ValueError, "stale"):
            validate(self.manifest, discover(self.root, self.go_entries))

    # {責務: [test_go_entrypoint_and_alias_additions_are_rejected: Goの新しい実行入口と別名を検出する], 処理: [1: 探索結果へ入口と別名を順に追加する, 2: 登録違いとして拒否する], 引数: [], 戻り値: []}
    def test_go_entrypoint_and_alias_additions_are_rejected(self):
        additions = [self.go_entries + [{"path": "tools/new/entry.go", "commands": []}],
                     [{"path": "tools/app/main.go", "commands": ["one", "two"]}]]
        for entries in additions:
            with self.subTest(entries=entries), self.assertRaises(ValueError):
                validate(self.manifest, discover(self.root, entries))

    # {責務: [test_ambiguous_or_duplicate_registration_fails: 重複と不正な位置と過大な検証済み表現を拒否する], 処理: [1: 登録を不正な値へ変える, 2: 検査の失敗を照合する], 引数: [], 戻り値: []}
    def test_ambiguous_or_duplicate_registration_fails(self):
        changes = [{"python": ["tools/app/entry.py", "tools/app/entry.py"]},
                   {"go": {"tools/app/main.go": ["one", "one"]}},
                   {"python": ["tools/../app.py"]}, {"schema_version": True},
                   {"coverage": "io_complete"}, {"typo": []}]
        for change in changes:
            manifest = copy.deepcopy(self.manifest)
            manifest.update(change)
            with self.subTest(change=change), self.assertRaises(ValueError):
                validate(manifest, discover(self.root, self.go_entries))
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            json.loads('{"python": [], "python": []}', object_pairs_hook=unique_object)
        with self.assertRaises(ValueError):
            discover(self.root, [])

    # {責務: [test_main_guards_and_ignored_test_fixtures: 起動条件を構文で判定し試験用ソースを除外する], 処理: [1: 逆順の比較を確認する, 2: 文字列内の偽の条件を除く, 3: 試験用ファイルを加えても一覧が変わらないことを照合する], 引数: [], 戻り値: []}
    def test_main_guards_and_ignored_test_fixtures(self):
        path = self.write("tools/app/entry.py", 'if "__main__" == __name__ and True: pass\n')
        self.assertTrue(has_main_guard(path))
        helper = self.write("tools/app/helper.py", 'EXAMPLE = "if __name__ == \'__main__\': pass"\n')
        self.assertFalse(has_main_guard(helper))
        self.write("tools/app/tests/test_fake.py", 'if __name__ == "__main__": pass\n')
        self.write("tools/app/dist/generated.py", 'if __name__ == "__main__": pass\n')
        self.assertEqual("inventory_ok", validate(self.manifest, discover(self.root, self.go_entries))["status"])


if __name__ == "__main__":
    unittest.main()
