package main

import (
    "os"
    "path/filepath"
    "testing"
)

// TestNativeSmallSymbolAnalyzers は対象機能の期待contractが将来の変更で崩れないことを検証します。
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
