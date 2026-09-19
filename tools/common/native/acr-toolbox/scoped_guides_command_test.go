package main

import (
  "os"
  "path/filepath"
  "testing"
)

func TestScopedGuidesAncestorOnly(t *testing.T){
  root:=t.TempDir()
  target:=filepath.Join(root,"apps","editor","src","x.go")
  if err:=os.MkdirAll(filepath.Dir(target),0755);err!=nil{t.Fatal(err)}
  if err:=os.WriteFile(target,[]byte("package x\n"),0644);err!=nil{t.Fatal(err)}
  for _,p:=range []string{
    filepath.Join(root,"AI_CONTEXT.md"),
    filepath.Join(root,"apps","editor","AI_CONTEXT.local.md"),
    filepath.Join(root,"apps","server","AI_CONTEXT.local.md"),
  }{
    if err:=os.MkdirAll(filepath.Dir(p),0755);err!=nil{t.Fatal(err)}
    if err:=os.WriteFile(p,[]byte("# guide\n"),0644);err!=nil{t.Fatal(err)}
  }
  if code:=cmdScopedGuides([]string{target,root});code!=0{t.Fatalf("code=%d",code)}
}

func TestScopedGuidesCustomName(t *testing.T){
  root:=t.TempDir()
  target:=filepath.Join(root,"pkg","src")
  if err:=os.MkdirAll(target,0755);err!=nil{t.Fatal(err)}
  if err:=os.WriteFile(filepath.Join(root,"LOCAL_GUIDE.md"),[]byte("# local\n"),0644);err!=nil{t.Fatal(err)}
  if code:=cmdScopedGuides([]string{"--name","LOCAL_GUIDE.md",target,root});code!=0{t.Fatalf("code=%d",code)}
}
