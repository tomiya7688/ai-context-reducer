#!/usr/bin/env python3
import argparse,fnmatch,json,re,sys
from pathlib import Path

IGNORE={'.git','.hg','.svn','.venv','venv','node_modules','bin','obj','build','dist','__pycache__','.godot','.idea','.vs','vendor'}

# globmatch はこのtool内の処理責務を局所化し、呼び出し側の理解負債を増やさない。
def globmatch(path,pat):
    path=path.replace('\\','/')
    if fnmatch.fnmatchcase(path,pat): return True
    if pat.endswith('/**') and (path==pat[:-3] or path.startswith(pat[:-2])): return True
    return False

# suppression はこのtool内の処理責務を局所化し、呼び出し側の理解負債を増やさない。
def suppression(line,rid):
    marker=f'acr-ignore {rid}'
    i=line.find(marker)
    if i<0:return None,False
    tail=line[i+len(marker):].strip()
    if tail.startswith(':') and tail[1:].strip(): return tail[1:].strip(),True
    return '',True

# main はCLI入力を解釈し、自己説明的な出力と終了状態を確定する。
def main():
    ap=argparse.ArgumentParser(description='Lightweight path-scoped policy checker.')
    ap.add_argument('root',nargs='?',default='.')
    ap.add_argument('--rules',required=True)
    ap.add_argument('--max-findings',type=int,default=100)
    a=ap.parse_args()
    root=Path(a.root).resolve()
    try: cfg=json.loads(Path(a.rules).read_text(encoding='utf-8'))
    except Exception as e:
        print(json.dumps({'tool':'policy-check','status':'rules_unavailable','rules_path':a.rules,'error':str(e)},indent=2));return 2
    findings=[];supp=[];bad_supp=[];unsupported=[];rule_errors=[];read_errors=[];files_scanned=0;checked=0
    files=[p for p in root.rglob('*') if p.is_file() and not any(part.lower() in IGNORE for part in p.parts)]
    for rule in cfg.get('rules',[]):
        rid=rule.get('id',''); forbid=rule.get('forbid',''); require=rule.get('require','')
        sev=rule.get('severity','error');mode=rule.get('mode','literal')
        if not rid or bool(forbid)==bool(require):
            rule_errors.append({'rule_id':rid,'error':'rule requires id and exactly one of forbid/require'});continue
        if sev not in ('error','warning'):
            rule_errors.append({'rule_id':rid,'error':'severity must be error or warning'});continue
        if rule.get('semantic'):
            unsupported.append({'rule_id':rid,'reason':'semantic rule requires AST/semantic backend'});continue
        try:
            rx=re.compile(forbid or require) if mode=='regex' else None
            if mode not in ('literal','regex'): raise ValueError(f'unsupported mode {mode}')
        except Exception as e:
            rule_errors.append({'rule_id':rid,'error':str(e)});continue
        checked+=1
        for p in files:
            rel=p.relative_to(root).as_posix()
            paths=rule.get('paths') or []
            exc=rule.get('exclude') or []
            if paths and not any(globmatch(rel,x) for x in paths):continue
            if exc and any(globmatch(rel,x) for x in exc):continue
            try: lines=p.read_text(encoding='utf-8',errors='replace').splitlines()
            except Exception: read_errors.append(rel);continue
            files_scanned+=1
            match=lambda s: bool(rx.search(s)) if rx else (forbid or require) in s
            if forbid:
                for i,line in enumerate(lines):
                    if not match(line):continue
                    reason,marked=suppression(line,rid)
                    if not marked and i>0: reason,marked=suppression(lines[i-1],rid)
                    if marked:
                        if reason:
                            supp.append({'rule_id':rid,'path':rel,'line':i+1,'reason':reason});continue
                        bad_supp.append({'rule_id':rid,'path':rel,'line':i+1,'reason':'suppression requires non-empty reason'})
                    findings.append({'rule_id':rid,'severity':sev,'path':rel,'line':i+1,'kind':'forbidden_pattern','message':rule.get('message') or 'forbidden pattern matched','match':line.strip()})
            elif not any(match(line) for line in lines):
                findings.append({'rule_id':rid,'severity':sev,'path':rel,'kind':'required_pattern_missing','message':rule.get('message') or 'required pattern missing'})
    findings.sort(key=lambda x:(x['path'],x.get('line',0)))
    total=len(findings);limit=max(0,a.max_findings);truncated=bool(limit and total>limit)
    errors=sum(x['severity']=='error' for x in findings);warnings=sum(x['severity']=='warning' for x in findings)
    if truncated:findings=findings[:limit]
    status='violations' if errors else 'partial' if rule_errors or read_errors else 'ok'
    print(json.dumps({'tool':'policy-check','status':status,'root_path':str(root),'rules_path':a.rules,'rules_total':len(cfg.get('rules',[])),'rules_checked':checked,'files_scanned':files_scanned,'finding_count_total':total,'error_count':errors,'warning_count':warnings,'findings':findings,'findings_truncated':truncated,'suppressions':supp,'invalid_suppressions':bad_supp,'unsupported_rules':unsupported,'rule_errors':rule_errors,'read_error_paths':sorted(set(read_errors))},ensure_ascii=False,indent=2))
    return 1 if errors else 2 if rule_errors else 0
if __name__=='__main__':sys.exit(main())
