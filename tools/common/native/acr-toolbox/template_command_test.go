package main

import (
  "os"
  "path/filepath"
  "testing"
)

// TestTemplateGenerateAndCheck は対象機能の契約と回帰条件が維持されることを確認します。
func TestTemplateGenerateAndCheck(t *testing.T){
  root:=t.TempDir()
  tpl:=filepath.Join(root,"tpl.txt");vars:=filepath.Join(root,"vars.json");out:=filepath.Join(root,"out.txt")
  if err:=os.WriteFile(tpl,[]byte("Hello {{name}}\n"),0644);err!=nil{t.Fatal(err)}
  if err:=os.WriteFile(vars,[]byte("{\"name\":\"World\"}\n"),0644);err!=nil{t.Fatal(err)}
  args:=[]string{"--template",tpl,"--vars",vars,"--out",out,"--required","name","--template-id","hello","--template-version","1"}
  if code:=cmdTemplate(args);code!=0{t.Fatalf("generate code=%d",code)}
  data,err:=os.ReadFile(out);if err!=nil{t.Fatal(err)}
  if string(data)!="Hello World\n"{t.Fatalf("got %q",string(data))}
  if code:=cmdTemplate(append(args,"--check"));code!=0{t.Fatalf("check code=%d",code)}
  if err:=os.WriteFile(vars,[]byte("{\"name\":\"Other\"}\n"),0644);err!=nil{t.Fatal(err)}
  if code:=cmdTemplate(append(args,"--check"));code!=1{t.Fatalf("expected drift code 1, got %d",code)}
}

// TestTemplateValidationAndDirectory は対象機能の契約と回帰条件が維持されることを確認します。
func TestTemplateValidationAndDirectory(t *testing.T){
  root:=t.TempDir();tplDir:=filepath.Join(root,"tpl");outDir:=filepath.Join(root,"out")
  if err:=os.MkdirAll(tplDir,0755);err!=nil{t.Fatal(err)}
  if err:=os.WriteFile(filepath.Join(tplDir,"a.txt"),[]byte("{{name}}\n"),0644);err!=nil{t.Fatal(err)}
  vars:=filepath.Join(root,"vars.json")
  if err:=os.WriteFile(vars,[]byte("{}\n"),0644);err!=nil{t.Fatal(err)}
  if code:=cmdTemplate([]string{"--template",tplDir,"--vars",vars,"--out",outDir,"--required","name"});code!=2{t.Fatalf("expected missing required code 2, got %d",code)}
  if err:=os.WriteFile(vars,[]byte("{\"name\":\"ok\"}\n"),0644);err!=nil{t.Fatal(err)}
  if code:=cmdTemplate([]string{"--template",tplDir,"--vars",vars,"--out",outDir,"--dry-run"});code!=0{t.Fatalf("dry-run code=%d",code)}
  if _,err:=os.Stat(filepath.Join(outDir,"a.txt"));!os.IsNotExist(err){t.Fatal("dry-run wrote output")}
}
