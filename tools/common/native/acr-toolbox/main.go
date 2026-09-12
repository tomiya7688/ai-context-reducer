package main

import (
    "bufio"
    "encoding/json"
    "fmt"
    "io"
    "io/fs"
    "os"
    "path/filepath"
    "regexp"
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

var typeSignals = map[string][]string{
    "game": {"project.godot", "assets", "scenes", "game"},
    "gui": {"ui", "views", "widgets", "forms", "window"},
    "compiler": {"lexer", "parser", "token", "ast", "compiler", "grammar"},
    "data-tool": {"dataset", "etl", "converter", "export", "importer", "migration"},
    "packaged-app": {"installer", "package", "publish", "release", "dist"},
    "simulation": {"simulation", "simulator", "agent", "physics", "seed", "random"},
    "rule-heavy": {"rules", "specification", "protocol", "validator", "policy"},
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

func usage() { fmt.Println("acr-toolbox <analyze|search|find|tree|stats|doc-index|slice|compact-log|env> ...") }

func cmdAnalyze(args []string) int {
    root := "."; if len(args) > 0 { root = args[0] }
    files, _ := walk(root)
    langs := map[string]int{}
    docs, tests, large := 0, 0, 0
    hay := strings.Builder{}
    for _, f := range files {
        rel, _ := filepath.Rel(root, f.Path)
        low := strings.ToLower(filepath.ToSlash(rel))
        hay.WriteString(low); hay.WriteByte(' ')
        if lang := languageByExt[strings.ToLower(filepath.Ext(f.Path))]; lang != "" { langs[lang]++ }
        ext := strings.ToLower(filepath.Ext(f.Path)); if ext == ".md" || ext == ".rst" || ext == ".txt" { docs++ }
        if strings.Contains(strings.ToLower(filepath.Base(f.Path)), "test") || strings.Contains(low, "/tests/") { tests++ }
        if f.Size >= 100000 { large++ }
    }
    size := "small"; if len(files) >= 2000 { size = "large" } else if len(files) >= 200 { size = "medium" }
    types := []string{}
    all := hay.String()
    for name, words := range typeSignals {
        for _, w := range words { if strings.Contains(all, w) { types = append(types, name); break } }
    }
    sort.Strings(types)
    techniques := []string{"AI_CONTEXT minimum core", "Search-first / Read-second", "Exploration stop condition", "Source of Truth", "Targeted validation"}
    if size != "small" { techniques = append(techniques, "Responsibility Map", "Change Routing Map") }
    if size == "large" || large > 0 { techniques = append(techniques, "Source Structure Index", "Bounded excerpts", "Context manifest") }
    for _, t := range types {
        if t == "simulation" { techniques = append(techniques, "Deterministic seam / structured observation") }
        if t == "packaged-app" { techniques = append(techniques, "Artifact-boundary validation") }
        if t == "rule-heavy" { techniques = append(techniques, "Policy Routing") }
    }
    out := map[string]any{"project":filepath.Base(root), "size":size, "files":len(files), "docs":docs, "tests":tests, "large_files_100kb_plus":large, "languages":langs, "project_types":types, "recommended_techniques":techniques, "runtime":map[string]string{"os":runtime.GOOS,"arch":runtime.GOARCH,"implementation":"native-go"}}
    enc := json.NewEncoder(os.Stdout); enc.SetIndent("","  "); enc.Encode(out); return 0
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

func cmdDocIndex(args []string) int {
    root := "."; if len(args) > 0 { root = args[0] }
    files, _ := walk(root); shown := 0
    for _, f := range files {
        if strings.ToLower(filepath.Ext(f.Path)) != ".md" { continue }
        h, err := os.Open(f.Path); if err != nil { continue }
        rel, _ := filepath.Rel(root, f.Path)
        scanner := bufio.NewScanner(h)
        headings := []string{}
        lineNo := 0
        for scanner.Scan() {
            lineNo++
            line := scanner.Text()
            if strings.HasPrefix(line, "# ") || strings.HasPrefix(line, "## ") || strings.HasPrefix(line, "### ") {
                headings = append(headings, fmt.Sprintf("  L%d %s", lineNo, line))
                if len(headings) >= 60 { break }
            }
        }
        h.Close()
        if len(headings) == 0 { continue }
        fmt.Println(filepath.ToSlash(rel))
        for _, x := range headings { fmt.Println(x) }
        shown++; if shown >= 200 { break }
    }
    return 0
}

func readLines(path string) ([]string, error) {
    h, err := os.Open(path); if err != nil { return nil, err }
    defer h.Close()
    out := []string{}
    s := bufio.NewScanner(h)
    buf := make([]byte, 64*1024); s.Buffer(buf, 2*1024*1024)
    for s.Scan() { out = append(out, s.Text()) }
    return out, s.Err()
}

func cmdSlice(args []string) int {
    if len(args) < 2 { fmt.Fprintln(os.Stderr, "usage: acr-toolbox slice PATTERN FILE [FILE...]"); return 2 }
    rx, err := regexp.Compile("(?i)" + args[0]); if err != nil { fmt.Fprintln(os.Stderr, err); return 2 }
    shown := 0
    for _, name := range args[1:] {
        lines, err := readLines(name); if err != nil { continue }
        for i, line := range lines {
            if !rx.MatchString(line) { continue }
            start := i - 3; if start < 0 { start = 0 }
            end := i + 6; if end > len(lines) { end = len(lines) }
            fmt.Printf("--- %s:%d ---\n", name, i+1)
            for n := start; n < end; n++ { fmt.Printf("%6d: %s\n", n+1, lines[n]) }
            shown++; if shown >= 20 { fmt.Println("[truncated: max matches reached]"); return 0 }
        }
    }
    return 0
}

var logSignal = regexp.MustCompile(`(?i)(error|failed|failure|fatal|exception|warning|warn|assert|traceback|ng\b)`)

func cmdCompactLog(args []string) int {
    var r io.Reader = os.Stdin
    if len(args) > 0 {
        h, err := os.Open(args[0]); if err != nil { fmt.Fprintln(os.Stderr, err); return 1 }
        defer h.Close(); r = h
    }
    lines := []string{}
    s := bufio.NewScanner(r)
    buf := make([]byte, 64*1024); s.Buffer(buf, 2*1024*1024)
    for s.Scan() { lines = append(lines, s.Text()) }
    findings := []int{}
    for i, line := range lines { if logSignal.MatchString(line) { findings = append(findings, i) } }
    fmt.Printf("lines=%d findings=%d\n", len(lines), len(findings))
    if len(findings) > 0 {
        fmt.Println("findings:")
        limit := len(findings); if limit > 80 { limit = 80 }
        for _, idx := range findings[:limit] {
            line := lines[idx]; if len(line) > 240 { line = line[:240] }
            fmt.Printf("  %d: %s\n", idx+1, line)
        }
        if len(findings) > limit { fmt.Printf("  ... truncated %d more findings\n", len(findings)-limit) }
    }
    fmt.Println("tail:")
    start := len(lines)-20; if start < 0 { start = 0 }
    for i := start; i < len(lines); i++ {
        line := lines[i]; if len(line) > 240 { line = line[:240] }
        fmt.Printf("  %d: %s\n", i+1, line)
    }
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
    case "analyze": code = cmdAnalyze(os.Args[2:])
    case "search": code = cmdSearch(os.Args[2:])
    case "find": code = cmdFind(os.Args[2:])
    case "tree": code = cmdTree(os.Args[2:])
    case "stats": code = cmdStats(os.Args[2:])
    case "doc-index": code = cmdDocIndex(os.Args[2:])
    case "slice": code = cmdSlice(os.Args[2:])
    case "compact-log": code = cmdCompactLog(os.Args[2:])
    case "env": code = cmdEnv()
    default: usage(); code = 2
    }
    os.Exit(code)
}
