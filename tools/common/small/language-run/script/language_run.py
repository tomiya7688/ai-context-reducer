#!/usr/bin/env python3
import argparse, json, shutil, subprocess
from pathlib import Path

LANG={'.py':'python','.cs':'csharp','.go':'go','.c':'c','.h':'c','.cpp':'cpp','.cc':'cpp','.cxx':'cpp','.hpp':'cpp','.hh':'cpp','.gd':'gdscript'}
IGNORE={'.git','.hg','.svn','.venv','venv','node_modules','bin','obj','build','dist','__pycache__','.godot','.idea','.vs','vendor'}
SCRIPTS={
 'python':('python/small/python-symbols','tools/python/small/python-symbols/script/python_symbols.py'),
 'csharp':('csharp/small/csharp-symbols','tools/csharp/small/csharp-symbols/script/csharp_symbols.py'),
 'c':('c/small/c-symbols','tools/c/small/c-symbols/script/c_symbols.py'),
 'cpp':('cpp/small/cpp-symbols','tools/cpp/small/cpp-symbols/script/cpp_symbols.py'),
 'gdscript':('gdscript/small/gdscript-symbols','tools/gdscript/small/gdscript-symbols/script/gdscript_symbols.py'),
}

# scan は対象scopeを調べ、routingに必要な情報だけを集める。
def scan(root):
    found=set()
    for p in root.rglob('*'):
        if any(x.lower() in IGNORE for x in p.parts): continue
        if p.is_file() and p.suffix.lower() in LANG: found.add(LANG[p.suffix.lower()])
    return found

# main はCLI入力を解釈し、自己説明的な出力と終了状態を確定する。
def main():
    ap=argparse.ArgumentParser(description='Run available shallow language analyzers and write full results to files.')
    ap.add_argument('root',nargs='?',default='.')
    ap.add_argument('--acr-root',default='.')
    ap.add_argument('--out',default='.acr/language')
    args=ap.parse_args()
    root=Path(args.root).resolve(); acr=Path(args.acr_root).resolve(); out=(root/args.out).resolve()
    py=shutil.which('python3') or shutil.which('python')
    results=[]
    for lang in ('python','csharp','c','cpp','gdscript'):
        if lang not in scan(root): continue
        tool,rel=SCRIPTS[lang]; script=acr/rel
        if not py or not script.exists():
            results.append({'tool_path':tool,'status':'skipped','error':'python runtime or analyzer script unavailable'})
            continue
        proc=subprocess.run([py,str(script),str(root)],text=True,capture_output=True)
        if proc.returncode:
            results.append({'tool_path':tool,'status':'failed','error':proc.stderr[-1200:]})
            continue
        out.mkdir(parents=True,exist_ok=True); target=out/(tool.replace('/','_').replace('-','_')+'.json')
        target.write_text(proc.stdout,encoding='utf-8')
        results.append({'tool_path':tool,'status':'ok','backend':'python','output_path':str(target)})
    if 'go' in scan(root):
        results.append({'tool_path':'go/small/go-symbols','status':'skipped','error':'use native language-run for standalone Go binary/go-run resolution'})
    failures=sum(r['status']=='failed' for r in results); skips=sum(r['status']=='skipped' for r in results)
    print(json.dumps({'tool':'language-run','status':'ok_with_failures' if failures else 'ok_with_skips' if skips else 'ok','project_root':str(root),'output_directory':str(out),'results':results,'failure_count':failures,'skip_count':skips},ensure_ascii=False,indent=2))
    raise SystemExit(1 if failures else 0)

if __name__=='__main__': main()
