package main

import (
    "encoding/json"
    "os"
    "path/filepath"
    "testing"
)

// TestSummarizeGitSizerFiltersSortsAndTruncates は対象機能の期待contractが将来の変更で崩れないことを検証します。
func TestSummarizeGitSizerFiltersSortsAndTruncates(t *testing.T) {
    payload := map[string]any{
        "uniqueBlobSize": map[string]any{"value": float64(100), "levelOfConcern": float64(0.2)},
        "maxBlobSize": map[string]any{"value": float64(50), "levelOfConcern": float64(3), "objectDescription": "assets/big.bin"},
        "nested": map[string]any{
            "maxPathDepth": map[string]any{"value": float64(30), "levelOfConcern": float64(2)},
        },
    }
    result := summarizeGitSizer(payload, 1, 1)
    if result["metric_count_total"] != 3 {
        t.Fatalf("unexpected metric count: %#v", result)
    }
    if result["concern_count_total"] != 2 {
        t.Fatalf("unexpected concern count: %#v", result)
    }
    if result["findings_truncated"] != true {
        t.Fatalf("expected truncation: %#v", result)
    }
    findings := result["findings"].([]gitHealthFinding)
    if len(findings) != 1 || findings[0].Metric != "maxBlobSize" || findings[0].ObjectDescription != "assets/big.bin" {
        t.Fatalf("unexpected findings: %#v", findings)
    }
}

// TestGitHistoryHealthCLIReadsSavedJSON は対象機能の期待contractが将来の変更で崩れないことを検証します。
func TestGitHistoryHealthCLIReadsSavedJSON(t *testing.T) {
    root := t.TempDir()
    input := filepath.Join(root, "git-sizer.json")
    payload := map[string]any{
        "maxBlobSize": map[string]any{"value": 20000000, "unit": "B", "levelOfConcern": 2.0},
    }
    data, err := json.Marshal(payload)
    if err != nil {
        t.Fatal(err)
    }
    if err := os.WriteFile(input, data, 0o644); err != nil {
        t.Fatal(err)
    }
    code, output := captureJSONCommand(t, func() int {
        return cmdGitHistoryHealth([]string{"--json-input", input, root})
    })
    if code != 0 {
        t.Fatalf("unexpected exit code=%d output=%#v", code, output)
    }
    if output["tool"] != "git-history-health" || output["backend"] != "git-sizer-json-input" {
        t.Fatalf("unexpected contract: %#v", output)
    }
    if output["concern_count_total"] != float64(1) {
        t.Fatalf("unexpected concern count: %#v", output)
    }
}
