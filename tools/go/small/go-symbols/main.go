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
    Status  string   `json:"status"`
    Symbols []symbol `json:"symbols"`
    Error   string   `json:"error,omitempty"`
}

type unsupportedInput struct {
    Path   string `json:"path"`
    Reason string `json:"reason"`
}

type symbolsResult struct {
    Tool                  string             `json:"tool"`
    Status                string             `json:"status"`
    Language              string             `json:"language"`
    Files                 []fileSymbols      `json:"files"`
    FileCount             int                `json:"file_count"`
    SymbolCount           int                `json:"symbol_count"`
    ParseErrorCount       int                `json:"parse_error_count"`
    ReadErrorCount        int                `json:"read_error_count"`
    UnsupportedInputCount int                `json:"unsupported_input_count"`
    UnsupportedInputs     []unsupportedInput `json:"unsupported_inputs"`
}

func scan(path string) fileSymbols {
    normalized := filepath.ToSlash(path)
    fset := token.NewFileSet()
    file, err := parser.ParseFile(fset, path, nil, 0)
    if err != nil {
        return fileSymbols{File: normalized, Status: "parse_failed", Symbols: []symbol{}, Error: err.Error()}
    }
    rows := []symbol{{Kind: "package", Name: file.Name.Name, Line: fset.Position(file.Package).Line}}
    for _, decl := range file.Decls {
        switch d := decl.(type) {
        case *ast.GenDecl:
            if d.Tok != token.TYPE {
                continue
            }
            for _, spec := range d.Specs {
                if ts, ok := spec.(*ast.TypeSpec); ok {
                    rows = append(rows, symbol{Kind: "type", Name: ts.Name.Name, Line: fset.Position(ts.Pos()).Line})
                }
            }
        case *ast.FuncDecl:
            rows = append(rows, symbol{Kind: "func", Name: d.Name.Name, Line: fset.Position(d.Pos()).Line})
        }
    }
    return fileSymbols{File: normalized, Status: "ok", Symbols: rows}
}

func collect(paths []string) ([]fileSymbols, []unsupportedInput, error) {
    files := []string{}
    unsupported := []unsupportedInput{}
    for _, raw := range paths {
        info, err := os.Stat(raw)
        if err != nil {
            if os.IsNotExist(err) {
                unsupported = append(unsupported, unsupportedInput{Path: raw, Reason: "input_missing"})
                continue
            }
            return nil, nil, err
        }
        if !info.IsDir() {
            if strings.EqualFold(filepath.Ext(raw), ".go") {
                files = append(files, raw)
            } else {
                unsupported = append(unsupported, unsupportedInput{Path: raw, Reason: "unsupported_input"})
            }
            continue
        }
        err = filepath.WalkDir(raw, func(path string, d os.DirEntry, err error) error {
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
            return nil, nil, err
        }
    }

    sort.Strings(files)
    deduped := files[:0]
    last := ""
    for _, path := range files {
        if path == last {
            continue
        }
        deduped = append(deduped, path)
        last = path
    }

    rows := make([]fileSymbols, 0, len(deduped))
    for _, path := range deduped {
        rows = append(rows, scan(path))
    }
    return rows, unsupported, nil
}

func buildResult(paths []string) (symbolsResult, error) {
    rows, unsupported, err := collect(paths)
    if err != nil {
        return symbolsResult{}, err
    }
    result := symbolsResult{
        Tool: "go-symbols", Status: "ok", Language: "go", Files: rows,
        FileCount: len(rows), UnsupportedInputCount: len(unsupported), UnsupportedInputs: unsupported,
    }
    for _, row := range rows {
        result.SymbolCount += len(row.Symbols)
        if row.Status == "parse_failed" {
            result.ParseErrorCount++
        }
        if row.Status == "read_failed" {
            result.ReadErrorCount++
        }
    }
    if result.ParseErrorCount > 0 || result.ReadErrorCount > 0 || result.UnsupportedInputCount > 0 {
        result.Status = "ok_with_warnings"
    }
    return result, nil
}

func main() {
    flag.Parse()
    if flag.NArg() == 0 {
        fmt.Fprintln(os.Stderr, "usage: go-symbols <path> [path...]")
        os.Exit(2)
    }
    result, err := buildResult(flag.Args())
    if err != nil {
        encoded, _ := json.MarshalIndent(map[string]any{
            "tool": "go-symbols", "status": "scan_failed", "language": "go", "error": err.Error(),
        }, "", "  ")
        fmt.Println(string(encoded))
        os.Exit(2)
    }
    enc := json.NewEncoder(os.Stdout)
    enc.SetIndent("", "  ")
    if err := enc.Encode(result); err != nil {
        os.Exit(2)
    }
}
