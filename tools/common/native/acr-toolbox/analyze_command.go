package main

import (
    "encoding/json"
    "os"
    "path/filepath"
    "runtime"
    "sort"
    "strings"
)

var typeSignals = map[string][]string{
    "game": {"project.godot", "assets", "scenes", "game"},
    "gui": {"ui", "views", "widgets", "forms", "window"},
    "compiler": {"lexer", "parser", "token", "ast", "compiler", "grammar"},
    "data-tool": {"dataset", "etl", "converter", "export", "importer", "migration"},
    "packaged-app": {"installer", "package", "publish", "release", "dist"},
    "simulation": {"simulation", "simulator", "agent", "physics", "seed", "random"},
    "rule-heavy": {"rules", "specification", "protocol", "validator", "policy"},
}

func cmdAnalyze(args []string) int {
    root := "."
    if len(args) > 0 {
        root = args[0]
    }
    files, _ := walk(root)
    langs := map[string]int{}
    docs, tests, large := 0, 0, 0
    var hay strings.Builder

    for _, f := range files {
        rel, _ := filepath.Rel(root, f.Path)
        low := strings.ToLower(filepath.ToSlash(rel))
        hay.WriteString(low)
        hay.WriteByte(' ')
        if lang := languageByExt[strings.ToLower(filepath.Ext(f.Path))]; lang != "" {
            langs[lang]++
        }
        ext := strings.ToLower(filepath.Ext(f.Path))
        if ext == ".md" || ext == ".rst" || ext == ".txt" {
            docs++
        }
        if strings.Contains(strings.ToLower(filepath.Base(f.Path)), "test") || strings.Contains(low, "/tests/") {
            tests++
        }
        if f.Size >= 100000 {
            large++
        }
    }

    size := "small"
    if len(files) >= 2000 {
        size = "large"
    } else if len(files) >= 200 {
        size = "medium"
    }

    types := []string{}
    all := hay.String()
    for name, words := range typeSignals {
        for _, word := range words {
            if strings.Contains(all, word) {
                types = append(types, name)
                break
            }
        }
    }
    sort.Strings(types)

    techniques := []string{
        "AI_CONTEXT minimum core",
        "Search-first / Read-second",
        "Exploration stop condition",
        "Source of Truth",
        "Targeted validation",
    }
    if size != "small" {
        techniques = append(techniques, "Responsibility Map", "Change Routing Map")
    }
    if size == "large" || large > 0 {
        techniques = append(techniques, "Source Structure Index", "Bounded excerpts", "Context manifest")
    }
    for _, projectType := range types {
        switch projectType {
        case "simulation":
            techniques = append(techniques, "Deterministic seam / structured observation")
        case "packaged-app":
            techniques = append(techniques, "Artifact-boundary validation")
        case "rule-heavy":
            techniques = append(techniques, "Policy Routing")
        }
    }

    out := map[string]any{
        "project": filepath.Base(root),
        "size": size,
        "files": len(files),
        "docs": docs,
        "tests": tests,
        "large_files_100kb_plus": large,
        "languages": langs,
        "project_types": types,
        "recommended_techniques": techniques,
        "runtime": map[string]string{
            "os": runtime.GOOS,
            "arch": runtime.GOARCH,
            "implementation": "native-go",
        },
    }
    enc := json.NewEncoder(os.Stdout)
    enc.SetIndent("", "  ")
    _ = enc.Encode(out)
    return 0
}
