package main

import (
    "bufio"
    "bytes"
    "encoding/json"
    "errors"
    "flag"
    "io"
    "io/fs"
    "os"
    "os/exec"
    pathpkg "path"
    "path/filepath"
    "sort"
    "strings"
)

const findErrorPathLimit = 20

var (
    errFindEnough    = errors.New("find result limit reached")
    errFindScanLimit = errors.New("find scan limit reached")
)

type findResult struct {
    Path string `json:"path"`
    Kind string `json:"kind"`
}

type findStats struct {
    WalkErrorCount int
    WalkErrorPaths []string
}

func emitFindJSON(value any) {
    enc := json.NewEncoder(os.Stdout)
    enc.SetIndent("", "  ")
    _ = enc.Encode(value)
}

func boundedFindError(text string) string {
    text = strings.TrimSpace(text)
    if len(text) <= 1200 {
        return text
    }
    return text[:1200]
}

func findNonNegative(value int) int {
    if value < 0 {
        return 0
    }
    return value
}

func findPatternMatch(name, rel, pattern string) bool {
    if ok, err := pathpkg.Match(pattern, name); err == nil && ok {
        return true
    }
    ok, err := pathpkg.Match(pattern, rel)
    return err == nil && ok
}

func pathDepth(rel string) int {
    if rel == "" || rel == "." {
        return 0
    }
    return len(strings.Split(filepath.ToSlash(rel), "/"))
}

func portableFind(root, pattern, entryType string, maxResults, maxDepth, maxVisited int) ([]findResult, bool, bool, findStats, error) {
    results := []findResult{}
    stats := findStats{WalkErrorPaths: []string{}}
    visited := 0
    wanted := 0
    if maxResults > 0 {
        wanted = maxResults + 1
    }
    resultsTruncated := false
    scanTruncated := false

    walkErr := filepath.WalkDir(root, func(path string, entry fs.DirEntry, visitErr error) error {
        if visitErr != nil {
            if path == root {
                return visitErr
            }
            stats.WalkErrorCount++
            if len(stats.WalkErrorPaths) < findErrorPathLimit {
                stats.WalkErrorPaths = append(stats.WalkErrorPaths, filepath.ToSlash(path))
            }
            return nil
        }
        if path == root {
            return nil
        }
        if entry.IsDir() && ignoreDirs[strings.ToLower(entry.Name())] {
            return filepath.SkipDir
        }

        rel, err := filepath.Rel(root, path)
        if err != nil {
            stats.WalkErrorCount++
            if len(stats.WalkErrorPaths) < findErrorPathLimit {
                stats.WalkErrorPaths = append(stats.WalkErrorPaths, filepath.ToSlash(path))
            }
            if entry.IsDir() {
                return filepath.SkipDir
            }
            return nil
        }
        rel = filepath.ToSlash(rel)
        depth := pathDepth(rel)
        if maxDepth > 0 && depth > maxDepth {
            if entry.IsDir() {
                return filepath.SkipDir
            }
            return nil
        }

        if maxVisited > 0 && visited >= maxVisited {
            scanTruncated = true
            return errFindScanLimit
        }
        visited++

        kind := "file"
        if entry.IsDir() {
            kind = "dir"
        }
        includeKind := entryType == "any" || entryType == kind
        if includeKind && findPatternMatch(entry.Name(), rel, pattern) {
            results = append(results, findResult{Path: rel, Kind: kind})
            if wanted > 0 && len(results) >= wanted {
                resultsTruncated = true
                return errFindEnough
            }
        }

        if entry.IsDir() && maxDepth > 0 && depth >= maxDepth {
            return filepath.SkipDir
        }
        return nil
    })

    if walkErr != nil && !errors.Is(walkErr, errFindEnough) && !errors.Is(walkErr, errFindScanLimit) {
        return nil, false, scanTruncated, stats, walkErr
    }
    if resultsTruncated {
        results = results[:maxResults]
    }
    return results, resultsTruncated, scanTruncated, stats, nil
}

func fdFind(executable, root, pattern, entryType string, maxResults, maxDepth int) ([]findResult, bool, string) {
    args := []string{"--glob", "--case-sensitive", "--hidden", "--no-ignore", "--color", "never"}
    if entryType == "file" {
        args = append(args, "--type", "file")
    } else if entryType == "dir" {
        args = append(args, "--type", "directory")
    }
    if maxDepth > 0 {
        args = append(args, "--max-depth", strconv.Itoa(maxDepth))
    }
    ignored := make([]string, 0, len(ignoreDirs)+1)
    for name := range ignoreDirs {
        ignored = append(ignored, name)
    }
    ignored = append(ignored, "generated")
    sort.Strings(ignored)
    for _, name := range ignored {
        args = append(args, "--exclude", name)
    }
    args = append(args, "--", pattern, ".")

    cmd := exec.Command(executable, args...)
    cmd.Dir = root
    stdout, err := cmd.StdoutPipe()
    if err != nil {
        return nil, false, boundedFindError(err.Error())
    }
    var stderr bytes.Buffer
    cmd.Stderr = &stderr
    if err := cmd.Start(); err != nil {
        return nil, false, boundedFindError(err.Error())
    }

    results := []findResult{}
    truncated := false
    wanted := 0
    if maxResults > 0 {
        wanted = maxResults + 1
    }
    scanner := bufio.NewScanner(stdout)
    scanner.Buffer(make([]byte, 64*1024), 2*1024*1024)
    for scanner.Scan() {
        rel := strings.TrimSuffix(strings.TrimPrefix(filepath.ToSlash(strings.TrimSpace(scanner.Text())), "./"), "/")
        if rel == "" {
            continue
        }
        kind := entryType
        if kind == "any" {
            info, err := os.Stat(filepath.Join(root, filepath.FromSlash(rel)))
            if err == nil && info.IsDir() {
                kind = "dir"
            } else {
                kind = "file"
            }
        }
        results = append(results, findResult{Path: rel, Kind: kind})
        if wanted > 0 && len(results) >= wanted {
            truncated = true
            _ = cmd.Process.Kill()
            break
        }
    }
    scanErr := scanner.Err()
    waitErr := cmd.Wait()
    if truncated {
        return results[:maxResults], true, ""
    }
    if scanErr != nil {
        return nil, false, boundedFindError(scanErr.Error())
    }
    if waitErr != nil {
        message := stderr.String()
        if strings.TrimSpace(message) == "" {
            message = waitErr.Error()
        }
        return nil, false, boundedFindError(message)
    }
    return results, false, ""
}

func cmdFind(args []string) int {
    flags := flag.NewFlagSet("find", flag.ContinueOnError)
    flags.SetOutput(io.Discard)
    entryType := flags.String("type", "file", "file, dir, or any")
    maxResults := flags.Int("max-results", 200, "maximum results; 0 means unlimited")
    maxDepth := flags.Int("max-depth", 0, "maximum depth; 0 means unlimited")
    maxVisited := flags.Int("max-visited", 0, "portable scan safety cap; 0 means unlimited")
    backend := flags.String("backend", "auto", "auto, portable, or fd")
    if err := flags.Parse(args); err != nil {
        emitFindJSON(map[string]any{"tool": "path-find", "status": "invalid_arguments", "error": boundedFindError(err.Error())})
        return 2
    }
    if *entryType != "file" && *entryType != "dir" && *entryType != "any" {
        emitFindJSON(map[string]any{"tool": "path-find", "status": "invalid_arguments", "invalid_type": *entryType})
        return 2
    }
    if *backend != "auto" && *backend != "portable" && *backend != "fd" {
        emitFindJSON(map[string]any{"tool": "path-find", "status": "invalid_arguments", "invalid_backend": *backend})
        return 2
    }

    pattern := "*"
    root := "."
    if flags.NArg() > 0 {
        pattern = flags.Arg(0)
    }
    if flags.NArg() > 1 {
        root = flags.Arg(1)
    }
    depth := findNonNegative(*maxDepth)
    query := map[string]any{"pattern": pattern, "type": *entryType, "max_depth": depth}

    absoluteRoot, err := filepath.Abs(root)
    if err != nil {
        emitFindJSON(map[string]any{"tool": "path-find", "status": "input_unavailable", "root_path": root, "query": query, "error": boundedFindError(err.Error())})
        return 2
    }
    info, statErr := os.Stat(absoluteRoot)
    if statErr != nil {
        status := "input_unavailable"
        if os.IsNotExist(statErr) {
            status = "input_missing"
        }
        emitFindJSON(map[string]any{"tool": "path-find", "status": status, "root_path": absoluteRoot, "query": query})
        return 2
    }
    if !info.IsDir() {
        emitFindJSON(map[string]any{"tool": "path-find", "status": "input_not_directory", "root_path": absoluteRoot, "query": query})
        return 2
    }
    if _, err := pathpkg.Match(pattern, "probe"); err != nil {
        emitFindJSON(map[string]any{"tool": "path-find", "status": "invalid_pattern", "root_path": absoluteRoot, "query": query, "error": boundedFindError(err.Error())})
        return 2
    }

    limit := findNonNegative(*maxResults)
    visitedLimit := findNonNegative(*maxVisited)
    fdPath, fdErr := exec.LookPath("fd")
    patternUsesPath := strings.ContainsAny(pattern, "/\\")
    canUseFD := !patternUsesPath && visitedLimit == 0
    if *backend == "fd" && fdErr != nil {
        emitFindJSON(map[string]any{"tool": "path-find", "status": "external_backend_unavailable", "root_path": absoluteRoot, "query": query, "backend": "fd"})
        return 2
    }
    if *backend == "fd" && !canUseFD {
        unsupported := "max_visited"
        if patternUsesPath {
            unsupported = "path_pattern"
        }
        emitFindJSON(map[string]any{"tool": "path-find", "status": "backend_query_unsupported", "root_path": absoluteRoot, "query": query, "backend": "fd", "unsupported_feature": unsupported})
        return 2
    }

    useFD := *backend == "fd" || (*backend == "auto" && fdErr == nil && canUseFD)
    var fallback map[string]any
    if useFD && fdErr == nil {
        results, truncated, backendError := fdFind(fdPath, absoluteRoot, pattern, *entryType, limit, depth)
        if backendError == "" {
            emitFindJSON(map[string]any{
                "tool": "path-find", "status": "ok", "root_path": absoluteRoot, "query": query,
                "backend": "fd", "results": results, "results_truncated": truncated, "scan_truncated": false,
            })
            return 0
        }
        if *backend == "fd" {
            emitFindJSON(map[string]any{"tool": "path-find", "status": "external_backend_failed", "root_path": absoluteRoot, "query": query, "backend": "fd", "error": backendError})
            return 2
        }
        fallback = map[string]any{"backend": "fd", "status": "failed", "error": backendError}
    }

    results, resultsTruncated, scanTruncated, stats, portableErr := portableFind(absoluteRoot, pattern, *entryType, limit, depth, visitedLimit)
    if portableErr != nil {
        emitFindJSON(map[string]any{"tool": "path-find", "status": "find_failed", "root_path": absoluteRoot, "query": query, "backend": "portable", "error": boundedFindError(portableErr.Error())})
        return 2
    }
    status := "ok"
    if stats.WalkErrorCount > 0 || scanTruncated {
        status = "partial"
    } else if fallback != nil {
        status = "ok_with_backend_fallback"
    }
    payload := map[string]any{
        "tool": "path-find", "status": status, "root_path": absoluteRoot, "query": query,
        "backend": "portable", "results": results, "results_truncated": resultsTruncated,
        "scan_truncated": scanTruncated, "walk_error_count": stats.WalkErrorCount,
    }
    if len(stats.WalkErrorPaths) > 0 {
        payload["walk_error_paths"] = stats.WalkErrorPaths
    }
    if fallback != nil {
        payload["backend_fallback"] = fallback
    }
    emitFindJSON(payload)
    return 0
}
