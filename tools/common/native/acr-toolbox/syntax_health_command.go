package main

import (
    "encoding/json"
    "flag"
    "io"
    "os"
    "os/exec"
    "path/filepath"
    "sort"
    "strings"
)

type syntaxHealthRow struct {
    Path         string `json:"path"`
    SyntaxOK     bool   `json:"syntax_ok"`
    ErrorCount   int    `json:"error_count"`
    MissingCount int    `json:"missing_count"`
}

// syntaxInt はこの責務内の変換・routingを局所化し、呼び出し側のworking setを増やさないための処理です。
func syntaxInt(value any) int {
    switch v := value.(type) {
    case float64:
        return int(v)
    case int:
        return v
    case bool:
        if v {
            return 1
        }
    }
    return 0
}

// syntaxString はこの責務内の変換・routingを局所化し、呼び出し側のworking setを増やさないための処理です。
func syntaxString(row map[string]any, names ...string) string {
    for _, name := range names {
        if value, ok := row[name].(string); ok {
            return value
        }
    }
    return ""
}

// normalizeSyntaxHealth は表記揺れを正規化し、後段の比較条件を単純化します。
func normalizeSyntaxHealth(payload any) []syntaxHealthRow {
    rawRows := []any{payload}
    if rows, ok := payload.([]any); ok {
        rawRows = rows
    }
    result := []syntaxHealthRow{}
    for _, raw := range rawRows {
        row, ok := raw.(map[string]any)
        if !ok {
            continue
        }
        errorCount := syntaxInt(row["error_count"])
        if _, exists := row["error_count"]; !exists {
            errorCount = syntaxInt(row["errors"])
        }
        missingCount := syntaxInt(row["missing_count"])
        if _, exists := row["missing_count"]; !exists {
            missingCount = syntaxInt(row["missing"])
        }
        success, hasSuccess := row["successful"].(bool)
        if !hasSuccess {
            success, hasSuccess = row["success"].(bool)
        }
        syntaxOK := errorCount == 0 && missingCount == 0
        if hasSuccess {
            syntaxOK = success && syntaxOK
        }
        result = append(result, syntaxHealthRow{
            Path: syntaxString(row, "path", "file", "filename"),
            SyntaxOK: syntaxOK,
            ErrorCount: errorCount,
            MissingCount: missingCount,
        })
    }
    sort.Slice(result, func(i, j int) bool {
        if result[i].SyntaxOK != result[j].SyntaxOK {
            return !result[i].SyntaxOK
        }
        return result[i].Path < result[j].Path
    })
    return result
}

// emitSyntaxHealth は内部結果を安定した利用者向け出力へ変換します。
func emitSyntaxHealth(rows []syntaxHealthRow, maxFiles int) {
    failing := []syntaxHealthRow{}
    for _, row := range rows {
        if !row.SyntaxOK {
            failing = append(failing, row)
        }
    }
    if maxFiles < 0 {
        maxFiles = 0
    }
    returned := failing
    truncated := false
    if maxFiles > 0 && len(failing) > maxFiles {
        returned = failing[:maxFiles]
        truncated = true
    }
    emitStatsJSON(map[string]any{
        "tool": "syntax-health",
        "status": "ok",
        "backend": "tree-sitter-summary",
        "files_seen": len(rows),
        "files_with_syntax_issues": len(failing),
        "syntax_issue_files": returned,
        "syntax_issue_files_truncated": truncated,
    })
}

// cmdSyntaxHealth は対象サブコマンドの引数解析・境界I/O・compact出力を統括します。
func cmdSyntaxHealth(args []string) int {
    flags := flag.NewFlagSet("syntax-health", flag.ContinueOnError)
    flags.SetOutput(io.Discard)
    jsonInput := flags.String("json-input", "", "saved tree-sitter --json-summary file")
    maxFiles := flags.Int("max-files", 80, "maximum failing files returned; 0 means unlimited")
    if err := flags.Parse(args); err != nil {
        emitStatsJSON(map[string]any{"tool": "syntax-health", "status": "invalid_arguments", "error": boundedStatsError(err.Error())})
        return 2
    }

    var data []byte
    if *jsonInput != "" {
        absolute, _ := filepath.Abs(*jsonInput)
        content, err := os.ReadFile(absolute)
        if err != nil {
            status := "input_read_failed"
            if os.IsNotExist(err) {
                status = "input_missing"
            }
            emitStatsJSON(map[string]any{"tool": "syntax-health", "status": status, "input_path": absolute})
            return 2
        }
        data = content
    } else {
        targets := flags.Args()
        if len(targets) == 0 {
            emitStatsJSON(map[string]any{"tool": "syntax-health", "status": "invalid_arguments", "missing_argument": "targets_or_json_input"})
            return 2
        }
        executable, err := exec.LookPath("tree-sitter")
        if err != nil {
            emitStatsJSON(map[string]any{"tool": "syntax-health", "status": "external_backend_unavailable", "backend": "tree-sitter", "error": "tree-sitter executable was not found on PATH"})
            return 2
        }
        commandArgs := append([]string{"parse", "--json-summary"}, targets...)
        command := exec.Command(executable, commandArgs...)
        output, err := command.Output()
        if err != nil && len(strings.TrimSpace(string(output))) == 0 {
            emitStatsJSON(map[string]any{"tool": "syntax-health", "status": "external_backend_failed", "backend": "tree-sitter", "error": boundedStatsError(err.Error())})
            return 2
        }
        data = output
    }

    var payload any
    if err := json.Unmarshal(data, &payload); err != nil {
        emitStatsJSON(map[string]any{"tool": "syntax-health", "status": "input_read_failed", "error": boundedStatsError(err.Error())})
        return 2
    }
    emitSyntaxHealth(normalizeSyntaxHealth(payload), *maxFiles)
    return 0
}
