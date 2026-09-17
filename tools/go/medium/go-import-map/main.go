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

type importRow struct {
    File    string   `json:"file"`
    Status  string   `json:"status"`
    Imports []string `json:"imports"`
    Error   string   `json:"error,omitempty"`
}

type importOutput struct {
    Tool            string      `json:"tool"`
    Status          string      `json:"status"`
    Language        string      `json:"language"`
    RootPath        string      `json:"root_path"`
    Files           []importRow `json:"files"`
    FileCountTotal  int         `json:"file_count_total"`
    FilesReturned   int         `json:"files_returned"`
    ImportsReturned int         `json:"imports_returned"`
    ParseErrorCount int         `json:"parse_error_count"`
    ReadErrorCount  int         `json:"read_error_count"`
    ScanTruncated   bool        `json:"scan_truncated"`
}

func fileImports(path string) importRow {
    fset := token.NewFileSet()
    f, err := parser.ParseFile(fset, path, nil, parser.ImportsOnly)
    if err != nil {
        return importRow{File: filepath.ToSlash(path), Status: "parse_failed", Imports: []string{}, Error: err.Error()}
    }
    set := map[string]bool{}
    for _, imp := range f.Imports {
        value, err := strconv.Unquote(imp.Path.Value)
        if err == nil && value != "" {
            set[value] = true
        }
    }
    imports := make([]string, 0, len(set))
    for value := range set {
        imports = append(imports, value)
    }
    sort.Strings(imports)
    return importRow{File: filepath.ToSlash(path), Status: "ok", Imports: imports}
}

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

func buildImportMap(root string, limit int) (importOutput, error) {
    allFiles, err := sourceFiles(root)
    if err != nil {
        return importOutput{}, err
    }
    if limit < 0 {
        limit = 0
    }
    truncated := limit > 0 && len(allFiles) > limit
    selected := allFiles
    if limit > 0 && len(selected) > limit {
        selected = selected[:limit]
    }
    rows := make([]importRow, 0, len(selected))
    result := importOutput{
        Tool: "go-import-map", Status: "ok", Language: "go", RootPath: filepath.ToSlash(root),
        FileCountTotal: len(allFiles), ScanTruncated: truncated,
    }
    for _, path := range selected {
        row := fileImports(path)
        rel, relErr := filepath.Rel(root, path)
        if relErr == nil {
            row.File = filepath.ToSlash(rel)
        }
        rows = append(rows, row)
        result.ImportsReturned += len(row.Imports)
        if row.Status == "parse_failed" {
            result.ParseErrorCount++
        }
        if row.Status == "read_failed" {
            result.ReadErrorCount++
        }
    }
    result.Files = rows
    result.FilesReturned = len(rows)
    if result.ParseErrorCount > 0 || result.ReadErrorCount > 0 || result.ScanTruncated {
        result.Status = "ok_with_warnings"
    }
    return result, nil
}

func emit(value any) {
    enc := json.NewEncoder(os.Stdout)
    enc.SetIndent("", "  ")
    _ = enc.Encode(value)
}

func main() {
    limit := flag.Int("limit", 0, "maximum files to return; 0 means unlimited")
    flag.Parse()
    root := "."
    if flag.NArg() > 0 {
        root = flag.Arg(0)
    }
    abs, err := filepath.Abs(root)
    if err != nil {
        emit(map[string]any{"tool": "go-import-map", "status": "input_resolution_failed", "error": err.Error()})
        os.Exit(2)
    }
    info, err := os.Stat(abs)
    if err != nil {
        status := "input_read_failed"
        if os.IsNotExist(err) {
            status = "input_missing"
        }
        emit(map[string]any{"tool": "go-import-map", "status": status, "root_path": filepath.ToSlash(abs), "error": err.Error()})
        os.Exit(2)
    }
    if !info.IsDir() {
        emit(map[string]any{"tool": "go-import-map", "status": "input_not_directory", "root_path": filepath.ToSlash(abs)})
        os.Exit(2)
    }
    result, err := buildImportMap(abs, *limit)
    if err != nil {
        emit(map[string]any{"tool": "go-import-map", "status": "scan_failed", "root_path": filepath.ToSlash(abs), "error": err.Error()})
        os.Exit(2)
    }
    emit(result)
}
