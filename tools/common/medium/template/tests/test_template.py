#!/usr/bin/env python3
import json,subprocess,sys,tempfile,unittest
from pathlib import Path

SCRIPT=Path(__file__).resolve().parents[1]/"script"/"template.py"

class TemplateTests(unittest.TestCase):
    def run_tool(self,*args):
        return subprocess.run([sys.executable,str(SCRIPT),*map(str,args)],text=True,capture_output=True)
    def test_generate_check_and_drift(self):
        with tempfile.TemporaryDirectory() as td:
            r=Path(td);tpl=r/"tpl.txt";vars=r/"vars.json";out=r/"out.txt"
            tpl.write_text("Hello {{name}}\n",encoding="utf-8");vars.write_text('{"name":"World"}\n',encoding="utf-8")
            base=["--template",tpl,"--vars",vars,"--out",out,"--required","name","--template-id","hello","--template-version","1"]
            p=self.run_tool(*base);self.assertEqual(p.returncode,0,p.stderr+p.stdout);self.assertEqual(out.read_text(),"Hello World\n")
            self.assertEqual(self.run_tool(*base,"--check").returncode,0)
            vars.write_text('{"name":"Other"}\n',encoding="utf-8")
            self.assertEqual(self.run_tool(*base,"--check").returncode,1)
    def test_required_and_directory_dry_run(self):
        with tempfile.TemporaryDirectory() as td:
            r=Path(td);tpl=r/"tpl";tpl.mkdir();(tpl/"a.txt").write_text("{{name}}\n",encoding="utf-8");vars=r/"vars.json";out=r/"out"
            vars.write_text("{}\n",encoding="utf-8")
            self.assertEqual(self.run_tool("--template",tpl,"--vars",vars,"--out",out,"--required","name").returncode,2)
            vars.write_text('{"name":"ok"}\n',encoding="utf-8")
            self.assertEqual(self.run_tool("--template",tpl,"--vars",vars,"--out",out,"--dry-run").returncode,0)
            self.assertFalse(out.exists())
if __name__=="__main__":unittest.main()
