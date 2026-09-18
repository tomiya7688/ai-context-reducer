package main

import (
    "os"
    "path/filepath"
    "testing"
)

func TestMediumDependencyMaps(t *testing.T) {
    cases := []struct{
        language string
        name string
        content string
        want string
    }{
        {"python","a.py","import os\nfrom pkg.sub import value\n","pkg.sub"},
        {"csharp","a.csproj","<Project><ItemGroup><ProjectReference Include=\"../lib/lib.csproj\" /></ItemGroup></Project>","../lib/lib.csproj"},
        {"go","a.go","package demo\nimport \"fmt\"\n","fmt"},
        {"c","a.c","#include <stdio.h>\n","stdio.h"},
        {"cpp","a.cpp","#include \"widget.hpp\"\n","widget.hpp"},
        {"gdscript","a.gd","extends \"res://base.gd\"\nvar x = preload(\"res://x.tscn\")\n","res://x.tscn"},
    }
    for _,tc:=range cases {
        t.Run(tc.language,func(t *testing.T){
            dir:=t.TempDir()
            if err:=os.WriteFile(filepath.Join(dir,tc.name),[]byte(tc.content),0644); err!=nil { t.Fatal(err) }
            result,err:=buildDependencyResult(dir,tc.language,tc.language+"-map")
            if err!=nil { t.Fatal(err) }
            found:=false
            for _,f:=range result.Files {
                for _,d:=range f.Dependencies { if d==tc.want { found=true } }
            }
            if !found { t.Fatalf("expected dependency %q in %#v",tc.want,result.Files) }
        })
    }
}
