package main

import (
    "encoding/json"
    "flag"
    "io"
    "os"
    "path/filepath"
    "sort"
    "strings"
)

var contextManifestHigh = map[string]bool{
    "README.md": true,
    "AI_CONTEXT.md": true,
    "AGENTS.md": true,
    "CLAUDE.md": true,
    "pyproject.toml": true,
    "package.json": true,
    "Cargo.toml": true,
    "go.mod": true,
}

var contextManifestSourceExts = map[string]bool{
    ".py": true, ".cs": true, ".go": true, ".rs": true, ".ts": true,
    ".js": true, ".cpp": true, ".c": true, ".h": true, ".java": true,
}

var contextManifestPriorityOrder = map[string]int{"P0": 0, "P1": 1, "P2": 2, "P3": 3, "P4": 4}

type contextManifestRow struct {
    ContextPriority string `json:"context_priority"`
    Path            string `json:"path"`
    Bytes           int64  `json:"bytes"`
}

func emitContextManifestJSON(value any) {
    enc := json.NewEncoder(os.Stdout)
    enc.SetIndent("", "  ")
    _ = enc.Encode(value)
}

func contextManifestPriority(path string) string {
    clean := filepath.ToSlash(path)
    name := filepath.Base(clean)
    lower := strings.ToLower(clean)
    if contextManifestHigh[name] {
        return "P0"
    }
    if strings.HasPrefix(lower, "tests/") || strings.Contains("/"+lower, "/tests/") {
        return "P2"
    }
    if strings.HasPrefix(lower, "docs/") || strings.Contains("/"+lower, "/docs/") {
        return "P3"
    }
    if contextManifestSourceExts[strings.ToLower(filepath.Ext(clean))] {
        return "P1"
    }
    return "P4"
}

func buildContextManifestRows(root string, files []fileInfo) ([]contextManifestRow, int) {
    rows := make([]contextManifestRow, 0, len(files))
    pathErrors := 0
    for _, file := range files {
        rel, err := filepath.Rel(root, file.Path)
        if err != nil {
            pathErrors++
            continue
        }
        path := filepath.ToSlash(rel)
        rows = append(rows, contextManifestRow{
            ContextPriority: contextManifestPriority(path),
            Path:            path,
            Bytes:           file.Size,
        })
    }
    sort.Slice(rows, func(i, j int) bool {
        left := contextManifestPriorityOrder[rows[i].ContextPriority]
        right := contextManifestPriorityOrder[rows[j].ContextPriority]
        if left != right {
            return left < right
        }
        return rows[i].Path < rows[j].Path
    })
    return rows, pathErrors
}

func cmdContextManifest(args []string) int {
    flags := flag.NewFlagSet("context-manifest", flag.ContinueOnError)
    flags.SetOutput(io.Discard)
    limit := flags.Int("limit", 400, "maximum files returned; 0 returns no file rows while still scanning the full scope")
    if err := flags.Parse(args); err != nil {
        emitContextManifestJSON(map[string]any{"tool": "context-manifest", "status": "invalid_arguments", "error": err.Error()})
        return 2
    }

    root := "."
    if flags.NArg() > 0 {
        root = flags.Arg(0)
    }
    rootAbs, err := filepath.Abs(root)
    if err != nil {
        emitContextManifestJSON(map[string]any{"tool": "context-manifest", "status": "input_read_failed", "root_path": root, "error": err.Error()})
        return 2
    }
    info, err := os.Stat(rootAbs)
    if err != nil {
        status := "input_read_failed"
        if os.IsNotExist(err) {
            status = "input_missing"
        }
        emitContextManifestJSON(map[string]any{"tool": "context-manifest", "status": status, "root_path": rootAbs})
        return 2
    }
    if !info.IsDir() {
        emitContextManifestJSON(map[string]any{"tool": "context-manifest", "status": "input_not_directory", "root_path": rootAbs})
        return 2
    }

    walked, err := walkWithOptions(rootAbs, false)
    if err != nil {
        emitContextManifestJSON(map[string]any{"tool": "context-manifest", "status": "input_read_failed", "root_path": rootAbs, "error": err.Error()})
        return 2
    }
    rows, pathErrors := buildContextManifestRows(rootAbs, walked.Files)
    statErrors := walked.StatErrorCount
    walkErrors := walked.WalkErrorCount + pathErrors
    resultLimit := *limit
    if resultLimit < 0 {
        resultLimit = 0
    }
    returned := rows
    if resultLimit == 0 {
        returned = []contextManifestRow{}
    } else if len(returned) > resultLimit {
        returned = returned[:resultLimit]
    }
    status := "ok"
    if statErrors+walkErrors > 0 {
        status = "ok_with_warnings"
    }
    emitContextManifestJSON(map[string]any{
        "tool":             "context-manifest",
        "status":           status,
        "root_path":        rootAbs,
        "total_files":      len(rows),
        "returned_files":   len(returned),
        "stat_error_count": statErrors,
        "walk_error_count": walkErrors,
        "files_truncated":  len(rows) > len(returned),
        "files":            returned,
    })
    return 0
}
