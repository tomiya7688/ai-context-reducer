package main

import (
    "bufio"
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

type edge struct {
    From string `json:"from"`
    To   string `json:"to"`
}

type output struct {
    Root      string `json:"root"`
    Module    string `json:"module"`
    Packages  int    `json:"packages"`
    Edges     []edge `json:"edges"`
    Truncated bool   `json:"truncated"`
}

func modulePath(root string) string {
    f, err := os.Open(filepath.Join(root, "go.mod"))
    if err != nil { return "" }
    defer f.Close()
    sc := bufio.NewScanner(f)
    for sc.Scan() {
        line := strings.TrimSpace(sc.Text())
        if strings.HasPrefix(line, "module ") {
            return strings.TrimSpace(strings.TrimPrefix(line, "module "))
        }
    }
    return ""
}

func importsOf(path string) []string {
    f, err := parser.ParseFile(token.NewFileSet(), path, nil, parser.ImportsOnly)
    if err != nil { return nil }
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

func packageName(root, mod, dir string) string {
    rel, _ := filepath.Rel(root, dir)
    rel = filepath.ToSlash(rel)
    if rel == "." { rel = "" }
    if mod == "" { return rel }
    if rel == "" { return mod }
    return strings.TrimSuffix(mod, "/") + "/" + rel
}

func main() {
    limit := flag.Int("limit", 1500, "maximum number of Go files")
    flag.Parse()
    root := "."
    if flag.NArg() > 0 { root = flag.Arg(0) }
    abs, err := filepath.Abs(root)
    if err != nil {
        fmt.Fprintln(os.Stderr, "go-package-graph:", err)
        os.Exit(2)
    }
    mod := modulePath(abs)

    var files []string
    err = filepath.WalkDir(abs, func(path string, d os.DirEntry, err error) error {
        if err != nil { return err }
        if d.IsDir() && (d.Name() == "vendor" || d.Name() == ".git") { return filepath.SkipDir }
        if !d.IsDir() && strings.EqualFold(filepath.Ext(path), ".go") { files = append(files, path) }
        return nil
    })
    if err != nil {
        fmt.Fprintln(os.Stderr, "go-package-graph:", err)
        os.Exit(2)
    }
    sort.Strings(files)

    truncated := false
    if *limit >= 0 && len(files) > *limit {
        files = files[:*limit]
        truncated = true
    }

    packages := map[string]map[string]bool{}
    for _, path := range files {
        pkg := packageName(abs, mod, filepath.Dir(path))
        if _, ok := packages[pkg]; !ok { packages[pkg] = map[string]bool{} }
        for _, dep := range importsOf(path) { packages[pkg][dep] = true }
    }

    local := map[string]bool{}
    for pkg := range packages { local[pkg] = true }
    var edges []edge
    for src, deps := range packages {
        for dep := range deps {
            if local[dep] { edges = append(edges, edge{From: src, To: dep}) }
        }
    }
    sort.Slice(edges, func(i, j int) bool {
        if edges[i].From == edges[j].From { return edges[i].To < edges[j].To }
        return edges[i].From < edges[j].From
    })

    out := output{Root: filepath.Base(abs), Module: mod, Packages: len(packages), Edges: edges, Truncated: truncated}
    enc := json.NewEncoder(os.Stdout)
    enc.SetIndent("", "  ")
    if err := enc.Encode(out); err != nil { os.Exit(2) }
}
