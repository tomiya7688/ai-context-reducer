#!/usr/bin/env python3
import argparse,json
from pathlib import Path

SIGNALS={
 'game': {'project.godot','Assets','Scenes','engine','game'},
 'gui': {'ui','views','widgets','forms','xaml'},
 'compiler': {'lexer','parser','ast','compiler','interpreter','bytecode'},
 'data-tool': {'data','etl','dataset','converter','export','importer'},
 'packaged-app': {'installer','package','dist','release','publish'},
 'simulation': {'simulation','sim','physics','random','seed','eval'},
 'rule-heavy': {'rules','specification','protocol','legal','validation'},
}
RECOMMEND={
 'game':['Validation Routing','headless-first','visual confirmation','deterministic seam'],
 'gui':['Validation Routing','headless-first','visual confirmation'],
 'compiler':['Change Routing Map','Source Structure Index','targeted regression tests'],
 'data-tool':['dry-run','disposable workspace','generated-data consistency'],
 'packaged-app':['artifact-boundary validation','artifact smoke'],
 'simulation':['fixed inputs/seed','deterministic seam','structured observation'],
 'rule-heavy':['Policy Routing','Responsibility Map','targeted policy checks'],
}

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('root',nargs='?',default='.'); a=ap.parse_args(); root=Path(a.root).resolve(); names=set()
 for p in root.rglob('*'):
  try: rel=p.relative_to(root)
  except ValueError: continue
  names.update(part.lower() for part in rel.parts)
 found=[]
 for typ,sigs in SIGNALS.items():
  score=sum(1 for s in sigs if s.lower() in names)
  if score: found.append({'type':typ,'score':score,'recommend':RECOMMEND[typ]})
 found.sort(key=lambda x:(-x['score'],x['type']))
 print(json.dumps({'root':root.name,'project_types':found},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
