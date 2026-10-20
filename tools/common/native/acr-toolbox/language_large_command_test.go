package main

import (
    "os"
    "path/filepath"
    "testing"
)

// TestLanguageLargePlanDoesNotAutoRun は計画表示だけではHeavy analyzerを起動しないことを確認します。
func TestLanguageLargePlanDoesNotAutoRun(t *testing.T) {
    dir:=t.TempDir()
    if err:=os.WriteFile(filepath.Join(dir,"a.go"),[]byte("package demo\n"),0644);err!=nil{t.Fatal(err)}
    oldArgs:=os.Args
    defer func(){os.Args=oldArgs}()
    if code:=cmdLanguageLargePlan([]string{dir});code!=0{t.Fatalf("plan code=%d",code)}
}

// TestLanguageLargeRunRequiresExplicitFlag は明示的な実行flagなしではLarge解析を始めないことを確認します。
func TestLanguageLargeRunRequiresExplicitFlag(t *testing.T) {
    dir:=t.TempDir()
    if code:=cmdLanguageLargeRun([]string{dir});code!=2{t.Fatalf("expected confirmation code 2, got %d",code)}
}


// TestLargeBackendExecutionContract はbackend選択後のLarge解析結果と失敗semanticsを確認します。
func TestLargeBackendExecutionContract(t *testing.T) {
    cases := []struct{
        backend string
        available bool
        wantRun bool
        wantExecution string
    }{
        {"existing-scip-index", true, true, "language-large-run"},
        {"universal-ctags", true, true, "language-large-run"},
        {"dotnet", true, false, "planning_only"},
        {"go-list", true, false, "planning_only"},
        {"compiler", true, false, "planning_only"},
        {"godot", true, false, "planning_only"},
        {"python-runtime", true, false, "planning_only"},
        {"", false, false, "unavailable"},
    }
    for _,tc:=range cases {
        t.Run(tc.backend,func(t *testing.T){
            got:=finalizeLargePlan(largeBackendPlan{Backend:tc.backend,Available:tc.available})
            if got.RunSupported!=tc.wantRun {
                t.Fatalf("backend %q run_supported=%v want %v",tc.backend,got.RunSupported,tc.wantRun)
            }
            if got.Execution!=tc.wantExecution {
                t.Fatalf("backend %q execution=%q want %q",tc.backend,got.Execution,tc.wantExecution)
            }
        })
    }
}
