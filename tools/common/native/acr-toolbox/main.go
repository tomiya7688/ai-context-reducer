package main

import (
    "bufio"
    "encoding/json"
    "fmt"
    "io/fs"
    "os"
    "path/filepath"
    "runtime"
    "sort"
    "strings"
)

var ignoreDirs = map[string]bool{
    ".git": true, ".venv": true, "venv": true, "node_modules": true,
    "bin": true, "obj": true, "build": true, "dist": true, "__pycache__": true, ".godot": true,
}

var languageByExt = map[string]string{
    ".py":"Python", ".cs":"CSharp", ".go":"Go", ".c":"C", ".h":"C/C++",
    ".cpp":"C++", ".cc":"C++", ".cxx":"C++", ".hpp":"C++", ".hh":"C++",
    ".gd":"GDScript", ".rs":"Rust", ".js":"JavaScript", ".ts":"TypeScript", ".java":"Java",
}

type fileInfo struct { Path string; Size int64 }

func walk(root string) ([]fileInfo, error) {
    out := []fileInfo{}
    err := filepath.WalkDir(root, func(path string, d fs.DirEntry, err error) error {
        if err != nil { return nil }
        if d.IsDir() {
            if path != root && ignoreDirs[strings.ToLower(d.Name())] { return filepath.SkipDir }
            return nil
        }
        info, e := d.Info(); if e != nil { return nil }
        out = append(out, fileInfo{Path:path, Size:info.Size()})
        return nil
    })
    return out, err
}

func usage() {
    fmt.Println("acr-toolbox <search|find|tree|stats|env> ...")
}

func cmdSearch(args []string) int {
    if len(args) < 1 { fmt.Fprintln(os.Stderr, "usage: acr-toolbox search PATTERN [ROOT]"); return 2 }
    pattern := args[0]; root := "."; if len(args) > 1 { root = args[1] }
    files, _ := walk(root); count := 0
    for _, f := range files {
        if f.Size > 2*1024*1024 { continue }
        h, err := os.Open(f.Path); if err != nil { continue }
        s := bufio.NewScanner(h); line := 0
        for s.Scan() {
            line++
            if strings.Contains(strings.ToLower(s.Text()), strings.ToLower(pattern)) {
                rel, _ := filepath.Rel(root, f.Path)
                fmt.Printf("%s:%d:%s\n", filepath.ToSlash(rel), line, s.Text())
                count++; if count >= 200 { h.Close(); return 0 }
            }
        }
        h.Close()
    }
    return 0
}

func cmdFind(args []string) int {
    query := ""; root := "."; if len(args) > 0 { query = strings.ToLower(args[0]) }; if len(args) > 1 { root = args[1] }
    files, _ := walk(root); n := 0
    for _, f := range files {
        rel, _ := filepath.Rel(root, f.Path)
        if query == "" || strings.Contains(strings.ToLower(rel), query) {
            fmt.Println(filepath.ToSlash(rel)); n++; if n >= 500 { break }
        }
    }
    return 0
}

func cmdTree(args []string) int {
    root := "."; maxDepth := 3
    if len(args) > 0 { root = args[0] }
    files, _ := walk(root); seen := map[string]bool{}; n := 0
    for _, f := range files {
        rel, _ := filepath.Rel(root, f.Path)
        parts := strings.Split(filepath.ToSlash(rel), "/")
        if len(parts) > maxDepth { parts = parts[:maxDepth] }
        key := strings.Join(parts, "/")
        if !seen[key] { seen[key] = true; fmt.Println(key); n++; if n >= 500 { break } }
    }
    return 0
}

func cmdStats(args []string) int {
    root := "."; if len(args) > 0 { root = args[0] }
    files, _ := walk(root)
    counts := map[string]int{}; lines := map[string]int{}
    for _, f := range files {
        lang := languageByExt[strings.ToLower(filepath.Ext(f.Path))]; if lang == "" { continue }
        counts[lang]++
        h, err := os.Open(f.Path); if err != nil { continue }
        s := bufio.NewScanner(h); for s.Scan() { lines[lang]++ }; h.Close()
    }
    keys := make([]string,0,len(counts)); for k := range counts { keys = append(keys,k) }; sort.Strings(keys)
    for _, k := range keys { fmt.Printf("%s files=%d lines=%d\n", k, counts[k], lines[k]) }
    fmt.Printf("total_files=%d\n", len(files))
    return 0
}

func cmdEnv() int {
    out := map[string]any{"os":runtime.GOOS, "arch":runtime.GOARCH, "native":true}
    enc := json.NewEncoder(os.Stdout); enc.SetIndent("","  "); enc.Encode(out); return 0
}

func main() {
    if len(os.Args) < 2 { usage(); os.Exit(2) }
    var code int
    switch os.Args[1] {
    case "search": code = cmdSearch(os.Args[2:])
    case "find": code = cmdFind(os.Args[2:])
    case "tree": code = cmdTree(os.Args[2:])
    case "stats": code = cmdStats(os.Args[2:])
    case "env": code = cmdEnv()
    default: usage(); code = 2
    }
    os.Exit(code)
}
