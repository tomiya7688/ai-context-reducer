package main

import (
    "encoding/json"
    "flag"
    "fmt"
    "go/parser"
    "go/token"
    "os"
    "path/filepath"
    "sort"
    "strconv"
    "strings"
)

type row struct {
    File    string   `json:"file"`
    Imports []string `json:"imports"`
}

type output struct {
    Root      string `json:"root"`
    Files     []row  `json:"files"`
    Truncated bool   `json:"truncated"`
}

func fileImports(path string) []string {
    fset := token.NewFileSet()
    f, err := parser.ParseFile(fset, path, nil, parser.ImportsOnly)
    if err != nil { return []string{} }
    set := map[string]bool{}
    for _, imp := range f.Imports {
        v, err := strconv.Unquote(imp.Path.Value)
        if err == nil && v != "" { set[v] = true }
    }
    out := make([]string, 0, len(set))
    for v := range set { out = append(out, v) }
    sort.Strings(out)
    return out
}

func main() {
    limit := flag.Int("limit", 500, "maximum number of Go files")
    flag.Parse()
    root := "."
    if flag.NArg() > 0 { root = flag.Arg(0) }
    abs, err := filepath.Abs(root)
    if err != nil {
        fmt.Fprintln(os.Stderr, "go-import-map:", err)
        os.Exit(2)
    }

    var files []string
    err = filepath.WalkDir(abs, func(path string, d os.DirEntry, err error) error {
        if err != nil { return err }
        if d.IsDir() && (d.Name() == "vendor" || d.Name() == ".git") { return filepath.SkipDir }
        if !d.IsDir() && strings.EqualFold(filepath.Ext(path), ".go") { files = append(files, path) }
        return nil
    })
    if err != nil {
        fmt.Fprintln(os.Stderr, "go-import-map:", err)
        os.Exit(2)
    }
    sort.Strings(files)

    truncated := false
    if *limit >= 0 && len(files) > *limit {
        files = files[:*limit]
        truncated = true
    }
    rows := make([]row, 0, len(files))
    for _, path := range files {
        rel, _ := filepath.Rel(abs, path)
        rows = append(rows, row{File: filepath.ToSlash(rel), Imports: fileImports(path)})
    }

    out := output{Root: filepath.Base(abs), Files: rows, Truncated: truncated}
    enc := json.NewEncoder(os.Stdout)
    enc.SetIndent("", "  ")
    if err := enc.Encode(out); err != nil { os.Exit(2) }
}
