#!/usr/bin/env python3
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT=Path(__file__).resolve().parents[1]/"script"/"policy_check.py"

class PolicyCheckTests(unittest.TestCase):
    def run_tool(self, root, rules):
        rules_path=Path(root)/"rules.json"
        rules_path.write_text(json.dumps({"rules":rules}),encoding="utf-8")
        return subprocess.run([sys.executable,str(SCRIPT),"--rules",str(rules_path),str(root)],text=True,capture_output=True)

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

    def test_violation_exit_one(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/"a.txt").write_text("forbidden\n",encoding="utf-8")
            p=self.run_tool(root,[{"id":"POL002","paths":["*.txt"],"severity":"error","forbid":"forbidden"}])
            self.assertEqual(p.returncode,1)
            self.assertEqual(json.loads(p.stdout)["status"],"violations")

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

if __name__=="__main__":
    unittest.main()
