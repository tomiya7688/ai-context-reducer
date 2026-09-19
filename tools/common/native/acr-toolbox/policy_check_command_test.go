package main

import (
  "encoding/json"
  "os"
  "path/filepath"
  "testing"
)

func writePolicyFixture(t *testing.T, root string, cfg policyRuleConfig) string {
  t.Helper()
  data,err:=json.Marshal(cfg);if err!=nil{t.Fatal(err)}
  p:=filepath.Join(root,"rules.json")
  if err:=os.WriteFile(p,data,0644);err!=nil{t.Fatal(err)}
  return p
}

func TestPolicyCheckPathScopeAndSuppression(t *testing.T){
  root:=t.TempDir()
  if err:=os.MkdirAll(filepath.Join(root,"src","ui"),0755);err!=nil{t.Fatal(err)}
  if err:=os.MkdirAll(filepath.Join(root,"src","core"),0755);err!=nil{t.Fatal(err)}
  if err:=os.WriteFile(filepath.Join(root,"src","ui","a.py"),[]byte("# acr-ignore POL001: reviewed exception\nPath.write_text('x')\n"),0644);err!=nil{t.Fatal(err)}
  if err:=os.WriteFile(filepath.Join(root,"src","core","b.py"),[]byte("Path.write_text('x')\n"),0644);err!=nil{t.Fatal(err)}
  rules:=writePolicyFixture(t,root,policyRuleConfig{Rules:[]policyRule{{
    ID:"POL001",Paths:[]string{"src/ui/**"},Severity:"error",Forbid:"Path.write_text(",
  }}})
  if code:=cmdPolicyCheck([]string{"--rules",rules,root});code!=0{t.Fatalf("expected suppressed scoped rule to pass, got %d",code)}
}

func TestPolicyCheckViolationReturnsOne(t *testing.T){
  root:=t.TempDir()
  if err:=os.WriteFile(filepath.Join(root,"a.txt"),[]byte("forbidden\n"),0644);err!=nil{t.Fatal(err)}
  rules:=writePolicyFixture(t,root,policyRuleConfig{Rules:[]policyRule{{ID:"POL002",Paths:[]string{"**/*.txt"},Severity:"error",Forbid:"forbidden"}}})
  if code:=cmdPolicyCheck([]string{"--rules",rules,root});code!=1{t.Fatalf("expected violation code 1, got %d",code)}
}

func TestPolicyCheckWarningAndSemanticRuleDoNotFail(t *testing.T){
  root:=t.TempDir()
  if err:=os.WriteFile(filepath.Join(root,"a.txt"),[]byte("hello\n"),0644);err!=nil{t.Fatal(err)}
  rules:=writePolicyFixture(t,root,policyRuleConfig{Rules:[]policyRule{
    {ID:"POL003",Paths:[]string{"*.txt"},Severity:"warning",Require:"required"},
    {ID:"POL004",Paths:[]string{"*.txt"},Severity:"error",Forbid:"x",Semantic:true},
  }})
  if code:=cmdPolicyCheck([]string{"--rules",rules,root});code!=0{t.Fatalf("expected warning/unsupported semantic rule not to fail, got %d",code)}
}

func TestPolicyGlobDoubleStar(t *testing.T){
  rx,err:=policyGlobRegex("src/ui/**");if err!=nil{t.Fatal(err)}
  if !rx.MatchString("src/ui/a/b.py"){t.Fatal("expected recursive glob match")}
  if rx.MatchString("src/core/a.py"){t.Fatal("unexpected unrelated path match")}
}
