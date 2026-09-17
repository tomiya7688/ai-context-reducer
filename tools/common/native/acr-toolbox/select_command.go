package main

import (
    "encoding/json"
    "os"
    "os/exec"
    "path/filepath"
    "sort"
    "strings"
)

var selectorLanguages = map[string]string{
    ".py": "python", ".cs": "csharp", ".go": "go", ".c": "c", ".h": "c",
    ".cpp": "cpp", ".cc": "cpp", ".cxx": "cpp", ".hpp": "cpp", ".hh": "cpp",
    ".gd": "gdscript", ".rs": "rust", ".js": "javascript", ".ts": "typescript", ".java": "java",
}

var selectorExternal = []string{"rg", "fd", "ast-grep", "sg", "ctags", "scip", "tree-sitter", "scc", "git-sizer"}
var selectorPhaseOrder = map[string]int{"orient": 0, "search": 1, "scope": 2, "inspect": 3, "validate": 4, "stop": 5}

func selectorItem(path, reason, phase, activation, availability string) map[string]any {
    if activation == "" { activation = "always" }
    if availability == "" { availability = "ready" }
    return map[string]any{"tool_path": path, "phase": phase, "activation": activation, "availability": availability, "reason": reason}
}

func selectorAvailability(path string, external map[string]bool) string {
    switch path {
    case "common/small/text-search":
        if external["rg"] { return "external_backend_ready" }
        return "portable_fallback_ready"
    case "common/small/path-find":
        if external["fd"] { return "external_backend_ready" }
        return "portable_fallback_ready"
    case "common/small/repo-profile", "common/small/repo-stats":
        if external["scc"] { return "external_backend_ready" }
        return "portable_fallback_ready"
    case "common/medium/structural-search":
        if external["ast-grep"] || external["sg"] { return "external_backend_ready" }
        return "python_ast_fallback_limited"
    }
    return "ready"
}

func selectorDedupeSort(rows []map[string]any, key string) []map[string]any {
    seen := map[string]bool{}
    out := []map[string]any{}
    for _, row := range rows {
        value, _ := row[key].(string)
        if seen[value] { continue }
        seen[value] = true
        out = append(out, row)
    }
    sort.SliceStable(out, func(i, j int) bool {
        pi, _ := out[i]["phase"].(string)
        pj, _ := out[j]["phase"].(string)
        return selectorPhaseOrder[pi] < selectorPhaseOrder[pj]
    })
    return out
}

func selectorRecommendations(size string, languages [][2]any, projectTypes []string, docs, tests int, hasGit bool, external map[string]bool) ([]map[string]any, []map[string]any, []map[string]any, []map[string]any) {
    recommended := []map[string]any{
        selectorItem("common/small/repo-profile", "identify repository size and language mix before deeper reads", "orient", "always", selectorAvailability("common/small/repo-profile", external)),
        selectorItem("common/small/source-of-truth-candidates", "find likely authoritative documentation entry points before broad reading", "orient", "always", "ready"),
        selectorItem("common/small/text-search", "search for target terms before opening whole files", "search", "always", selectorAvailability("common/small/text-search", external)),
        selectorItem("common/small/path-find", "narrow candidate paths before tree-wide reading", "search", "always", selectorAvailability("common/small/path-find", external)),
    }
    conditional := []map[string]any{}
    if docs > 0 {
        conditional = append(conditional, selectorItem("common/small/doc-index", "documentation exists; inspect headings before full documents", "search", "when documentation is relevant", "ready"))
    }
    if hasGit {
        recommended = append(recommended, selectorItem("common/medium/compact-diff", "Git repository detected; inspect bounded change evidence before full diff", "scope", "when the task concerns current changes", "ready"))
        conditional = append(conditional,
            selectorItem("common/medium/remote-delta", "compare local and remote state before broad repository exploration", "scope", "when remote divergence matters", "ready"),
            selectorItem("common/medium/change-router", "route changed files to likely tests and documentation", "scope", "when changed files are known", "ready"),
            selectorItem("common/medium/context-pack-builder", "materialize a bounded task context when context must be handed off", "inspect", "when a reusable Context Pack is needed", "ready"),
        )
        if size == "large" && external["git-sizer"] {
            conditional = append(conditional, selectorItem("common/small/git-history-health", "reuse existing git-sizer for compact history/object health findings", "orient", "when repository history/object size may affect work", "external_backend_ready"))
        }
    }
    if tests > 0 {
        conditional = append(conditional,
            selectorItem("common/medium/validation-plan", "derive targeted validation from changed paths instead of running everything first", "validate", "when implementation changes are ready to validate", "ready"),
            selectorItem("common/medium/compact-log", "compress large validation output to actionable findings", "validate", "when validation output is verbose", "ready"),
        )
    }
    if docs > 0 {
        conditional = append(conditional,
            selectorItem("common/medium/acceptance-extractor", "extract Goal/Required/Acceptance before implementation when task docs contain them", "orient", "when a task/specification document exists", "ready"),
            selectorItem("common/medium/exploration-stop-check", "check whether enough task context exists to stop broad exploration", "stop", "after Goal/Required/Acceptance/source/tests are identified", "ready"),
        )
    }
    if size == "medium" || size == "large" {
        recommended = append(recommended, selectorItem("common/medium/change-router", size+" repository benefits from change-to-test/doc routing", "scope", "when changed files are known", "ready"))
        conditional = append(conditional,
            selectorItem("common/medium/structural-search", "use syntax-shaped search when text search is noisy", "search", "when text search returns unrelated matches", selectorAvailability("common/medium/structural-search", external)),
            selectorItem("common/medium/responsibility-candidates", "locate likely responsibility boundaries before reading neighboring modules", "scope", "when ownership boundaries are unclear", "ready"),
            selectorItem("common/medium/doc-duplicate-hints", "find duplicated documentation that may inflate context", "orient", "when documentation is repetitive", "ready"),
            selectorItem("common/large/hotspot-report", "find large/deep hotspots before broad source reads", "orient", "when repository shape is unclear", "ready"),
        )
    }
    if size == "large" {
        recommended = append(recommended,
            selectorItem("common/large/context-manifest", "prioritize likely context entry points in a large repository", "orient", "always", "ready"),
            selectorItem("common/large/source-structure-index", "query and expand only the target symbol/dependency neighborhood", "scope", "always", "ready"),
            selectorItem("common/large/target-slice", "read bounded excerpts instead of full source files", "inspect", "always", "ready"),
            selectorItem("common/large/context-budget", "estimate likely agent context cost before broad reads", "orient", "always", "ready"),
        )
    }
    if external["tree-sitter"] && len(languages) > 0 {
        conditional = append(conditional, selectorItem("common/small/syntax-health", "reuse configured Tree-sitter parsers to surface only files with syntax issues", "validate", "when syntax-level validation is useful", "external_backend_ready"))
    }
    for _, t := range projectTypes {
        if t == "rule_heavy" {
            conditional = append(conditional, selectorItem("common/medium/policy-index", "extract likely policy lines before reading full rule documents", "orient", "when policy/rule constraints govern the task", "ready"))
        }
    }
    groups := []map[string]any{}
    conditionalGroups := []map[string]any{}
    for i, langRow := range languages {
        if i >= 3 { break }
        lang, _ := langRow[0].(string)
        groups = append(groups, map[string]any{"tool_group_path": lang+"/small", "phase": "search", "reason": lang+" source files detected"})
        if size == "medium" || size == "large" {
            conditionalGroups = append(conditionalGroups, map[string]any{"tool_group_path": lang+"/medium", "phase": "scope", "reason": size+" "+lang+" project may need dependency/change analysis"})
        }
        if size == "large" {
            conditionalGroups = append(conditionalGroups, map[string]any{"tool_group_path": lang+"/large", "phase": "scope", "reason": "large "+lang+" project may benefit from whole-scope analysis"})
        }
    }
    if len(projectTypes) > 0 {
        conditionalGroups = append(conditionalGroups, map[string]any{"tool_group_path": "profiles/project-type-profile", "phase": "orient", "reason": "project-type signals were detected"})
    }
    return selectorDedupeSort(recommended, "tool_path"), selectorDedupeSort(conditional, "tool_path"), selectorDedupeSort(groups, "tool_group_path"), selectorDedupeSort(conditionalGroups, "tool_group_path")
}

func cmdSelect(args []string) int {
    root := "."
    if len(args) > 0 { root = args[0] }
    absRoot, _ := filepath.Abs(root)
    info, err := os.Stat(absRoot)
    if err != nil {
        writeJSON(map[string]any{"tool": "tool-selector", "status": "input_missing", "project_root": absRoot})
        return 2
    }
    if !info.IsDir() {
        writeJSON(map[string]any{"tool": "tool-selector", "status": "input_not_directory", "project_root": absRoot})
        return 2
    }
    walked, err := walkWithOptions(absRoot, false)
    if err != nil {
        writeJSON(map[string]any{"tool": "tool-selector", "status": "scan_failed", "project_root": absRoot, "error": boundedText(err.Error(), 800)})
        return 1
    }
    langCounts := map[string]int{}
    nonLang, docs, tests := 0, 0, 0
    detected := map[string]bool{}
    for _, f := range walked.Files {
        rel, _ := filepath.Rel(absRoot, f.Path)
        relSlash := filepath.ToSlash(rel)
        ext := strings.ToLower(filepath.Ext(f.Path))
        if lang := selectorLanguages[ext]; lang != "" { langCounts[lang]++ } else { nonLang++ }
        if ext == ".md" || ext == ".rst" || ext == ".txt" { docs++ }
        name := strings.ToLower(filepath.Base(f.Path))
        parts := strings.Split(strings.ToLower(relSlash), "/")
        isTest := strings.HasPrefix(name, "test_") || strings.HasSuffix(name, "_test.py") || strings.HasSuffix(name, "_test.go")
        for _, p := range parts { if p == "test" || p == "tests" { isTest = true } }
        if isTest { tests++ }
        low := strings.ToLower(relSlash)
        for projectType, words := range typeSignals {
            normalized := strings.ReplaceAll(projectType, "-", "_")
            if detected[normalized] { continue }
            for _, word := range words { if strings.Contains(low, word) { detected[normalized] = true; break } }
        }
    }
    size := "small"
    if len(walked.Files) >= 2000 { size = "large" } else if len(walked.Files) >= 200 { size = "medium" }
    typeList := []string{}
    for t := range detected { typeList = append(typeList, t) }
    sort.Strings(typeList)
    type langPair struct { name string; count int }
    pairs := []langPair{}
    for name, count := range langCounts { pairs = append(pairs, langPair{name, count}) }
    sort.Slice(pairs, func(i, j int) bool { if pairs[i].count == pairs[j].count { return pairs[i].name < pairs[j].name }; return pairs[i].count > pairs[j].count })
    languages := make([][2]any, 0, len(pairs))
    for _, p := range pairs { languages = append(languages, [2]any{p.name, p.count}) }
    externalMap := map[string]bool{}
    externalList := []string{}
    for _, name := range selectorExternal { if _, err := exec.LookPath(name); err == nil { externalMap[name] = true; externalList = append(externalList, name) } }
    hasGit := false
    if stat, err := os.Stat(filepath.Join(absRoot, ".git")); err == nil && stat.IsDir() { hasGit = true }
    recommended, conditional, groups, conditionalGroups := selectorRecommendations(size, languages, typeList, docs, tests, hasGit, externalMap)
    out := map[string]any{
        "tool": "tool-selector", "status": "ok", "project_root": absRoot, "project_size_class": size,
        "files_scanned": len(walked.Files), "scan_truncated": false,
        "recognized_source_files_scanned": len(walked.Files)-nonLang, "non_language_files_scanned": nonLang,
        "language_file_counts": langCounts, "detected_project_types": typeList,
        "documentation_file_count": docs, "test_file_count": tests, "git_repository_detected": hasGit,
        "external_tools_available": externalList,
        "routing_order": []string{"orient", "search", "scope", "inspect", "validate", "stop"},
        "exploration_stop_conditions": []string{
            "Goal, Required, and Acceptance are known",
            "authoritative source or implementation target is identified",
            "targeted validation path is identified",
            "additional broad exploration is unlikely to change the working set",
        },
        "recommended_tools": recommended, "conditional_tools": conditional,
        "recommended_tool_groups": groups, "conditional_tool_groups": conditionalGroups,
    }
    if walked.ErrorCount > 0 { out["status"] = "ok_with_warnings"; out["scan_error_count"] = walked.ErrorCount }
    writeJSON(out)
    return 0
}
