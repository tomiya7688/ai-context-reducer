#!/usr/bin/env python3
import argparse,hashlib,json,shutil,sys
from pathlib import Path
import re

RX=re.compile(r'\{\{\s*([A-Za-z_][A-Za-z0-9_.-]*)\s*\}\}')

# scalar はこのtool内の処理責務を局所化し、呼び出し側の理解負債を増やさない。
def scalar(v):
    if v is None:return ''
    if isinstance(v,bool):return 'true' if v else 'false'
    if isinstance(v,(str,int,float)):return str(v)
    raise TypeError

# render は内部結果を安定した利用者向け表現へ変換する。
def render(data,vars):
    text=data.decode('utf-8')
    text=RX.sub(lambda m:vars.get(m.group(1),m.group(0)),text)
    return text.encode('utf-8'),sorted(set(RX.findall(text)))

# diff_hint はこのtool内の処理責務を局所化し、呼び出し側の理解負債を増やさない。
def diff_hint(old,new):
    if old==new:return None
    a=old.decode('utf-8','replace').replace('\r\n','\n').split('\n')
    b=new.decode('utf-8','replace').replace('\r\n','\n').split('\n')
    for i in range(max(len(a),len(b))):
        x=a[i] if i<len(a) else '';y=b[i] if i<len(b) else ''
        if x!=y:return {'first_changed_line':i+1,'before':x[:160],'after':y[:160],'old_line_count':len(a),'new_line_count':len(b)}
    return {'old_line_count':len(a),'new_line_count':len(b)}

# main はCLI入力を解釈し、自己説明的な出力と終了状態を確定する。
def main():
    ap=argparse.ArgumentParser(description='Deterministic canonical template generator.')
    ap.add_argument('--template',required=True);ap.add_argument('--vars',required=True);ap.add_argument('--out',required=True)
    ap.add_argument('--template-id',default='');ap.add_argument('--template-version',default='')
    ap.add_argument('--required',action='append',default=[]);ap.add_argument('--dry-run',action='store_true');ap.add_argument('--check',action='store_true')
    a=ap.parse_args();src=Path(a.template);out=Path(a.out)
    try: raw=json.loads(Path(a.vars).read_text(encoding='utf-8'))
    except Exception as e:
        print(json.dumps({'tool':'template','status':'variables_invalid','error':str(e)},indent=2));return 2
    vars={};bad=[]
    for k,v in raw.items():
        try:vars[k]=scalar(v)
        except TypeError:bad.append(k)
    missing=sorted(k for k in a.required if not vars.get(k,'').strip())
    if bad or missing:
        print(json.dumps({'tool':'template','status':'validation_failed','missing_required_variables':missing,'unsupported_variable_types':sorted(bad)},indent=2));return 2
    vh=hashlib.sha256(Path(a.vars).read_bytes()).hexdigest()
    if not src.exists():
        print(json.dumps({'tool':'template','status':'template_unavailable','template_path':str(src)},indent=2));return 2
    pairs=[]
    if src.is_dir():
        for p in sorted(x for x in src.rglob('*') if x.is_file()):pairs.append((p,out/p.relative_to(src),p.relative_to(src).as_posix()))
    else:pairs=[(src,out,src.name)]
    plans=[];rendered={};unresolved_all=set();changed_count=0;missing_output=0
    for s,d,rel in pairs:
        data=s.read_bytes();binary=b'\x00' in data[:4096];unresolved=[]
        if binary:r=data
        else:
            try:r,unresolved=render(data,vars)
            except UnicodeDecodeError:r=data;binary=True;unresolved=[]
        old=d.read_bytes() if d.exists() else None
        existing=old is not None;changed=old!=r
        if changed:changed_count+=1
        if not existing:missing_output+=1
        plans.append({'template_path':rel,'output_path':str(d),'binary':binary,'changed':changed,'existing':existing,'unresolved_placeholders':unresolved,**({'diff_hint':diff_hint(old,r)} if existing and changed and not binary else {})})
        rendered[d]=r;unresolved_all.update(unresolved)
    unresolved_all=sorted(unresolved_all);status='ok';code=0
    if unresolved_all:status='validation_failed';code=2
    if a.check and not code and (changed_count or missing_output):status='drift_detected';code=1
    meta_path=out/'.acr-template.json' if src.is_dir() else Path(str(out)+'.acr-template.json');wrote=False
    if not a.dry_run and not a.check and code==0:
        for d,data in rendered.items():d.parent.mkdir(parents=True,exist_ok=True);d.write_bytes(data)
        meta={'template_id':a.template_id,'template_version':a.template_version,'template_path':str(src),'variables_sha256':vh,'variable_keys':sorted(vars),'output_path':str(out)}
        meta_path.parent.mkdir(parents=True,exist_ok=True);meta_path.write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');wrote=True
    mode='check' if a.check else 'dry_run' if a.dry_run else 'generate'
    print(json.dumps({'tool':'template','status':status,'mode':mode,'template_path':str(src),'output_path':str(out),'template_id':a.template_id,'template_version':a.template_version,'variables_sha256':vh,'variable_keys':sorted(vars),'file_count':len(plans),'changed_file_count':changed_count,'missing_output_count':missing_output,'files':plans,'unresolved_placeholders':unresolved_all,'metadata_path':str(meta_path),'wrote':wrote,'advanced_backends':{'copier':shutil.which('copier') or '','cookiecutter':shutil.which('cookiecutter') or ''}},ensure_ascii=False,indent=2))
    return code
if __name__=='__main__':sys.exit(main())
