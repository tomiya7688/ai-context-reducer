#!/usr/bin/env python3
import contextlib
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path

SCRIPT=Path(__file__).resolve().parents[1]/"script"/"policy_check.py"
SPEC=importlib.util.spec_from_file_location("policy_check_under_test",SCRIPT)
POLICY_CHECK=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(POLICY_CHECK)

class PolicyCheckTests(unittest.TestCase):
    # run_tool は一時rules fileを用意してpolicy CLIを実行し、exit statusを返します。
    def run_tool(self, root, rules):
        rules_path=Path(root)/"rules.json"
        rules_path.write_text(json.dumps({"rules":rules}),encoding="utf-8")
        return subprocess.run([sys.executable,str(SCRIPT),"--rules",str(rules_path),str(root)],text=True,capture_output=True)

    # test_path_scope_and_suppression はpath rule適用とfile内suppressionが違反判定を変えることを確認します。
    def test_path_scope_and_suppression(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/"src/ui").mkdir(parents=True)
            (root/"src/core").mkdir(parents=True)
            (root/"src/ui/a.py").write_text("# acr-ignore POL001: reviewed exception\nPath.write_text('x')\n",encoding="utf-8")
            (root/"src/core/b.py").write_text("Path.write_text('x')\n",encoding="utf-8")
            p=self.run_tool(root,[{"id":"POL001","paths":["src/ui/**"],"severity":"error","forbid":"Path.write_text("}])
            self.assertEqual(p.returncode,0,p.stderr+p.stdout)
            out=json.loads(p.stdout)
            self.assertEqual(out["error_count"],0)
            self.assertEqual(len(out["suppressions"]),1)

    # test_violation_exit_one はerror severityの違反をCLIがexit code 1で返すことを確認します。
    def test_violation_exit_one(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/"a.txt").write_text("forbidden\n",encoding="utf-8")
            p=self.run_tool(root,[{"id":"POL002","paths":["*.txt"],"severity":"error","forbid":"forbidden"}])
            self.assertEqual(p.returncode,1)
            self.assertEqual(json.loads(p.stdout)["status"],"violations")

    # test_warning_and_semantic_rule はwarning ruleと意味検査ruleが別severityで出ることを確認します。
    def test_warning_and_semantic_rule(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/"a.txt").write_text("hello\n",encoding="utf-8")
            p=self.run_tool(root,[
                {"id":"POL003","paths":["*.txt"],"severity":"warning","require":"required"},
                {"id":"POL004","paths":["*.txt"],"severity":"error","forbid":"x","semantic":True},
            ])
            self.assertEqual(p.returncode,0,p.stderr+p.stdout)
            out=json.loads(p.stdout)
            self.assertEqual(out["warning_count"],1)
            self.assertEqual(out["unsupported_rules"][0]["rule_id"],"POL004")

    # test_invalid_roots_fail はmissing rootとfile rootをclean成功にしない。
    def test_invalid_roots_fail(self):
        with tempfile.TemporaryDirectory() as td:
            parent=Path(td)
            rules_path=parent/"rules.json"
            rules_path.write_text(json.dumps({"rules":[{"id":"POL005","forbid":"x"}]}),encoding="utf-8")
            missing=parent/"missing"
            result=subprocess.run([sys.executable,str(SCRIPT),"--rules",str(rules_path),str(missing)],text=True,capture_output=True)
            self.assertEqual(result.returncode,2,result.stdout+result.stderr)
            self.assertEqual(json.loads(result.stdout)["status"],"input_missing")

            file_root=parent/"root.txt"
            file_root.write_text("content",encoding="utf-8")
            result=subprocess.run([sys.executable,str(SCRIPT),"--rules",str(rules_path),str(file_root)],text=True,capture_output=True)
            self.assertEqual(result.returncode,2,result.stdout+result.stderr)
            self.assertEqual(json.loads(result.stdout)["status"],"input_not_directory")

    # test_nested_walk_failure_marks_partial は走査失敗と併存する違反を保持する。
    def test_nested_walk_failure_marks_partial(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/"a.txt").write_text("forbidden\n",encoding="utf-8")
            rules_path=root/"rules.json"
            rules_path.write_text(json.dumps({"rules":[{"id":"POL006","forbid":"forbidden"}]}),encoding="utf-8")

            # failed_walk は走査中のpermission errorを再現する。
            def failed_walk(path,topdown=True,onerror=None):
                yield str(path),[],["a.txt"]
                onerror(PermissionError(13,"permission denied",str(Path(path)/"unreadable")))

            output=io.StringIO()
            with mock.patch.object(POLICY_CHECK.os,"walk",failed_walk),contextlib.redirect_stdout(output):
                code=POLICY_CHECK.main(["--rules",str(rules_path),str(root)])
            result=json.loads(output.getvalue())
            self.assertEqual(code,1)
            self.assertEqual(result["status"],"violations")
            self.assertEqual(result["error_count"],1)
            self.assertEqual(result["walk_error_count"],1)
            self.assertEqual(result["walk_error_paths"],["unreadable"])

            (root/"a.txt").write_text("clean\n",encoding="utf-8")
            output=io.StringIO()
            with mock.patch.object(POLICY_CHECK.os,"walk",failed_walk),contextlib.redirect_stdout(output):
                code=POLICY_CHECK.main(["--rules",str(rules_path),str(root)])
            result=json.loads(output.getvalue())
            self.assertEqual(code,2)
            self.assertEqual(result["status"],"partial")
            self.assertEqual(result["walk_error_count"],1)

if __name__=="__main__":
    unittest.main()
