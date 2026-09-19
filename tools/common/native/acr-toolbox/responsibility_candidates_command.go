package main

import (
    "errors"
    "flag"
    "fmt"
    "io"
    "io/fs"
    "os"
    "path/filepath"
    "sort"
    "strings"
)

var responsibilityCodeExts = map[string]bool{
    ".py": true, ".cs": true, ".go": true, ".c": true, ".h": true,
    ".cpp": true, ".cc": true, ".cxx": true, ".hpp": true, ".hh": true,
    ".gd": true, ".rs": true, ".java": true, ".js": true, ".ts": true,
}

var errStopResponsibilityScan = errors.New("responsibility scan limit exceeded")

type responsibilityCandidateRow struct {
    Path          string
    Size          int64
    SizeAvailable bool
}

// responsibilityIgnoredDir はこの責務内の変換・routingを局所化し、呼び出し側のworking setを増やさないための処理です。
func responsibilityIgnoredDir(name string) bool {
    lower := strings.ToLower(name)
    return ignoreDirs[lower] || lower == "generated"
}

// scanResponsibilityCandidates は対象scopeを走査し、agentへ渡す候補情報を収集します。
func scanResponsibilityCandidates(root string, maxScanFiles int) ([]responsibilityCandidateRow, int, bool, int, int, error) {
    rows := []responsibilityCandidateRow{}
    scanned := 0
    truncated := false
    statErrors := 0
    walkErrors := 0

    walkErr := filepath.WalkDir(root, func(path string, entry fs.DirEntry, visitErr error) error {
        if visitErr != nil {
            if path == root {
                return visitErr
            }
            walkErrors++
            return nil
        }
        if entry.IsDir() {
            if path != root && responsibilityIgnoredDir(entry.Name()) {
                return filepath.SkipDir
            }
            return nil
        }
        if !responsibilityCodeExts[strings.ToLower(filepath.Ext(path))] {
            return nil
        }
        if maxScanFiles > 0 && scanned >= maxScanFiles {
            truncated = true
            return errStopResponsibilityScan
        }
        scanned++
        rel, err := filepath.Rel(root, path)
        if err != nil {
            walkErrors++
            return nil
        }
        row := responsibilityCandidateRow{Path: filepath.ToSlash(rel)}
        info, err := entry.Info()
        if err != nil {
            statErrors++
        } else {
            row.Size = info.Size()
            row.SizeAvailable = true
        }
        rows = append(rows, row)
        return nil
    })
    if walkErr != nil && !errors.Is(walkErr, errStopResponsibilityScan) {
        return nil, scanned, truncated, statErrors, walkErrors, walkErr
    }
    return rows, scanned, truncated, statErrors, walkErrors, nil
}

// sortResponsibilityCandidates はこの責務内の変換・routingを局所化し、呼び出し側のworking setを増やさないための処理です。
func sortResponsibilityCandidates(rows []responsibilityCandidateRow) {
    sort.Slice(rows, func(i, j int) bool {
        if rows[i].SizeAvailable != rows[j].SizeAvailable {
            return rows[i].SizeAvailable
        }
        if rows[i].Size != rows[j].Size {
            return rows[i].Size > rows[j].Size
        }
        return rows[i].Path > rows[j].Path
    })
}

// renderResponsibilityCandidates は内部結果を安定した利用者向け出力へ変換します。
func renderResponsibilityCandidates(rows []responsibilityCandidateRow, maxRows, scanned int, scanTruncated bool, statErrors, walkErrors int) string {
    if maxRows < 0 {
        maxRows = 0
    }
    sortResponsibilityCandidates(rows)
    var out strings.Builder
    out.WriteString("| Path | Size | Responsibility |\n")
    out.WriteString("|---|---:|---|\n")
    returned := 0
    if maxRows > 0 {
        returned = len(rows)
        if returned > maxRows {
            returned = maxRows
        }
        for _, row := range rows[:returned] {
            sizeText := "unavailable"
            if row.SizeAvailable {
                sizeText = fmt.Sprintf("%d", row.Size)
            }
            fmt.Fprintf(&out, "| `%s` | %s | TODO: describe ownership in one short sentence |\n", row.Path, sizeText)
        }
    }
    hidden := len(rows) - returned
    if hidden > 0 {
        fmt.Fprintf(&out, "\n<!-- output truncated: %d more scanned code files -->\n", hidden)
    }
    if statErrors > 0 {
        fmt.Fprintf(&out, "<!-- stat warnings: %d code files had unavailable size metadata -->\n", statErrors)
    }
    if walkErrors > 0 {
        fmt.Fprintf(&out, "<!-- walk warnings: %d filesystem entries could not be visited -->\n", walkErrors)
    }
    if scanTruncated {
        fmt.Fprintf(&out, "<!-- scan truncated at %d code files by explicit safety limit -->\n", scanned)
    }
    fmt.Fprintf(&out, "<!-- scanned code files: %d -->\n", scanned)
    return out.String()
}

// cmdResponsibilityCandidates は対象サブコマンドの引数解析・境界I/O・compact出力を統括します。
func cmdResponsibilityCandidates(args []string) int {
    flags := flag.NewFlagSet("responsibility-candidates", flag.ContinueOnError)
    flags.SetOutput(io.Discard)
    maxRows := flags.Int("max", 120, "maximum rows printed; 0 prints no candidate rows")
    maxScanFiles := flags.Int("max-scan-files", 0, "optional safety limit for inspected code files; 0 means unlimited")
    if err := flags.Parse(args); err != nil {
        fmt.Fprintf(os.Stderr, "responsibility-candidates: invalid_arguments: %v\n", err)
        return 2
    }
    root := "."
    if flags.NArg() > 0 {
        root = flags.Arg(0)
    }
    rootAbs, err := filepath.Abs(root)
    if err != nil {
        fmt.Fprintf(os.Stderr, "responsibility-candidates: input_read_failed: %v\n", err)
        return 2
    }
    info, err := os.Stat(rootAbs)
    if err != nil {
        if os.IsNotExist(err) {
            fmt.Fprintf(os.Stderr, "responsibility-candidates: input_missing: %s\n", rootAbs)
        } else {
            fmt.Fprintf(os.Stderr, "responsibility-candidates: input_read_failed: %v\n", err)
        }
        return 2
    }
    if !info.IsDir() {
        fmt.Fprintf(os.Stderr, "responsibility-candidates: input_not_directory: %s\n", rootAbs)
        return 2
    }
    scanLimit := *maxScanFiles
    if scanLimit < 0 {
        scanLimit = 0
    }
    rows, scanned, truncated, statErrors, walkErrors, err := scanResponsibilityCandidates(rootAbs, scanLimit)
    if err != nil {
        fmt.Fprintf(os.Stderr, "responsibility-candidates: input_read_failed: %v\n", err)
        return 2
    }
    fmt.Print(renderResponsibilityCandidates(rows, *maxRows, scanned, truncated, statErrors, walkErrors))
    return 0
}
