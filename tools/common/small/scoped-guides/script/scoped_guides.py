#!/usr/bin/env python3
import argparse,json
from pathlib import Path

DEFAULT=["AI_CONTEXT.md","AI_CONTEXT.local.md","AGENTS.md","CLAUDE.md"]

# main はCLI入力を解釈し、自己説明的な出力と終了状態を確定する。
def main():
    ap=argparse.ArgumentParser(description="Resolve scoped AI guide candidates on the target ancestor path.")
    ap.add_argument("target",nargs="?",default=".")
    ap.add_argument("root",nargs="?",default=".")
    ap.add_argument("--name",action="append",dest="names")
    a=ap.parse_args()
    root=Path(a.root).resolve(); target=Path(a.target).resolve()
    if not root.is_dir():
        print(json.dumps({"tool":"scoped-guides","status":"input_unavailable","root_path":str(root)},indent=2)); raise SystemExit(2)
    try: target.relative_to(root)
    except ValueError:
        print(json.dumps({"tool":"scoped-guides","status":"target_outside_root","root_path":str(root),"target_path":str(target)},indent=2)); raise SystemExit(2)
    d=target if target.is_dir() else target.parent
    chain=[]
    while True:
        chain.append(d)
        if d==root: break
        d=d.parent
    chain.reverse()
    guides=[]; seen=set(); names=a.names or DEFAULT
    for depth,d in enumerate(chain):
        for name in names:
            p=d/name
            if p in seen or not p.is_file(): continue
            seen.add(p)
            scope=d.relative_to(root).as_posix()
            guides.append({"path":p.relative_to(root).as_posix(),"scope":"" if scope=="." else scope,"depth":depth,"reason":"guide is on the ancestor path from repository root to target"})
    print(json.dumps({"tool":"scoped-guides","status":"ok","root_path":str(root),"target_path":str(target),"guide_names":names,"guides":guides,"guide_count":len(guides),"precedence_defined":False,"policy":"filesystem scope resolver only; agent-specific instruction precedence is not inferred"},ensure_ascii=False,indent=2))
if __name__=="__main__": main()
