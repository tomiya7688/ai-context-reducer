package main

import (
    "flag"
    "io"
    "io/fs"
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
    flags := flag.NewFlagSet("hotspot-report", flag.ContinueOnError)
    flags.SetOutput(io.Discard)
    limit := flags.Int("limit", 30, "maximum hotspots returned; 0 returns none")
    maxFiles := flags.Int("max-files", 0, "optional safety limit; 0 means unlimited")
    if err := flags.Parse(args); err != nil {
        emitStructureJSON(map[string]any{"tool": "hotspot-report", "status": "invalid_arguments", "error": err.Error()})
        return 2
    }

    root := "."
    if flags.NArg() > 0 {
        root = flags.Arg(0)
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

    rows := []hotspotRow{}
    statErrors := 0
    walkErrors := 0
    truncated := false
    stopWalk := false
    walkErr := filepath.WalkDir(rootAbs, func(path string, entry fs.DirEntry, visitErr error) error {
        if stopWalk {
            if entry != nil && entry.IsDir() {
                return filepath.SkipDir
            }
            return nil
        }
        if visitErr != nil {
            walkErrors++
            return nil
        }
        if entry.IsDir() {
            if path != rootAbs && ignoreDirs[strings.ToLower(entry.Name())] {
                return filepath.SkipDir
            }
            return nil
        }
        info, infoErr := entry.Info()
        if infoErr != nil {
            statErrors++
            return nil
        }
        rel, relErr := filepath.Rel(rootAbs, path)
        if relErr != nil {
            walkErrors++
            return nil
        }
        slash := filepath.ToSlash(rel)
        rows = append(rows, hotspotRow{
            Path: slash,
            Bytes: info.Size(),
            Depth: strings.Count(slash, "/") + 1,
        })
        if *maxFiles > 0 && len(rows) >= *maxFiles {
            truncated = true
            stopWalk = true
        }
        return nil
    })
    if walkErr != nil {
        emitStructureJSON(map[string]any{"tool": "hotspot-report", "status": "input_read_failed", "root": rootAbs, "error": walkErr.Error()})
        return 2
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
    if statErrors+walkErrors > 0 {
        status = "ok_with_warnings"
    }
    emitStructureJSON(map[string]any{
        "tool": "hotspot-report",
        "status": status,
        "root": rootAbs,
        "scanned_file_count": len(rows),
        "stat_error_count": statErrors,
        "walk_error_count": walkErrors,
        "scan_truncated": truncated,
        "hotspot_count": len(rows),
        "hotspots": returned,
        "hotspots_truncated": len(rows) > len(returned),
    })
    return 0
}
