package main

import (
    "encoding/json"
    "flag"
    "fmt"
    "go/ast"
    "go/parser"
    "go/token"
    "os"
    "path/filepath"
    "sort"
    "strings"
)

type symbol struct {
    Kind string `json:"kind"`
    Name string `json:"name"`
    Line int    `json:"line"`
}

type fileSymbols struct {
    File    string   `json:"file"`
    Symbols []symbol `json:"symbols"`
}

func scan(path string) fileSymbols {
    fset := token.NewFileSet()
    file, err := parser.ParseFile(fset, path, nil, 0)
    if err != nil {
        return fileSymbols{File: filepath.ToSlash(path), Symbols: []symbol{}}
    }
    rows := []symbol{{Kind: "package", Name: file.Name.Name, Line: fset.Position(file.Package).Line}}
    for _, decl := range file.Decls {
        switch d := decl.(type) {
        case *ast.GenDecl:
            if d.Tok != token.TYPE { continue }
            for _, spec := range d.Specs {
                if ts, ok := spec.(*ast.TypeSpec); ok {
                    rows = append(rows, symbol{Kind: "type", Name: ts.Name.Name, Line: fset.Position(ts.Pos()).Line})
                }
            }
        case *ast.FuncDecl:
            rows = append(rows, symbol{Kind: "func", Name: d.Name.Name, Line: fset.Position(d.Pos()).Line})
        }
    }
    return fileSymbols{File: filepath.ToSlash(path), Symbols: rows}
}

func collect(paths []string) ([]fileSymbols, error) {
    var files []string
    for _, raw := range paths {
        info, err := os.Stat(raw)
        if err != nil { return nil, err }
        if !info.IsDir() {
            if strings.EqualFold(filepath.Ext(raw), ".go") { files = append(files, raw) }
            continue
        }
        err = filepath.WalkDir(raw, func(path string, d os.DirEntry, err error) error {
            if err != nil { return err }
            if d.IsDir() && (d.Name() == "vendor" || d.Name() == ".git") { return filepath.SkipDir }
            if !d.IsDir() && strings.EqualFold(filepath.Ext(path), ".go") { files = append(files, path) }
            return nil
        })
        if err != nil { return nil, err }
    }
    sort.Strings(files)
    out := make([]fileSymbols, 0, len(files))
    for _, f := range files { out = append(out, scan(f)) }
    return out, nil
}

func main() {
    flag.Parse()
    if flag.NArg() == 0 {
        fmt.Fprintln(os.Stderr, "usage: go-symbols <path> [path...]")
        os.Exit(2)
    }
    out, err := collect(flag.Args())
    if err != nil {
        fmt.Fprintln(os.Stderr, "go-symbols:", err)
        os.Exit(2)
    }
    enc := json.NewEncoder(os.Stdout)
    enc.SetIndent("", "  ")
    if err := enc.Encode(out); err != nil { os.Exit(2) }
}
