package main

import (
    "flag"
    "io"
    "os"
    "strings"
)

var explorationChecks = map[string][]string{
    "goal":       {"goal", "目的"},
    "required":   {"required", "requirement", "要件", "必須", "制約"},
    "acceptance": {"acceptance", "完了条件", "受け入れ", "completion"},
    "deferred":   {"deferred", "out of scope", "非対象", "対象外"},
    "source":     {"source", "target file", "対象ファイル", "実装"},
    "tests":      {"test", "tests", "検証", "validation"},
}

var explorationRequired = []string{"goal", "required", "acceptance", "source", "tests"}

func evaluateExplorationStop(text string) map[string]any {
    lowered := strings.ToLower(text)
    checks := map[string]bool{}
    for key, terms := range explorationChecks {
        matched := false
        for _, term := range terms {
            if contextTermPresent(lowered, term) {
                matched = true
                break
            }
        }
        checks[key] = matched
    }
    missing := []string{}
    for _, key := range explorationRequired {
        if !checks[key] {
            missing = append(missing, key)
        }
    }
    return map[string]any{
        "checks":                  checks,
        "required_checks":         explorationRequired,
        "missing_required_checks": missing,
        "stop_broad_exploration":  len(missing) == 0,
    }
}

func cmdExplorationStopCheck(args []string) int {
    fs := flag.NewFlagSet("exploration-stop-check", flag.ContinueOnError)
    fs.SetOutput(io.Discard)
    if err := fs.Parse(args); err != nil {
        emitStructureJSON(map[string]any{"tool": "exploration-stop-check", "status": "invalid_arguments", "error": err.Error()})
        return 2
    }
    if fs.NArg() != 1 {
        emitStructureJSON(map[string]any{"tool": "exploration-stop-check", "status": "invalid_arguments", "required_argument": "context_file"})
        return 2
    }
    path := fs.Arg(0)
    info, err := os.Stat(path)
    if err != nil {
        status := "read_failed"
        if os.IsNotExist(err) {
            status = "input_missing"
        }
        emitStructureJSON(map[string]any{"tool": "exploration-stop-check", "status": status, "input_file": path})
        return 2
    }
    if !info.Mode().IsRegular() {
        emitStructureJSON(map[string]any{"tool": "exploration-stop-check", "status": "input_not_file", "input_file": path})
        return 2
    }
    data, err := os.ReadFile(path)
    if err != nil {
        emitStructureJSON(map[string]any{"tool": "exploration-stop-check", "status": "read_failed", "input_file": path})
        return 2
    }
    text := strings.ToValidUTF8(string(data), "")
    result := evaluateExplorationStop(text)
    result["tool"] = "exploration-stop-check"
    result["status"] = "ok"
    result["input_file"] = path
    emitStructureJSON(result)
    return 0
}
