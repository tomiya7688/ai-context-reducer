#!/usr/bin/env python3
import argparse, json, os, shutil, subprocess
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
    walk_error_paths=[]
    def on_walk_error(error):
        path=getattr(error,'filename',None) or str(root)
        try: path=Path(path).relative_to(root).as_posix()
        except ValueError: path=str(path)
        walk_error_paths.append(path)
    for current,dirs,files in os.walk(root,onerror=on_walk_error):
        dirs[:]=[name for name in dirs if name.lower() not in IGNORE]
        for name in files:
            suffix=Path(name).suffix.lower()
            if suffix in LANG: found.add(LANG[suffix])
    return found, sorted(walk_error_paths)


# payload_incomplete は解析payloadの警告とtruncationを呼び出し側へ伝える。
def payload_incomplete(payload):
    if payload.get('status','ok') != 'ok' or payload.get('complete') is False:
        return True
    for key,value in payload.items():
        if key.endswith('_truncated') and value is True:
            return True
    for key in ('parse_error_count','read_error_count','walk_error_count','unsupported_input_count'):
        if isinstance(payload.get(key),int) and payload[key] > 0:
            return True
    return False

# main は指定rootの対応analyzerを実行し、各結果のpartial・failure statusを伝えます。
def main():
    ap=argparse.ArgumentParser(description='Run available shallow language analyzers and write full results to files.')
    ap.add_argument('root',nargs='?',default='.')
    ap.add_argument('--acr-root',default='.')
    ap.add_argument('--out',default='.acr/language')
    args=ap.parse_args()
    root=Path(args.root).resolve(); acr=Path(args.acr_root).resolve(); out=(root/args.out).resolve()
    if not root.exists():
        status='input_missing'
    elif not root.is_dir():
        status='input_not_directory'
    else:
        status=''
    if status:
        print(json.dumps({
            'tool':'language-run','status':status,'project_root':str(root),'output_directory':str(out),
            'results':[],'failure_count':1,'skip_count':0,
        },ensure_ascii=False,indent=2))
        raise SystemExit(2)
    py=shutil.which('python3') or shutil.which('python')
    languages,walk_error_paths=scan(root)
    results=[]
    for lang in ('python','csharp','c','cpp','gdscript'):
        if lang not in languages: continue
        tool,rel=SCRIPTS[lang]; script=acr/rel
        if not py or not script.exists():
            results.append({'tool_path':tool,'status':'skipped','error':'python runtime or analyzer script unavailable'})
            continue
        proc=subprocess.run([py,str(script),str(root)],text=True,capture_output=True)
        if proc.returncode:
            results.append({'tool_path':tool,'status':'failed','error':proc.stderr[-1200:]})
            continue
        try:
            payload=json.loads(proc.stdout)
            if not isinstance(payload,dict): raise ValueError('analyzer output must be a JSON object')
        except (json.JSONDecodeError,ValueError) as error:
            results.append({'tool_path':tool,'status':'failed','error':f'invalid analyzer JSON: {error}'})
            continue
        out.mkdir(parents=True,exist_ok=True); target=out/(tool.replace('/','_').replace('-','_')+'.json')
        target.write_text(proc.stdout,encoding='utf-8')
        row_status=payload.get('status','ok')
        if row_status=='ok' and payload_incomplete(payload): row_status='ok_with_warnings'
        row={'tool_path':tool,'status':row_status,'backend':'python','output_path':str(target)}
        for key in ('parse_error_count','read_error_count','walk_error_count','unsupported_input_count'):
            if isinstance(payload.get(key),int): row[key]=payload[key]
        results.append(row)
    if 'go' in languages:
        results.append({'tool_path':'go/small/go-symbols','status':'skipped','error':'use native language-run for standalone Go binary/go-run resolution'})
    failures=sum(r['status'] in ('failed','write_failed') for r in results)
    skips=sum(r['status']=='skipped' for r in results)
    warnings=sum(r['status'] not in ('ok','failed','write_failed','skipped') for r in results)
    status='ok_with_failures' if failures else 'ok_with_warnings' if warnings or walk_error_paths else 'ok_with_skips' if skips else 'ok'
    print(json.dumps({'tool':'language-run','status':status,'project_root':str(root),'output_directory':str(out),'results':results,'failure_count':failures,'skip_count':skips,'warning_count':warnings+len(walk_error_paths),'walk_error_count':len(walk_error_paths),'walk_error_paths':walk_error_paths},ensure_ascii=False,indent=2))
    raise SystemExit(1 if failures else 0)

if __name__=='__main__': main()
