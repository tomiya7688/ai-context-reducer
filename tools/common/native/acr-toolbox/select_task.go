package main

import (
    "path/filepath"
    "strings"
)

type selectorTaskOptions struct {
    Root             string
    Goal             string
    TaskFile         string
    ChangedFiles     []string
    ValidationIntent string
}

func parseSelectorTaskArgs(args []string) selectorTaskOptions {
    out := selectorTaskOptions{Root: ".", ValidationIntent: "unknown"}
    for i := 0; i < len(args); i++ {
        switch args[i] {
        case "--goal":
            if i+1 < len(args) { i++; out.Goal = args[i] }
        case "--task-file":
            if i+1 < len(args) { i++; out.TaskFile = args[i] }
        case "--changed":
            if i+1 < len(args) { i++; out.ChangedFiles = append(out.ChangedFiles, filepath.ToSlash(args[i])) }
        case "--validation-intent":
            if i+1 < len(args) { i++; out.ValidationIntent = args[i] }
        default:
            if !strings.HasPrefix(args[i], "-") { out.Root = args[i] }
        }
    }
    return out
}

func selectorApplyTaskContext(recommended, conditional []map[string]any, options selectorTaskOptions) ([]map[string]any, []map[string]any, map[string]any) {
    applied := strings.TrimSpace(options.Goal) != "" || options.TaskFile != "" || len(options.ChangedFiles) > 0 || options.ValidationIntent != "unknown"
    if !applied {
        return recommended, conditional, map[string]any{"applied": false}
    }

    rows := map[string]map[string]any{}
    for _, row := range append(append([]map[string]any{}, recommended...), conditional...) {
        path, _ := row["tool_path"].(string)
        rows[path] = row
    }
    selectedPaths := map[string]bool{}
    reasons := []string{}
    if strings.TrimSpace(options.Goal) != "" {
        selectedPaths["common/small/text-search"] = true
        selectedPaths["common/small/path-find"] = true
        reasons = append(reasons, "goal_provided")
    }
    if options.TaskFile != "" {
        selectedPaths["common/medium/acceptance-extractor"] = true
        selectedPaths["common/small/doc-index"] = true
        selectedPaths["common/medium/exploration-stop-check"] = true
        reasons = append(reasons, "task_file_provided")
    }
    if len(options.ChangedFiles) > 0 {
        selectedPaths["common/medium/compact-diff"] = true
        selectedPaths["common/medium/change-router"] = true
        selectedPaths["common/large/source-structure-index"] = true
        selectedPaths["common/large/target-slice"] = true
        reasons = append(reasons, "changed_files_provided")
    }
    if options.ValidationIntent == "targeted" || options.ValidationIntent == "full" {
        selectedPaths["common/medium/validation-plan"] = true
        selectedPaths["common/small/syntax-health"] = true
        reasons = append(reasons, "validation_"+options.ValidationIntent)
    }

    selected := []map[string]any{}
    for path := range selectedPaths {
        if row, ok := rows[path]; ok {
            copied := map[string]any{}
            for key, value := range row { copied[key] = value }
            copied["task_relevance"] = "direct"
            selected = append(selected, copied)
        }
    }
    selected = selectorDedupeSort(selected, "tool_path")
    uniqueTotal := map[string]bool{}
    for path := range rows { uniqueTotal[path] = true }
    deferred := len(uniqueTotal) - len(selected)
    if deferred < 0 { deferred = 0 }
    return selected, []map[string]any{}, map[string]any{
        "applied": true,
        "goal_present": strings.TrimSpace(options.Goal) != "",
        "task_file": options.TaskFile,
        "changed_files": options.ChangedFiles,
        "validation_intent": options.ValidationIntent,
        "routing_reasons": reasons,
        "deferred_tool_count": deferred,
    }
}
