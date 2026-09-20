#!/usr/bin/env python3
import argparse
import json
import shutil
from collections import Counter
from pathlib import Path

IGNORE={'.git','.hg','.svn','.venv','venv','node_modules','bin','obj','build','dist','__pycache__','.godot','.idea','.vs','vendor'}
LANG={'.py':'python','.cs':'csharp','.go':'go','.c':'c','.h':'c','.cpp':'cpp','.cc':'cpp','.cxx':'cpp','.hpp':'cpp','.hh':'cpp','.gd':'gdscript'}
RUNTIME={
    'python':('python3','python'),'csharp':('dotnet',),'go':('go',),
    'c':('gcc','clang','cc'),'cpp':('g++','clang++','c++'),'gdscript':('godot4','godot')
}
TOOLS={
    'python':('python/small/python-symbols','python/medium/python-import-map','python/large/python-module-graph'),
    'csharp':('csharp/small/csharp-symbols','csharp/medium/csharp-project-map','csharp/large/csharp-project-graph'),
    'go':('go/small/go-symbols','go/medium/go-import-map','go/large/go-package-graph'),
    'c':('c/small/c-symbols','c/medium/c-include-map','c/large/c-include-graph'),
    'cpp':('cpp/small/cpp-symbols','cpp/medium/cpp-include-map','cpp/large/cpp-include-graph'),
    'gdscript':('gdscript/small/gdscript-symbols','gdscript/medium/gdscript-dependency-map','gdscript/large/godot-scene-graph'),
}

# first はこのtool内の処理責務を局所化し、呼び出し側の理解負債を増やさない。
def first(names):
    for n in names:
        p=shutil.which(n)
        if p: return p
    return ''

# walk は対象scopeを調べ、routingに必要な情報だけを集める。
def walk(root):
    for p in root.rglob('*'):
        if any(part.lower() in IGNORE for part in p.parts):
            continue
        if p.is_file():
            yield p

# main はCLI入力を解釈し、自己説明的な出力と終了状態を確定する。
def main():
    ap=argparse.ArgumentParser(description='Select compatible language-specific tools from repository language + environment.')
    ap.add_argument('root',nargs='?',default='.')
    ap.add_argument('--run-small',action='store_true')
    args=ap.parse_args()
    root=Path(args.root).resolve()
    if not root.is_dir():
        print(json.dumps({'tool':'language-setup','status':'input_not_directory','project_root':str(root)},ensure_ascii=False,indent=2))
        raise SystemExit(2)
    files=list(walk(root))
    counts=Counter(LANG[p.suffix.lower()] for p in files if p.suffix.lower() in LANG)
    size='large' if len(files)>=2000 else 'medium' if len(files)>=200 else 'small'
    runtime={k:first(v) for k,v in RUNTIME.items()}
    enabled=[]; skipped=[]
    for lang,count in counts.most_common():
        if lang not in TOOLS:
            skipped.append({'language':lang,'file_count':count,'reason':'no bundled language-specific tool group'})
            continue
        if not runtime.get(lang):
            skipped.append({'language':lang,'file_count':count,'reason':'matching runtime/compiler unavailable; dependencies are not auto-installed'})
            continue
        names=TOOLS[lang]
        enabled.append({'tool_path':names[0],'level':'small','enabled':True,'reason':'source detected and matching runtime/compiler available'})
        if size in {'medium','large'}:
            enabled.append({'tool_path':names[1],'level':'medium','enabled':True,'reason':'repository size may justify dependency/project mapping'})
        if size=='large':
            enabled.append({'tool_path':names[2],'level':'large','enabled':True,'reason':'large repository may justify bounded graph analysis'})
    run=[x['tool_path'] for x in enabled if args.run_small and x['level']=='small']
    print(json.dumps({
        'tool':'language-setup','status':'ok','project_root':str(root),'project_size_class':size,
        'language_file_counts':dict(counts),'runtime_commands':runtime,'enabled_tools':enabled,
        'skipped_languages':skipped,'run_small_requested':args.run_small,'small_tools_to_run':run,
        'policy':'do not install missing runtimes; enable only language tools supported by the existing environment'
    },ensure_ascii=False,indent=2))

if __name__=='__main__': main()
