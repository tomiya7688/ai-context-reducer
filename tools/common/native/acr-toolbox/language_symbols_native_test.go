package main

import (
    "errors"
    "io/fs"
    "os"
    "path/filepath"
    "testing"
)

// TestNativeSmallSymbolAnalyzers は対応言語ごとにsymbol位置とwarningを返すことを確認します。
func TestNativeSmallSymbolAnalyzers(t *testing.T) {
    cases := []struct{
        language string
        name string
        content string
        want string
    }{
        {"python","a.py","class Demo:\n    pass\ndef run():\n    pass\n","Demo"},
        {"csharp","A.cs","namespace Demo;\npublic class Widget {\n public void Run() {}\n}\n","Widget"},
        {"go","a.go","package demo\ntype Widget struct{}\nfunc Run() {}\n","Widget"},
        {"c","a.c","struct Widget { int x; };\nint run(void) { return 0; }\n","Widget"},
        {"cpp","a.cpp","namespace demo {\nclass Widget {};\n}\n","demo"},
        {"gdscript","a.gd","class_name Widget\nfunc run():\n    pass\n","Widget"},
    }
    for _,tc:=range cases {
        t.Run(tc.language,func(t *testing.T){
            dir:=t.TempDir()
            if err:=os.WriteFile(filepath.Join(dir,tc.name),[]byte(tc.content),0644); err!=nil { t.Fatal(err) }
            result,err:=buildNativeSymbolResult(dir,tc.language,tc.language+"-symbols")
            if err!=nil { t.Fatal(err) }
            found:=false
            for _,f:=range result.Files {
                for _,s:=range f.Symbols { if s.Name==tc.want { found=true } }
            }
            if !found { t.Fatalf("expected symbol %q in %#v",tc.want,result.Files) }
        })
    }
}

// TestNativeSymbolWalkWarningsRemainVisible はpartial scanをnative analyzer resultへ残します。
func TestNativeSymbolWalkWarningsRemainVisible(t *testing.T) {
    dir := t.TempDir()
    file := filepath.Join(dir, "a.py")
    if err := os.WriteFile(file, []byte("def run():\n    pass\n"), 0644); err != nil { t.Fatal(err) }
    entries, err := os.ReadDir(dir)
    if err != nil { t.Fatal(err) }
    walk := func(root string, visit fs.WalkDirFunc) error {
        if err := visit(filepath.Join(root, "restricted"), nil, errors.New("permission denied")); err != nil { return err }
        return visit(file, entries[0], nil)
    }
    result, err := buildNativeSymbolResultWithWalker(dir, "python", "python-symbols", walk)
    if err != nil { t.Fatal(err) }
    if result.Status != "ok_with_warnings" || result.WalkErrorCount != 1 || len(result.WalkErrorPaths) != 1 {
        t.Fatalf("walk warning was lost: %#v", result)
    }
    if result.WalkErrorPaths[0] != "restricted" || result.FileCount != 1 {
        t.Fatalf("unexpected partial scan result: %#v", result)
    }
    runResult := writeNativeSymbolsWithWalker(dir, "python", "python/small/python-symbols", filepath.Join(dir, "out"), walk)
    if runResult.Status != "ok_with_warnings" || runResult.WalkErrorCount != 1 {
        t.Fatalf("language-run row lost analyzer warnings: %#v", runResult)
    }
    status, failures, skips, warnings := summarizeLanguageStatuses([]string{runResult.Status}, 0)
    if status != "ok_with_warnings" || failures != 0 || skips != 0 || warnings != 1 {
        t.Fatalf("top-level language-run status hid partial analysis: status=%s failures=%d skips=%d warnings=%d", status, failures, skips, warnings)
    }
}
