package main

import (
    "encoding/json"
    "flag"
    "io"
    "io/fs"
    "os"
    "path/filepath"
    "sort"
    "strings"
)

var ignoreCandidateNames = map[string]bool{
    "build": true, "dist": true, "bin": true, "obj": true, ".cache": true, "cache": true,
    ".godot": true, "node_modules": true, ".venv": true, "venv": true, "coverage": true,
    "logs": true, "log": true, "tmp": true, "temp": true, "backups": true, "backup": true,
}

var ignoreCandidateExts = map[string]bool{
    ".log": true, ".tmp": true, ".bak": true, ".cache": true, ".pyc": true, ".pdb": true,
    ".dll": true, ".so": true, ".dylib": true, ".exe": true, ".class": true, ".jar": true,
    ".zip": true, ".7z": true,
}

type ignoreCandidate struct {
    Path        string `json:"path"`
    Kind        string `json:"kind"`
    MatchedRule string `json:"matched_rule"`
}

// emitIgnoreCandidatesJSON は内部結果を安定した利用者向け出力へ変換します。
func emitIgnoreCandidatesJSON(value any) {
    enc := json.NewEncoder(os.Stdout)
    enc.SetIndent("", "  ")
    _ = enc.Encode(value)
}

// scanNativeIgnoreCandidates は対象scopeを走査し、agentへ渡す候補情報を収集します。
func scanNativeIgnoreCandidates(root string) ([]ignoreCandidate, int) {
    candidates := []ignoreCandidate{}
    walkErrors := 0
    _ = filepath.WalkDir(root, func(path string, entry fs.DirEntry, visitErr error) error {
        if visitErr != nil {
            walkErrors++
            return nil
        }
        if path == root {
            return nil
        }
        name := strings.ToLower(entry.Name())
        relative, err := filepath.Rel(root, path)
        if err != nil {
            relative = path
        }
        relative = filepath.ToSlash(relative)

        if entry.IsDir() && ignoreCandidateNames[name] {
            candidates = append(candidates, ignoreCandidate{
                Path: relative,
                Kind: "directory",
                MatchedRule: "directory_name:" + name,
            })
            return filepath.SkipDir
        }
        if !entry.IsDir() {
            suffix := strings.ToLower(filepath.Ext(entry.Name()))
            if ignoreCandidateExts[suffix] {
                candidates = append(candidates, ignoreCandidate{
                    Path: relative,
                    Kind: "file",
                    MatchedRule: "file_extension:" + suffix,
                })
            }
        }
        return nil
    })
    sort.Slice(candidates, func(i, j int) bool { return candidates[i].Path < candidates[j].Path })
    return candidates, walkErrors
}

// cmdIgnoreCandidates は対象サブコマンドの引数解析・境界I/O・compact出力を統括します。
func cmdIgnoreCandidates(args []string) int {
    flags := flag.NewFlagSet("ignore-candidates", flag.ContinueOnError)
    flags.SetOutput(io.Discard)
    limit := flags.Int("limit", 80, "maximum candidates returned; 0 means unlimited")
    if err := flags.Parse(args); err != nil {
        emitIgnoreCandidatesJSON(map[string]any{"tool": "ignore-candidates", "status": "invalid_arguments", "error": err.Error()})
        return 2
    }
    root := "."
    if flags.NArg() > 0 {
        root = flags.Arg(0)
    }
    if flags.NArg() > 1 {
        emitIgnoreCandidatesJSON(map[string]any{"tool": "ignore-candidates", "status": "invalid_arguments", "error": "expected at most one root path"})
        return 2
    }
    absolute, err := filepath.Abs(root)
    if err == nil {
        root = absolute
    }
    info, err := os.Stat(root)
    if err != nil {
        status := "input_unavailable"
        if os.IsNotExist(err) {
            status = "input_missing"
        }
        emitIgnoreCandidatesJSON(map[string]any{"tool": "ignore-candidates", "status": status, "root_path": root})
        return 2
    }
    if !info.IsDir() {
        emitIgnoreCandidatesJSON(map[string]any{"tool": "ignore-candidates", "status": "input_not_directory", "root_path": root})
        return 2
    }

    allCandidates, walkErrors := scanNativeIgnoreCandidates(root)
    maxReturned := *limit
    if maxReturned < 0 {
        maxReturned = 0
    }
    returned := allCandidates
    if maxReturned > 0 && len(returned) > maxReturned {
        returned = returned[:maxReturned]
    }
    status := "ok"
    if walkErrors > 0 {
        status = "ok_with_warnings"
    }
    emitIgnoreCandidatesJSON(map[string]any{
        "tool": "ignore-candidates",
        "status": status,
        "root_path": root,
        "candidate_count_total": len(allCandidates),
        "candidates": returned,
        "candidates_truncated": len(returned) < len(allCandidates),
        "walk_error_count": walkErrors,
        "review_required_before_ignoring": true,
    })
    return 0
}
