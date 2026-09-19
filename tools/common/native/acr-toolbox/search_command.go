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
    "regexp"
    "sort"
    "strconv"
    "strings"
)

const searchErrorPathLimit = 20

var errSearchEnough = errors.New("search result limit reached")

type searchStringList []string

// String はこの責務内の変換・routingを局所化し、呼び出し側のworking setを増やさないための処理です。
func (s *searchStringList) String() string { return strings.Join(*s, ",") }
// Set はこの責務内の変換・routingを局所化し、呼び出し側のworking setを増やさないための処理です。
func (s *searchStringList) Set(value string) error {
    *s = append(*s, value)
    return nil
}

type searchContextLine struct {
    Line int    `json:"line"`
    Text string `json:"text"`
}

type searchMatch struct {
    Path   string              `json:"path"`
    Line   int                 `json:"line"`
    Text   string              `json:"text"`
    Before []searchContextLine `json:"before,omitempty"`
    After  []searchContextLine `json:"after,omitempty"`
}

type searchStats struct {
    WalkErrorCount int
    StatErrorCount int
    ReadErrorCount int
    WalkErrorPaths []string
    StatErrorPaths []string
    ReadErrorPaths []string
}

type rgJSONMessage struct {
    Type string `json:"type"`
    Data struct {
        Path struct {
            Text string `json:"text"`
        } `json:"path"`
        Lines struct {
            Text string `json:"text"`
        } `json:"lines"`
        LineNumber int `json:"line_number"`
    } `json:"data"`
}

// emitSearchJSON は内部結果を安定した利用者向け出力へ変換します。
func emitSearchJSON(value any) {
    enc := json.NewEncoder(os.Stdout)
    enc.SetIndent("", "  ")
    _ = enc.Encode(value)
}

// searchNonNegative は広い探索結果から条件に合う対象だけを絞り込みます。
func searchNonNegative(value int) int {
    if value < 0 {
        return 0
    }
    return value
}

// boundedSearchError はこの責務内の変換・routingを局所化し、呼び出し側のworking setを増やさないための処理です。
func boundedSearchError(text string) string {
    text = strings.TrimSpace(text)
    if len(text) <= 1200 {
        return text
    }
    return text[:1200]
}

// searchGlobMatch は広い探索結果から条件に合う対象だけを絞り込みます。
func searchGlobMatch(rel, name, pattern string) bool {
    if ok, err := pathpkg.Match(pattern, name); err == nil && ok {
        return true
    }
    ok, err := pathpkg.Match(pattern, rel)
    return err == nil && ok
}

// searchAllowedPath は広い探索結果から条件に合う対象だけを絞り込みます。
func searchAllowedPath(rel, name string, globs, excludes []string) bool {
    for _, pattern := range excludes {
        if searchGlobMatch(rel, name, pattern) {
            return false
        }
    }
    if len(globs) == 0 {
        return true
    }
    for _, pattern := range globs {
        if searchGlobMatch(rel, name, pattern) {
            return true
        }
    }
    return false
}

// portableSearch はこの責務内の変換・routingを局所化し、呼び出し側のworking setを増やさないための処理です。
func portableSearch(
    root, pattern string,
    ignoreCase, fixedString bool,
    globs, excludes []string,
    maxResults int,
    maxFileBytes int64,
    context int,
) ([]searchMatch, bool, searchStats, error) {
    stats := searchStats{WalkErrorPaths: []string{}, StatErrorPaths: []string{}, ReadErrorPaths: []string{}}
    matches := []searchMatch{}
    wanted := 0
    if maxResults > 0 {
        wanted = maxResults + 1
    }

    var expression *regexp.Regexp
    var err error
    if !fixedString {
        source := pattern
        if ignoreCase {
            source = "(?i)" + source
        }
        expression, err = regexp.Compile(source)
        if err != nil {
            return nil, false, stats, err
        }
    }
    fixedNeedle := pattern
    if fixedString && ignoreCase {
        fixedNeedle = strings.ToLower(pattern)
    }

    walkErr := filepath.WalkDir(root, func(path string, entry fs.DirEntry, visitErr error) error {
        if visitErr != nil {
            if path == root {
                return visitErr
            }
            stats.WalkErrorCount++
            if len(stats.WalkErrorPaths) < searchErrorPathLimit {
                stats.WalkErrorPaths = append(stats.WalkErrorPaths, filepath.ToSlash(path))
            }
            return nil
        }
        if entry.IsDir() {
            if path != root && ignoreDirs[strings.ToLower(entry.Name())] {
                return filepath.SkipDir
            }
            return nil
        }

        rel, relErr := filepath.Rel(root, path)
        if relErr != nil {
            stats.StatErrorCount++
            if len(stats.StatErrorPaths) < searchErrorPathLimit {
                stats.StatErrorPaths = append(stats.StatErrorPaths, filepath.ToSlash(path))
            }
            return nil
        }
        rel = filepath.ToSlash(rel)
        if !searchAllowedPath(rel, entry.Name(), globs, excludes) {
            return nil
        }
        info, infoErr := entry.Info()
        if infoErr != nil {
            stats.StatErrorCount++
            if len(stats.StatErrorPaths) < searchErrorPathLimit {
                stats.StatErrorPaths = append(stats.StatErrorPaths, rel)
            }
            return nil
        }
        if maxFileBytes > 0 && info.Size() > maxFileBytes {
            return nil
        }
        data, readErr := os.ReadFile(path)
        if readErr != nil {
            stats.ReadErrorCount++
            if len(stats.ReadErrorPaths) < searchErrorPathLimit {
                stats.ReadErrorPaths = append(stats.ReadErrorPaths, rel)
            }
            return nil
        }
        sample := data
        if len(sample) > 4096 {
            sample = sample[:4096]
        }
        if bytes.IndexByte(sample, 0) >= 0 {
            return nil
        }
        text := strings.ReplaceAll(string(data), "\r\n", "\n")
        text = strings.ReplaceAll(text, "\r", "\n")
        lines := strings.Split(text, "\n")
        for index, line := range lines {
            matched := false
            if fixedString {
                haystack := line
                if ignoreCase {
                    haystack = strings.ToLower(line)
                }
                matched = strings.Contains(haystack, fixedNeedle)
            } else {
                matched = expression.MatchString(line)
            }
            if !matched {
                continue
            }
            item := searchMatch{Path: rel, Line: index + 1, Text: line}
            if context > 0 {
                start := index - context
                if start < 0 {
                    start = 0
                }
                for n := start; n < index; n++ {
                    item.Before = append(item.Before, searchContextLine{Line: n + 1, Text: lines[n]})
                }
                end := index + context + 1
                if end > len(lines) {
                    end = len(lines)
                }
                for n := index + 1; n < end; n++ {
                    item.After = append(item.After, searchContextLine{Line: n + 1, Text: lines[n]})
                }
            }
            matches = append(matches, item)
            if wanted > 0 && len(matches) >= wanted {
                return errSearchEnough
            }
        }
        return nil
    })
    if walkErr != nil && !errors.Is(walkErr, errSearchEnough) {
        return nil, false, stats, walkErr
    }
    truncated := wanted > 0 && len(matches) >= wanted
    if truncated {
        matches = matches[:maxResults]
    }
    return matches, truncated, stats, nil
}

// ripgrepSearch はこの責務内の変換・routingを局所化し、呼び出し側のworking setを増やさないための処理です。
func ripgrepSearch(
    executable, root, pattern string,
    ignoreCase, fixedString bool,
    globs, excludes []string,
    maxResults int,
    maxFileBytes int64,
) ([]searchMatch, bool, string) {
    args := []string{"--json", "--color", "never", "--hidden", "--no-ignore"}
    if ignoreCase {
        args = append(args, "--ignore-case")
    }
    if fixedString {
        args = append(args, "--fixed-strings")
    }
    if maxFileBytes > 0 {
        args = append(args, "--max-filesize", strconv.FormatInt(maxFileBytes, 10))
    }
    ignoreNames := make([]string, 0, len(ignoreDirs)+1)
    for name := range ignoreDirs {
        ignoreNames = append(ignoreNames, name)
    }
    ignoreNames = append(ignoreNames, "generated")
    sort.Strings(ignoreNames)
    for _, name := range ignoreNames {
        args = append(args, "--glob", "!**/"+name+"/**")
    }
    for _, pattern := range globs {
        args = append(args, "--glob", pattern)
    }
    for _, pattern := range excludes {
        args = append(args, "--glob", "!"+pattern)
    }
    args = append(args, "--", pattern, ".")

    cmd := exec.Command(executable, args...)
    cmd.Dir = root
    stdout, err := cmd.StdoutPipe()
    if err != nil {
        return nil, false, boundedSearchError(err.Error())
    }
    var stderr bytes.Buffer
    cmd.Stderr = &stderr
    if err := cmd.Start(); err != nil {
        return nil, false, boundedSearchError(err.Error())
    }

    matches := []searchMatch{}
    truncated := false
    wanted := 0
    if maxResults > 0 {
        wanted = maxResults + 1
    }
    scanner := bufio.NewScanner(stdout)
    scanner.Buffer(make([]byte, 64*1024), 8*1024*1024)
    for scanner.Scan() {
        var message rgJSONMessage
        if err := json.Unmarshal(scanner.Bytes(), &message); err != nil || message.Type != "match" {
            continue
        }
        if message.Data.Path.Text == "" || message.Data.LineNumber <= 0 {
            continue
        }
        path := strings.TrimPrefix(filepath.ToSlash(message.Data.Path.Text), "./")
        text := strings.TrimRight(message.Data.Lines.Text, "\r\n")
        matches = append(matches, searchMatch{Path: path, Line: message.Data.LineNumber, Text: text})
        if wanted > 0 && len(matches) >= wanted {
            truncated = true
            _ = cmd.Process.Kill()
            break
        }
    }
    scanErr := scanner.Err()
    waitErr := cmd.Wait()
    if truncated {
        return matches[:maxResults], true, ""
    }
    if scanErr != nil {
        return nil, false, boundedSearchError(scanErr.Error())
    }
    if waitErr != nil {
        if exitErr, ok := waitErr.(*exec.ExitError); ok && exitErr.ExitCode() == 1 {
            return matches, false, ""
        }
        message := stderr.String()
        if strings.TrimSpace(message) == "" {
            message = waitErr.Error()
        }
        return nil, false, boundedSearchError(message)
    }
    return matches, false, ""
}

// cmdSearch は対象サブコマンドの引数解析・境界I/O・compact出力を統括します。
func cmdSearch(args []string) int {
    flags := flag.NewFlagSet("search", flag.ContinueOnError)
    flags.SetOutput(io.Discard)
    var ignoreCase bool
    var fixedString bool
    flags.BoolVar(&ignoreCase, "i", false, "ignore case")
    flags.BoolVar(&ignoreCase, "ignore-case", false, "ignore case")
    flags.BoolVar(&fixedString, "F", false, "fixed string")
    flags.BoolVar(&fixedString, "fixed-string", false, "fixed string")
    globs := searchStringList{}
    excludes := searchStringList{}
    flags.Var(&globs, "g", "include glob; repeatable")
    flags.Var(&globs, "glob", "include glob; repeatable")
    flags.Var(&excludes, "exclude", "exclude glob; repeatable")
    maxResults := flags.Int("max-results", 100, "maximum matches; 0 means unlimited")
    maxFileBytes := flags.Int64("max-file-bytes", 2_000_000, "skip larger files; 0 means unlimited")
    contextLines := flags.Int("context", 0, "context lines")
    backend := flags.String("backend", "auto", "auto, portable, or ripgrep")
    if err := flags.Parse(args); err != nil {
        emitSearchJSON(map[string]any{"tool": "text-search", "status": "invalid_arguments", "error": boundedSearchError(err.Error())})
        return 2
    }
    if flags.NArg() < 1 {
        emitSearchJSON(map[string]any{"tool": "text-search", "status": "invalid_arguments", "required_argument": "pattern"})
        return 2
    }
    if *backend != "auto" && *backend != "portable" && *backend != "ripgrep" {
        emitSearchJSON(map[string]any{"tool": "text-search", "status": "invalid_arguments", "invalid_backend": *backend})
        return 2
    }

    pattern := flags.Arg(0)
    root := "."
    if flags.NArg() > 1 {
        root = flags.Arg(1)
    }
    absoluteRoot, err := filepath.Abs(root)
    if err != nil {
        emitSearchJSON(map[string]any{"tool": "text-search", "status": "input_unavailable", "root_path": root, "error": boundedSearchError(err.Error())})
        return 2
    }
    context := searchNonNegative(*contextLines)
    query := map[string]any{
        "pattern": pattern,
        "mode": map[bool]string{true: "fixed_string", false: "regex"}[fixedString],
        "ignore_case": ignoreCase,
        "globs": []string(globs),
        "excludes": []string(excludes),
        "context_lines": context,
    }
    info, statErr := os.Stat(absoluteRoot)
    if statErr != nil {
        status := "input_unavailable"
        if os.IsNotExist(statErr) {
            status = "input_missing"
        }
        emitSearchJSON(map[string]any{"tool": "text-search", "status": status, "root_path": absoluteRoot, "query": query})
        return 2
    }
    if !info.IsDir() {
        emitSearchJSON(map[string]any{"tool": "text-search", "status": "input_not_directory", "root_path": absoluteRoot, "query": query})
        return 2
    }
    if !fixedString {
        source := pattern
        if ignoreCase {
            source = "(?i)" + source
        }
        if _, err := regexp.Compile(source); err != nil {
            emitSearchJSON(map[string]any{"tool": "text-search", "status": "invalid_pattern", "root_path": absoluteRoot, "query": query, "error": boundedSearchError(err.Error())})
            return 2
        }
    }

    resultsLimit := searchNonNegative(*maxResults)
    fileBytes := *maxFileBytes
    if fileBytes < 0 {
        fileBytes = 0
    }
    rgPath, rgErr := exec.LookPath("rg")
    canUseRG := context == 0
    if *backend == "ripgrep" && rgErr != nil {
        emitSearchJSON(map[string]any{"tool": "text-search", "status": "external_backend_unavailable", "root_path": absoluteRoot, "query": query, "backend": "ripgrep"})
        return 2
    }
    if *backend == "ripgrep" && !canUseRG {
        emitSearchJSON(map[string]any{"tool": "text-search", "status": "backend_query_unsupported", "root_path": absoluteRoot, "query": query, "backend": "ripgrep", "unsupported_feature": "context_lines"})
        return 2
    }

    useRG := *backend == "ripgrep" || (*backend == "auto" && rgErr == nil && canUseRG)
    var fallback map[string]any
    if useRG && rgErr == nil {
        matches, truncated, backendError := ripgrepSearch(rgPath, absoluteRoot, pattern, ignoreCase, fixedString, []string(globs), []string(excludes), resultsLimit, fileBytes)
        if backendError == "" {
            emitSearchJSON(map[string]any{
                "tool": "text-search", "status": "ok", "root_path": absoluteRoot,
                "query": query, "backend": "ripgrep", "matches": matches, "matches_truncated": truncated,
            })
            return 0
        }
        if *backend == "ripgrep" {
            emitSearchJSON(map[string]any{"tool": "text-search", "status": "external_backend_failed", "root_path": absoluteRoot, "query": query, "backend": "ripgrep", "error": backendError})
            return 2
        }
        fallback = map[string]any{"backend": "ripgrep", "status": "failed", "error": backendError}
    }

    matches, truncated, stats, portableErr := portableSearch(absoluteRoot, pattern, ignoreCase, fixedString, []string(globs), []string(excludes), resultsLimit, fileBytes, context)
    if portableErr != nil {
        emitSearchJSON(map[string]any{"tool": "text-search", "status": "search_failed", "root_path": absoluteRoot, "query": query, "backend": "portable", "error": boundedSearchError(portableErr.Error())})
        return 2
    }
    warningCount := stats.WalkErrorCount + stats.StatErrorCount + stats.ReadErrorCount
    status := "ok"
    if warningCount > 0 {
        status = "partial"
    } else if fallback != nil {
        status = "ok_with_backend_fallback"
    }
    payload := map[string]any{
        "tool": "text-search", "status": status, "root_path": absoluteRoot,
        "query": query, "backend": "portable", "matches": matches, "matches_truncated": truncated,
        "walk_error_count": stats.WalkErrorCount, "stat_error_count": stats.StatErrorCount, "read_error_count": stats.ReadErrorCount,
    }
    if len(stats.WalkErrorPaths) > 0 {
        payload["walk_error_paths"] = stats.WalkErrorPaths
    }
    if len(stats.StatErrorPaths) > 0 {
        payload["stat_error_paths"] = stats.StatErrorPaths
    }
    if len(stats.ReadErrorPaths) > 0 {
        payload["read_error_paths"] = stats.ReadErrorPaths
    }
    if fallback != nil {
        payload["backend_fallback"] = fallback
    }
    emitSearchJSON(payload)
    return 0
}
