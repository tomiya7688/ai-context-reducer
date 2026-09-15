package main

import (
    "flag"
    "io"
    "os"
    "path/filepath"
    "sort"
    "strings"
)

type hotspotRow struct {
    Path  string `json:"path"`
    Bytes int64  `json:"bytes"`
    Depth int    `json:"depth"`
}

func cmdHotspotReport(args []string) int {
    fs := flag.NewFlagSet("hotspot-report", flag.ContinueOnError)
    fs.SetOutput(io.Discard)
    limit := fs.Int("limit", 30, "maximum hotspots returned; 0 returns none")
    maxFiles := fs.Int("max-files", 0, "optional safety limit; 0 means unlimited")
    if err := fs.Parse(args); err != nil {
        emitStructureJSON(map[string]any{"tool": "hotspot-report", "status": "invalid_arguments", "error": err.Error()})
        return 2
    }

    root := "."
    if fs.NArg() > 0 {
        root = fs.Arg(0)
    }
    rootAbs, err := filepath.Abs(root)
    if err != nil {
        emitStructureJSON(map[string]any{"tool": "hotspot-report", "status": "input_read_failed", "root": root, "error": err.Error()})
        return 2
    }
    info, err := os.Stat(rootAbs)
    if err != nil {
        status := "input_read_failed"
        if os.IsNotExist(err) {
            status = "input_missing"
        }
        emitStructureJSON(map[string]any{"tool": "hotspot-report", "status": status, "root": rootAbs})
        return 2
    }
    if !info.IsDir() {
        emitStructureJSON(map[string]any{"tool": "hotspot-report", "status": "input_not_directory", "root": rootAbs})
        return 2
    }

    walked, err := walkWithOptions(rootAbs, false)
    if err != nil {
        emitStructureJSON(map[string]any{"tool": "hotspot-report", "status": "input_read_failed", "root": rootAbs, "error": err.Error()})
        return 2
    }

    rows := []hotspotRow{}
    truncated := false
    for _, file := range walked.Files {
        rel, relErr := filepath.Rel(rootAbs, file.Path)
        if relErr != nil {
            walked.ErrorCount++
            continue
        }
        slash := filepath.ToSlash(rel)
        depth := 1
        if slash != "." && slash != "" {
            depth = strings.Count(slash, "/") + 1
        }
        rows = append(rows, hotspotRow{Path: slash, Bytes: file.Size, Depth: depth})
        if *maxFiles > 0 && len(rows) >= *maxFiles {
            truncated = len(walked.Files) > len(rows)
            break
        }
    }

    sort.Slice(rows, func(i, j int) bool {
        if rows[i].Bytes != rows[j].Bytes {
            return rows[i].Bytes > rows[j].Bytes
        }
        if rows[i].Depth != rows[j].Depth {
            return rows[i].Depth > rows[j].Depth
        }
        return rows[i].Path > rows[j].Path
    })

    resultLimit := *limit
    if resultLimit < 0 {
        resultLimit = 0
    }
    returned := rows
    if resultLimit == 0 {
        returned = []hotspotRow{}
    } else if len(returned) > resultLimit {
        returned = returned[:resultLimit]
    }
    status := "ok"
    if walked.ErrorCount > 0 {
        status = "ok_with_warnings"
    }
    emitStructureJSON(map[string]any{
        "tool": "hotspot-report",
        "status": status,
        "root": rootAbs,
        "scanned_file_count": len(rows),
        "stat_error_count": 0,
        "walk_error_count": walked.ErrorCount,
        "scan_truncated": truncated,
        "hotspot_count": len(rows),
        "hotspots": returned,
        "hotspots_truncated": len(rows) > len(returned),
    })
    return 0
}
