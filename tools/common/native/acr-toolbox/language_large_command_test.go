package main

import (
    "os"
    "path/filepath"
    "testing"
)

func TestLanguageLargePlanDoesNotAutoRun(t *testing.T) {
    dir:=t.TempDir()
    if err:=os.WriteFile(filepath.Join(dir,"a.go"),[]byte("package demo\n"),0644);err!=nil{t.Fatal(err)}
    oldArgs:=os.Args
    defer func(){os.Args=oldArgs}()
    if code:=cmdLanguageLargePlan([]string{dir});code!=0{t.Fatalf("plan code=%d",code)}
}

func TestLanguageLargeRunRequiresExplicitFlag(t *testing.T) {
    dir:=t.TempDir()
    if code:=cmdLanguageLargeRun([]string{dir});code!=2{t.Fatalf("expected confirmation code 2, got %d",code)}
}
