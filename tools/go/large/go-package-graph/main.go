package main

import (
    "bufio"
    "encoding/json"
    "flag"
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

type graphOutput struct {
    Tool            string `json:"tool"`
    Status          string `json:"status"`
    Language        string `json:"language"`
    RootPath        string `json:"root_path"`
    Module          string `json:"module"`
    PackageCount    int    `json:"package_count"`
    Edges           []edge `json:"edges"`
    EdgeCount       int    `json:"edge_count"`
    FilesScanned    int    `json:"files_scanned"`
    FileCountTotal  int    `json:"file_count_total"`
    ParseErrorCount int    `json:"parse_error_count"`
    ReadErrorCount  int    `json:"read_error_count"`
    ScanTruncated   bool   `json:"scan_truncated"`
}

// go.modからmodule pathを読み、package nodeをrepo内の安定識別子へ寄せる。
func modulePath(root string) string {
    file, err := os.Open(filepath.Join(root, "go.mod"))
    if err != nil {
        return ""
    }
    defer file.Close()
    scanner := bufio.NewScanner(file)
    for scanner.Scan() {
        line := strings.TrimSpace(scanner.Text())
        if strings.HasPrefix(line, "module ") {
            return strings.TrimSpace(strings.TrimPrefix(line, "module "))
        }
    }
    return ""
}

// 1つのGo sourceをparseし、import依存とparse失敗を別signalとして返す。
func importsOf(path string) ([]string, string) {
    file, err := parser.ParseFile(token.NewFileSet(), path, nil, parser.ImportsOnly)
    if err != nil {
        return nil, "parse_failed"
    }
    set := map[string]bool{}
    for _, imp := range file.Imports {
        value, err := strconv.Unquote(imp.Path.Value)
        if err == nil && value != "" {
            set[value] = true
        }
    }
    out := make([]string, 0, len(set))
    for value := range set {
        out = append(out, value)
    }
    sort.Strings(out)
    return out, "ok"
}

// Go sourceのpackage名だけをparseし、失敗時は空packageと混同しない。
func packageName(root, module, dir string) string {
    rel, _ := filepath.Rel(root, dir)
    rel = filepath.ToSlash(rel)
    if rel == "." {
        rel = ""
    }
    if module == "" {
        return rel
    }
    if rel == "" {
        return module
    }
    return strings.TrimSuffix(module, "/") + "/" + rel
}

// vendor等を避けながらGo sourceを決定論的に列挙する。
func sourceFiles(root string) ([]string, error) {
    files := []string{}
    err := filepath.WalkDir(root, func(path string, d os.DirEntry, err error) error {
        if err != nil {
            return err
        }
        if d.IsDir() && (d.Name() == "vendor" || d.Name() == ".git") {
            return filepath.SkipDir
        }
        if !d.IsDir() && strings.EqualFold(filepath.Ext(path), ".go") {
            files = append(files, path)
        }
        return nil
    })
    if err != nil {
        return nil, err
    }
    sort.Strings(files)
    return files, nil
}

// package依存をfile nodeへ橋渡しし、truncationとparse失敗を完全性signalとして保持する。
func buildPackageGraph(root string, limit int) (graphOutput, error) {
    allFiles, err := sourceFiles(root)
    if err != nil {
        return graphOutput{}, err
    }
    if limit < 0 {
        limit = 0
    }
    truncated := limit > 0 && len(allFiles) > limit
    files := allFiles
    if limit > 0 && len(files) > limit {
        files = files[:limit]
    }

    module := modulePath(root)
    packages := map[string]map[string]bool{}
    parseErrors := 0
    for _, path := range files {
        pkg := packageName(root, module, filepath.Dir(path))
        if _, ok := packages[pkg]; !ok {
            packages[pkg] = map[string]bool{}
        }
        imports, status := importsOf(path)
        if status == "parse_failed" {
            parseErrors++
            continue
        }
        for _, dep := range imports {
            packages[pkg][dep] = true
        }
    }

    local := map[string]bool{}
    for pkg := range packages {
        local[pkg] = true
    }
    edges := []edge{}
    for source, deps := range packages {
        for dep := range deps {
            if local[dep] {
                edges = append(edges, edge{From: source, To: dep})
            }
        }
    }
    sort.Slice(edges, func(i, j int) bool {
        if edges[i].From == edges[j].From {
            return edges[i].To < edges[j].To
        }
        return edges[i].From < edges[j].From
    })

    status := "ok"
    if parseErrors > 0 || truncated {
        status = "ok_with_warnings"
    }
    return graphOutput{
        Tool: "go-package-graph", Status: status, Language: "go",
        RootPath: filepath.ToSlash(root), Module: module, PackageCount: len(packages),
        Edges: edges, EdgeCount: len(edges), FilesScanned: len(files),
        FileCountTotal: len(allFiles), ParseErrorCount: parseErrors, ScanTruncated: truncated,
    }, nil
}

// graph結果を単一JSON表現へ出力し、同内容のtext重複を避ける。
func emitGraph(value any) {
    enc := json.NewEncoder(os.Stdout)
    enc.SetIndent("", "  ")
    _ = enc.Encode(value)
}

// CLI入力を検証し、bounded package graphと明示的failureを同じJSON契約で返す。
func main() {
    limit := flag.Int("limit", 0, "maximum source files to analyze; 0 means unlimited")
    flag.Parse()
    root := "."
    if flag.NArg() > 0 {
        root = flag.Arg(0)
    }
    abs, err := filepath.Abs(root)
    if err != nil {
        emitGraph(map[string]any{"tool": "go-package-graph", "status": "input_resolution_failed", "error": err.Error()})
        os.Exit(2)
    }
    info, err := os.Stat(abs)
    if err != nil {
        status := "input_read_failed"
        if os.IsNotExist(err) {
            status = "input_missing"
        }
        emitGraph(map[string]any{"tool": "go-package-graph", "status": status, "root_path": filepath.ToSlash(abs), "error": err.Error()})
        os.Exit(2)
    }
    if !info.IsDir() {
        emitGraph(map[string]any{"tool": "go-package-graph", "status": "input_not_directory", "root_path": filepath.ToSlash(abs)})
        os.Exit(2)
    }
    result, err := buildPackageGraph(abs, *limit)
    if err != nil {
        emitGraph(map[string]any{"tool": "go-package-graph", "status": "scan_failed", "root_path": filepath.ToSlash(abs), "error": err.Error()})
        os.Exit(2)
    }
    emitGraph(result)
}
