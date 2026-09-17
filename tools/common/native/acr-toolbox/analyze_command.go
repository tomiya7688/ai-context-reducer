package main

import (
    "encoding/json"
    "os"
    "os/exec"
    "path/filepath"
    "runtime"
    "sort"
    "strings"
)

var analyzeLanguages = map[string]string{
    ".py": "python", ".cs": "csharp", ".go": "go", ".c": "c", ".h": "c",
    ".cpp": "cpp", ".cc": "cpp", ".cxx": "cpp", ".hpp": "cpp", ".hh": "cpp",
    ".gd": "gdscript", ".rs": "rust", ".js": "javascript", ".ts": "typescript", ".java": "java",
}

var analyzeTypeSignals = map[string][]string{
    "game": {"project.godot", "assets", "scenes", "game"},
    "gui": {"ui", "views", "widgets", "forms", "window"},
    "compiler": {"lexer", "parser", "token", "ast", "compiler", "grammar"},
    "data_tool": {"dataset", "etl", "converter", "export", "importer", "migration"},
    "packaged_app": {"installer", "package", "publish", "release", "dist"},
    "simulation": {"simulation", "simulator", "agent", "physics", "seed", "random"},
    "rule_heavy": {"rules", "specification", "protocol", "validator", "policy"},
}

func analyzeWriteJSON(value any) {
    enc := json.NewEncoder(os.Stdout)
    enc.SetIndent("", "  ")
    _ = enc.Encode(value)
}

func analyzeBoundedText(text string, limit int) string {
    if limit <= 0 || len(text) <= limit { return text }
    return text[:limit]
}

func nativeExternalTools() []string {
    candidates := []string{"rg", "fd", "ast-grep", "sg", "ctags", "scip", "tree-sitter", "scc", "git-sizer"}
    out := []string{}
    for _, name := range candidates {
        if _, err := exec.LookPath(name); err == nil { out = append(out, name) }
    }
    return out
}

func cmdAnalyze(args []string) int {
    root := "."
    if len(args) > 0 { root = args[0] }
    absRoot, _ := filepath.Abs(root)
    info, err := os.Stat(absRoot)
    if err != nil {
        analyzeWriteJSON(map[string]any{"tool": "analyze-and-recommend", "status": "input_missing", "project_root": absRoot})
        return 2
    }
    if !info.IsDir() {
        analyzeWriteJSON(map[string]any{"tool": "analyze-and-recommend", "status": "input_not_directory", "project_root": absRoot})
        return 2
    }
    walked, err := walkWithOptions(absRoot, false)
    if err != nil {
        analyzeWriteJSON(map[string]any{"tool": "analyze-and-recommend", "status": "scan_failed", "project_root": absRoot, "error": analyzeBoundedText(err.Error(), 800)})
        return 1
    }
    langs := map[string]int{}
    nonLang, docs, tests, large := 0, 0, 0, 0
    detected := map[string]bool{}
    for _, f := range walked.Files {
        ext := strings.ToLower(filepath.Ext(f.Path))
        if lang := analyzeLanguages[ext]; lang != "" { langs[lang]++ } else { nonLang++ }
        if ext == ".md" || ext == ".rst" || ext == ".txt" { docs++ }
        rel, _ := filepath.Rel(absRoot, f.Path)
        relSlash := strings.ToLower(filepath.ToSlash(rel))
        name := strings.ToLower(filepath.Base(f.Path))
        parts := strings.Split(relSlash, "/")
        isTest := strings.HasPrefix(name, "test_") || strings.HasSuffix(name, "_test.py") || strings.HasSuffix(name, "_test.go")
        for _, p := range parts { if p == "test" || p == "tests" { isTest = true } }
        if isTest { tests++ }
        if f.Size >= 100000 { large++ }
        for projectType, words := range analyzeTypeSignals {
            if detected[projectType] { continue }
            for _, word := range words { if strings.Contains(relSlash, word) { detected[projectType] = true; break } }
        }
    }
    size := "small"
    if len(walked.Files) >= 2000 { size = "large" } else if len(walked.Files) >= 200 { size = "medium" }
    types := []string{}
    for t := range detected { types = append(types, t) }
    sort.Strings(types)
    gitPresent := false
    if stat, err := os.Stat(filepath.Join(absRoot, ".git")); err == nil && stat.IsDir() { gitPresent = true }
    _, gitErr := exec.LookPath("git")
    gitAvailable := gitErr == nil
    gitStatus := "not_repository"
    var dirty any = nil
    if gitPresent && !gitAvailable {
        gitStatus = "git_unavailable"
    } else if gitPresent && gitAvailable {
        cmd := exec.Command("git", "-C", absRoot, "status", "--porcelain")
        raw, err := cmd.Output()
        if err != nil { gitStatus = "query_failed" } else { gitStatus = "ok"; dirty = len(strings.TrimSpace(string(raw))) > 0 }
    }
    status := "ok"
    if walked.ErrorCount > 0 { status = "ok_with_warnings" }
    out := map[string]any{
        "tool": "analyze-and-recommend", "status": status, "project_root": absRoot,
        "project_size_class": size, "files_scanned": len(walked.Files), "scan_truncated": false,
        "recognized_source_files_scanned": len(walked.Files)-nonLang, "non_language_files_scanned": nonLang,
        "documentation_file_count": docs, "test_file_count": tests, "large_files_100kb_plus_count": large,
        "file_stat_error_count": walked.StatErrorCount, "language_file_counts": langs, "detected_project_types": types,
        "git": map[string]any{"repository_present": gitPresent, "executable_available": gitAvailable, "status": gitStatus, "dirty": dirty},
        "external_tools_available": nativeExternalTools(),
        "runtime_plan": map[string]any{"os": runtime.GOOS, "arch": runtime.GOARCH, "preferred_implementation": "native", "native_command": "acr-toolbox"},
        "routing_handoff": map[string]any{
            "tool_path": "common/small/tool-selector",
            "native_command": "acr-toolbox select",
            "reason": "tool-selector is the Source of Truth for ordered tool routing and exploration-stop conditions",
        },
    }
    if walked.WalkErrorCount > 0 { out["walk_error_count"] = walked.WalkErrorCount }
    analyzeWriteJSON(out)
    return 0
}
