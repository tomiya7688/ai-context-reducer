package main

import (
    "bytes"
    "encoding/json"
    "flag"
    "io"
    "io/fs"
    "os"
    "os/exec"
    "path/filepath"
    "sort"
    "strings"
)

const statsErrorPathLimit = 20

type statsLanguageMetrics struct {
    FileCount    int   `json:"file_count"`
    LineCount    int   `json:"line_count"`
    ByteCount    int64 `json:"byte_count"`
    CodeCount    *int  `json:"code_count"`
    CommentCount *int  `json:"comment_count"`
    BlankCount   *int  `json:"blank_count"`
    Complexity   *int  `json:"complexity"`
}

type sccLanguageSummary struct {
    Name       string `json:"Name"`
    Bytes      int64  `json:"Bytes"`
    Lines      int    `json:"Lines"`
    Code       int    `json:"Code"`
    Comment    int    `json:"Comment"`
    Blank      int    `json:"Blank"`
    Complexity int    `json:"Complexity"`
    Count      int    `json:"Count"`
}

type portableStatsResult struct {
    Languages           map[string]statsLanguageMetrics
    RecognizedFilesSeen int
    AnalyzedFileCount   int
    AnalyzedLineCount   int
    OversizedFileCount  int
    ReadErrorCount      int
    WalkErrorCount      int
    BinaryLikeFileCount int
    ReadErrorPaths      []string
    WalkErrorPaths      []string
}

var statsLanguageByExt = map[string]string{
    ".py": "Python", ".cs": "CSharp", ".go": "Go", ".c": "C",
    ".h": "C/C++ Header", ".cpp": "C++", ".cc": "C++", ".cxx": "C++",
    ".hpp": "C++ Header", ".hh": "C++ Header", ".gd": "GDScript",
    ".rs": "Rust", ".js": "JavaScript", ".ts": "TypeScript", ".java": "Java",
    ".md": "Markdown", ".json": "JSON", ".yaml": "YAML", ".yml": "YAML",
    ".toml": "TOML", ".xml": "XML", ".html": "HTML", ".css": "CSS",
}

func emitStatsJSON(value any) {
    enc := json.NewEncoder(os.Stdout)
    enc.SetIndent("", "  ")
    _ = enc.Encode(value)
}

func boundedStatsError(text string) string {
    text = strings.TrimSpace(text)
    if len(text) <= 1200 {
        return text
    }
    return text[:1200]
}

func statsIgnoredDir(name string) bool {
    if strings.EqualFold(name, "generated") {
        return true
    }
    return ignoreDirs[strings.ToLower(name)]
}

func lineCount(data []byte) int {
    if len(data) == 0 {
        return 0
    }
    count := bytes.Count(data, []byte{'\n'})
    if data[len(data)-1] != '\n' {
        count++
    }
    return count
}

func buildPortableStats(root string, maxFileBytes int64) (portableStatsResult, error) {
    result := portableStatsResult{
        Languages:      map[string]statsLanguageMetrics{},
        ReadErrorPaths: []string{},
        WalkErrorPaths: []string{},
    }

    err := filepath.WalkDir(root, func(path string, entry fs.DirEntry, visitErr error) error {
        if visitErr != nil {
            if path == root {
                return visitErr
            }
            result.WalkErrorCount++
            if len(result.WalkErrorPaths) < statsErrorPathLimit {
                result.WalkErrorPaths = append(result.WalkErrorPaths, filepath.ToSlash(path))
            }
            return nil
        }
        if entry.IsDir() {
            if path != root && statsIgnoredDir(entry.Name()) {
                return filepath.SkipDir
            }
            return nil
        }

        language := statsLanguageByExt[strings.ToLower(filepath.Ext(path))]
        if language == "" {
            return nil
        }
        result.RecognizedFilesSeen++
        info, infoErr := entry.Info()
        if infoErr != nil {
            result.ReadErrorCount++
            if len(result.ReadErrorPaths) < statsErrorPathLimit {
                result.ReadErrorPaths = append(result.ReadErrorPaths, filepath.ToSlash(path))
            }
            return nil
        }
        if maxFileBytes > 0 && info.Size() > maxFileBytes {
            result.OversizedFileCount++
            return nil
        }
        data, readErr := os.ReadFile(path)
        if readErr != nil {
            result.ReadErrorCount++
            if len(result.ReadErrorPaths) < statsErrorPathLimit {
                result.ReadErrorPaths = append(result.ReadErrorPaths, filepath.ToSlash(path))
            }
            return nil
        }
        sample := data
        if len(sample) > 4096 {
            sample = sample[:4096]
        }
        if bytes.IndexByte(sample, 0) >= 0 {
            result.BinaryLikeFileCount++
            return nil
        }
        lines := lineCount(data)
        row := result.Languages[language]
        row.FileCount++
        row.LineCount += lines
        row.ByteCount += info.Size()
        result.Languages[language] = row
        result.AnalyzedFileCount++
        result.AnalyzedLineCount += lines
        return nil
    })
    return result, err
}

func parseSCCStats(data []byte) (map[string]statsLanguageMetrics, int, int, error) {
    rows := []sccLanguageSummary{}
    if err := json.Unmarshal(data, &rows); err != nil {
        return nil, 0, 0, err
    }
    languages := map[string]statsLanguageMetrics{}
    totalFiles := 0
    totalLines := 0
    for _, raw := range rows {
        if raw.Name == "" {
            continue
        }
        name := raw.Name
        if name == "C#" {
            name = "CSharp"
        }
        code := raw.Code
        comment := raw.Comment
        blank := raw.Blank
        complexity := raw.Complexity
        languages[name] = statsLanguageMetrics{
            FileCount: raw.Count, LineCount: raw.Lines, ByteCount: raw.Bytes,
            CodeCount: &code, CommentCount: &comment, BlankCount: &blank, Complexity: &complexity,
        }
        totalFiles += raw.Count
        totalLines += raw.Lines
    }
    return languages, totalFiles, totalLines, nil
}

func runSCCStats(root string) (map[string]statsLanguageMetrics, int, int, string, string) {
    executable, err := exec.LookPath("scc")
    if err != nil {
        return nil, 0, 0, "unavailable", "scc executable was not found on PATH"
    }
    args := []string{"--format", "json"}
    ignored := []string{}
    for name := range ignoreDirs {
        if name != ".git" && name != ".hg" && name != ".svn" {
            ignored = append(ignored, name)
        }
    }
    ignored = append(ignored, "generated")
    sort.Strings(ignored)
    for _, name := range ignored {
        args = append(args, "--exclude-dir", name)
    }
    args = append(args, root)
    cmd := exec.Command(executable, args...)
    var stderr bytes.Buffer
    cmd.Stderr = &stderr
    output, err := cmd.Output()
    if err != nil {
        message := stderr.String()
        if strings.TrimSpace(message) == "" {
            message = err.Error()
        }
        return nil, 0, 0, "failed", boundedStatsError(message)
    }
    languages, files, lines, parseErr := parseSCCStats(output)
    if parseErr != nil {
        return nil, 0, 0, "failed", boundedStatsError(parseErr.Error())
    }
    return languages, files, lines, "ok", ""
}

func emitPortableStats(root string, limit int64, portable portableStatsResult, status string, fallback map[string]any) {
    payload := map[string]any{
        "tool": "repo-stats", "status": status, "project_root": root, "backend": "portable",
        "recognized_files_seen": portable.RecognizedFilesSeen,
        "analyzed_file_count": portable.AnalyzedFileCount,
        "analyzed_line_count": portable.AnalyzedLineCount,
        "oversized_file_count": portable.OversizedFileCount,
        "read_error_count": portable.ReadErrorCount,
        "walk_error_count": portable.WalkErrorCount,
        "binary_like_file_count": portable.BinaryLikeFileCount,
        "max_file_bytes": limit,
        "languages": portable.Languages,
    }
    if len(portable.ReadErrorPaths) > 0 {
        payload["read_error_paths"] = portable.ReadErrorPaths
    }
    if len(portable.WalkErrorPaths) > 0 {
        payload["walk_error_paths"] = portable.WalkErrorPaths
    }
    if fallback != nil {
        payload["backend_fallback"] = fallback
    }
    emitStatsJSON(payload)
}

func cmdStats(args []string) int {
    flags := flag.NewFlagSet("stats", flag.ContinueOnError)
    flags.SetOutput(io.Discard)
    maxFileBytes := flags.Int64("max-file-bytes", 0, "portable per-file safety limit; 0 means unlimited")
    backend := flags.String("backend", "auto", "auto, portable, or scc")
    if err := flags.Parse(args); err != nil {
        emitStatsJSON(map[string]any{"tool": "repo-stats", "status": "invalid_arguments", "error": boundedStatsError(err.Error())})
        return 2
    }
    if *backend != "auto" && *backend != "portable" && *backend != "scc" {
        emitStatsJSON(map[string]any{"tool": "repo-stats", "status": "invalid_arguments", "invalid_backend": *backend})
        return 2
    }
    root := "."
    if flags.NArg() > 0 {
        root = flags.Arg(0)
    }
    absoluteRoot, err := filepath.Abs(root)
    if err != nil {
        emitStatsJSON(map[string]any{"tool": "repo-stats", "status": "input_unavailable", "project_root": root, "error": boundedStatsError(err.Error())})
        return 2
    }
    info, statErr := os.Stat(absoluteRoot)
    if statErr != nil {
        status := "input_unavailable"
        if os.IsNotExist(statErr) {
            status = "input_missing"
        }
        emitStatsJSON(map[string]any{"tool": "repo-stats", "status": status, "project_root": absoluteRoot})
        return 2
    }
    if !info.IsDir() {
        emitStatsJSON(map[string]any{"tool": "repo-stats", "status": "input_not_directory", "project_root": absoluteRoot})
        return 2
    }
    limit := *maxFileBytes
    if limit < 0 {
        limit = 0
    }
    if *backend == "scc" && limit > 0 {
        emitStatsJSON(map[string]any{
            "tool": "repo-stats", "status": "backend_query_unsupported", "project_root": absoluteRoot,
            "backend": "scc", "unsupported_feature": "max_file_bytes",
        })
        return 2
    }

    _, lookupErr := exec.LookPath("scc")
    sccAvailable := lookupErr == nil
    shouldTrySCC := limit == 0 && (*backend == "scc" || (*backend == "auto" && sccAvailable))
    if shouldTrySCC {
        languages, files, lines, backendStatus, backendError := runSCCStats(absoluteRoot)
        if backendStatus == "ok" {
            emitStatsJSON(map[string]any{
                "tool": "repo-stats", "status": "ok", "project_root": absoluteRoot, "backend": "scc",
                "recognized_files_seen": files, "analyzed_file_count": files, "analyzed_line_count": lines,
                "oversized_file_count": 0, "read_error_count": 0, "walk_error_count": 0,
                "binary_like_file_count": 0, "max_file_bytes": int64(0), "languages": languages,
            })
            return 0
        }
        if *backend == "scc" {
            status := "external_backend_failed"
            if backendStatus == "unavailable" {
                status = "external_backend_unavailable"
            }
            emitStatsJSON(map[string]any{
                "tool": "repo-stats", "status": status, "project_root": absoluteRoot,
                "backend": "scc", "error": backendError,
            })
            return 2
        }
        portable, portableErr := buildPortableStats(absoluteRoot, limit)
        if portableErr != nil {
            emitStatsJSON(map[string]any{"tool": "repo-stats", "status": "stats_failed", "project_root": absoluteRoot, "backend": "portable", "error": boundedStatsError(portableErr.Error())})
            return 2
        }
        status := "ok_with_backend_fallback"
        if portable.ReadErrorCount+portable.WalkErrorCount > 0 {
            status = "partial"
        }
        emitPortableStats(absoluteRoot, limit, portable, status, map[string]any{"backend": "scc", "status": "failed", "error": backendError})
        return 0
    }

    if *backend == "scc" {
        status := "external_backend_unavailable"
        errorText := "scc executable was not found on PATH"
        if sccAvailable {
            status = "backend_query_unsupported"
            errorText = "max_file_bytes is not supported by the scc backend"
        }
        emitStatsJSON(map[string]any{
            "tool": "repo-stats", "status": status, "project_root": absoluteRoot,
            "backend": "scc", "error": errorText,
        })
        return 2
    }

    portable, portableErr := buildPortableStats(absoluteRoot, limit)
    if portableErr != nil {
        emitStatsJSON(map[string]any{"tool": "repo-stats", "status": "stats_failed", "project_root": absoluteRoot, "backend": "portable", "error": boundedStatsError(portableErr.Error())})
        return 2
    }
    status := "ok"
    if portable.ReadErrorCount+portable.WalkErrorCount > 0 {
        status = "partial"
    }
    emitPortableStats(absoluteRoot, limit, portable, status, nil)
    return 0
}
