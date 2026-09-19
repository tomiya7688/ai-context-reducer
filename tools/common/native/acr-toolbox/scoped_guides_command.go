package main

import (
  "flag"
  "os"
  "path/filepath"
  "strings"
)

type scopedGuideNameList []string
func (s *scopedGuideNameList) String() string { return strings.Join(*s,",") }
func (s *scopedGuideNameList) Set(v string) error { *s=append(*s,v); return nil }

func cmdScopedGuides(args []string) int {
  fs:=flag.NewFlagSet("scoped-guides",flag.ContinueOnError)
  names:=scopedGuideNameList{"AI_CONTEXT.md","AI_CONTEXT.local.md","AGENTS.md","CLAUDE.md"}
  fs.Var(&names,"name","guide filename; repeatable")
  if err:=fs.Parse(args);err!=nil{return 2}
  root:="."; target:="."
  if fs.NArg()>0{target=fs.Arg(0)}
  if fs.NArg()>1{root=fs.Arg(1)}
  absRoot,err:=filepath.Abs(root); if err!=nil{return 2}
  absTarget,err:=filepath.Abs(target); if err!=nil{return 2}
  info,err:=os.Stat(absRoot); if err!=nil||!info.IsDir(){selectorWriteJSON(map[string]any{"tool":"scoped-guides","status":"input_unavailable","root_path":absRoot});return 2}
  if rel,err:=filepath.Rel(absRoot,absTarget);err!=nil||strings.HasPrefix(rel,".."){selectorWriteJSON(map[string]any{"tool":"scoped-guides","status":"target_outside_root","root_path":absRoot,"target_path":absTarget});return 2}
  dir:=absTarget
  if st,err:=os.Stat(absTarget);err==nil&&!st.IsDir(){dir=filepath.Dir(absTarget)}
  dirs:=[]string{}
  cur:=dir
  for {
    dirs=append(dirs,cur)
    if cur==absRoot{break}
    next:=filepath.Dir(cur)
    if next==cur{break}
    cur=next
  }
  for i,j:=0,len(dirs)-1;i<j;i,j=i+1,j-1{dirs[i],dirs[j]=dirs[j],dirs[i]}
  seen:=map[string]bool{}
  guides:=[]map[string]any{}
  for depth,d:=range dirs{
    for _,name:=range names{
      p:=filepath.Join(d,name)
      if seen[p]{continue}
      if st,err:=os.Stat(p);err==nil&&!st.IsDir(){
        seen[p]=true
        rel,_:=filepath.Rel(absRoot,p)
        scope,_:=filepath.Rel(absRoot,d)
        if scope=="."{scope=""}
        guides=append(guides,map[string]any{
          "path":filepath.ToSlash(rel),"scope":filepath.ToSlash(scope),"depth":depth,
          "reason":"guide is on the ancestor path from repository root to target",
        })
      }
    }
  }
  selectorWriteJSON(map[string]any{
    "tool":"scoped-guides","status":"ok","root_path":absRoot,"target_path":absTarget,
    "guide_names":[]string(names),"guides":guides,"guide_count":len(guides),
    "precedence_defined":false,
    "policy":"filesystem scope resolver only; agent-specific instruction precedence is not inferred",
  })
  return 0
}
