package main

import (
    "os"
    "path/filepath"
    "testing"
)

// TestSelectReturnsOrderedRoutingAndNoLatestFalsePositive は対象機能の契約と回帰条件が維持されることを確認します。
func TestSelectReturnsOrderedRoutingAndNoLatestFalsePositive(t *testing.T) {
    root := t.TempDir()
    if err := os.WriteFile(filepath.Join(root, "latest.py"), []byte("x = 1\n"), 0o644); err != nil { t.Fatal(err) }
    if err := os.WriteFile(filepath.Join(root, "README.md"), []byte("# demo\n"), 0o644); err != nil { t.Fatal(err) }
    code, output := captureJSONCommand(t, func() int { return cmdSelect([]string{root}) })
    if code != 0 { t.Fatalf("unexpected exit code=%d output=%#v", code, output) }
    if output["tool"] != "tool-selector" || output["status"] != "ok" { t.Fatalf("unexpected contract: %#v", output) }
    if output["test_file_count"] != float64(0) { t.Fatalf("latest.py must not be counted as test: %#v", output) }
    routing, ok := output["routing_order"].([]any)
    if !ok || len(routing) != 6 || routing[0] != "orient" || routing[5] != "stop" { t.Fatalf("unexpected routing order: %#v", output["routing_order"]) }
    taskContext := output["task_context"].(map[string]any)
    if taskContext["applied"] != false { t.Fatalf("task context should be inactive: %#v", taskContext) }
    recommended, ok := output["recommended_tools"].([]any)
    if !ok || len(recommended) == 0 { t.Fatalf("missing recommended tools: %#v", output) }
    first := recommended[0].(map[string]any)
    if first["phase"] != "orient" { t.Fatalf("routing is not phase ordered: %#v", recommended) }
}

// TestSelectTaskContextNarrowsRecommendedTools は対象機能の契約と回帰条件が維持されることを確認します。
func TestSelectTaskContextNarrowsRecommendedTools(t *testing.T) {
    root := t.TempDir()
    if err := os.Mkdir(filepath.Join(root, ".git"), 0o755); err != nil { t.Fatal(err) }
    if err := os.Mkdir(filepath.Join(root, "src"), 0o755); err != nil { t.Fatal(err) }
    if err := os.Mkdir(filepath.Join(root, "tests"), 0o755); err != nil { t.Fatal(err) }
    if err := os.WriteFile(filepath.Join(root, "src", "service.go"), []byte("package service\n"), 0o644); err != nil { t.Fatal(err) }
    if err := os.WriteFile(filepath.Join(root, "tests", "service_test.go"), []byte("package tests\n"), 0o644); err != nil { t.Fatal(err) }
    if err := os.WriteFile(filepath.Join(root, "TASK.md"), []byte("# Goal\nChange service behavior\n"), 0o644); err != nil { t.Fatal(err) }

    code, output := captureJSONCommand(t, func() int {
        return cmdSelect([]string{
            "--goal", "Change service behavior",
            "--task-file", "TASK.md",
            "--changed", "src/service.go",
            "--validation-intent", "targeted",
            root,
        })
    })
    if code != 0 { t.Fatalf("unexpected exit code=%d output=%#v", code, output) }
    taskContext := output["task_context"].(map[string]any)
    if taskContext["applied"] != true { t.Fatalf("task context should be active: %#v", taskContext) }
    conditional := output["conditional_tools"].([]any)
    if len(conditional) != 0 { t.Fatalf("task-aware routing should defer unrelated conditional tools: %#v", conditional) }
    recommended := output["recommended_tools"].([]any)
    selected := map[string]bool{}
    for _, raw := range recommended {
        row := raw.(map[string]any)
        selected[row["tool_path"].(string)] = true
        if row["task_relevance"] != "direct" { t.Fatalf("missing task relevance: %#v", row) }
    }
    for _, path := range []string{"common/small/text-search", "common/medium/acceptance-extractor", "common/medium/compact-diff", "common/medium/change-router", "common/medium/validation-plan"} {
        if !selected[path] { t.Fatalf("expected task-aware tool %s in %#v", path, selected) }
    }
    if selected["common/large/context-budget"] { t.Fatalf("unrelated large routing tool should be deferred: %#v", selected) }
}

// TestAnalyzeHandsRoutingToSelector は対象機能の契約と回帰条件が維持されることを確認します。
func TestAnalyzeHandsRoutingToSelector(t *testing.T) {
    root := t.TempDir()
    if err := os.WriteFile(filepath.Join(root, "main.go"), []byte("package main\n"), 0o644); err != nil { t.Fatal(err) }
    code, output := captureJSONCommand(t, func() int { return cmdAnalyze([]string{root}) })
    if code != 0 { t.Fatalf("unexpected exit code=%d output=%#v", code, output) }
    if output["tool"] != "analyze-and-recommend" { t.Fatalf("unexpected tool: %#v", output) }
    handoff, ok := output["routing_handoff"].(map[string]any)
    if !ok || handoff["native_command"] != "acr-toolbox select" { t.Fatalf("missing selector handoff: %#v", output) }
    if _, duplicated := output["recommended_tool_paths"]; duplicated { t.Fatalf("analyze must not duplicate selector recommendations: %#v", output) }
}
