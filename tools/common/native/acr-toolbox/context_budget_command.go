package main

import (
    "flag"
    "io"
    "os"
    "path/filepath"
    "sort"
    "strings"
    "unicode/utf8"
)

var contextTextExtensions = map[string]bool{
    ".py": true, ".cs": true, ".go": true, ".c": true, ".h": true,
    ".cpp": true, ".cc": true, ".cxx": true, ".hpp": true, ".hh": true,
    ".gd": true, ".md": true, ".txt": true, ".rst": true, ".json": true,
    ".yaml": true, ".yml": true, ".toml": true, ".xml": true, ".ini": true,
}

type contextBudgetRow struct {
    Path            string `json:"path"`
    EstimatedTokens int64  `json:"estimated_tokens"`
    Bytes           int64  `json:"bytes"`
}

// contextEstimate はこの責務内の変換・routingを局所化し、呼び出し側のworking setを増やさないための処理です。
func contextEstimate(file fileInfo, mode string) (contextBudgetRow, bool) {
    size := file.Size
    estimateBasis := size
    if mode == "accurate" {
        data, err := os.ReadFile(file.Path)
        if err != nil {
            return contextBudgetRow{}, false
        }
        valid := strings.ToValidUTF8(string(data), "")
        size = int64(len([]byte(valid)))
        estimateBasis = int64(utf8.RuneCountInString(valid))
    }
    tokens := estimateBasis / 4
    if tokens < 1 {
        tokens = 1
    }
    return contextBudgetRow{EstimatedTokens: tokens, Bytes: size}, true
}

// cmdContextBudget は対象サブコマンドの引数解析・境界I/O・compact出力を統括します。
func cmdContextBudget(args []string) int {
    fs := flag.NewFlagSet("context-budget", flag.ContinueOnError)
    fs.SetOutput(io.Discard)
    top := fs.Int("top", 40, "maximum largest candidates returned; 0 returns none")
    mode := fs.String("mode", "fast", "fast or accurate")
    maxFiles := fs.Int("max-files", 0, "optional safety limit; 0 means unlimited")
    includeIgnored := fs.Bool("include-ignored", false, "include normally ignored dependency/generated directories")
    if err := fs.Parse(args); err != nil {
        emitStructureJSON(map[string]any{"tool": "context-budget", "status": "invalid_arguments", "error": err.Error()})
        return 2
    }
    if *mode != "fast" && *mode != "accurate" {
        emitStructureJSON(map[string]any{"tool": "context-budget", "status": "invalid_arguments", "error": "mode must be fast or accurate"})
        return 2
    }

    root := "."
    if fs.NArg() > 0 {
        root = fs.Arg(0)
    }
    rootAbs, err := filepath.Abs(root)
    if err != nil {
        emitStructureJSON(map[string]any{"tool": "context-budget", "status": "input_read_failed", "root_path": root, "error": err.Error()})
        return 2
    }
    info, err := os.Stat(rootAbs)
    if err != nil {
        status := "input_read_failed"
        if os.IsNotExist(err) {
            status = "input_missing"
        }
        emitStructureJSON(map[string]any{"tool": "context-budget", "status": status, "root_path": rootAbs})
        return 2
    }
    if !info.IsDir() {
        emitStructureJSON(map[string]any{"tool": "context-budget", "status": "input_not_directory", "root_path": rootAbs})
        return 2
    }

    walked, err := walkWithOptions(rootAbs, *includeIgnored)
    if err != nil {
        emitStructureJSON(map[string]any{"tool": "context-budget", "status": "input_read_failed", "root_path": rootAbs, "error": err.Error()})
        return 2
    }

    rows := []contextBudgetRow{}
    estimationErrors := 0
    scanned := 0
    truncated := false
    total := int64(0)
    for _, file := range walked.Files {
        if !contextTextExtensions[strings.ToLower(filepath.Ext(file.Path))] {
            continue
        }
        if *maxFiles > 0 && scanned >= *maxFiles {
            truncated = true
            break
        }
        row, ok := contextEstimate(file, *mode)
        if !ok {
            estimationErrors++
            continue
        }
        rel, relErr := filepath.Rel(rootAbs, file.Path)
        if relErr != nil {
            estimationErrors++
            continue
        }
        row.Path = filepath.ToSlash(rel)
        rows = append(rows, row)
        total += row.EstimatedTokens
        scanned++
    }

    sort.Slice(rows, func(i, j int) bool {
        if rows[i].EstimatedTokens != rows[j].EstimatedTokens {
            return rows[i].EstimatedTokens > rows[j].EstimatedTokens
        }
        if rows[i].Bytes != rows[j].Bytes {
            return rows[i].Bytes > rows[j].Bytes
        }
        return rows[i].Path > rows[j].Path
    })
    limit := *top
    if limit < 0 {
        limit = 0
    }
    returned := rows
    if limit == 0 {
        returned = []contextBudgetRow{}
    } else if len(returned) > limit {
        returned = returned[:limit]
    }

    status := "ok"
    if estimationErrors+walked.ErrorCount > 0 {
        status = "ok_with_warnings"
    }
    formula := "file_size_bytes_div_4"
    readsContents := false
    if *mode == "accurate" {
        formula = "decoded_text_characters_div_4"
        readsContents = true
    }
    emitStructureJSON(map[string]any{
        "tool":      "context-budget",
        "status":    status,
        "mode":      *mode,
        "root_path": rootAbs,
        "token_estimate": map[string]any{
            "unit": "estimated_tokens",
            "approximate": true,
            "formula": formula,
            "reads_file_contents": readsContents,
            "note": "This is a routing estimate, not tokenizer-exact token counting.",
        },
        "estimated_total_tokens_if_all_candidates_read": total,
        "scanned_text_files": scanned,
        "estimation_error_count": estimationErrors,
        "walk_error_count": walked.ErrorCount,
        "scan_truncated": truncated,
        "largest_context_candidates": returned,
        "largest_context_candidates_truncated": len(rows) > len(returned),
    })
    return 0
}
