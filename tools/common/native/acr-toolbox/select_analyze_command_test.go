package main

import (
    "os"
    "path/filepath"
    "testing"
)

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
    recommended, ok := output["recommended_tools"].([]any)
    if !ok || len(recommended) == 0 { t.Fatalf("missing recommended tools: %#v", output) }
    first := recommended[0].(map[string]any)
    if first["phase"] != "orient" { t.Fatalf("routing is not phase ordered: %#v", recommended) }
}

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
