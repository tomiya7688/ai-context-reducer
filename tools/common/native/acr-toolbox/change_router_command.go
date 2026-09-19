package main

import (
    "encoding/json"
    "errors"
    "flag"
    "io"
    "io/fs"
    "os"
    "os/exec"
    "path/filepath"
    "strings"
)

var changeRouterDocExts = map[string]bool{".md": true, ".rst": true, ".txt": true}
var changeRouterTestDirs = map[string]bool{"test": true, "tests": true, "spec": true, "specs": true}
var errStopChangeRouterIndex = errors.New("change-router index limit exceeded")

type changeRouterStringList []string

// String はこの責務内の変換・routingを局所化し、呼び出し側のworking setを増やさないための処理です。
func (s *changeRouterStringList) String() string { return strings.Join(*s, ",") }
// Set はこの責務内の変換・routingを局所化し、呼び出し側のworking setを増やさないための処理です。
func (s *changeRouterStringList) Set(value string) error {
    *s = append(*s, value)
    return nil
}

type changeRouterCandidate struct {
    Path   string `json:"path"`
    Name   string `json:"name"`
    IsTest bool   `json:"is_test"`
    IsDoc  bool   `json:"is_doc"`
}

type changeRouterRoute struct {
    ChangedFile             string   `json:"changed_file"`
    CandidateTests          []string `json:"candidate_tests"`
    CandidateTestsTruncated bool     `json:"candidate_tests_truncated"`
    CandidateDocs           []string `json:"candidate_docs"`
    CandidateDocsTruncated  bool     `json:"candidate_docs_truncated"`
}

// emitChangeRouterJSON は内部結果を安定した利用者向け出力へ変換します。
func emitChangeRouterJSON(value any) {
    enc := json.NewEncoder(os.Stdout)
    enc.SetIndent("", "  ")
    _ = enc.Encode(value)
}

// changeRouterDedupe はこの責務内の変換・routingを局所化し、呼び出し側のworking setを増やさないための処理です。
func changeRouterDedupe(values []string) []string {
    out := []string{}
    seen := map[string]bool{}
    for _, value := range values {
        value = strings.TrimSpace(value)
        if value == "" || seen[value] {
            continue
        }
        seen[value] = true
        out = append(out, value)
    }
    return out
}

// changeRouterGitChanged はこの責務内の変換・routingを局所化し、呼び出し側のworking setを増やさないための処理です。
func changeRouterGitChanged(root, base string) (bool, []string, string) {
    executable, err := exec.LookPath("git")
    if err != nil {
        return false, nil, "git_unavailable"
    }
    if base == "" {
        base = "HEAD"
    }
    output, err := exec.Command(executable, "-C", root, "diff", "--name-only", base).Output()
    if err != nil {
        return false, nil, "git_query_failed"
    }
    return true, changeRouterDedupe(strings.Split(string(output), "\n")), ""
}

// changeRouterIsTestCandidate はこの責務内の変換・routingを局所化し、呼び出し側のworking setを増やさないための処理です。
func changeRouterIsTestCandidate(path string, directoryParts []string) bool {
    for _, part := range directoryParts {
        if changeRouterTestDirs[strings.ToLower(part)] {
            return true
        }
    }
    name := strings.ToLower(filepath.Base(path))
    stem := strings.TrimSuffix(name, filepath.Ext(name))
    return strings.HasPrefix(stem, "test_") || strings.HasPrefix(stem, "test-") ||
        strings.HasPrefix(stem, "spec_") || strings.HasPrefix(stem, "spec-") ||
        strings.HasSuffix(stem, "_test") || strings.HasSuffix(stem, "-test") ||
        strings.HasSuffix(stem, "_spec") || strings.HasSuffix(stem, "-spec") ||
        strings.Contains(name, ".test.") || strings.Contains(name, ".spec.")
}

// scanChangeRouterCandidates は対象scopeを走査し、agentへ渡す候補情報を収集します。
func scanChangeRouterCandidates(root string, maxFiles int) ([]changeRouterCandidate, bool, int, error) {
    rows := []changeRouterCandidate{}
    truncated := false
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
            if path != root && ignoreDirs[strings.ToLower(entry.Name())] {
                return filepath.SkipDir
            }
            return nil
        }
        rel, err := filepath.Rel(root, path)
        if err != nil {
            walkErrors++
            return nil
        }
        slash := filepath.ToSlash(rel)
        directory := filepath.ToSlash(filepath.Dir(rel))
        parts := []string{}
        if directory != "." && directory != "" {
            parts = strings.Split(directory, "/")
        }
        isTest := changeRouterIsTestCandidate(path, parts)
        isDoc := changeRouterDocExts[strings.ToLower(filepath.Ext(path))]
        if !isTest && !isDoc {
            return nil
        }
        if maxFiles > 0 && len(rows) >= maxFiles {
            truncated = true
            return errStopChangeRouterIndex
        }
        rows = append(rows, changeRouterCandidate{
            Path: slash,
            Name: strings.ToLower(filepath.Base(path)),
            IsTest: isTest,
            IsDoc: isDoc,
        })
        return nil
    })
    if walkErr != nil && !errors.Is(walkErr, errStopChangeRouterIndex) {
        return nil, truncated, walkErrors, walkErr
    }
    return rows, truncated, walkErrors, nil
}

// changeRouterNormalizedStem はこの責務内の変換・routingを局所化し、呼び出し側のworking setを増やさないための処理です。
func changeRouterNormalizedStem(path string) string {
    name := strings.ToLower(filepath.Base(path))
    stem := strings.TrimSuffix(name, filepath.Ext(name))
    stem = strings.TrimPrefix(stem, "test_")
    stem = strings.TrimSuffix(stem, "_test")
    return stem
}

// routeChangeCandidates はこの責務内の変換・routingを局所化し、呼び出し側のworking setを増やさないための処理です。
func routeChangeCandidates(path string, index []changeRouterCandidate, limit int) changeRouterRoute {
    stem := changeRouterNormalizedStem(path)
    tests := []string{}
    docs := []string{}
    if stem != "" {
        for _, row := range index {
            if !strings.Contains(row.Name, stem) {
                continue
            }
            if row.IsTest {
                tests = append(tests, row.Path)
            } else if row.IsDoc {
                docs = append(docs, row.Path)
            }
        }
    }
    if limit < 0 {
        limit = 0
    }
    returnedTests := tests
    returnedDocs := docs
    if limit > 0 && len(returnedTests) > limit {
        returnedTests = returnedTests[:limit]
    }
    if limit > 0 && len(returnedDocs) > limit {
        returnedDocs = returnedDocs[:limit]
    }
    return changeRouterRoute{
        ChangedFile: path,
        CandidateTests: returnedTests,
        CandidateTestsTruncated: len(tests) > len(returnedTests),
        CandidateDocs: returnedDocs,
        CandidateDocsTruncated: len(docs) > len(returnedDocs),
    }
}

// cmdChangeRouter は対象サブコマンドの引数解析・境界I/O・compact出力を統括します。
func cmdChangeRouter(args []string) int {
    flags := flag.NewFlagSet("change-router", flag.ContinueOnError)
    flags.SetOutput(io.Discard)
    base := flags.String("base", "", "Git diff base; defaults to HEAD")
    changed := changeRouterStringList{}
    flags.Var(&changed, "changed", "explicit changed file; repeatable")
    maxChanged := flags.Int("max-changed", 80, "maximum changed files returned/routed; 0 means unlimited")
    maxIndexFiles := flags.Int("max-index-files", 0, "optional safety limit for indexed test/doc candidates; 0 means unlimited")
    perKind := flags.Int("per-kind", 8, "maximum test/doc candidates per changed file; 0 means unlimited")
    if err := flags.Parse(args); err != nil {
        emitChangeRouterJSON(map[string]any{"tool": "change-router", "status": "invalid_arguments", "error": err.Error()})
        return 2
    }

    root := "."
    if flags.NArg() > 0 {
        root = flags.Arg(0)
    }
    rootAbs, err := filepath.Abs(root)
    if err != nil {
        emitChangeRouterJSON(map[string]any{"tool": "change-router", "status": "input_read_failed", "root_path": root, "error": err.Error()})
        return 2
    }
    info, err := os.Stat(rootAbs)
    if err != nil {
        status := "input_read_failed"
        if os.IsNotExist(err) {
            status = "input_missing"
        }
        emitChangeRouterJSON(map[string]any{"tool": "change-router", "status": status, "root_path": rootAbs})
        return 2
    }
    if !info.IsDir() {
        emitChangeRouterJSON(map[string]any{"tool": "change-router", "status": "input_not_directory", "root_path": rootAbs})
        return 2
    }

    changedSource := "explicit"
    changedFiles := changeRouterDedupe(changed)
    if len(changedFiles) == 0 {
        changedSource = "git_diff"
        ok, lines, errorKind := changeRouterGitChanged(rootAbs, *base)
        if !ok {
            emitChangeRouterJSON(map[string]any{
                "tool": "change-router", "status": "git_diff_unavailable", "root_path": rootAbs,
                "git_error_kind": errorKind, "changed_source": changedSource,
                "changed_files": []string{}, "changed_files_truncated": false,
                "index_candidates": 0, "index_truncated": false, "index_walk_error_count": 0,
                "routes": []changeRouterRoute{},
            })
            return 2
        }
        changedFiles = lines
    }

    changedLimit := *maxChanged
    if changedLimit < 0 {
        changedLimit = 0
    }
    changedTruncated := changedLimit > 0 && len(changedFiles) > changedLimit
    if changedTruncated {
        changedFiles = changedFiles[:changedLimit]
    }
    indexLimit := *maxIndexFiles
    if indexLimit < 0 {
        indexLimit = 0
    }
    index, indexTruncated, walkErrors, err := scanChangeRouterCandidates(rootAbs, indexLimit)
    if err != nil {
        emitChangeRouterJSON(map[string]any{"tool": "change-router", "status": "input_read_failed", "root_path": rootAbs, "error": err.Error()})
        return 2
    }
    candidateLimit := *perKind
    if candidateLimit < 0 {
        candidateLimit = 0
    }
    routes := make([]changeRouterRoute, 0, len(changedFiles))
    for _, path := range changedFiles {
        routes = append(routes, routeChangeCandidates(path, index, candidateLimit))
    }
    status := "ok"
    if walkErrors > 0 {
        status = "ok_with_warnings"
    }
    emitChangeRouterJSON(map[string]any{
        "tool": "change-router",
        "status": status,
        "root_path": rootAbs,
        "changed_source": changedSource,
        "changed_files": changedFiles,
        "changed_files_truncated": changedTruncated,
        "index_candidates": len(index),
        "index_truncated": indexTruncated,
        "index_walk_error_count": walkErrors,
        "routes": routes,
    })
    return 0
}
