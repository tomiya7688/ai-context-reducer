package main

import (
  "encoding/json"
  "io/fs"
  "io"
  "os"
  "path/filepath"
  "strings"
  "testing"
)

// writePolicyFixture はtest setupや検証を局所化し、各testの意図を読みやすく保ちます。
func writePolicyFixture(t *testing.T, root string, cfg policyRuleConfig) string {
  t.Helper()
  data,err:=json.Marshal(cfg);if err!=nil{t.Fatal(err)}
  p:=filepath.Join(root,"rules.json")
  if err:=os.WriteFile(p,data,0644);err!=nil{t.Fatal(err)}
  return p
}

// capturePolicyCheck はexit codeとJSON結果を同じ実行から取得します。
func capturePolicyCheck(t *testing.T,args []string)(int,map[string]any){
  t.Helper()
  previous:=os.Stdout
  reader,writer,err:=os.Pipe();if err!=nil{t.Fatal(err)}
  os.Stdout=writer
  code:=cmdPolicyCheck(args)
  _=writer.Close();os.Stdout=previous
  data,err:=io.ReadAll(reader);_=reader.Close();if err!=nil{t.Fatal(err)}
  var result map[string]any
  if err:=json.Unmarshal(data,&result);err!=nil{t.Fatalf("invalid JSON output %q: %v",string(data),err)}
  return code,result
}

// TestPolicyCheckPathScopeAndSuppression は対象scopeの違反だけを返しignore markerで抑制することを確認します。
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

// TestPolicyCheckViolationReturnsOne はerror severityの違反でexit code 1を返すことを確認します。
func TestPolicyCheckViolationReturnsOne(t *testing.T){
  root:=t.TempDir()
  if err:=os.WriteFile(filepath.Join(root,"a.txt"),[]byte("forbidden\n"),0644);err!=nil{t.Fatal(err)}
  rules:=writePolicyFixture(t,root,policyRuleConfig{Rules:[]policyRule{{ID:"POL002",Paths:[]string{"**/*.txt"},Severity:"error",Forbid:"forbidden"}}})
  if code:=cmdPolicyCheck([]string{"--rules",rules,root});code!=1{t.Fatalf("expected violation code 1, got %d",code)}
}

// TestPolicyCheckWarningAndSemanticRuleDoNotFail はwarningとsemantic ruleだけでは失敗終了しないことを確認します。
func TestPolicyCheckWarningAndSemanticRuleDoNotFail(t *testing.T){
  root:=t.TempDir()
  if err:=os.WriteFile(filepath.Join(root,"a.txt"),[]byte("hello\n"),0644);err!=nil{t.Fatal(err)}
  rules:=writePolicyFixture(t,root,policyRuleConfig{Rules:[]policyRule{
    {ID:"POL003",Paths:[]string{"*.txt"},Severity:"warning",Require:"required"},
    {ID:"POL004",Paths:[]string{"*.txt"},Severity:"error",Forbid:"x",Semantic:true},
  }})
  if code:=cmdPolicyCheck([]string{"--rules",rules,root});code!=0{t.Fatalf("expected warning/unsupported semantic rule not to fail, got %d",code)}
}

// TestPolicyGlobDoubleStar は** patternがnested pathを含むfile範囲へ一致することを確認します。
func TestPolicyGlobDoubleStar(t *testing.T){
  rx,err:=policyGlobRegex("src/ui/**");if err!=nil{t.Fatal(err)}
  if !rx.MatchString("src/ui/a/b.py"){t.Fatal("expected recursive glob match")}
  if rx.MatchString("src/core/a.py"){t.Fatal("unexpected unrelated path match")}
}

// TestPolicyCheckRejectsInvalidRoots はmissing rootとfile rootをnon-zeroで拒否します。
func TestPolicyCheckRejectsInvalidRoots(t *testing.T){
  parent:=t.TempDir()
  rules:=writePolicyFixture(t,parent,policyRuleConfig{Rules:[]policyRule{{ID:"POL005",Forbid:"x"}}})
  for _,tc:=range []struct{name,root,status string}{
    {name:"missing",root:filepath.Join(parent,"missing"),status:"input_missing"},
    {name:"file",root:filepath.Join(parent,"root.txt"),status:"input_not_directory"},
  }{
    t.Run(tc.name,func(t *testing.T){
      if tc.name=="file"{if err:=os.WriteFile(tc.root,[]byte("content"),0644);err!=nil{t.Fatal(err)}}
      code,result:=capturePolicyCheck(t,[]string{"--rules",rules,tc.root})
      if code!=2||result["status"]!=tc.status{t.Fatalf("got code=%d status=%v, want code=2 status=%s",code,result["status"],tc.status)}
    })
  }
}

// TestPolicyCheckWalkErrorsArePartial は列挙失敗を記録しclean成功にしません。
func TestPolicyCheckWalkErrorsArePartial(t *testing.T){
  parent:=t.TempDir();root:=filepath.Join(parent,"root")
  if err:=os.Mkdir(root,0755);err!=nil{t.Fatal(err)}
  if err:=os.WriteFile(filepath.Join(root,"a.txt"),[]byte("clean\n"),0644);err!=nil{t.Fatal(err)}
  rules:=writePolicyFixture(t,parent,policyRuleConfig{Rules:[]policyRule{{ID:"POL006",Forbid:"forbidden"}}})
  previous:=walkPolicyDir
  walkPolicyDir=func(path string,walkFn fs.WalkDirFunc)error{
    entries,err:=os.ReadDir(path);if err!=nil{return err}
    for _,entry:=range entries{if err:=walkFn(filepath.Join(path,entry.Name()),entry,nil);err!=nil{return err}}
    return walkFn(filepath.Join(path,"unreadable"),nil,os.ErrPermission)
  }
  defer func(){walkPolicyDir=previous}()
  code,result:=capturePolicyCheck(t,[]string{"--rules",rules,root})
  if code!=2||result["status"]!="partial"{t.Fatalf("walk failure should be partial/non-zero: code=%d result=%v",code,result)}
  if result["walk_error_count"]!=float64(1){t.Fatalf("walk_error_count=%v",result["walk_error_count"])}
  paths,ok:=result["walk_error_paths"].([]any);if !ok||len(paths)!=1||!strings.HasSuffix(paths[0].(string),"unreadable"){t.Fatalf("walk_error_paths=%v",result["walk_error_paths"])}

  if err:=os.WriteFile(filepath.Join(root,"a.txt"),[]byte("forbidden\n"),0644);err!=nil{t.Fatal(err)}
  code,result=capturePolicyCheck(t,[]string{"--rules",rules,root})
  if code!=1||result["status"]!="violations"||result["error_count"]!=float64(1)||result["walk_error_count"]!=float64(1){t.Fatalf("violation must retain walk incompleteness: code=%d result=%v",code,result)}
}
